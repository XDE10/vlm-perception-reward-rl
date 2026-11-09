import json

from scripts.data.calibrate_perception_v5 import attack_table, calibrate, main, summary_markdown
from tests._fixtures import geometry_1670, release_row_1670
from tests._mini_release import make_release


def test_calibration_on_real_row_1670_has_no_false_refutations_at_defaults():
    row = release_row_1670()
    index = {"1670": geometry_1670()}
    result = calibrate([row], index)
    line = {e["threshold"]: e for e in result["sweep"]["PointLiesOnLine"]["entries"]}
    assert result["positives_by_relation"] == {"Length": 4, "PointLiesOnLine": 2}
    assert line[0.06]["false_refutations"] == 0 and line[0.06]["spray_refuted_fraction"] > 0.5
    table = attack_table([row], index)
    assert table["incidence_spray"]["mean_v5"] < 0 < table["incidence_spray"]["mean_v4"]


def test_cli_writes_json_and_markdown(tmp_path):
    pytest = __import__("pytest")
    pytest.importorskip("PIL")
    make_release(tmp_path)
    out = tmp_path / "calib"
    result = main(["--root", str(tmp_path), "--output", str(out)])
    data = json.loads((out / "calibration.json").read_text(encoding="utf-8"))
    assert data["train_rows"] == 4 and data["schema"] == "v5-calibration-v2"
    assert data["train"]["after_gate"] and data["train"]["loo"]["limit"] == 0.05
    text = (out / "summary.md").read_text(encoding="utf-8")
    for heading in ["罗列攻击", "一致性门控", "留一法残余误杀率", "关闭门控"]:
        assert heading in text, heading
    assert summary_markdown(result).startswith("# v5")


def _row(sample_id, oid, gold):
    return {"sample_id": sample_id, "original_id": oid, "certified_positive_tokens": gold}


def _geometry(oid, points, lines):
    from src.data.intergps_index import geometry_from_record
    from tests._fixtures import synthetic_record

    return geometry_from_record(synthetic_record(original_id=oid, points=points, lines=lines))


def test_gate_report_counts_gated_rows_and_leave_one_out_residuals():
    from scripts.data.calibrate_perception_v5 import gate_report, wilson

    square = {"A": (0, 0), "B": (10, 0), "C": (10, 8), "D": (5, 0)}
    skewed = {"A": (0, 0), "B": (10, 0), "C": (15, 6), "D": (5, 0)}  # right angle drawn at ~50 degrees
    twice = {"A": (0, 0), "B": (10, 0), "C": (15, 6), "D": (5, 3), "E": (2, 0)}  # two contradictions
    perp, on_ab = "Perpendicular((A,B),(B,C))", "PointLiesOnLine(D,(A,B))"
    rows = [_row("train:1", "1", [perp, on_ab]), _row("train:2", "2", [perp, on_ab]),
            _row("train:3", "3", [perp, on_ab, "PointLiesOnLine(E,(A,B))"])]
    index = {"1": _geometry("1", square, ["AB", "BC"]), "2": _geometry("2", skewed, ["AB", "BC"]),
             "3": _geometry("3", twice, ["AB", "BC"])}
    report = gate_report(rows, index)
    assert report["gate"]["rows"] == 2 and set(report["gate"]["rows_detail"]) == {"train:2", "train:3"}
    assert report["after_gate"] == {"PointLiesOnLine": 0, "Parallel": 0, "Perpendicular": 0, "PointLiesOnCircle": 0}
    loo = report["loo"]["relations"]
    # row 2: its only contradiction is the right angle itself, so leaving it out lets it through (a residual);
    # row 3: the off-line point D still gates the coordinates when the right angle is left out (and vice versa)
    assert (loo["Perpendicular"]["certified"], loo["Perpendicular"]["residual"]) == (3, 1)
    assert loo["Perpendicular"]["residual_ids"] == ["train:2"]
    assert (loo["PointLiesOnLine"]["certified"], loo["PointLiesOnLine"]["residual"]) == (4, 0)
    assert report["loo"]["pooled"] == {"certified": 7, "residual": 1, "rate": round(1 / 7, 4), "ci95": wilson(1, 7)}
    raw = {(e["sample_id"], e["certified"]): e for e in report["raw_false_refutations"]}
    assert raw[("train:2", perp)]["reason"] == "not_perpendicular"
    assert abs(raw[("train:2", perp)]["measured"]["deviation_deg"] - 39.81) < 0.01  # 90 - atan2(6, 5)
    assert raw[("train:3", on_ab)]["measured"]["line_distance"] == 0.3


def test_wilson_interval_matches_known_values():
    from scripts.data.calibrate_perception_v5 import wilson

    assert wilson(0, 0) is None
    low, high = wilson(11, 264)
    assert 0.023 < low < 0.024 and 0.072 < high < 0.074
