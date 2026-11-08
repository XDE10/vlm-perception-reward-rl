import importlib.util

import pytest

from tests._qwen import processor_dir, tiny_model

pytestmark = pytest.mark.skipif(
    processor_dir() is None or importlib.util.find_spec("peft") is None,
    reason="needs pinned Qwen2.5-VL processor files and peft",
)


def test_suffix_only_targets_would_hit_the_vit():
    model = tiny_model()
    names = [n for n, _ in model.named_modules()]
    assert any(n.startswith("model.visual.blocks.") and n.endswith(".mlp.gate_proj") for n in names)


def test_language_lora_targets_exclude_every_vision_module():
    from src.training.lora_language import language_lora_targets

    targets = language_lora_targets(tiny_model())
    assert targets and all("visual" not in t and t.startswith("model.language_model.layers.") for t in targets)
    assert len(targets) == 2 * 7  # two tiny decoder layers x seven projections


def test_attach_language_lora_freezes_vision_and_trains_only_lora():
    from src.training.lora_language import attach_language_lora

    model, targets, identity = attach_language_lora(tiny_model(), r=4, alpha=8)
    assert identity["vision_frozen"] and identity["vision_tensors"] > 0
    assert all("lora_" in n and "visual" not in n for n in identity["trainable_names"])
    trainable = {n for n, p in model.named_parameters() if p.requires_grad}
    assert trainable == set(identity["trainable_names"])


def test_parameter_identity_rejects_trainable_vision_or_non_lora():
    from src.training.lora_language import attach_language_lora, parameter_identity

    model, _, _ = attach_language_lora(tiny_model(), r=4, alpha=8)
    vision_param = next(p for n, p in model.named_parameters() if "visual" in n)
    vision_param.requires_grad_(True)
    with pytest.raises(ValueError, match="Vision"):
        parameter_identity(model)
    vision_param.requires_grad_(False)
    next(p for n, p in model.named_parameters() if "embed_tokens" in n).requires_grad_(True)
    with pytest.raises(ValueError, match="Non-LoRA"):
        parameter_identity(model)
