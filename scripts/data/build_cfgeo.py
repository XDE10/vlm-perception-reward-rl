"""Build CF-Geo edit patches with OCR (local machine or sandbox; needs rapidocr-onnxruntime 1.4.4 and Pillow 13.0.0).

    python -m scripts.data.build_cfgeo --sources DIR --spec reports/eval_sets_20261109/eval_sets.json \
        --out reports/cfgeo_20261109/cfgeo.json
    python -m scripts.data.build_cfgeo --sources DIR --dev-train 48 --out reports/cfgeo_20261109/cfgeo_dev_train.json

Implements docs/plan/S3设计_20261109.md section 3.2 with the editing steps of its revision 1 (section 11), for every
CF candidate of the evaluation-set specification (validation and test) or, with ``--dev-train``, for train
candidates that only serve code-path checks. For k=1 (erase and redraw the same numbers, the artifact control) and
k=2 (double every length number):

1. OCR every text box. Each annotated numeric length must be found exactly as often as annotated (a unit such as
   "cm" or "in." may follow the number and is redrawn unchanged); every box with a digit must be an annotated
   length or angle; otherwise the item is excluded.
2. Erase the label: inside its box (grown by 2 px), every ink blob that does not leave the grown box is the label
   and is set to the local background (RGB median of a 3 px ring), together with its faint anti-aliased fringe.
   A stroke that enters the box from outside stays untouched; if any of its pixels has the label's colour (for
   example a black line touching black digits) the label cannot be separated and the item is excluded.
3. Draw the new text in Pillow's built-in font in the label's colour: k=1 redraws exactly the printed string, k=2
   prints k*v with the fewest digits. One style per label serves both: the font size matches the ink height of the
   original string, the glyphs are condensed to its ink width, and a stroke (drawn at 4x and reduced by area
   averaging) matches its ink mass, i.e. its weight (editor v3, after the first spot check). The new text is centred
   on the original ink; text that would cover other ink or touch another label excludes the item.
4. OCR the edited image: every new number read back at its place (IoU >= 0.3 with the original box), every angle
   label unchanged (IoU >= 0.5), no other number; otherwise the item is excluded.

An item is kept only if both k=1 and k=2 pass. A patch is an RGBA rectangle whose alpha is 255 exactly where we set
a pixel (our background fill or our digits) and 0 elsewhere, with those other pixels stored as zeros; no source
pixel and no source image is written. Development used train only (scripts in reports/cfgeo_20261109/).
"""
import argparse
import json
import math
import random
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDIT_VERSION = "cfgeo-edit-v3-20261109"
PARAMS = {"upscale": 2, "pad": 2, "ring": 3, "bg_tolerance": 24, "ring_background_share": 0.6, "ink_threshold": 64,
          "text_tolerance": 80, "cover_alpha": 0.2, "squeeze": [0.6, 1.2], "supersample": 4, "max_stroke": 6,
          "iou_new": 0.3, "iou_angle": 0.5, "font_sizes": [6, 120]}
DEGREE_MARKS = "°º˚"
TOKEN = re.compile(r"^(\d+(?:\.\d+)?)(\s*(?:cm|mm|km|m|in\.?|ft|yd|units?))?$")
DIGIT = re.compile(r"\d")
SEED = 20261109


class Reject(Exception):
    pass


def canon(value):
    return format(Decimal(str(value)).normalize(), "f")


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def grow(box, by, width, height):
    return (max(0, box[0] - by), max(0, box[1] - by), min(width, box[2] + by), min(height, box[3] + by))


def overlaps(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


class Ocr(object):
    def __init__(self):
        from rapidocr_onnxruntime import RapidOCR

        self.engine = RapidOCR()

    def boxes(self, image):
        import numpy as np
        from PIL import Image

        k = PARAMS["upscale"]
        result, _ = self.engine(np.array(image.resize((image.width * k, image.height * k), Image.LANCZOS)))
        out = []
        for points, word, confidence in result or []:
            xs, ys = [p[0] / k for p in points], [p[1] / k for p in points]
            box = (max(0, math.floor(min(xs))), max(0, math.floor(min(ys))), min(image.width, math.ceil(max(xs))),
                   min(image.height, math.ceil(max(ys))))
            raw = str(word).strip()
            core = re.sub(r"\s+", " ", raw).strip(DEGREE_MARKS + " ")
            match = TOKEN.match(core)
            out.append({"text": raw, "box": box, "degree": any(m in raw for m in DEGREE_MARKS),
                        "number": match.group(1) if match else None, "suffix": (match.group(2) or "") if match else "",
                        "digit": bool(DIGIT.search(raw)), "confidence": round(float(confidence), 4)})
        return out


def classify(boxes, lengths, angles):
    """(length boxes, angle boxes) or Reject: every digit must be an annotated length or angle label."""
    need = Counter(canon(v) for v in lengths)
    angle_values = {canon(a) for a in angles}
    length_boxes, angle_boxes = [], []
    for b in boxes:
        if not b["digit"]:
            continue
        if b["number"] is None:
            raise Reject("text with a digit that is not a number label: %r" % b["text"])
        value = canon(b["number"])
        if b["degree"]:
            if value not in angle_values or b["suffix"]:
                raise Reject("angle %r is not annotated" % b["text"])
            angle_boxes.append(b)
        elif value in need and value in angle_values:
            raise Reject("number %s is both a length and an angle label" % value)
        elif value in need:
            length_boxes.append(b)
        elif value in angle_values and not b["suffix"]:
            angle_boxes.append(b)  # an angle label whose degree mark OCR did not read
        else:
            raise Reject("number %r is not annotated" % b["text"])
    found = Counter(canon(b["number"]) for b in length_boxes)
    if found != need:
        raise Reject("length labels found %s, annotated %s" % (dict(found), dict(need)))
    return length_boxes, angle_boxes


_FONTS = {}


def font(size):
    from PIL import ImageFont

    if size not in _FONTS:
        _FONTS[size] = ImageFont.load_default(size=size)
    return _FONTS[size]


def render(text, size, squeeze, stroke=0):
    """Coverage (mode L) of ``text``: drawn at SUPERSAMPLE x the size with ``stroke`` (in supersampled pixels) to
    match the original weight, condensed by ``squeeze`` and reduced by area averaging (no ringing)."""
    from PIL import Image, ImageDraw

    k = PARAMS["supersample"]
    big = font(size * k)
    left, top, right, bottom = big.getbbox(text, stroke_width=stroke)
    canvas = Image.new("L", (right - left + 4 * k, bottom - top + 4 * k), 0)
    ImageDraw.Draw(canvas).text((2 * k - left, 2 * k - top), text, font=big, fill=255, stroke_width=stroke,
                                stroke_fill=255)
    return canvas.resize((max(1, int(round(canvas.width * squeeze / k))), max(1, int(round(canvas.height / k)))),
                         Image.BOX)


def ink_extent(glyph):
    """Width and height of the pixels with coverage >= 0.1 (comparable to the original ink box)."""
    import numpy as np

    ys, xs = np.nonzero(np.asarray(glyph) >= 26)
    return (int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)) if len(xs) else (0, 0)


def fit_style(text, ink_width, ink_height, ink_mass):
    """Font size, horizontal condensing and stroke so that ``text`` (the original string) has the original ink
    height, width and ink mass (sum of coverage); S3 design 3.2 step 3, revisions 1 and 3."""
    import numpy as np

    low, high = PARAMS["font_sizes"]
    best = None
    for stroke in range(0, PARAMS["max_stroke"] + 1):
        guess = min(range(low, high + 1), key=lambda s: abs(ink_extent_estimate(text, s, stroke) - ink_height))
        sizes = [s for s in range(guess - 2, guess + 3) if low <= s <= high]
        size = min(sizes, key=lambda s: abs(ink_extent(render(text, s, 1.0, stroke))[1] - ink_height))
        width = ink_extent(render(text, size, 1.0, stroke))[0]
        squeeze = min(PARAMS["squeeze"][1], max(PARAMS["squeeze"][0], ink_width / float(width or 1)))
        glyph = render(text, size, squeeze, stroke)
        mass = float(np.asarray(glyph, dtype=np.float64).sum() / 255.0)
        error = abs(mass - ink_mass) / max(ink_mass, 1e-6)
        if best is None or error < best[0]:
            best = (error, size, squeeze, stroke)
    return best[1], best[2], best[3]


def ink_extent_estimate(text, size, stroke):
    left, top, right, bottom = font(size * PARAMS["supersample"]).getbbox(text, stroke_width=stroke)
    return (bottom - top) / float(PARAMS["supersample"])


def dilate(mask):
    """One-pixel 8-neighbour dilation of a boolean mask."""
    out = mask.copy()
    out[1:, :] |= mask[:-1, :]
    out[:-1, :] |= mask[1:, :]
    out[:, 1:] |= mask[:, :-1]
    out[:, :-1] |= mask[:, 1:]
    out[1:, 1:] |= mask[:-1, :-1]
    out[1:, :-1] |= mask[:-1, 1:]
    out[:-1, 1:] |= mask[1:, :-1]
    out[:-1, :-1] |= mask[1:, 1:]
    return out


def components(mask):
    """8-connected components of a small boolean mask, as (ys, xs) index arrays."""
    import numpy as np

    seen = np.zeros_like(mask, dtype=bool)
    height, width = mask.shape
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        stack, ys, xs = [(y0, x0)], [], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            ys.append(y)
            xs.append(x)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        out.append((np.array(ys), np.array(xs)))
    return out


def edit(image, length_boxes, all_boxes, factor):
    """The edited image and its edit records, or Reject (S3 design 3.2 steps 2-3, revision 1)."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    from src.evaluation.cfgeo import encode_patch
    from src.evaluation.eval_sets import scale_number

    if not isinstance(font(12), ImageFont.FreeTypeFont):
        raise SystemExit("Pillow was built without FreeType; the patches would not match the documented font")
    width, height = image.size
    source = np.asarray(image.convert("RGB"), dtype=np.int16)
    work = source.astype(np.float64)
    changed = np.zeros((height, width), dtype=bool)
    records = []
    for b in length_boxes:
        e = grow(b["box"], PARAMS["pad"], width, height)
        ring_box = grow(e, PARAMS["ring"], width, height)
        band = source[ring_box[1]:ring_box[3], ring_box[0]:ring_box[2]]
        inner = np.zeros(band.shape[:2], dtype=bool)
        inner[e[1] - ring_box[1]:e[3] - ring_box[1], e[0] - ring_box[0]:e[2] - ring_box[0]] = True
        ring = band[~inner]
        if not len(ring):
            raise Reject("no background around %s" % b["text"])
        background = np.median(ring, axis=0).round().astype(np.int16)
        if (np.abs(ring - background).max(axis=1) <= PARAMS["bg_tolerance"]).mean() < PARAMS["ring_background_share"]:
            raise Reject("the label %s sits in a busy area (no clear background)" % b["text"])
        core = source[b["box"][1]:b["box"][3], b["box"][0]:b["box"][2]]
        distance = np.abs(core - background).max(axis=2)
        core_ink = distance > PARAMS["ink_threshold"]
        if not core_ink.any():
            raise Reject("no ink in the box of %s" % b["text"])
        # the darkest part of the strokes (anti-aliased edges would pull a median towards the background)
        dark = core_ink & (distance >= np.quantile(distance[core_ink], 0.6))
        text_colour = np.median(core[dark], axis=0).round().astype(np.int16)
        inside = source[e[1]:e[3], e[0]:e[2]]
        distance_e = np.abs(inside - background).max(axis=2)
        ink_any = distance_e > PARAMS["bg_tolerance"]
        mask = np.zeros_like(ink_any)
        kept_strokes = np.zeros_like(ink_any)
        box_in_e = (b["box"][0] - e[0], b["box"][1] - e[1], b["box"][2] - e[0], b["box"][3] - e[1])
        for ys, xs in components(ink_any):
            on_border = ys.min() == 0 or xs.min() == 0 or ys.max() == ink_any.shape[0] - 1 or xs.max() == ink_any.shape[1] - 1
            in_box = (ys >= box_in_e[1]) & (ys < box_in_e[3]) & (xs >= box_in_e[0]) & (xs < box_in_e[2])
            if in_box.any() and on_border:
                # a stroke that leaves the box may stay only if none of it has the label's colour (a blue line next
                # to black digits); a text-coloured one could be part of the label or a black line touching it
                pixels = inside[ys[in_box], xs[in_box]]
                if (np.abs(pixels - text_colour).max(axis=1) <= PARAMS["text_tolerance"]).any():
                    raise Reject("the label %s touches another stroke" % b["text"])
                kept_strokes[ys, xs] = True
            elif in_box.any():
                mask[ys, xs] = True  # an ink blob inside the label box that reaches nothing outside it: the label
            else:
                kept_strokes[ys, xs] = True
        ys, xs = np.nonzero(mask)
        if not len(ys):
            raise Reject("no label ink found for %s" % b["text"])
        ink_box = (e[0] + int(xs.min()), e[1] + int(ys.min()), e[0] + int(xs.max()) + 1, e[1] + int(ys.max()) + 1)
        # the faint anti-aliased fringe of the digits goes too (never pixels next to a stroke that stays)
        fringe = dilate(mask) & ~mask & ~dilate(kept_strokes) & (distance_e <= PARAMS["ink_threshold"])
        mask = mask | fringe
        region = work[e[1]:e[3], e[0]:e[2]]
        region[mask] = background
        changed[e[1]:e[3], e[0]:e[2]] |= mask
        original_text = b["number"] + b["suffix"]
        # k=1 redraws exactly the printed string (e.g. "3.0" stays "3.0"); k=2 prints k*v with the fewest digits
        text = original_text if factor == 1 else scale_number(b["number"], factor) + b["suffix"]
        # one style per label, used for k=1 and k=2: the original string redrawn has the original ink height, width
        # and ink mass (the textbook font is narrower and often bolder than Pillow's)
        lift = np.clip(((inside.astype(np.float64) - background) @ (text_colour - background).astype(np.float64))
                       / max(1.0, float(((text_colour - background).astype(np.float64) ** 2).sum())), 0.0, 1.0)
        size, squeeze, stroke = fit_style(original_text, ink_box[2] - ink_box[0], ink_box[3] - ink_box[1],
                                          float(lift[mask].sum()))
        glyph = render(text, size, squeeze, stroke)
        gx0, gy0, gx1, gy1 = glyph.getbbox()
        x = int(round((ink_box[0] + ink_box[2]) / 2 - (gx0 + gx1) / 2))
        y = int(round((ink_box[1] + ink_box[3]) / 2 - (gy0 + gy1) / 2))
        new_box = (x + gx0, y + gy0, x + gx1, y + gy1)
        if x < 0 or y < 0 or x + glyph.width > width or y + glyph.height > height:
            raise Reject("new text for %s would leave the image" % b["text"])
        for other in all_boxes:
            if other is not b and overlaps(grow(new_box, 1, width, height), grow(other["box"], 1, width, height)):
                raise Reject("new text for %s would touch the label %r" % (b["text"], other["text"]))
        coverage = Image.new("L", (width, height), 0)
        coverage.paste(glyph, (x, y))
        alpha = np.asarray(coverage, dtype=np.float64) / 255.0
        drawn = alpha > 0
        # the new text may only cover background or the ink we erased: never a line, a mark or another label
        foreign = (alpha >= PARAMS["cover_alpha"]) & ~changed & (np.abs(source - background).max(axis=2) > PARAMS["ink_threshold"])
        if foreign.any():
            raise Reject("new text for %s would cover other ink" % b["text"])
        work = work * (1 - alpha[..., None]) + text_colour[None, None, :] * alpha[..., None]
        changed |= drawn
        records.append({"from": b["text"], "to": text, "font_size": size, "squeeze": round(squeeze, 4), "stroke": stroke,
                        "original_box": list(b["box"]),
                        "new_box": list(new_box), "background": [int(c) for c in background],
                        "text_colour": [int(c) for c in text_colour],
                        "rect": list(grow((min(e[0], new_box[0]), min(e[1], new_box[1]), max(e[2], new_box[2]),
                                           max(e[3], new_box[3])), 1, width, height))})
    edited = np.clip(np.rint(work), 0, 255).astype(np.uint8)
    changed &= np.any(edited != source.astype(np.uint8), axis=2)
    if not changed.any():
        raise Reject("the edit changed no pixel")
    rects = merge_rects([r.pop("rect") for r in records])
    inside = np.zeros_like(changed)
    patches = []
    for x0, y0, x1, y1 in rects:
        inside[y0:y1, x0:x1] = True
        sub = changed[y0:y1, x0:x1]
        rgba = np.zeros((y1 - y0, x1 - x0, 4), dtype=np.uint8)
        rgba[..., :3][sub] = edited[y0:y1, x0:x1][sub]
        rgba[..., 3][sub] = 255
        patches.append({"box": [x0, y0, x1, y1], "patch": encode_patch(Image.fromarray(rgba, "RGBA"))})
    if (changed & ~inside).any():
        raise SystemExit("internal error: a changed pixel lies outside every patch")
    return Image.fromarray(edited, "RGB"), records, patches


def merge_rects(rects):
    """Merge overlapping rectangles (x0, y0, x1, y1) so that patches never overlap."""
    rects = [tuple(r) for r in rects]
    merged = True
    while merged:
        merged = False
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if overlaps(rects[i], rects[j]):
                    a, b = rects[i], rects[j]
                    rects[i] = (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))
                    del rects[j]
                    merged = True
                    break
            if merged:
                break
    return sorted(rects)


def verify(ocr, edited, records, angle_boxes):
    """S3 design 3.2 step 4; returns None or the reason."""
    boxes = [b for b in ocr.boxes(edited) if b["digit"]]
    used = set()
    for record in records:
        target = TOKEN.match(re.sub(r"\s+", " ", record["to"]).strip())
        hit = [i for i, b in enumerate(boxes) if i not in used and b["number"] is not None and not b["degree"]
               and canon(b["number"]) == canon(target.group(1)) and iou(b["box"], record["original_box"]) >= PARAMS["iou_new"]]
        if not hit:
            return "new number %s not read back at its place" % record["to"]
        used.add(hit[0])
    for a in angle_boxes:
        hit = [i for i, b in enumerate(boxes) if i not in used and b["number"] is not None
               and canon(b["number"]) == canon(a["number"]) and iou(b["box"], a["box"]) >= PARAMS["iou_angle"]]
        if not hit:
            return "angle label %s changed" % a["text"]
        used.add(hit[0])
    extra = [b["text"] for i, b in enumerate(boxes) if i not in used]
    return "other numbers appeared: %s" % extra if extra else None


def references(candidate, factor_name):
    from src.evaluation.eval_sets import rounded_answer_set, scaled_exact_gold

    m = {"k1": 1, "k2": 2}[factor_name] ** candidate["degree"]
    if candidate["places"] is None:
        return {"answer": candidate["answer"] if m == 1 else scaled_exact_gold(candidate["answer"], m)}
    centre = format((Decimal(candidate["answer"]) * m).normalize(), "f") if m != 1 else candidate["answer"]
    return {"answer": centre, "answer_set": rounded_answer_set(candidate["answer"], candidate["places"], m)}


def build_item(ocr, candidate, image):
    from src.evaluation.public_sources import image_pixel_sha256

    if image_pixel_sha256(image) != candidate["pixel"]:
        raise Reject("source image pixels differ from the evaluation-set specification")
    boxes = ocr.boxes(image)
    length_boxes, angle_boxes = classify(boxes, candidate["lengths"], candidate["angles"])
    item = {key: candidate[key] for key in ("id", "pixel", "original_id", "answer", "degree", "places", "lengths",
                                            "angles")}
    if candidate["places"] is not None:
        item["answer_set"] = [candidate["answer"]]
    for name, factor in (("k1", 1), ("k2", 2)):
        edited, records, patches = edit(image, length_boxes, boxes, factor)
        problem = verify(ocr, edited, records, angle_boxes)
        if problem:
            raise Reject("%s verification: %s" % (name, problem))
        item[name] = {"pixel": image_pixel_sha256(edited), "edits": patches, "labels": records,
                      **references(candidate, name)}
    item["ocr_original"] = [{"text": b["text"], "box": list(b["box"])} for b in boxes if b["digit"]]
    return item


def train_candidates(sources):
    from src.data.project3_audit import original_records
    from src.evaluation.eval_sets import _forms, cf_candidate, join_rows
    from src.evaluation.public_sources import read_wrapper

    rows = read_wrapper(Path(sources) / "geometry3k/data/train-00000-of-00001.parquet")
    records = [r for r in original_records(Path(sources)) if r["split"] == "train"]
    out = []
    for item in join_rows("train", rows, records):
        if item["status"] != "matched":
            continue
        diagram, text = _forms(item["record"])
        verdict = cf_candidate(item["problem"], item["answer"], diagram, text)
        if verdict["ok"]:
            out.append({"id": item["id"], "pixel": item["pixel"], "original_id": str(item["record"]["original_id"]),
                        "answer": str(item["answer"]), "degree": verdict["degree"], "places": verdict["places"],
                        "lengths": verdict["lengths"], "angles": verdict["angles"]})
    return out


def run(candidates, images, limit=None):
    ocr = Ocr()
    items, rejected = [], []
    for candidate in candidates:
        if limit is not None and len(items) >= limit:
            break
        try:
            items.append(build_item(ocr, candidate, images[candidate["id"]]))
        except Reject as exc:
            rejected.append({"id": candidate["id"], "reason": str(exc)})
    return items, rejected


def main(argv=None):
    import PIL

    from src.evaluation.cfgeo import SCHEMA
    from src.evaluation.public_sources import read_wrapper

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True)
    parser.add_argument("--spec", default=None, help="evaluation-set specification (held-out CF candidates)")
    parser.add_argument("--dev-train", type=int, default=None, help="build this many train items instead")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if bool(args.spec) == bool(args.dev_train):
        parser.error("pass exactly one of --spec and --dev-train")
    if args.dev_train:
        candidates = train_candidates(args.sources)
        random.Random(SEED).shuffle(candidates)
        splits, purpose = ["train"], "development set (train only): code-path checks, never an endpoint"
    else:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        candidates = spec["cf_candidates"]
        splits, purpose = ["validation", "test"], "E2 evaluation set (S3 design section 3, D45)"
    images = {}
    for split in splits:
        for number, row in enumerate(read_wrapper(Path(args.sources) / ("geometry3k/data/%s-00000-of-00001.parquet" % split),
                                                  with_images=True)):
            images["%s:%d" % (split, number)] = row["image"]
    items, rejected = run(candidates, images, args.dev_train)
    by_reason = Counter(_short(r["reason"]) for r in rejected)
    out = {"schema": SCHEMA, "edit_version": EDIT_VERSION, "purpose": purpose,
           "design": "docs/plan/S3设计_20261109.md section 3.2", "params": PARAMS,
           "tools": {"ocr": "rapidocr-onnxruntime 1.4.4", "pillow": PIL.__version__,
                     "font": "Pillow ImageFont.load_default(size) (bundled Aileron Regular)"},
           "source_spec": args.spec, "candidates": len(candidates) if not args.dev_train else None,
           "counts": {"kept": len(items), "rejected": len(rejected),
                      "kept_by_split": dict(Counter(i["id"].split(":")[0] for i in items)),
                      "kept_rounded": sum(i["places"] is not None for i in items),
                      "kept_degree": dict(Counter(str(i["degree"]) for i in items)),
                      "edits": sum(len(i["k2"]["edits"]) for i in items)},
           "rejected_by_reason": dict(by_reason.most_common()), "rejected": rejected, "items": items}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"counts": out["counts"], "rejected_by_reason": out["rejected_by_reason"]}, ensure_ascii=False))


def _short(reason):
    """Group rejection reasons without their item-specific values."""
    reason = re.sub(r"'[^']*'|\"[^\"]*\"", "<text>", reason)
    reason = re.sub(r"\{[^}]*\}", "<counts>", reason)
    reason = re.sub(r"\[[^\]]*\]", "<list>", reason)
    reason = re.sub(r"\b\d+(?:\.\d+)?\b", "<n>", reason)
    return reason


if __name__ == "__main__":
    main()
