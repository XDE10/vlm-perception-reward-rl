import pytest

from src.data.perception_v4 import scoped_score
from src.rewards.attacks import as_completion, attack_suite
from src.rewards.perception_v5 import V5Config, score_v5
from tests._fixtures import geometry_1670, release_row_1670

GOLD = release_row_1670()["certified_positive_tokens"]


def v5(claims, geometry=None, config=V5Config()):
    return score_v5(as_completion(claims), GOLD, geometry_1670() if geometry is None else geometry, config=config)


def v4(claims):
    return scoped_score(as_completion(claims), GOLD, [])


def test_honest_reading_scores_proportionally():
    assert v5(GOLD)["reward"] == pytest.approx(1.0)
    half = v5(GOLD[:3])
    assert half["reward"] == pytest.approx(0.5) and half["unknown"] == 0 and half["false"] == 0


def test_true_but_uncertified_fact_costs_only_beta():
    # AB is parallel to DE in the figure (arrow marks) but the fact is not certified.
    result = v5(GOLD + ["Parallel((A,B),(D,E))"])
    assert result["unknown"] == 1 and result["false"] == 0
    assert result["reward"] == pytest.approx(1.0 - 0.1 / 6)


def test_invalid_chunk_costs_one_claim_instead_of_zeroing_the_block():
    result = v5(GOLD + ["Angle(A,C,B)=60°"])
    assert v4(GOLD + ["Angle(A,C,B)=60°"])["reward"] == 0.0  # frozen v4 behaviour
    assert result["false"] == 1 and result["false_reasons"] == {"invalid_chunk": 1}
    assert result["reward"] == pytest.approx(5 / 6)


def test_certified_constant_conflict_is_false():
    result = v5(["Length(A,C)=2"])
    assert result["false_reasons"] == {"certified_constant_conflict": 1}
    assert result["reward"] == pytest.approx(-1 / 6)


def test_over_cap_and_missing_block():
    assert v5([f"Length(A,B)={i}" for i in range(1, 26)])["reward"] == -1.0
    missing = score_v5("<think>.</think><answer>4</answer>", GOLD, geometry_1670())
    assert missing["status"] == "block_missing" and missing["reward"] == 0.0
    assert score_v5(as_completion(GOLD), [], geometry_1670())["mask"] is False


def test_spray_attacks_beat_honest_reading_under_v4_but_not_under_v5():
    suite = attack_suite(geometry_1670(), GOLD)
    honest_v4, honest_v5 = v4(suite["honest_half"])["reward"], v5(suite["honest_half"])["reward"]
    for name in ["incidence_spray", "pair_spray", "combined_spray"]:
        attack = suite[name]
        assert attack, name
        assert v5(attack)["reward"] < honest_v5, name
        assert v5(attack)["reward"] < 0, name
    # v4 rewards the incidence spray as much as honestly reading half of the facts
    assert v4(suite["incidence_spray"])["reward"] >= honest_v4 - 0.2
    # padding honest facts with sprayed claims keeps v4 at 1.0 but costs under v5
    padded = suite["combined_spray_with_gold"]
    assert v4(padded)["reward"] == pytest.approx(1.0)
    assert v5(padded)["reward"] < 0.5


def test_without_geometry_only_certified_rules_apply():
    result = score_v5(as_completion(["PointLiesOnLine(A,(B,C))"]), GOLD, None)
    assert result["unknown"] == 1 and result["false"] == 0


def test_config_round_trip():
    config = V5Config.from_dict({"alpha": 2.0, "oracle": {"parallel_deg": 10.0}})
    assert config.alpha == 2.0 and config.oracle.parallel_deg == 10.0
    assert V5Config.from_dict(config.to_dict()) == config
