# Provenance copy (2026-11-09): run once in the Kiro sandbox on Geometry3K TRAIN only; paths are sandbox paths.
# Inputs: SHA-verified public pinned sources (wrapper parquet @fd21e53, InterGPS @99e6b52 train.zip and logic forms).
# Output of this run: estimate_subsets_train.out next to this file. Not part of the package or tests.
"""Planning estimate on Geometry3K TRAIN only (InterGPS ids 0-2100): how many problems the draft S3 rules keep.

Uses the public pinned InterGPS logic forms. Text digits are approximated by numeric literals in the
dissolved text logic forms (the S3 rule itself will read the real problem text). Validation (2101-2400) and
test (2401-3001) are not read.
"""
import json
import re
from collections import Counter

LF = "/projects/sandbox/.work/scratch/g3k/lf/logic_forms/"
diagram = json.load(open(LF + "diagram_logic_forms_annot.json"))
text = json.load(open(LF + "text_logic_forms_annot_dissolved.json"))
EQ = re.compile(r"^Equals\((LengthOf|MeasureOf|AreaOf|PerimeterOf|RadiusOf|DiameterOf|ScaleFactorOf|.*?)\((.*)\),\s*(.+)\)$")
NUM = re.compile(r"^\s*\d+(\.\d+)?\s*$")
HAS_DIGIT = re.compile(r"\d")
VAR = re.compile(r"\b([a-z])\b")


def split_equals(form):
    """Equals(F(args), value) -> (F, value); value may be an expression."""
    if not form.startswith("Equals("):
        return None
    body = form[len("Equals("):-1]
    depth = 0
    for i, ch in enumerate(body):
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            left, right = body[:i].strip(), body[i + 1:].strip()
            return left.split("(", 1)[0], right
    return None


stats = Counter()
for oid in range(0, 2101):
    d, t = diagram[str(oid)], text[str(oid)]["text_logic_forms"]
    stats["train problems"] += 1
    values = [split_equals(f) for f in d["diagram_logic_forms"]]
    values = [v for v in values if v]
    numeric_diagram = [v for v in values if HAS_DIGIT.search(v[1])]
    text_numeric = any(HAS_DIGIT.search(f) for f in t if not f.startswith("Find("))
    vn = bool(numeric_diagram) and not text_numeric
    stats["vision-needed (VN)"] += vn
    if not vn:
        continue
    goal = next((f for f in t if f.startswith("Find(")), "")
    lengths = [v for v in values if v[0] == "LengthOf"]
    angles = [v for v in values if v[0] == "MeasureOf"]
    goal_var = re.fullmatch(r"Find\(([a-z])\)", goal)
    is_length_goal = goal.startswith(("Find(LengthOf", "Find(PerimeterOf", "Find(RadiusOf", "Find(DiameterOf"))
    is_area_goal = goal.startswith("Find(AreaOf")
    if goal_var:
        var = goal_var.group(1)
        in_len = any(var in VAR.findall(v[1]) for v in lengths)
        in_ang = any(var in VAR.findall(v[1]) for v in angles)
        is_length_goal = in_len and not in_ang
    plain = all(NUM.match(v[1]) or re.fullmatch(r"\s*[a-z]\s*", v[1]) for v in lengths)
    numeric_lengths = [v for v in lengths if NUM.match(v[1])]
    no_var_in_angles = not any(VAR.search(v[1]) for v in angles)
    stats["VN with length goal"] += is_length_goal
    stats["VN with area goal"] += is_area_goal
    cf = (is_length_goal or is_area_goal) and plain and numeric_lengths and no_var_in_angles
    stats["CF-Geo candidate (strict)"] += bool(cf)
    if cf:
        stats["numeric length labels to edit (in CF candidates)"] += len(numeric_lengths)
for k, v in stats.items():
    print("%-52s %5d  (%.1f%% of train)" % (k, v, 100.0 * v / stats["train problems"]))
