"""Unified protocol-v3 GRPO entry (all arms): data gates -> model -> rewards -> TRL.

One code path serves every arm; arms differ only through the resolved config
(``src/training/rl_config.py``). Runtime choices that do not change the
algorithm (generation backend, frozen-ViT cache) come from a frozen runtime file
written by preflight and are recorded in the run identity.
"""
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from src.rewards.perception_v5 import V5Config
from src.training.lora_language import attach_language_lora, parameter_identity
from src.training.multimodal_guard import MultimodalAlignmentGuard, left_pad_processor
from src.training.rl_config import canonical_sha256
from src.training.rl_data import build_items, load_training_rows, prompt_length_report
from src.training.rl_rewards import RewardBank

ROOT = Path(__file__).resolve().parents[2]
IDENTITY_SCHEMA = "rl-run-identity-v1"
DEFAULT_RUNTIME = {"generation_backend": "hf", "vllm_gpu_memory_utilization": 0.3, "vllm_max_model_length": 4096,
                   "vision_cache": False, "per_device_train_batch_size": None, "gradient_checkpointing": None,
                   "source": "default (no preflight decision file)"}
# Runtime keys only change memory/speed, never the optimisation problem: per_device_train_batch_size
# re-splits the same 64 completions per step (DAPO normalises over the whole accumulated batch).
ALGORITHM_NEUTRAL_RUNTIME_KEYS = {"generation_backend", "vllm_gpu_memory_utilization", "vllm_max_model_length",
                                  "vision_cache", "per_device_train_batch_size", "gradient_checkpointing"}
SOURCE_FILES = [
    "src/rewards/answer.py", "src/rewards/attacks.py", "src/rewards/claims.py", "src/rewards/geometry_oracle.py",
    "src/rewards/perception_v5.py", "src/training/hf_compat.py", "src/training/lora_language.py",
    "src/training/multimodal_guard.py", "src/training/protocol_v3.py", "src/training/rl_config.py",
    "src/training/rl_data.py",
    "src/training/rl_entry.py", "src/training/rl_rewards.py", "src/training/vision_cache.py",
    "src/data/approved_training_inputs.py", "src/data/intergps_index.py", "src/data/perception_v4.py",
    "src/data/project3_perception_v2.py", "src/data/project3_perception_prototype.py",
    "src/training/perception_reward_v4.py", "scripts/training/math_verify_v3_strict_worker.py",
    "scripts/training/math_verify_pilot_worker.py",
]
PACKAGES = ["torch", "transformers", "trl", "peft", "accelerate", "datasets", "math-verify", "sympy", "vllm", "pillow"]


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def package_versions():
    out = {}
    for name in PACKAGES:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = None
    return out


def git_commit():
    if os.environ.get("P3_GIT_COMMIT"):
        return os.environ["P3_GIT_COMMIT"]
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=10,
                              check=True).stdout.strip()
    except Exception:
        return None


def load_runtime(path):
    if not path:
        return dict(DEFAULT_RUNTIME)
    runtime = json.loads(Path(path).read_text(encoding="utf-8"))
    if runtime.get("generation_backend") not in {"hf", "vllm"}:
        raise ValueError("runtime generation_backend must be hf or vllm")
    return {**DEFAULT_RUNTIME, **runtime}


def apply_runtime(config, runtime):
    """Apply algorithm-neutral runtime choices (micro-batch split) to a resolved config."""
    micro = runtime.get("per_device_train_batch_size")
    if micro and not config.get("smoke", {}).get("per_device_train_batch_size"):
        train = config["train"]
        completions = train["prompts_per_step"] * train["num_generations"]
        if completions % int(micro):
            raise ValueError(f"runtime per_device_train_batch_size={micro} does not divide {completions} completions/step")
        train["per_device_train_batch_size"] = int(micro)
        train["gradient_accumulation_steps"] = completions // int(micro)
        train["generation_batch_size"] = completions
    return config


def finalize_budget(config, n_rows):
    train = config["train"]
    rows = min(n_rows, config.get("smoke", {}).get("limit_rows", n_rows))
    train["max_steps"] = config.get("smoke", {}).get("max_steps") or math.floor(train["epochs"] * rows / train["prompts_per_step"])
    config["config_sha256"] = canonical_sha256({k: v for k, v in config.items() if k != "config_sha256"})
    return config


def grpo_args(config, runtime, output_dir, cuda, weights):
    from trl import GRPOConfig

    t = config["train"]
    checkpointing = runtime.get("gradient_checkpointing")
    checkpointing = bool(cuda) if checkpointing is None else bool(checkpointing)
    options = dict(
        output_dir=str(output_dir), max_steps=t["max_steps"], learning_rate=t["learning_rate"],
        lr_scheduler_type=t["lr_scheduler_type"], warmup_steps=t["warmup_steps"], max_grad_norm=t["max_grad_norm"],
        per_device_train_batch_size=t["per_device_train_batch_size"],
        gradient_accumulation_steps=t["gradient_accumulation_steps"], num_generations=t["num_generations"],
        generation_batch_size=t["generation_batch_size"], max_completion_length=t["max_completion_length"],
        temperature=t["temperature"], top_p=t["top_p"], beta=t["beta"], loss_type=t["loss_type"],
        epsilon=t["epsilon"], epsilon_high=t["epsilon_high"], scale_rewards=t["scale_rewards"],
        mask_truncated_completions=t["mask_truncated_completions"], reward_weights=weights,
        num_iterations=1, disable_dropout=True, bf16=bool(cuda), use_cpu=not cuda,
        gradient_checkpointing=checkpointing, gradient_checkpointing_kwargs={"use_reentrant": False},
        logging_steps=t["logging_steps"], save_strategy="steps", save_steps=t["save_steps"], save_only_model=False,
        seed=config["seed"], data_seed=config["seed"], report_to="none", remove_unused_columns=False,
        log_completions=False, dataloader_num_workers=0,
        use_vllm=runtime["generation_backend"] == "vllm",
    )
    if options["use_vllm"]:
        options.update(vllm_mode="colocate", vllm_gpu_memory_utilization=runtime["vllm_gpu_memory_utilization"],
                       vllm_max_model_length=runtime["vllm_max_model_length"])
    return GRPOConfig(**options)


def load_model_and_processor(config, model_path=None, cuda=True):
    import torch
    from transformers import AutoProcessor

    from src.training.hf_compat import vision_model_class

    m = config["model"]
    source = model_path or m["id"]
    kwargs = {} if model_path else {"revision": m["revision"]}
    processor = AutoProcessor.from_pretrained(source, max_pixels=m["max_pixels"], min_pixels=m["min_pixels"], **kwargs)
    model = vision_model_class().from_pretrained(source, dtype=torch.bfloat16 if cuda else torch.float32,
                                                 attn_implementation=m["attn_implementation"], **kwargs)
    return model, processor


def run(config, root=ROOT, runtime=None, model_path=None, resume=None, model=None, processor=None,
        extra_reward_funcs=None):
    import torch
    from datasets import Dataset
    from transformers import TrainerCallback, set_seed
    from trl import GRPOTrainer

    root = Path(root)
    runtime = dict(runtime or DEFAULT_RUNTIME)
    cuda = torch.cuda.is_available()
    if not cuda and not config.get("smoke"):
        raise RuntimeError("Formal runs require CUDA; CPU is allowed for smoke configs only")
    if cuda and torch.cuda.device_count() != 1:
        raise RuntimeError("Exactly one visible GPU is supported")
    set_seed(config["seed"])
    rows, index = load_training_rows(config, root)
    unknown = set(runtime) - ALGORITHM_NEUTRAL_RUNTIME_KEYS - {"source", "measured", "notes", "decided_utc", "rationale",
                                                               "gpu", "torch_backend", "env_lock_sha256", "schema"}
    if unknown:
        raise ValueError(f"runtime file has keys that could change the algorithm: {sorted(unknown)}")
    apply_runtime(config, runtime)
    finalize_budget(config, len(rows))
    out = Path(config["output_dir"])
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)
    if model is None or processor is None:
        model, processor = load_model_and_processor(config, model_path, cuda)
    left_pad_processor(processor)  # TRL's scoring pass relies on the processor default (D33)
    items, mapping = build_items(config, rows, index, root)
    prompt_report = prompt_length_report(items, processor, config["train"]["max_prompt_tokens"])
    lora = config["lora"]
    model, targets, params = attach_language_lora(model, lora["r"], lora["alpha"], lora["dropout"])
    cache = None
    if runtime.get("vision_cache") and config["arm"]["train_with_image"]:
        from src.training.vision_cache import FrozenVisionCache

        cache = FrozenVisionCache(model)
    data = config["data"]
    identity = {
        "schema": IDENTITY_SCHEMA,
        "config_sha256": config["config_sha256"],
        "config": config,
        "runtime": {k: v for k, v in runtime.items() if k not in {"measured", "notes"}},
        "versions": package_versions(),
        "git_commit": git_commit(),
        "source_sha256": {p: sha256_file(ROOT / p) for p in SOURCE_FILES if (ROOT / p).is_file()},
        "data_sha256": {
            "manifest": sha256_file(root / data["manifest"]),
            "train_file": sha256_file((root / data["manifest"]).parent / data["train_file"]),
            "intergps_annotations": sha256_file(root / data["intergps_annotations"]),
        },
        "rows": len(rows),
        "placebo_mapping_sha256": canonical_sha256(mapping),
        "prompt_report": prompt_report,
        "lora_targets_sha256": canonical_sha256(targets),
        "parameters": {k: v for k, v in params.items() if k != "trainable_names"},
        "model_source": f"{config['model']['id']}@{config['model']['revision']}",
        "model_local_path": str(model_path) if model_path else None,
    }
    identity_path = out / "run_identity.json"
    if resume:
        prior = json.loads((Path(resume) / "run_identity.json").read_text(encoding="utf-8"))
        changed = [k for k in identity if k != "git_commit" and prior.get(k) != identity[k]]
        if changed:
            raise ValueError(f"Checkpoint identity mismatch in {changed}; start a new output directory")
    elif list(out.glob("checkpoint-*")):
        raise ValueError("Output directory already has checkpoints; pass --resume or use a new output directory")
    identity_path.write_text(json.dumps(identity, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "trainable_parameters.json").write_text(json.dumps(params, indent=2), encoding="utf-8")

    weights = {"answer": config["rewards"]["answer_weight"], "format": config["rewards"]["format_weight"],
               "perception": config["arm"]["perception_weight"]}
    from src.rewards.answer import AnswerVerifier

    bank = RewardBank(config["arm"], weights, V5Config.from_dict(config["perception_v5"]), out / "rollouts.jsonl",
                      AnswerVerifier(config["rewards"]["verifier_workers"], config["rewards"]["verifier_timeout"]),
                      run_meta={"arm": config["arm"]["name"], "seed": config["seed"], "run": config["run_name"]})
    reward_funcs = bank.reward_funcs() + list(extra_reward_funcs or [])
    reward_weights = bank.reward_weights() + [1.0] * len(extra_reward_funcs or [])

    class IdentityCallback(TrainerCallback):
        def on_save(self, args, state, control, **kwargs):
            target = Path(args.output_dir) / f"checkpoint-{state.global_step}" / "run_identity.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(identity, ensure_ascii=False, indent=2), encoding="utf-8")

    class ProgressCallback(TrainerCallback):
        def on_log(self, args, state, control, logs=None, **kwargs):
            keep = {k: round(v, 4) if isinstance(v, float) else v for k, v in (logs or {}).items()
                    if k.startswith(("p3/", "reward", "kl", "loss", "completions/", "entropy", "step_time", "grad_norm"))}
            print(json.dumps({"event": "train_log", "step": state.global_step, "max_steps": state.max_steps, **keep}),
                  flush=True)

    trainer = GRPOTrainer(model=model, args=grpo_args(config, runtime, out, cuda, reward_weights),
                          train_dataset=Dataset.from_list(items), processing_class=processor,
                          reward_funcs=reward_funcs, callbacks=[IdentityCallback(), ProgressCallback()])
    parameter_identity(trainer.model)
    guard = MultimodalAlignmentGuard(trainer.model)
    started = time.time()
    try:
        trainer.train(resume_from_checkpoint=resume)
    finally:
        bank.close()
        guard.remove()
    trainer.save_model(str(out / "final"))
    processor.save_pretrained(str(out / "final"))
    summary = {
        "run": config["run_name"],
        "config_sha256": config["config_sha256"],
        "global_step": trainer.state.global_step,
        "max_steps": config["train"]["max_steps"],
        "wall_seconds": time.time() - started,
        "peak_gpu_memory_gb": (torch.cuda.max_memory_allocated() / 1e9) if cuda else None,
        "vision_cache": cache.stats() if cache else None,
        "mm_alignment": guard.stats(),
        "generation_backend": runtime["generation_backend"],
        "python": sys.version.split()[0],
    }
    (out / "log_history.json").write_text(json.dumps(trainer.state.log_history, indent=1), encoding="utf-8")
    (out / "train_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"event": "train_done", **summary}), flush=True)
    return summary


__all__ = ["ALGORITHM_NEUTRAL_RUNTIME_KEYS", "DEFAULT_RUNTIME", "apply_runtime", "finalize_budget", "grpo_args",
           "load_model_and_processor", "load_runtime", "run"]
