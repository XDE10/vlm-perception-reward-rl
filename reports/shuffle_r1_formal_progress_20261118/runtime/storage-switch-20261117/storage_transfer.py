"""Copy only this run's inputs and verified resume state between Drive accounts."""

from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


BASE = Path("/mnt/d/project3-shuffle-r1/recovery-20261116")
STATE = Path(__file__).resolve().parent
CONFIG = STATE / "rclone-project3.conf"
RELATIVE = "ColabProjects/vlm-perception-reward-rl/shuffle-r1-overnight-20261116"
LOGICAL = f"mydrive:{RELATIVE}"
TZ = timezone(timedelta(hours=8))


def log(message):
    print(datetime.now(TZ).isoformat(timespec="seconds"), message, flush=True)


def command(*args, timeout=90, capture=True):
    return subprocess.run(
        ["rclone", "--config", str(CONFIG), *args, "--tpslimit", "2", "--checkers", "2",
         "--transfers", "2", "--retries", "2", "--low-level-retries", "3",
         "--drive-stop-on-upload-limit", "--drive-chunk-size", "64M",
         "--stats-log-level", "NOTICE"],
        check=True, timeout=timeout, stdout=subprocess.PIPE if capture else None,
    ).stdout


def read(remote):
    return command("cat", remote)


def verify(remote, step, identity, marker=True):
    manifest_bytes = read(f"{remote}/manifest.json")
    manifest = json.loads(manifest_bytes)
    if (manifest["identity"] != identity or manifest["global_step"] != step
            or manifest["optimizer_steps"] != step * 4 or manifest["scheduler_steps"] != step):
        raise RuntimeError(f"Manifest identity or counters differ at step {step}")
    expected = {name: entry["bytes"] for name, entry in manifest["files"].items()}
    expected["manifest.json"] = len(manifest_bytes)
    if marker:
        marker_bytes = read(f"{remote}/PERSISTED.json")
        record = json.loads(marker_bytes)
        if (record.get("step") != step or record.get("verified") is not True
                or record.get("remote") != f"{LOGICAL}/formal-checkpoints/global_step_{step}"):
            raise RuntimeError(f"Invalid source marker for step {step}")
        expected["PERSISTED.json"] = len(marker_bytes)
    files = json.loads(command("lsjson", "--recursive", "--files-only", remote))
    if len(files) != len(expected) or {item["Path"]: item["Size"] for item in files} != expected:
        raise RuntimeError(f"Checkpoint directory differs from manifest at step {step}")
    return manifest, manifest_bytes


def latest(source, identity, minimum, count=2):
    root = f"{source}:{RELATIVE}"
    listed = command("lsf", "--dirs-only", f"{root}/formal-checkpoints").decode()
    steps = sorted({int(n) for n in re.findall(r"^global_step_([1-9]\d*)/$", listed, re.M)}, reverse=True)
    selected = []
    for step in steps:
        if step < minimum and not selected:
            break
        folder = f"{root}/formal-checkpoints/global_step_{step}"
        files = command("lsf", "--files-only", folder).decode().splitlines()
        if "PERSISTED.json" not in files:
            continue
        verify(folder, step, identity)
        selected.append(step)
        if len(selected) == count:
            return selected
    if selected and selected[0] >= minimum:
        return selected
    raise RuntimeError(f"No verified source checkpoint could be found after step {minimum}")


def transfer(source, destination, minimum, count=2):
    reference = json.loads((BASE / "formal/evidence/first-step-verified-manifest.json").read_text())
    identity = reference["identity"]
    source_root = f"{source}:{RELATIVE}"
    dest_root = f"{destination}:{RELATIVE}"
    steps = latest(source, identity, minimum, count)
    log(f"Selected source checkpoints {steps} for {source} -> {destination}")
    # Publish older first so a destination never advances to a partially copied checkpoint.
    for step in reversed(steps):
        start = f"{source_root}/formal-checkpoints/global_step_{step}"
        end = f"{dest_root}/formal-checkpoints/global_step_{step}"
        manifest, original = verify(start, step, identity)
        log(f"Copying checkpoint {step}, {sum(v['bytes'] for v in manifest['files'].values())} bytes")
        command("copy", start, end, "--exclude", "/PERSISTED.json", "--disable", "copy",
                "--stats", "60s", "--stats-one-line", capture=False, timeout=14400)
        command("check", start, end, "--exclude", "/PERSISTED.json", "--one-way",
                capture=False, timeout=600)
        _, copied = verify(end, step, identity, marker=False)
        if copied != original:
            raise RuntimeError(f"Manifest contents differ after transferring step {step}")
        if step % 25 == 0:
            transfer_validation(source_root, dest_root, step, identity)
        command("copyto", f"{start}/PERSISTED.json", f"{end}/PERSISTED.json", "--disable", "copy")
        verify(end, step, identity)
        log(f"Destination checkpoint {step} marker and manifest verified")
    for step in range(25, steps[0] + 1, 25):
        transfer_validation(source_root, dest_root, step, identity)
    folders = command("lsf", "--dirs-only", source_root).decode().splitlines()
    if source == "p3temporary" and "formal-model-archives/" in folders:
        log("Copying and checking retained validation model archives")
        command("copy", f"{source_root}/formal-model-archives", f"{dest_root}/formal-model-archives",
                "--disable", "copy", capture=False, timeout=14400)
        command("check", f"{source_root}/formal-model-archives", f"{dest_root}/formal-model-archives",
                "--one-way", capture=False, timeout=1200)
    if "formal-environment/" in folders:
        log("Copying and checking environment reconstruction records")
        command("copy", f"{source_root}/formal-environment", f"{dest_root}/formal-environment",
                "--disable", "copy", capture=False, timeout=1800)
        command("check", f"{source_root}/formal-environment", f"{dest_root}/formal-environment",
                "--one-way", capture=False, timeout=300)
    log("Copying and checking frozen training inputs")
    command("copy", f"{source_root}/inputs", f"{dest_root}/inputs", "--disable", "copy",
            capture=False, timeout=1800)
    command("check", f"{source_root}/inputs", f"{dest_root}/inputs", "--one-way",
            capture=False, timeout=300)
    result = {
        "source": source, "destination": destination, "steps": steps,
        "identity": identity, "verified_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "manifest_sha256": hashlib.sha256(
            read(f"{dest_root}/formal-checkpoints/global_step_{steps[0]}/manifest.json")
        ).hexdigest(),
    }
    path = STATE / f"transfer-{source}-to-{destination}.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    log(f"TRANSFER_VERIFIED {path}")
    return result


def transfer_validation(source, destination, step, identity):
    relative = f"formal-validation/global_step_{step}.json"
    record = read(f"{source}/{relative}")
    sys.path.insert(0, str(BASE))
    from formal_validation import validate_record
    validate_record(json.loads(record), step, identity)
    command("copyto", f"{source}/{relative}", f"{destination}/{relative}", "--disable", "copy")
    if read(f"{destination}/{relative}") != record:
        raise RuntimeError(f"Fixed-dev result readback differs at step {step}")


if __name__ == "__main__":
    transfer(sys.argv[1], sys.argv[2], int(sys.argv[3]),
             int(sys.argv[4]) if len(sys.argv) > 4 else 2)
