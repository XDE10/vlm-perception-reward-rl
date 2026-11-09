# Provenance copy (2026-11-09): run once in the Kiro sandbox on Geometry3K TRAIN only; paths are sandbox paths.
# Inputs: SHA-verified public pinned sources (wrapper parquet @fd21e53, InterGPS @99e6b52 train.zip and logic forms).
# Output of this run: estimate_cf_exact_train.out next to this file. Not part of the package or tests.
"""Planning estimate on Geometry3K TRAIN only: the S3 subset rules as pre-registered in S3设计_20261109.md.

Joins the pinned wrapper train parquet to InterGPS train records by exact RGB pixels + normalized question
(same rule as src/data/project3_audit.py). Validation and test files are not opened.
"""
import hashlib
import io
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict

import pyarrow.parquet as pq
from PIL import Image

sys.path.insert(0, "/projects/sandbox/vlm-perception-reward-rl")
G3K = "/projects/sandbox/.work/scratch/g3k/"


def norm(text):
    text = unicodedata.normalize("NFKC", str(text)).replace("<image>", "")
    return re.sub(r"\s+", "", text).casefold().rstrip(".")


def image_hash(data):
    image = Image.open(io.BytesIO(data)).convert("RGB")
    return hashlib.sha256(str(image.size).encode() + b"\0" + image.tobytes()).hexdigest()


lf = zipfile.ZipFile(G3K + "logic_forms.zip")
diagram = json.loads(lf.read("logic_forms/diagram_logic_forms_annot.json"))
dissolved = json.loads(lf.read("logic_forms/text_logic_forms_annot_dissolved.json"))
z = zipfile.ZipFile(G3K + "train.zip")
by_pixels = defaultdict(list)
for name in z.namelist():
    if not name.endswith("/data.json"):
        continue
    data = json.loads(z.read(name))
    folder = name.rsplit("/", 1)[0]
    forms = {norm(data[f]) for f in ("problem_text", "compact_text", "annotat_text") if data.get(f)}
    by_pixels[image_hash(z.read(folder + "/img_diagram.png"))].append((str(data["id"]), forms, data))

rows = pq.read_table(G3K + "train-00000-of-00001.parquet").to_pylist()

DIGIT = re.compile(r"[0-9]")
NUM = re.compile(r"^\s*\d+(\.\d+)?\s*$")
VAR1 = re.compile(r"^\s*[a-z]\s*$")
VAR = re.compile(r"\b[a-z]\b")
ROUND = re.compile(r"\b(round|nearest)\b", re.I)
LENGTH_GOALS = ("Find(LengthOf", "Find(PerimeterOf", "Find(RadiusOf", "Find(DiameterOf")


def split_equals(form):
    if not form.startswith("Equals("):
        return None
    body = form[len("Equals("):-1]
    depth = 0
    for i, ch in enumerate(body):
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            return body[:i].strip().split("(", 1)[0], body[i + 1:].strip()
    return None


from math_verify import parse  # noqa: E402

stats = Counter()
reasons = Counter()
for row in rows:
    stats["wrapper rows"] += 1
    pixels = image_hash(row["images"][0]["bytes"])
    agreeing = [c for c in by_pixels.get(pixels, []) if norm(row["problem"]) in c[1]]
    if len(agreeing) != 1:
        stats["not joined (excluded)"] += 1
        continue
    oid, _, data = agreeing[0]
    stats["joined"] += 1
    text = row["problem"].removeprefix("<image>").strip()
    values = [v for v in (split_equals(f) for f in diagram[oid]["diagram_logic_forms"]) if v]
    numeric = [v for v in values if DIGIT.search(v[1])]
    vn = bool(numeric) and not DIGIT.search(text)
    stats["VN"] += vn
    if not vn:
        continue
    goal = next((f for f in dissolved[oid]["text_logic_forms"] if f.startswith("Find(")), "")
    lengths = [v for v in values if v[0] == "LengthOf"]
    angles = [v for v in values if v[0] == "MeasureOf"]
    if any(v[0] not in ("LengthOf", "MeasureOf") for v in numeric):
        reasons["other numeric diagram value (area/perimeter/radius/...)"] += 1
        continue
    if not all(NUM.match(v[1]) or VAR1.match(v[1]) for v in lengths):
        reasons["length label is an expression"] += 1
        continue
    if not all(NUM.match(v[1]) for v in angles):
        reasons["angle label is not a plain number"] += 1
        continue
    if not any(NUM.match(v[1]) for v in lengths):
        reasons["no numeric length label"] += 1
        continue
    m = re.fullmatch(r"Find\(([a-z])\)", goal)
    if m:
        degree = 1 if any(m.group(1) == v[1].strip() for v in lengths) else None
    elif goal.startswith(LENGTH_GOALS):
        degree = 1
    elif goal.startswith("Find(AreaOf"):
        degree = 2
    else:
        degree = None
    if degree is None:
        reasons["goal is not a length or area"] += 1
        continue
    stats["CF strict (structure)"] += 1
    stats[f"CF strict, degree {degree}"] += 1
    if ROUND.search(text):
        reasons["rounding requested"] += 1
        continue
    gold = parse("$" + row["answer"] + "$")
    if not gold:
        reasons["gold does not parse"] += 1
        continue
    stats["CF strict + exact gold"] += 1
    stats["numeric length labels to edit"] += sum(bool(NUM.match(v[1])) for v in lengths)

n = stats["wrapper rows"]
for k, v in stats.items():
    print("%-44s %5d  (%.1f%% of train rows; x601 = %.0f)" % (k, v, 100.0 * v / n, 601.0 * v / n))
print("excluded from CF after VN:")
for k, v in reasons.most_common():
    print("   %-60s %4d" % (k, v))
