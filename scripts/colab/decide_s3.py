"""Apply the pre-registered S3 decision rules to the measurements of a ``v0`` run (VM step, standard library only).

    python -m scripts.colab.decide_s3 --out-dir <run dir> [--allow-missing]

Rules (docs/plan/S3设计_20261109.md section 6; measurements are on approved train problems only):

* prompt: P1 replaces P0 when, at the training temperature, its format rate is at least 0.10 higher and its answer
  accuracy at most 0.02 lower;
* warm-up: a shared format warm-up is needed when the chosen prompt's format rate is below 0.50;
* length: 1024 new tokens stay when the 95th percentile of completions that wrote ``</answer>`` is at most 870,
  otherwise 1536 (with fewer than 20 such completions the length is not decided here: it stays 1024 and is measured
  again in the S4 pilot);
* resolution: max_pixels stays 802,816 for every arm and evaluation; the share of evaluation images it resizes is
  reported;
* vLLM importance sampling (D41): every step's mean weight in [0.9, 1.1] and mean |log-prob difference| <= 0.10,
  otherwise every S4 arm generates with HF. No measurement counts as a failure.

Writes ``s3_decisions.json``; V0's val82 diagnosis is copied in as a measurement and never used by a rule.
"""
import argparse
import json
import sys
from pathlib import Path

SCHEMA = "p3-s3-decisions-v1"
FORMAT_GAIN, ANSWER_DROP, WARMUP_BELOW = 0.10, 0.02, 0.50
P95_LIMIT, LONG_LENGTH, DEFAULT_LENGTH, MIN_FINISHED = 870, 1536, 1024, 20
IS_RANGE, LOGP_LIMIT = (0.9, 1.1), 0.10
MAX_PIXELS = 802816
EPS = 1e-12


def _load(path):
    path = Path(path)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def prompt_rule(variants):
    p0, p1 = variants["p0"]["sampled"], variants["p1"]["sampled"]
    gain = p1["format_rate"] - p0["format_rate"]
    change = p1["answer_accuracy"] - p0["answer_accuracy"]
    chosen = "p1" if gain >= FORMAT_GAIN - EPS and change >= -ANSWER_DROP - EPS else "p0"
    return {"chosen": chosen, "format_gain": gain, "answer_change": change,
            "rule": "P1 if format gain >= %.2f and answer change >= -%.2f (temperature-1 samples)" % (FORMAT_GAIN, ANSWER_DROP)}


def warmup_rule(format_rate):
    return {"needed": format_rate < WARMUP_BELOW, "format_rate": format_rate, "threshold": WARMUP_BELOW}


def length_rule(sampled):
    finished, tokens = sampled.get("finished", 0), sampled.get("finished_tokens") or {}
    if finished < MIN_FINISHED or not tokens:
        return {"value": DEFAULT_LENGTH, "decided": False, "finished": finished, "p95": tokens.get("p95"),
                "reason": "fewer than %d completions wrote </answer>; keep %d and measure again in the S4 pilot"
                          % (MIN_FINISHED, DEFAULT_LENGTH)}
    value = DEFAULT_LENGTH if tokens["p95"] <= P95_LIMIT else LONG_LENGTH
    return {"value": value, "decided": True, "finished": finished, "p95": tokens["p95"],
            "rule": "%d if p95 <= %d else %d" % (DEFAULT_LENGTH, P95_LIMIT, LONG_LENGTH)}


def is_rule(log_history):
    steps = [h for h in (log_history or []) if isinstance(h, dict) and "sampling/importance_sampling_ratio/mean" in h]
    if not steps:
        return {"value": "hf", "passed": False, "steps": [], "reason": "the vLLM importance-sampling check produced no "
                "measurement; the pre-registered fallback is HF generation for every arm"}
    rows = [{"step": h.get("step"), "ratio_mean": h["sampling/importance_sampling_ratio/mean"],
             "logp_difference_mean": h.get("sampling/sampling_logp_difference/mean"),
             "logp_difference_max": h.get("sampling/sampling_logp_difference/max")} for h in steps]
    passed = all(IS_RANGE[0] <= r["ratio_mean"] <= IS_RANGE[1] and r["logp_difference_mean"] is not None
                 and r["logp_difference_mean"] <= LOGP_LIMIT for r in rows)
    return {"value": "vllm" if passed else "hf", "passed": passed, "steps": rows,
            "rule": "every step: mean weight in [%.1f, %.1f] and mean |dlogp| <= %.2f" % (IS_RANGE + (LOGP_LIMIT,))}


def decide(out_dir, allow_missing=False):
    out = Path(out_dir)
    prompt = _load(out / "prompt_select" / "summary.json")
    checks = _load(out / "eval_sets_check.json") or {}
    cfgeo = _load(out / "cfgeo_build.json") or {}
    harness = _load(out / "harness_check" / "summary.json") or {}
    v0 = _load(out / "v0_val82" / "summary.json")
    decisions = {"schema": SCHEMA, "design": "docs/plan/S3设计_20261109.md section 6",
                 "inputs": {"eval_sets_identical": checks.get("ok"), "cfgeo_rebuilt": cfgeo.get("ok"),
                            "harness_check": harness.get("ok")},
                 "resolution": {"max_pixels": MAX_PIXELS, "evaluation_images": checks.get("resolution")},
                 "generation_backend": is_rule(_load(out / "is_check" / "log_history.json")),
                 "v0_val82_measured_only": (v0 or {}).get("conditions")}
    if prompt:
        choice = prompt_rule(prompt["variants"])
        sampled = prompt["variants"][choice["chosen"]]["sampled"]
        decisions.update(prompt=dict(choice, problems=prompt["problems"]), warmup=warmup_rule(sampled["format_rate"]),
                         max_completion_length=length_rule(sampled),
                         grpo_answer_signal={"problems_with_mixed_answer_reward": sampled["problems_with_mixed_answer_reward"],
                                             "problems": sampled["problems"]})
    elif not allow_missing:
        raise SystemExit("prompt_select/summary.json is missing: the prompt, warm-up and length decisions cannot be taken")
    decisions["complete"] = bool(prompt) and all(v is True for v in decisions["inputs"].values())
    return decisions


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--allow-missing", action="store_true", help="dry runs: write what can be decided")
    args = parser.parse_args(argv)
    decisions = decide(args.out_dir, args.allow_missing)
    (Path(args.out_dir) / "s3_decisions.json").write_text(json.dumps(decisions, indent=2, ensure_ascii=False),
                                                          encoding="utf-8")
    print(json.dumps({k: decisions.get(k) for k in ("prompt", "warmup", "max_completion_length")}, ensure_ascii=False)[:2000])
    print("generation backend for S4: %s" % decisions["generation_backend"]["value"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
