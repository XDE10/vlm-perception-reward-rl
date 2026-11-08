"""Read-only geometry view of the official InterGPS human annotations.

Source file: ``data/project3_audit/intergps_annotations.jsonl`` (one record per
original Geometry3K problem, built by ``src/data/project3_audit.py``). The
perception reward v5 uses this view only to *refute* claims (point existence,
incidence, parallel/perpendicular directions, on-circle distance). Coordinates
are diagram pixels up to an unknown translation, so every check built on them
must be translation invariant. Nothing here is a visual gold label.
"""
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

POINT = r"[A-Z][0-9]*"
_POINT_RE = re.compile(POINT)
_ON_CIRCLE_RE = re.compile(r"PointLiesOnCircle\(\s*(" + POINT + r")\s*,\s*Circle\(\s*(" + POINT + r")\b")
MISSING = (-1.0, -1.0)


@dataclass(frozen=True)
class Geometry:
    original_id: str
    split: str
    point_names: tuple
    points: dict = field(default_factory=dict)  # name -> (x, y); only valid coordinates
    lines: tuple = ()  # sorted (a, b) pairs of drawn segments
    circles: tuple = ()  # circle centre names
    circle_points: dict = field(default_factory=dict)  # centre -> sorted point names on it
    diagram_logic_forms: tuple = ()
    text_logic_forms: tuple = ()
    problem_text: str = ""
    goal_types: tuple = ()
    answer: str = ""
    precise_answer: float = None
    image_pixel_sha256: str = ""

    def has_line(self, a, b):
        return tuple(sorted((a, b))) in set(self.lines)

    def to_json(self):
        data = asdict(self)
        data["points"] = {k: list(v) for k, v in self.points.items()}
        return json.dumps(data, sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_json(cls, text):
        data = json.loads(text)
        data["points"] = {k: tuple(v) for k, v in data["points"].items()}
        data["circle_points"] = {k: tuple(v) for k, v in data["circle_points"].items()}
        for key in ["point_names", "lines", "circles", "diagram_logic_forms", "text_logic_forms", "goal_types"]:
            data[key] = tuple(tuple(x) if isinstance(x, list) else x for x in data[key])
        return cls(**data)


def _segment(text):
    names = _POINT_RE.findall(str(text))
    if len(names) != 2 or names[0] == names[1] or "".join(names) != str(text).strip():
        return None
    return tuple(sorted(names))


def _valid_xy(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    try:
        x, y = float(value[0]), float(value[1])
    except (TypeError, ValueError):
        return None
    if (x, y) == MISSING or x != x or y != y:
        return None
    return (x, y)


def geometry_from_record(record):
    """Build a Geometry from one intergps_annotations.jsonl record (fail closed on identity)."""
    oid = str(record["original_id"])
    diagram = record.get("diagram_annotation") or {}
    text = record.get("text_annotation") or {}
    original = record.get("original_data") or {}
    names = tuple(n for n in diagram.get("point_instances") or [] if re.fullmatch(POINT, str(n)))
    points = {}
    for name, value in (diagram.get("point_positions") or {}).items():
        xy = _valid_xy(value)
        if xy is not None and re.fullmatch(POINT, str(name)):
            points[str(name)] = xy
    lines = sorted({seg for seg in (_segment(x) for x in diagram.get("line_instances") or []) if seg})
    circles = sorted({str(c) for c in diagram.get("circle_instances") or [] if re.fullmatch(POINT, str(c))})
    forms = tuple(str(x) for x in diagram.get("diagram_logic_forms") or [])
    on_circle = {}
    for form in forms:
        for point, centre in _ON_CIRCLE_RE.findall(form):
            on_circle.setdefault(centre, set()).add(point)
    precise = None
    choices = original.get("choices") or []
    letter = original.get("answer")
    values = original.get("precise_value") or []
    if isinstance(letter, str) and len(letter) == 1 and 0 <= ord(letter) - 65 < min(len(choices), len(values)):
        try:
            precise = float(values[ord(letter) - 65])
        except (TypeError, ValueError):
            precise = None
    return Geometry(
        original_id=oid,
        split=str(record.get("split", "")),
        point_names=names,
        points=points,
        lines=tuple(lines),
        circles=tuple(circles),
        circle_points={k: tuple(sorted(v)) for k, v in sorted(on_circle.items())},
        diagram_logic_forms=forms,
        text_logic_forms=tuple(str(x) for x in text.get("text_logic_forms") or []),
        problem_text=str(original.get("problem_text", record.get("question", ""))),
        goal_types=tuple(str(x) for x in original.get("problem_type_goal") or []),
        answer=str(record.get("answer") or ""),
        precise_answer=precise,
        image_pixel_sha256=str(record.get("image_pixel_sha256", "")),
    )


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def load_index(path, original_ids=None):
    """Return {original_id: Geometry}; optional subset must be fully present."""
    wanted = None if original_ids is None else {str(x) for x in original_ids}
    index = {}
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            oid = str(record["original_id"])
            if wanted is not None and oid not in wanted:
                continue
            if oid in index:
                raise ValueError(f"Duplicate InterGPS original_id {oid}")
            index[oid] = geometry_from_record(record)
    if wanted is not None and wanted - set(index):
        missing = sorted(wanted - set(index))[:10]
        raise ValueError(f"InterGPS annotations missing for {len(wanted - set(index))} ids, e.g. {missing}")
    return index
