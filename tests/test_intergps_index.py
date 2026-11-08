import json

import pytest

from src.data.intergps_index import Geometry, geometry_from_record, load_index
from tests._fixtures import geometry_1670, record_1670, synthetic_record


def test_real_record_1670_geometry():
    g = geometry_1670()
    assert g.original_id == "1670" and g.split == "train"
    assert g.point_names == ("A", "B", "C", "D", "E")
    assert g.points["C"] == (118.0, 78.0)
    # line_instances BA, CA, CB, DA, DC, EB, EC, ED are normalised to sorted pairs
    assert g.lines == (("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "E"), ("C", "D"), ("C", "E"), ("D", "E"))
    assert g.has_line("B", "A") and not g.has_line("A", "E")
    assert g.circles == () and g.circle_points == {}
    assert g.goal_types == ("Length",) and g.answer == "4" and g.precise_answer == 4.0
    assert g.text_logic_forms == ("Find(x)",)


def test_missing_coordinates_and_circles_are_parsed_conservatively():
    record = synthetic_record(
        points={"A": (0, 0), "B": (-1, -1), "O": (5, 5)},
        names=["A", "B", "O", "bad name"],
        lines=["AB", "AO", "A", "ABC"],
        circles=["O", ""],
        forms=["PointLiesOnCircle(A, Circle(O, radius_1_0))", "PointLiesOnCircle(B, Circle(O))"],
    )
    g = geometry_from_record(record)
    assert g.point_names == ("A", "B", "O")
    assert "B" not in g.points  # [-1, -1] is the InterGPS "no position" sentinel
    assert g.lines == (("A", "B"), ("A", "O"))
    assert g.circles == ("O",) and g.circle_points == {"O": ("A", "B")}


def test_json_round_trip_is_lossless():
    g = geometry_1670()
    back = Geometry.from_json(g.to_json())
    assert back == g


def test_load_index_subset_fails_closed(tmp_path):
    path = tmp_path / "ann.jsonl"
    path.write_text(json.dumps(record_1670()) + "\n" + json.dumps(synthetic_record("9001")) + "\n", encoding="utf-8")
    assert set(load_index(path)) == {"1670", "9001"}
    assert set(load_index(path, ["1670"])) == {"1670"}
    with pytest.raises(ValueError, match="missing"):
        load_index(path, ["1670", "77"])
    path.write_text(json.dumps(record_1670()) + "\n" + json.dumps(record_1670()) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        load_index(path)
