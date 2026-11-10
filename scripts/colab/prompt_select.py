"""S3 measurements for the prompt, warm-up and length decisions, on approved train problems only (VM step).

    python -m scripts.colab.prompt_select --model-path <snapshot> --out <out>/prompt_select

docs/plan/S3设计_20261109.md section 6: 64 approved train problems (seed 20261109), with their images. For prompts P0
and P1: 4 samples per problem at the training temperature and top_p, and one greedy completion. The decisions
themselves are taken by scripts/colab/decide_s3.py from ``summary.json``; this step only measures.
"""
import argparse
import json
import math
import random
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261109
VARIANTS = ("p0", "p1")


def pick(items, n, seed=SEED):
    ordered = sorted(items, key=lambda item: item["id"])
    return random.Random(seed).sample(ordered, min(n, len(ordered)))


def percentile(values, q):
    """Nearest-rank percentile (q in 0..100) of a non-empty list: the smallest value with at least q% at or below."""
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, math.ceil(q / 100.0 * len(ordered)) - 1))]


def variant_stats(sampled, greedy, samples):
    """Format and answer rates, finished-completion lengths and GRPO answer signal for one prompt variant."""
    n = len(sampled)
    finished = [r["completion_tokens"] for r in sampled if "</answer>" in r["text"]]
    by_problem = {}
    for record in sampled:
        by_problem.setdefault(record["item"], []).append(bool(record["answer"]["correct"]))
    mixed = sum(len(set(v)) > 1 for v in by_problem.values())
    return {
        "sampled": {"completions": n, "samples_per_problem": samples,
                    "format_rate": sum(r["format"] for r in sampled) / n,
                    "answer_accuracy": sum(r["answer"]["correct"] for r in sampled) / n,
                    "protocol_ok_rate": sum(bool(r["protocol_ok"]) for r in sampled) / n,
                    "budget_exhausted_rate": sum(bool(r["budget_exhausted"]) for r in sampled) / n,
                    "finished": len(finished),
                    "finished_tokens": {"p50": statistics.median(finished), "p90": percentile(finished, 90),
                                        "p95": percentile(finished, 95), "max": max(finished)} if finished else None,
                    "problems_with_mixed_answer_reward": mixed, "problems": len(by_problem)},
        "greedy": {"completions": len(greedy), "format_rate": sum(r["format"] for r in greedy) / max(1, len(greedy)),
                   "answer_accuracy": sum(r["answer"]["correct"] for r in greedy) / max(1, len(greedy)),
                   "budget_exhausted_rate": sum(bool(r["budget_exhausted"]) for r in greedy) / max(1, len(greedy))},
    }


def measure(model, processor, items, verifier, v5_config, temperature, top_p, max_new_tokens, samples=4, batch_size=64,
            seed=SEED, variants=VARIANTS):
    from src.evaluation.generate_v3 import generate, score

    out, records = {}, []
    references = {}
    for item in items:
        for variant in variants:
            for name in ["greedy"] + ["s%d" % j for j in range(samples)]:
                references["%s|%s|%s" % (variant, name, item["id"])] = {
                    "answer": item["answer"], "gold_tokens": item["gold_tokens"],
                    "negative_tokens": item["negative_tokens"], "geometry": item["geometry"]}
    for variant in variants:
        sampled_requests = [{"id": "%s|s%d|%s" % (variant, j, item["id"]), "problem": item["problem"],
                             "image": item["image"]} for item in items for j in range(samples)]
        greedy_requests = [{"id": "%s|greedy|%s" % (variant, item["id"]), "problem": item["problem"],
                            "image": item["image"]} for item in items]
        started = time.time()
        sampled = score(generate(model, processor, sampled_requests, max_new_tokens, batch_size, do_sample=True,
                                 temperature=temperature, top_p=top_p, seed=seed, prompt_variant=variant),
                        references, verifier, v5_config)
        greedy = score(generate(model, processor, greedy_requests, max_new_tokens, batch_size, prompt_variant=variant),
                       references, verifier, v5_config)
        for record in sampled + greedy:
            record["item"] = record["id"].split("|", 2)[2]
            record["decoding"] = "greedy" if "|greedy|" in record["id"] else "sampled"
        out[variant] = dict(variant_stats(sampled, greedy, samples), seconds=round(time.time() - started, 1))
        records += sampled + greedy
    return out, records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--n", type=int, default=64)
    parser.add_argument("--samples", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--experiment", default=str(ROOT / "configs/experiments/rl_v3.json"))
    args = parser.parse_args(argv)
    from src.evaluation.harness import load_model, train_items, write_jsonl
    from src.rewards.answer import AnswerVerifier
    from src.rewards.perception_v5 import V5Config

    config = json.loads(Path(args.experiment).read_text(encoding="utf-8"))
    items = pick(train_items(ROOT, config), args.n)
    model, processor = load_model(args.model_path, config)
    verifier = AnswerVerifier(config["rewards"]["verifier_workers"], config["rewards"]["verifier_timeout"])
    t = config["train"]
    try:
        result, records = measure(model, processor, items, verifier, V5Config.from_dict(config["perception_v5"]),
                                  t["temperature"], t["top_p"], t["max_completion_length"], args.samples, args.batch_size)
    finally:
        verifier.close()
    out = Path(args.out)
    write_jsonl(out / "predictions.jsonl", records)
    summary = {"schema": "p3-prompt-select-v1", "problems": len(items), "sample_ids": [i["id"] for i in items],
               "seed": SEED, "temperature": t["temperature"], "top_p": t["top_p"],
               "max_new_tokens": t["max_completion_length"], "variants": result}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({v: {"format": r["sampled"]["format_rate"], "answer": r["sampled"]["answer_accuracy"]}
                      for v, r in result.items()}))


if __name__ == "__main__":
    main()
