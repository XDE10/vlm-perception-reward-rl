"""Resolve one experiment run (base config + arm + seed) into a frozen dict.

Arms may only override the keys listed in ``arms.json:allowed_overrides``;
everything else is shared, so two arms differ exactly in the declared factors.
Smoke overrides exist for engineering checks only, are recorded in the
resolved config and must never feed reported results.
"""
import copy
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "rl-experiment-v1"
ARMS_SCHEMA = "rl-arms-v1"
PERCEPTION_MODES = {"none", "v4", "v5"}
METADATA_MODES = {"own", "placebo"}
SCALE_MODES = {"group", "batch", "none"}
SMOKE_KEYS = {"max_steps", "num_generations", "prompts_per_step", "per_device_train_batch_size",
              "max_completion_length", "limit_rows", "save_steps"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def validate_arms(arms):
    if arms.get("schema") != ARMS_SCHEMA:
        raise ValueError("arms.json schema mismatch")
    allowed = set(arms["allowed_overrides"])
    for name, arm in arms["arms"].items():
        extra = set(arm) - allowed
        if extra:
            raise ValueError(f"arm {name} overrides non-whitelisted keys {sorted(extra)}")
        if arm.get("perception_reward") not in PERCEPTION_MODES:
            raise ValueError(f"arm {name}: perception_reward must be one of {sorted(PERCEPTION_MODES)}")
        if arm.get("metadata") not in METADATA_MODES:
            raise ValueError(f"arm {name}: metadata must be one of {sorted(METADATA_MODES)}")
        if not isinstance(arm.get("train_with_image"), bool):
            raise ValueError(f"arm {name}: train_with_image must be boolean")
        weight = arm.get("perception_weight")
        if not isinstance(weight, (int, float)) or weight < 0:
            raise ValueError(f"arm {name}: perception_weight must be >= 0")
        if (arm["perception_reward"] == "none") != (weight == 0):
            raise ValueError(f"arm {name}: weight must be 0 exactly when perception_reward is none")
        if arm["metadata"] == "placebo" and arm["perception_reward"] == "none":
            raise ValueError(f"arm {name}: placebo metadata needs a perception reward")
        if "scale_rewards" in arm and arm["scale_rewards"] not in SCALE_MODES:
            raise ValueError(f"arm {name}: bad scale_rewards")
        if name not in arms["seeds"] or not arms["seeds"][name]:
            raise ValueError(f"arm {name} has no seeds")
    return arms


def resolve(experiment_path, arm, seed, arms_path=None, smoke=None, n_rows=None):
    base = read_json(experiment_path)
    if base.get("schema") != SCHEMA:
        raise ValueError("experiment schema mismatch")
    arms = validate_arms(read_json(arms_path or Path(experiment_path).with_name("arms.json")))
    if arm not in arms["arms"]:
        raise ValueError(f"unknown arm {arm}; known: {sorted(arms['arms'])}")
    if int(seed) not in arms["seeds"][arm] and not smoke:
        raise ValueError(f"seed {seed} not registered for arm {arm}: {arms['seeds'][arm]}")
    resolved = copy.deepcopy(base)
    overrides = arms["arms"][arm]
    resolved["arm"] = {"name": arm, **{k: v for k, v in overrides.items() if k != "scale_rewards"}}
    if "scale_rewards" in overrides:
        resolved["train"]["scale_rewards"] = overrides["scale_rewards"]
    resolved["seed"] = int(seed)
    resolved["smoke"] = dict(smoke or {})
    for key, value in resolved["smoke"].items():
        if key not in SMOKE_KEYS:
            raise ValueError(f"smoke override {key} not allowed")
        if key in resolved["train"]:
            resolved["train"][key] = value
    train = resolved["train"]
    completions_per_step = train["prompts_per_step"] * train["num_generations"]
    if completions_per_step % train["per_device_train_batch_size"]:
        raise ValueError("prompts_per_step * num_generations must be divisible by per_device_train_batch_size")
    train["gradient_accumulation_steps"] = completions_per_step // train["per_device_train_batch_size"]
    train["generation_batch_size"] = completions_per_step
    if n_rows is not None:
        rows = min(n_rows, resolved["smoke"].get("limit_rows", n_rows))
        train["max_steps"] = resolved["smoke"].get("max_steps") or math.floor(train["epochs"] * rows / train["prompts_per_step"])
    resolved["run_name"] = f"{arm}/seed{int(seed)}" + ("_smoke" if smoke else "")
    resolved["output_dir"] = str(Path(base["output_root"]) / resolved["run_name"])
    resolved["config_sha256"] = canonical_sha256({k: v for k, v in resolved.items() if k != "config_sha256"})
    return resolved


def registered_runs(arms_path, include_optional=False):
    arms = validate_arms(read_json(arms_path))
    optional = set(arms.get("optional_arms", []))
    return [(arm, seed) for arm in arms["arms"] if include_optional or arm not in optional for seed in arms["seeds"][arm]]


__all__ = ["canonical_sha256", "read_json", "registered_runs", "resolve", "validate_arms"]
