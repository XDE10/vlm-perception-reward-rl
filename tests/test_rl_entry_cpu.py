"""End-to-end CPU smoke of the unified GRPO entry on a tiny random Qwen2.5-VL.

Exercises the real path (release gates, TRL multimodal rollout, three reward
heads, rollout logging, identity files, language-only LoRA, adapter export).
The tiny model's text is random; an extra random reward forces non-zero
advantages so a real optimizer step happens.
"""
import importlib.util
import json
import random

import pytest

from tests._mini_release import make_release, mini_config
from tests._qwen import processor_dir, tiny_model

NEEDED = ["trl", "peft", "datasets", "math_verify"]
pytestmark = pytest.mark.skipif(processor_dir() is None or any(importlib.util.find_spec(m) is None for m in NEEDED),
                                reason="needs pinned Qwen2.5-VL processor files and trl/peft/datasets/math_verify")
SMOKE = {"max_steps": 2, "num_generations": 2, "prompts_per_step": 2, "per_device_train_batch_size": 2,
         "max_completion_length": 8, "save_steps": 1}


def noisy_reward(completions, **kwargs):
    rng = random.Random(len(completions) + sum(len(str(c)) for c in completions))
    return [rng.random() for _ in completions]


@pytest.mark.parametrize("arm", ["rl_v5", "rl_blind"])
def test_unified_entry_runs_two_grpo_steps_on_cpu(tmp_path, arm):
    import torch
    from transformers import AutoProcessor

    from src.training.rl_entry import run

    make_release(tmp_path)
    config = mini_config(tmp_path, arm, smoke=SMOKE)
    # Test-only: 8-token random completions are all truncated, so keep them in the loss and skip warmup
    # to guarantee a non-zero update on the tiny model. Real runs use the registered config unchanged.
    config["train"].update(mask_truncated_completions=False, warmup_steps=0, learning_rate=1e-3)
    model = tiny_model()
    vision_before = {n: p.detach().clone() for n, p in model.named_parameters() if "visual" in n}
    processor = AutoProcessor.from_pretrained(processor_dir())
    summary = run(config, tmp_path, model=model, processor=processor, extra_reward_funcs=[noisy_reward])
    out = tmp_path / "runs" / config["run_name"]
    assert summary["global_step"] == 2
    records = [json.loads(x) for x in (out / "rollouts.jsonl").read_text().splitlines()]
    assert len(records) == 2 * 2 * 2  # steps x prompts x generations
    assert {r["arm"] for r in records} == {arm}
    identity = json.loads((out / "run_identity.json").read_text())
    assert identity["config"]["smoke"]["max_steps"] == 2 and identity["parameters"]["vision_frozen"]
    assert identity["prompt_report"]["max_tokens"] <= config["train"]["max_prompt_tokens"]
    assert (out / "checkpoint-1" / "run_identity.json").is_file()
    assert (out / "final" / "adapter_config.json").is_file()
    for name, before in vision_before.items():
        assert torch.equal(dict(model.named_parameters())[name].detach(), before), name
    lora = [p for n, p in model.named_parameters() if "lora_B" in n]
    assert lora and any(p.detach().abs().sum() > 0 for p in lora)  # LoRA B starts at zero, so a step moved it


def test_resume_requires_identical_identity_and_continues(tmp_path):
    import copy

    from transformers import AutoProcessor

    from src.training.rl_entry import run

    make_release(tmp_path)
    config = mini_config(tmp_path, "rl_v5", smoke=SMOKE)
    config["train"].update(mask_truncated_completions=False, warmup_steps=0, learning_rate=1e-3)
    processor = AutoProcessor.from_pretrained(processor_dir())
    run(copy.deepcopy(config), tmp_path, model=tiny_model(), processor=processor, extra_reward_funcs=[noisy_reward])
    out = tmp_path / "runs" / config["run_name"]
    with pytest.raises(ValueError, match="already has checkpoints"):
        run(copy.deepcopy(config), tmp_path, model=tiny_model(), processor=processor)
    resumed = run(copy.deepcopy(config), tmp_path, model=tiny_model(), processor=processor,
                  resume=str(out / "checkpoint-1"), extra_reward_funcs=[noisy_reward])
    assert resumed["global_step"] == 2
    changed = copy.deepcopy(config)
    changed["train"]["learning_rate"] = 5e-4
    with pytest.raises(ValueError, match="identity mismatch"):
        run(changed, tmp_path, model=tiny_model(), processor=processor, resume=str(out / "checkpoint-1"))


def test_gradient_checkpointing_path_and_runtime_micro_batch(tmp_path):
    """GPU runs use gradient checkpointing + PEFT; exercise that TRL path on CPU with a runtime micro-batch split."""
    from transformers import AutoProcessor

    from src.training.rl_entry import run

    make_release(tmp_path)
    # 2 prompts x 4 generations = 8 completions per step; base micro-batch 8, runtime re-splits into 4 x 2
    smoke = {"max_steps": 2, "num_generations": 4, "prompts_per_step": 2, "max_completion_length": 8, "save_steps": 1}
    config = mini_config(tmp_path, "rl_v5", smoke=smoke)
    config["train"].update(mask_truncated_completions=False, warmup_steps=0, learning_rate=1e-3)
    runtime = {"generation_backend": "hf", "gradient_checkpointing": True, "per_device_train_batch_size": 2,
               "vllm_gpu_memory_utilization": 0.3, "vllm_max_model_length": 4096, "vision_cache": False,
               "source": "test"}
    model = tiny_model()
    summary = run(config, tmp_path, runtime=runtime, model=model,
                  processor=AutoProcessor.from_pretrained(processor_dir()), extra_reward_funcs=[noisy_reward])
    out = tmp_path / "runs" / config["run_name"]
    identity = json.loads((out / "run_identity.json").read_text())
    assert summary["global_step"] == 2
    assert identity["config"]["train"]["per_device_train_batch_size"] == 2
    assert identity["config"]["train"]["gradient_accumulation_steps"] == 4  # 8 completions / micro-batch 2
    assert identity["runtime"]["gradient_checkpointing"] is True
    lora = [p for n, p in model.named_parameters() if "lora_B" in n]
    assert any(p.detach().abs().sum() > 0 for p in lora)


def test_runtime_keys_that_could_change_the_algorithm_are_rejected(tmp_path):
    from src.training.rl_entry import apply_runtime, run

    make_release(tmp_path)
    config = mini_config(tmp_path, "rl_v5", smoke=SMOKE)
    with pytest.raises(ValueError, match="could change the algorithm"):
        run(config, tmp_path, runtime={"generation_backend": "hf", "learning_rate": 1.0}, model=object(),
            processor=object())
    base = mini_config(tmp_path, "rl_v5", smoke={"max_steps": 1})
    with pytest.raises(ValueError, match="does not divide"):
        apply_runtime(base, {"per_device_train_batch_size": 7})
    applied = apply_runtime(base, {"per_device_train_batch_size": 4})
    assert applied["train"]["gradient_accumulation_steps"] == 16 and applied["train"]["generation_batch_size"] == 64
