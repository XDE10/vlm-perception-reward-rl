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
