"""Cluster-bootstrap interval of the S3 format rates (supporting number for docs/plan/S4预注册_20261110.md section 2).

Reads the prompt-selection predictions of the S3 ``v0`` run from its results branch and, for each prompt variant,
resamples the 64 approved train problems with replacement (10,000 times, seed 20261109, percentile interval, as in
src/evaluation/stats.py) to give a 95% interval of the temperature-1 format rate. Only train problems are involved.
The S3 warm-up rule compares the point estimate with 0.50 (S3 design section 6); this interval is reported and
decides nothing.

    git fetch origin 'refs/heads/results/*:refs/remotes/origin/results/*'
    python reports/s4_preregistration_20261110/format_rate_interval.py
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RUN = "v0-20261110T023008Z-60fc"
REF = "origin/results/" + RUN
BASE = "reports/colab_runs_20261110/%s/prompt_select/" % RUN
SEED, RESAMPLES = 20261109, 10000


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout.decode("utf-8")


def interval(per_problem, seed=SEED, resamples=RESAMPLES):
    """95% percentile interval of sum(hits) / sum(completions) when problems are resampled with replacement."""
    keys = sorted(per_problem)
    hits = np.array([per_problem[k][0] for k in keys], dtype=np.float64)
    counts = np.array([per_problem[k][1] for k in keys], dtype=np.float64)
    picks = np.random.default_rng(seed).integers(0, len(keys), size=(resamples, len(keys)))
    rates = hits[picks].sum(axis=1) / counts[picks].sum(axis=1)
    low, high = np.percentile(rates, [2.5, 97.5])
    return float(low), float(high)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ref", default=REF, help="git ref of the results branch")
    parser.add_argument("--out", default=str(Path(__file__).with_name("format_rate_interval.json")))
    args = parser.parse_args(argv)
    predictions = BASE + "predictions.jsonl"
    records = [json.loads(line) for line in git("show", "%s:%s" % (args.ref, predictions)).splitlines() if line.strip()]
    summary = json.loads(git("show", "%s:%s" % (args.ref, BASE + "summary.json")))
    out = {"schema": "p3-s4-format-rate-interval-v1", "run": RUN, "ref": args.ref,
           "ref_commit": git("rev-parse", args.ref).strip(),
           "predictions_commit": git("log", "-1", "--format=%H", args.ref, "--", predictions).strip(),
           "source": predictions, "decoding": "sampled (temperature 1.0, 4 per problem)", "cluster": "train problem",
           "resamples": RESAMPLES, "seed": SEED, "interval": "95% percentile", "variants": {}}
    for variant in sorted(summary["variants"]):
        sampled = [r for r in records if r["prompt_variant"] == variant and r["decoding"] == "sampled"]
        per_problem = {}
        for record in sampled:
            hits, n = per_problem.get(record["item"], (0, 0))
            per_problem[record["item"]] = (hits + int(record["format"] == 1.0), n + 1)
        rate = sum(h for h, _ in per_problem.values()) / sum(n for _, n in per_problem.values())
        expected = summary["variants"][variant]["sampled"]
        if abs(rate - expected["format_rate"]) > 1e-12 or len(sampled) != expected["completions"]:
            raise SystemExit("%s: recomputed format rate %.6f over %d completions differs from summary.json (%.6f, %d)"
                             % (variant, rate, len(sampled), expected["format_rate"], expected["completions"]))
        low, high = interval(per_problem)
        out["variants"][variant] = {"problems": len(per_problem), "completions": len(sampled),
                                    "format_reward_1": sum(h for h, _ in per_problem.values()), "format_rate": rate,
                                    "ci95": [round(low, 4), round(high, 4)]}
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out["variants"], indent=1))


if __name__ == "__main__":
    main()
