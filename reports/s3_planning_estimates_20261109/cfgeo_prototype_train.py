# Provenance copy (2026-11-09): run once in the Kiro sandbox on Geometry3K TRAIN only; paths are sandbox paths.
# Inputs: SHA-verified public pinned sources (wrapper parquet @fd21e53, InterGPS @99e6b52 train.zip and logic forms).
# Output of this run: cfgeo_prototype_train.out next to this file. Not part of the package or tests.
"""CF-Geo edit + verify prototype on TRAIN only (development; no validation/test data is read).

For each sampled strict candidate: OCR -> require every numeric token to be an annotated value and every annotated
length to be found exactly as often as annotated -> erase each length label box, redraw k*value (k=1 identity
redraw as the artifact control, k=2 the counterfactual) with Pillow's bundled font at the box height -> OCR again:
every edited box must read the new value and every other number must be unchanged. Saves a few images to look at.
"""
import io
import random
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rapidocr_onnxruntime import RapidOCR

sys.path.insert(0, "/projects/sandbox/.work/scratch")
from estimate_subsets_train import HAS_DIGIT, NUM, VAR, diagram, split_equals, text  # noqa: E402

OUT = Path("/projects/sandbox/.work/scratch/cfgeo_proto")
OUT.mkdir(exist_ok=True)
z = zipfile.ZipFile("/projects/sandbox/.work/scratch/g3k/train.zip")
ocr = RapidOCR()
NUMBER_TOKEN = re.compile(r"^(\d+(?:\.\d+)?)(?:\s*(?:cm|in\.?|ft|m|mm|yd|units?))?$")


def candidates():
    out = []
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
        if not ((length_goal or goal.startswith("Find(AreaOf")) and not any(VAR.search(v[1]) for v in angles)):
            continue
        if not all(NUM.match(v[1]) or re.fullmatch(r"\s*[a-z]\s*", v[1]) for v in lengths):
            continue
        numbers = [v[1].strip() for v in lengths if NUM.match(v[1])]
        others = [re.sub(r"[^\d.]", "", v[1]) for v in angles if NUM.match(v[1].replace(" ", ""))]
        if numbers:
            out.append((oid, numbers, others))
    return out


def read(image):
    big = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
    result, _ = ocr(np.array(big))
    boxes = []
    for points, word, conf in result or []:
        xs, ys = [p[0] / 2 for p in points], [p[1] / 2 for p in points]
        match = NUMBER_TOKEN.match(word.strip().replace("°", ""))
        boxes.append({"word": word.strip(), "number": match.group(1) if match else None,
                      "box": (min(xs), min(ys), max(xs), max(ys)), "degree": "°" in word})
    return boxes


def fmt(value):
    return str(int(value)) if float(value).is_integer() else ("%g" % value)


def edit(image, boxes, numbers, k):
    image = image.copy()
    draw = ImageDraw.Draw(image)
    arr = np.asarray(image.convert("L"))
    edits = []
    for b in boxes:
        if b["number"] in numbers and not b["degree"]:
            x0, y0, x1, y1 = [int(round(v)) for v in b["box"]]
            pad = 2
            x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(image.width - 1, x1 + pad), min(image.height - 1, y1 + pad)
            ring = np.concatenate([arr[max(0, y0 - 2), x0:x1 + 1], arr[min(arr.shape[0] - 1, y1 + 2), x0:x1 + 1]])
            background = int(np.median(ring)) if ring.size else 255
            draw.rectangle((x0, y0, x1, y1), fill=(background,) * 3)
            new = fmt(float(b["number"]) * k)
            font = ImageFont.load_default(size=max(8, int((y1 - y0) * 0.95)))
            tw, th = draw.textbbox((0, 0), new, font=font)[2:]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            draw.text((cx - tw / 2, cy - th / 2 - 1), new, fill=(0, 0, 0), font=font)
            edits.append((b["number"], new))
    return image, edits


stats = Counter()
pool = candidates()
random.Random(20261109).shuffle(pool)
saved = 0
for oid, numbers, others in pool[:40]:
    image = Image.open(io.BytesIO(z.read("train/%d/img_diagram.png" % oid))).convert("RGB")
    boxes = read(image)
    found = Counter(b["number"] for b in boxes if b["number"] in numbers and not b["degree"])
    unexplained = [b["number"] for b in boxes if b["number"] and b["number"] not in numbers and b["number"] not in others]
    if found != Counter(numbers) or unexplained:
        stats["rejected: labels not found exactly / unexplained number"] += 1
        continue
    ok = True
    for k in (1, 2):
        edited, edits = edit(image, boxes, set(numbers), k)
        expected = Counter(fmt(float(n) * k) for n in numbers)
        reread = read(edited)
        got = Counter(b["number"] for b in reread if b["number"] and not b["degree"] and b["number"] not in others)
        if got != expected:
            ok = False
            stats["rejected at verification (k=%d)" % k] += 1
            break
        if saved < 4:
            edited.save(OUT / ("%d_k%d.png" % (oid, k)))
            if k == 1:
                image.save(OUT / ("%d_orig.png" % oid))
    if ok:
        stats["accepted (k=1 and k=2 verified)"] += 1
        saved += 1
print("sampled", min(40, len(pool)), "strict candidates")
for key, value in stats.items():
    print("  %-56s %2d" % (key, value))
print("saved:", sorted(p.name for p in OUT.iterdir())[:12])
