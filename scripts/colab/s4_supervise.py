"""Run one training process under supervision, and the S4 pilot runs (standard library only, VM side).

``supervise`` starts ``python -m scripts.training.train_rl ...`` in its own process group and

* writes its output to a log file and prints one short progress line per step (the runner's heartbeat shows it),
* reads the JSON events rl_entry prints (registration_matched, train_log, checkpoint_saved, train_done); tqdm may
  write on the same line first, so events are found anywhere in a line,
* copies every saved checkpoint to Drive in a worker thread (``s4_state.RunDrive``: rclone copy, rclone check,
  DRIVE_VERIFIED.json, retention), so the training never waits for Drive and a Drive failure never stops it (D31),
* stops the process at a deadline, right after a given checkpoint (pilot_resume) or when another job took the run,
* and says how it ended: ``completed``, ``interrupted``, ``setup`` (would fail the same way again: registration or
  identity mismatch, bad arguments) or ``computation`` (out of memory, NaN/inf, a failed guard, a reward error:
  the pre-registered single restart applies, S4 pre-registration section 8).

Pilot entry points (S4 pre-registration section 11; runs are smoke-marked and never feed any analysis):

    python -m scripts.colab.s4_supervise pilot-run --repo R --kind learning_run --name pilot_v5 --out DIR ...
    python -m scripts.colab.s4_supervise pilot-run --repo R --kind arm_runs --index 0 --name pilot_rl_ans ...
    python -m scripts.colab.s4_supervise pilot-run --repo R --kind learning_retry --name pilot_v5_retry \\
        --only-if-g4-failed DIR/pilot_v5 ...
    python -m scripts.colab.s4_supervise pilot-resume --repo R --name pilot_resume --out DIR ...
"""
import argparse
import json
import os
import queue
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from scripts.colab import s4_state
from scripts.colab.common import format_seconds, log, read_json, sha256_file, tail, write_json

REGISTRY = "configs/experiments/s4_runs_20261110.json"
TRAIN_MODULE = "scripts.training.train_rl"
EVENT_START = '{"event": "'
KILL_GRACE_SECONDS = 15  # SIGTERM, then SIGKILL: well inside the runner's own 30 s grace for this step
STALL_SECONDS = 3600  # no output line at all for this long: the process hangs (a computation failure)
REAP_SECONDS = 30  # after the trainer exited, children still holding its output pipe are killed
UPLOAD_DRAIN_SECONDS = 3600
TERMINATE = threading.Event()  # set on SIGTERM: the runner is stopping this step


def on_sigterm(signum, frame):
    TERMINATE.set()


def install_sigterm():
    """The trainer runs in its own process group, so the runner's kill of this step would not reach it: on SIGTERM
    the supervision loop stops the trainer group itself (within KILL_GRACE_SECONDS) and then returns."""
    signal.signal(signal.SIGTERM, on_sigterm)
# setup problems repeat identically on a restart; everything else that exits non-zero is a computation failure
SETUP_PATTERNS = [("does not match its registration", "registration"), ("is not a registered run", "registration"),
                  ("differs from the registered", "registration"), ("is not allowed for a registered run", "arguments"),
                  ("Checkpoint identity mismatch", "identity"), ("already has checkpoints", "output_dir"),
                  ("error: argument", "arguments"), ("error: unrecognized arguments", "arguments")]
COMPUTATION_PATTERNS = [("OutOfMemoryError", "out_of_memory"), ("CUDA out of memory", "out_of_memory"),
                        ("FloatingPointError", "non_finite"), ("mm_token_type_ids", "alignment_guard"),
                        ("patch grid", "image_grid"), ("vLLM would give", "image_grid")]


def parse_events(text):
    """JSON event objects in one output line."""
    events, decoder = [], json.JSONDecoder()
    start = text.find(EVENT_START)
    while start != -1:
        try:
            value, end = decoder.raw_decode(text, start)
        except ValueError:
            break
        if isinstance(value, dict) and "event" in value:
            events.append(value)
        start = text.find(EVENT_START, end)
    return events


def classify(returncode, log_text):
    """(outcome, detail) of a process that ended on its own with a non-zero exit code."""
    tail_text = log_text[-20000:]
    for needle, detail in SETUP_PATTERNS:
        if needle in tail_text:
            return "setup", detail
    for needle, detail in COMPUTATION_PATTERNS:
        if needle in tail_text:
            return "computation", detail
    if returncode is not None and returncode < 0:
        return "computation", "killed by signal %d" % -returncode
    return "computation", "exit code %s" % returncode


percentile = s4_state.percentile


def _killpg(proc, sig):
    try:
        os.killpg(proc.pid, sig)
    except OSError:
        pass


def supervise(name, cmd, out_dir, log_path, cwd, env=None, run_drive=None, key_extra=None, deadline=None,
              stop_after_checkpoint=None, heartbeat=None, heartbeat_seconds=300.0, progress_every=1,
              final_upload=True, record_path=None, poll=2.0, stall_seconds=STALL_SECONDS):
    """Run ``cmd`` to the end; return (and optionally write) the supervision record."""
    out_dir, log_path = Path(out_dir), Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {"schema": "p3-s4-supervised-v1", "name": name, "cmd": [str(c) for c in cmd], "started_utc": s4_state.utc(),
              "out_dir": str(out_dir), "log": str(log_path), "registration": None, "train_done": None, "last_step": 0,
              "max_steps": None, "step_seconds": {}, "format_rate": {}, "checkpoints_saved": [], "uploads": [],
              "uploads_superseded": [], "interrupted": None, "final_upload": None, "key": None}
    started = time.time()
    todo, lock, wake, closing = [], threading.Lock(), threading.Event(), threading.Event()

    def uploader():
        while True:
            wake.wait(1.0)
            with lock:
                batch = list(todo)
                del todo[:]
                wake.clear()
            if batch:
                step, path = max(batch)
                record["uploads_superseded"] += [s for s, _ in batch if s != step]
                result = run_drive.upload_checkpoint(path, step, rollouts=out_dir / s4_state.ROLLOUTS)
                record["uploads"].append(result)
                log("[%s] checkpoint-%d on Drive: %s%s" % (name, step, "verified" if result.get("ok") else "FAILED",
                                                          "" if result.get("ok") else " (%s)" % result.get("reason")))
                continue
            if closing.is_set():
                with lock:
                    if not todo:
                        return

    worker = None
    if run_drive is not None:
        worker = threading.Thread(target=uploader, name="drive-uploads", daemon=True)
        worker.start()
    proc = subprocess.Popen([str(c) for c in cmd], cwd=str(cwd), env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, start_new_session=True)
    lines = queue.Queue()

    def reader():
        for raw in iter(proc.stdout.readline, b""):
            lines.put(raw)
        lines.put(None)

    threading.Thread(target=reader, name="train-output", daemon=True).start()
    state = {"kill_at": None, "outcome": "interrupted", "last_output": time.time(), "exited_at": None}

    def interrupt(reason, outcome="interrupted"):
        if record["interrupted"] is not None:
            return
        record["interrupted"] = reason
        state["outcome"] = outcome
        log("[%s] stopping the training process: %s" % (name, reason))
        _killpg(proc, signal.SIGTERM)
        state["kill_at"] = time.time() + KILL_GRACE_SECONDS

    def handle(event):
        kind = event.get("event")
        if kind == "registration_matched":
            record["registration"] = event
        elif kind == "train_log":
            step = int(event.get("step") or 0)
            record["max_steps"] = event.get("max_steps") or record["max_steps"]
            if "step_time" in event:
                record["step_seconds"][str(step)] = event["step_time"]
                if "p3/format_rate" in event:
                    record["format_rate"][str(step)] = event["p3/format_rate"]
                record["last_step"] = max(record["last_step"], step)
                if progress_every and (step % progress_every == 0 or step == record["max_steps"]):
                    times = list(record["step_seconds"].values())
                    median = percentile(times, 0.5)
                    left = (record["max_steps"] or step) - step
                    log("[%s] step %d/%s | %.1f s/step | eta %s | format %s | answer %s" % (
                        name, step, record["max_steps"], median or 0, format_seconds(left * (median or 0)),
                        event.get("p3/format_rate"), event.get("p3/answer_acc")))
        elif kind == "checkpoint_saved":
            step = int(event["step"])
            record["checkpoints_saved"].append(step)
            if record["interrupted"] is not None:
                return  # the process is being stopped: a checkpoint written in that window is not the one resumed
            if run_drive is not None:
                key = dict(key_extra or {}, config_sha256=event.get("config_sha256"))
                record["key"] = key
                if not run_drive.set_key(key):
                    interrupt("the run's configuration %s differs from the one on Drive %s" % (key, run_drive.key))
                    return
                path = Path(event["path"])
                with lock:
                    todo.append((step, str(path if path.is_absolute() else Path(cwd) / path)))
                    wake.set()
            if stop_after_checkpoint is not None and step == int(stop_after_checkpoint):
                interrupt("pilot: stop right after checkpoint-%d (emulates a lost VM)" % step)
        elif kind == "train_done":
            record["train_done"] = event

    beat_stop = threading.Event()

    def beater():
        # its own thread: a Drive call can take minutes (rclone timeouts of 600 s), and the loop below must keep
        # watching the deadline and the output meanwhile
        while not beat_stop.wait(heartbeat_seconds):
            try:
                heartbeat()
            except Exception as exc:  # a missed heartbeat is reported, never fatal
                log("[%s] heartbeat failed: %s" % (name, exc))

    if heartbeat is not None:
        threading.Thread(target=beater, name="claim-heartbeat", daemon=True).start()
    with open(str(log_path), "ab") as handle_log:
        while True:
            try:
                raw = lines.get(timeout=poll)
            except queue.Empty:
                raw = b""
            if raw is None:
                break
            now = time.time()
            if raw:
                state["last_output"] = now
                handle_log.write(raw)
                handle_log.flush()
                for event in parse_events(raw.decode("utf-8", "replace")):
                    handle(event)
            if TERMINATE.is_set():
                interrupt("the supervisor was asked to stop (SIGTERM from the runner)")
            if deadline is not None and now > deadline:
                interrupt("time budget: deadline %s reached" % s4_state.utc(deadline))
            if run_drive is not None and run_drive.lost_claim:
                interrupt("another job holds this run now (lost claim)")
            if stall_seconds and now - state["last_output"] > stall_seconds:
                interrupt("no output for %d s (the process hangs)" % stall_seconds, outcome="computation")
            if state["kill_at"] is not None and now > state["kill_at"] and proc.poll() is None:
                _killpg(proc, signal.SIGKILL)
            if proc.poll() is not None:
                # children that inherited the output pipe (e.g. answer-verifier workers of a trainer killed by the
                # OOM killer) would keep it open forever: the trainer's process group is killed, then the loop ends
                state["exited_at"] = state["exited_at"] or now
                if now - state["exited_at"] > REAP_SECONDS:
                    _killpg(proc, signal.SIGKILL)
                if now - state["exited_at"] > 2 * REAP_SECONDS:
                    record["output_pipe_held_open"] = True
                    break
    record["exit_code"] = proc.wait()
    record["wall_seconds"] = round(time.time() - started, 1)
    times = [float(t) for t in record["step_seconds"].values()]
    record["startup_seconds"] = round(max(0.0, record["wall_seconds"] - sum(times)), 1) if times else None
    log_text = tail(log_path, 400, max_bytes=262144)
    if record["interrupted"] is not None:
        record["outcome"], record["detail"] = state["outcome"], record["interrupted"]
    elif record["exit_code"] == 0 and record["train_done"]:
        record["outcome"], record["detail"] = "completed", None
    elif record["exit_code"] == 0:
        record["outcome"], record["detail"] = "computation", "exit code 0 without a train_done event"
    else:
        record["outcome"], record["detail"] = classify(record["exit_code"], log_text)
    if record["outcome"] != "completed":
        record["log_tail"] = "\n".join(log_text.splitlines()[-40:])
    if worker is not None:
        closing.set()
        wake.set()
        worker.join(UPLOAD_DRAIN_SECONDS)
        if worker.is_alive():
            record["uploads_unfinished"] = True
    if run_drive is not None and final_upload and record["outcome"] == "completed" and not run_drive.lost_claim:
        record["final_upload"] = run_drive.upload_final(out_dir, record["train_done"].get("global_step"))
        log("[%s] final/ and run files on Drive: %s" % (name, "verified, COMPLETED.json written"
                                                       if record["final_upload"].get("ok")
                                                       else "FAILED (%s)" % record["final_upload"].get("reason")))
    beat_stop.set()  # after the last Drive write of this attempt; the claim itself is released by train_s4
    record["finished_utc"] = s4_state.utc()
    log("[%s] ended: %s%s after %s" % (name, record["outcome"], " (%s)" % record["detail"] if record["detail"] else "",
                                        format_seconds(record["wall_seconds"])))
    if record_path is not None:
        write_json(record_path, record)
    return record


# ---- pilot -------------------------------------------------------------------------------------------------------

def load_registry(repo, registry=REGISTRY):
    repo = Path(repo)
    path = repo / registry
    reg = read_json(path)
    experiment = read_json(repo / reg["experiment"]["path"])
    return reg, experiment, path


def smoke_text(smoke):
    return ",".join("%s=%s" % (k, smoke[k]) for k in sorted(smoke))


def pilot_spec(reg, kind, index=None):
    pilot = reg["pilot"]
    spec = pilot["arm_runs"][int(index)] if kind == "arm_runs" else pilot[kind]
    return dict(spec, seed=pilot["seed"])


def pilot_cmd(args, reg, spec, out_dir, resume=None):
    repo = Path(args.repo)
    cmd = [args.python, "-m", args.train_module, "--experiment", repo / reg["experiment"]["path"], "--arm", spec["arm"],
           "--seed", str(spec["seed"]), "--smoke", smoke_text(spec["smoke"]), "--runtime", repo / reg["runtime"]["path"],
           "--output-dir", out_dir]
    if args.model_path:
        cmd += ["--model-path", args.model_path]
    if resume:
        cmd += ["--resume", resume]
    return [str(c) for c in cmd]


def pilot_env(args):
    return dict(os.environ, PYTHONUNBUFFERED="1")


def open_store(args):
    store, info = s4_state.Store.open(Path(args.out_dir_root) / ".drive_scratch", remote=args.drive_remote,
                                      base_dir=args.drive_dir, mount=args.drive_mount)
    return store, info


def pilot_drive_rel(reg, experiment, job, name):
    return "%s/pilot/%s/%s" % (s4_state.experiment_base(reg, experiment["name"]), job, name)


def cmd_pilot_run(args):
    reg, experiment, _ = load_registry(args.repo)
    out = Path(args.out)
    record_path = out / "supervisor.json"
    if args.only_if_g4_failed:
        from scripts.colab import decide_pilot

        need, reason = decide_pilot.retry_needed(Path(args.only_if_g4_failed), reg, args.repo)
        if not need:
            out.mkdir(parents=True, exist_ok=True)
            write_json(record_path, {"schema": "p3-s4-supervised-v1", "name": args.name, "skipped": True,
                                     "reason": reason})
            log("[%s] not run: %s" % (args.name, reason))
            return 0
        log("[%s] G4 failed on %s with the other gates passing: running the pre-registered retry" % (
            args.name, args.only_if_g4_failed))
    spec = pilot_spec(reg, args.kind, args.index)
    run_drive = None
    if args.drive:
        store, info = open_store(args)
        if store is None:
            write_json(record_path, {"schema": "p3-s4-supervised-v1", "name": args.name, "outcome": "setup",
                                     "detail": "Drive is not usable: %s" % "; ".join(info["notes"])})
            log("[%s] Drive is not usable: %s" % (args.name, "; ".join(info["notes"])))
            return 1
        run_drive = s4_state.RunDrive(store, pilot_drive_rel(reg, experiment, args.job, args.name), None, args.job,
                                      args.name, keep=reg["checkpoints"]["keep_full_checkpoints_on_drive"])
    record = supervise(args.name, pilot_cmd(args, reg, spec, out), out, out / "train.log", args.repo, env=pilot_env(args),
                       run_drive=run_drive, key_extra={"runtime_content_sha256": reg["runtime"]["content_sha256"]},
                       record_path=record_path)
    record.update(kind=args.kind, spec=spec, drive_rel=run_drive.rel if run_drive else None)
    write_json(record_path, record)
    return 0 if record["outcome"] == "completed" else 1


def cmd_pilot_resume(args):
    """Leg A stops right after checkpoint-1 (its copy goes to Drive), the local directory is set aside, checkpoint-1
    is restored from Drive into the same directory, and leg B resumes from it to the end (gate G5)."""
    reg, experiment, _ = load_registry(args.repo)
    out = Path(args.out)
    spec = pilot_spec(reg, "resume_run")
    record_path = out.parent / (out.name + ".supervisor.json")
    result = {"schema": "p3-s4-pilot-resume-v1", "name": args.name, "spec": spec, "legs": {}, "ok": False}
    store, info = open_store(args)
    if store is None:
        result["reason"] = "Drive is not usable: %s" % "; ".join(info["notes"])
        write_json(record_path, result)
        log("[%s] %s" % (args.name, result["reason"]))
        return 1
    rel = pilot_drive_rel(reg, experiment, args.job, args.name)
    result["drive_rel"] = rel
    keep = reg["checkpoints"]["keep_full_checkpoints_on_drive"]
    extra = {"runtime_content_sha256": reg["runtime"]["content_sha256"]}
    leg_a = s4_state.RunDrive(store, rel, None, args.job, args.name, keep=keep)
    a = supervise(args.name + "/a", pilot_cmd(args, reg, spec, out), out, out / "train.log", args.repo,
                  env=pilot_env(args), run_drive=leg_a, key_extra=extra, stop_after_checkpoint=1, final_upload=False)
    result["legs"]["a"] = a
    uploaded = [u for u in a["uploads"] if u.get("step") == 1 and u.get("ok")]
    if a["outcome"] != "interrupted" or not uploaded:
        result["reason"] = "leg A did not stop after a verified checkpoint-1 (outcome %s, uploads %s)" % (
            a["outcome"], [(u.get("step"), u.get("ok")) for u in a["uploads"]])
        write_json(record_path, result)
        return 1
    aside = out.parent / (out.name + ".leg_a")
    shutil.rmtree(str(aside), ignore_errors=True)
    os.replace(str(out), str(aside))  # as on a new VM: nothing of leg A is left in the run directory
    leg_b = s4_state.RunDrive(store, rel, leg_a.key, args.job, args.name, keep=keep)
    step, marker = leg_b.latest_verified()
    result["latest_verified"] = step
    if step != 1:
        result["reason"] = "Drive does not offer checkpoint-1 as the latest verified checkpoint (%s)" % marker
        write_json(record_path, result)
        return 1
    restored = leg_b.restore(step, marker, out)
    result["restore"] = restored
    if not restored.get("ok"):
        result["reason"] = "restore from Drive failed: %s" % restored.get("reason")
        write_json(record_path, result)
        return 1
    b = supervise(args.name + "/b", pilot_cmd(args, reg, spec, out, resume=restored["path"]), out, out / "train.log",
                  args.repo, env=pilot_env(args), run_drive=leg_b, key_extra=extra)
    result["legs"]["b"] = b
    done = b.get("train_done") or {}
    result["ok"] = (b["outcome"] == "completed" and done.get("global_step") == spec["smoke"]["max_steps"]
                    and all(u.get("ok") for u in b["uploads"]) and bool((b.get("final_upload") or {}).get("ok")))
    if not result["ok"]:
        result["reason"] = "leg B: outcome %s, global step %s, uploads %s, final %s" % (
            b["outcome"], done.get("global_step"), [(u.get("step"), u.get("ok")) for u in b["uploads"]],
            (b.get("final_upload") or {}).get("ok"))
    write_json(record_path, result)
    log("[%s] %s" % (args.name, "resume from Drive passed" if result["ok"] else "FAILED: %s" % result["reason"]))
    return 0 if result["ok"] else 1


def add_common(parser):
    parser.add_argument("--repo", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--job", required=True, help="the job's run id (names the pilot's Drive directory)")
    parser.add_argument("--python", default=sys.executable, help="interpreter of the training environment")
    parser.add_argument("--model-path")
    parser.add_argument("--train-module", default=TRAIN_MODULE, help=argparse.SUPPRESS)  # tests: a fake trainer
    parser.add_argument("--drive-remote")
    parser.add_argument("--drive-dir")
    parser.add_argument("--drive-mount")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("pilot-run")
    add_common(p)
    p.add_argument("--kind", required=True, choices=["learning_run", "learning_retry", "arm_runs"])
    p.add_argument("--index", type=int)
    p.add_argument("--drive", action="store_true", help="copy checkpoints to Drive and verify them (gate G5)")
    p.add_argument("--only-if-g4-failed", help="pilot_v5 directory: run only when its G4 failed, other gates passed")
    p = sub.add_parser("pilot-resume")
    add_common(p)
    args = parser.parse_args(argv)
    args.out_dir_root = str(Path(args.out).parent)
    install_sigterm()
    if args.command == "pilot-run":
        if args.kind == "arm_runs" and args.index is None:
            parser.error("--kind arm_runs needs --index")
        return cmd_pilot_run(args)
    return cmd_pilot_resume(args)


if __name__ == "__main__":
    sys.exit(main())
