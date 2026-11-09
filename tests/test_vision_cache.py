import importlib.util

import pytest

from tests._qwen import processor_dir, tiny_model

pytestmark = pytest.mark.skipif(processor_dir() is None or importlib.util.find_spec("peft") is None,
                                reason="needs pinned Qwen2.5-VL processor files and peft")


def inputs(processor, sizes):
    from PIL import Image, ImageDraw

    from src.training.protocol_v3 import eval_messages

    images, texts = [], []
    for i, size in enumerate(sizes):
        image = Image.new("RGB", size, "white")
        ImageDraw.Draw(image).line((0, 0, size[0], size[1]), fill=(i * 60, 0, 0), width=3)
        images.append(image)
        texts.append(processor.apply_chat_template(eval_messages("Find x."), tokenize=False, add_generation_prompt=True))
    return processor(text=texts, images=images, padding=True, return_tensors="pt")


def test_cached_forward_is_identical_and_keys_never_mix_images():
    import torch
    from transformers import AutoProcessor

    from src.training.lora_language import attach_language_lora
    from src.training.vision_cache import FrozenVisionCache

    processor = AutoProcessor.from_pretrained(processor_dir())
    model, _, _ = attach_language_lora(tiny_model(), r=4, alpha=8)
    model.eval()
    batch = inputs(processor, [(56, 84), (84, 56)])
    with torch.no_grad():
        reference = model(**batch).logits
    cache = FrozenVisionCache(model)
    with torch.no_grad():
        first = model(**batch).logits
        second = model(**batch).logits
    assert torch.equal(reference, first) and torch.equal(reference, second)
    assert cache.stats()["misses"] == 2 and cache.stats()["hits"] == 2
    other = inputs(processor, [(84, 56), (56, 84)])  # same sizes, different pixels/order
    with torch.no_grad():
        swapped = model(**other).logits
    cache.remove()
    with torch.no_grad():
        uncached = model(**other).logits
    assert torch.equal(swapped, uncached)


def test_cache_refuses_a_trainable_vision_tower():
    from src.training.vision_cache import FrozenVisionCache

    model = tiny_model()
    with pytest.raises(ValueError, match="frozen"):
        FrozenVisionCache(model)
