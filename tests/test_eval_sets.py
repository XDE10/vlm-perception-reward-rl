"""Pre-registered evaluation-set rules (docs/plan/S3设计_20261109.md sections 1-3) on synthetic annotations."""
import random
from decimal import ROUND_HALF_UP, Decimal

import pytest

from src.evaluation.eval_sets import (build_eval_sets, cf_candidate, join_rows, on_grid, rounded_answer_set,
                                      rounding_places, scale_number, split_equals, vision_needed)

ALWAYS = lambda answer: True  # noqa: E731  (rule 5's parse check is tested separately with math_verify)
TRIANGLE = ["Equals(LengthOf(Line(A, B)), 12)", "Equals(LengthOf(Line(B, C)), x)",
            "Equals(MeasureOf(Angle(A, B, C)), 30)", "PointLiesOnLine(D, Line(A, C))"]


def test_split_equals_handles_nesting_and_expressions():
    assert split_equals("Equals(LengthOf(Line(A, B)), 12)") == ("LengthOf", "12")
    assert split_equals("Equals(MeasureOf(Angle(A, B, C)), 2x+3)") == ("MeasureOf", "2x+3")
    assert split_equals("Perpendicular(Line(A, B), Line(B, C))") is None


def test_vision_needed_looks_only_at_question_digits_and_diagram_values():
    assert vision_needed("<image>Find x.", TRIANGLE)
    assert not vision_needed("<image>Find x if AB = 12.", TRIANGLE)  # the question carries a number
    assert not vision_needed("Find m \\angle 2.", TRIANGLE)  # an angle number counts as a digit: excluded on purpose
    assert not vision_needed("Find x.", ["Equals(LengthOf(Line(A, B)), x)", "Parallel(Line(A, B), Line(C, D))"])


def test_cf_candidate_rules():
    ok = cf_candidate("<image>Find x.", "6", TRIANGLE, ["Find(x)"], ALWAYS)
    assert ok["ok"] and (ok["degree"], ok["places"], ok["lengths"], ok["angles"]) == (1, None, ["12"], ["30"])
    area = cf_candidate("Find the area of the triangle.", "24", TRIANGLE, ["Find(AreaOf(Triangle(A, B, C)))"], ALWAYS)
    assert area["ok"] and area["degree"] == 2
    perimeter = cf_candidate("Find the perimeter.", "40", TRIANGLE, ["Find(PerimeterOf(Triangle(A, B, C)))"], ALWAYS)
    assert perimeter["ok"] and perimeter["degree"] == 1
    rounded = cf_candidate("Find x. Round to the nearest tenth.", "6.9", TRIANGLE, ["Find(x)"], ALWAYS)
    assert rounded["ok"] and rounded["places"] == 1
    reasons = {
        "not vision-needed": cf_candidate("Find x if AB = 3.", "6", TRIANGLE, ["Find(x)"], ALWAYS),
        "length label is an expression": cf_candidate("Find x.", "6", TRIANGLE + ["Equals(LengthOf(Line(C, D)), x+3)"],
                                                      ["Find(x)"], ALWAYS),
        "angle label is not a plain number": cf_candidate("Find x.", "6", TRIANGLE[:2] + ["Equals(MeasureOf(Angle(A, B, C)), 2y)"],
                                                          ["Find(x)"], ALWAYS),
        "numeric value that is not a length or an angle": cf_candidate(
            "Find x.", "6", TRIANGLE + ["Equals(AreaOf(Triangle(A, B, C)), 24)"], ["Find(x)"], ALWAYS),
        "no numeric length label": cf_candidate("Find x.", "6", TRIANGLE[1:], ["Find(x)"], ALWAYS),
        "goal is not a length or an area": cf_candidate("Find y.", "6", TRIANGLE, ["Find(MeasureOf(Angle(A, C, B)))"],
                                                        ALWAYS),
        "rounding phrase not recognised": cf_candidate("Find x. Round to the nearest degree.", "6", TRIANGLE,
                                                       ["Find(x)"], ALWAYS),
        "rounding requested but the reference is not a plain decimal": cf_candidate(
            "Find x. Round to the nearest tenth.", "2\\sqrt{3}", TRIANGLE, ["Find(x)"], ALWAYS),
        "reference has more decimals than the rounding request": cf_candidate(
            "Find x. Round to the nearest tenth.", "6.93", TRIANGLE, ["Find(x)"], ALWAYS),
        "reference does not parse": cf_candidate("Find x.", "6", TRIANGLE, ["Find(x)"], lambda a: False),
    }
    for reason, verdict in reasons.items():
        assert not verdict["ok"] and verdict["reason"] == reason, (reason, verdict)
    # a letter goal must be the letter of a length label, not of an angle
    assert cf_candidate("Find y.", "6", TRIANGLE, ["Find(y)"], ALWAYS)["reason"] == "goal is not a length or an area"


def test_rounding_places():
    assert rounding_places("Find x. Round to the nearest hundredth.") == 2
    assert rounding_places("Find x.") is None
    assert rounding_places("Round your answer to the nearest whole number.") == "unrecognised"


def test_rounded_answer_set_contains_every_correct_rounding():
    assert rounded_answer_set("56.6", 1, 2) == ["113.1", "113.2", "113.3"]
    assert rounded_answer_set("56.6", 1, 1) == ["56.6"]  # S_1 = {g}: the usual strict grading
    assert rounded_answer_set("56.6", 1, 4) == ["226.2", "226.3", "226.4", "226.5", "226.6"]
    assert rounded_answer_set("420", 1, 2) == ["839.9", "840.0", "840.1"]
    with pytest.raises(ValueError):
        rounded_answer_set("56.57", 1, 2)
    rng = random.Random(0)
    for gold, places, factor in [("56.6", 1, 2), ("3.46", 2, 2), ("12.5", 1, 4), ("0.7", 1, 2)]:
        unit = Decimal(1).scaleb(-places)
        allowed = set(rounded_answer_set(gold, places, factor))
        g = Decimal(gold)
        hits = set()
        for _ in range(2000):
            v = g - unit / 2 + unit * Decimal(rng.random())  # a true value consistent with the rounded reference
            hits.add(str((Decimal(factor) * v).quantize(unit, rounding=ROUND_HALF_UP)))
        assert hits <= allowed, (gold, hits - allowed)
        assert len(allowed) <= factor + 1
    assert on_grid("420", 1) and not on_grid("0.05", 1)


def test_scaled_labels_and_references():
    assert [scale_number(x, 2) for x in ["3.5", "12", "0.75", "10"]] == ["7", "24", "1.5", "20"]
    pytest.importorskip("math_verify")
    from src.evaluation.eval_sets import gold_parses, scaled_exact_gold

    assert scaled_exact_gold("2 \\sqrt { 221 }", 2) == "4 \\sqrt{221}"
    assert scaled_exact_gold("\\frac { 40 } { 3 }", 4) == "\\frac{160}{3}"
    assert scaled_exact_gold("7.5", 2) == "15"
    assert gold_parses("2 \\sqrt { 221 }") and not gold_parses("x = 4") and not gold_parses(" ")


def _record(oid, split, pixel, question, diagram, text):
    return {"original_id": oid, "split": split, "image_pixel_sha256": pixel,
            "original_data": {"problem_text": question, "compact_text": question, "annotat_text": question},
            "diagram_annotation": {"diagram_logic_forms": diagram}, "dissolved_annotation": {"text_logic_forms": text}}


def test_join_rows_statuses():
    records = [_record("1", "test", "p1", "Find x.", TRIANGLE, ["Find(x)"]),
               _record("2", "test", "p2", "Find x.", TRIANGLE, ["Find(x)"]),
               _record("3", "test", "p2", "Find x", TRIANGLE, ["Find(x)"])]
    rows = [{"problem": "<image>Find x.", "answer": "6", "pixel": "p1"},
            {"problem": "<image>Find x.", "answer": "6", "pixel": "p2"},
            {"problem": "<image>Find y.", "answer": "6", "pixel": "p1"},
            {"problem": "<image>Find x.", "answer": "6", "pixel": "p9"}]
    statuses = [x["status"] for x in join_rows("test", rows, records)]
    assert statuses == ["matched", "ambiguous", "question_conflict", "missing_image"]


def test_build_eval_sets_is_deterministic_and_swaps_distinct_images():
    records, wrapper = [], {"validation": [], "test": []}
    for split, n, base in [("validation", 4, 100), ("test", 8, 200)]:
        for i in range(n):
            question = "Find x." if i % 2 == 0 else "Find x if AB = %d." % i
            records.append(_record(str(base + i), split, "%s-%d" % (split, i), question, TRIANGLE, ["Find(x)"]))
            wrapper[split].append({"problem": "<image>" + question, "answer": "6", "pixel": "%s-%d" % (split, i)})
    wrapper["test"].append({"problem": "<image>Find x.", "answer": "6", "pixel": "test-0"})  # same image, no record
    first = build_eval_sets(wrapper, records, parse_check=ALWAYS)
    assert first == build_eval_sets(wrapper, records, parse_check=ALWAYS)
    assert first["counts"]["test601"] == 9 and first["test_vn"] == ["test:0", "test:2", "test:4", "test:6", "test:8"]
    assert first["counts"]["cf_candidates_by_split"] == {"validation": 2, "test": 5}
    pixel = {x["id"]: x["pixel"] for x in first["test601"]}
    assert all(pixel[a] != pixel[b] for a, b in first["swap"].items()) and len(first["swap"]) == 9
    assert first["excluded"]["test_vn"] == {"not vision-needed": 4}
