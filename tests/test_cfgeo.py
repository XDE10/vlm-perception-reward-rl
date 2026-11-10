"""CF-Geo patches (src/evaluation/cfgeo.py) and the OCR-free parts of the builder (scripts/data/build_cfgeo.py)."""
import pytest

pytest.importorskip("PIL")
np = pytest.importorskip("numpy")

from PIL import Image, ImageDraw  # noqa: E402

from scripts.data import build_cfgeo as B  # noqa: E402
from src.evaluation.cfgeo import apply_edits, encode_patch, rebuild, references  # noqa: E402
from src.evaluation.public_sources import image_pixel_sha256  # noqa: E402

CREAM, BLACK, BLUE = (252, 249, 236), (30, 30, 30), (0, 112, 192)


def test_patches_replace_only_their_pixels_and_rebuild_checks_both_hashes():
    source = Image.new("RGB", (40, 30), CREAM)
    rgba = np.zeros((6, 8, 4), dtype=np.uint8)
    rgba[2:4, 1:7] = (200, 0, 0, 255)
    edits = [{"box": [5, 5, 13, 11], "patch": encode_patch(Image.fromarray(rgba, "RGBA"))}]
    edited = apply_edits(source, edits)
    changed = np.argwhere(np.any(np.asarray(edited) != np.asarray(source), axis=2))
    assert sorted({tuple(x) for x in changed.tolist()}) == [(y, x) for y in (7, 8) for x in range(6, 12)]
    item = {"id": "test:1", "pixel": image_pixel_sha256(source), "k2": {"edits": edits, "pixel": image_pixel_sha256(edited)}}
    assert image_pixel_sha256(rebuild(item, source, "k2")) == item["k2"]["pixel"]
    with pytest.raises(ValueError, match="source image pixels"):
        rebuild(item, Image.new("RGB", (40, 30), "white"), "k2")
    with pytest.raises(ValueError, match="rebuilt k2"):
        rebuild(dict(item, k2=dict(item["k2"], pixel="0" * 64)), source, "k2")
    soft = rgba.copy()
    soft[2, 1, 3] = 128
    with pytest.raises(ValueError, match="alpha must be 0 or 255"):
        apply_edits(source, [{"box": [5, 5, 13, 11], "patch": encode_patch(Image.fromarray(soft, "RGBA"))}])
    with pytest.raises(ValueError, match="does not fit"):
        apply_edits(source, [{"box": [35, 25, 43, 31], "patch": edits[0]["patch"]}])


def test_references_for_exact_and_rounded_items():
    exact = {"answer": "6", "k2": {"answer": "12"}}
    rounded = {"answer": "6.9", "answer_set": ["6.9"], "k2": {"answer": "13.8", "answer_set": ["13.7", "13.8", "13.9"]}}
    assert references(exact, "original") == {"answer": "6"} and references(exact, "k2") == {"answer": "12"}
    assert references(rounded, "k2")["answer_set"] == ["13.7", "13.8", "13.9"]
    assert B.references({"answer": "6.9", "places": 1, "degree": 1}, "k2") == {
        "answer": "13.8", "answer_set": ["13.7", "13.8", "13.9"]}
    assert B.references({"answer": "56.6", "places": 1, "degree": 2}, "k1") == {"answer": "56.6", "answer_set": ["56.6"]}


def _box(text, box, number=None, suffix="", degree=False):
    return {"text": text, "box": box, "number": number if number is not None else text, "suffix": suffix,
            "degree": degree, "digit": True, "confidence": 0.99}


def test_classify_requires_every_digit_to_be_an_annotated_label():
    lengths, angles = ["12", "5"], ["30"]
    boxes = [_box("12", (0, 0, 9, 9)), _box("5 cm", (20, 0, 39, 9), "5", " cm"), _box("30°", (0, 20, 9, 29), "30", "", True),
             {"text": "x", "box": (40, 40, 45, 45), "number": None, "suffix": "", "degree": False, "digit": False}]
    length_boxes, angle_boxes = B.classify(boxes, lengths, angles)
    assert [b["text"] for b in length_boxes] == ["12", "5 cm"] and [b["text"] for b in angle_boxes] == ["30°"]
    with pytest.raises(B.Reject, match="not annotated"):
        B.classify(boxes + [_box("7", (50, 50, 55, 59))], lengths, angles)
    with pytest.raises(B.Reject, match="not a number label"):
        B.classify(boxes + [dict(_box("x+3", (50, 50, 55, 59)), number=None)], lengths, angles)
    with pytest.raises(B.Reject, match="found"):
        B.classify(boxes[1:], lengths, angles)
    with pytest.raises(B.Reject, match="both a length and an angle"):
        B.classify([_box("30", (0, 0, 9, 9))], ["30"], ["30"])


def _label_image(line_colour=BLUE, line_x=60, text="12"):
    image = Image.new("RGB", (120, 70), CREAM)
    draw = ImageDraw.Draw(image)
    font = B.font(16)
    left, top, right, bottom = font.getbbox(text)
    if line_colour is not None:
        draw.line([(line_x, 0), (line_x, 69)], fill=line_colour, width=2)
    draw.text((20, 20), text, font=font, fill=BLACK)
    return image, (20 + left - 1, 20 + top - 1, 20 + right + 1, 20 + bottom + 1)


def test_edit_replaces_the_label_keeps_nearby_lines_and_patches_reproduce_it():
    image, box = _label_image()
    label = _box("12", box)
    for factor, expected in [(1, "12"), (2, "24")]:
        edited, records, patches = B.edit(image, [label], [label], factor)
        assert records[0]["to"] == expected
        source, out = np.asarray(image), np.asarray(edited)
        assert (source[:, 58:63] == out[:, 58:63]).all()  # the blue line is untouched
        assert np.any(source[box[1]:box[3], box[0]:box[2]] != out[box[1]:box[3], box[0]:box[2]])
        assert image_pixel_sha256(apply_edits(image, patches)) == image_pixel_sha256(edited)
        for patch in patches:
            alpha = np.asarray(_decode(patch["patch"]))[..., 3]
            assert set(np.unique(alpha).tolist()) <= {0, 255}


def test_k1_redraws_the_printed_string_and_bold_labels_get_a_stroke():
    """Spot-check round 1 (reports/cfgeo_20261109/spot_check.md): "3.0" must stay "3.0" at k=1, bold digits stay bold."""
    image, box = _label_image(line_colour=None, text="3.0")
    label = _box("3.0", box)
    assert B.edit(image, [label], [label], 1)[1][0]["to"] == "3.0"
    assert B.edit(image, [label], [label], 2)[1][0]["to"] == "6"
    image, box = _label_image(line_colour=None)
    label = _box("12", box)
    plain = B.edit(image, [label], [label], 1)[1][0]["stroke"]
    bold = Image.new("RGB", (120, 70), CREAM)
    font = B.font(16)
    ImageDraw.Draw(bold).text((20, 20), "12", font=font, fill=BLACK, stroke_width=1, stroke_fill=BLACK)
    left, top, right, bottom = font.getbbox("12", stroke_width=1)
    label = _box("12", (20 + left - 1, 20 + top - 1, 20 + right + 1, 20 + bottom + 1))
    assert B.edit(bold, [label], [label], 1)[1][0]["stroke"] > plain


def _decode(text):
    from src.evaluation.cfgeo import decode_patch

    return decode_patch(text)


def test_edit_refuses_labels_it_cannot_separate():
    for colour in (BLACK, BLUE):  # a line running through the digits: label and line are one blob
        image, box = _label_image(line_colour=colour, line_x=30)
        label = _box("12", box)
        with pytest.raises(B.Reject, match="touches another stroke"):
            B.edit(image, [label], [label], 2)
    font = B.font(16)
    right = 20 + font.getbbox("8")[2]
    image, box = _label_image(line_colour=BLUE, line_x=right + 2, text="8")  # "16" is wider than "8"
    label = _box("8", box)
    B.edit(image, [label], [label], 1)  # the same digit fits
    with pytest.raises(B.Reject, match="cover other ink"):
        B.edit(image, [label], [label], 2)
    image, box = _label_image(line_colour=None, text="8")
    label, other = _box("8", box), _box("y", (box[2] + 1, box[1], box[2] + 8, box[3]), number="0")
    B.edit(image, [label], [label, other], 1)
    with pytest.raises(B.Reject, match="touch the label"):  # the wider "16" would reach the next label
        B.edit(image, [label], [label, other], 2)


def test_small_helpers():
    assert B.merge_rects([(0, 0, 5, 5), (4, 4, 8, 8), (20, 20, 22, 22)]) == [(0, 0, 8, 8), (20, 20, 22, 22)]
    mask = np.zeros((5, 5), dtype=bool)
    mask[2, 2] = True
    assert B.dilate(mask).sum() == 9
    mask[0, 0] = True
    assert sorted(len(ys) for ys, _ in B.components(mask)) == [1, 1]
    assert B.iou((0, 0, 10, 10), (5, 0, 15, 10)) == pytest.approx(1 / 3)
    assert B.canon("12.0") == "12" and B.canon("3.50") == "3.5"
