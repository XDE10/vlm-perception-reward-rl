#!/usr/bin/env python3
"""Own one B512 Colab session through its bounded run and evidence collection."""
from datetime import datetime, timezone, timedelta
import json
import hashlib
import math
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import time
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))
from resume_formal import resume_on_existing_gpu, verify_before_release

CLI_ROOT = Path.home() / ".local/bin"
SESSION = "p3-shuffle-formal-1117-162647-1"
REMOTE = "/content/shuffle-r1-formal"
BUDGET = int(os.environ["P3_FORMAL_BUDGET_SECONDS"])
ENV = {**os.environ, "COLAB_CLI_ASSIGN_RETRIES": "0"}
BEGIN = time.monotonic()
DEADLINE = BEGIN + BUDGET if BUDGET else None
BEIJING = timezone(timedelta(hours=8))
account = None
endpoint = None


def now():
    return datetime.now(BEIJING).strftime("%Y-%m-%d %H:%M:%S")


def log(message):
    print(f"[{now()}] {message}", flush=True)


def state(stage, **additional):
    path = ROOT / "status.json"
    pending = path.with_suffix(".tmp")
    info = {"time": now(), "stage": stage, "account": account, "session": SESSION,
            "endpoint": endpoint, "budget_seconds": BUDGET or None,
            "remaining_seconds": remaining() if BUDGET else None,
            **additional}
    pending.write_text(json.dumps(info, indent=2) + "\n")
    pending.replace(path)


def remaining(reserve=0):
    return max(0, math.floor(DEADLINE - time.monotonic() - reserve)) if BUDGET else math.inf


def call(acc, *command, capture=False, timeout=30, check=False, release=False, stdin=None):
    if not release:
        timeout = min(timeout, remaining(15))
        if timeout < 1:
            raise TimeoutError("GPU deadline reached")
    arguments = [str(CLI_ROOT / ("colab-" + acc)), *command]
    with subprocess.Popen(
        arguments, env=ENV, text=True, start_new_session=True,
        stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None,
        stdin=subprocess.DEVNULL if stdin is None else stdin,
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            raise
        result = subprocess.CompletedProcess(arguments, process.returncode, stdout, stderr)
        if check:
            result.check_returncode()
        return result


def find(acc, *, release=False):
    reply = call(acc, "sessions", capture=True, timeout=15, check=True, release=release)
    match = re.search(r"^\[" + re.escape(SESSION) + r"\]\s+(\S+)", reply.stdout, re.M)
    return match.group(1) if match else None


def remote(*args, **kwargs):
    return call(account, "ssh", "-s", SESSION, "--", *args, **kwargs)


def lookup_for_allocation(candidate):
    for _ in range(2):
        try:
            return find(candidate)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            log(f"Could not list sessions on account {candidate.upper()}; checking again")
            time.sleep(2)
    raise RuntimeError(f"Cannot verify sessions on account {candidate.upper()}")


def acquire():
    global account, endpoint
    for candidate in ('b',):
        try:
            existing = lookup_for_allocation(candidate)
        except RuntimeError as error:
            log(str(error))
            continue
        if not existing:
            account = candidate
            state("requesting_gpu")
            log(f"Requesting one G4 on account {candidate.upper()} as {SESSION}")
            try:
                call(candidate, "new", "-s", SESSION, "--gpu", "G4", timeout=80)
            except subprocess.TimeoutExpired:
                log(f"Account {candidate.upper()} allocation command timed out, checking the session")
            for _ in range(3):
                try:
                    endpoint = lookup_for_allocation(candidate)
                except RuntimeError as error:
                    log(str(error))
                    continue
                if endpoint:
                    state("gpu_allocated")
                    log(f"Allocated {endpoint} on account {candidate.upper()}")
                    return
                time.sleep(2)
            log(f"Account {candidate.upper()} did not create the named G4 session")
            account = None
        else:
            log(f"The name {SESSION} is already in use on account {candidate.upper()}")
    raise RuntimeError("G4 allocation failed on the selected accounts")


def launch():
    state("configuring_storage")
    config = Path(os.environ.get(
        "RCLONE_CONFIG", CLI_ROOT.parent.parent / ".config/rclone/rclone.conf",
    ))
    storage_command = "umask 077; cat > /content/.p3-overnight-rclone.conf; test -s /content/.p3-overnight-rclone.conf"
    for attempt in range(3):
        try:
            with config.open("rb") as stream:
                result = remote("bash", "-lc", storage_command, capture=True, timeout=25, stdin=stream)
            if result.returncode == 0:
                break
        except subprocess.TimeoutExpired:
            pass
    else:
        raise RuntimeError("Could not initialize the existing private Drive storage")
    state("uploading_and_launching")
    payload = ROOT / "payload.tgz"
    with payload.open("rb") as stream:
        payload_digest = hashlib.file_digest(stream, "sha256").hexdigest()
    duration = remaining(180)
    if duration < 1:
        raise TimeoutError("no time left to launch")
    training_command = f"timeout --signal=TERM --kill-after=12s {duration}s " if BUDGET else ""
    launch_command = (
        f"set -e; mkdir -p {REMOTE}; cd {REMOTE}; exec 8>launch.lock; flock 8; "
        "if [ -s probe.pid ]; then printf 'REMOTE_PID=%s\\n' \"$(cat probe.pid)\"; exit 0; fi; "
        'if ! command -v rclone >/dev/null; then apt-get install -y -qq rclone || (apt-get update -qq && apt-get install -y -qq rclone); fi; rclone --config /content/.p3-overnight-rclone.conf copyto mydrive:ColabProjects/vlm-perception-reward-rl/shuffle-r1-overnight-20261116/launch-payloads/p3-shuffle-formal-1117-162647-1.tgz payload.pending --retries 2; '
        f"printf '%s  %s\\n' {payload_digest} payload.pending | sha256sum -c - >&2; "
        f"tar -xzf payload.pending -C {REMOTE}; rm -f payload.pending; "
        f"nohup {training_command}bash run_remote.sh "
        ">run.log 2>&1 </dev/null 8>&- & pid=$!; printf '%s\\n' \"$pid\" > probe.pid; printf 'REMOTE_PID=%s\\n' \"$pid\""
    )
    for _ in range(4):
        try:
            response = remote("bash", "-lc", launch_command, capture=True, timeout=240)
        except subprocess.TimeoutExpired:
            log("SSH upload or launch timed out, checking the same session")
            time.sleep(2)
            continue
        match = re.search(r"REMOTE_PID=(\d+)", response.stdout)
        if response.returncode == 0 and match:
            pid = int(match.group(1))
            break
        log(f"SSH launch acknowledgement unavailable, retrying on the same session (code {response.returncode}): {response.stderr[-400:]}")
        time.sleep(2)
    else:
        raise RuntimeError("Could not acknowledge launch on the allocated GPU")
    log("Launch verified from Drive")
    try:
        subprocess.run(["rclone", "deletefile", 'mydrive:ColabProjects/vlm-perception-reward-rl/shuffle-r1-overnight-20261116/launch-payloads/p3-shuffle-formal-1117-162647-1.tgz', "--retries", "1"], timeout=25)
    except (OSError, subprocess.TimeoutExpired):
        log("Temporary Drive launch payload cleanup can be retried")
    state("running", remote_pid=pid)
    log(f"Bounded remote probe launched, pid {pid}, working directory {REMOTE}")
    # The detached job logs its GPU identity before preparing its environment.
    return pid


def follow(pid):
    # The remote process is detached. An SSH reconnect only reattaches logs.
    attempt = 0
    while not BUDGET or attempt < 4:
        seconds = remaining(45) if BUDGET else 1800
        if seconds <= 0:
            return
        option = ["-n", "+1"] if attempt == 0 else ["-n", "50"]
        attempt += 1
        try:
            if not BUDGET and find(account, release=True) != endpoint:
                log(f"Confirmed runtime {SESSION} is no longer assigned to this job")
                return
            follow_command = (
                f"tail {shlex.join(option)} -F {REMOTE}/run.log & listener=$!; "
                f"while kill -0 {pid} 2>/dev/null && [ ! -f {REMOTE}/evidence.tgz ]; do sleep 3; done; "
                'sleep 2; kill "$listener" 2>/dev/null || true; wait "$listener" 2>/dev/null || true'
            )
            tail = remote("bash", "-lc", follow_command, timeout=seconds)
            if tail.returncode == 0:
                return
        except subprocess.TimeoutExpired:
            if BUDGET:
                return
        except subprocess.CalledProcessError:
            pass
        log("SSH log connection dropped; reconnecting to the existing job")
        time.sleep(min(2, remaining(45)))
    state("log_connection_unstable", remote_pid=pid)
    while remaining(45) > 0:
        try:
            if remote("test", "-f", REMOTE + "/evidence.tgz", timeout=10).returncode == 0:
                return
        except subprocess.TimeoutExpired:
            pass
        time.sleep(min(15, remaining(45)))


def collect():
    timeout = min(35, remaining(25))
    if timeout < 1:
        return None
    path = ROOT / "evidence.tgz"
    try:
        ret = call(account, "download", "-s", SESSION, REMOTE + "/evidence.tgz", str(path), timeout=timeout)
    except subprocess.TimeoutExpired:
        log("Compact evidence download timed out")
        return None
    if ret.returncode != 0 or not path.is_file():
        return None
    import tarfile
    with tarfile.open(path) as bundle:
        code = bundle.extractfile("evidence/remote-exit-code.txt")
        rc = int(code.read()) if code is not None else None
        bundle.extractall(ROOT, filter="data")
    return rc


def release():
    if account is None or endpoint is None:
        return True
    for i in range(3):
        try:
            current = find(account, release=True)
            if current is None:
                log(f"Verified {SESSION} is no longer listed on account {account.upper()}")
                return True
            if current != endpoint:
                log(f"The session name now belongs to {current}; leaving it alone")
                return False
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            log(f"Could not list the owned session, releasing the allocated alias {SESSION}")
        try:
            call(account, "stop", "-s", SESSION, timeout=15, release=True)
        except subprocess.TimeoutExpired:
            log("Release call timed out, checking session state")
    try:
        return find(account, release=True) is None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def interrupt(_sig, _frame):
    raise KeyboardInterrupt


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, interrupt)
    result, failure = None, None
    try:
        acquire()
        pid = launch()
        follow(pid)
        state("collecting_evidence")
        result = collect()
        if result is None:
            failure = "probe did not produce verified completion evidence within the budget"
        elif result != 0:
            failure = f"GPU probe exited with {result}"
    except (Exception, KeyboardInterrupt) as error:
        failure = f"{type(error).__name__}: {error}"
        log(failure)
    finally:
        confirmation = None
        released = endpoint is None
        publication_retried = False
        while endpoint is not None:
            try:
                state("verifying_drive_before_release", result=result)
                confirmation = verify_before_release(ROOT, result == 0)
            except (OSError, KeyError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
                verification_failure = f"Drive verification before GPU release: {error}"
                log(verification_failure)
                state("awaiting_drive_verification", result=result, error=verification_failure)
                try:
                    released = find(account, release=True) is None
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass
                if released or not remaining(15):
                    failure = verification_failure
                    break
                if (not publication_retried and result is not None and remaining(60) >= 120
                        and (ROOT / "evidence/latest-local-checkpoint-manifest.json").is_file()):
                    publication_retried = True
                    republish = (
                        f"cd {REMOTE}; export RCLONE_CONFIG=/content/.p3-overnight-rclone.conf; "
                        "read -r deadline target P3_FORMAL_RESUME_STEP < run-target.txt; "
                        "export P3_FORMAL_RESUME_STEP; "
                        "bash persist_checkpoint.sh checkpoints/qwen25vl3b_b512_seed1 "
                        "mydrive:ColabProjects/vlm-perception-reward-rl/shuffle-r1-overnight-20261116 "
                        "evidence"
                    )
                    try:
                        log("Retrying final checkpoint publication on the existing GPU")
                        remote("bash", "-lc", republish, timeout=min(remaining(45), 1800))
                    except subprocess.SubprocessError:
                        log("Final publication retry ended without acknowledgement")
                time.sleep(min(20, remaining(15)))
            else:
                training_exit = ROOT / "evidence/training-exit-code.txt"
                if publication_retried and training_exit.is_file() and training_exit.read_text().strip() == "0":
                    target = int((ROOT / "payload/run-target.txt").read_text().split()[1])
                    if confirmation["step"] >= target:
                        result, failure = 0, None
                log(f"Drive marker and manifest confirmed before release at step {confirmation['step']}")
                if confirmation.get("validation_steps"):
                    log(f"Drive validation confirmed before release at steps {confirmation['validation_steps']}")
                state("releasing", result=result, drive_confirmation=confirmation)
                released = release()
                break
        status = "completed" if result == 0 and released and confirmation else "failed"
        state(status, result=result, error=failure, released=released, drive_confirmation=confirmation)
        log(f"Final status {status}, GPU released={released}, remote exit={result}")
