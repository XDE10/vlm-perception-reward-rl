"""Resume the same formal Shuffle-R1 training from verified private storage."""
import argparse
import base64
import datetime
import fcntl
import json
import math
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tarfile
import time

import continue_experiment as runner
from formal_validation import FREQUENCY, result_path, validate_record


MAX_STEPS = 150
SECONDS_PER_STEP = 3710  # Formal step 2, including local save and readback.
RESERVE_SECONDS = 4200
DAYTIME_GUARD = "# A replacement runtime follows the same one-step limit.\nstop_step=1\n"
READ_RUN_TARGET = "read -r deadline stop_step resume_step < run-target.txt"
VALIDATE_RUN_TARGET = '[[ "$deadline" =~ ^[0-9]+$ && "$stop_step" =~ ^[1-9][0-9]*$ && "$resume_step" =~ ^[0-9]+$ ]]'
SESSION_PREFIX = re.compile(r"^\[(p3-shuffle-(?:night-1116|formal-)[^\]]*)\]", re.MULTILINE)


def verify_no_formal_sessions(accounts=("c", "a")):
    for account in accounts:
        cli = Path.home() / ".local/bin" / f"colab-{account}"
        try:
            result = subprocess.run(
                [str(cli), "sessions"], capture_output=True, text=True, check=True, timeout=25,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError(f"Cannot confirm formal session ownership on Colab account {account.upper()}") from exc
        aliases = SESSION_PREFIX.findall(result.stdout)
        if aliases:
            raise RuntimeError(f"Formal session already active on {account.upper()}: {', '.join(aliases)}")


def require_verified_checkpoint(expected_manifest, minimum):
    error = None
    for attempt in range(3):
        try:
            checkpoint = runner.read_private_checkpoint(expected_manifest, minimum)
            if checkpoint is not None and minimum <= checkpoint["step"] <= MAX_STEPS:
                return checkpoint
            error = None
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, RuntimeError) as exc:
            error = exc
        if attempt < 2:
            time.sleep(2)
    raise RuntimeError(f"Cannot confirm the Drive marker and manifest at step {minimum} or later") from error


def plan_stop_step(latest, remaining):
    available = max(0, remaining - RESERVE_SECONDS)
    return min(MAX_STEPS, latest + available // SECONDS_PER_STEP)


def configure_resume_script(path):
    source = path.read_text()
    if (source.count(DAYTIME_GUARD) != 1 or source.count(READ_RUN_TARGET) != 1
            or source.count(VALIDATE_RUN_TARGET) != 1):
        raise RuntimeError("The formal resume template does not match its expected stop-step inputs")
    patched = source.replace(DAYTIME_GUARD, "", 1)
    if re.search(r"^\s*stop_step\s*=", patched, re.MULTILINE):
        raise RuntimeError("A fixed stop-step override remains in the formal resume payload")
    patched = patched.replace(
        VALIDATE_RUN_TARGET,
        VALIDATE_RUN_TARGET + '\n(( resume_step > 0 && stop_step > resume_step )) || {\n'
        "    echo 'Invalid formal resume range' >&2\n"
        "    exit 2\n"
        "}",
        1,
    )
    path.write_text(patched)
    subprocess.run(["bash", "-n", str(path)], check=True)


def configure_continuous_payload(base, payload):
    shutil.copy2(base / "formal_validation.py", payload)
    publisher = payload / "persist_checkpoint.sh"
    source = publisher.read_text()
    step_line = 'step=${latest##*_}'
    stage_line = 'cp -al -- "$latest" "$stage"'
    if source.count(step_line) != 1 or source.count(stage_line) != 1:
        raise RuntimeError("Could not configure checkpoint publication cadence")
    source = source.replace(
        step_line,
        step_line + '\ninterval=${4:-1}\n'
        f'(( step % interval == 0 || step % {FREQUENCY} == 0 )) || exit 0',
        1,
    )
    source = source.replace(
        stage_line,
        'python3 "$(dirname "$evidence")/formal_validation.py" '
        '"$evidence" "$drive" "$P3_FORMAL_RESUME_STEP" "$latest"\n' + stage_line,
        1,
    )
    publisher.write_text(source)
    script = payload / "run_remote.sh"
    source = script.read_text()
    periodic = 'bash "$root/persist_checkpoint.sh" "$checkpoint_root" "$drive" "$root/evidence" || true'
    if source.count(periodic) != 1:
        raise RuntimeError("Could not locate periodic checkpoint publication")
    source = source.replace(periodic, periodic.replace(" || true", " 2 || true"), 1)
    archive_line = '    tar -C "$root" -czf "$root/evidence.tgz" evidence || true'
    if source.count(archive_line) != 1:
        raise RuntimeError("Could not locate formal evidence archive")
    source = source.replace(
        archive_line,
        """    latest_manifest=$(find "$checkpoint_root" -mindepth 2 -maxdepth 2 -name manifest.json -print 2>/dev/null |
        awk -F / '$(NF-1) ~ /^global_step_[1-9][0-9]*$/' | sort -V | tail -n 1) || true
    if [[ -n "$latest_manifest" ]]; then
        cp "$latest_manifest" "$root/evidence/latest-local-checkpoint-manifest.json"
    fi
""" + archive_line,
        1,
    )
    script.write_text(source.replace(
        'export RCLONE_CONFIG=',
        'export P3_FORMAL_RESUME_STEP="$resume_step"\nexport RCLONE_CONFIG=',
        1,
    ))
    for path in (script, publisher):
        subprocess.run(["bash", "-n", str(path)], check=True)


def verify_validations(identity, through, evidence=None):
    for step in range(FREQUENCY, through + 1, FREQUENCY):
        for attempt in range(3):
            try:
                data = runner.read_drive("cat", result_path(runner.DRIVE, step))
                break
            except (OSError, subprocess.SubprocessError) as error:
                if attempt == 2:
                    raise RuntimeError(f"Could not read fixed-dev results for step {step}") from error
                time.sleep(2)
        validate_record(json.loads(data), step, identity)
        if evidence is not None:
            saved = evidence / f"validation-step-{step}.json"
            if saved.exists() and saved.read_bytes() != data:
                raise RuntimeError(f"Validation on Drive differs from saved results at step {step}")


def verify_before_release(folder, successful):
    startup = json.loads((folder / "drive-resume-verification.json").read_text())
    reference = json.loads(
        (folder.parents[1] / "formal/evidence/first-step-verified-manifest.json").read_text()
    )
    minimum = startup["step"]
    if successful:
        _, minimum, _ = map(int, (folder / "payload/run-target.txt").read_text().split())
        saved = json.loads((folder / "evidence/persisted-checkpoint-manifest.json").read_text())
        if saved["global_step"] != minimum or saved["identity"] != reference["identity"]:
            raise RuntimeError("The final evidence does not identify this formal target checkpoint")
        reference = saved
    local_manifest = folder / "evidence/latest-local-checkpoint-manifest.json"
    if local_manifest.exists():
        saved = json.loads(local_manifest.read_text())
        if saved["identity"] != reference["identity"] or saved["global_step"] < minimum:
            raise RuntimeError("The latest local checkpoint has an unexpected identity or step")
        minimum = saved["global_step"]
        reference = saved
    confirmation = require_verified_checkpoint(reference, minimum)
    if (folder / "payload/formal_validation.py").is_file():
        verify_validations(reference["identity"], confirmation["step"], folder / "evidence")
        confirmation["validation_steps"] = list(range(FREQUENCY, confirmation["step"] + 1, FREQUENCY))
    return confirmation


def prepare_drive_payload(folder, session):
    remote = f"{runner.DRIVE}/launch-payloads/{session}.tgz"
    for attempt in range(3):
        try:
            subprocess.run(
                ["rclone", "copyto", str(folder / "payload.tgz"), remote, "--retries", "2",
                 "--drive-chunk-size", "64M", "--stats", "30s", "--stats-log-level", "NOTICE"],
                check=True, timeout=600,
            )
            return remote
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            if attempt == 2:
                raise
            print(f"Launch-payload transfer will retry on the same Drive, attempt {attempt + 2}", flush=True)
            time.sleep(5)


def resume_on_existing_gpu(folder, confirmation, remote):
    encoded = base64.b64encode((folder / "payload/run_remote.sh").read_bytes()).decode()
    target = int((folder / "payload/run-target.txt").read_text().split()[1])
    step = confirmation["step"]
    digest = confirmation["manifest_sha256"]
    if not re.fullmatch(r"[a-f0-9]{64}", digest) or not 0 < step < target <= MAX_STEPS:
        raise RuntimeError("Invalid verified warm-resume state")
    target_text = shlex.quote(f"0 {target} {step}\n")
    command = (
        "set -e; cd /content/shuffle-r1-formal; exec 8>launch.lock; flock 8; "
        "if test -s continuation.pid; then printf 'REMOTE_PID=%s\\n' \"$(cat continuation.pid)\"; exit 0; fi; "
        "test -f evidence.tgz || test -f evidence-before-continuation.tgz; "
        f"printf %s {shlex.quote(encoded)} | base64 -d > run-continuation.sh; bash -n run-continuation.sh; "
        "env/bin/ray stop --force > evidence/ray-before-continuation.log 2>&1 || true; "
        "if test -f evidence.tgz; then mv evidence.tgz evidence-before-continuation.tgz; "
        "mv run.log run-before-continuation.log; fi; "
        f"printf %s {target_text} > run-target.txt; "
        "rm -f evidence/remote-exit-code.txt evidence/training-exit-code.txt; "
        f"export P3_FORMAL_WARM_RESUME=1 P3_WARM_MANIFEST_SHA={digest}; "
        "nohup bash run-continuation.sh >run.log 2>&1 </dev/null 8>&- & "
        "pid=$!; printf '%s\\n' \"$pid\" > continuation.pid; "
        "printf '%s\\n' \"$pid\" > probe.pid; printf 'REMOTE_PID=%s\\n' \"$pid\""
    )
    for _ in range(3):
        try:
            response = remote("bash", "-lc", command, capture=True, timeout=90, release=True)
        except subprocess.TimeoutExpired:
            continue
        match = re.search(r"REMOTE_PID=(\d+)", response.stdout)
        if response.returncode == 0 and match:
            return int(match[1])
        raise RuntimeError(f"Failed to continue on the same VM: {response.stderr[-500:]}")
    raise RuntimeError("The same-VM continuation could not be acknowledged")


def configure_launcher(template, session, accounts=("c", "a"), drive_payload=None, adopt=None):
    release_line = '        released = release()'
    if template.count(release_line) != 1:
        raise RuntimeError("The launcher does not match its expected release point")
    verify_then_release = """        confirmation = None
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
"""
    template = template.replace("import time\n", "import time\nimport sys\n", 1)
    template = template.replace(
        "CLI_ROOT = Path.home()",
        "sys.path.insert(0, str(ROOT.parents[1]))\n"
        "from resume_formal import resume_on_existing_gpu, verify_before_release\n\n"
        "CLI_ROOT = Path.home()",
        1,
    )
    template = template.replace('for candidate in ("c", "a"):', f"for candidate in {accounts!r}:", 1)
    if adopt is not None:
        original = '        acquire()\n        pid = launch()\n        follow(pid)\n        state("collecting_evidence")\n        result = collect()'
        if template.count(original) != 1:
            raise RuntimeError("Could not locate launcher attachment point")
        attached = f"""        account = {adopt['account']!r}
        endpoint = {adopt['endpoint']!r}
        pid = {int(adopt['remote_pid'])}
        if find(account, release=True) == endpoint:
            state("running", remote_pid=pid, adopted=True)
            log(f"Attached to existing GPU {{SESSION}}, training PID {{pid}}")
            follow(pid)
            state("collecting_evidence")
            result = collect()
            if result is None and find(account, release=True) == endpoint:
                result = collect()
            if result in (0, 31, 124, 137, 143) and find(account, release=True) == endpoint:
                anchor = verify_before_release(ROOT, False)
                target = int((ROOT / "payload/run-target.txt").read_text().split()[1])
                if anchor["step"] < target:
                    pid = resume_on_existing_gpu(ROOT, anchor, remote)
                    state("running", remote_pid=pid, adopted=True, resume_step=anchor["step"])
                    log(f"Continuing on the same GPU from verified step {{anchor['step']}}, target={{target}}, PID {{pid}}")
                    follow(pid)
                    state("collecting_evidence")
                    result = collect()
        elif find(account, release=True) is not None:
            raise RuntimeError("The session alias belongs to a different VM")
"""
        template = template.replace(original, attached.rstrip(), 1)
    if drive_payload is not None:
        source = '"cat > payload.pending; "'
        call = ('            with payload.open("rb") as stream:\n'
                '                response = remote("bash", "-lc", launch_command, capture=True, timeout=180, stdin=stream)')
        if template.count(source) != 1 or template.count(call) != 1:
            raise RuntimeError("Could not configure direct Drive deployment")
        transfer = (
            "if ! command -v rclone >/dev/null; then "
            "apt-get install -y -qq rclone || (apt-get update -qq && apt-get install -y -qq rclone); fi; "
            "rclone --config /content/.p3-overnight-rclone.conf copyto "
            f"{shlex.quote(drive_payload)} payload.pending --retries 2; "
        )
        template = template.replace(source, repr(transfer), 1).replace(
            call, '            response = remote("bash", "-lc", launch_command, capture=True, timeout=240)', 1,
        )
        template = template.replace(
            '    state("running", remote_pid=pid)',
            f'    log("Launch verified from Drive")\n'
            f'    try:\n'
            f'        subprocess.run(["rclone", "deletefile", {drive_payload!r}, "--retries", "1"], timeout=25)\n'
            f'    except (OSError, subprocess.TimeoutExpired):\n'
            f'        log("Temporary Drive launch payload cleanup can be retried")\n'
            '    state("running", remote_pid=pid)',
            1,
        )
    template = template.replace(release_line, verify_then_release.rstrip(), 1)
    template = template.replace('        state("releasing", result=result, error=failure)\n', "", 1)
    template = template.replace(
        'status = "completed" if result == 0 and released else "failed"',
        'status = "completed" if result == 0 and released and confirmation else "failed"',
        1,
    )
    template = template.replace(
        'state(status, result=result, error=failure, released=released)',
        'state(status, result=result, error=failure, released=released, drive_confirmation=confirmation)',
        1,
    )
    launcher = template.replace("p3-shuffle-night-1116", session)
    compile(launcher, "launch.py", "exec")
    return launcher


def resume(base, hours, lock_fd, stop_after_step=MAX_STEPS, min_resume_step=1,
           accounts=("c", "a"), continuous=False, adopt=None):
    day = runner.status(base)
    if day["stage"] not in {"completed", "stopped_formal"} or day.get("gpu_released") is not True:
        raise RuntimeError("The daytime formal session has not confirmed GPU release")

    started = datetime.datetime.now(runner.TZ)
    runner.DEADLINE = int(time.time() + hours * 3600) if hours is not None else 0
    daytime_checkpoint = day.get("persistent_checkpoint") or {}
    minimum = daytime_checkpoint["step"] if daytime_checkpoint.get("verified") is True else 1
    expected_manifest = json.loads(
        (base / "formal/evidence/first-step-verified-manifest.json").read_text()
    )
    anchor = require_verified_checkpoint(expected_manifest, max(min_resume_step, minimum))
    latest = anchor["step"]
    if continuous:
        verify_validations(expected_manifest["identity"], latest)
    if latest >= stop_after_step:
        print(f"The verified formal checkpoint already reached step {latest}.")
        verify_no_formal_sessions(accounts)
        return {"persistent_checkpoint": anchor, "gpu_released": True, "launcher_result": "completed"}
    target = min(stop_after_step, plan_stop_step(latest, runner.seconds_left())) if hours else stop_after_step
    if target <= latest:
        raise RuntimeError("The requested duration cannot fit another full step and checkpoint transfer")

    session_tag = started.strftime("%m%d-%H%M%S")
    root = base / f"formal-resume-{session_tag}"
    root.mkdir()
    runner.ROOT = root
    original = (base / "formal/launch.py").read_text()
    retry_error = None
    for attempt in range(3):
        name = "formal" if attempt == 0 else f"formal-retry-{attempt}"
        folder = root / name
        folder.mkdir()
        shutil.copytree(base / "formal/payload", folder / "payload")
        configure_resume_script(folder / "payload/run_remote.sh")
        if continuous:
            configure_continuous_payload(base, folder / "payload")

        active = adopt if attempt == 0 else None
        if active is None:
            verify_no_formal_sessions(accounts)
        revised_target = min(target, plan_stop_step(latest, runner.seconds_left())) if hours else target
        if revised_target <= latest:
            if attempt == 0:
                raise RuntimeError("The remaining window cannot fit another full step")
            break
        target = revised_target
        (folder / "drive-resume-verification.json").write_text(json.dumps(anchor, indent=2) + "\n")
        runner.set_stage("resuming_formal", previous_verified_step=latest, stop_after_step=target,
                         estimated_step_seconds=SECONDS_PER_STEP,
                         reserve_seconds=RESERVE_SECONDS if hours else None)
        runner.make_formal_payload(folder, target, resume_step=latest)
        session = active["session"] if active else f"p3-shuffle-formal-{session_tag}-{attempt + 1}"
        drive_payload = prepare_drive_payload(folder, session) if continuous and active is None else None
        launcher = configure_launcher(original, session, accounts, drive_payload, active)
        (folder / "launch.py").write_text(launcher)
        expected_target = f"{runner.DEADLINE} {target} {latest}\n".encode()
        with tarfile.open(folder / "payload.tgz", "r:gz") as archive:
            packed_target = archive.extractfile("./run-target.txt")
            packed_script = archive.extractfile("./run_remote.sh")
            if packed_target.read() != expected_target or packed_script.read() != (
                    folder / "payload/run_remote.sh").read_bytes():
                raise RuntimeError("Packed stop target or resume script differs from the formal resume plan")
        result = runner.run_stage(name, runner.seconds_left(), lock_fd=lock_fd, milestones=continuous)
        checkpoint_file = folder / "evidence/persistent-checkpoint.json"
        if checkpoint_file.is_file():
            saved = json.loads(checkpoint_file.read_text())
            step = saved.get("step")
            if saved.get("verified") is True and type(step) is int and latest <= step <= target:
                latest = step
        if not runner.is_interrupted(result) or latest >= target:
            break
        try:
            anchor = require_verified_checkpoint(expected_manifest, latest)
            latest = anchor["step"]
            if continuous:
                verify_validations(expected_manifest["identity"], latest)
            runner.set_stage("verified_resume_anchor", checkpoint=anchor, next_attempt=attempt + 2)
        except RuntimeError as exc:
            retry_error = str(exc)
            break
        if latest >= target or (hours and plan_stop_step(latest, runner.seconds_left()) <= latest):
            break

    released = result.get("released") is True
    minimum_final = max(latest, target) if result["stage"] == "completed" else latest
    confirmation = None
    verification_error = None
    try:
        confirmation = require_verified_checkpoint(expected_manifest, minimum_final)
        if continuous:
            verify_validations(expected_manifest["identity"], confirmation["step"])
    except RuntimeError as exc:
        verification_error = str(exc)
        confirmation = None
    completed = (result["stage"] == "completed" and released
                 and confirmation is not None and confirmation["step"] >= target)
    runner.set_stage(
        "completed" if completed else "stopped_formal",
        persistent_checkpoint=confirmation,
        last_known_step=max(latest, confirmation["step"]) if confirmation else latest,
        checkpoint_unconfirmed=confirmation is None, gpu_released=released,
        launcher_result=result["stage"], launcher_error=result.get("error"),
        launcher_exit_code=result.get("result"), stop_after_step=target,
        retry_error=retry_error, verification_error=verification_error,
    )
    return runner.status(root)


def train_until_complete(base, hours, lock_fd, target, minimum, accounts, adopt=None):
    stalled = 0
    while True:
        outcome = resume(base, hours, lock_fd, target, minimum, accounts, continuous=True, adopt=adopt)
        adopt = None
        if not outcome.get("gpu_released"):
            raise RuntimeError("The previous formal GPU session still needs verified closure")
        checkpoint = outcome.get("persistent_checkpoint")
        if checkpoint is None:
            raise RuntimeError("Could not recheck the latest checkpoint and validation results")
        latest = checkpoint["step"]
        if latest >= target:
            print(f"FORMAL_TRAINING_COMPLETE step={latest} account={accounts[0].upper()}", flush=True)
            return
        exit_code = outcome.get("launcher_exit_code")
        if exit_code not in (None, 0, 31, 124, 137, 143):
            raise RuntimeError(f"Training exited with code {exit_code}: {outcome.get('launcher_error')}")
        stalled = stalled + 1 if latest == minimum else 0
        if stalled >= 3:
            raise RuntimeError(f"Three consecutive runtime windows made no progress past step {latest}")
        minimum = latest
        print(f"FORMAL_NEXT_RUNTIME account={accounts[0].upper()} resume_step={minimum} target={target}", flush=True)
        if stalled:
            time.sleep(60)



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=float)
    parser.add_argument("--stop-after-step", type=int, default=MAX_STEPS)
    parser.add_argument("--min-resume-step", type=int, default=1)
    parser.add_argument("--account", choices=("a", "b", "c"))
    parser.add_argument("--until-complete", action="store_true")
    parser.add_argument("--adopt-runtime", type=Path)
    args = parser.parse_args()
    if args.hours is not None and (not math.isfinite(args.hours) or args.hours <= 0):
        parser.error("--hours must be positive")
    if not 1 <= args.stop_after_step <= MAX_STEPS:
        parser.error(f"--stop-after-step must be between 1 and {MAX_STEPS}")
    if not 1 <= args.min_resume_step <= args.stop_after_step:
        parser.error("--min-resume-step must be positive and at most --stop-after-step")
    if args.until_complete and args.account is None:
        parser.error("--until-complete requires one explicit account")
    adopt = None
    if args.adopt_runtime is not None:
        if not args.until_complete or args.hours is not None:
            parser.error("--adopt-runtime requires --until-complete and no --hours")
        adopt = json.loads(args.adopt_runtime.read_text())
        if (adopt.get("stage") != "running" or adopt.get("account") != args.account
                or not adopt.get("endpoint") or not adopt.get("remote_pid")
                or SESSION_PREFIX.fullmatch(f"[{adopt.get('session')}]") is None):
            parser.error("--adopt-runtime does not identify a running formal job on this account")

    base = Path(__file__).resolve().parent
    with (base / ".formal-resume.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX if adopt else fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Another local formal resume controller holds the lock") from exc
        accounts = (args.account,) if args.account else ("c", "a")
        if args.until_complete:
            train_until_complete(base, args.hours, lock.fileno(), args.stop_after_step,
                                 args.min_resume_step, accounts, adopt)
        else:
            resume(base, args.hours or 8.0, lock.fileno(), args.stop_after_step, args.min_resume_step, accounts)


if __name__ == "__main__":
    main()
