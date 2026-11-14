import pytest

from src.data.intergps_index import geometry_from_record
from src.rewards.claims import parse_claim
from src.rewards.geometry_oracle import OracleConfig, refute
from tests._fixtures import geometry_1670, release_row_1670, synthetic_record


def verdict(text, geometry, config=OracleConfig()):
    claim = parse_claim(text)
    assert claim.valid, claim.error
    return refute(claim, geometry, config)


def test_certified_positives_of_1670_are_never_refuted():
    g = geometry_1670()
    for token in release_row_1670()["certified_positive_tokens"]:
        assert verdict(token, g) is None, token


@pytest.mark.parametrize("text,reason", [
    ("PointLiesOnLine(A,(B,C))", "not_collinear"),
    ("PointLiesOnLine(E,(A,D))", "not_collinear"),
    ("PointLiesOnLine(A,(C,D))", None),  # collinear but outside the segment: unknown, not false
    ("PointLiesOnLine(C,(C,D))", "degenerate_incidence"),
    ("Parallel((A,B),(D,E))", None),  # the arrow-marked pair that is not in the certified list
    ("Parallel((A,B),(C,D))", "not_parallel"),
    ("Parallel((A,C),(C,D))", "collinear_pair"),
    ("Perpendicular((A,B),(D,E))", "not_perpendicular"),
    ("Length(A,Z)=3", "unknown_point"),
    ("Angle(Q,C,B)=30 deg", "unknown_point"),
    ("PointLiesOnCircle(A,Circle)", "no_circle_in_diagram"),
    ("Length(A,E)=7", None),  # values are never refuted from coordinates
])
def test_refutations_on_real_diagram_1670(text, reason):
    assert verdict(text, geometry_1670()) == reason


def circle_geometry():
    return geometry_from_record(synthetic_record(
        points={"O": (0, 0), "A": (10, 0), "B": (0, 10), "C": (5, 5), "D": (-10, 0)},
        lines=["OA", "OB"],
        circles=["O"],
        forms=["PointLiesOnCircle(A, Circle(O, radius_1_0))", "PointLiesOnCircle(B, Circle(O, radius_1_0))",
               "PointLiesOnCircle(D, Circle(O, radius_1_0))"],
    ))


def test_circle_rules():
    g = circle_geometry()
    assert verdict("PointLiesOnCircle(A,Circle(O))", g) is None
    assert verdict("PointLiesOnCircle(A,Circle)", g) is None  # single circle: alias resolves to O
    assert verdict("PointLiesOnCircle(C,Circle(O))", g) == "off_circle"
    assert verdict("PointLiesOnCircle(O,Circle(A))", g) == "unknown_circle"


def test_value_checks_are_off_by_default_and_work_when_enabled():
    g = circle_geometry()
    assert verdict("Angle(A,O,B)=30 deg", g) is None
    strict = OracleConfig(check_angle_value=True, check_congruent_length=True, check_congruent_angle=True)
    assert verdict("Angle(A,O,B)=30 deg", g, strict) == "angle_value_mismatch"
    assert verdict("Angle(A,O,B)=90 deg", g, strict) is None
    assert verdict("CongruentLength((O,A),(O,C))", g, strict) is None  # ratio 1.41 is within the 1.5 tolerance
    assert verdict("CongruentLength((O,C),(A,B))", g, strict) == "lengths_not_equal"  # ratio 2.0
    assert verdict("CongruentLength((O,A),(O,B))", g, strict) is None
    assert verdict("CongruentAngle((A,O,B),(A,O,C))", g, strict) == "angles_not_equal"


def test_missing_coordinates_mean_unknown():
    g = geometry_from_record(synthetic_record(points={"A": (0, 0)}, names=["A", "B", "C"], lines=["AB"]))
    assert verdict("PointLiesOnLine(A,(B,C))", g) is None
    assert verdict("Perpendicular((A,B),(B,C))", g) is None
