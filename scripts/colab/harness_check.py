"""Run the S5 evaluation code path end to end on train-only inputs (VM step; S3 design section 7, revision 2).

    python -m scripts.colab.harness_check --model-path <snapshot> --sources <public> --out <out>/harness_check

* E1 path: the first 16 approved train rows by sample_id, original image, v5 verdicts.
* Answer conditions: 32 CF-Geo development items from public train (reports/cfgeo_20261109/cfgeo_dev_train.json,
  seed 20261109) under original, blind, swap (fixed pairing among the 32), CF k=1 and CF k=2.
* The statistics module on V0's own outputs (original vs blind, CF k=2 vs k=1), to exercise it on real records.

Every input is train, so nothing here touches held-out data; the numbers only show that the code path works.
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "reports/cfgeo_20261109/cfgeo_dev_train.json"
SEED = 20261109


def dev_items(sources, n=32, seed=SEED):
    from src.evaluation.harness import cfgeo_items

    items = cfgeo_items(DEV, sources)
    return random.Random(seed).sample(items, min(n, len(items)))


def compare(records_a, records_b, resamples=10000):
    from src.evaluation.stats import align, paired_ratio, per_item

    a = per_item(records_a, lambda r: r["answer"]["correct"])
    b = per_item(records_b, lambda r: r["answer"]["correct"])
    return paired_ratio(*align(a, b), resamples=resamples)


def run(model, processor, e1_items, items, verifier, v5_config, max_new_tokens, batch_size=32, resamples=10000):
    from src.evaluation.eval_sets import swap_pairing
    from src.evaluation.harness import CONDITIONS, run_condition, summarize

    records = {"e1_original": run_condition(model, processor, e1_items, "original", verifier, v5_config,
                                            max_new_tokens=max_new_tokens, batch_size=batch_size, model_name="V0")}
    swap = swap_pairing([{"id": i["id"], "pixel": i["cluster"]} for i in items])
    for condition in CONDITIONS:
        records[condition] = run_condition(model, processor, items, condition, verifier, v5_config,
                                           max_new_tokens=max_new_tokens, batch_size=batch_size, swap=swap,
                                           model_name="V0")
    summary = {name: summarize(rows) for name, rows in records.items()}
    comparisons = {"original_vs_blind": compare(records["original"], records["blind"], resamples),
                   "cf_k2_vs_cf_k1": compare(records["cf_k2"], records["cf_k1"], resamples)}
    checks = {
        "e1_scored": summary["e1_original"].get("e1", {}).get("items") == len(e1_items),
        "all_conditions_complete": all(summary[c]["n"] == len(items) for c in CONDITIONS),
        "blind_has_no_image": not any(r["has_image"] for r in records["blind"]),
        "swap_shows_other_images": all(r["shown_image_of"] != r["item"] for r in records["swap"]),
        "cf_k2_old_answer_measured": "old_answer_rate" in summary["cf_k2"],
        "statistics_ran": all(c["resamples"] == resamples for c in comparisons.values()),
    }
    return records, {"summary": summary, "comparisons": comparisons, "checks": checks, "ok": all(checks.values()),
                     "swap": swap}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--sources", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--experiment", default=str(ROOT / "configs/experiments/rl_v3.json"))
    args = parser.parse_args(argv)
    from src.evaluation.harness import load_model, train_items, write_jsonl
    from src.rewards.answer import AnswerVerifier
    from src.rewards.perception_v5 import V5Config

    config = json.loads(Path(args.experiment).read_text(encoding="utf-8"))
    e1_items, items = train_items(ROOT, config, 16), dev_items(args.sources)
    model, processor = load_model(args.model_path, config)
    verifier = AnswerVerifier(config["rewards"]["verifier_workers"], config["rewards"]["verifier_timeout"])
    try:
        records, report = run(model, processor, e1_items, items, verifier, V5Config.from_dict(config["perception_v5"]),
                              config["train"]["max_completion_length"])
    finally:
        verifier.close()
    out = Path(args.out)
    write_jsonl(out / "predictions.jsonl", [r for rows in records.values() for r in rows])
    report.update(schema="p3-harness-check-v1", e1_items=[i["id"] for i in e1_items], items=[i["id"] for i in items])
    (out / "summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["checks"]))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
