#!/usr/bin/env python3
"""Validate the G4 probe/step/full configs against Shuffle-R1's structured config."""
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path

from omegaconf import OmegaConf

from shuffle_r1.config import PPOConfig
from shuffle_r1.single_gpu import derive_batch_geometry

ROOT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/shuffle-r1-g4-dev")
REPORT = Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
CONFIGS = [
    "examples/qwen2_5_vl_3b_g4_b16_probe.yaml",
    "examples/qwen2_5_vl_3b_g4_b512_step.yaml",
    "examples/qwen2_5_vl_3b_g4_full_20ep.yaml",
]


def serializable(value):
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "__dict__"):
        return vars(value)
    if isinstance(value, dict):
        return value
    return str(value)


def main():
    results = []
    base = OmegaConf.structured(PPOConfig)
    for relative in CONFIGS:
        path = ROOT / relative
        config = OmegaConf.merge(base, OmegaConf.load(path))
        obj = OmegaConf.to_object(config)
        obj.deep_post_init()
        obj.validate_execution()
        geometry = derive_batch_geometry(
            obj.data.rollout_batch_size,
            obj.worker.actor.global_batch_size,
            samples_per_prompt=obj.worker.rollout.n,
            pruning_ratio=obj.worker.actor.purning_ratio,
            world_size=obj.trainer.reference_data_parallel_size,
            micro_batch_size=obj.worker.actor.micro_batch_size_per_device_for_update,
            replay_times=obj.trainer.replay_times,
        )
        rows = {
            "config": relative,
            "validated": True,
            "model": obj.worker.actor.model.model_path,
            "model_revision": obj.worker.actor.model.revision,
            "train_files": obj.data.train_files,
            "val_files": obj.data.val_files,
            "rollout_batch_size": obj.data.rollout_batch_size,
            "actor_global_batch_size": obj.worker.actor.global_batch_size,
            "rollout_n": obj.worker.rollout.n,
            "purning_ratio": obj.worker.actor.purning_ratio,
            "reference_data_parallel_size": obj.trainer.reference_data_parallel_size,
            "reference_micro_batch_size": obj.trainer.reference_micro_batch_size,
            "physical_update_micro_batch_size": obj.worker.actor.micro_batch_size_per_device_for_update,
            "physical_experience_micro_batch_size": obj.worker.actor.micro_batch_size_per_device_for_experience,
            "rollout_chunk_prompts": obj.worker.rollout.rollout_chunk_prompts,
            "gpu_memory_utilization": obj.worker.rollout.gpu_memory_utilization,
            "episodes": obj.trainer.total_episodes,
            "max_steps": obj.trainer.max_steps,
            "checkpoint_model_revision": obj.trainer.checkpoint_model_revision,
            "strict_checkpoint_manifest": obj.trainer.require_checkpoint_manifest,
            "driver_rng_checkpoint": obj.trainer.require_driver_rng_checkpoint,
            "geometry": serializable(geometry),
        }
        results.append(rows)

    final_train_rows = 27802
    full = results[-1]
    batches_per_episode = final_train_rows // full["rollout_batch_size"]
    full["derived_batches_per_episode_drop_last"] = batches_per_episode
    full["derived_total_outer_steps_20_episodes"] = batches_per_episode * full["episodes"]
    out = {
        "status": "PASS",
        "configs": results,
        "data": {
            "final_train_rows": final_train_rows,
            "rollout_batch_size": 512,
            "drop_last": True,
            "batches_per_episode": batches_per_episode,
            "outer_steps_20_episodes": batches_per_episode * full["episodes"],
        },
        "note": "These are config/geometry validations only; no CUDA, vLLM, FSDP, NCCL, or G4 memory behavior is proven.",
    }
    (REPORT / "g4_config_validation.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
