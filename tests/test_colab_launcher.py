"""End-to-end tests of colab/launch.sh against a stub `colab` CLI (no network, no GPU).

A throwaway copy of this repository (with a mini data payload and a matching
ledger) runs `launch.sh preflight --dry-run`: pack, upload, remote verification
of every uploaded part, kernel bootstrap, job steps, polling, result fetch, VM
release and the results-branch push to a local bare "origin". Further runs
inject faults: a dropped job connection, failed and corrupted uploads, a code
tarball "from GitHub" (a file:// URL), a tampered tarball that must fall back to
uploading the code, and the Drive check with a fake rclone.
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from tests._mini_release import make_release

ROOT = Path(__file__).resolve().parents[1]


def _is_git_work_tree():
    if shutil.which("git") is None:
        return False
    probe = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT, capture_output=True, text=True)
    return probe.returncode == 0 and probe.stdout.strip() == "true"


# On the Colab VM the code arrives without .git, so the world-building step cannot run there.
pytestmark = pytest.mark.skipif(shutil.which("bash") is None or not _is_git_work_tree(),
                                reason="needs bash and a git work tree of this repository")
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
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    wrapper = bin_dir / "colab"
    wrapper.write_text("#!/bin/sh\nexec '%s' '%s' \"$@\"\n" % (sys.executable, ROOT / "tests" / "colab_stub.py"))
    wrapper.chmod(0o755)
    env = dict(os.environ, STUB_ROOT=str(stub_root), P3_COLAB_BIN=str(wrapper), P3_PYTHON=sys.executable,
               P3_DATA_ROOT=str(data_parent / "data"), P3_POLL_SECONDS="1", P3_UPLOAD_BACKOFF="0", PYTHONPATH="",
               # never let a real rclone remote of the developer be used by these tests
               P3_DRIVE_REMOTE="p3-test-no-such-remote:")
    for name in ["P3_QWEN_PROCESSOR_DIR", "P3_DRIVE_MOUNT_CMD", "P3_DRIVE_SETUP_FILE", "P3_CODE_SOURCE",
                 "P3_CODE_TARBALL_URL", "P3_PART_MB", "P3_GPU", "P3_DRIVE_DIR", "P3_DRIVE_MOUNT"]:
        env.pop(name, None)
    return repo, origin, stub_root, env


def publish(repo, tmp_path, tamper=None):
    """Push HEAD to the bare origin and serve a codeload-style tarball of it from a file:// URL."""
    git("push", "-q", "origin", "HEAD:refs/heads/master", cwd=repo)
    commit = git("rev-parse", "HEAD", cwd=repo).strip()
    raw = subprocess.run(["git", "archive", "--format=tar", "--prefix=repo-%s/" % commit, commit], cwd=repo, check=True,
                         capture_output=True).stdout
    served = tmp_path / "codeload"
    served.mkdir(exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(raw)) as source, tarfile.open(served / ("%s.tar.gz" % commit), "w:gz") as out:
        for member in source.getmembers():
            data = source.extractfile(member).read() if member.isfile() else None
            if data is not None and tamper and member.name.endswith(tamper):
                data += b"\n# tampered\n"
                member.size = len(data)
            out.addfile(member, io.BytesIO(data) if data is not None else None)
    return "file://%s/{commit}.tar.gz" % served


def launch(repo, env, *args, timeout=600):
    return subprocess.run(["bash", "colab/launch.sh", *args], cwd=repo, env=env, capture_output=True, text=True,
                          timeout=timeout)


def only_run(repo):
    runs = [p for p in (repo / ".colab_runs").iterdir() if p.is_dir()]
    assert len(runs) == 1, runs
    return runs[0]


def branch_files(origin, run_dir):
    run_id = run_dir.name
    names = subprocess.run(["git", "--git-dir", str(origin), "ls-tree", "-r", "--name-only", "results/" + run_id],
                           check=True, capture_output=True, text=True).stdout.splitlines()
    prefix = "reports/colab_runs_%s/%s/" % (run_id.split("-")[-2][:8], run_id)
    return prefix, [n[len(prefix):] for n in names if n.startswith(prefix)]


def show(origin, run_dir, rel):
    prefix, _ = branch_files(origin, run_dir)
    return subprocess.run(["git", "--git-dir", str(origin), "show", "results/%s:%s%s" % (run_dir.name, prefix, rel)],
                          check=True, capture_output=True, text=True).stdout


def assert_pushed(origin, run_dir, expected=("summary.md", "summary.json", "status.json", "frozen_runtime.json",
                                             "pack_verification.json", "calibration/calibration.json",
                                             "logs/pytest.log", "_local/launch.log", "_local/upload.log")):
    _, names = branch_files(origin, run_dir)
    for name in expected:
        assert name in names, (name, names[:60])
    return json.loads(show(origin, run_dir, "summary.json"))


def uploads(stub_root):
    return [line.split()[-1] for line in (stub_root / "calls.log").read_text().splitlines() if line.startswith("upload ")]


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
    # origin is not GitHub here, so the code is uploaded in parts and verified on the VM before use
    assert any("/inbox/code_" in name for name in uploads(stub_root))
    assert "all uploaded parts verified on the VM" in result.stderr
    bootstrap = json.loads(show(origin, run_dir, "bootstrap.json"))
    assert bootstrap["code_source"] == "upload"
    # Drive is optional: not configured here, so it is probed, reported and skipped without failing anything
    assert "drive_probe" in [s["name"] for s in summary["steps"]]
    assert "## Google Drive" in show(origin, run_dir, "summary.md")
    done = json.loads((run_dir / "done.json").read_text())
    assert done["drive"]["mode"] == "results" and done["drive"]["attempted"] is False
    # results come back in parts no larger than the request's part size
    assert all(p["bytes"] <= 2 * 1024 * 1024 for p in done["package"]["parts"])


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


def test_github_code_and_upload_faults_are_repaired(tmp_path):
    """Published commit: the VM fetches the code itself; failed and corrupted uploads are retried and repaired."""
    repo, origin, stub_root, env = build_world(tmp_path)
    hang = shutil.which("timeout") is not None  # the per-call time limit needs coreutils `timeout`
    env.update(P3_CODE_TARBALL_URL=publish(repo, tmp_path), STUB_HANG_UPLOADS="1" if hang else "0",
               P3_UPLOAD_TIMEOUT="3", STUB_FAIL_UPLOADS="2", STUB_CORRUPT_UPLOAD="p3_private", P3_PART_MB="0.0625")
    result = launch(repo, env, "preflight", "--dry-run", "--no-vllm")
    assert result.returncode == 0, result.stderr[-4000:]
    assert "downloads commit" in result.stderr
    assert not any("/inbox/code_" in name for name in uploads(stub_root))  # no code upload at all
    if hang:  # the stalled call was ended by the time limit and retried
        assert re.search(r"failed \(attempt 1/6 after [34]s\)", result.stderr), result.stderr[-3000:]
    assert "failed (attempt %d/6" % (3 if hang else 2) in result.stderr
    assert "re-uploading 1 part(s) that are missing or damaged" in result.stderr
    run_dir = only_run(repo)
    summary = assert_pushed(origin, run_dir)
    assert summary["overall"] == "passed"
    assert json.loads(show(origin, run_dir, "bootstrap.json"))["code_source"] == "github"
    # the stub's failure message carries a proxy token in its URL, like the real CLI; it must never be published
    assert "SECRET-PROXY-TOKEN-123" in (run_dir / "upload.log").read_text()  # the local log keeps the raw output
    for rel in ["_local/upload.log", "_local/launch.log"]:
        published = show(origin, run_dir, rel)
        assert "SECRET-PROXY-TOKEN-123" not in published
    assert "colab-runtime-proxy-token=REDACTED" in show(origin, run_dir, "_local/upload.log")
    assert "_local/REDACTIONS.txt" in branch_files(origin, run_dir)[1]


def test_tampered_github_tarball_falls_back_to_uploaded_code(tmp_path):
    repo, origin, stub_root, env = build_world(tmp_path)
    env["P3_CODE_TARBALL_URL"] = publish(repo, tmp_path, tamper="scripts/colab/runner.py")
    result = launch(repo, env, "preflight", "--dry-run", "--no-vllm")
    assert result.returncode == 0, result.stderr[-4000:]
    assert "does not match the commit" in result.stdout
    assert "uploading the code archive instead" in result.stderr
    assert any("/inbox/code_" in name for name in uploads(stub_root))
    run_dir = only_run(repo)
    assert assert_pushed(origin, run_dir)["overall"] == "passed"
    assert json.loads(show(origin, run_dir, "bootstrap.json"))["code_source"] == "upload"


def test_drive_check_on_a_cpu_vm_with_fake_rclone(tmp_path):
    repo, origin, stub_root, env = build_world(tmp_path)
    fake_bin = tmp_path / "fake_rclone_bin"
    fake_bin.mkdir()
    rclone = fake_bin / "rclone"
    rclone.write_text("#!/bin/sh\nexec '%s' '%s' \"$@\"\n" % (sys.executable, ROOT / "tests" / "rclone_stub.py"))
    rclone.chmod(0o755)
    drive_root = tmp_path / "drive"
    (drive_root / "ColabProjects").mkdir(parents=True)
    (drive_root / "ColabProjects" / "keep.txt").write_text("user file")
    env.update(PATH=str(fake_bin) + os.pathsep + env["PATH"], FAKE_DRIVE_ROOT=str(drive_root),
               P3_DRIVE_REMOTE="mydrive:", P3_DRIVE_MOUNT=str(tmp_path / "no_mount"),
               P3_DRIVE_MOUNT_CMD='echo "hook for {session} with token=HOOK-SECRET"; echo "$P3_SESSION" > "%s"'
                                  % (tmp_path / "hook_session.txt"))
    result = launch(repo, env, "drive-check")
    assert result.returncode == 0, result.stderr[-4000:] + result.stdout[-2000:]
    calls = (stub_root / "calls.log").read_text()
    assert "--gpu" not in calls  # a CPU VM
    assert not any("p3_private" in name for name in uploads(stub_root))  # no private data for this task
    run_dir = only_run(repo)
    session = (run_dir / "session").read_text().strip()
    assert (tmp_path / "hook_session.txt").read_text().strip() == session
    assert "HOOK-SECRET" in (run_dir / "drive_mount.log").read_text()
    summary = assert_pushed(origin, run_dir, expected=("summary.md", "summary.json", "drive_probe.json",
                                                      "_local/launch.log"))
    assert summary["overall"] == "passed"
    assert {c["check"]: c["ok"] for c in summary["checks"]} == {"Drive 写入、读回、哈希校验、删除全部成功": True}
    _, names = branch_files(origin, run_dir)
    assert "_local/drive_mount.log" not in names  # hook output never leaves the machine
    assert not any("HOOK-SECRET" in show(origin, run_dir, n) for n in names if n.startswith("_local/"))
    leftovers = sorted(str(p.relative_to(drive_root)) for p in drive_root.rglob("*"))
    assert leftovers == ["ColabProjects", "ColabProjects/keep.txt", "ColabProjects/vlm-perception-reward-rl"]
