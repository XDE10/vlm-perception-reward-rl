"""Small fixtures built from evidence files that are committed to git.

``reports/handover_audit_20261024_v1/sample_trace.json`` holds the released
row ``train:10`` (InterGPS id 1670) and its official InterGPS record, so tests
can exercise real labels and real coordinates without the (untracked) data/.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "reports/handover_audit_20261024_v1/sample_trace.json"


def trace():
    return json.loads(TRACE.read_text(encoding="utf-8"))


def release_row_1670():
    return trace()["release_row"]


def record_1670():
    return trace()["original_annotation"]


def geometry_1670():
    from src.data.intergps_index import geometry_from_record

    return geometry_from_record(record_1670())


def synthetic_record(original_id="9001", points=None, lines=(), circles=(""), forms=(), names=None, split="train"):
    points = points or {}
    return {
        "original_id": original_id,
        "split": split,
        "question": "Find x.",
        "answer": "1",
        "image_pixel_sha256": "0" * 64,
        "original_data": {"problem_text": "Find x.", "choices": ["1"], "answer": "A", "precise_value": [1.0],
                          "problem_type_goal": ["Length"]},
        "diagram_annotation": {
            "point_instances": list(names if names is not None else points),
            "line_instances": list(lines),
            "circle_instances": list(circles),
            "diagram_logic_forms": list(forms),
            "point_positions": {k: list(v) for k, v in points.items()},
        },
        "text_annotation": {"text_logic_forms": ["Find(x)"]},
    }
