"""The evaluation harness (src/evaluation/harness.py) on synthetic items.

The first test replaces generation with canned outputs and checks grading per condition; the others run the real
code path on the tiny random Qwen2.5-VL (skipped without the pinned processor files)."""
import importlib.util
import io

import pytest

pytest.importorskip("PIL")
pytest.importorskip("pyarrow")
pytest.importorskip("math_verify")

from PIL import Image, ImageDraw  # noqa: E402

from src.evaluation import harness  # noqa: E402
from src.evaluation.public_sources import image_pixel_sha256  # noqa: E402
from tests._mini_release import make_release, mini_config  # noqa: E402
from tests._qwen import processor_dir, tiny_model  # noqa: E402

HAS_MODEL = processor_dir() is not None and all(importlib.util.find_spec(m) for m in ["transformers", "peft", "trl"])
GOOD = "<perception>Length(A,B)=3</perception><think>t</think><answer>%s</answer>"


class FakeVerifier:
    def verify_many(self, answers, references):
        return [{"correct": a is not None and a == r, "status": "equivalent" if a == r else "mismatch",
                 "normalized_answer": a} for a, r in zip(answers, references)]


def _diagram(text, n):
    from scripts.data import build_cfgeo as B

    image = Image.new("RGB", (120, 70), (252, 249, 236))
    draw = ImageDraw.Draw(image)
    draw.line([(90, 0), (90 + 3 * n, 69)], fill=(0, 112, 192), width=2)  # a different picture for every item
    font = B.font(16)
    draw.text((20, 20), text, font=font, fill=(30, 30, 30))
    left, top, right, bottom = font.getbbox(text)
    return image, (20 + left - 1, 20 + top - 1, 20 + right + 1, 20 + bottom + 1)


def _write_wrapper(root, split, rows):
    import pyarrow as pa
    import pyarrow.parquet as pq

    path = root / "geometry3k/data" / ("%s-00000-of-00001.parquet" % split)
    path.parent.mkdir(parents=True, exist_ok=True)
    images = []
    for _, _, image in rows:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        images.append([{"bytes": buffer.getvalue(), "path": None}])
    pq.write_table(pa.table({"images": images, "problem": [r[0] for r in rows], "answer": [r[1] for r in rows]}), path)


def cf_world(tmp_path):
    """Three wrapper rows with one length label each, and a CF-Geo specification made by the real editor."""
    from scripts.data import build_cfgeo as B

    rows, items = [], []
    for n, (text, answer, places) in enumerate([("12", "6", None), ("8", "4.6", 1), ("10", "5", None)]):
        image, box = _diagram(text, n)
        rows.append(("<image>Find x.", answer, image))
        label = {"text": text, "box": box, "number": text, "suffix": "", "degree": False, "digit": True}
        record = {"id": "test:%d" % n, "pixel": image_pixel_sha256(image), "original_id": str(100 + n), "answer": answer,
                  "degree": 1, "places": places, "lengths": [text], "angles": []}
        if places:
            record["answer_set"] = [answer]
        for name, factor in (("k1", 1), ("k2", 2)):
            edited, labels, patches = B.edit(image, [label], [label], factor)
            record[name] = {"pixel": image_pixel_sha256(edited), "edits": patches, "labels": labels,
                            **B.references(record, name)}
        items.append(record)
    _write_wrapper(tmp_path / "sources", "test", rows)
    return {"schema": "p3-cfgeo-v1", "items": items}


def test_conditions_grading_and_summary_with_canned_outputs(tmp_path, monkeypatch):
    items = harness.cfgeo_items(cf_world(tmp_path), tmp_path / "sources")
    assert [i["id"] for i in items] == ["test:0", "test:1", "test:2"]
    assert items[1]["cf"]["k2"]["answer_set"] == ["9.1", "9.2", "9.3"] and items[0]["cf"]["k2"]["answer"] == "12"
    items[0]["gold_tokens"] = ["Length(A,B)=3", "Length(B,C)=4"]
    answers = {"original|test:0": "6", "original|test:1": "4.6", "original|test:2": "7",
               "cf_k2|test:0": "12", "cf_k2|test:1": "4.6", "cf_k2|test:2": "10",
               "cf_k1|test:0": "6", "cf_k1|test:1": "4.6", "cf_k1|test:2": "5"}
    seen = []

    def canned(model, processor, requests, max_new_tokens=1024, batch_size=16, progress=None, prompt_variant="p0", **_):
        seen.append(([r["id"] for r in requests], [r["image"] is not None for r in requests], batch_size, prompt_variant))
        return [{"id": r["id"], "text": GOOD % answers.get(r["id"], "0"), "has_image": r["image"] is not None,
                 "prompt_variant": prompt_variant, "prompt_tokens": 1, "completion_tokens": 3, "ended_eos": True,
                 "budget_exhausted": False, "batch_seconds": 0.0} for r in requests]

    monkeypatch.setattr("src.evaluation.generate_v3.generate", canned)
    run = lambda condition, **kw: harness.run_condition(None, None, items, condition, FakeVerifier(), **kw)  # noqa: E731
    original = run("original", prompt_variant="p1")
    assert [r["answer"]["correct"] for r in original] == [True, True, False]
    assert seen[-1][2] == harness.BATCH_SIZE and seen[-1][3] == "p1" and all(seen[-1][1])
    assert original[0]["v5"]["tp"] == 1 and original[0]["gold_count"] == 2 and original[1]["v5"] is None
    summary = harness.summarize(original)
    assert summary["accuracy"] == pytest.approx(2 / 3) and summary["e1"]["recall"] == 0.5
    assert summary["e1"]["verified_precision"] == 1.0 and summary["clusters"] == 3
    k2 = run("cf_k2")
    assert [r["answer"]["correct"] for r in k2] == [True, False, True]
    assert [r["old_answer"] for r in k2] == [False, True, False]  # 4.6 is the answer of the unedited diagram
    assert harness.summarize(k2)["old_answer_rate"] == pytest.approx(1 / 3) and k2[0]["v5"] is None
    assert [r["answer"]["correct"] for r in run("cf_k1")] == [True, True, True]
    blind = run("blind")
    assert not any(seen[-1][1]) and [r["item"] for r in blind] == ["test:0", "test:1", "test:2"]
    swap = run("swap", swap={"test:0": "test:1", "test:1": "test:2", "test:2": "test:0"})
    assert [r["shown_image_of"] for r in swap] == ["test:1", "test:2", "test:0"]
    with pytest.raises(ValueError, match="must differ"):
        run("swap", swap={"test:0": "test:0", "test:1": "test:2", "test:2": "test:1"})
    with pytest.raises(ValueError, match="no swap partner"):
        run("swap", swap={"test:0": "test:1"})
    with pytest.raises(ValueError, match="unknown condition"):
        run("rotated")


def test_release_items_check_images(tmp_path):
    make_release(tmp_path, evaluation=2)
    config = mini_config(tmp_path)
    val = harness.val82_items(tmp_path, config)
    assert [i["id"] for i in val] == ["validation:0", "validation:1"] and val[0]["gold_tokens"] == ["Length(A,B)=3"]
    train = harness.train_items(tmp_path, config, n=3)
    assert [i["id"] for i in train] == ["train:0", "train:1", "train:2"] and train[0]["geometry"] is not None
    image = tmp_path / "data/images/9500.png"
    image.write_bytes(image.read_bytes() + b"\0")
    with pytest.raises(ValueError, match="image bytes changed"):
        harness.val82_items(tmp_path, config)


@pytest.mark.skipif(not HAS_MODEL, reason="needs pinned processor files, transformers, peft, trl")
def test_every_condition_runs_on_the_tiny_model(tmp_path):
    from transformers import AutoProcessor

    from src.evaluation.stats import align, paired_ratio, per_item
    from src.rewards.answer import AnswerVerifier

    items = harness.cfgeo_items(cf_world(tmp_path), tmp_path / "sources")
    model, processor = tiny_model().eval(), AutoProcessor.from_pretrained(processor_dir())
    verifier = AnswerVerifier(workers=1, timeout=60)
    records = {}
    try:
        for condition in harness.CONDITIONS:
            records[condition] = harness.run_condition(
                model, processor, items, condition, verifier, max_new_tokens=4, batch_size=2,
                swap={"test:0": "test:1", "test:1": "test:2", "test:2": "test:0"}, model_name="tiny")
    finally:
        verifier.close()
    for condition, rows in records.items():
        assert [r["item"] for r in rows] == ["test:0", "test:1", "test:2"]
        assert all(r["condition"] == condition and r["model"] == "tiny" and r["completion_tokens"] <= 4 for r in rows)
        assert harness.summarize(rows)["n"] == 3
    assert not any(r["has_image"] for r in records["blind"]) and all(r["has_image"] for r in records["cf_k2"])
    a = per_item(records["original"], lambda r: r["answer"]["correct"])
    b = per_item(records["blind"], lambda r: r["answer"]["correct"])
    result = paired_ratio(*align(a, b), resamples=200)
    assert result["items"] == 3 and result["clusters"] == 3
    harness.write_jsonl(tmp_path / "out/predictions.jsonl", records["cf_k2"])
    assert (tmp_path / "out/predictions.jsonl").read_text(encoding="utf-8").count("\n") == 3


@pytest.mark.skipif(not HAS_MODEL, reason="needs pinned processor files, transformers, peft, trl")
def test_load_model_with_a_saved_lora_adapter(tmp_path):
    """S5 evaluates trained runs from <run>/final (a LoRA adapter): load it on CPU and generate."""
    from transformers import AutoProcessor

    from src.evaluation.generate_v3 import generate
    from src.training.lora_language import attach_language_lora

    base = tmp_path / "base"
    tiny_model().save_pretrained(base)
    AutoProcessor.from_pretrained(processor_dir()).save_pretrained(base)
    import torch
    from peft import PeftModel

    peft_model, _, _ = attach_language_lora(tiny_model(), 4, 8, 0.0)
    torch.manual_seed(1)
    trained = {}
    for name, param in peft_model.named_parameters():
        if "lora_B" in name:  # lora_B starts at zero: give it values so loading is actually checked
            param.data.normal_()
            trained[name] = param.detach().clone()
    peft_model.save_pretrained(tmp_path / "adapter")
    make_release(tmp_path / "release")
    config = mini_config(tmp_path / "release")
    model, processor = harness.load_model(base, config, adapter=tmp_path / "adapter", device="cpu")
    assert isinstance(model, PeftModel) and not model.training
    loaded = dict(model.named_parameters())
    assert trained and all(torch.equal(loaded[name], value) for name, value in trained.items())
    out = generate(model, processor, [{"id": "a", "problem": "Find x.", "image": Image.new("RGB", (56, 56), "white")}],
                   max_new_tokens=2)
    assert out[0]["completion_tokens"] <= 2
