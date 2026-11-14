import pytest

from src.data.perception_v4 import token_key
from src.rewards.claims import entity_points, extract_block, parse_block, parse_claim
from tests._fixtures import release_row_1670


def test_certified_tokens_parse_with_frozen_v4_keys():
    for token in release_row_1670()["certified_positive_tokens"]:
        claim = parse_claim(token)
        assert claim.valid, claim.error
        assert claim.key == token_key(token)


@pytest.mark.parametrize("text", [
    "Angle(A,B)=60 deg",  # wrong arity
    "Angle(A,A,C)=60 deg",  # degenerate
    "Angle(A,B,C)=60",  # missing unit
    "Angle(A,B,C)=60°",  # unit outside schema
    "Length(A,B)=-3",
    "Length(A,B)=0",
    "Length(A,B)",  # value required
    "Parallel((A,B),(B,A))",
    "Perpendicular(AB,CD)",  # legacy segment syntax is not this schema
    "Tangent(Circle(O),(A,B))",
    "__import__(A)",
    "Foo(A,B)",
])
def test_schema_rejects_malformed_facts(text):
    claim = parse_claim(text)
    assert not claim.valid and claim.key is None


def test_reflex_angles_are_allowed_up_to_360():
    assert parse_claim("Angle(A,B,C)=270 deg").valid
    assert not parse_claim("Angle(A,B,C)=400 deg").valid


def test_block_extraction_statuses():
    assert extract_block("<perception>Length(A,B)=3</perception><think>.</think>") == ("Length(A,B)=3", "ok")
    assert extract_block("no block")[1] == "missing"
    assert extract_block("<perception>a</perception><perception>b</perception>")[1] == "multiple"
    assert extract_block("<perception>a</perception> text <perception>")[1] == "multiple"


def test_parse_block_is_per_chunk_and_deduplicated():
    claims, info = parse_block("Length(A,B)=3; Length(B,A)=3; Angle(A,B,C)=60°; Angle(A,B,C)=60° ; ;Parallel((A,B),(C,D))")
    assert info["chunks"] == 5 and info["unique"] == 3 and info["invalid"] == 1
    assert [c.valid for c in claims] == [True, False, True]


def test_over_cap_is_reported():
    block = "; ".join(f"Length(A,B)={i}" for i in range(1, 26))
    _, info = parse_block(block, max_claims=24)
    assert info["over_cap"] and info["chunks"] == 25


def test_entity_points_excludes_circle_aliases():
    assert sorted(entity_points(parse_claim("PointLiesOnLine(C,(A,D))").args)) == ["A", "C", "D"]
    assert entity_points(parse_claim("PointLiesOnCircle(A,Circle)").args) == ["A"]
    assert sorted(entity_points(parse_claim("PointLiesOnCircle(A,Circle(O))").args)) == ["A", "O"]
    assert sorted(entity_points(parse_claim("Angle(A,B,C)=60 deg").args)) == ["A", "B", "C"]
