"""Locate the pinned Qwen2.5-VL processor files and build a tiny random model.

The processor files (tokenizer, chat template, preprocessor config; no weights)
come from ``P3_QWEN_PROCESSOR_DIR`` or the local Hugging Face cache for the
pinned revision. Tests that need them are skipped when they are absent.
"""
import os
from pathlib import Path

REPO = "Qwen/Qwen2.5-VL-3B-Instruct"
REVISION = "66285546d2b821cf421d4f5eb2576359d3770cd3"


def processor_dir():
    explicit = os.environ.get("P3_QWEN_PROCESSOR_DIR")
    candidates = [Path(explicit)] if explicit else []
    hf_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache/huggingface"))
    candidates.append(hf_home / "hub" / ("models--" + REPO.replace("/", "--")) / "snapshots" / REVISION)
    for path in candidates:
        if (path / "preprocessor_config.json").is_file() and (path / "tokenizer.json").is_file():
            return path
    return None


def tiny_model(seed=0):
    """Random Qwen2.5-VL with the real architecture/module names but tiny sizes."""
    import torch
    from transformers import Qwen2_5_VLConfig, Qwen2_5_VLForConditionalGeneration

    config = Qwen2_5_VLConfig.from_pretrained(processor_dir())
    text, vision = config.text_config, config.vision_config
    text.hidden_size, text.intermediate_size = 64, 128
    text.num_hidden_layers, text.num_attention_heads, text.num_key_value_heads = 2, 4, 2
    if getattr(text, "layer_types", None):
        text.layer_types = text.layer_types[:2]
    rope = dict(text.rope_parameters)
    rope["mrope_section"] = [2, 3, 3]  # sums to head_dim / 2 = (64 / 4) / 2
    text.rope_parameters = rope
    vision.depth, vision.hidden_size, vision.intermediate_size, vision.num_heads = 2, 32, 64, 2
    vision.out_hidden_size, vision.fullatt_block_indexes = 64, [1]
    torch.manual_seed(seed)
    return Qwen2_5_VLForConditionalGeneration(config)
