import os
import sys
from pathlib import Path

import pytest

from scripts.colab import drive

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def fake_rclone(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    wrapper = bin_dir / "rclone"
    wrapper.write_text("#!/bin/sh\nexec '%s' '%s' \"$@\"\n" % (sys.executable, ROOT / "tests" / "rclone_stub.py"))
    wrapper.chmod(0o755)
    drive_root = tmp_path / "drive"
    drive_root.mkdir()
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("FAKE_DRIVE_ROOT", str(drive_root))
    return drive_root


def test_detect_without_rclone_is_not_usable(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))  # no rclone anywhere
    info = drive.detect(mount=str(tmp_path / "no_mount"))
    assert not info["usable"] and info["method"] is None and info["notes"]


def test_detect_and_probe_with_rclone(fake_rclone, tmp_path):
    info = drive.detect(mount=str(tmp_path / "no_mount"))
    assert info["usable"] and info["method"] == "rclone" and info["remote"] == "mydrive:"
    result = drive.probe("run-1", tmp_path / "scratch", mount=str(tmp_path / "no_mount"), size_mb=1)
    assert result["ok"], result
    assert result["steps"]["download_blob"]["md5_matches"] and result["steps"]["rclone_check"]["identical"]
    probe_dir = fake_rclone / drive.DEFAULT_DIR / "_p3_probe" / "run-1"
    assert not probe_dir.exists()  # only the probe's own files were created and then removed
    assert set(result["deleted_probe_files"]) == {"probe.txt", "probe.bin"}


def test_config_of_a_running_rclone_mount_is_used(fake_rclone, tmp_path, monkeypatch):
    proc = tmp_path / "proc"
    for pid, argv in [("17", [b"python3", b"-m", b"mount"]),  # not rclone
                      ("42", [b"/usr/bin/rclone", b"mount", b"mydrive:", b"/content/mydrive", b"--config",
                              b"/content/rc/rclone.conf", b"--daemon"])]:
        (proc / pid).mkdir(parents=True)
        (proc / pid / "cmdline").write_bytes(b"\0".join(argv) + b"\0")
    assert drive.mount_process_config(proc) == "/content/rc/rclone.conf"
    monkeypatch.setenv("FAKE_RCLONE_CONFIG", "/content/rc/rclone.conf")
    info = drive.detect(mount=str(tmp_path / "no_mount"), proc_root=proc)
    assert info["usable"] and info["config"] == "/content/rc/rclone.conf"
    assert drive.rclone_cmd(info, "lsf", "mydrive:")[-2:] == ["--config", "/content/rc/rclone.conf"]
    assert not drive.detect(mount=str(tmp_path / "no_mount"), proc_root=tmp_path / "empty")["usable"]


def test_probe_reports_mount_visibility(fake_rclone, tmp_path):
    mount = fake_rclone  # the fake mount writes straight into the fake remote, i.e. "uploads" instantly
    (mount / "existing.txt").write_text("user file")
    result = drive.probe("run-2", tmp_path / "scratch", mount=str(mount), size_mb=1)
    assert result["ok"] and result["steps"]["mount_write"]["visible_on_remote"]
    assert (mount / "existing.txt").read_text() == "user file"  # unrelated files are never touched


def test_persist_copies_and_verifies(fake_rclone, tmp_path, monkeypatch):
    src = tmp_path / "run"
    (src / "final").mkdir(parents=True)
    (src / "final" / "adapter_model.safetensors").write_bytes(b"w" * 1000)
    (src / "summary.json").write_text("{}")
    result = drive.persist(src, "runs/run-3", mount=str(tmp_path / "no_mount"))
    assert result["ok"] and result["verified"] and result["files"] == 2
    assert (fake_rclone / drive.DEFAULT_DIR / "runs/run-3/final/adapter_model.safetensors").read_bytes() == b"w" * 1000
    monkeypatch.setenv("FAKE_DRIVE_CORRUPT", "1")
    broken = drive.persist(src, "runs/run-4", mount=str(tmp_path / "no_mount"))
    assert not broken["ok"] and broken["check_rc"] != 0  # an incomplete upload is never reported as persisted


def _job(tmp_path, mode):
    from scripts.colab.runner import Job

    request = {"run_id": "preflight-20261109T000000Z-abcd", "task": "preflight", "part_bytes": 64 * 1024,
               "options": {"drive_persist": mode, "drive_mount": str(tmp_path / "no_mount")}}
    job = Job(tmp_path / "vm", request)
    (job.out / "summary.json").write_text("{}")
    (job.out / "final").mkdir()
    (job.out / "final" / "adapter_model.safetensors").write_bytes(b"w" * 100)
    job.status["overall"] = "passed"
    return job


def test_runner_copies_the_results_archive_to_drive(fake_rclone, tmp_path):
    job = _job(tmp_path, "results")
    package = job.package()
    summary = job.persist_to_drive(package)
    assert summary["ok"] and summary["verified"] and summary["attempted"] and summary["mode"] == "results"
    remote = fake_rclone / drive.DEFAULT_DIR / "runs" / job.run_id
    assert sorted(p.name for p in remote.iterdir()) == sorted([package["name"], "package.json"])
    assert (remote / package["name"]).read_bytes() == (job.root / "out" / package["name"]).read_bytes()
    assert not (job.root / "out" / (job.run_id + ".drive")).exists()  # staging removed
    assert all(p["bytes"] <= 64 * 1024 for p in package["parts"])  # result parts follow the request's part size


def test_runner_drive_copy_never_fails_the_job(fake_rclone, tmp_path, monkeypatch):
    job = _job(tmp_path, "full")
    monkeypatch.setenv("FAKE_DRIVE_CORRUPT", "1")
    summary = job.persist_to_drive(job.package())
    assert summary["attempted"] and not summary["ok"] and "check" in summary["reason"]
    broken = _job(tmp_path / "broken", "results").persist_to_drive({"name": "missing.results.tar.gz"})
    assert broken["attempted"] and not broken["ok"] and "FileNotFoundError" in broken["reason"]  # caught, not raised
    off = _job(tmp_path / "off", "none").persist_to_drive({"name": "x"})
    assert off == {"mode": "none", "ok": False, "attempted": False, "reason": "not requested for this run"}
