"""Calibrate the v5 geometry oracle on certified facts and measure spray resistance.

    python -m scripts.data.calibrate_perception_v5 --output reports/perception_v5_calibration_<date>

Reads only the approved release (train rows for threshold selection, validation
rows for reporting) and the InterGPS annotations. For every relation it sweeps
the oracle threshold and reports (a) how many certified positive facts would be
falsely refuted and (b) what fraction of deterministic spray claims is refuted.
At the registered thresholds it also reports the per-diagram consistency gate,
what the gated reward still refutes, a leave-one-out estimate of the residual
false-refutation rate with Wilson intervals, and every raw false refutation with
the measured quantity (D35). It tabulates v4 vs v5 rewards for the spray probes,
with and without the gate. No model, no GPU.
"""
import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

from src.data.approved_training_inputs import load_approved
from src.data.intergps_index import load_index
from src.data.perception_v4 import scoped_score
from src.rewards.attacks import as_completion, attack_suite
from src.rewards.claims import parse_claim
from src.rewards.geometry_oracle import ORACLE_VERSION, OracleConfig, measure, reason_family, refute
from src.rewards.perception_v5 import VERSION, V5Config, consistency_gate, score_v5

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "v5-calibration-v2"
DEFAULT_ON = ["PointLiesOnLine", "Parallel", "Perpendicular", "PointLiesOnCircle"]
# Acceptance for the gated oracle (D35), fixed from the registered reward weights before any gated number existed:
# a falsely refuted true claim costs alpha instead of beta, so the extra expected cost is (alpha - beta) * p.
# Keeping it at most beta / 2 gives p <= 0.1 / 1.8 = 5.6 %; rounded down to 5 %.
LOO_LIMIT = 0.05
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
    result = {"positives_by_relation": {k: len(v) for k, v in sorted(positives.items())},
              "existence_refutations_of_certified": dict(existence), "sweep": sweep}
    result.update(gate_report(rows, index))
    return result


def wilson(k, n, z=1.96):
    """95 % Wilson score interval for k successes in n trials."""
    if not n:
        return None
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)]


def gate_report(rows, index, config=OracleConfig()):
    """Consistency gate at the registered thresholds (D35).

    * ``gate``: diagrams whose annotation refutes one of their own certified facts, by family;
    * ``after_gate``: certified facts the gated reward would still refute (0 by construction; checks the code);
    * ``loo``: leave-one-out residual - each certified fact is treated as an unseen true claim, the gate is
      computed from the diagram's *other* certified facts, and the fact counts if it would still be refuted.
      This estimates how often a true but uncertified claim is falsely refuted, which is what the reward pays;
    * ``raw_false_refutations``: every refuted certified fact with the measured quantity (diagnostics).
    """
    gated_rows, after, raw = {}, Counter(), []
    loo = defaultdict(lambda: {"certified": 0, "residual": 0, "residual_ids": []})
    for row in rows:
        geometry = index[str(row["original_id"])]
        gold = list(row["certified_positive_tokens"])
        gate = consistency_gate(gold, geometry, config)
        if gate:
            gated_rows[row["sample_id"]] = gate
        for i, token in enumerate(gold):
            claim = parse_claim(token)
            if not claim.valid or claim.relation not in DEFAULT_ON:
                continue
            reason = refute(claim, geometry, config)
            if reason is not None:
                raw.append({"sample_id": row["sample_id"], "certified": token, "reason": reason,
                            "measured": measure(claim, geometry)})
                if reason_family(reason) not in gate:
                    after[claim.relation] += 1
            entry = loo[claim.relation]
            entry["certified"] += 1
            others = consistency_gate(gold[:i] + gold[i + 1:], geometry, config)
            if reason is not None and reason_family(reason) not in others:
                entry["residual"] += 1
                entry["residual_ids"].append(row["sample_id"])
    loo_out = {}
    for relation in DEFAULT_ON:
        entry = loo.get(relation, {"certified": 0, "residual": 0, "residual_ids": []})
        n, k = entry["certified"], entry["residual"]
        loo_out[relation] = {"certified": n, "residual": k, "rate": round(k / n, 4) if n else None,
                             "ci95": wilson(k, n), "within_limit": (k / n <= LOO_LIMIT) if n else None,
                             "residual_ids": sorted(set(entry["residual_ids"]))[:30]}
    pooled_n = sum(v["certified"] for v in loo_out.values())
    pooled_k = sum(v["residual"] for v in loo_out.values())
    families = Counter(family for gate in gated_rows.values() for family in gate)
    return {"gate": {"rows": len(gated_rows), "by_family": dict(families),
                     "rows_detail": dict(sorted(gated_rows.items()))},
            "after_gate": {relation: after.get(relation, 0) for relation in DEFAULT_ON},
            "loo": {"limit": LOO_LIMIT, "relations": loo_out,
                    "pooled": {"certified": pooled_n, "residual": pooled_k,
                               "rate": round(pooled_k / pooled_n, 4) if pooled_n else None,
                               "ci95": wilson(pooled_k, pooled_n)}},
            "raw_false_refutations": raw[:300]}


def attack_table(rows, index, config=V5Config()):
    table = defaultdict(lambda: {"v4": [], "v5": [], "beats_honest_half_v4": 0, "beats_honest_half_v5": 0})
    for row in rows:
        geometry = index[str(row["original_id"])]
        gold = row["certified_positive_tokens"]
        suite = attack_suite(geometry, gold)
        honest_v4 = scoped_score(as_completion(suite["honest_half"]), gold, [])["reward"]
        honest_v5 = score_v5(as_completion(suite["honest_half"]), gold, geometry, config=config)["reward"]
        for name, claims in suite.items():
            if not claims:
                continue
            text = as_completion(claims)
            a, b = scoped_score(text, gold, [])["reward"], score_v5(text, gold, geometry, config=config)["reward"]
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
    train, val = result["train"], result["validation"]
    lines += ["", "## 一致性门控（D35，奖励实际使用的口径）", "",
              "若一张图的标注否定了它自己的某条认证事实，这张图上同一类检验（坐标类或存在性类）不再用来证伪其他断言。",
              "", "| | 被门控的图 | 按类别 | 门控后仍被证伪的认证正例（默认开启的四类） |", "|---|---|---|---|",
              f"| train | {train['gate']['rows']} / {result['train_rows']} | {train['gate']['by_family']} | "
              f"{sum(train['after_gate'].values())} |",
              f"| validation | {val['gate']['rows']} / {result['validation_rows']} | {val['gate']['by_family']} | "
              f"{sum(val['after_gate'].values())} |",
              "", f"## 留一法残余误杀率（train；上限 {LOO_LIMIT:.0%}，由 α、β 推出）", "",
              "把每条认证事实当作没见过的真实断言：门控只用同一张图的其他认证事实计算，看这条事实是否仍被证伪。"
              "这估计了奖励对未认证的真实断言的误杀率。", "",
              "| 关系 | 认证正例 | 残余误杀 | 比例 | 95% 区间 | 不超过上限 |", "|---|---|---|---|---|---|"]
    for relation, e in train["loo"]["relations"].items():
        ci = "—" if e["ci95"] is None else f"{e['ci95'][0]:.3f}–{e['ci95'][1]:.3f}"
        rate = "—" if e["rate"] is None else f"{e['rate']:.3f}"
        lines.append(f"| {relation} | {e['certified']} | {e['residual']} | {rate} | {ci} | "
                     f"{'—' if e['within_limit'] is None else ('是' if e['within_limit'] else '否')} |")
    pooled = train["loo"]["pooled"]
    if pooled["rate"] is not None:
        lines.append(f"| 合计 | {pooled['certified']} | {pooled['residual']} | {pooled['rate']:.3f} | "
                     f"{pooled['ci95'][0]:.3f}–{pooled['ci95'][1]:.3f} | |")
    lines += ["", "## 原始误杀明细（train，默认阈值，门控前）", "", "| 题 | 认证事实 | 原因 | 测量值 |", "|---|---|---|---|"]
    for e in train["raw_false_refutations"][:60]:
        lines.append(f"| {e['sample_id']} | `{e['certified']}` | {e['reason']} | {json.dumps(e['measured'])} |")
    for title, key in [("罗列攻击（train，每题一组探针；奖励实际口径，含门控）", "attacks_train"),
                       ("罗列攻击（同上，但关闭门控，对照用）", "attacks_train_without_gate")]:
        if key not in result:
            continue
        lines += ["", f"## {title}", "",
                  "| 探针 | 题数 | v4 均值 | v5 均值 | v4 高于诚实读一半的比例 | v5 高于诚实读一半的比例 |",
                  "|---|---|---|---|---|---|"]
        for name, e in result[key].items():
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
    result = {"schema": SCHEMA, "oracle_version": ORACLE_VERSION, "reward_version": VERSION,
              "train_rows": len(train), "validation_rows": len(validation), "loo_limit": LOO_LIMIT,
              "train": calibrate(train, index), "validation": calibrate(validation, index, include_spray=False),
              "attacks_train": attack_table(train, index),
              "attacks_train_without_gate": attack_table(train, index, V5Config(consistency_gate=False))}
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "calibration.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "summary.md").write_text(summary_markdown(result), encoding="utf-8")
    print(json.dumps({"event": "calibration_done", "output": str(out), "train_rows": len(train)}))
    return result


if __name__ == "__main__":
    main()
