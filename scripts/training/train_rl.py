"""Unified protocol-v3 GRPO entry for every registered arm.

    python -m scripts.training.train_rl --arm rl_v5 --seed 1 [--runtime runs/frozen_runtime.json]
        [--model-path /content/models/qwen] [--resume runs/.../checkpoint-38]
        [--smoke max_steps=2,num_generations=2,prompts_per_step=2,per_device_train_batch_size=2]

Smoke overrides are engineering checks only (recorded as ``smoke`` in the run
identity) and never feed reported results.
"""
import argparse
from pathlib import Path

from src.training.rl_config import resolve
from src.training.rl_entry import ROOT, load_runtime, run


def parse_smoke(text):
    if not text:
        return None
    out = {}
    for item in text.split(","):
        key, _, value = item.partition("=")
        out[key.strip()] = int(value) if value.strip().isdigit() else value.strip()
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--experiment", default=str(ROOT / "configs/experiments/rl_v3.json"))
    parser.add_argument("--arm", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--runtime", help="frozen runtime decisions written by preflight")
    parser.add_argument("--model-path", help="local snapshot of the pinned model revision")
    parser.add_argument("--resume", help="checkpoint directory to resume from (identity must match)")
    parser.add_argument("--output-dir", help="override output directory (default from config)")
    parser.add_argument("--smoke", help="comma-separated smoke overrides, e.g. max_steps=2,num_generations=2")
    args = parser.parse_args(argv)
    config = resolve(args.experiment, args.arm, args.seed, smoke=parse_smoke(args.smoke))
    if args.output_dir:
        config["output_dir"] = str(Path(args.output_dir))
    return run(config, ROOT, load_runtime(args.runtime), model_path=args.model_path, resume=args.resume)


if __name__ == "__main__":
    main()
