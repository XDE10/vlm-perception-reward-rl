"""Record the realised VM environment: packages, GPU, CPU/RAM/disk, env lock and model files.

    python -m scripts.colab.env_report --root /content/p3 --out <out>/env.json
"""
import argparse
import json
import os
import platform
import shutil
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PACKAGES = ["torch", "torchvision", "transformers", "trl", "peft", "accelerate", "datasets", "math-verify", "sympy",
            "huggingface-hub", "numpy", "pillow", "pytest", "vllm"]


def _versions():
    out = {}
    for name in PACKAGES:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = None
    return out


def _meminfo():
    try:
        text = Path("/proc/meminfo").read_text()
    except OSError:
        return None
    values = dict(line.split(":", 1) for line in text.splitlines() if ":" in line)
    return round(int(values.get("MemTotal", "0 kB").split()[0]) / 1e6, 1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    root = Path(args.root)
    report = {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count": os.cpu_count(),
              "ram_gb": _meminfo(), "disk_free_gb": round(shutil.disk_usage(str(root)).free / 1e9, 1),
              "packages": _versions()}
    try:
        import torch

        report["torch"] = {"version": torch.__version__, "cuda_runtime": torch.version.cuda,
                           "cudnn": torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None,
                           "cuda_available": torch.cuda.is_available()}
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            report["gpu"] = {"name": props.name, "total_gb": round(props.total_memory / 1e9, 2),
                             "capability": list(torch.cuda.get_device_capability(0)), "count": torch.cuda.device_count(),
                             "bf16": torch.cuda.is_bf16_supported()}
    except ImportError as exc:
        report["torch"] = {"error": str(exc)}
    state = root / "state"
    bootstrap = json.loads((state / "bootstrap.json").read_text()) if (state / "bootstrap.json").is_file() else {}
    base = bootstrap.get("envs", {}).get("base", {})
    report["env"] = {k: base.get(k) for k in ["torch_backend", "lock", "lock_sha256", "freeze_sha256", "install_seconds"]}
    report["driver"] = bootstrap.get("gpu")
    model = bootstrap.get("model") or {}
    report["model"] = {k: model.get(k) for k in ["repo", "revision", "local_dir", "total_bytes", "download_seconds"]}
    report["model_files_sha256"] = {name: info["sha256"] for name, info in (model.get("files") or {}).items()}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    freeze = Path(base.get("python", "")).parent.parent / "freeze.txt" if base.get("python") else None
    if freeze and freeze.is_file():
        shutil.copy2(str(freeze), str(out.parent / "env_freeze.txt"))
    if (state / "nvidia_smi.txt").is_file():
        shutil.copy2(str(state / "nvidia_smi.txt"), str(out.parent / "nvidia_smi.txt"))
    print(json.dumps({k: report.get(k) for k in ["python", "gpu", "torch", "env"]}, default=str)[:1500])


if __name__ == "__main__":
    main()
