"""S4 runner on CPU: Drive state, supervision, the pilot gates and the formal-run job (no model, no GPU).

Training is ``tests/fake_train_rl.py`` (same arguments, files and events as the real entry); Google Drive is
``tests/rclone_stub.py`` on a temporary directory.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.colab import decide_pilot, drive, s4_state, tasks, train_s4
from scripts.colab.common import sha256_file
from scripts.colab.s4_supervise import classify, parse_events

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "configs/experiments/s4_runs_20261110.json"
PY = sys.executable
PROJECT = "ColabProjects/vlm-perception-reward-rl"
EXPERIMENT = "s4/rl_v3_p1_20261110"
FAST = {"step_seconds_p90": 0.001, "step_seconds_median": 0.001, "startup_seconds": 0.5, "final_upload_seconds": 0.5,
        "restore_seconds": 0.5}
FAKE_ENV = ("FAKE_DRIVE_CORRUPT", "FAKE_DRIVE_FAIL", "FAKE_TRAIN_FAIL", "FAKE_TRAIN_FAIL_ONCE", "FAKE_TRAIN_HANG",
            "FAKE_TRAIN_SETUP", "FAKE_TRAIN_FORMAT", "FAKE_TRAIN_IS_RATIO", "FAKE_TRAIN_STEP_SECONDS", "P3_DRIVE_REMOTE",
            "P3_DRIVE_DIR", "P3_DRIVE_MOUNT")


@pytest.fixture()
def fake_drive(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    wrapper = bin_dir / "rclone"
    wrapper.write_text("#!/bin/sh\nexec '%s' '%s' \"$@\"\n" % (PY, ROOT / "tests" / "rclone_stub.py"))
    wrapper.chmod(0o755)
    root = tmp_path / "drive"
    root.mkdir()
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("FAKE_DRIVE_ROOT", str(root))
    for name in FAKE_ENV:
        monkeypatch.delenv(name, raising=False)
    return root / PROJECT


def open_store(tmp_path):
    store, info = s4_state.Store.open(tmp_path / "scratch", mount=str(tmp_path / "no_mount"))
    assert store is not None, info
    return store


def supervise_cli(tmp_path, *args):
    cmd = [PY, "-m", "scripts.colab.s4_supervise", *args, "--repo", str(ROOT), "--job", "pilot-t", "--python", PY,
           "--train-module", "tests.fake_train_rl", "--drive-mount", str(tmp_path / "no_mount")]
    return subprocess.run(cmd, cwd=str(ROOT), env=dict(os.environ), capture_output=True, text=True, timeout=600)


def checkpoint(directory, step, size=3000):
    directory = Path(directory) / ("checkpoint-%d" % step)
    directory.mkdir(parents=True)
    (directory / "adapter_model.safetensors").write_bytes(b"%d" % step * size)
    (directory / "optimizer.pt").write_bytes(b"o" * size)
    (directory / "trainer_state.json").write_text(json.dumps({"global_step": step}))
    return directory


# ---- pure helpers ------------------------------------------------------------------------------------------------

def test_events_behind_tqdm_text_and_failure_classes():
    line = ' 33%|###| 1/3 [00:42<01:24]{"event": "train_log", "step": 1, "loss": 0.03} tail {"event": "x", "a": [1]}'
    assert parse_events(line) == [{"event": "train_log", "step": 1, "loss": 0.03}, {"event": "x", "a": [1]}]
    assert parse_events("no events here") == [] and parse_events('{"event": "cut') == []
    assert classify(1, "Traceback\ntorch.OutOfMemoryError: CUDA out of memory") == ("computation", "out_of_memory")
    assert classify(1, "FloatingPointError: non-finite {'loss': nan}") == ("computation", "non_finite")
    assert classify(1, "ValueError: run does not match its registration (s4): GPU") == ("setup", "registration")
    assert classify(1, "ValueError: Checkpoint identity mismatch in ['source_sha256']") == ("setup", "identity")
    assert classify(-9, "") == ("computation", "killed by signal 9")
    assert s4_state.percentile([5, 1, 3, 2, 4], 0.9) == 5 and s4_state.percentile(list(range(1, 101)), 0.95) == 95


def test_drive_paths_stay_inside_the_project_directory():
    assert drive.check_rel("/s4/x/checkpoint-38/") == "s4/x/checkpoint-38"
    for bad in ["", "/", "../x", "a/../b", "a/./b", "a//b", "a b", "a;b", "a\\b", "mydrive:x"]:
        with pytest.raises(ValueError):
            drive.check_rel(bad)


def test_usage_numbers_and_gpu_name_guard():
    from scripts.colab.bootstrap import gpu_name_problem
    from scripts.colab.local_tools import usage_numbers

    text = "Current balance: 2,386.50 compute units\nUsage rate: 6.73/hr\nActive assignments: 1\n"
    assert usage_numbers(text) == {"balance": 2386.5, "rate": 6.73} and usage_numbers("stub usage") == {}
    assert gpu_name_problem({"name": "NVIDIA A100-SXM4-40GB"}, "NVIDIA A100-SXM4-40GB") is None
    assert "runs only on NVIDIA A100-SXM4-40GB" in gpu_name_problem({"name": "NVIDIA A100-SXM4-80GB"},
                                                                     "NVIDIA A100-SXM4-40GB")
    assert gpu_name_problem({"name": "NVIDIA L4"}, None) is None


def test_deadlines_planner_and_container_start(tmp_path):
    proc = tmp_path / "proc"
    (proc / "1").mkdir(parents=True)
    (proc / "stat").write_text("cpu  1 2 3\nbtime 1000000\n")
    (proc / "1" / "stat").write_text("1 (init) " + " ".join(["S"] + ["0"] * 18 + ["360000"] + ["0"] * 10))
    assert train_s4.container_started_epoch(str(proc)) == pytest.approx(1000000 + 360000 / os.sysconf("SC_CLK_TCK"))
    assert train_s4.container_started_epoch(str(tmp_path / "none")) is None
    finish, stop = train_s4.deadlines(1000.0, max_hours=2, vm_hours=24, container_start=0.0)
    assert stop == 8200.0 and finish == stop - train_s4.PLAN_BEFORE_STOP_SECONDS
    finish, stop = train_s4.deadlines(50000.0, max_hours=None, vm_hours=24, container_start=0.0)
    assert stop == 24 * 3600 - train_s4.STOP_BEFORE_VM_END_SECONDS  # the VM lifetime counts from the container start
    planner = train_s4.Planner({"step_seconds_p90": 50, "startup_seconds": 300, "final_upload_seconds": 100,
                                "restore_seconds": 200})
    assert planner.step_seconds() == pytest.approx(55.0)
    assert planner.seconds(228, resuming=False) == pytest.approx(300 + 228 * 55 + 100 + train_s4.RUN_MARGIN_SECONDS)
    assert planner.seconds(10, resuming=True) - planner.seconds(10, resuming=False) == pytest.approx(200)
    planner.add([80.0] * 10)
    assert planner.step_seconds() == pytest.approx(88.0)  # slower steps measured in the job raise the estimate


def test_formal_runs_need_a_passed_pilot_with_the_same_registry_runtime_and_code():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    sha = "r" * 64
    good = {"passed": True, "job": "pilot-1", "registry_sha256": sha, "source_sha256": {"src/a.py": "1"},
            "runtime_content_sha256": reg["runtime"]["content_sha256"], "versions": {"trl": "1.17.1"}}
    now = {"source_sha256": {"src/a.py": "1"}, "versions": {"trl": "1.17.1"}}
    problems = train_s4.gate_problems
    assert problems(good, "ok", reg, sha, now, None) == []
    assert "run `bash colab/launch.sh pilot` first" in problems(None, "missing", reg, sha, now, None)[0]
    assert any("did not pass" in p for p in problems(dict(good, passed=False), "ok", reg, sha, now, None))
    assert any("registry differs" in p for p in problems(good, "ok", reg, "x" * 64, now, None))
    assert any("frozen runtime differs" in p for p in problems(dict(good, runtime_content_sha256="y"), "ok", reg, sha,
                                                               now, None))
    changed = problems(good, "ok", reg, sha, dict(now, source_sha256={"src/a.py": "2"}), None)
    assert any("code freeze" in p and "src/a.py" in p for p in changed)
    assert any("package versions" in p for p in problems(good, "ok", reg, sha, dict(now, versions={"trl": "2"}), None))
    assert any("could not compute" in p for p in problems(good, "ok", reg, sha, None, "ImportError"))


def test_pilot_and_train_task_steps(tmp_path):
    request = {"run_id": "pilot-x", "task": "pilot", "options": {"drive_remote": "mydrive:", "drive_dir": "D",
                                                                 "drive_mount": "/content/mydrive", "session": "p3"}}
    bootstrap = {"envs": {"base": {"python": "/env/bin/python"}}, "model": {"local_dir": "/models/q"}}
    steps = tasks.steps_for(tasks.Context(tmp_path, request, bootstrap, kernel_python="/usr/bin/python3"))
    by = {s["name"]: s for s in steps}
    assert [s["name"] for s in steps] == ["env_report", "verify_pack", "pytest", "register_check", "drive_probe", "vllm_env",
                                          "pilot_v5", "pilot_resume", "pilot_rl_ans", "pilot_rl_v4", "pilot_rl_v5_placebo",
                                          "pilot_rl_blind", "pilot_v5_retry", "decide_pilot"]
    assert all(s["required"] for s in steps)  # Drive and vLLM are required here, unlike in preflight and v0
    assert "--drive" in by["pilot_v5"]["cmd"] and by["pilot_v5"]["depends_on"] == ["vllm_env", "drive_probe"]
    assert by["pilot_v5"]["cmd"][by["pilot_v5"]["cmd"].index("--python") + 1].endswith("env/vllm/bin/python")
    assert by["pilot_v5_retry"]["depends_on"] == ["vllm_env", "pilot_v5"] and "--only-if-g4-failed" in by["pilot_v5_retry"]["cmd"]
    assert by["decide_pilot"]["depends_on"] == [] and "D" in by["decide_pilot"]["cmd"]  # decided whatever the runs did
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert [r["arm"] for r in reg["pilot"]["arm_runs"]] == tasks.PILOT_ARMS
    dry = tasks.steps_for(tasks.Context(tmp_path, dict(request, options={"dry_run": True}), bootstrap, "/usr/bin/python3"))
    assert [s["name"] for s in dry] == ["env_report", "verify_pack", "pytest", "decide_pilot"]
    train = dict(request, run_id="train-x", task="train", options=dict(request["options"], max_hours=10.0, vm_hours=24.0,
                                                                         cu_balance=2386.5, cu_rate=6.73,
                                                                         cu_measured_epoch=1.0))
    steps = tasks.steps_for(tasks.Context(tmp_path, train, bootstrap, "/usr/bin/python3"))
    assert [s["name"] for s in steps] == ["env_report", "verify_pack", "register_check", "drive_probe", "vllm_env",
                                          "train_runs"]
    cmd = steps[-1]["cmd"]
    for flag, value in [("--session", "p3"), ("--max-hours", "10.0"), ("--cu-balance", "2386.5"), ("--cu-rate", "6.73"),
                        ("--model-path", "/models/q")]:
        assert cmd[cmd.index(flag) + 1] == value
    assert steps[-1]["timeout"] > 23 * 3600
    dry = tasks.steps_for(tasks.Context(tmp_path, dict(train, options=dict(train["options"], dry_run=True)), bootstrap,
                                        "/usr/bin/python3"))
    assert [s["name"] for s in dry] == ["env_report", "verify_pack", "train_runs"] and "--dry-run" in dry[-1]["cmd"]


# ---- Drive state ---------------------------------------------------------------------------------------------------

def test_restore_checks_every_file_against_the_marker(fake_drive, tmp_path):
    store = open_store(tmp_path)
    local = tmp_path / "local"
    ckpt = checkpoint(local, 38)
    (local / "rollouts.jsonl").write_text("".join(json.dumps({"global_step": s}) + "\n" for s in range(40)) + '{"glob')
    run = s4_state.RunDrive(store, "s4/test/rl_v5/seed1", {"config_sha256": "a"}, "job1", "rl_v5/seed1")
    uploaded = run.upload_checkpoint(ckpt, 38, rollouts=local / "rollouts.jsonl")
    assert uploaded["ok"], uploaded
    marker_path = fake_drive / "s4/test/rl_v5/seed1/checkpoint-38" / s4_state.VERIFIED
    marker = json.loads(marker_path.read_text())
    assert marker["files"] == s4_state.file_table(ckpt) and marker["rollouts"]["lines"] == 40  # half a line left out
    step, found = run.latest_verified()
    assert step == 38 and found == marker
    restored = run.restore(38, marker, tmp_path / "again")
    assert restored["ok"] and restored["rollouts_kept"] == 38 and restored["rollouts_dropped_after_checkpoint"] == 2
    assert s4_state.file_table(tmp_path / "again" / "checkpoint-38") == marker["files"]
    assert "not empty" in run.restore(38, marker, tmp_path / "again")["reason"]
    (fake_drive / "s4/test/rl_v5/seed1/checkpoint-38/optimizer.pt").write_bytes(b"damaged")
    damaged = run.restore(38, marker, tmp_path / "third")
    assert not damaged["ok"] and "differ from the marker" in damaged["reason"] and "optimizer.pt" in damaged["reason"]
    assert not (tmp_path / "third").exists()  # nothing half-restored is left behind
    other = s4_state.RunDrive(store, "s4/test/rl_v5/seed1", {"config_sha256": "b"}, "job2", "rl_v5/seed1")
    assert other.latest_verified() == (None, "no verified checkpoint")  # another configuration is never resumed


def test_upload_failures_are_reported_and_never_marked_verified(fake_drive, tmp_path, monkeypatch):
    store = open_store(tmp_path)
    ckpt = checkpoint(tmp_path / "local", 38)
    run = s4_state.RunDrive(store, "s4/test/rl_v4/seed1", {"config_sha256": "a"}, "job1", "rl_v4/seed1")
    monkeypatch.setenv("FAKE_DRIVE_CORRUPT", "1")
    corrupt = run.upload_checkpoint(ckpt, 38)
    assert not corrupt["ok"] and "rclone check" in corrupt["reason"]
    assert not (fake_drive / "s4/test/rl_v4/seed1/checkpoint-38" / s4_state.VERIFIED).exists()
    monkeypatch.setenv("FAKE_DRIVE_CORRUPT", "0")
    monkeypatch.setenv("FAKE_DRIVE_FAIL", "copy")
    failed = run.upload_checkpoint(ckpt, 38)
    assert not failed["ok"] and "rclone copy failed" in failed["reason"]
    assert run.latest_verified() == (None, "no verified checkpoint")
    lost = s4_state.RunDrive(store, "s4/test/rl_v4/seed1", {"config_sha256": "a"}, "job1", "x", guard=lambda: False)
    assert "another job holds this run" in lost.upload_checkpoint(ckpt, 38)["reason"] and lost.lost_claim


def test_retention_keeps_the_newest_and_leaves_other_configurations_alone(fake_drive, tmp_path):
    store = open_store(tmp_path)
    rel = "s4/test/rl_ans/seed2"
    a = s4_state.RunDrive(store, rel, {"config_sha256": "a"}, "job1", "rl_ans/seed2")
    assert a.upload_checkpoint(checkpoint(tmp_path / "a", 38), 38)["ok"]
    b = s4_state.RunDrive(store, rel, {"config_sha256": "b"}, "job2", "rl_ans/seed2")
    first = b.upload_checkpoint(checkpoint(tmp_path / "b", 76), 76)
    assert first["ok"] and first["retained"]["left_alone"] == [38] and first["retained"]["purged"] == []
    c = s4_state.RunDrive(store, rel, {"config_sha256": "b"}, "job3", "rl_ans/seed2")
    second = c.upload_checkpoint(checkpoint(tmp_path / "c", 114), 114)
    assert second["retained"]["purged"] == [76] and second["retained"]["left_alone"] == [38]
    names = sorted(p.name for p in (fake_drive / rel).iterdir())
    assert names == ["checkpoint-114", "checkpoint-38"]
    assert a.latest_verified()[0] == 38 and c.latest_verified()[0] == 114


def test_claims_earliest_live_claim_wins(fake_drive, tmp_path):
    store = open_store(tmp_path)
    rel = "s4/test/rl_v5/seed3"
    claims = fake_drive / rel / "claims"
    one = s4_state.Claim(store, rel, "job1", "p3", settle=0)
    assert one.acquire() == (True, None)
    two = s4_state.Claim(store, rel, "job2", "p3b", settle=0)
    held, why = two.acquire()
    assert not held and "job1" in why and not (claims / "job2.json").exists()  # a lost claim is withdrawn
    three = s4_state.Claim(store, rel, "job3", "p3", settle=0)
    assert three.acquire() == (True, None)  # job1 ran on session p3, which runs one kernel job at a time: job1 is dead
    three.release()
    doc = json.loads((claims / "job1.json").read_text())
    doc["heartbeat_epoch"] -= 2 * s4_state.CLAIM_TTL_SECONDS
    (claims / "job1.json").write_text(json.dumps(doc))
    assert two.acquire() == (True, None)  # no heartbeat for longer than the TTL: job1 is dead for everyone
    live = s4_state.live_claims([{"job": "a", "session": "s", "heartbeat_epoch": 100.0, "claimed_epoch": 5.0},
                                 {"job": "b", "session": "t", "heartbeat_epoch": 100.0, "claimed_epoch": 5.0}],
                                now=200.0, session="u", own_job="c")
    assert s4_state.winner(live)["job"] == "a"  # ties go to the smaller job id


def test_run_status_states(fake_drive, tmp_path):
    store = open_store(tmp_path)
    rel, key = "s4/test/rl_blind/seed1", {"config_sha256": "a", "runtime_content_sha256": "r"}
    assert s4_state.run_status(store, rel, key)["state"] == "new"
    assert store.put_json(rel + "/" + s4_state.STARTED, {"key": key})["ok"]
    assert s4_state.run_status(store, rel, key)["state"] == "started"
    assert store.put_json(rel + "/" + s4_state.COMPLETED, {"key": key, "global_step": 228})["ok"]
    assert s4_state.run_status(store, rel, key)["state"] == "completed"
    assert store.put_json(rel + "/" + s4_state.COMPLETED, {"key": dict(key, config_sha256="z")})["ok"]
    status = s4_state.run_status(store, rel, key)
    assert status["state"] == "foreign" and "another key" in status["reason"]
    assert (store.about() or {}).get("free")


# ---- pilot --------------------------------------------------------------------------------------------------------

def test_pilot_run_verifies_every_checkpoint_and_keeps_the_newest(fake_drive, tmp_path):
    out = tmp_path / "out" / "pilot_v5"
    result = supervise_cli(tmp_path, "pilot-run", "--kind", "learning_run", "--name", "pilot_v5", "--out", str(out),
                           "--drive")
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    record = json.loads((out / "supervisor.json").read_text())
    assert record["outcome"] == "completed" and record["checkpoints_saved"] == [20, 40]
    assert [(u["step"], u["ok"]) for u in record["uploads"]] == [(20, True), (40, True)]
    assert record["uploads"][1]["retained"]["purged"] == [20]
    assert "[pilot_v5] step 40/40" in result.stdout and "checkpoint-40 on Drive: verified" in result.stdout
    run = fake_drive / EXPERIMENT / "pilot" / "pilot-t" / "pilot_v5"
    assert sorted(p.name for p in run.iterdir() if p.is_dir()) == ["checkpoint-40", "final"]
    marker = json.loads((run / "checkpoint-40" / s4_state.VERIFIED).read_text())
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert marker["step"] == 40 and marker["key"]["runtime_content_sha256"] == reg["runtime"]["content_sha256"]
    assert marker["files"] == s4_state.file_table(out / "checkpoint-40") and marker["rollouts"]["lines"] == 80
    completed = json.loads((run / s4_state.COMPLETED).read_text())
    assert completed["global_step"] == 40 and completed["key"] == marker["key"]
    assert (run / "final/adapter_model.safetensors").read_bytes() == (out / "final/adapter_model.safetensors").read_bytes()


def test_pilot_resume_restores_checkpoint_one_from_drive(fake_drive, tmp_path):
    out = tmp_path / "out" / "pilot_resume"
    result = supervise_cli(tmp_path, "pilot-resume", "--name", "pilot_resume", "--out", str(out))
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    record = json.loads((tmp_path / "out" / "pilot_resume.supervisor.json").read_text())
    assert record["ok"] and record["latest_verified"] == 1, record.get("reason")
    leg_a, leg_b = record["legs"]["a"], record["legs"]["b"]
    assert leg_a["outcome"] == "interrupted" and "checkpoint-1" in leg_a["detail"]
    assert [(u["step"], u["ok"]) for u in leg_a["uploads"]] == [(1, True)]
    assert record["restore"]["ok"] and record["restore"]["rollouts_kept"] == 2
    assert leg_b["outcome"] == "completed" and leg_b["train_done"]["global_step"] == 2
    assert (tmp_path / "out" / "pilot_resume.leg_a" / "checkpoint-1").is_dir()  # set aside, not deleted
    rows = [json.loads(x) for x in (out / "rollouts.jsonl").read_text().splitlines()]
    assert sorted({r["global_step"] for r in rows}) == [0, 1] and len(rows) == 4  # each step exactly once
    run = fake_drive / EXPERIMENT / "pilot" / "pilot-t" / "pilot_resume"
    assert sorted(p.name for p in run.iterdir() if p.is_dir()) == ["checkpoint-2", "final"]


def test_pilot_gates_from_the_pilot_runs(fake_drive, tmp_path):
    out = tmp_path / "out"
    runs = [("pilot-run", "--kind", "learning_run", "--name", "pilot_v5", "--out", str(out / "pilot_v5"), "--drive"),
            ("pilot-resume", "--name", "pilot_resume", "--out", str(out / "pilot_resume"))]
    runs += [("pilot-run", "--kind", "arm_runs", "--index", str(i), "--name", "pilot_" + arm, "--out",
              str(out / ("pilot_" + arm))) for i, arm in enumerate(tasks.PILOT_ARMS)]
    runs.append(("pilot-run", "--kind", "learning_retry", "--name", "pilot_v5_retry", "--out", str(out / "pilot_v5_retry"),
                 "--only-if-g4-failed", str(out / "pilot_v5")))
    for args in runs:
        result = supervise_cli(tmp_path, *args)
        assert result.returncode == 0, (args, result.stdout[-2000:], result.stderr[-2000:])
    assert json.loads((out / "pilot_v5_retry" / "supervisor.json").read_text())["skipped"] is True  # G4 passed
    code = decide_pilot.main(["--out-dir", str(out), "--repo", str(ROOT), "--job", "pilot-t", "--python", PY,
                              "--drive-mount", str(tmp_path / "no_mount")])
    gates = json.loads((out / "pilot_gates.json").read_text())
    assert code == 0 and gates["passed"], {k: v["ok"] for k, v in gates["gates"].items()}
    assert gates["consistency"]["one_source"] and gates["code_now"]["matches_pilot"]
    latest = json.loads((fake_drive / EXPERIMENT / "PILOT_LATEST.json").read_text())
    assert latest["passed"] and latest["registry_sha256"] == sha256_file(REGISTRY)
    assert latest["timing"]["step_seconds_p90"] is not None and latest["timing"]["checkpoint_upload_seconds"] is not None
    assert (fake_drive / EXPERIMENT / "pilot" / "pilot-t" / "RESULT.json").is_file()
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    history = out / "pilot_v5" / "log_history.json"
    original = history.read_text()
    falling = [dict(h, **{"p3/format_rate": 1 - h["p3/format_rate"]}) if "p3/format_rate" in h else h
               for h in json.loads(original)]
    history.write_text(json.dumps(falling))
    need, why = decide_pilot.retry_needed(out / "pilot_v5", reg, ROOT)
    assert need, why  # G4 failed while G1, G2, G3 and G6 passed: the pre-registered 76-step retry runs
    result, _, _ = decide_pilot.decide(out, ROOT, "pilot-t", PY)
    assert not result["passed"] and not result["gates"]["G4_learning"]["ok"] and result["gates"]["G1_importance_sampling"]["ok"]
    low = [dict(h, **{"sampling/importance_sampling_ratio/mean": 0.5}) if h.get("step") == 7 else h
           for h in json.loads(original)]
    history.write_text(json.dumps(low))
    result, _, _ = decide_pilot.decide(out, ROOT, "pilot-t", PY)
    g1 = result["gates"]["G1_importance_sampling"]
    assert not g1["ok"] and g1["detail"]["pilot_v5"]["failing_steps"] == [7]
    assert not decide_pilot.retry_needed(out / "pilot_v5", reg, ROOT)[0]  # G1 failed too: no retry, the pilot fails
    history.write_text(original)
    shutil.rmtree(str(out / "pilot_rl_blind"))
    result, _, _ = decide_pilot.decide(out, ROOT, "pilot-t", PY)
    assert not result["passed"] and not result["gates"]["G3_stability"]["ok"]  # a missing pilot run fails closed


def test_supervisor_stops_the_training_when_the_claim_is_lost(fake_drive, tmp_path, monkeypatch):
    from scripts.colab import s4_supervise

    monkeypatch.setenv("FAKE_TRAIN_HANG", "rl_v5/2:30")  # still training when the checkpoint-20 upload finds the claim gone
    run_drive = s4_state.RunDrive(open_store(tmp_path), "s4/test/rl_v5/seed2", None, "job1", "rl_v5/seed2",
                                  guard=lambda: False)
    out = tmp_path / "run"
    cmd = [PY, "-m", "tests.fake_train_rl", "--arm", "rl_v5", "--seed", "2", "--smoke", "max_steps=40,save_steps=20",
           "--output-dir", str(out)]
    record = s4_supervise.supervise("rl_v5/seed2", cmd, out, out / "train.log", ROOT, env=dict(os.environ),
                                    run_drive=run_drive, key_extra={"runtime_content_sha256": "r"}, poll=0.2)
    assert record["outcome"] == "interrupted" and "lost claim" in record["detail"], record
    assert [(u["step"], u["ok"]) for u in record["uploads"]] == [(20, False)]
    assert not (fake_drive / "s4/test/rl_v5/seed2").exists()  # nothing was written for a run another job holds


# ---- formal runs ---------------------------------------------------------------------------------------------------

def repo_copy(tmp_path, cutoff="2099-01-01T00:00:00Z"):
    """train_s4 links <repo>/runs to <root>/runs: give it a copy of the code, never the working tree. The copy's
    no-new-run cutoff is moved so the tests do not depend on today's date (one test sets it into the past)."""
    copy = tmp_path / "repo"
    for name in ("src", "scripts", "configs", "tests"):
        shutil.copytree(str(ROOT / name), str(copy / name), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    set_cutoff(copy, cutoff)
    return copy


def set_cutoff(copy, cutoff):
    path = copy / "configs/experiments/s4_runs_20261110.json"
    reg = json.loads(path.read_text(encoding="utf-8"))
    reg["stop_rules"]["no_new_run_after_utc"] = cutoff
    path.write_text(json.dumps(reg, indent=2), encoding="utf-8")


def put_pilot_latest(store, copy, timing=FAST, passed=True):
    current, error = decide_pilot.code_identity(PY, copy)
    assert current, error
    reg = json.loads((copy / "configs/experiments/s4_runs_20261110.json").read_text(encoding="utf-8"))
    latest = {"schema": "p3-pilot-latest-v1", "passed": passed, "job": "pilot-x", "gates": {},
              "registry_sha256": sha256_file(copy / "configs/experiments/s4_runs_20261110.json"),
              "runtime_content_sha256": reg["runtime"]["content_sha256"], "source_sha256": current["source_sha256"],
              "versions": current["versions"], "timing": timing}
    assert store.put_json(EXPERIMENT + "/PILOT_LATEST.json", latest)["ok"]
    return reg


def job(copy, tmp_path, name, *extra):
    args = train_s4.build_parser().parse_args([
        "--repo", str(copy), "--root", str(tmp_path / "vm"), "--out", str(tmp_path / "out" / name), "--job", name,
        "--session", "p3", "--python", PY, "--train-module", "tests.fake_train_rl", "--vm-hours", "0",
        "--drive-mount", str(tmp_path / "no_mount"), *extra])
    code = train_s4.Job(args).run()
    return code, json.loads((tmp_path / "out" / name / "train_job.json").read_text())


@pytest.fixture()
def fast_job(monkeypatch):
    monkeypatch.setattr(train_s4, "RUN_MARGIN_SECONDS", 0)
    monkeypatch.setattr(train_s4, "PLAN_BEFORE_STOP_SECONDS", 0)
    monkeypatch.setattr(train_s4, "MIN_FREE_DISK_GB", 0)
    monkeypatch.setattr(s4_state, "CLAIM_SETTLE_SECONDS", 0)


def test_train_job_order_deadline_resume_restart_and_failure(fake_drive, tmp_path, monkeypatch, fast_job):
    copy = repo_copy(tmp_path)
    put_pilot_latest(open_store(tmp_path), copy)
    base = fake_drive / EXPERIMENT
    # job 1: run 1 completes; run 2 hangs at step 50 and is stopped at the deadline after checkpoint-38 is on Drive.
    # The budget leaves room for run 1 on a busy CPU (every stub rclone call starts a Python process)
    monkeypatch.setenv("FAKE_TRAIN_HANG", "rl_ans/1:50")
    code, record = job(copy, tmp_path, "job1", "--max-hours", str(45 / 3600.0), "--cu-balance", "1000",
                       "--cu-rate", "6.73")
    assert code == 0, record
    assert [(r["run"], r["state"]) for r in record["runs"]] == [("rl_v5/seed1", "completed"), ("rl_ans/seed1", "interrupted")]
    assert record["stop"]["kind"] == "time" and "time budget" in record["runs"][1]["reason"]
    done = base / "rl_v5/seed1"
    assert {s4_state.STARTED, s4_state.COMPLETED, "checkpoint-228", "final", "rollouts.jsonl"} <= {p.name for p in done.iterdir()}
    assert sorted(p.name for p in (base / "rl_ans/seed1").glob("checkpoint-*")) == ["checkpoint-38"]
    assert not list((base / "rl_ans/seed1/claims").glob("*.json")) and (base / "code_baseline/job1.json").is_file()
    assert (copy / "runs").is_symlink() and Path(os.readlink(str(copy / "runs"))) == tmp_path / "vm" / "runs"
    assert (tmp_path / "out/job1/runs/rl_v5_seed1/rollouts.jsonl.gz").is_file()
    # job 2: no new run may start (projected balance below 150 CU); run 2 is resumed, fails once, restarts, completes
    monkeypatch.delenv("FAKE_TRAIN_HANG")
    monkeypatch.setenv("FAKE_TRAIN_FAIL_ONCE", "rl_ans/1:60")
    monkeypatch.setenv("FAKE_TRAIN_STATE_DIR", str(tmp_path / "fake_state"))
    code, record = job(copy, tmp_path, "job2", "--max-hours", "1", "--cu-balance", "100", "--cu-rate", "0")
    assert code == 0, record
    run = record["runs"][0]
    assert run["run"] == "rl_ans/seed1" and run["state"] == "completed" and len(run["attempts"]) == 2
    assert run["attempts"][0]["outcome"] == "computation" and run["attempts"][0]["detail"] == "non_finite"
    assert [a["restore"]["step"] for a in run["attempts"]] == [38, 38] and run["attempts"][0]["set_aside"]
    later = [p for p in record["plan"] if p["order"] and p["order"] >= 3]
    assert later and all(p["action"] == "skip" and "projected balance" in p["reason"] for p in later)
    assert (base / "rl_ans/seed1/failures/job2-1.json").is_file() and (base / "rl_ans/seed1" / s4_state.COMPLETED).is_file()
    rows = [json.loads(x) for x in (tmp_path / "vm/runs/rl_v3_p1_20261110/rl_ans/seed1/rollouts.jsonl").read_text().splitlines()]
    assert sorted(r["global_step"] for r in rows) == sorted(s for s in range(228) for _ in range(2))  # no step twice
    # job 3: run 3 fails twice (FAILED.json) and the job goes on; run 4 has a setup problem, which stops the job
    monkeypatch.delenv("FAKE_TRAIN_FAIL_ONCE")
    monkeypatch.setenv("FAKE_TRAIN_FAIL", "rl_blind/1:5")
    monkeypatch.setenv("FAKE_TRAIN_SETUP", "rl_v4/1:0")
    code, record = job(copy, tmp_path, "job3", "--max-hours", "1", "--cu-balance", "1000", "--cu-rate", "0")
    assert code == 1 and record["stop"]["kind"] == "setup"
    assert [(r["run"], r["state"]) for r in record["runs"]] == [("rl_blind/seed1", "failed"), ("rl_v4/seed1", "setup")]
    assert [a["outcome"] for a in record["runs"][0]["attempts"]] == ["computation", "computation"]
    assert (base / "rl_blind/seed1" / s4_state.FAILED).is_file()
    assert len(list((base / "rl_blind/seed1/failures").glob("*.json"))) == 2


def test_train_job_setup_problems_and_dry_run_plans(fake_drive, tmp_path, monkeypatch, fast_job):
    copy = repo_copy(tmp_path)
    store = open_store(tmp_path)
    code, record = job(copy, tmp_path, "nopilot", "--dry-run")
    assert code == 0 and record["stop"]["kind"] == "setup" and "pilot" in record["checks"]["problems"][0]
    code, record = job(copy, tmp_path, "nopilot2")
    assert code == 1 and record["runs"] == []  # without a passed pilot nothing starts
    reg = put_pilot_latest(store, copy, timing={"step_seconds_p90": 60.0, "startup_seconds": 300.0,
                                                "final_upload_seconds": 120.0, "restore_seconds": 120.0})
    code, record = job(copy, tmp_path, "short", "--dry-run", "--max-hours", "1")
    assert code == 0 and record["plan"][0]["action"] == "stop" and "needs about" in record["plan"][0]["reason"]
    needed = train_s4.MIN_DRIVE_FREE_GB
    monkeypatch.setattr(train_s4, "MIN_DRIVE_FREE_GB", 1e12)  # more than the stub's (real) free space
    code, record = job(copy, tmp_path, "full", "--dry-run", "--max-hours", "20")
    assert code == 0 and record["stop"]["kind"] == "space" and "free on Google Drive" in record["plan"][0]["reason"]
    monkeypatch.setattr(train_s4, "MIN_DRIVE_FREE_GB", needed)
    monkeypatch.setenv("FAKE_TRAIN_SETUP", "rl_v5/1:0")  # e.g. a registration mismatch: would fail the same way again
    code, record = job(copy, tmp_path, "setup", "--max-hours", "20", "--cu-balance", "1000")
    assert code == 1 and [(r["run"], r["state"]) for r in record["runs"]] == [("rl_v5/seed1", "setup")]
    assert record["stop"]["kind"] == "setup" and len(record["runs"][0]["attempts"]) == 1  # no restart, the job stops
    assert not (fake_drive / EXPERIMENT / "rl_v5/seed1/failures").exists()  # not counted as a computation failure
    monkeypatch.delenv("FAKE_TRAIN_SETUP")
    for entry in reg["runs"]:  # every main run completed: the optional runs come next
        rel = train_s4.s4_state.run_rel(reg, "rl_v3_p1_20261110", entry["arm"], entry["seed"])
        assert store.put_json(rel + "/" + s4_state.COMPLETED, {"key": train_s4.run_key(reg, entry)})["ok"]
    code, record = job(copy, tmp_path, "optional", "--dry-run", "--max-hours", "20", "--cu-balance", "1000")
    actions = {p["order"]: p["action"] for p in record["plan"]}
    assert all(actions[e["order"]] == "skip" for e in reg["runs"]) and actions[13] == "start" and actions[14] == "start"
    set_cutoff(copy, "2000-01-01T00:00:00Z")  # after the cutoff, no run that was never started may start
    put_pilot_latest(store, copy, timing=FAST)
    code, record = job(copy, tmp_path, "late", "--dry-run", "--max-hours", "20", "--cu-balance", "1000")
    late = {p["order"]: p for p in record["plan"]}
    assert late[13]["action"] == "skip" and "no new run after 2000-01-01T00:00:00Z" in late[13]["reason"]
    (copy / "src/training/rl_entry.py").write_text((copy / "src/training/rl_entry.py").read_text() + "\n# change\n")
    code, record = job(copy, tmp_path, "changed", "--dry-run")
    assert any("code freeze" in p for p in record["checks"]["problems"])
    assert not list((fake_drive / EXPERIMENT).rglob("claims/*.json"))  # dry runs write nothing
