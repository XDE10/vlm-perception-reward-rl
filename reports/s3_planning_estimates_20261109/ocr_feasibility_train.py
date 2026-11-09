# Provenance copy (2026-11-09): run once in the Kiro sandbox on Geometry3K TRAIN only; paths are sandbox paths.
# Inputs: SHA-verified public pinned sources (wrapper parquet @fd21e53, InterGPS @99e6b52 train.zip and logic forms).
# Output of this run: ocr_feasibility_train.out next to this file. Not part of the package or tests.
"""CF-Geo feasibility on TRAIN only: can OCR find every numeric length label of a candidate exactly once?

Sample: 60 strict CF-Geo candidates from InterGPS train ids (seed 20261109). Uses the pinned public InterGPS
train.zip (img_diagram.png, data.json) and logic forms. No validation or test problem is read.
"""
import io
import json
import random
import re
import sys
import zipfile
from collections import Counter

import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

sys.path.insert(0, "/projects/sandbox/.work/scratch")
from estimate_subsets_train import HAS_DIGIT, NUM, VAR, diagram, split_equals, text  # noqa: E402

z = zipfile.ZipFile("/projects/sandbox/.work/scratch/g3k/train.zip")
candidates = []
for oid in range(0, 2101):
    d, t = diagram[str(oid)], text[str(oid)]["text_logic_forms"]
    values = [v for v in (split_equals(f) for f in d["diagram_logic_forms"]) if v]
    if not any(HAS_DIGIT.search(v[1]) for v in values) or any(HAS_DIGIT.search(f) for f in t if not f.startswith("Find(")):
        continue
    goal = next((f for f in t if f.startswith("Find(")), "")
    lengths = [v for v in values if v[0] == "LengthOf"]
    angles = [v for v in values if v[0] == "MeasureOf"]
    m = re.fullmatch(r"Find\(([a-z])\)", goal)
    length_goal = goal.startswith(("Find(LengthOf", "Find(PerimeterOf", "Find(RadiusOf", "Find(DiameterOf"))
    if m:
        length_goal = any(m.group(1) in VAR.findall(v[1]) for v in lengths) and not any(
            m.group(1) in VAR.findall(v[1]) for v in angles)
    area_goal = goal.startswith("Find(AreaOf")
    plain = all(NUM.match(v[1]) or re.fullmatch(r"\s*[a-z]\s*", v[1]) for v in lengths)
    numbers = [v[1].strip() for v in lengths if NUM.match(v[1])]
    if (length_goal or area_goal) and plain and numbers and not any(VAR.search(v[1]) for v in angles):
        candidates.append((oid, numbers, [v[1].strip() for v in values if HAS_DIGIT.search(v[1])]))
random.Random(20261109).shuffle(candidates)
sample = candidates[:60]
ocr = RapidOCR()
outcome = Counter()
examples = []
for oid, numbers, all_numeric in sample:
    image = Image.open(io.BytesIO(z.read("train/%d/img_diagram.png" % oid))).convert("RGB")
    scale = 2 if max(image.size) < 600 else 1  # small diagrams: upscale for the detector
    big = image.resize((image.width * scale, image.height * scale), Image.LANCZOS)
    result, _ = ocr(np.array(big))
    tokens = [(r[1].strip(), r[2]) for r in (result or [])]
    found = Counter()
    for word, conf in tokens:
        for number in set(numbers):
            if re.fullmatch(r"%s(\s*(cm|in\.?|ft|m|mm|yd|units?))?" % re.escape(number), word):
                found[number] += 1
    need = Counter(numbers)
    exact = all(found[n] == need[n] for n in need)
    outcome["all labels found exactly as often as annotated" if exact else "missing or ambiguous"] += 1
    if len(examples) < 8:
        examples.append({"oid": oid, "need": dict(need), "found": dict(found), "ocr": [w for w, _ in tokens][:12]})
print("strict CF candidates in train:", len(candidates), "| sampled:", len(sample))
for k, v in outcome.items():
    print("  %-50s %2d / %d" % (k, v, len(sample)))
for e in examples:
    print(json.dumps(e, ensure_ascii=False))
