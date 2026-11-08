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
    assert data["train_rows"] == 4 and data["schema"] == "v5-calibration-v1"
    assert "罗列攻击" in (out / "summary.md").read_text(encoding="utf-8")
    assert summary_markdown(result).startswith("# v5")
