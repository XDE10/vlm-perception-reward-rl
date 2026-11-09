import copy
import json
from pathlib import Path

import pytest

from src.training.protocol_v3 import PROTOCOL
from src.training.rl_config import read_json, registered_runs, resolve, validate_arms

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "configs/experiments/rl_v3.json"
ARMS = ROOT / "configs/experiments/arms.json"


def flat(d, prefix=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def test_base_config_pins_model_protocol_and_relative_paths():
    base = read_json(BASE)
    assert base["protocol"] == PROTOCOL
    assert len(base["model"]["revision"]) == 40 and base["model"]["revision"] != "main"
    for path in [*base["data"].values(), base["output_root"]]:
        assert not Path(path).is_absolute() and ":" not in path


def test_registered_runs_match_the_plan():
    runs = registered_runs(ARMS)
    assert len(runs) == 12
    counts = {}
    for arm, _ in runs:
        counts[arm] = counts.get(arm, 0) + 1
    assert counts == {"rl_ans": 3, "rl_v4": 2, "rl_v5": 3, "rl_v5_placebo": 2, "rl_blind": 2}
    assert len(registered_runs(ARMS, include_optional=True)) == 14


def test_arms_differ_only_in_declared_factors():
    resolved = {arm: resolve(BASE, arm, seed, n_rows=609) for arm, seed in registered_runs(ARMS, include_optional=True)}
    reference = flat(resolved["rl_ans"])
    allowed = {"arm.name", "arm.perception_reward", "arm.perception_weight", "arm.train_with_image", "arm.metadata",
               "train.scale_rewards", "seed", "run_name", "output_dir", "config_sha256"}
    for arm, config in resolved.items():
        diff = {k for k, v in flat(config).items() if reference.get(k) != v}
        assert diff <= allowed, (arm, diff - allowed)


def test_derived_budget_matches_the_plan():
    r = resolve(BASE, "rl_v5", 1, n_rows=609)
    assert r["train"]["gradient_accumulation_steps"] == 8 and r["train"]["generation_batch_size"] == 64
    assert r["train"]["max_steps"] == 228
    assert r["output_dir"] == "runs/rl_v3_20261109/rl_v5/seed1"
    assert resolve(BASE, "rl_v5_groupnorm", 1)["train"]["scale_rewards"] == "group"
    assert resolve(BASE, "rl_v5", 1)["config_sha256"] == resolve(BASE, "rl_v5", 1)["config_sha256"]


def test_unregistered_seed_and_bad_smoke_keys_fail_closed():
    with pytest.raises(ValueError, match="not registered"):
        resolve(BASE, "rl_v5", 7)
    with pytest.raises(ValueError, match="not allowed"):
        resolve(BASE, "rl_v5", 1, smoke={"learning_rate": 1.0})
    smoke = resolve(BASE, "rl_v5", 7, smoke={"max_steps": 2, "num_generations": 2, "prompts_per_step": 2,
                                              "per_device_train_batch_size": 2}, n_rows=609)
    assert smoke["train"]["max_steps"] == 2 and smoke["run_name"].endswith("_smoke")


def test_arm_validation_rejects_hidden_differences():
    arms = read_json(ARMS)
    bad = copy.deepcopy(arms)
    bad["arms"]["rl_v5"]["learning_rate"] = 1e-4
    with pytest.raises(ValueError, match="non-whitelisted"):
        validate_arms(bad)
    bad = copy.deepcopy(arms)
    bad["arms"]["rl_ans"]["perception_weight"] = 0.1
    with pytest.raises(ValueError, match="weight must be 0"):
        validate_arms(bad)
    assert json.dumps(validate_arms(arms))


def test_vllm_importance_sampling_is_token_level_and_part_of_the_config_hash(tmp_path):
    """D41: the IS correction is an algorithm setting (in config_sha256), not a runtime choice, and is token-level.

    Preflight measured TRL's default sequence-level mask weighting sequences by 0.29-0.55 on average."""
    import importlib.util

    from src.training.rl_entry import ALGORITHM_NEUTRAL_RUNTIME_KEYS, finalize_budget

    base = read_json(BASE)
    assert base["train"]["vllm_importance_sampling_mode"] == "token_truncate"
    assert base["train"]["vllm_importance_sampling_clip_max"] == 2.0
    assert not {k for k in ALGORITHM_NEUTRAL_RUNTIME_KEYS if "importance" in k}  # a runtime file cannot change it
    changed = copy.deepcopy(base)
    changed["train"]["vllm_importance_sampling_mode"] = "sequence_mask"
    (tmp_path / "rl_v3.json").write_text(json.dumps(changed), encoding="utf-8")
    hashes = []
    for path in (BASE, tmp_path / "rl_v3.json"):
        config = resolve(path, "rl_v5", 1, arms_path=ARMS)
        finalize_budget(config, 609)
        hashes.append(config["config_sha256"])
    assert hashes[0] != hashes[1]
    if importlib.util.find_spec("trl") is None:
        return
    a = resolve(BASE, "rl_v5", 1, smoke={"max_steps": 1}, n_rows=8)
    from src.training.rl_entry import DEFAULT_RUNTIME, grpo_args

    vllm = grpo_args(a, dict(DEFAULT_RUNTIME, generation_backend="vllm"), "/tmp/p3-grpo-args-test", False, [1.0])
    assert vllm.use_vllm and vllm.vllm_importance_sampling_correction
    assert (vllm.vllm_importance_sampling_mode, vllm.vllm_importance_sampling_clip_max) == ("token_truncate", 2.0)
    hf = grpo_args(a, dict(DEFAULT_RUNTIME), "/tmp/p3-grpo-args-test", False, [1.0])
    assert not hf.use_vllm  # exactly on-policy: TRL computes no IS ratio without vLLM


def test_accepted_frozen_runtime_loads_and_carries_only_neutral_keys():
    """S4 trains with the runtime frozen by preflight-20261109T122305Z-e6cd (D43)."""
    from src.training.rl_entry import ALGORITHM_NEUTRAL_RUNTIME_KEYS, RUNTIME_META_KEYS, load_runtime

    path = ROOT / "configs/experiments/runtime_frozen_20261109.json"
    runtime = load_runtime(path)
    assert set(json.loads(path.read_text(encoding="utf-8"))) <= ALGORITHM_NEUTRAL_RUNTIME_KEYS | RUNTIME_META_KEYS
    assert runtime["source"] == "preflight preflight-20261109T122305Z-e6cd"
    assert (runtime["generation_backend"], runtime["per_device_train_batch_size"], runtime["vision_cache"],
            runtime["gradient_checkpointing"]) == ("vllm", 8, False, True)
    assert runtime["measured"]["vllm_step_seconds"] <= 0.7 * runtime["measured"]["hf_step_seconds"]  # D21
