"""Descriptive reward-hacking monitors in the run summary (S4 pre-registration revision 3, D65)."""
from scripts.colab.summarize_run import perception_monitor

W = {"answer": 1.0, "format": 0.05, "perception": 0.1}


def row(fmt, perception, status="ok", tp=0, false=0, unknown=0, gated=None):
    return {"rewards": {"answer": 0.0, "format": fmt, "perception": perception}, "weights": W,
            "v5": {"status": status, "tp": tp, "false": false, "unknown": unknown, "gated": gated or []}}


def test_perception_monitor_counts():
    rows = [row(1.0, -0.8, false=2, unknown=2, gated=["coordinates"]),  # 0.05 - 0.08 < 0: below a broken block
            row(1.0, 0.5, tp=2, unknown=2),
            row(0.0, 0.0, status="block_missing"),
            row(1.0, -0.4, false=1)]  # 0.05 - 0.04 >= 0
    m = perception_monitor(rows)
    assert m["block_fail_rate"] == 0.25
    assert m["unknown_share"] == round(4 / 9, 4)
    assert m["gated_rate"] == 0.25
    assert m["valid_format_below_broken_rate"] == 0.25


def test_perception_monitor_handles_old_records():
    m = perception_monitor([{"rewards": {"format": 0.0, "perception": 0.0}, "weights": W, "v5": {"status": "block_x"}}])
    assert m == {"block_fail_rate": 1.0, "unknown_share": None, "gated_rate": 0.0, "valid_format_below_broken_rate": 0.0}
