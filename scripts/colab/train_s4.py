"""S4 formal runs on one VM: pick, claim, restore, train, verify on Drive (standard library only, VM side).

    python -m scripts.colab.train_s4 --repo /content/p3/repo --root /content/p3 --out <job dir> --job <run id>
        --session <colab session> --python <training python> --model-path <snapshot>
        [--max-hours H] [--vm-hours 24] [--cu-balance X --cu-rate Y --cu-measured-epoch T] [--dry-run]
        [--drive-remote ... --drive-dir ... --drive-mount ...]

Rules (docs/plan/S4预注册_20261110.md sections 8-12; decisions D52-D58 and the ones of this stage):

* Formal runs start only when the latest pilot on Drive passed with the same registry and runtime, and the training
  code and package versions here equal the pilot's (code freeze). The first formal run writes the code baseline;
  every later run must match it.
* Runs are taken in the registered order. A run is skipped when it is completed or failed on Drive, or held by a live
  claim of another job. A run that was never started is not started after ``no_new_run_after_utc`` or when the
  projected compute-unit balance is below ``min_compute_units_to_start_a_run``; a started run is resumed regardless.
  Optional runs come only after all main runs are completed or failed.
* A run starts (or resumes) only if it is expected to finish before the job's deadline (VM lifetime and --max-hours)
  and the VM disk and Google Drive have room for it (otherwise the job stops and says so).
  At the hard deadline the training is stopped; its latest verified checkpoint on Drive is where the next job resumes.
* Resume only from a checkpoint with DRIVE_VERIFIED.json, downloaded into the run's own (emptied) output directory
  and checked file by file; the local directory is set aside first, never deleted.
* A computation failure is recorded on Drive and restarted once from the latest verified checkpoint; the second
  failure of a run (in any job) writes FAILED.json. A setup failure (registration or identity mismatch) stops the job.
"""
import argparse
import calendar
import gzip
import json
import os
import shutil
import sys
import time
from pathlib import Path

from scripts.colab import s4_state, s4_supervise
from scripts.colab.common import format_seconds, log, read_json, sha256_file, write_json

SCHEMA = "p3-s4-train-job-v1"
STEP_MARGIN = 1.10  # planned step time = 1.10 x the larger of the pilot's and this job's 90th-percentile step time
RUN_MARGIN_SECONDS = 600
STOP_BEFORE_VM_END_SECONDS = 1800  # leave time to package and push the job's results
PLAN_BEFORE_STOP_SECONDS = 900
MIN_FREE_DISK_GB = 15.0
# a run keeps at most two checkpoints on Drive at once (the new one is verified before the old one is purged, about
# 0.36 GB each) plus final/ (about 0.12 GB); a full Drive would leave a finished run without a copy that outlives the VM
MIN_DRIVE_FREE_GB = 2.0
DEFAULTS = {"startup_seconds": 900.0, "final_upload_seconds": 600.0, "restore_seconds": 600.0, "step_seconds": 120.0}
# run results that need attention: the job's exit code becomes non-zero, so the run is reported as "not passed"
PROBLEM_STATES = ("failed", "failed_once", "completed_drive_failed", "restore_failed", "setup", "not_started")


def parse_utc(text):
    return calendar.timegm(time.strptime(text, "%Y-%m-%dT%H:%M:%SZ"))


def container_started_epoch(proc="/proc"):
    """Start time of PID 1 (the Colab container), from /proc; None when it cannot be read."""
    try:
        btime = None
        with open(os.path.join(proc, "stat")) as handle:
            for line in handle:
                if line.startswith("btime"):
                    btime = int(line.split()[1])
        with open(os.path.join(proc, "1", "stat")) as handle:
            fields = handle.read().rsplit(")", 1)[1].split()
        return btime + int(fields[19]) / float(os.sysconf("SC_CLK_TCK")) if btime else None
    except (OSError, ValueError, IndexError):
        return None


def deadlines(job_start, max_hours=None, vm_hours=24.0, container_start=None):
    """(finish_by, stop_at): runs are planned to end by finish_by; a run still going at stop_at is stopped."""
    limits = []
    if max_hours:
        limits.append(job_start + float(max_hours) * 3600)
    if vm_hours:
        start = job_start if container_start is None else container_start
        limits.append(start + float(vm_hours) * 3600 - STOP_BEFORE_VM_END_SECONDS)
    stop_at = min(limits) if limits else job_start + 23 * 3600
    return stop_at - PLAN_BEFORE_STOP_SECONDS, stop_at


def unused_name(path):
    """``path``, or ``path``-2, -3, ... when it exists (two renames can fall in the same second)."""
    path, number = Path(path), 1
    candidate = path
    while candidate.exists() or candidate.is_symlink():
        number += 1
        candidate = path.with_name("%s-%d" % (path.name, number))
    return candidate


def ensure_runs_link(root, repo):
    """repo/runs -> root/runs: bootstrap deletes the repo directory when the code changes, run outputs must outlive it."""
    target = Path(root) / "runs"
    target.mkdir(parents=True, exist_ok=True)
    link = Path(repo) / "runs"
    if link.is_symlink():
        if Path(os.readlink(str(link))) == target:
            return {"link": str(link), "target": str(target), "moved": None}
        link.unlink()
    moved = None
    if link.exists():
        moved = unused_name(target / ("from_repo_" + s4_state.utc().replace(":", "")))
        os.replace(str(link), str(moved))
    os.symlink(str(target), str(link))
    return {"link": str(link), "target": str(target), "moved": str(moved) if moved else None}


def set_aside(directory):
    """Rename a non-empty run directory to <name>.aside-<utc> (never delete); return the new path or None."""
    directory = Path(directory)
    if not directory.exists() or not any(directory.iterdir()):
        if directory.exists():
            directory.rmdir()
        return None
    aside = unused_name(directory.with_name("%s.aside-%s" % (directory.name, s4_state.utc().replace(":", ""))))
    os.replace(str(directory), str(aside))
    return str(aside)


def gzip_copy(source, target):
    with open(str(source), "rb") as src, gzip.open(str(target), "wb", compresslevel=6) as out:
        shutil.copyfileobj(src, out)


def collect(local, dest):
    """Small result files of a run (no weights) for the job's results branch; rollouts.jsonl is gzipped."""
    local, dest = Path(local), Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in s4_state.RUN_FILES + (s4_state.RESTORED_NOTE,):
        if (local / name).is_file():
            shutil.copy2(str(local / name), str(dest / name))
            copied.append(name)
    if (local / s4_state.ROLLOUTS).is_file():
        gzip_copy(local / s4_state.ROLLOUTS, dest / (s4_state.ROLLOUTS + ".gz"))
        copied.append(s4_state.ROLLOUTS + ".gz")
    return copied


class Planner(object):
    """Expected wall time of a run, from the pilot's timing and the steps measured in this job."""

    def __init__(self, timing):
        timing = timing or {}
        self.timing = {k: timing.get(k) for k in ("startup_seconds", "final_upload_seconds", "restore_seconds")}
        self.pilot_step = timing.get("step_seconds_p90") or timing.get("step_seconds_median")
        self.measured = []

    def step_seconds(self):
        candidates = [x for x in (self.pilot_step, s4_state.percentile(self.measured, 0.9)) if x]
        return STEP_MARGIN * (max(candidates) if candidates else DEFAULTS["step_seconds"])

    def seconds(self, remaining_steps, resuming):
        part = lambda key: float(self.timing.get(key) or DEFAULTS[key])  # noqa: E731
        return (part("startup_seconds") + remaining_steps * self.step_seconds() + part("final_upload_seconds")
                + (part("restore_seconds") if resuming else 0.0) + RUN_MARGIN_SECONDS)

    def add(self, step_seconds):
        self.measured.extend(float(x) for x in step_seconds if x)


def entries(reg):
    main = [dict(e, optional=False) for e in reg["runs"]]
    optional = [dict(e, optional=True) for e in reg.get("optional_runs", [])]
    return sorted(main, key=lambda e: e["order"]), sorted(optional, key=lambda e: e["order"])


def run_key(reg, entry):
    return {"config_sha256": entry["config_sha256"], "runtime_content_sha256": reg["runtime"]["content_sha256"]}


def gate_problems(latest, latest_status, reg, registry_sha, current, current_error):
    """Why formal runs may not start (empty list: they may)."""
    problems = []
    if latest is None:
        return ["no pilot result on Drive (PILOT_LATEST.json: %s); run `bash colab/launch.sh pilot` first" % latest_status]
    if not latest.get("passed"):
        problems.append("the latest pilot (%s) did not pass its gates %s" % (latest.get("job"), latest.get("gates")))
    if latest.get("registry_sha256") != registry_sha:
        problems.append("the registry differs from the one the latest pilot ran with")
    if latest.get("runtime_content_sha256") != reg["runtime"]["content_sha256"]:
        problems.append("the frozen runtime differs from the one the latest pilot ran with")
    if current is None:
        problems.append("could not compute this code's identity: %s" % current_error)
    else:
        if current.get("source_sha256") != latest.get("source_sha256"):
            changed = sorted(k for k in set(current["source_sha256"]) | set(latest.get("source_sha256") or {})
                             if current["source_sha256"].get(k) != (latest.get("source_sha256") or {}).get(k))
            problems.append("training code differs from the pilot's (code freeze): %s" % changed[:6])
        if current.get("versions") != latest.get("versions"):
            problems.append("package versions differ from the pilot's: %s vs %s" % (current.get("versions"),
                                                                                   latest.get("versions")))
    return problems


def read_baseline(store, base):
    """The earliest code baseline written by any job (one file per job), or None; (doc, problem)."""
    entries_ = store.tree(base + "/code_baseline", depth=1)
    if entries_ is None:
        return None, "could not list the code baselines"
    docs = []
    for entry in entries_:
        if entry.get("IsDir") or not entry["Path"].endswith(".json"):
            continue
        doc, status = store.get_json("%s/code_baseline/%s" % (base, entry["Path"]))
        if doc is None:
            return None, "code baseline %s unreadable (%s)" % (entry["Path"], status)
        docs.append(doc)
    if not docs:
        return None, None
    return min(docs, key=lambda d: (d.get("written_utc") or "", d.get("job") or "")), None


class Job(object):
    def __init__(self, args):
        self.args = args
        self.repo, self.root, self.out = Path(args.repo), Path(args.root), Path(args.out)
        self.registry_path = self.repo / s4_supervise.REGISTRY
        self.reg = read_json(self.registry_path)
        self.experiment = read_json(self.repo / self.reg["experiment"]["path"])
        self.base = s4_state.experiment_base(self.reg, self.experiment["name"])
        self.started = time.time()
        self.record = {"schema": SCHEMA, "job": args.job, "session": args.session, "dry_run": bool(args.dry_run),
                       "started_utc": s4_state.utc(self.started), "plan": [], "runs": [], "stop": None, "checks": {}}
        self.store = None
        self.planner = None
        self.current = None
        self.baseline = None
        self.finish_by = self.stop_at = None
        self.exit_code = 0

    def save(self):
        write_json(self.out / "train_job.json", self.record)

    def stop(self, kind, reason, code=None):
        self.record["stop"] = {"kind": kind, "reason": reason, "utc": s4_state.utc()}
        log("train: stop (%s): %s" % (kind, reason))
        if code is not None:
            self.exit_code = max(self.exit_code, code)

    def checks(self):
        """Drive, pilot, code freeze, baseline, deadlines, disk. Returns False when no run may start."""
        args = self.args
        self.store, info = s4_state.Store.open(self.out / ".drive_scratch", remote=args.drive_remote,
                                               base_dir=args.drive_dir, mount=args.drive_mount)
        if self.store is None:
            self.stop("setup", "Google Drive is not usable on this VM: %s" % "; ".join(info["notes"]), 1)
            return False
        self.record["checks"]["drive_free_bytes"] = (self.store.about() or {}).get("free")
        latest, latest_status = self.store.get_json(self.base + "/PILOT_LATEST.json")
        current, error = code_identity(args.python, self.repo)
        problems = gate_problems(latest, latest_status, self.reg, sha256_file(self.registry_path), current, error)
        baseline, baseline_problem = read_baseline(self.store, self.base)
        if baseline_problem:
            problems.append(baseline_problem)
        elif baseline and current and baseline.get("source_sha256") != current.get("source_sha256"):
            problems.append("training code differs from the code baseline of the first formal run (job %s, %s); a code "
                            "change during S4 needs a new decision (pre-registration section 9)" % (
                                baseline.get("job"), baseline.get("written_utc")))
        self.record["checks"].update(pilot=(latest or {}).get("job"), pilot_passed=(latest or {}).get("passed"),
                                     baseline=(baseline or {}).get("job"), problems=problems)
        self.current = current
        self.baseline = baseline
        if problems:
            self.stop("setup", "; ".join(problems), 0 if args.dry_run else 1)
            return False
        self.planner = Planner(latest.get("timing"))
        container = container_started_epoch()
        self.finish_by, self.stop_at = deadlines(self.started, args.max_hours, args.vm_hours, container)
        self.record["checks"].update(container_started_utc=s4_state.utc(container) if container else None,
                                     finish_by_utc=s4_state.utc(self.finish_by), stop_at_utc=s4_state.utc(self.stop_at),
                                     planned_step_seconds=round(self.planner.step_seconds(), 1))
        log("train: pilot %s passed, code matches it%s; plan runs to finish by %s, stop at %s (%.0f s/step planned)" % (
            latest.get("job"), "" if not baseline else " and the baseline of job %s" % baseline.get("job"),
            s4_state.utc(self.finish_by), s4_state.utc(self.stop_at), self.planner.step_seconds()))
        return True

    def new_run_allowed(self):
        rules = self.reg["stop_rules"]
        now = time.time()
        if now >= parse_utc(rules["no_new_run_after_utc"]):
            return False, "no new run after %s (pre-registration section 10)" % rules["no_new_run_after_utc"]
        balance, rate, measured = self.args.cu_balance, self.args.cu_rate, self.args.cu_measured_epoch
        if balance is None:
            log("train: the compute-unit balance is unknown (colab usage was not parsed); not applying that rule")
            return True, None
        projected = balance - (rate or 0.0) * max(0.0, now - (measured or self.started)) / 3600.0
        if projected < rules["min_compute_units_to_start_a_run"]:
            return False, "projected balance %.0f CU is below %s CU (pre-registration section 10)" % (
                projected, rules["min_compute_units_to_start_a_run"])
        return True, None

    def free_disk_gb(self):
        path = self.root
        while not path.exists() and path != path.parent:  # a dry run may not have created the root yet
            path = path.parent
        return shutil.disk_usage(str(path)).free / 1e9

    def run(self):
        self.out.mkdir(parents=True, exist_ok=True)
        if not self.checks():
            self.save()
            return self.exit_code
        if not self.args.dry_run:
            self.record["checks"]["runs_link"] = ensure_runs_link(self.root, self.repo)
        main, optional = entries(self.reg)
        if self.go_through(main) and optional:
            # optional runs start only after every main run is completed or failed (pre-registration section 10)
            states = {e["run_name"]: self.status(e)["state"] for e in main}
            open_runs = sorted(name for name, state in states.items() if state not in ("completed", "failed"))
            if open_runs:
                self.record["plan"].append({"order": None, "run": "optional runs", "state": None, "action": "skip",
                                            "reason": "main runs not all completed or failed: %s" % open_runs[:4],
                                            "utc": s4_state.utc()})
            else:
                self.go_through(optional)
        if self.record["stop"] is None:
            self.record["stop"] = {"kind": "done", "reason": "no further run to start in this job", "utc": s4_state.utc()}
        self.record["finished_utc"] = s4_state.utc()
        self.save()
        return self.exit_code

    def status(self, entry):
        return s4_state.run_status(self.store, self.rel(entry), run_key(self.reg, entry))

    def go_through(self, group):
        """Decide and execute the runs of ``group`` in order; False when the job must stop."""
        for entry in group:
            if s4_supervise.TERMINATE.is_set():
                self.stop("interrupted", "the runner asked this step to stop")
                return False
            status = self.status(entry)  # read now: another VM may have claimed or finished it meanwhile
            action, reason, remaining = self.decide(entry, status)
            self.record["plan"].append({"order": entry["order"], "run": entry["run_name"], "state": status["state"],
                                        "action": action, "reason": reason, "remaining_steps": remaining,
                                        "utc": s4_state.utc()})
            log("train: #%d %s: %s%s" % (entry["order"], entry["run_name"], action, " (%s)" % reason if reason else ""))
            self.save()
            if action == "stop":
                self.stop("time", reason)
                return False
            if action == "no_space":  # needs you: a fresh VM (local disk) or room on Google Drive
                self.stop("space", reason, 0 if self.args.dry_run else 1)
                return False
            if action == "skip" or self.args.dry_run:
                continue
            result = self.execute(entry, status)
            self.record["runs"].append(result)
            self.save()
            if result.get("state") in PROBLEM_STATES:
                self.exit_code = max(self.exit_code, 1)
            if result.get("stop_job"):
                self.stop(result["stop_job"], result.get("reason"),
                          0 if result["stop_job"] in ("time", "interrupted") else 1)
                return False
        return True

    def rel(self, entry):
        return s4_state.run_rel(self.reg, self.experiment["name"], entry["arm"], entry["seed"])

    def drive_free_gb(self):
        """Free space on the Drive remote in GB as `rclone about` reports it; None when it reports none."""
        free = (self.store.about() or {}).get("free")
        return free / 1e9 if isinstance(free, (int, float)) else None

    def decide(self, entry, status):
        """("start" | "resume" | "skip" | "stop" | "no_space", reason, remaining steps)."""
        state = status["state"]
        if state in ("completed", "failed"):
            return "skip", state, 0
        if state in ("foreign", "unknown"):
            return "skip", status.get("reason"), None
        others = [c for c in s4_state.live_claims(status["claims"], time.time(), self.args.session, self.args.job)
                  if c.get("job") != self.args.job]
        if others:
            first = s4_state.winner(others)
            return "skip", "held by job %s (session %s, heartbeat %s)" % (first.get("job"), first.get("session"),
                                                                         first.get("heartbeat_utc")), None
        if state != "started":
            allowed, why = self.new_run_allowed()
            if not allowed:
                return "skip", why, entry["max_steps"]
        done = max(status["checkpoints"]) if status["checkpoints"] else 0
        remaining = entry["max_steps"] - done
        if self.free_disk_gb() < MIN_FREE_DISK_GB:
            return "no_space", "only %.1f GB free on the VM disk (need %.0f GB)" % (
                self.free_disk_gb(), MIN_FREE_DISK_GB), remaining
        drive_free = self.drive_free_gb()
        if drive_free is not None and drive_free < MIN_DRIVE_FREE_GB:
            return "no_space", "only %.1f GB free on Google Drive (need %.0f GB for a run's checkpoints and final/)" % (
                drive_free, MIN_DRIVE_FREE_GB), remaining
        expected = self.planner.seconds(remaining, resuming=done > 0)
        if time.time() + expected > self.finish_by:
            return "stop", "%s needs about %s, %s left before the deadline" % (
                entry["run_name"], format_seconds(expected), format_seconds(max(0, self.finish_by - time.time()))), \
                remaining
        return ("resume" if done else "start"), "from checkpoint-%d" % done if done else None, remaining

    def execute(self, entry, status):
        """Claim, (restore), train, handle the outcome; restart once after a computation failure."""
        args, rel, key = self.args, self.rel(entry), run_key(self.reg, entry)
        name = entry["run_name"]
        dest = self.out / "runs" / name.replace("/", "_")
        result = {"order": entry["order"], "run": name, "attempts": [], "state": None, "started_utc": s4_state.utc()}
        claim = s4_state.Claim(self.store, rel, args.job, args.session)
        held, why = claim.acquire()
        if not held:
            result.update(state="skipped", reason=why)
            return result
        failures = len(status.get("failures") or [])
        try:
            self.write_baseline(entry)
            if status["state"] == "new":
                started = self.store.put_json(rel + "/STARTED.json", {"key": key, "job": args.job, "run": name,
                                                                      "started_utc": s4_state.utc()})
                if not started.get("ok"):
                    result.update(state="not_started", stop_job="setup",
                                  reason="could not write STARTED.json: %s" % started.get("reason"))
                    return result
            while True:
                attempt = self.attempt(entry, rel, key, claim, dest, len(result["attempts"]) + 1)
                result["attempts"].append(attempt)
                outcome = attempt.get("outcome")
                if outcome == "completed":
                    result["state"] = "completed" if (attempt.get("final_upload") or {}).get("ok") else \
                        "completed_drive_failed"
                    self.planner.add((attempt.get("step_seconds") or {}).values())
                    return result
                if outcome == "interrupted":
                    result["state"] = "interrupted"
                    lost = "lost claim" in (attempt.get("detail") or "")
                    if not lost:
                        result.update(stop_job="time" if "time budget" in (attempt.get("detail") or "")
                                      else "interrupted", reason=attempt.get("detail"))
                    return result
                if outcome in ("setup", "restore_failed"):
                    result.update(state=outcome, stop_job="setup", reason=attempt.get("detail"))
                    return result
                failures += 1
                record_failure = s4_state.record_failure(self.store, rel, args.job, len(result["attempts"]), {
                    "run": name, "key": key, "job": args.job, "attempt": len(result["attempts"]),
                    "detail": attempt.get("detail"), "last_step": attempt.get("last_step"),
                    "log_tail": (attempt.get("log_tail") or "")[-4000:], "utc": s4_state.utc()})
                attempt["failure_recorded"] = bool(record_failure.get("ok"))
                limit = self.reg["stop_rules"]["computation_failure_restarts"]
                if failures > limit:
                    failed = self.store.put_json(rel + "/" + s4_state.FAILED, {
                        "schema": "p3-run-failed-v1", "run": name, "key": key, "job": args.job, "failures": failures,
                        "last_detail": attempt.get("detail"), "failed_utc": s4_state.utc()})
                    result.update(state="failed", reason="computation failure %d of %d allowed restart(s)+1; %s" % (
                        failures, limit, "FAILED.json written" if failed.get("ok") else "FAILED.json NOT written"))
                    return result
                allowed_time = time.time() + self.planner.seconds(entry["max_steps"], resuming=True) <= self.finish_by
                if not allowed_time:
                    result.update(state="failed_once", stop_job="time",
                                  reason="computation failure; the one allowed restart does not fit in this job")
                    return result
                log("train: %s: computation failure (%s); the one pre-registered restart follows" % (
                    name, attempt.get("detail")))
        finally:
            claim.release()
            result["finished_utc"] = s4_state.utc()

    def write_baseline(self, entry):
        if self.baseline is not None:
            return
        doc = {"schema": "p3-code-baseline-v1", "job": self.args.job, "run": entry["run_name"],
               "source_sha256": self.current["source_sha256"], "versions": self.current["versions"],
               "written_utc": s4_state.utc()}
        written = self.store.put_json("%s/code_baseline/%s.json" % (self.base, self.args.job), doc)
        if written.get("ok"):
            self.baseline = doc
            log("train: code baseline written (first formal run of this experiment: %s)" % entry["run_name"])

    def attempt(self, entry, rel, key, claim, dest, number):
        args = self.args
        name = entry["run_name"]
        local = self.repo / entry["output_dir"]
        record = {"attempt": number, "started_utc": s4_state.utc()}
        record["set_aside"] = set_aside(local)

        def guard():
            """Write only while this job's claim is the winning one; a failed listing is not a lost claim."""
            held, why = claim.holds()
            if not held and why and why.startswith("could not list"):
                log("train: %s: claim check skipped (%s)" % (name, why))
                return True
            return held

        run_drive = s4_state.RunDrive(self.store, rel, key, args.job, name,
                                      keep=self.reg["checkpoints"]["keep_full_checkpoints_on_drive"], guard=guard)
        step, marker = run_drive.latest_verified()
        resume = None
        if step:
            restored = run_drive.restore(step, marker, local)
            record["restore"] = restored
            if not restored.get("ok"):
                record.update(outcome="restore_failed", detail="restore of checkpoint-%d failed: %s" % (
                    step, restored.get("reason")))
                return record
            resume = restored["path"]
            log("train: %s: restored checkpoint-%d from Drive (%d files checked)" % (name, step, restored["files"]))
        cmd = [args.python, "-m", args.train_module, "--registered", str(self.registry_path), "--arm", entry["arm"],
               "--seed", str(entry["seed"])]
        if args.model_path:
            cmd += ["--model-path", args.model_path]
        if resume:
            cmd += ["--resume", resume]
        attempt_dir = dest / ("attempt%d" % number)
        sup = s4_supervise.supervise(name, cmd, local, attempt_dir / "train.log", self.repo,
                                     env=dict(os.environ, PYTHONUNBUFFERED="1"), run_drive=run_drive,
                                     key_extra={"runtime_content_sha256": key["runtime_content_sha256"]},
                                     deadline=self.stop_at, heartbeat=claim.heartbeat,
                                     record_path=attempt_dir / "supervisor.json")
        record.update({k: sup.get(k) for k in ("outcome", "detail", "exit_code", "last_step", "max_steps", "wall_seconds",
                                               "startup_seconds", "step_seconds", "final_upload", "log_tail",
                                               "registration")})
        record["uploads"] = [{k: u.get(k) for k in ("step", "ok", "seconds", "reason")} for u in sup["uploads"]]
        record["collected"] = collect(local, dest)
        return record


def code_identity(python, repo, env=None):
    from scripts.colab.decide_pilot import code_identity as identity

    return identity(python, repo, env=env)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--session", default="")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--model-path")
    parser.add_argument("--max-hours", type=float)
    parser.add_argument("--vm-hours", type=float, default=24.0, help="VM lifetime counted from the container start; "
                                                                     "0 = no VM limit (then only --max-hours)")
    parser.add_argument("--cu-balance", type=float)
    parser.add_argument("--cu-rate", type=float)
    parser.add_argument("--cu-measured-epoch", type=float)
    parser.add_argument("--dry-run", action="store_true", help="read Drive and print the plan; write and run nothing")
    parser.add_argument("--drive-remote")
    parser.add_argument("--drive-dir")
    parser.add_argument("--drive-mount")
    parser.add_argument("--train-module", default=s4_supervise.TRAIN_MODULE, help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    Path(args.out).mkdir(parents=True, exist_ok=True)
    s4_supervise.install_sigterm()
    return Job(args).run()


if __name__ == "__main__":
    sys.exit(main())
