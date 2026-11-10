"""Statistics of S3 design section 5 (D46) on constructed data with known answers."""
import pytest

np = pytest.importorskip("numpy")

from src.evaluation.stats import align, distinguishable, holm, mcnemar_exact, paired_ratio, per_item  # noqa: E402


def test_identical_models_give_zero_and_p_one():
    scores = [1, 0, 1, 1, 0, 0, 1, 0] * 5
    clusters = ["c%d" % (i // 2) for i in range(len(scores))]
    result = paired_ratio(scores, [1] * 40, scores, [1] * 40, clusters, resamples=2000)
    assert result["estimate"] == 0 and result["ci95"] == [0.0, 0.0] and result["p_value"] == 1.0
    assert result["clusters"] == 20 and result["items"] == 40


def test_a_always_right_b_always_wrong():
    n = 60
    result = paired_ratio([1] * n, [1] * n, [0] * n, [1] * n, ["c%d" % i for i in range(n)], resamples=999)
    assert result["estimate"] == 1.0 and result["ci95"] == [1.0, 1.0]
    assert result["p_value"] == pytest.approx(1 / 1000)  # no permutation is as extreme except the identity draws
    assert distinguishable(result, holm([result["p_value"]])[0])


def test_clustering_widens_the_interval_when_items_in_a_cluster_agree():
    # 20 images with 10 questions each; within an image all questions are answered alike
    a = [1 if image < 12 else 0 for image in range(20) for _ in range(10)]
    b = [1 if image < 8 else 0 for image in range(20) for _ in range(10)]
    ones = [1] * 200
    by_image = paired_ratio(a, ones, b, ones, [str(i // 10) for i in range(200)], resamples=4000)
    by_item = paired_ratio(a, ones, b, ones, [str(i) for i in range(200)], resamples=4000)
    assert by_image["estimate"] == pytest.approx(0.2) == by_item["estimate"]
    width = lambda r: r["ci95"][1] - r["ci95"][0]  # noqa: E731
    assert width(by_image) > 2 * width(by_item)
    assert by_image["p_value"] > by_item["p_value"]


def test_ratio_metric_pools_counts_before_dividing():
    # E1 precision: TRUE / (TRUE + FALSE) summed over items, not a mean of per-item ratios
    true_a, claims_a = [9, 1], [10, 10]
    true_b, claims_b = [1, 1], [1, 10]
    result = paired_ratio(true_a, claims_a, true_b, claims_b, ["x", "y"], resamples=500)
    assert result["a"] == pytest.approx(10 / 20) and result["b"] == pytest.approx(2 / 11)
    assert result["estimate"] == pytest.approx(10 / 20 - 2 / 11)
    empty = paired_ratio([0, 0], [0, 0], [1, 1], [1, 1], ["x", "y"], resamples=200)
    assert np.isnan(empty["a"]) and empty["undefined_resamples"] == 200


def test_bootstrap_and_permutation_are_reproducible():
    rng = np.random.default_rng(1)
    a, b = rng.integers(0, 2, 120), rng.integers(0, 2, 120)
    clusters = [str(i % 37) for i in range(120)]
    first = paired_ratio(a, [1] * 120, b, [1] * 120, clusters, resamples=3000)
    assert first == paired_ratio(a, [1] * 120, b, [1] * 120, clusters, resamples=3000)
    assert 0 < first["p_value"] <= 1 and first["ci95"][0] <= first["estimate"] <= first["ci95"][1]


def test_holm_matches_hand_computation():
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([0.5, 0.001]) == pytest.approx([0.5, 0.002])
    assert holm([0.02, 0.04]) == pytest.approx([0.04, 0.04])
    assert holm([0.9, 0.8, 0.7]) == [1.0, 1.0, 1.0]  # 3 x 0.7 > 1 is capped, and later values never decrease


def test_mcnemar_exact_known_values():
    a = [1] * 10 + [0] * 5
    b = [0] * 10 + [0] * 5
    assert mcnemar_exact(a, b) == {"only_a": 10, "only_b": 0, "p_value": pytest.approx(2 / 2 ** 10)}
    assert mcnemar_exact([1, 0], [0, 1])["p_value"] == 1.0
    assert mcnemar_exact([1, 1], [1, 1]) == {"only_a": 0, "only_b": 0, "p_value": 1.0}
    # 7 vs 2 discordant pairs: 2 * P(X <= 2 | n=9) = 2 * (1 + 9 + 36) / 512
    assert mcnemar_exact([1] * 7 + [0] * 2, [0] * 7 + [1] * 2)["p_value"] == pytest.approx(2 * 46 / 512)


def test_distinguishable_needs_both_conditions():
    assert not distinguishable({"ci95": [-0.01, 0.2]}, 0.001)
    assert not distinguishable({"ci95": [0.01, 0.2]}, 0.06)
    assert distinguishable({"ci95": [-0.3, -0.02]}, 0.01)


def test_per_item_averages_seeds_and_align_checks_items():
    records = [{"item": "t:1", "cluster": "p1", "ok": 1}, {"item": "t:1", "cluster": "p1", "ok": 0},
               {"item": "t:2", "cluster": "p2", "ok": 1}]
    accuracy = per_item(records, lambda r: r["ok"])
    assert accuracy == {"t:1": (0.5, 1.0, "p1"), "t:2": (1.0, 1.0, "p2")}
    counts = per_item(records, lambda r: r["ok"], lambda r: 2)
    assert counts["t:1"] == (1.0, 4.0, "p1")
    num_a, den_a, num_b, den_b, clusters = align(accuracy, {"t:2": (0.0, 1.0, "p2"), "t:1": (1.0, 1.0, "p1")})
    assert (num_a, num_b, clusters) == ([0.5, 1.0], [1.0, 0.0], ["p1", "p2"])
    with pytest.raises(ValueError, match="same items"):
        align(accuracy, {"t:1": (1.0, 1.0, "p1")})
    with pytest.raises(ValueError, match="different clusters"):
        per_item(records + [{"item": "t:2", "cluster": "p9", "ok": 1}], lambda r: r["ok"])
