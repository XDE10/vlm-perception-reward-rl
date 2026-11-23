"""Restore and run the pinned single-GPU Shuffle-R1 experiment on Linux."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCE = "1a7fb4b67e02a6b41cde437d7edc074ddd5a22e6"
SOURCE_BRANCH = "g4-logical-batch-prep-20261115"


def digest(path, algorithm="sha256"):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def restore_source(work):
    source = work / "source"
    if not source.exists():
        work.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-c", "core.autocrlf=false", "--branch", SOURCE_BRANCH, str(HERE / "source.bundle"),
                        str(source)], check=True)
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"], text=True)
    if head != SOURCE or dirty:
        raise ValueError(f"Expected an unmodified checkout of {SOURCE}: {source}")
    return source


def verify_inputs(inputs, manifest):
    for name in ("train.parquet", "dev.parquet"):
        path = inputs / name
        if not path.is_file() or digest(path) != manifest["files"][name]["sha256"]:
            raise ValueError(f"Missing or changed frozen input: {path}")


def verify_model(model, identity):
    for name, expected in identity["files"].items():
        path = model / name
        if not path.is_file() or path.stat().st_size != expected["bytes"]:
            raise ValueError(f"Missing or changed model file: {path}")
        if "sha256" in expected:
            matches = digest(path) == expected["sha256"]
        else:
            content = path.read_bytes()
            matches = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest() == expected["git_blob_sha1"]
        if not matches:
            raise ValueError(f"Model digest differs from the pinned revision: {path}")


def train(args, source):
    manifest = json.loads((HERE / "split_manifest.json").read_text(encoding="utf-8"))
    inputs = (args.inputs or args.work_dir / "data").resolve()
    verify_inputs(inputs, manifest)
    identity = json.loads((HERE / "model-identity.json").read_text(encoding="utf-8"))
    model = (args.model or args.work_dir / "model-snapshot").absolute()
    if args.model is None and not model.exists():
        from huggingface_hub import snapshot_download

        snapshot = snapshot_download(identity["repo"], revision=identity["revision"],
                                     allow_patterns=list(identity["files"]))
        model.symlink_to(snapshot, target_is_directory=True)
    verify_model(model, identity)

    manifest["processor"]["model"] = str(model)
    local_manifest = args.work_dir / "data" / "split_manifest.json"
    local_manifest.parent.mkdir(parents=True, exist_ok=True)
    if local_manifest.exists():
        if json.loads(local_manifest.read_text(encoding="utf-8")) != manifest:
            raise ValueError(f"Existing split manifest differs: {local_manifest}")
    else:
        local_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    checkpoints = args.work_dir / "checkpoints" / "qwen25vl3b_b512_seed1"
    if args.resume is None and checkpoints.is_dir() and any(checkpoints.iterdir()):
        raise ValueError(f"Existing checkpoints in {checkpoints}. Supply --resume or use a different --work-dir.")
    command = [sys.executable, "-u", str(HERE / "run_main.py"), f"config={HERE / 'train.yaml'}",
               f"data.train_files={inputs / 'train.parquet'}", f"data.val_files={inputs / 'dev.parquet'}",
               f"data.split_manifest={local_manifest}", f"worker.actor.model.model_path={model}",
               f"worker.actor.model.tokenizer_path={model}", f"trainer.save_checkpoint_path={checkpoints}",
               f"trainer.stop_after_step={args.stop_after}"]
    if args.resume is not None:
        command.append(f"trainer.load_checkpoint_path={args.resume.resolve()}")
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(source), str(HERE)]), PYTHONHASHSEED="0",
               HF_HUB_OFFLINE="1", FLASH_ATTENTION_DETERMINISTIC="1", CUBLAS_WORKSPACE_CONFIG=":4096:8",
               VLLM_USE_V1="1", VLLM_ENABLE_V1_MULTIPROCESSING="0", VLLM_ATTENTION_BACKEND="FLASH_ATTN",
               VLLM_USE_FLASHINFER_SAMPLER="0", RAY_DEDUP_LOGS="0", NCCL_SOCKET_IFNAME="lo",
               NCCL_IB_DISABLE="1", NCCL_P2P_DISABLE="1", TORCH_NCCL_AVOID_RECORD_STREAMS="1")
    subprocess.run(command, cwd=source, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "train"))
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, help="directory with the frozen train.parquet and dev.parquet")
    parser.add_argument("--model", type=Path, help="existing pinned model snapshot")
    parser.add_argument("--resume", type=Path, help="full checkpoint made with the same model/data paths and config")
    parser.add_argument("--stop-after", type=int, default=150, choices=range(1, 151), metavar="1..150")
    args = parser.parse_args()
    args.work_dir = args.work_dir.resolve()
    try:
        source = restore_source(args.work_dir)
        if args.command == "prepare":
            print(f"Prepared {SOURCE} at {source}")
        else:
            train(args, source)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Shuffle-R1: {exc}\n")


if __name__ == "__main__":
    main()
