"""Calibrate the v5 geometry oracle on certified facts and measure spray resistance.

    python -m scripts.data.calibrate_perception_v5 --output reports/perception_v5_calibration_<date>

Reads only the approved release (train rows for threshold selection, validation
rows for reporting) and the InterGPS annotations. For every relation it sweeps
the oracle threshold and reports (a) how many certified positive facts would be
falsely refuted and (b) what fraction of deterministic spray claims is refuted.
It also tabulates v4 vs v5 rewards for the spray probes. No model, no GPU.
"""
import argparse
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

from src.data.approved_training_inputs import load_approved
from src.data.intergps_index import load_index
from src.data.perception_v4 import scoped_score
from src.rewards.attacks import as_completion, attack_suite
from src.rewards.claims import parse_claim
from src.rewards.geometry_oracle import ORACLE_VERSION, OracleConfig, refute
from src.rewards.perception_v5 import VERSION, score_v5

ROOT = Path(__file__).resolve().parents[2]
GRID = {
    "PointLiesOnLine": ("line_distance", [0.02, 0.03, 0.04, 0.06, 0.08, 0.10]),
    "Parallel": ("parallel_deg", [5.0, 8.0, 10.0, 15.0, 20.0, 25.0]),
    "Perpendicular": ("perpendicular_deg", [5.0, 8.0, 10.0, 15.0, 20.0, 25.0]),
    "PointLiesOnCircle": ("circle_relative", [0.05, 0.08, 0.10, 0.15, 0.20, 0.25]),
    "Angle": ("angle_value_deg", [10.0, 15.0, 25.0, 35.0, 45.0]),
    "CongruentLength": ("congruent_length_ratio", [1.1, 1.2, 1.35, 1.5, 2.0]),
    "CongruentAngle": ("congruent_angle_deg", [5.0, 10.0, 15.0, 25.0, 40.0]),
}
ENABLE = {"Angle": "check_angle_value", "CongruentLength": "check_congruent_length",
          "CongruentAngle": "check_congruent_angle"}


def _config_for(relation, value):
    field, _ = GRID[relation]
    config = replace(OracleConfig(), **{field: value})
    if relation in ENABLE:
        config = replace(config, **{ENABLE[relation]: True})
    return config


def calibrate(rows, index, include_spray=True):
    positives = defaultdict(list)  # relation -> [(claim, geometry, sample_id)]
    existence = Counter()
    for row in rows:
        geometry = index[str(row["original_id"])]
        for token in row["certified_positive_tokens"]:
            claim = parse_claim(token)
            if not claim.valid:
                existence["unparseable_certified"] += 1
                continue
            positives[claim.relation].append((claim, geometry, row["sample_id"]))
            reason = refute(claim, geometry, OracleConfig())
            if reason in {"unknown_point", "no_circle_in_diagram", "unknown_circle"}:
                existence[reason] += 1
    sprays = defaultdict(list)
    if include_spray:
        for row in rows:
            geometry = index[str(row["original_id"])]
            gold = set(row["certified_positive_tokens"])
            suite = attack_suite(geometry, row["certified_positive_tokens"], max_claims=10_000)
            for text in suite["incidence_spray"] + suite["pair_spray"] + suite["value_spray"]:
                claim = parse_claim(text)
                if claim.valid and text not in gold:
                    sprays[claim.relation].append((claim, geometry))
    sweep = {}
    for relation, (field, values) in GRID.items():
        entries = []
        for value in values:
            config = _config_for(relation, value)
            false_hits = [sid for claim, geometry, sid in positives.get(relation, []) if refute(claim, geometry, config)]
            spray = sprays.get(relation, [])
            refuted = sum(bool(refute(claim, geometry, config)) for claim, geometry in spray)
            entries.append({"threshold": value, "certified": len(positives.get(relation, [])),
                            "false_refutations": len(false_hits), "false_refutation_ids": sorted(set(false_hits))[:20],
                            "spray_claims": len(spray), "spray_refuted_fraction": refuted / len(spray) if spray else None})
        sweep[relation] = {"field": field, "entries": entries}
    return {"positives_by_relation": {k: len(v) for k, v in sorted(positives.items())},
            "existence_refutations_of_certified": dict(existence), "sweep": sweep}


def attack_table(rows, index):
    table = defaultdict(lambda: {"v4": [], "v5": [], "beats_honest_half_v4": 0, "beats_honest_half_v5": 0})
    for row in rows:
        geometry = index[str(row["original_id"])]
        gold = row["certified_positive_tokens"]
        suite = attack_suite(geometry, gold)
        honest_v4 = scoped_score(as_completion(suite["honest_half"]), gold, [])["reward"]
        honest_v5 = score_v5(as_completion(suite["honest_half"]), gold, geometry)["reward"]
        for name, claims in suite.items():
            if not claims:
                continue
            text = as_completion(claims)
            a, b = scoped_score(text, gold, [])["reward"], score_v5(text, gold, geometry)["reward"]
            entry = table[name]
            entry["v4"].append(a)
            entry["v5"].append(b)
            entry["beats_honest_half_v4"] += a > honest_v4
            entry["beats_honest_half_v5"] += b > honest_v5
    return {name: {"rows": len(e["v4"]), "mean_v4": statistics.fmean(e["v4"]), "mean_v5": statistics.fmean(e["v5"]),
                   "share_beating_honest_half_v4": e["beats_honest_half_v4"] / len(e["v4"]),
                   "share_beating_honest_half_v5": e["beats_honest_half_v5"] / len(e["v5"])}
            for name, e in table.items()}


def load_release(root):
    release = root / "data/portable_release"
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    train = load_approved(release / "manifest.json", manifest["approved_training_files"][0])
    validation = []
    for name in manifest.get("approved_evaluation_files", []):
        validation += [json.loads(x) for x in (release / name).read_text(encoding="utf-8").splitlines() if x.strip()]
    return train, validation


def summary_markdown(result):
    lines = [f"# v5 几何证伪校准（{result['oracle_version']}）", "",
             f"train 行数 {result['train_rows']}，validation 行数 {result['validation_rows']}。阈值只按 train 选择；"
             "validation 只报告。数字由脚本生成，未手工修改。", "",
             "| 关系 | 阈值字段 | 阈值 | train 认证正例 | train 误杀 | val 误杀 | 罗列断言被证伪比例 |", "|---|---|---|---|---|---|---|"]
    for relation, block in result["train"]["sweep"].items():
        val_entries = {e["threshold"]: e for e in result["validation"]["sweep"][relation]["entries"]}
        for e in block["entries"]:
            power = "—" if e["spray_refuted_fraction"] is None else f"{e['spray_refuted_fraction']:.3f}"
            lines.append(f"| {relation} | {block['field']} | {e['threshold']} | {e['certified']} | {e['false_refutations']} | "
                         f"{val_entries[e['threshold']]['false_refutations']} | {power} |")
    lines += ["", "## 罗列攻击（train，每题一组探针）", "",
              "| 探针 | 题数 | v4 均值 | v5 均值 | v4 高于诚实读一半的比例 | v5 高于诚实读一半的比例 |", "|---|---|---|---|---|---|"]
    for name, e in result["attacks_train"].items():
        lines.append(f"| {name} | {e['rows']} | {e['mean_v4']:.3f} | {e['mean_v5']:.3f} | "
                     f"{e['share_beating_honest_half_v4']:.3f} | {e['share_beating_honest_half_v5']:.3f} |")
    lines += ["", f"认证正例被存在性规则否定的计数（train）：{result['train']['existence_refutations_of_certified']}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root = Path(args.root)
    train, validation = load_release(root)
    ids = [r["original_id"] for r in train + validation]
    index = load_index(root / "data/project3_audit/intergps_annotations.jsonl", ids)
    result = {"schema": "v5-calibration-v1", "oracle_version": ORACLE_VERSION, "reward_version": VERSION,
              "train_rows": len(train), "validation_rows": len(validation),
              "train": calibrate(train, index), "validation": calibrate(validation, index, include_spray=False),
              "attacks_train": attack_table(train, index)}
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "calibration.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "summary.md").write_text(summary_markdown(result), encoding="utf-8")
    print(json.dumps({"event": "calibration_done", "output": str(out), "train_rows": len(train)}))
    return result


if __name__ == "__main__":
    main()
