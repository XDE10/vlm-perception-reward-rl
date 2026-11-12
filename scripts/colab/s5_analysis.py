"""Pre-registered S5 comparisons and descriptive tables from completed predictions."""
import math

from src.evaluation import stats
from src.evaluation.harness import summarize


MAIN = (
    ("E1", "val82", "precision", "rl_v5", "rl_ans"),
    ("E1", "val82", "precision", "rl_v5", "rl_v4"),
    ("E1", "val82", "recall", "rl_v5", "rl_ans"),
    ("E1", "val82", "recall", "rl_v5", "rl_v4"),
    ("E2", "cf_k2", "accuracy", "rl_v5", "rl_ans"),
    ("E2", "cf_k2", "accuracy", "rl_v5", "rl_v5_placebo"),
    ("E2", "cf_k2", "accuracy", "rl_v5", "rl_blind"),
    ("E3", "test_vn", "accuracy", "rl_v5", "rl_ans"),
    ("E3", "test_vn", "accuracy", "rl_ans", "rl_blind"),
)


def accuracy(row):
    return row["answer"]["correct"]


def ratio(rows_a, rows_b, metric):
    if metric == "accuracy":
        return stats.paired_ratio(*stats.align(stats.per_item(rows_a, accuracy), stats.per_item(rows_b, accuracy)))
    denominator = (lambda r: r["v5"]["tp"] + r["v5"]["false"]) if metric == "precision" else (lambda r: r["gold_count"])
    a = stats.per_item(rows_a, lambda r: r["v5"]["tp"], denominator)
    b = stats.per_item(rows_b, lambda r: r["v5"]["tp"], denominator)
    return stats.paired_ratio(*stats.align(a, b))


def _finite(value):
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, list):
        return [_finite(x) for x in value]
    if isinstance(value, dict):
        return {k: _finite(v) for k, v in value.items()}
    return value


def _tables(records):
    tables = {name: summarize(rows) for name, rows in records.items()}
    if "test_original" in records:
        matched = [r["intergps"] for r in records["test_original"] if r["intergps"] is not None]
        claims = sum(r["valid_claims"] for r in matched)
        false = sum(r["refuted"] for r in matched)
        tables["test_original"]["intergps"] = {"outputs": len(matched), "claims": claims, "refuted": false,
                                               "false_rate": false / claims if claims else None}
    if all(name in records for name in ("cf_original", "cf_k1", "cf_k2")):
        rates = {name: tables[name]["accuracy"] for name in ("cf_original", "cf_k1", "cf_k2")}
        tables["cf_k1_minus_original"] = rates["cf_k1"] - rates["cf_original"]
        tables["cf_k2_minus_k1"] = rates["cf_k2"] - rates["cf_k1"]
    return tables


def analyze(models):
    """models maps arm -> seed -> condition -> list of records. Empty arms yield unavailable comparisons."""
    groups = {
        arm: {key: [row for records in seeds.values() for row in records[key]]
              for key in next(iter(seeds.values()))}
        for arm, seeds in models.items() if seeds
    }
    main, sensitivity, exploratory = [], [], []
    for endpoint, dataset, metric, a, b in MAIN:
        entry = {"endpoint": endpoint, "dataset": dataset, "metric": metric, "a": a, "b": b,
                 "seeds_a": sorted(models.get(a, {})), "seeds_b": sorted(models.get(b, {}))}
        if a not in groups or b not in groups:
            main.append(dict(entry, result=None, unavailable="no completed seed for one or both arms"))
            continue
        result = ratio(groups[a][dataset], groups[b][dataset], metric)
        if not math.isfinite(result["estimate"]):
            main.append(dict(entry, result=result, unavailable="zero denominator"))
        else:
            main.append(dict(entry, result=result))
        filtered = {"E1": "val82_without_errata", "E2": "cf_k2_exact"}.get(endpoint)
        if filtered:
            sensitivity.append(dict(entry, dataset=filtered, result=ratio(groups[a][filtered], groups[b][filtered], metric)))
        if metric == "accuracy":
            for seed in sorted(set(models[a]) & set(models[b])):
                rows_a = {r["item"]: r for r in models[a][seed][dataset]}
                rows_b = {r["item"]: r for r in models[b][seed][dataset]}
                items = sorted(rows_a)
                if set(items) != set(rows_b):
                    raise ValueError("seed-level McNemar requires matching item IDs")
                main[-1].setdefault("mcnemar", {})[seed] = stats.mcnemar_exact(
                    [accuracy(rows_a[i]) for i in items], [accuracy(rows_b[i]) for i in items])
    # Retain the nine-hypothesis family even when a comparison is unavailable.
    p_values = [e["result"]["p_value"] if "unavailable" not in e else 1.0 for e in main]
    for entry, adjusted in zip(main, stats.holm(p_values)):
        entry["holm_p"] = adjusted if "unavailable" not in entry else None
        entry["distinguishable"] = ("unavailable" not in entry and stats.distinguishable(entry["result"], adjusted))
    if "rl_v5_groupnorm" in groups and "rl_v5" in groups:
        for dataset, metric in [("val82", "precision"), ("val82", "recall"), ("cf_k2", "accuracy"),
                                ("test_vn", "accuracy")]:
            exploratory.append({"dataset": dataset, "metric": metric, "a": "rl_v5_groupnorm", "b": "rl_v5",
                                "result": ratio(groups["rl_v5_groupnorm"][dataset], groups["rl_v5"][dataset], metric)})
    return _finite({"main": main, "sensitivity": sensitivity, "exploratory": exploratory,
                    "pooled": {arm: _tables(records) for arm, records in groups.items()},
                    "by_seed": {arm: {seed: _tables(records) for seed, records in seeds.items()}
                                for arm, seeds in models.items()}})


def markdown(report):
    def pp(value):
        return "—" if value is None else f"{100 * value:+.2f}"

    lines = ["# S5 正式终评", "", "差值为 A − B，单位为百分点。区间按原图聚类。", "",
             "| 终点 | 指标 | A | B | 差值 | 95% 区间 | Holm p | 判定 |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in report["main"]:
        result = row["result"] or {}
        ci = " 至 ".join(pp(x) for x in result.get("ci95", [None, None]))
        adjusted = f'{row["holm_p"]:.4g}' if row["holm_p"] is not None else "—"
        verdict = "无法计算" if "unavailable" in row else ("能区分" if row["distinguishable"] else "未能区分")
        lines.append(f'| {row["endpoint"]} | {row["metric"]} | {row["a"]} | {row["b"]} | '
                     f'{pp(result.get("estimate"))} | {ci} | {adjusted} | {verdict} |')
    lines += ["", "逐种子、次要指标和敏感性分析见 [summary.json](summary.json)。"]
    return "\n".join(lines) + "\n"
