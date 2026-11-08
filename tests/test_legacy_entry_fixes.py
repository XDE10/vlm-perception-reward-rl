"""Regression tests for the 2026-11-09 fixes to the legacy entry (src/training/approved_hf.py)."""
import importlib.util
import re
from pathlib import Path

import pytest

from tests._qwen import processor_dir, tiny_model

ROOT = Path(__file__).resolve().parents[1]


def test_legacy_sources_no_longer_use_suffix_only_lora_or_removed_auto_class():
    source = (ROOT / "src/training/approved_hf.py").read_text(encoding="utf-8")
    assert "target_modules=['q_proj'" not in source
    assert "target_modules=language_lora_targets(model)" in source
    assert "parameter_identity(trainer.model)" in source
    for path in ["src/training/approved_hf.py", "scripts/training/diagnose_project3_vision.py"]:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert not re.search(r"\bAutoModelForVision2Seq\b", text), path


def test_vision_model_class_resolves_on_installed_transformers():
    pytest.importorskip("transformers")
    from src.training.hf_compat import vision_model_class

    assert vision_model_class().__name__ in {"AutoModelForImageTextToText", "AutoModelForVision2Seq"}


@pytest.mark.skipif(processor_dir() is None or importlib.util.find_spec("peft") is None,
                    reason="needs pinned Qwen2.5-VL processor files and peft")
def test_legacy_lora_config_on_real_module_tree_keeps_vit_frozen():
    from peft import LoraConfig, get_peft_model

    from src.training.lora_language import language_lora_targets, parameter_identity

    model = tiny_model()
    legacy_suffix = LoraConfig(r=4, lora_alpha=8, target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj",
                                                                  "up_proj", "down_proj"], task_type="CAUSAL_LM")
    leaked = get_peft_model(tiny_model(), legacy_suffix)
    assert any("visual" in n and p.requires_grad for n, p in leaked.named_parameters())  # the original bug
    fixed = get_peft_model(model, LoraConfig(r=4, lora_alpha=8, target_modules=language_lora_targets(model),
                                             task_type="CAUSAL_LM"))
    assert parameter_identity(fixed)["vision_frozen"]
