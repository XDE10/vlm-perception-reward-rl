"""Run the overnight experiment in order, with a fixed deadline and explicit gates."""
import datetime
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
TZ = datetime.timezone(datetime.timedelta(hours=8))
DEADLINE = int(datetime.datetime(2026, 11, 16, 15, 30, tzinfo=TZ).timestamp())
SHORT = Path.home() / ".local/state/vlm-perception-reward-rl/shuffle-r1-b16-g4-20261115/attempt-9"
DRIVE = "mydrive:ColabProjects/vlm-perception-reward-rl/shuffle-r1-overnight-20261116"
STORAGE_ROUTE = ROOT / "storage-route.json"
if STORAGE_ROUTE.is_file():
    storage = json.loads(STORAGE_ROUTE.read_text())
    os.environ["RCLONE_CONFIG"] = storage["rclone_config"]
    os.environ.setdefault("RCLONE_TPSLIMIT", "2")
    os.environ.setdefault("RCLONE_CHECKERS", "2")
    os.environ.setdefault("RCLONE_TRANSFERS", "2")
    os.environ.setdefault("RCLONE_DRIVE_STOP_ON_UPLOAD_LIMIT", "true")


def seconds_left():
    return DEADLINE - int(time.time()) if DEADLINE else 0


def set_stage(stage, **details):
    now = datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    data = {"time": now, "stage": stage,
            "seconds_left": max(0, seconds_left()) if DEADLINE else None, **details}
    pending = ROOT / "status.tmp"
    pending.write_text(json.dumps(data, indent=2) + "\n")
    pending.replace(ROOT / "status.json")
    print(now, stage, json.dumps(details), flush=True)


def status(path):
    return json.loads((path / "status.json").read_text())


def verify_short():
    set_stage("waiting_b16", log=str(SHORT / "runner.log"), session="p3-shuffle-b16-1116-r9")
    stop_waiting = min(DEADLINE, time.time() + 2700)
    while time.time() < stop_waiting:
        if (SHORT / "status.json").is_file():
            result = status(SHORT)
            if result["stage"] in {"completed", "failed"}:
                check = SHORT / "evidence/comparison.json"
                return (result["stage"] == "completed" and result.get("released") is True
                        and check.is_file() and json.loads(check.read_text()).get("checks_passed") is True)
        time.sleep(15)
    return False


def run_stage(directory, budget=None, *, lock_fd=None, milestones=False):
    folder = ROOT / directory
    environment = os.environ.copy()
    if budget is not None:
        environment["P3_FORMAL_BUDGET_SECONDS"] = str(budget)
    set_stage(directory, log=str(folder / "runner.log"),
              planned_budget_seconds=(budget or None) if budget is not None else 5400)
    command = ["python3", "-u", str(folder / "launch.py")]
    options = dict(cwd=folder, env=environment, stdin=subprocess.DEVNULL,
                   stderr=subprocess.STDOUT, pass_fds=() if lock_fd is None else (lock_fd,))
    with (folder / "runner.log").open("xb", buffering=0) as log:
        if milestones:
            with subprocess.Popen(command, stdout=subprocess.PIPE, **options) as process:
                for line in process.stdout:
                    log.write(line)
                    match = re.search(
                        rb"(?:FORMAL_(?:STAGE|VALIDATION_PERSISTED|CHECKPOINT_PERSISTED)[ ^=]*[ =]"
                        rb"|Load from checkpoint: |\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] )"
                        rb"[^\r\n]{1,260}", line,
                    )
                    if match:
                        print(match.group().decode(errors="replace"), flush=True)
            if process.returncode:
                raise subprocess.CalledProcessError(process.returncode, command)
        else:
            subprocess.run(command, stdout=log, check=True, **options)
    return status(folder)


def make_formal_payload(folder, target, resume_step=0):
    payload = folder / "payload"
    publisher = payload / "persist_checkpoint.sh"
    source = publisher.read_text()
    unfiltered = " | sort -V | tail -n 1)"
    numeric_only = " | awk -F / '$NF ~ /^global_step_[1-9][0-9]*$/'" + unfiltered
    if numeric_only not in source:
        if source.count(unfiltered) != 1:
            raise RuntimeError("The checkpoint publisher does not match its expected directory selection")
        publisher.write_text(source.replace(unfiltered, numeric_only, 1))
    subprocess.run(["bash", "-n", str(publisher)], check=True)
    (payload / "run-target.txt").write_text(f"{DEADLINE} {target} {resume_step}\n")
    sums = payload / "SHA256SUMS"
    entries = []
    for path in sorted(payload.rglob("*")):
        if path.is_file() and path != sums:
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            entries.append(f"{digest}  {path.relative_to(payload)}\n")
    sums.write_text("".join(entries))
    subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=payload, check=True)
    subprocess.run(["tar", "-C", str(payload), "-czf", str(folder / "payload.tgz"), "."], check=True)


def is_interrupted(result):
    return (result["stage"] == "failed" and result.get("released") is True
            and result.get("result") is None)


def read_drive(*args):
    return subprocess.run(
        ["rclone", *args], capture_output=True, timeout=25, check=True,
    ).stdout


def verify_drive_manifest(directory, step, marker_bytes, expected_manifest):
    manifest_bytes = read_drive("cat", f"{directory}/manifest.json")
    manifest = json.loads(manifest_bytes)
    if (not isinstance(manifest, dict)
            or manifest.get("schema") != 1
            or manifest.get("identity") != expected_manifest["identity"]
            or manifest.get("global_step") != step
            or manifest.get("optimizer_steps") != 4 * step
            or manifest.get("scheduler_steps") != step):
        raise RuntimeError(f"Drive manifest does not match formal identity and counters for step {step}")
    if step == expected_manifest["global_step"] and manifest != expected_manifest:
        raise RuntimeError(f"Drive manifest differs from the previously verified step {step} manifest")

    files = manifest.get("files")
    required = {
        "dataloader.pt", "driver_rng.pt", "actor/model_world_size_1_rank_0.pt",
        "actor/optim_world_size_1_rank_0.pt", "actor/extra_state_world_size_1_rank_0.pt",
        "actor/rollout_rng_rank_0.pt",
    }
    if not isinstance(files, dict) or not required.issubset(files):
        raise RuntimeError(f"Drive manifest lacks required checkpoint state for step {step}")
    expected_sizes = {"PERSISTED.json": len(marker_bytes), "manifest.json": len(manifest_bytes)}
    for name, metadata in files.items():
        if (name in expected_sizes or any(part in {"", ".", ".."} for part in name.split("/"))
                or not isinstance(metadata, dict)
                or type(metadata.get("bytes")) is not int or metadata["bytes"] < 0
                or not re.fullmatch(r"[0-9a-f]{64}", str(metadata.get("sha256")))):
            raise RuntimeError(f"Invalid checkpoint file entry for formal step {step}: {name}")
        expected_sizes[name] = metadata["bytes"]

    listing = json.loads(read_drive("lsjson", "--recursive", "--files-only", directory))
    if not isinstance(listing, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("Path"), str)
        or type(item.get("Size")) is not int for item in listing
    ):
        raise RuntimeError(f"Invalid Drive directory listing for formal step {step}")
    actual_sizes = {item["Path"]: item["Size"] for item in listing}
    if len(listing) != len(actual_sizes) or actual_sizes != expected_sizes:
        raise RuntimeError(f"Drive checkpoint paths or file sizes differ from manifest for step {step}")
    return {
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "checkpoint_files": len(files),
        "checkpoint_bytes": sum(metadata["bytes"] for metadata in files.values()),
        "optimizer_steps": manifest["optimizer_steps"],
        "scheduler_steps": manifest["scheduler_steps"],
    }


def read_private_checkpoint(expected_manifest=None, minimum=1):
    base = DRIVE + "/formal-checkpoints"
    listed = read_drive("lsf", "--dirs-only", base).decode()
    steps = sorted((int(step) for step in re.findall(r"^global_step_([1-9]\d*)/$", listed, re.M)), reverse=True)
    for step in steps:
        if step < minimum:
            break
        directory = f"{base}/global_step_{step}"
        files = read_drive("lsf", "--files-only", directory).decode()
        if "PERSISTED.json" not in files.splitlines():
            continue
        marker_bytes = read_drive("cat", f"{directory}/PERSISTED.json")
        marker = json.loads(marker_bytes)
        if (not isinstance(marker, dict) or marker.get("verified") is not True
                or marker.get("step") != step or marker.get("remote") != directory):
            raise RuntimeError(f"Invalid persistence marker for formal step {step}")
        confirmation = {"step": step, "remote": directory, "verified": True}
        if expected_manifest is not None:
            confirmation.update(verify_drive_manifest(directory, step, marker_bytes, expected_manifest))
            confirmation["checked_at"] = datetime.datetime.now(TZ).isoformat(timespec="seconds")
        return confirmation
    return None


def latest_private_checkpoint():
    checkpoint = read_private_checkpoint()
    return checkpoint["step"] if checkpoint else 0


def run_capacity():
    capacity = run_stage("b512")
    directory = ROOT / "b512"
    if is_interrupted(capacity) and capacity["remaining_seconds"] >= 600 and seconds_left() >= 7200:
        remaining = capacity["remaining_seconds"]
        retry = ROOT / "b512-retry"
        retry.mkdir()
        shutil.copyfile(directory / "payload.tgz", retry / "payload.tgz")
        launcher = (directory / "launch.py").read_text()
        launcher = launcher.replace("p3-shuffle-b512-1116", "p3-shuffle-b512-1116-r2")
        launcher = launcher.replace("BUDGET = 5400", f"BUDGET = {remaining}")
        (retry / "launch.py").write_text(launcher)
        capacity = run_stage(retry.name, remaining)
        directory = retry
    return capacity, directory


def run_formal(target, elapsed):
    folder = ROOT / "formal"
    make_formal_payload(folder, target)
    result = run_stage(folder.name, seconds_left())
    for retry_index in range(1, 3):
        if not is_interrupted(result) or seconds_left() <= elapsed + 3000:
            break
        saved = latest_private_checkpoint()
        if saved < 1:
            break
        if saved >= target:
            set_stage("completed", persistent_checkpoint={"step": saved, "verified": True},
                      gpu_released=True)
            return
        retry = ROOT / f"formal-resume-{retry_index}"
        retry.mkdir()
        shutil.copytree(ROOT / "formal/payload", retry / "payload")
        launcher = (ROOT / "formal/launch.py").read_text()
        launcher = launcher.replace("p3-shuffle-night-1116", f"p3-shuffle-night-1116-r{retry_index + 1}")
        (retry / "launch.py").write_text(launcher)
        set_stage("recovering_formal", resume_step=saved, planned_stop_step=target)
        make_formal_payload(retry, target, resume_step=saved)
        result = run_stage(retry.name, seconds_left())
        folder = retry
    evidence = folder / "evidence/persistent-checkpoint.json"
    checkpoint = json.loads(evidence.read_text()) if evidence.is_file() else None
    if checkpoint is None and result.get("released") is True:
        saved = latest_private_checkpoint()
        if saved:
            checkpoint = {"step": saved, "verified": True,
                          "remote": f"{DRIVE}/formal-checkpoints/global_step_{saved}"}
    set_stage("completed" if result["stage"] == "completed" else "stopped_formal",
              persistent_checkpoint=checkpoint, gpu_released=result.get("released"))


def main():
    if not verify_short():
        set_stage("stopped_b16_acceptance_failed", log=str(SHORT / "runner.log"))
        return
    if seconds_left() < 5400:
        set_stage("stopped_overnight_budget")
        return
    capacity, directory = run_capacity()
    verified = directory / "evidence/verification.json"
    if (capacity["stage"] != "completed" or capacity.get("released") is not True
            or not verified.is_file() or not json.loads(verified.read_text()).get("checkpoint_hashes_verified")):
        set_stage("stopped_capacity_acceptance_failed", log=str(directory / "runner.log"))
        return
    elapsed = max(1, capacity["budget_seconds"] - capacity["remaining_seconds"])
    local_train = (Path.home() / ".local/state/vlm-perception-reward-rl"
                   / "mmrl30k-b362381-visible-family-v2-20261115/train.parquet")
    set_stage("waiting_for_formal_dataset", measured_capacity_seconds=elapsed)
    while seconds_left() > elapsed + 3000:
        try:
            train = subprocess.run(
                ["rclone", "lsjson", "--stat", DRIVE + "/inputs/train.parquet"],
                capture_output=True, text=True, timeout=25, check=False,
            )
            train_stat = json.loads(train.stdout) if train.returncode == 0 else None
            if train_stat and train_stat.get("Size") == local_train.stat().st_size:
                break
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
        time.sleep(45)
    else:
        set_stage("stopped_frozen_train_dataset_unavailable")
        return
    budget = seconds_left()
    target = min(25, (budget - 2850) // elapsed)
    if target < 1:
        set_stage("stopped_training_window_too_short", measured_capacity_seconds=elapsed)
        return
    set_stage("preparing_formal", planned_stop_step=target, measured_capacity_seconds=elapsed)
    run_formal(target, elapsed)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        set_stage("failed", error=f"{type(exc).__name__}: {exc}")
        raise
