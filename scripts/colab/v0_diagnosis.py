"""V0 diagnosis on the 82 approved validation problems: measurement only, never a decision (VM step).

    python -m scripts.colab.v0_diagnosis --model-path <snapshot> --out <out>/v0_val82

docs/plan/S3设计_20261109.md section 6 (last paragraph) and D44: greedy decoding of the untrained model under three
conditions on the same 82 problems: protocol prompt P0 with the image, P0 without the image, and the answer-only
diagnostic prompt with the image (how much the three-part protocol itself costs V0). Every completion gets a failure
class. The numbers are reported in the S3 stage report; the S5 evaluation of V0 is separate and uses the final rules.
"""
import argparse
import json
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONDITIONS = [("p0_image", "p0", True), ("p0_blind", "p0", False), ("answer_only_image", "answer_only", True)]


def repeats(text, max_period=200):
    """True when the completion ends in the same block repeated three times (a decoding loop)."""
    for period in range(5, max_period + 1):
        tail = text[-3 * period:]
        if len(tail) == 3 * period and tail[:period] == tail[period:2 * period] == tail[2 * period:]:
            return True
    return False


def failure_class(text, protocol_ok):
    """One label per completion, from the text alone."""
    from src.rewards.claims import parse_block

    if protocol_ok:
        return "complete"
    tags = {tag: tag in text for tag in ("<perception>", "</perception>", "<think>", "<answer>", "</answer>")}
    if not any(tags.values()):
        claims, _ = parse_block(text, 10 ** 6)
        return "facts_without_tags" if any(c.valid for c in claims) else "no_tags"
    if tags["<answer>"] and tags["</answer>"]:
        return "answer_but_malformed"
    if tags["<think>"]:
        return "perception_and_think_no_answer" if tags["<perception>"] else "think_no_answer"
    if tags["<perception>"]:
        return "perception_only"
    return "other"


def annotate(records):
    for record in records:
        record["failure_class"] = failure_class(record["text"], record["protocol_ok"])
        record["repetition_loop"] = bool(record["budget_exhausted"]) and repeats(record["text"])
    return records


def condition_summary(records):
    from src.evaluation.generate_v3 import summarize

    out = summarize(records)
    out["failure_classes"] = dict(Counter(r["failure_class"] for r in records).most_common())
    out["repetition_loops"] = sum(r["repetition_loop"] for r in records)
    return out


def run(model, processor, items, verifier, v5_config, max_new_tokens, batch_size=32):
    from src.evaluation.generate_v3 import generate, score

    results, summary = [], {}
    for name, variant, with_image in CONDITIONS:
        references, requests = {}, []
        for item in items:
            rid = "%s|%s" % (name, item["id"])
            references[rid] = {"answer": item["answer"], "gold_tokens": item["gold_tokens"] if variant != "answer_only" else [],
                               "negative_tokens": item["negative_tokens"], "geometry": item["geometry"]}
            requests.append({"id": rid, "problem": item["problem"], "image": item["image"] if with_image else None})
        started = time.time()
        scored = annotate(score(generate(model, processor, requests, max_new_tokens, batch_size, prompt_variant=variant),
                                references, verifier, v5_config))
        for record in scored:
            record.update(condition=name, item=record["id"].split("|", 1)[1])
        summary[name] = dict(condition_summary(scored), seconds=round(time.time() - started, 1))
        results += scored
    return results, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--experiment", default=str(ROOT / "configs/experiments/rl_v3.json"))
    args = parser.parse_args(argv)
    from src.evaluation.harness import load_model, val82_items, write_jsonl
    from src.rewards.answer import AnswerVerifier
    from src.rewards.perception_v5 import V5Config

    config = json.loads(Path(args.experiment).read_text(encoding="utf-8"))
    items = val82_items(ROOT, config)
    model, processor = load_model(args.model_path, config)
    verifier = AnswerVerifier(config["rewards"]["verifier_workers"], config["rewards"]["verifier_timeout"])
    try:
        records, summary = run(model, processor, items, verifier, V5Config.from_dict(config["perception_v5"]),
                               config["train"]["max_completion_length"], args.batch_size)
    finally:
        verifier.close()
    out = Path(args.out)
    write_jsonl(out / "predictions.jsonl", records)
    (out / "summary.json").write_text(json.dumps({"schema": "p3-v0-diagnosis-v1", "problems": len(items),
                                                  "decoding": "greedy", "batch_size": args.batch_size,
                                                  "max_new_tokens": config["train"]["max_completion_length"],
                                                  "conditions": summary}, indent=2, ensure_ascii=False),
                                     encoding="utf-8")
    print(json.dumps({k: {"answer": v["answer_accuracy"], "protocol": v["protocol_ok_rate"]} for k, v in summary.items()}))


if __name__ == "__main__":
    main()
