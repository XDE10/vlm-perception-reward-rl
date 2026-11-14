"""Unified protocol-v3 GRPO entry for every registered arm.

    python -m scripts.training.train_rl --arm rl_v5 --seed 1 [--runtime runs/frozen_runtime.json]
        [--model-path /content/models/qwen] [--resume runs/.../checkpoint-38]
        [--smoke max_steps=2,num_generations=2,prompts_per_step=2,per_device_train_batch_size=2]

    # S4 formal run: experiment, arms and runtime come from the registered-runs file and must match it exactly
    python -m scripts.training.train_rl --registered configs/experiments/s4_runs_20261110.json --arm rl_v5 --seed 1 \
        [--model-path ...] [--resume runs/rl_v3_p1_20261110/rl_v5/seed1/checkpoint-38]

Smoke overrides are engineering checks only (recorded as ``smoke`` in the run
identity) and never feed reported results. A registered run refuses smoke and
output-directory overrides, a different experiment or runtime file, and (inside
``rl_entry.run``) any difference in config hash, data, row count or GPU.
"""
import argparse
from pathlib import Path

from src.training import registry as registered_runs
from src.training.rl_config import read_json, resolve
from src.training.rl_entry import ROOT, load_runtime, run

DEFAULT_EXPERIMENT = ROOT / "configs/experiments/rl_v3.json"


def parse_smoke(text):
    if not text:
        return None
    out = {}
    for item in text.split(","):
        key, _, value = item.partition("=")
        out[key.strip()] = int(value) if value.strip().isdigit() else value.strip()
    return out


def registered_setup(args, parser):
    """(experiment path, arms path, runtime path, expectation) for ``--registered``; parser errors on any override."""
    if args.smoke:
        parser.error("--smoke is not allowed for a registered run (use the unregistered entry for engineering checks)")
    if args.output_dir:
        parser.error("--output-dir is not allowed for a registered run: its output directory is part of the config hash")
    ledger = registered_runs.load(args.registered, ROOT)
    experiment = ROOT / ledger["experiment"]["path"]
    if args.experiment and Path(args.experiment).resolve() != experiment.resolve():
        parser.error("--experiment %s differs from the registered %s" % (args.experiment, ledger["experiment"]["path"]))
    runtime = Path(args.runtime) if args.runtime else ROOT / ledger["runtime"]["path"]
    if registered_runs.runtime_sha256(read_json(runtime)) != ledger["runtime"]["content_sha256"]:
        parser.error("runtime %s differs from the registered %s" % (runtime, ledger["runtime"]["path"]))
    try:
        expected = registered_runs.expectation(ledger, args.arm, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    return experiment, ROOT / ledger["arms"]["path"], runtime, expected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--experiment", help="experiment config (default configs/experiments/rl_v3.json; with "
                                             "--registered the registered one)")
    parser.add_argument("--arm", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--runtime", help="frozen runtime decisions written by preflight")
    parser.add_argument("--model-path", help="local snapshot of the pinned model revision")
    parser.add_argument("--resume", help="checkpoint directory to resume from (identity must match)")
    parser.add_argument("--output-dir", help="override output directory (default from config)")
    parser.add_argument("--smoke", help="comma-separated smoke overrides, e.g. max_steps=2,num_generations=2")
    parser.add_argument("--registered", help="registered-runs file (S4 formal runs): the run must match it exactly")
    args = parser.parse_args(argv)
    if args.registered:
        experiment, arms, runtime, expected = registered_setup(args, parser)
        config = resolve(experiment, args.arm, args.seed, arms_path=arms)
        return run(config, ROOT, load_runtime(runtime), model_path=args.model_path, resume=args.resume,
                   registered=expected)
    config = resolve(args.experiment or DEFAULT_EXPERIMENT, args.arm, args.seed, smoke=parse_smoke(args.smoke))
    if args.output_dir:
        config["output_dir"] = str(Path(args.output_dir))
    return run(config, ROOT, load_runtime(args.runtime), model_path=args.model_path, resume=args.resume)


if __name__ == "__main__":
    main()
