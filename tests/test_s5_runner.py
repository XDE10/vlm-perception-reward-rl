import json

import pytest

from scripts.colab import final_eval, s5_analysis
from scripts.colab.common import read_json
from scripts.colab.s5_inputs import MathVistaVerifier, ROOT


def test_inventory_does_not_admit_old_seed1(monkeypatch):
    registry = read_json(ROOT / final_eval.S4_REGISTRY)

    def run_status(store, rel, key):
        state = "foreign" if rel.endswith("/rl_v5/seed1") else "new"
        return {"state": state, "checkpoints": []}

    monkeypatch.setattr(final_eval.s4_state, "run_status", run_status)
    runs = final_eval.inventory(object(), registry)
    assert len(runs) == 14
    assert sum(not run["optional"] for run in runs) == 12
    assert runs[0]["state"] == "foreign"
    assert runs[0]["run_name"] == "rl_v5/seed1"


def test_s5_keeps_nine_comparisons_and_pools_e1_over_seeds():
    def row(correct, tp, false, gold):
        return {"item": "validation:1", "cluster": "one-image", "answer": {"correct": correct, "extracted": "1"},
                "format": 1, "protocol_ok": True, "budget_exhausted": False, "gold_count": gold,
                "v5": {"tp": tp, "false": false, "unknown": 0, "status": "ok"}}

    def records(record):
        return {key: [record] for key in ("val82", "val82_without_errata", "cf_k2", "cf_k2_exact", "test_vn")}

    models = {
        "rl_v5": {1: records(row(True, 1, 0, 3)), 2: records(row(False, 0, 3, 3))},
        "rl_ans": {1: records(row(False, 0, 1, 3))},
    }
    result = s5_analysis.analyze(models)
    assert len(result["main"]) == 9
    assert result["main"][0]["result"]["a"] == pytest.approx(0.25)
    assert result["main"][2]["result"]["a"] == pytest.approx(1 / 6)
    assert result["main"][4]["result"]["a"] == pytest.approx(0.5)
    assert result["main"][4]["mcnemar"][1]["only_a"] == 1
    assert result["main"][1]["holm_p"] is None


def test_mathvista_choices_and_lists_are_deterministic():
    class Numeric:
        def verify_many(self, predictions, targets):
            return [{"correct": p == t} for p, t in zip(predictions, targets)]

    choice = json.dumps({"answer": "rectangle", "choices": ["ellipse", "rectangle"], "type": "text"})
    numerical = json.dumps({"answer": "12", "choices": [], "type": "integer"})
    list_ref = json.dumps({"answer": "[1, 2]", "choices": [], "type": "list"})
    verdicts = MathVistaVerifier(Numeric()).verify_many(
        ["(B)", "A", None, "12", "[1, 2]", "[2, 1]"], [choice, choice, choice, numerical, list_ref, list_ref])
    assert [v["correct"] for v in verdicts] == [True, False, False, True, True, False]
