import importlib.util

import pytest

from src.rewards.answer import AnswerVerifier, normalize_answer

HAS_MATH_VERIFY = importlib.util.find_spec("math_verify") is not None


@pytest.mark.parametrize("raw,expected", [
    ("4", "4"),
    ("x = 4", "4"),
    ("$x=4$.", "4"),
    ("12 cm", "12"),
    ("78 cm^2", "78"),
    ("78 square units", "78"),
    ("30^\\circ", "30"),
    ("30°", "30"),
    ("30 degrees", "30"),
    ("\\approx 12.3", "12.3"),
    ("2\\sqrt{3}", "2\\sqrt{3}"),
    ("\\frac{20}{3}", "\\frac{20}{3}"),
    ("x + 3", "x + 3"),  # not an assignment: left untouched
])
def test_normalization_only_removes_presentation(raw, expected):
    assert normalize_answer(raw) == expected


@pytest.mark.skipif(not HAS_MATH_VERIFY, reason="math_verify not installed")
def test_verifier_correct_wrong_relational_and_missing():
    verifier = AnswerVerifier(workers=2, timeout=60)
    try:
        out = verifier.verify_many(["x = 4", "5", "x > 3", "", "8.0", "2\\sqrt{3}"], ["4", "4", "4", "4", "8", "2\\sqrt{3}"])
    finally:
        verifier.close()
    assert [r["correct"] for r in out] == [True, False, False, False, True, True]
    assert out[2]["status"].startswith("relational") and out[3]["status"] == "no_answer"
    assert out[0]["normalized_answer"] == "4"


@pytest.mark.skipif(not HAS_MATH_VERIFY, reason="math_verify not installed")
def test_timeout_is_isolated_and_pool_restarts():
    verifier = AnswerVerifier(workers=1, timeout=1e-6)
    try:
        out = verifier.verify_many(["4"], ["4"])
        assert out[0]["status"] == "verifier_timeout" and not out[0]["correct"]
        assert verifier.restarts == 1
        verifier.timeout = 60
        assert verifier.verify_many(["4"], ["4"])[0]["correct"]
    finally:
        verifier.close()


def test_length_mismatch_fails_closed():
    with pytest.raises(ValueError):
        AnswerVerifier().verify_many(["1"], [])
