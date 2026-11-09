"""End-to-end test of colab/launch.sh against a stub `colab` CLI (no network, no GPU).

A throwaway copy of this repository (with a mini data payload and a matching
ledger) runs `launch.sh preflight --dry-run`: pack, upload, kernel bootstrap,
job steps, polling, result fetch, VM release and the results-branch push to a
local bare "origin". A second run drops the live job connection so the launcher
must poll the remote status file.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests._mini_release import make_release

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(shutil.which("git") is None or shutil.which("bash") is None,
                                reason="needs git and bash")
pytest.importorskip("PIL")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args, cwd):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout


def build_world(tmp_path):
    repo = tmp_path / "repo"
    listed = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=ROOT, check=True,
                            capture_output=True).stdout.decode().split("\0")
    for rel in filter(None, listed):
        source = ROOT / rel
        if source.is_file():
            target = repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    data_parent = tmp_path / "payload"
    make_release(data_parent)
    ledger = [{"path": rel, "bytes": (data_parent / rel).stat().st_size, "sha256": sha(data_parent / rel)}
              for rel in ["data/portable_release/manifest.json", "data/project3_audit/intergps_annotations.jsonl"]]
    (repo / "migration_manifest.json").write_text(json.dumps({"files": ledger}), encoding="utf-8")
    git("init", "-q", cwd=repo)
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "test world", cwd=repo)
    origin = tmp_path / "origin.git"
    git("init", "-q", "--bare", str(origin), cwd=tmp_path)
    git("remote", "add", "origin", str(origin), cwd=repo)
    stub_root = tmp_path / "stub"
    stub_root.mkdir()
    wrapper = tmp_path / "bin" / "colab"
    wrapper.parent.mkdir()
    wrapper.write_text("#!/bin/sh\nexec '%s' '%s' \"$@\"\n" % (sys.executable, ROOT / "tests" / "colab_stub.py"))
    wrapper.chmod(0o755)
    env = dict(os.environ, STUB_ROOT=str(stub_root), P3_COLAB_BIN=str(wrapper), P3_PYTHON=sys.executable,
               P3_DATA_ROOT=str(data_parent / "data"), P3_POLL_SECONDS="1", PYTHONPATH="")
    env.pop("P3_QWEN_PROCESSOR_DIR", None)
    return repo, origin, stub_root, env


def launch(repo, env, *args, timeout=600):
    return subprocess.run(["bash", "colab/launch.sh", *args], cwd=repo, env=env, capture_output=True, text=True,
                          timeout=timeout)


def only_run(repo):
    runs = [p for p in (repo / ".colab_runs").iterdir() if p.is_dir()]
    assert len(runs) == 1, runs
    return runs[0]


def assert_pushed(origin, run_dir):
    run_id = run_dir.name
    branch = "results/" + run_id
    names = subprocess.run(["git", "--git-dir", str(origin), "ls-tree", "-r", "--name-only", branch], check=True,
                           capture_output=True, text=True).stdout.splitlines()
    day = run_id.split("-")[1][:8]
    prefix = "reports/colab_runs_%s/%s/" % (day, run_id)
    for name in ["summary.md", "summary.json", "status.json", "frozen_runtime.json", "pack_verification.json",
                 "calibration/calibration.json", "logs/pytest.log", "_local/launch.log"]:
        assert prefix + name in names, (name, names[:40])
    summary = json.loads(subprocess.run(["git", "--git-dir", str(origin), "show", "%s:%ssummary.json" % (branch, prefix)],
                                        check=True, capture_output=True, text=True).stdout)
    return summary


def test_dry_run_preflight_end_to_end(tmp_path):
    repo, origin, stub_root, env = build_world(tmp_path)
    result = launch(repo, env, "preflight", "--dry-run")
    assert result.returncode == 0, result.stderr[-4000:] + result.stdout[-2000:]
    run_dir = only_run(repo)
    assert (run_dir / "state").read_text().strip() == "pushed"
    summary = assert_pushed(origin, run_dir)
    assert summary["overall"] == "passed"
    assert [s["state"] for s in summary["steps"]] == ["passed"] * len(summary["steps"])
    assert {c["check"]: c["ok"] for c in summary["checks"]}["私有数据与锚点一致"] is True
    assert not any((stub_root / "sessions").iterdir())  # the VM was released
    calls = (stub_root / "calls.log").read_text()
    assert "new -s" in calls and "stop -s" in calls and "--gpu A100" in calls


def test_dropped_connection_falls_back_to_polling(tmp_path):
    repo, origin, stub_root, env = build_world(tmp_path)
    env["STUB_DROP_JOB"] = "1"
    result = launch(repo, env, "preflight", "--dry-run", "--no-vllm")
    assert result.returncode == 0, result.stderr[-4000:]
    assert "polling the VM" in result.stderr
    summary = assert_pushed(origin, only_run(repo))
    assert summary["overall"] == "passed"


def test_uncommitted_code_is_refused_without_allow_dirty(tmp_path):
    repo, _, stub_root, env = build_world(tmp_path)
    (repo / "src" / "rewards" / "claims.py").write_text("# local edit\n", encoding="utf-8")
    result = launch(repo, env, "preflight", "--dry-run")
    assert result.returncode != 0 and "uncommitted changes" in result.stderr
    assert not (stub_root / "calls.log").exists() or "new -s" not in (stub_root / "calls.log").read_text()
