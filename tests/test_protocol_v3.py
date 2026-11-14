import re

import pytest

from src.rewards.claims import parse_claim
from src.training.protocol_v3 import (SYSTEM_PROMPT, eval_messages, extract_answer, format_reward, parse_completion,
                                      training_prompt)
from tests._qwen import processor_dir

GOOD = "<perception>Length(A,C)=1; PointLiesOnLine(C,(A,D))</perception>\n<think>similar triangles</think>\n<answer>4</answer>"


def test_prompt_examples_follow_the_claim_schema():
    examples = re.search(r"syntax: (.*?)\.\n", SYSTEM_PROMPT).group(1).split("; ")
    assert len(examples) == 7
    assert all(parse_claim(x).valid for x in examples), examples


def test_parse_and_format_reward():
    parsed = parse_completion(GOOD)
    assert parsed["protocol_ok"] and parsed["answer"] == "4"
    assert format_reward(GOOD) == 1.0
    assert format_reward("<perception></perception><think>t</think><answer>4</answer>") == 0.0  # needs one valid fact
    assert format_reward("<perception>junk</perception><think>t</think><answer>4</answer>") == 0.0
    assert format_reward("<think>t</think><answer>4</answer>") == 0.0
    assert format_reward(GOOD + " trailing") == 0.0
    assert format_reward("<perception>Length(A,C)=1</perception><think><answer>3</answer></think><answer>4</answer>") == 0.0
    over = "; ".join(f"Length(A,B)={i}" for i in range(1, 26))
    assert format_reward(f"<perception>{over}</perception><think>t</think><answer>4</answer>") == 0.0


def test_answer_extraction_is_independent_of_perception_format():
    assert extract_answer("<perception>broken</perception> <answer> 4 </answer>") == ("4", "ok")
    assert extract_answer("no tags")[1] == "no_answer_block"
    assert extract_answer("<answer>1</answer><answer>2</answer>")[1] == "multiple_answer_blocks"
    assert extract_answer("<answer> </answer>")[1] == "empty_answer"


def test_problem_cleaning_and_message_shapes():
    assert training_prompt("<image>Find x.")[1] == {"role": "user", "content": "Find x."}
    blind = eval_messages("<image>Find x.", with_image=False)
    assert blind[1]["content"] == [{"type": "text", "text": "Find x."}]


def test_prompt_variants_are_the_pre_registered_text():
    """S3 design section 6 fixes the P1 sentence verbatim; the code must use exactly that sentence."""
    from pathlib import Path

    from src.training.protocol_v3 import (ANSWER_ONLY_SYSTEM_PROMPT, P1_SUFFIX, PROTOCOL, protocol_id, system_prompt,
                                          user_text)

    design = (Path(__file__).resolve().parents[1] / "docs/plan/S3设计_20261109.md").read_text(encoding="utf-8")
    assert P1_SUFFIX == "Respond in the format <perception>...</perception><think>...</think><answer>...</answer>."
    assert "`%s`" % P1_SUFFIX in design
    assert user_text("<image>Find x.", "p1") == "Find x.\n\n" + P1_SUFFIX
    assert user_text("<image>Find x.", "p0") == "Find x." == user_text("Find x.", "answer_only")
    assert system_prompt("p1") == system_prompt("p0") == SYSTEM_PROMPT
    assert system_prompt("answer_only") == ANSWER_ONLY_SYSTEM_PROMPT and "<perception>" not in ANSWER_ONLY_SYSTEM_PROMPT
    assert protocol_id("p0") == PROTOCOL and len({protocol_id(v) for v in ("p0", "p1", "answer_only")}) == 3
    assert training_prompt("Find x.", "p1")[1]["content"].endswith(P1_SUFFIX)
    assert eval_messages("Find x.", True, "p1")[1]["content"][-1]["text"].endswith(P1_SUFFIX)
    with pytest.raises(ValueError, match="diagnostic"):
        training_prompt("Find x.", "answer_only")
    with pytest.raises(ValueError, match="unknown prompt variant"):
        eval_messages("Find x.", True, "p2")


def test_protocol_ids_map_back_to_their_prompt_variant():
    from src.training.protocol_v3 import PROMPT_VARIANTS, TRAINING_VARIANTS, protocol_id, variant_for_protocol

    assert all(variant_for_protocol(protocol_id(v)) == v for v in PROMPT_VARIANTS)
    assert set(TRAINING_VARIANTS) == set(PROMPT_VARIANTS) - {"answer_only"}
    with pytest.raises(ValueError, match="unknown protocol id"):
        variant_for_protocol("perception-think-answer-v3-p2")


@pytest.mark.skipif(processor_dir() is None, reason="pinned Qwen2.5-VL processor files not available")
def test_training_and_eval_prompts_render_identically_through_trl():
    from PIL import Image
    from transformers import AutoProcessor
    from trl.data_utils import prepare_multimodal_messages

    processor = AutoProcessor.from_pretrained(processor_dir())
    image = Image.new("RGB", (64, 64), "white")
    via_trl = prepare_multimodal_messages(training_prompt("<image>Find x."), images=[image])
    ours = eval_messages("<image>Find x.", with_image=True)
    render = lambda m: processor.apply_chat_template(m, tokenize=False, add_generation_prompt=True)  # noqa: E731
    assert render(via_trl) == render(ours)
    # the P1 variant, if S3 adopts it, must also be identical between training and evaluation
    p1_trl = prepare_multimodal_messages(training_prompt("<image>Find x.", "p1"), images=[image])
    assert render(p1_trl) == render(eval_messages("<image>Find x.", True, "p1")) != render(ours)
    text_only = processor.apply_chat_template(eval_messages("Find x.", with_image=False), tokenize=False,
                                              add_generation_prompt=True)
    assert "<|image_pad|>" not in text_only and "<|image_pad|>" in render(ours)
