"""Run a task's steps on the VM, keep the kernel busy, package results (standard library only).

Called from ``colab/kernel_job.py`` inside the Colab kernel. Each step is a
subprocess in its own process group with a timeout; its output goes to
``<out>/logs/<step>.log``. ``<out>/status.json`` is rewritten atomically after
every step and every heartbeat so the launcher can poll it through the Jupyter
contents API even while the kernel is busy. At the end the run directory is
packaged (weights and checkpoints excluded) and split into parts. If the user put
a GitHub credential on the VM, the VM pushes the results branch itself
(``push_to_github``, D37); if the request asks for it and rclone can reach the
user's Drive, a verified copy goes to Drive (``persist_to_drive``). The part
list and both outcomes are written to ``<root>/out/<run_id>.done.json`` and
``JOB_DONE`` is printed.
"""
import gzip
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from pathlib import Path

from scripts.colab.common import (PART_BYTES, Heartbeat, format_seconds, log, read_json, sha256_file, split_file, tail,
                                  write_json)

STATUS_SCHEMA = "p3-job-status-v1"
HEARTBEAT_SECONDS = 60.0
POLL_SECONDS = 5.0
EXCLUDED_DIRS = ("checkpoint-",)
EXCLUDED_DIR_NAMES = {"final", "__pycache__"}
EXCLUDED_SUFFIXES = (".safetensors", ".bin", ".pt", ".pth", ".ckpt", ".tmp")
GZIP_ABOVE_BYTES = 20 * 1024 * 1024
SKIP_ABOVE_BYTES = 200 * 1024 * 1024
DRIVE_TIMEOUTS = {"results": 1800, "full": 4 * 3600}
DRIVE_SUMMARY_KEYS = ["ok", "attempted", "verified", "target", "files", "bytes", "copy_seconds", "check_seconds", "reason"]


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Job(object):
    def __init__(self, root, request):
        self.root = Path(root)
        self.request = request
        self.run_id = request["run_id"]
        self.out = self.root / "out" / self.run_id
        self.logs = self.out / "logs"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.status = {"schema": STATUS_SCHEMA, "run_id": self.run_id, "task": request["task"], "state": "starting",
                       "started_utc": _now(), "updated_utc": _now(), "steps": [], "current": None}
        self.proc = None
        self.github_check = None

    def save(self):
        self.status["updated_utc"] = _now()
        write_json(self.out / "status.json", self.status)

    def _step_record(self, name):
        return next(s for s in self.status["steps"] if s["name"] == name)

    def run_step(self, step):
        record = self._step_record(step["name"])
        failed_deps = [d for d in step.get("depends_on", []) if self._step_record(d)["state"] != "passed"]
        if failed_deps:
            record.update(state="skipped", reason="dependency not passed: " + ",".join(failed_deps))
            log("step %s skipped (%s)" % (step["name"], record["reason"]))
            self.save()
            return
        log_path = self.logs / (step["name"] + ".log")
        env = dict(os.environ)
        env.update({k: str(v) for k, v in step.get("env", {}).items()})
        env.setdefault("PYTHONUNBUFFERED", "1")
        code = self.request.get("code", {})
        if code.get("commit"):  # the VM checkout is a git-archive export; run identities still record the commit
            env["P3_GIT_COMMIT"] = code["commit"] + ("-dirty" if code.get("dirty") else "")
        started = time.time()
        record.update(state="running", started_utc=_now(), log="logs/%s.log" % step["name"])
        self.status["current"] = {"step": step["name"], "elapsed": "0m00s", "last": ""}
        self.save()
        log("step %s started: %s" % (step["name"], " ".join(str(c) for c in step["cmd"])[:300]))
        with open(str(log_path), "ab") as handle:
            self.proc = subprocess.Popen([str(c) for c in step["cmd"]], cwd=str(step.get("cwd", self.root / "repo")),
                                         env=env, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
            next_beat = time.time() + HEARTBEAT_SECONDS
            timeout = step.get("timeout", 3600)
            rc = None
            while rc is None:
                try:
                    rc = self.proc.wait(timeout=POLL_SECONDS)
                except subprocess.TimeoutExpired:
                    rc = None
                elapsed = time.time() - started
                if rc is None and elapsed > timeout:
                    self._kill()
                    rc = "timeout"
                    break
                if time.time() >= next_beat:
                    last = tail(log_path, 1)[:200]
                    self.status["current"] = {"step": step["name"], "elapsed": format_seconds(elapsed), "last": last}
                    self.save()
                    log("%s running %s | %s" % (step["name"], format_seconds(elapsed), last))
                    next_beat = time.time() + HEARTBEAT_SECONDS
        self.proc = None
        seconds = time.time() - started
        state = "passed" if rc == 0 else ("timeout" if rc == "timeout" else "failed")
        record.update(state=state, exit_code=None if rc == "timeout" else rc, seconds=round(seconds, 1),
                      finished_utc=_now())
        if state != "passed":
            record["log_tail"] = tail(log_path, 25)
        self.status["current"] = None
        self.save()
        log("step %s %s in %s" % (step["name"], state.upper(), format_seconds(seconds)))

    def _kill(self):
        if self.proc is None:
            return
        try:
            os.killpg(self.proc.pid, signal.SIGTERM)
            self.proc.wait(timeout=30)
        except Exception:
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)
            except Exception:
                pass

    def package(self):
        """Copy the run directory minus weights/checkpoints into a tar.gz split into parts."""
        stage = self.root / "out" / (self.run_id + ".stage")
        if stage.exists():
            shutil.rmtree(str(stage))
        skipped, gzipped = [], []
        for path in sorted(self.out.rglob("*")):
            rel = path.relative_to(self.out)
            if any(part.startswith(EXCLUDED_DIRS) or part in EXCLUDED_DIR_NAMES for part in rel.parts[:-1]):
                continue
            if not path.is_file():
                continue
            size = path.stat().st_size
            if path.name.endswith(EXCLUDED_SUFFIXES) or path.name.startswith("optimizer"):
                skipped.append({"path": str(rel), "bytes": size, "reason": "weights_or_state"})
                continue
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if size > SKIP_ABOVE_BYTES and not path.name.endswith((".jsonl", ".log", ".txt", ".json")):
                skipped.append({"path": str(rel), "bytes": size, "reason": "too_large"})
                continue
            if size > GZIP_ABOVE_BYTES and not path.name.endswith(".gz"):
                with open(str(path), "rb") as source, gzip.open(str(target) + ".gz", "wb", compresslevel=6) as out:
                    shutil.copyfileobj(source, out)
                gzipped.append(str(rel))
            else:
                shutil.copy2(str(path), str(target))
        write_json(stage / "PACKAGING.json", {"skipped": skipped, "gzipped": gzipped, "packaged_utc": _now()})
        archive = self.root / "out" / (self.run_id + ".results.tar.gz")
        with tarfile.open(str(archive), "w:gz") as tar:
            tar.add(str(stage), arcname=self.run_id)
        shutil.rmtree(str(stage))
        # the launcher downloads these parts through the same proxy that limits uploads: keep them small
        parts = split_file(archive, int(self.request.get("part_bytes") or PART_BYTES))
        return {"name": archive.name, "sha256": sha256_file(archive), "bytes": archive.stat().st_size, "parts": parts,
                "skipped": len(skipped), "gzipped": gzipped}

    def check_github(self):
        """Before the steps: can this VM push the results itself (D37)? Never raises."""
        try:
            from scripts.colab import vm_github

            info = vm_github.check(self.root, self.request)
            vm_github.report(self.out, info)
        except Exception as exc:
            info = {"ok": False, "reason": "%s: %s" % (type(exc).__name__, str(exc)[:300])}
        self.status["github_check"] = {k: info.get(k) for k in ("mode", "ok", "credentials_present", "push_access",
                                                                 "branch", "reason", "warning")}
        self.save()
        return info

    def push_to_github(self, package):
        """After packaging: push results/<run_id> from the VM; the launcher pushes instead if this fails."""
        try:
            from scripts.colab import vm_github

            with Heartbeat("pushing the results to GitHub", HEARTBEAT_SECONDS):
                result = vm_github.push(self.root, self.request, self.root / "out" / package["name"],
                                        overall=self.status.get("overall"), prior_check=self.github_check)
        except Exception as exc:
            result = {"attempted": True, "ok": False, "reason": "%s: %s" % (type(exc).__name__, str(exc)[:300])}
        if result.get("ok"):
            log("results pushed from the VM to %s (commit %s)" % (result["branch"], (result.get("commit") or "?")[:12]))
        elif result.get("attempted"):
            log("WARNING: the VM could not push the results (%s); the launcher will push them" % result.get("reason"))
        return result

    def persist_to_drive(self, package):
        """Optional verified copy to the user's Google Drive (rclone). Never raises, never fails the job.

        ``drive_persist``: "results" copies the results archive (small, no weights); "full" copies the whole
        run directory including checkpoints and adapters; anything else does nothing."""
        options = self.request.get("options") or {}
        mode = options.get("drive_persist") or "none"
        if mode not in DRIVE_TIMEOUTS:
            return {"mode": mode, "ok": False, "attempted": False, "reason": "not requested for this run"}
        staging = None
        try:
            from scripts.colab import drive

            if mode == "results":
                staging = self.root / "out" / (self.run_id + ".drive")
                if staging.exists():
                    shutil.rmtree(str(staging))
                staging.mkdir(parents=True)
                archive = self.root / "out" / package["name"]
                try:
                    os.link(str(archive), str(staging / archive.name))
                except OSError:
                    shutil.copy2(str(archive), str(staging / archive.name))
                write_json(staging / "package.json", dict(package, run_id=self.run_id, overall=self.status.get("overall")))
                source = staging
            else:
                source = self.out
            with Heartbeat("copying %s to Google Drive" % mode, HEARTBEAT_SECONDS):
                result = drive.persist(source, "runs/" + self.run_id, remote=options.get("drive_remote"),
                                       base_dir=options.get("drive_dir"), mount=options.get("drive_mount"),
                                       timeout=DRIVE_TIMEOUTS[mode])
            summary = {key: result.get(key) for key in DRIVE_SUMMARY_KEYS}
        except Exception as exc:  # Drive is a convenience copy; GitHub results stay the record of the run
            summary = {"ok": False, "attempted": True, "reason": "%s: %s" % (type(exc).__name__, str(exc)[:300])}
        finally:
            if staging is not None:
                shutil.rmtree(str(staging), ignore_errors=True)
        summary["mode"] = mode
        if summary.get("attempted"):
            log("Drive copy (%s): %s %s" % (mode, "verified" if summary.get("ok") else "FAILED",
                                            summary.get("target") or summary.get("reason") or ""))
        else:
            log("Drive copy (%s) skipped: %s" % (mode, (summary.get("reason") or "")[:200]))
        return summary

    def overall(self):
        required = [s for s in self.status["steps"] if s.get("required", True)]
        return "passed" if required and all(s["state"] == "passed" for s in required) else "failed"


def run_job(root, request):
    from scripts.colab import tasks

    job = Job(root, request)
    bootstrap_path = Path(root) / "state" / "bootstrap.json"
    bootstrap = read_json(bootstrap_path) if bootstrap_path.is_file() else {"ok": False, "error": "bootstrap missing"}
    steps = []
    try:
        if not bootstrap.get("ok"):
            raise RuntimeError("bootstrap did not succeed: %s" % bootstrap.get("error"))
        context = tasks.Context(Path(root), request, bootstrap, kernel_python=sys.executable)
        steps = tasks.steps_for(context)
        tasks.prepare(context)
        job.status["steps"] = [{"name": s["name"], "state": "pending", "required": s.get("required", True),
                                "description": s.get("description", "")} for s in steps]
        job.status["state"] = "running"
        job.save()
        job.github_check = job.check_github()
        log("job %s: %d steps" % (job.run_id, len(steps)))
        for step in steps:
            job.run_step(step)
    except KeyboardInterrupt:
        job._kill()
        job.status["interrupted"] = True
        log("job interrupted")
    except Exception as exc:  # orchestration errors are reported in status, never swallowed silently
        job.status["error"] = "%s: %s" % (type(exc).__name__, str(exc)[-2000:])
        log("job error: %s" % job.status["error"])
    finally:
        job.status["state"] = "summarizing"
        job.save()
        try:
            from scripts.colab import summarize_run

            python = bootstrap.get("envs", {}).get("base", {}).get("python", sys.executable)
            with open(str(job.logs / "summarize.log"), "ab") as handle:
                subprocess.run([python, "-m", "scripts.colab.summarize_run", "--out-dir", str(job.out)],
                               cwd=str(Path(root) / "repo"), timeout=900, check=False, stdout=handle,
                               stderr=subprocess.STDOUT)
            if not (job.out / "summary.json").is_file():
                summarize_run.minimal(job.out)
        except Exception as exc:
            job.status["summary_error"] = "%s: %s" % (type(exc).__name__, exc)
        overall = job.overall() if not job.status.get("error") else "failed"
        summary_path = job.out / "summary.json"
        if overall == "passed" and summary_path.is_file():
            overall = read_json(summary_path).get("overall", overall)  # summary checks can veto a pass
        job.status["overall"] = overall
        job.status["state"] = "packaging"
        job.save()
        package = job.package()
        job.status["package"] = package
        job.status["state"] = "github_push"  # small and the primary record: before the (possibly long) Drive copy
        job.save()
        job.status["github"] = job.push_to_github(package)
        job.status["state"] = "drive_copy"
        job.save()
        job.status["drive"] = job.persist_to_drive(package)
        job.status["state"] = "done"
        job.status["finished_utc"] = _now()
        job.save()
        write_json(Path(root) / "out" / (job.run_id + ".done.json"),
                   {"run_id": job.run_id, "overall": job.status["overall"], "package": package,
                    "github": job.status["github"], "drive": job.status["drive"],
                    "finished_utc": job.status["finished_utc"]})
        log("JOB_DONE overall=%s package=%s (%d parts, %.1f MB)" % (job.status["overall"], package["name"],
                                                                     len(package["parts"]), package["bytes"] / 1e6))
    return job.status


__all__ = ["Job", "run_job"]
