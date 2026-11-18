#!/usr/bin/env python3
"""Capture non-secret local evidence for the project-three status report."""
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path("/home/xde10/projects/vlm-perception-reward-rl")
REPORT = PROJECT / "reports/shuffle_r1_cpu_data_freeze_20261115"
DEV = Path("/home/xde10/.local/state/vlm-perception-reward-rl/shuffle-r1-g4-dev")
FINAL_DATA = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-visible-clean")
DRIVE_DEST = "mydrive:datasets/Shuffle-R1/MMRL30k-b362381-visible-clean"


def run(args, cwd=None, timeout=15):
    try:
        p = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        return {"returncode": p.returncode, "output": p.stdout.strip()}
    except Exception as e:
        return {"error": repr(e)}


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    state = {
        "project_root": str(PROJECT),
        "shuffle_r1_dev": str(DEV),
        "dev_git_status": run(["git", "status", "--short", "--branch"], cwd=DEV),
        "dev_git_log": run(["git", "log", "-4", "--format=%H %s"], cwd=DEV),
        "dev_git_diff_stat": run(["git", "diff", "--stat"], cwd=DEV),
        "dev_git_diff_check": run(["git", "diff", "--check"], cwd=DEV),
        "cpu_test_log_tail": (REPORT / "cpu-alpha-fix-full.txt").read_text(encoding="utf-8", errors="replace")[-5000:] if (REPORT / "cpu-alpha-fix-full.txt").exists() else None,
        "real_data_collate": json.loads((REPORT / "real-filtered-data-collate.txt").read_text(encoding="utf-8")) if (REPORT / "real-filtered-data-collate.txt").exists() else None,
        "alpha_rendering_audit": json.loads((REPORT / "alpha_rendering_delta.json").read_text(encoding="utf-8")) if (REPORT / "alpha_rendering_delta.json").exists() else None,
        "final_train_manifest": json.loads((REPORT / "final_decontaminated_train_manifest.json").read_text(encoding="utf-8")) if (REPORT / "final_decontaminated_train_manifest.json").exists() else None,
        "decontaminated_train_verification": json.loads((REPORT / "decontaminated_train_verification.json").read_text(encoding="utf-8")) if (REPORT / "decontaminated_train_verification.json").exists() else None,
        "g4_config_validation": json.loads((REPORT / "g4_config_validation.json").read_text(encoding="utf-8")) if (REPORT / "g4_config_validation.json").exists() else None,
        "s5_resume_verification": json.loads((REPORT / "s5-resume-verification.json").read_text(encoding="utf-8")),
        "colab_usage": run(["colab", "usage"], timeout=20),
        "colab_sessions": run(["colab", "sessions"], timeout=20),
        "colab_ls": run(["colab", "ls"], timeout=20),
        "drive_listing": run(["rclone", "lsjson", DRIVE_DEST], timeout=60),
        "drive_about": run(["rclone", "about", "mydrive:"], timeout=30),
        "final_data_files": {},
    }
    for name in ["train.parquet", "probe_val.parquet", "manifest.json"]:
        path = FINAL_DATA / name
        if path.exists():
            state["final_data_files"][name] = {
                "bytes": path.stat().st_size,
                "sha256": file_sha(path),
            }
    out = REPORT / "latest_state_snapshot.json"
    out.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out)
    print("snapshot_bytes", out.stat().st_size)


if __name__ == "__main__":
    main()
