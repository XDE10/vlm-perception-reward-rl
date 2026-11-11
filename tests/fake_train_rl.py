"""A stand-in for ``python -m scripts.training.train_rl`` used by the S4 runner tests (no model, no torch).

Takes the same arguments, writes what rl_entry writes (rollouts.jsonl, checkpoint-<step>/ with run_identity.json and
trainer_state.json, final/, run_identity.json, train_summary.json, log_history.json, trainable_parameters.json) and
prints the same JSON events (registration_matched, train_log, checkpoint_saved, train_done), the first ones behind
tqdm-like text as on the VM. Behaviour is chosen per run through environment variables whose value is
"<arm>/<seed>:<step>" (several separated by ","; the seed may be "*"):

* FAKE_TRAIN_FAIL       raise FloatingPointError at that step (a computation failure);
* FAKE_TRAIN_FAIL_ONCE  the same, only while the file $FAKE_TRAIN_STATE_DIR/<arm>_<seed>.failed does not exist;
* FAKE_TRAIN_HANG       print that step, then sleep until killed;
* FAKE_TRAIN_SETUP      exit at once with "does not match its registration" (a setup failure; the step is ignored).

FAKE_TRAIN_STEP_SECONDS (default 0) is slept per step; FAKE_TRAIN_FORMAT ("up" or "down") shapes the logged format
rate for gate G4; FAKE_TRAIN_IS_RATIO overrides the logged importance-sampling mean weight for gate G1.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

P1 = "perception-think-answer-v3-p1-20261109"


def matches(variable, arm, seed):
    """The step named for this run in ``variable``, or None."""
    for item in filter(None, os.environ.get(variable, "").split(",")):
        target, _, step = item.partition(":")
        want_arm, _, want_seed = target.partition("/")
        if want_arm == arm and want_seed in ("*", str(seed)):
            return int(step or 0)
    return None


def parse_smoke(text):
    out = {}
    for item in filter(None, (text or "").split(",")):
        key, _, value = item.partition("=")
        out[key] = int(value)
    return out


def identity_of(args, config_sha, out_dir):
    source, versions = {"fake": "registered run"}, {}
    if not args.registered:
        # pilot runs: the code identity the real entry records, by the same functions (decide_pilot compares it);
        # registered runs skip this slow import, train_s4 checks the code before it starts them
        from src.training.rl_entry import ROOT, SOURCE_FILES, package_versions, sha256_file

        source = {p: sha256_file(ROOT / p) for p in SOURCE_FILES if (ROOT / p).is_file()}
        versions = package_versions()
    return {"schema": "rl-run-identity-v1", "config_sha256": config_sha, "fake": True,
            "config": {"arm": {"name": args.arm, "train_with_image": args.arm != "rl_blind"}, "seed": args.seed,
                       "protocol": P1, "output_dir": str(out_dir),
                       "train": {"max_steps": args.max_steps}},
            "source_sha256": source, "versions": versions,
            "prompt_report": {"prompts": 609, "max_tokens": 1153, "mean_tokens": 453.3, "limit": 1600},
            "parameters": {"trainable_parameters": 29933568, "vision_frozen": True}}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment")
    parser.add_argument("--arm", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--runtime")
    parser.add_argument("--model-path")
    parser.add_argument("--resume")
    parser.add_argument("--output-dir")
    parser.add_argument("--smoke")
    parser.add_argument("--registered")
    args = parser.parse_args(argv)
    if matches("FAKE_TRAIN_SETUP", args.arm, args.seed) is not None:
        sys.exit("ValueError: run does not match its registration (fake): config_sha256 differs")
    smoke = parse_smoke(args.smoke)
    if args.registered:
        registry = json.loads(Path(args.registered).read_text(encoding="utf-8"))
        entry = next(e for e in registry["runs"] + registry.get("optional_runs", [])
                     if e["arm"] == args.arm and int(e["seed"]) == args.seed)
        out_dir = Path(entry["output_dir"])
        config_sha, args.max_steps, save_steps = entry["config_sha256"], entry["max_steps"], 38
        print(json.dumps({"event": "registration_matched", "registry": registry["name"], "arm": args.arm,
                          "seed": args.seed, "config_sha256": config_sha}), flush=True)
    else:
        out_dir = Path(args.output_dir)
        args.max_steps, save_steps = smoke.get("max_steps", 228), smoke.get("save_steps", 38)
        config_sha = hashlib.sha256(json.dumps([args.arm, args.seed, smoke, str(out_dir)]).encode()).hexdigest()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir = out_dir.absolute()  # like rl_entry, which prints checkpoint paths under root / output_dir
    identity = identity_of(args, config_sha, out_dir)
    start = 0
    if args.resume:
        prior = json.loads((Path(args.resume) / "run_identity.json").read_text(encoding="utf-8"))
        if prior.get("config_sha256") != config_sha:
            sys.exit("ValueError: Checkpoint identity mismatch in ['config']; start a new output directory")
        start = json.loads((Path(args.resume) / "trainer_state.json").read_text())["global_step"]
    elif list(out_dir.glob("checkpoint-*")):
        sys.exit("ValueError: Output directory already has checkpoints; pass --resume or use a new output directory")
    (out_dir / "run_identity.json").write_text(json.dumps(identity, indent=2), encoding="utf-8")
    history = []
    if args.resume:
        history = json.loads((Path(args.resume) / "trainer_state.json").read_text()).get("log_history", [])
    fail_at = matches("FAKE_TRAIN_FAIL", args.arm, args.seed)
    once_at = matches("FAKE_TRAIN_FAIL_ONCE", args.arm, args.seed)
    once_file = Path(os.environ.get("FAKE_TRAIN_STATE_DIR", ".")) / ("%s_%d.failed" % (args.arm, args.seed))
    hang_at = matches("FAKE_TRAIN_HANG", args.arm, args.seed)
    pause = float(os.environ.get("FAKE_TRAIN_STEP_SECONDS", "0"))
    shape = os.environ.get("FAKE_TRAIN_FORMAT", "up")
    ratio = float(os.environ.get("FAKE_TRAIN_IS_RATIO", "0.998"))
    sys.stdout.write("Loading weights: 100%|##########| 824/824\n")
    for step in range(start + 1, args.max_steps + 1):
        if pause:
            time.sleep(pause)
        if fail_at == step or (once_at == step and not once_file.exists()):
            if once_at == step:
                once_file.parent.mkdir(parents=True, exist_ok=True)
                once_file.write_text("1")
            raise FloatingPointError("non-finite {'loss': nan} at step %d; the run stops (fake)" % step)
        fraction = step / float(args.max_steps)
        fmt = round(0.5 + 0.3 * fraction if shape == "up" else 0.8 - 0.3 * fraction, 4)
        with (out_dir / "rollouts.jsonl").open("a", encoding="utf-8") as handle:
            for index in range(2):
                handle.write(json.dumps({"schema": "rl-rollout-v1", "protocol": P1, "arm": args.arm, "seed": args.seed,
                                         "global_step": step - 1, "index": index, "completion_tokens": 100,
                                         "protocol_ok": True, "answer": {"correct": False, "status": "mismatch"},
                                         "rewards": {"answer": 0.0, "format": 1.0, "perception": 0.0},
                                         "v5_own": {"reward": 0.0, "unique": 2}}) + "\n")
        logs = {"loss": 0.01, "grad_norm": 0.1, "step_time": pause or 0.001, "p3/format_rate": fmt,
                "p3/answer_acc": 0.03, "p3/claims_per_completion": 2.0, "kl": 0.0005, "entropy": 1.0,
                "completions/mean_length": 180.0, "completions/clipped_ratio": 0.0,
                "sampling/importance_sampling_ratio/mean": ratio, "sampling/sampling_logp_difference/mean": 0.065}
        history.append(dict(logs, step=step))
        print(" %d%%|###| %d/%d [00:01<00:01]" % (100 * step // args.max_steps, step, args.max_steps)
              + json.dumps(dict({"event": "train_log", "step": step, "max_steps": args.max_steps}, **logs)), flush=True)
        if hang_at == step:
            while True:
                time.sleep(1)
        if step % save_steps == 0 or step == args.max_steps:
            checkpoint = out_dir / ("checkpoint-%d" % step)
            checkpoint.mkdir(exist_ok=True)
            (checkpoint / "adapter_model.safetensors").write_bytes(hashlib.sha256(b"%d" % step).digest() * 64)
            (checkpoint / "optimizer.pt").write_bytes(b"o" * 3000)
            (checkpoint / "trainer_state.json").write_text(json.dumps({"global_step": step, "log_history": history}))
            (checkpoint / "run_identity.json").write_text(json.dumps(identity, indent=2), encoding="utf-8")
            print(json.dumps({"event": "checkpoint_saved", "step": step, "path": str(checkpoint),
                              "config_sha256": config_sha}), flush=True)
    final = out_dir / "final"
    final.mkdir(exist_ok=True)
    (final / "adapter_model.safetensors").write_bytes(b"final-%d" % args.max_steps)
    (final / "adapter_config.json").write_text("{}")
    summary = {"run": "%s/seed%d" % (args.arm, args.seed), "config_sha256": config_sha, "global_step": args.max_steps,
               "max_steps": args.max_steps, "peak_gpu_memory_gb": 23.2, "generation_backend": "vllm",
               "mm_alignment": {"checked_forwards": 3, "left_padded_rows": 8},
               "vllm_image_grid": {"images": 609, "mismatches": 0} if args.arm != "rl_blind" else None}
    (out_dir / "train_summary.json").write_text(json.dumps(summary, indent=2))
    (out_dir / "log_history.json").write_text(json.dumps(history))
    (out_dir / "trainable_parameters.json").write_text(json.dumps({"trainable_parameters": 29933568}))
    print(json.dumps(dict({"event": "train_done"}, **summary)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
