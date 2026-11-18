"""Read final Parquet back and check the actual Shuffle-R1 CPU entry paths."""
import argparse
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import unicodedata

import pyarrow.parquet as pq

from freeze_dataset import HISTORY, load_lines, sha, write_json


def norm(value):
    return " ".join(unicodedata.normalize("NFKC", value).split())


def verify(worktree, data):
    sys.path.insert(0, str(worktree))
    from shuffle_r1 import main
    from shuffle_r1.checkpoint import verify_split_manifest
    from verl.utils.dataset import RLHFDataset, collate_fn
    from verl.utils.tokenizer import get_processor, get_tokenizer

    manifest = json.loads((data / "split_manifest.json").read_text())
    records = load_lines(data / "rows.jsonl")
    assert sha(data / "rows.jsonl") == manifest["rows_manifest_sha256"]
    source = {r["row"]: r for r in load_lines(HISTORY / "mmrl30k-visible-rows.jsonl") if r["split"] == "train"}
    expected = {name: [r for r in records if r.get("in_dev16", False)] if name == "dev16.parquet"
                else [r for r in records if r["partition"] == name.removesuffix(".parquet")]
                for name in manifest["files"]}
    signatures = {}
    for name, identity in manifest["files"].items():
        reader = pq.ParquetFile(data / name)
        assert sha(data / name) == identity["sha256"] and reader.metadata.num_rows == identity["rows"]
        verified = 0
        fingerprints = set()
        for batch in reader.iter_batches(batch_size=128):
            for row in batch.to_pylist():
                record = expected[name][verified]
                raw_img = row["images"][0]["bytes"]
                assert len(row["images"]) == 1 and hashlib.sha256(raw_img).hexdigest() == record["image_bytes"]
                assert row["source"] == record["source"]
                key = f"{record['visible_rgb']}\n{norm(row['problem'])}\n{norm(row['answer'])}".encode()
                assert hashlib.sha256(key).hexdigest() == source[record["original_train_row"]]["problem_visible_image_answer"]
                fingerprints.add(record["visible_rgb"])
                verified += 1
        assert verified == identity["rows"] == len(expected[name])
        signatures[name] = fingerprints
        print(f"Read back and matched {verified} rows in {name}", flush=True)
    holdout = {r["image_visible_rgb"] for r in load_lines(HISTORY / "mmrl30k-visible-rows.jsonl")
               if r["split"] in {"geo3k_test", "k12_test"}}
    assert not (signatures["train.parquet"] & signatures["dev.parquet"])
    assert not ((signatures["train.parquet"] | signatures["dev.parquet"]) & holdout)
    assert signatures["dev16.parquet"] <= signatures["dev.parquet"]

    paths = [f"config={worktree / 'configs/g4_clean_seed1.yaml'}", f"data.train_files={data/'train.parquet'}",
             f"data.val_files={data/'dev.parquet'}", f"data.split_manifest={data/'split_manifest.json'}"]
    config = main.load_config(paths)
    verify_split_manifest(config)
    parsed = []
    for prompts, actor_batch, chunk in ((16, 4, 4), (64, 16, 16), (128, 32, 16), (512, 128, 16)):
        sys.argv = ["shuffle_r1.main", "--print-config", *paths, f"data.rollout_batch_size={prompts}",
                    f"worker.actor.global_batch_size={actor_batch}", f"worker.rollout.rollout_chunk_prompts={chunk}"]
        with redirect_stdout(StringIO()) as stream:
            main.main()
        resolved = json.loads(stream.getvalue())
        assert resolved["data"]["rollout_batch_size"] == prompts and resolved["data"]["dataloader_num_workers"] == 0
        assert resolved["worker"]["actor"]["global_batch_size"] == actor_batch
        assert resolved["worker"]["rollout"]["rollout_chunk_prompts"] == chunk
        assert resolved["worker"]["rollout"]["max_num_seqs"] == 64
        assert resolved["trainer"]["max_steps"] == 150
        parsed.append([prompts, actor_batch, chunk])

    model = config.worker.actor.model
    kwargs = {"revision": model.revision, "trust_remote_code": model.trust_remote_code,
              "use_fast": True, "local_files_only": True}
    tokenizer = get_tokenizer(model.model_path, **kwargs)
    processor = get_processor(model.model_path, **kwargs)
    probe = main.load_config([*paths, f"data.val_files={data/'dev16.parquet'}",
                              "data.rollout_batch_size=16", "worker.actor.global_batch_size=4",
                              "worker.rollout.rollout_chunk_prompts=4", "trainer.max_steps=2"])
    verify_split_manifest(probe)
    dataset = RLHFDataset(str(data / "dev16.parquet"), tokenizer, processor,
        prompt_key=probe.data.prompt_key, answer_key=probe.data.answer_key, image_key=probe.data.image_key,
        min_pixels=probe.data.min_pixels, max_pixels=probe.data.max_pixels, max_prompt_length=probe.data.max_prompt_length,
        truncation="error", system_prompt=probe.data.system_prompt)
    features = [dataset[index] for index in range(16)]
    batch = collate_fn(features)
    assert batch["position_ids"].shape == (16, 3, 2048)
    assert batch["attention_mask"].sum(dim=1).tolist() == [r["prompt_tokens"] for r in expected["dev16.parquet"]]
    for row, identity in zip(features, expected["dev16.parquet"], strict=True):
        assert row["multi_modal_inputs"]["image_grid_thw"][0].tolist() == identity["image_grid_thw"]
    program = ("import random, numpy, torch; from shuffle_r1.single_gpu import seed_process; "
               "seed_process(1); print(random.random(), numpy.random.rand(), torch.rand(1).item())")
    first = subprocess.check_output([sys.executable, "-B", "-c", program], cwd=worktree)
    second = subprocess.check_output([sys.executable, "-B", "-c", program], cwd=worktree)
    assert first == second
    return {"config_shapes_B_G_chunk": parsed, "parquet_files_rechecked": manifest["files"],
            "dev16_live_cpu_processor": str(type(processor.image_processor).__name__),
            "dev16_position_ids_shape": list(batch["position_ids"].shape),
            "all_dev16_image_grids_and_lengths_match_manifest": True,
            "same_driver_seed_reproduced_in_fresh_processes": True,
            "visible_exact_train_dev_and_test_intersections": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.worktree, args.data)
    write_json(args.report, result)
    print(json.dumps(result, indent=2), flush=True)
