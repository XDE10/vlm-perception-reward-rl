import importlib.util

import pytest

from src.evaluation.generate_v3 import score, summarize
from tests._fixtures import geometry_1670, release_row_1670
from tests._qwen import processor_dir, tiny_model


class FakeVerifier:
    def verify_many(self, answers, references):
        return [{"correct": a == r, "status": "equivalent" if a == r else "mismatch", "normalized_answer": a}
                for a, r in zip(answers, references)]


def test_score_and_summarize_on_real_labels():
    row = release_row_1670()
    gold = row["certified_positive_tokens"]
    refs = {"a": {"answer": "4", "gold_tokens": gold, "negative_tokens": [], "geometry": geometry_1670().to_json()},
            "b": {"answer": "4", "gold_tokens": gold, "negative_tokens": [], "geometry": geometry_1670()}}
    results = [
        {"id": "a", "text": "<perception>" + "; ".join(gold) + "</perception><think>t</think><answer>4</answer>",
         "completion_tokens": 40, "ended_eos": True, "budget_exhausted": False},
        {"id": "b", "text": "<perception>PointLiesOnLine(A,(B,C))</perception><think>t</think><answer>5</answer>",
         "completion_tokens": 1024, "ended_eos": False, "budget_exhausted": True},
    ]
    scored = score(results, refs, FakeVerifier())
    assert scored[0]["answer"]["correct"] and scored[0]["v5"]["reward"] == pytest.approx(1.0)
    assert not scored[1]["answer"]["correct"] and scored[1]["v5"]["false"] == 1
    summary = summarize(scored)
    assert summary["n"] == 2 and summary["answer_accuracy"] == 0.5 and summary["budget_exhausted_rate"] == 0.5
    assert summary["protocol_ok_rate"] == 1.0 and summary["completion_tokens_max"] == 1024


def test_answer_set_references_accept_any_member_and_nothing_else():
    """CF-Geo rounded items (S3 design 3.1): correct iff the answer matches one of the correct roundings."""
    from src.evaluation.generate_v3 import verify_answers

    refs = [{"answer": "56.6", "answer_set": ["113.1", "113.2", "113.3"]}] * 3 + [{"answer": "7"}]
    verdicts = verify_answers(["113.2", "113.25", None, "7"], refs, FakeVerifier())
    assert [v["correct"] for v in verdicts] == [True, False, False, True]
    assert verdicts[0]["normalized_answer"] == "113.2" and verdicts[1]["status"] == "mismatch"
    results = [{"id": "r", "text": "<answer>113.3</answer>", "completion_tokens": 5, "ended_eos": True,
                "budget_exhausted": False, "prompt_variant": "p1"}]
    scored = score(results, {"r": refs[0]}, FakeVerifier())
    assert scored[0]["answer"]["correct"] and scored[0]["protocol"] == "perception-think-answer-v3-p1-20261109"


@pytest.mark.skipif(processor_dir() is None or importlib.util.find_spec("transformers") is None,
                    reason="needs pinned Qwen2.5-VL processor files")
def test_batched_generation_with_and_without_images_on_tiny_model():
    from PIL import Image
    from transformers import AutoProcessor

    from src.evaluation.generate_v3 import generate

    processor = AutoProcessor.from_pretrained(processor_dir())
    side_before = processor.tokenizer.padding_side
    model = tiny_model().eval()
    images = [Image.new("RGB", (84, 56), "white"), Image.new("RGB", (56, 112), "white")]
    with_image = generate(model, processor, [{"id": i, "problem": "<image>Find x.", "image": im} for i, im in enumerate(images)],
                          max_new_tokens=6, batch_size=2)
    blind = generate(model, processor, [{"id": 9, "problem": "Find x.", "image": None}], max_new_tokens=6)
    assert [r["id"] for r in with_image] == [0, 1] and all(r["has_image"] for r in with_image)
    assert not blind[0]["has_image"] and blind[0]["completion_tokens"] <= 6
    assert with_image[0]["prompt_tokens"] > blind[0]["prompt_tokens"]  # image placeholders were expanded
    assert processor.tokenizer.padding_side == side_before  # left padding is only applied during generation
    with pytest.raises(ValueError, match="all-image or all-text"):
        generate(model, processor, [{"id": 0, "problem": "a", "image": images[0]}, {"id": 1, "problem": "b"}], 4, 2)
