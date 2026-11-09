"""V0 probe: greedy protocol-v3 generations of the untrained model on a few validation problems.

    python -m scripts.colab.v0_probe --model-path <snapshot> --out <out>/v0_probe --n 16

Early signal for decisions that must be frozen before training (format
compliance, completion length vs. the 1024-token budget). Uses the first ``n``
approved validation rows by sample_id, each with and without its image. Small n:
an engineering probe, not an evaluation result.
"""
import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_validation(root, config):
    manifest = Path(root) / config["data"]["manifest"]
    release = json.loads(manifest.read_text(encoding="utf-8"))
    rows = []
    for name in release.get("approved_evaluation_files", []):
        rows += [json.loads(x) for x in (manifest.parent / name).read_text(encoding="utf-8").splitlines() if x.strip()]
    return sorted(rows, key=lambda r: r["sample_id"])


def run_probe(model, processor, rows, index, root, max_new_tokens, batch_size, verifier):
    from PIL import Image

    from src.evaluation.generate_v3 import generate, score, summarize

    references = {}
    image_requests, blind_requests = [], []
    for row in rows:
        geometry = index[str(row["original_id"])]
        references[row["sample_id"]] = {"answer": str(row["reference_answer"]), "gold_tokens": row["certified_positive_tokens"],
                                        "negative_tokens": row["certified_negative_tokens"], "geometry": geometry}
        references["blind:" + row["sample_id"]] = references[row["sample_id"]]
        image_requests.append({"id": row["sample_id"], "problem": row["problem"],
                               "image": Image.open(Path(root) / row["image_path"]).convert("RGB")})
        blind_requests.append({"id": "blind:" + row["sample_id"], "problem": row["problem"], "image": None})
    started = time.time()
    with_image = score(generate(model, processor, image_requests, max_new_tokens, batch_size), references, verifier)
    blind = score(generate(model, processor, blind_requests, max_new_tokens, batch_size), references, verifier)
    return {"with_image": with_image, "blind": blind, "summary": {"with_image": summarize(with_image),
                                                                  "blind": summarize(blind)},
            "seconds": round(time.time() - started, 1)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--n", type=int, default=16)
    parser.add_argument("--max-new-tokens", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--experiment", default=str(ROOT / "configs/experiments/rl_v3.json"))
    args = parser.parse_args(argv)
    import torch
    from transformers import AutoProcessor

    from src.data.intergps_index import load_index
    from src.evaluation.generate_v3 import write_jsonl
    from src.rewards.answer import AnswerVerifier
    from src.training.hf_compat import vision_model_class

    config = json.loads(Path(args.experiment).read_text(encoding="utf-8"))
    m = config["model"]
    rows = load_validation(ROOT, config)[: args.n]
    index = load_index(ROOT / config["data"]["intergps_annotations"], [r["original_id"] for r in rows])
    processor = AutoProcessor.from_pretrained(args.model_path, max_pixels=m["max_pixels"], min_pixels=m["min_pixels"])
    model = vision_model_class().from_pretrained(args.model_path, dtype=torch.bfloat16,
                                                 attn_implementation=m["attn_implementation"]).to("cuda").eval()
    verifier = AnswerVerifier(config["rewards"]["verifier_workers"], config["rewards"]["verifier_timeout"])
    try:
        result = run_probe(model, processor, rows, index, ROOT, args.max_new_tokens or config["train"]["max_completion_length"],
                           args.batch_size, verifier)
    finally:
        verifier.close()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "predictions.jsonl", result["with_image"] + result["blind"])
    summary = {"n": len(rows), "sample_ids": [r["sample_id"] for r in rows], "seconds": result["seconds"],
               "decoding": "greedy, repetition_penalty=1.0, max_new_tokens=%d" % (args.max_new_tokens or config["train"]["max_completion_length"]),
               **result["summary"]}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
