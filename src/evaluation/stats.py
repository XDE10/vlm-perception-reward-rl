"""Pre-registered statistics for paired model comparisons (docs/plan/S3设计_20261109.md section 5, decision D46).

Two models are compared on the same items. Each item contributes a numerator and a denominator per model and belongs
to a cluster (the pixel hash of its source image):

* accuracy: numerator = the item's score in [0, 1] (already averaged over seeds), denominator = 1;
* pooled E1 precision: numerator = TRUE claims, denominator = TRUE + FALSE claims (summed over seeds);
* pooled E1 recall: numerator = TRUE claims, denominator = certified facts.

The statistic is sum(num_a) / sum(den_a) - sum(num_b) / sum(den_b).

* ``paired_ratio``: point estimate; 95% percentile interval from a cluster bootstrap (clusters resampled with
  replacement, 10,000 times, seed 20261109); two-sided p from a cluster permutation test (inside each cluster the two
  models' values are swapped with probability 1/2, 10,000 times), p = (1 + extreme) / (1 + 10,000).
* ``holm``: step-down adjusted p-values over the primary comparisons.
* ``distinguishable``: Holm-adjusted p < 0.05 and the interval excludes 0 (both are required).
* ``mcnemar_exact``: supplementary exact test for one seed with 0/1 outcomes.
"""
import math

import numpy as np

SEED = 20261109
RESAMPLES = 10000
ALPHA = 0.05
_CHUNK = 1000


def _cluster_table(values, clusters):
    """Sum the item rows of ``values`` (n x 4) per cluster; clusters are sorted so the result is deterministic."""
    keys = sorted(set(clusters))
    position = {key: i for i, key in enumerate(keys)}
    table = np.zeros((len(keys), values.shape[1]))
    np.add.at(table, np.array([position[c] for c in clusters], dtype=np.int64), values)
    return keys, table


def _ratio(num, den):
    num, den = np.asarray(num, dtype=np.float64), np.asarray(den, dtype=np.float64)
    out = np.full(np.shape(num), np.nan)
    np.divide(num, den, out=out, where=den > 0)
    return out


def paired_ratio(num_a, den_a, num_b, den_b, clusters, resamples=RESAMPLES, seed=SEED):
    """Paired comparison of model a against model b; see the module docstring."""
    values = np.column_stack([np.asarray(x, dtype=np.float64) for x in (num_a, den_a, num_b, den_b)])
    clusters = list(clusters)
    if values.shape[0] != len(clusters) or not len(clusters):
        raise ValueError("every item needs one cluster, and there must be at least one item")
    if (values[:, [1, 3]] < 0).any():
        raise ValueError("denominators must be non-negative")
    keys, table = _cluster_table(values, clusters)
    total = table.sum(axis=0)
    a, b = float(_ratio(total[0], total[1])), float(_ratio(total[2], total[3]))
    estimate = a - b
    k = len(keys)
    rng = np.random.default_rng(seed)
    boot = []
    for start in range(0, resamples, _CHUNK):
        size = min(_CHUNK, resamples - start)
        sums = table[rng.integers(0, k, size=(size, k))].sum(axis=1)
        boot.append(_ratio(sums[:, 0], sums[:, 1]) - _ratio(sums[:, 2], sums[:, 3]))
    boot = np.concatenate(boot)
    defined = boot[~np.isnan(boot)]
    ci = [float(x) for x in np.percentile(defined, [2.5, 97.5])] if len(defined) else [float("nan")] * 2
    rng = np.random.default_rng(seed)
    extreme = 0
    for start in range(0, resamples, _CHUNK):
        size = min(_CHUNK, resamples - start)
        flip = (rng.random((size, k)) < 0.5).astype(np.float64)
        keep = 1.0 - flip
        perm_a = keep @ table[:, :2] + flip @ table[:, 2:]
        perm_b = keep @ table[:, 2:] + flip @ table[:, :2]
        stat = _ratio(perm_a[:, 0], perm_a[:, 1]) - _ratio(perm_b[:, 0], perm_b[:, 1])
        extreme += int(np.sum(np.abs(np.nan_to_num(stat, nan=0.0)) >= abs(estimate) - 1e-12))
    return {"estimate": estimate, "a": a, "b": b, "ci95": ci, "p_value": (1 + extreme) / (1 + resamples),
            "items": int(values.shape[0]), "clusters": k, "resamples": resamples, "seed": seed,
            "undefined_resamples": int(np.isnan(boot).sum())}


def holm(p_values):
    """Holm step-down adjusted p-values, in the input order."""
    p = [float(x) for x in p_values]
    m = len(p)
    adjusted, running = [0.0] * m, 0.0
    for rank, i in enumerate(sorted(range(m), key=lambda j: p[j])):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adjusted[i] = running
    return adjusted


def distinguishable(result, p_adjusted, alpha=ALPHA):
    low, high = result["ci95"]
    return bool(p_adjusted < alpha and (low > 0 or high < 0))


def mcnemar_exact(correct_a, correct_b):
    """Two-sided exact McNemar test on paired 0/1 outcomes; returns the discordant counts and p."""
    pairs = list(zip(correct_a, correct_b))
    only_a = sum(1 for x, y in pairs if x and not y)
    only_b = sum(1 for x, y in pairs if y and not x)
    n = only_a + only_b
    tail = sum(math.comb(n, i) for i in range(min(only_a, only_b) + 1)) / 2.0 ** n if n else 1.0
    return {"only_a": only_a, "only_b": only_b, "p_value": min(1.0, 2.0 * tail)}


def align(rows_a, rows_b):
    """Two {item: (num, den, cluster)} maps on the same items -> arrays for paired_ratio, in sorted item order."""
    if set(rows_a) != set(rows_b):
        missing = sorted(set(rows_a) ^ set(rows_b))[:5]
        raise ValueError("the two models were not evaluated on the same items (e.g. %s)" % missing)
    items = sorted(rows_a)
    for item in items:
        if rows_a[item][2] != rows_b[item][2]:
            raise ValueError("item %s has different clusters in the two models" % item)
    return ([rows_a[i][0] for i in items], [rows_a[i][1] for i in items], [rows_b[i][0] for i in items],
            [rows_b[i][1] for i in items], [rows_a[i][2] for i in items])


def per_item(records, numerator, denominator=None):
    """Average (accuracy) or pool (counts) a model's records per item over seeds.

    ``records``: dicts with ``item``, ``cluster`` and the fields named by ``numerator``/``denominator`` (callables
    taking a record). Accuracy: denominator None -> (mean score over seeds, 1). Counts: (sum num, sum den).
    """
    grouped = {}
    for record in records:
        grouped.setdefault(record["item"], []).append(record)
    out = {}
    for item, group in grouped.items():
        clusters = {r["cluster"] for r in group}
        if len(clusters) != 1:
            raise ValueError("item %s has records with different clusters" % item)
        if denominator is None:
            out[item] = (sum(float(numerator(r)) for r in group) / len(group), 1.0, clusters.pop())
        else:
            out[item] = (sum(float(numerator(r)) for r in group), sum(float(denominator(r)) for r in group),
                         clusters.pop())
    return out


__all__ = ["ALPHA", "RESAMPLES", "SEED", "align", "distinguishable", "holm", "mcnemar_exact", "paired_ratio", "per_item"]
