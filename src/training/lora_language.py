"""Language-only LoRA with fail-closed checks that the vision tower stays frozen.

Qwen2.5-VL's vision blocks use MLP layers named ``gate_proj``/``up_proj``/
``down_proj`` (``model.visual.blocks.N.mlp.*``), so a suffix-only LoRA target
list silently trains part of the ViT. Targets are therefore resolved to exact
module names outside every vision/merger path, and the resulting parameter set
is checked: no vision or merger tensor may require grad, and every trainable
tensor must be a LoRA tensor.
"""
import hashlib
import json

LANGUAGE_SUFFIXES = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
VISION_MARKERS = ("visual", "vision", "merger", "multi_modal_projector", "mm_projector")


def is_vision_name(name):
    lowered = name.lower()
    return any(marker in lowered for marker in VISION_MARKERS)


def language_lora_targets(model):
    import torch

    names = [
        name for name, module in model.named_modules()
        if isinstance(module, torch.nn.Linear) and name.rsplit(".", 1)[-1] in LANGUAGE_SUFFIXES
        and not is_vision_name(name)
    ]
    if not names:
        raise ValueError("No language LoRA targets found; explicit architecture mapping required")
    return names


def parameter_identity(model, require_vision=True):
    rows = [{"name": n, "numel": p.numel(), "requires_grad": bool(p.requires_grad)} for n, p in model.named_parameters()]
    vision = [r for r in rows if is_vision_name(r["name"])]
    if require_vision and not vision:
        raise ValueError("Cannot locate vision parameters; refusing to claim the vision tower is frozen")
    trainable_vision = [r["name"] for r in vision if r["requires_grad"]]
    if trainable_vision:
        raise ValueError("Vision/merger parameters are trainable: " + ", ".join(trainable_vision[:5]))
    trainable = [r for r in rows if r["requires_grad"]]
    if not trainable:
        raise ValueError("No trainable parameters")
    non_lora = [r["name"] for r in trainable if "lora_" not in r["name"]]
    if non_lora:
        raise ValueError("Non-LoRA parameters are trainable: " + ", ".join(non_lora[:5]))
    return {
        "trainable_tensors": len(trainable),
        "trainable_parameters": sum(r["numel"] for r in trainable),
        "total_parameters": sum(r["numel"] for r in rows),
        "vision_tensors": len(vision),
        "vision_parameters": sum(r["numel"] for r in vision),
        "vision_frozen": True,
        "trainable_names_sha256": hashlib.sha256(json.dumps([r["name"] for r in trainable]).encode()).hexdigest(),
        "trainable_names": [r["name"] for r in trainable],
    }


def lora_config(model, r=16, alpha=32, dropout=0.0):
    from peft import LoraConfig

    return LoraConfig(r=r, lora_alpha=alpha, lora_dropout=dropout, target_modules=language_lora_targets(model),
                      task_type="CAUSAL_LM")


def attach_language_lora(model, r=16, alpha=32, dropout=0.0):
    from peft import get_peft_model

    for param in model.parameters():
        param.requires_grad_(False)
    config = lora_config(model, r, alpha, dropout)
    peft_model = get_peft_model(model, config)
    return peft_model, list(config.target_modules), parameter_identity(peft_model)


__all__ = ["LANGUAGE_SUFFIXES", "VISION_MARKERS", "attach_language_lora", "is_vision_name", "language_lora_targets",
           "lora_config", "parameter_identity"]
