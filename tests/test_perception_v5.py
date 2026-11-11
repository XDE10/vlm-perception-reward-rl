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
    assert missing["status"] == "block_missing" and missing["reward"] == -1.0
    multiple = score_v5("<perception></perception><perception></perception><think>.</think><answer>4</answer>", GOLD, geometry_1670())
    assert multiple["status"] == "block_multiple" and multiple["reward"] == -1.0
    unclosed = score_v5("<perception>Length(A,B)=3<think>.</think><answer>4</answer>", GOLD, geometry_1670())
    assert unclosed["status"] == "block_missing" and unclosed["reward"] == -1.0
    mismatched = score_v5("<perception>Length(A,B)=3</perception></perception><think>.</think><answer>4</answer>", GOLD, geometry_1670())
    assert mismatched["status"] == "block_multiple" and mismatched["reward"] == -1.0
    empty = score_v5("<perception></perception><think>.</think><answer>4</answer>", GOLD, geometry_1670())
    assert empty["status"] == "empty" and empty["reward"] == 0.0
    assert score_v5(as_completion(GOLD), [], geometry_1670())["mask"] is False


def test_broken_block_cannot_be_used_as_safe_haven_against_negative_perception():
    from src.training.protocol_v3 import format_reward

    # Broken perception block gives format=0 and perception=-1.0
    broken_text = "<think>reasoning</think><answer>4</answer>"
    assert format_reward(broken_text) == 0.0
    assert score_v5(broken_text, GOLD, geometry_1670())["reward"] == -1.0
    # Under rl_v5 weights (format: 0.05, perception: 0.1), broken total contribution is -0.1
    broken_weighted = 0.05 * format_reward(broken_text) + 0.1 * score_v5(broken_text, GOLD, geometry_1670())["reward"]
    assert broken_weighted == -0.1

    # Even worst-case valid format completion (format=1, all perception claims false -> perception reward=-1.0)
    # gives 0.05 * 1.0 + 0.1 * (-1.0) = -0.05, which is strictly higher than a broken block (-0.1).
    six_refuted_claims = [f"PointLiesOnLine({p},({l1},{l2}))" for p, l1, l2 in
                          [("D", "A", "B"), ("E", "A", "B"), ("C", "D", "E"), ("A", "D", "E"), ("B", "D", "E"), ("D", "B", "C")]]
    worst_valid_text = f"<perception>{'; '.join(six_refuted_claims)}</perception><think>t</think><answer>4</answer>"
    assert format_reward(worst_valid_text) == 1.0
    assert score_v5(worst_valid_text, GOLD, geometry_1670())["reward"] == -1.0
    worst_valid_weighted = 0.05 * format_reward(worst_valid_text) + 0.1 * score_v5(worst_valid_text, GOLD, geometry_1670())["reward"]
    assert worst_valid_weighted == -0.05
    assert worst_valid_weighted > broken_weighted


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


def _right_angle_geometry(d_xy):
    """Diagram where Perpendicular((A,B),(B,C)) is certified; C sits at d_xy (off-scale when not on the y axis)."""
    from src.data.intergps_index import geometry_from_record
    from tests._fixtures import synthetic_record

    points = {"A": (0, 0), "B": (10, 0), "C": d_xy, "D": (5, 0), "E": (5, 8)}
    return geometry_from_record(synthetic_record(points=points, lines=["AB", "BC", "AD", "DB", "DE"]))


RIGHT_GOLD = ["Perpendicular((A,B),(B,C))", "PointLiesOnLine(D,(A,B))"]


def test_consistency_gate_drops_coordinate_refutations_on_self_contradicting_diagrams():
    from src.rewards.perception_v5 import consistency_gate

    claims = RIGHT_GOLD + ["PointLiesOnLine(E,(A,B))", "PointLiesOnLine(Z,(A,B))"]
    drawn_to_scale = _right_angle_geometry((10, 8))
    assert consistency_gate(RIGHT_GOLD, drawn_to_scale) == {}
    ok = score_v5(as_completion(claims), RIGHT_GOLD, drawn_to_scale)
    assert ok["gated"] == [] and ok["false_reasons"] == {"not_collinear": 1, "unknown_point": 1}
    # the certified right angle is drawn at ~50 degrees: these coordinates refute a true fact of this diagram
    off_scale = _right_angle_geometry((15, 6))
    gate = consistency_gate(RIGHT_GOLD, off_scale)
    assert gate == {"coordinates": {"certified": "Perpendicular((A,B),(B,C))", "reason": "not_perpendicular"}}
    gated = score_v5(as_completion(claims), RIGHT_GOLD, off_scale)
    # coordinate refutations are dropped (E stays UNKNOWN); the point inventory still refutes the invented point Z
    assert gated["gated"] == ["coordinates"] and gated["false_reasons"] == {"unknown_point": 1}
    assert gated["tp"] == 2 and gated["unknown"] == 1
    ungated = score_v5(as_completion(claims), RIGHT_GOLD, off_scale, config=V5Config(consistency_gate=False))
    assert ungated["false_reasons"] == {"not_collinear": 1, "unknown_point": 1} and ungated["gated"] == []


def test_gate_never_changes_scores_on_the_real_row_1670():
    from src.rewards.perception_v5 import consistency_gate

    assert consistency_gate(GOLD, geometry_1670()) == {}
    suite = attack_suite(geometry_1670(), GOLD)
    for claims in suite.values():
        if claims:
            assert v5(claims)["reward"] == v5(claims, config=V5Config(consistency_gate=False))["reward"]
