"""CF-Geo images from committed edit patches (docs/plan/S3设计_20261109.md section 3.2, decision D45).

An item stores, for each factor k (``"k1"``: erase and redraw the same numbers, the artifact control; ``"k2"``:
every length number doubled), a list of rectangles with replacement pixels. A patch holds only pixels we made: the
background colour we filled and the digits we drew. ``rebuild`` pastes the patches onto the pinned public image and
checks the pixel SHA256 before and after, so the result is the same on every machine and no source image has to be
stored in this repository. The OCR-based builder that makes the patches is ``scripts/data/build_cfgeo.py``.
"""
import base64
import io

from src.evaluation.public_sources import image_pixel_sha256

SCHEMA = "p3-cfgeo-v1"
FACTORS = {"k1": 1, "k2": 2}


def encode_patch(image):
    """PNG (base64) of an RGBA patch: alpha 255 where we set the pixel, 0 where the source pixel stays."""
    buffer = io.BytesIO()
    image.convert("RGBA").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def decode_patch(text):
    from PIL import Image

    patch = Image.open(io.BytesIO(base64.b64decode(text.encode("ascii"))))
    patch.load()
    return patch.convert("RGBA")


def apply_edits(image, edits):
    out = image.convert("RGB").copy()
    for edit in edits:
        x0, y0, x1, y1 = edit["box"]
        patch = decode_patch(edit["patch"])
        if patch.size != (x1 - x0, y1 - y0) or x0 < 0 or y0 < 0 or x1 > out.width or y1 > out.height:
            raise ValueError("patch %s does not fit box %s in a %sx%s image" % (patch.size, edit["box"], out.width, out.height))
        alpha = patch.getchannel("A")
        if sum(alpha.histogram()[1:255]):
            raise ValueError("patch alpha must be 0 or 255 (pixels are replaced, never blended)")
        out.paste(patch.convert("RGB"), (x0, y0), mask=alpha)
    return out


def rebuild(item, source_image, variant):
    """The edited image for ``variant`` ("k1" or "k2"); raises when the source or the result has other pixels."""
    if image_pixel_sha256(source_image) != item["pixel"]:
        raise ValueError("%s: source image pixels differ from the specification" % item["id"])
    edited = apply_edits(source_image, item[variant]["edits"])
    if image_pixel_sha256(edited) != item[variant]["pixel"]:
        raise ValueError("%s: rebuilt %s image pixels differ from the specification" % (item["id"], variant))
    return edited


def references(item, variant):
    """Grading reference for the original image ("original") or an edit: {"answer"} or {"answer", "answer_set"}."""
    block = item if variant == "original" else item[variant]
    ref = {"answer": block["answer"]}
    if block.get("answer_set"):
        ref["answer_set"] = list(block["answer_set"])
    return ref


__all__ = ["FACTORS", "SCHEMA", "apply_edits", "decode_patch", "encode_patch", "rebuild", "references"]
