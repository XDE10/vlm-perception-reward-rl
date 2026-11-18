"""Freeze image-family exclusions, train/dev splits and Qwen prompt geometry on CPU."""
import argparse
from collections import Counter, defaultdict
from io import BytesIO
import hashlib
import json
from pathlib import Path
import random
import sys
import tempfile

import numpy as np
from PIL import Image
import pyarrow as pa
import pyarrow.parquet as pq
from transformers.models.qwen2_vl.image_processing_qwen2_vl import smart_resize


HERE = Path(__file__).resolve().parent
HISTORY = HERE.parent / "shuffle_r1_cpu_data_freeze_20261115"
SEED = 20261115


def load_lines(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, item):
    path.write_text(json.dumps(item, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def bind_source(root, review):
    source_manifest = json.loads((root / "mmrl30k-b362381-visible-clean/manifest.json").read_text())
    source = Path(source_manifest["output"]["path"])
    if sha(source) != source_manifest["output"]["sha256"]:
        raise ValueError("source clean dataset SHA256 mismatch")
    audit = json.loads((HISTORY / "mmrl30k-visible-audit.json").read_text())
    for name, info in audit["shards"].items():
        if sha(root / "mmrl30k-b362381" / name) != info["sha256"]:
            raise ValueError(f"publisher shard SHA256 mismatch: {name}")
    rows = load_lines(HISTORY / "mmrl30k-visible-rows.jsonl")
    offsets = {}
    for row in rows:
        if row["split"] == "train":
            offsets.setdefault(row["shard"], row["row"])
    exact = {(entry["shard"], entry["row_in_shard"]) for entry in load_lines(HISTORY / "decontamination_removed_rows.jsonl")}
    initial_clean = {
        idx: item for idx, item in enumerate((row for row in rows if row["split"] == "train"
        and (row["shard"], row["row"] - offsets[row["shard"]]) not in exact), start=1)
    }
    previous = {entry["clean_train_row"] for entry in load_lines(HISTORY / "near_duplicate_removed_rows.jsonl")}
    previous_families = {initial_clean[idx]["image_visible_rgb"] for idx in previous}
    confirmed, uncertain = set(), set()
    train_candidates = {entry["clean_train_row"] for entry in review}
    assert len(review) == 369 and len(train_candidates) == 337 and not (train_candidates & previous)
    for entry in review:
        family = initial_clean[entry["clean_train_row"]]["image_visible_rgb"]
        if entry["decision"] == "confirmed_same_image_family":
            confirmed.add(family)
        elif entry["decision"] == "uncertain":
            uncertain.add(family)
        elif entry["decision"] != "different":
            raise ValueError(f"unsupported review decision: {entry['decision']}")
    eligible = [(idx, row) for idx, row in initial_clean.items() if idx not in previous]
    assert len(eligible) == source_manifest["final_train_rows"]
    tests = {row["image_visible_rgb"] for row in rows if row["split"] in {"geo3k_test", "k12_test"}}
    return source, eligible, confirmed, uncertain, previous_families, tests


def image_fingerprints(rgb):
    gray = rgb.convert("L")
    small = np.asarray(gray.resize((9, 8), Image.Resampling.LANCZOS))
    dhash = int.from_bytes(np.packbits(small[:, :-1] > small[:, 1:]).tobytes(), "big")
    pixels = np.asarray(gray.resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float32)
    coeff = DCT @ pixels @ DCT.T
    low = coeff[:8, :8].reshape(-1)
    phash = int.from_bytes(np.packbits(low > np.median(low[1:])).tobytes(), "big")
    return dhash, phash


DCT = np.cos(np.pi / 32 * (np.arange(32)[None, :] + .5) * np.arange(32)[:, None]).astype(np.float32)
DCT[0] *= 1 / np.sqrt(2)


def prompt_geometry(dataset, image_token_id, row, payload):
    image_processor = dataset.processor.image_processor
    prompt = dataset.render_prompt(row)
    raw_ids = dataset.tokenizer.encode(prompt, add_special_tokens=False)
    if raw_ids.count(image_token_id) != 1:
        raise ValueError("expected exactly one image placeholder")
    with Image.open(BytesIO(payload)) as image:
        size = image.size
    width, height = dataset.image_size(*size)
    patch, merge = image_processor.patch_size, image_processor.merge_size
    height, width = smart_resize(height, width, factor=patch * merge,
        min_pixels=image_processor.size["shortest_edge"], max_pixels=image_processor.size["longest_edge"])
    grid = (1, height // patch, width // patch)
    length = len(raw_ids) - 1 + (grid[1] * grid[2] // merge**2)
    return length, grid


def choose_dev(groups, fingerprints, records):
    # Exact families stay together. Avoid dev families with a perceptual
    # candidate edge to any other family, including mixed-source groups.
    rng = random.Random(SEED)
    hashes = sorted(groups)
    rng.shuffle(hashes)
    image_codes = np.asarray([fingerprints[key] for key in hashes], dtype=np.uint64)
    counts = Counter(records[index]["source"] for indices in groups.values() for index in indices)
    target = {source: round(256 * count / counts.total()) for source, count in counts.items()}
    selected = []
    actual = Counter()
    for position, key in enumerate(hashes):
        indices = groups[key]
        family_sources = {records[index]["source"] for index in indices}
        if len(family_sources) != 1:
            continue
        source = next(iter(family_sources))
        if actual[source] >= target[source]:
            continue
        distance = np.bitwise_count(image_codes ^ image_codes[position])
        close = (distance[:, 0] <= 5) | (distance[:, 1] <= 8)
        close[position] = False
        if close.any():
            continue
        selected.extend(indices)
        actual[source] += len(indices)
        if all(actual[source] >= goal for source, goal in target.items()):
            break
    if len(selected) < 256:
        raise RuntimeError(f"only {len(selected)} independent dev rows")
    dev_groups = {records[index]["visible_rgb"] for index in selected}
    rng.shuffle(selected)
    probe = []
    for index in selected:
        family = records[index]["visible_rgb"]
        if family not in dev_groups:
            continue
        dev_groups.remove(family)
        probe.append(index)
        if len(probe) == 16:
            break
    if len(probe) != 16:
        raise RuntimeError("need 16 distinct dev families for the probe")
    return set(selected), set(probe), dict(actual)


def freeze(root, worktree, review_path, output):
    sys.path.insert(0, str(worktree))
    from shuffle_r1.main import load_config
    from verl.utils.dataset import RLHFDataset
    from verl.utils.tokenizer import get_processor, get_tokenizer

    cfg = load_config([f"config={worktree / 'configs/g4_clean_seed1.yaml'}"])
    model = cfg.worker.actor.model
    options = {"revision": model.revision, "trust_remote_code": model.trust_remote_code,
               "use_fast": True, "local_files_only": True}
    tokenizer = get_tokenizer(model.model_path, **options)
    processor = get_processor(model.model_path, **options)
    dataset = object.__new__(RLHFDataset)
    dataset.tokenizer, dataset.processor = tokenizer, processor
    for field in ("prompt_key", "image_key", "system_prompt", "min_pixels", "max_pixels"):
        setattr(dataset, field, getattr(cfg.data, field))
    image_token_id = tokenizer.convert_tokens_to_ids(processor.image_token)
    review = load_lines(review_path)
    source, identities, confirmed, uncertain, previous, tests = bind_source(root, review)
    if output.exists():
        raise FileExistsError(output)
    groups, fingerprints, records = defaultdict(list), {}, []
    reader = pq.ParquetFile(source)
    for batch in reader.iter_batches(batch_size=64):
        for row in batch.to_pylist():
            position = len(records)
            index, original = identities[position]
            payload = row["images"][0]["bytes"]
            if hashlib.sha256(payload).hexdigest() != original["image_bytes"] or row["source"] != original["source"]:
                raise ValueError(f"source row identity mismatch at first clean row {index}")
            family = original["image_visible_rgb"]
            record = {"source": row["source"], "source_clean_row": index, "original_train_row": original["row"],
                      "original_shard": original["shard"], "visible_rgb": family, "image_bytes": original["image_bytes"]}
            records.append(record)
            if family in confirmed or family in previous or family in tests:
                record["partition"] = "confirmed_excluded"
                continue
            if family in uncertain:
                record["partition"] = "uncertain"
                continue
            try:
                length, grid = prompt_geometry(dataset, image_token_id, row, payload)
            except (ValueError, ZeroDivisionError) as error:
                record.update(partition="prompt_invalid", prompt_error=str(error))
                continue
            record.update(prompt_tokens=length, image_grid_thw=grid)
            if length > cfg.data.max_prompt_length:
                record["partition"] = "prompt_invalid"
                continue
            if family not in fingerprints:
                with Image.open(BytesIO(payload)) as image:
                    rgba = image.convert("RGBA")
                    rgb = Image.alpha_composite(Image.new("RGBA", rgba.size, "white"), rgba).convert("RGB")
                digest = hashlib.sha256(f"{rgb.width}x{rgb.height}:".encode())
                digest.update(rgb.tobytes())
                if digest.hexdigest() != family:
                    raise ValueError(f"visible image identity differs at {index}")
                fingerprints[family] = image_fingerprints(rgb)
            groups[family].append(position)
            # Spot-check the fast size/token audit against HF's full pixel path.
            if position % 257 == 0:
                inputs = processor([dataset.process_image(payload)], [dataset.render_prompt(row)],
                                   add_special_tokens=False, return_tensors="pt")
                if len(inputs.input_ids[0]) != length or tuple(inputs.image_grid_thw[0].tolist()) != grid:
                    raise ValueError(f"prompt geometry does not match the processor at {index}")
        if len(records) % 2048 == 0:
            print(f"Audited {len(records)} rows", flush=True)
    assert len(records) == len(identities) == reader.metadata.num_rows
    dev, probe, dev_sources = choose_dev(groups, fingerprints, records)
    for position, record in enumerate(records):
        record.setdefault("partition", "dev" if position in dev else "train")
        if position in probe:
            record["in_dev16"] = True
    counts = Counter(record["partition"] for record in records)
    print("Split accounting", dict(counts), "dev sources", dev_sources, flush=True)
    train_families = {r["visible_rgb"] for r in records if r["partition"] == "train"}
    dev_families = {r["visible_rgb"] for r in records if r["partition"] == "dev"}
    assert not (train_families & dev_families or (train_families | dev_families) & tests)
    files = {"train.parquet": "train", "dev.parquet": "dev", "dev16.parquet": "dev16",
             "uncertain.parquet": "uncertain", "prompt_invalid.parquet": "prompt_invalid"}
    files = {name: partition for name, partition in files.items()
             if counts[partition] or partition == "dev16"}
    with tempfile.TemporaryDirectory(prefix=".split-staging-", dir=output.parent) as stage:
        staging = Path(stage)
        from contextlib import ExitStack
        with ExitStack() as stack:
            writers = {name: stack.enter_context(pq.ParquetWriter(staging / name, reader.schema_arrow, compression="zstd"))
                       for name in files}
            offset = 0
            for batch in reader.iter_batches(batch_size=128):
                entries = records[offset:offset + batch.num_rows]
                for name, partition in files.items():
                    matches = [r.get("in_dev16", False) if partition == "dev16" else r["partition"] == partition for r in entries]
                    if any(matches):
                        writers[name].write_batch(batch.filter(pa.array(matches)))
                offset += batch.num_rows
        with (staging / "rows.jsonl").open("w", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        manifest = {"schema": 1, "base_data_sha256": sha(source), "source_revision": "b362381652529d67ebc26f5e140bd0a54ba4647d",
            "review_sha256": sha(review_path), "split_seed": SEED,
            "dev_rule": "exact visible RGB families; dev families also have no dHash <= 5 or pHash <= 8 edge to other eligible families",
            "counts": dict(counts), "dev_sources": dev_sources,
            "partition_sources": {name: dict(Counter(r["source"] for r in records if r["partition"] == name)) for name in counts},
            "confirmed_families_excluded": len({r["visible_rgb"] for r in records if r["partition"] == "confirmed_excluded"}),
            "visible_exact_intersections": {"train_dev": 0, "train_public_test": 0, "dev_public_test": 0},
            "largest_prompt_tokens": max(r["prompt_tokens"] for r in records if r["partition"] in {"train", "dev"}),
            "rows_manifest_sha256": sha(staging / "rows.jsonl"),
            "processor": {"model": model.model_path, "revision": model.revision, "min_pixels": cfg.data.min_pixels,
                "max_pixels": cfg.data.max_pixels, "max_prompt_length": cfg.data.max_prompt_length,
                "system_prompt": cfg.data.system_prompt, "image_rendering": "opaque_white_rgb_before_resize"},
            "files": {name: {"rows": pq.ParquetFile(staging / name).metadata.num_rows, "sha256": sha(staging / name)}
                      for name in files}}
        for name, partition in files.items():
            assert manifest["files"][name]["rows"] == (16 if partition == "dev16" else counts[partition])
        write_json(staging / "split_manifest.json", manifest)
        staging.rename(output)
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    freeze(args.state, args.worktree, args.review, args.output)
