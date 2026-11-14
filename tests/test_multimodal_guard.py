"""Unit checks of the scoring-pass alignment guard (D33)."""
import pytest

from tests._qwen import processor_dir, tiny_model

pytestmark = pytest.mark.skipif(processor_dir() is None, reason="needs pinned Qwen2.5-VL processor files")


def _batch(image_id, pad, prompt=6, image=(2, 3), completion=3):
    import torch

    """Left-padded batch: the row with pad p has a prompt p tokens shorter than the longest one."""
    ids, mask = [], []
    width = max(pad) + prompt + completion
    for row_pad in pad:
        row = [0] * row_pad + [7] * (width - completion - row_pad) + [9] * completion
        start = row_pad + image[0]
        for i in range(start, start + image[1]):
            row[i] = image_id
        ids.append(row)
        mask.append([0] * row_pad + [1] * (width - row_pad))
    ids = torch.tensor(ids)
    types = (ids == image_id).long()
    return ids, types, torch.tensor(mask)


def test_guard_accepts_aligned_types_and_counts_left_padding():
    from src.training.multimodal_guard import MultimodalAlignmentGuard

    model = tiny_model()
    guard = MultimodalAlignmentGuard(model)
    ids, types, mask = _batch(guard.image_id, pad=[0, 2])
    guard._check(None, (), {"input_ids": ids, "mm_token_type_ids": types, "attention_mask": mask})
    guard._check(None, (), {"input_ids": ids[:, -1:], "mm_token_type_ids": types})  # cached decoding: shapes differ
    assert guard.stats()["checked_forwards"] == 1 and guard.stats()["left_padded_rows"] == 1
    assert guard.stats()["max_left_padding"] == 2
    guard.remove()


def test_guard_rejects_types_padded_on_the_other_side():
    import torch

    from src.training.multimodal_guard import MultimodalAlignmentGuard

    guard = MultimodalAlignmentGuard(tiny_model())
    ids, types, mask = _batch(guard.image_id, pad=[0, 2])
    shifted = types.clone()
    shifted[1] = torch.roll(types[1], -2)  # what a right-padding processor produced for the padded row
    with pytest.raises(RuntimeError, match=r"row 1: first image token at column 4 in input_ids, 2 in"):
        guard._check(None, (), {"input_ids": ids, "mm_token_type_ids": shifted, "attention_mask": mask})
    guard.remove()


def test_guard_is_called_by_the_model_forward():
    from src.training.multimodal_guard import MultimodalAlignmentGuard

    model = tiny_model()
    guard = MultimodalAlignmentGuard(model)
    ids, types, mask = _batch(guard.image_id, pad=[0])
    with pytest.raises(RuntimeError, match="mm_token_type_ids disagree"):
        model(input_ids=ids, attention_mask=mask, mm_token_type_ids=types * 0)  # no pixels needed: fails first
    guard.remove()


def test_left_pad_processor_matches_what_trl_sets_itself():
    from transformers import AutoProcessor

    from src.training.multimodal_guard import left_pad_processor

    processor = AutoProcessor.from_pretrained(processor_dir())
    assert processor.tokenizer.padding_side == "right"
    left_pad_processor(processor)
    assert (processor.tokenizer.padding_side, processor.tokenizer.truncation_side) == ("left", "left")
