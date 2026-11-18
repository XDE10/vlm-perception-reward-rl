"""Switch only the project-three Drive alias after verified storage migration."""

import base64
import configparser
import fcntl
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from storage_transfer import BASE, CONFIG, RELATIVE, STATE, TZ, command, log, transfer


ROUTE = BASE / "storage-route.json"
TOTAL_LOG = BASE / "formal-b-to-150-1116-204856.log"


def atomic_json(path, record):
    temporary = path.with_suffix(".pending")
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(path)


def activate(remote):
    config = configparser.ConfigParser(interpolation=None)
    config.read(CONFIG)
    if remote not in ("p3original", "p3temporary") or not config[remote].get("token"):
        raise RuntimeError("The project Drive remote is not authorized")
    config["mydrive"] = dict(config[remote])
    pending = CONFIG.with_suffix(".pending")
    with pending.open("w") as stream:
        config.write(stream)
    pending.chmod(0o600)
    pending.replace(CONFIG)
    route = json.loads(ROUTE.read_text()) if ROUTE.exists() else {"rclone_config": str(CONFIG)}
    route.update(active_remote=remote, switched_at=datetime.now(TZ).isoformat(timespec="seconds"))
    if remote == "p3temporary" and "switchback_due" not in route:
        route["switchback_due"] = (datetime.now(TZ) + timedelta(hours=24)).isoformat(timespec="seconds")
    atomic_json(ROUTE, route)
    return route


def current_runtime():
    names = re.findall(r'"log": "([^"]+/runner\.log)"', TOTAL_LOG.read_text(errors="replace"))
    for name in reversed(names):
        status = Path(name).with_name("status.json")
        if status.exists():
            record = json.loads(status.read_text())
            if record.get("stage") in ("running", "awaiting_drive_verification", "verifying_drive_before_release"):
                return record
            if record.get("released") is True:
                return None
            raise RuntimeError("The controller is currently changing runtime state")
    return None


def run_remote(runtime, code):
    command = [str(Path.home() / ".local/bin/colab-b"), "exec", "-s", runtime["session"]]
    reply = subprocess.run(command, input=code, capture_output=True, text=True, timeout=30)
    if reply.returncode or "P3_STORAGE_OPERATION_OK" not in reply.stdout:
        raise RuntimeError("The remote storage operation was not acknowledged")
    return reply.stdout


def pause_publication(runtime, earliest, require_latest_uploaded=True):
    if runtime is None:
        return
    code = (f"earliest = {float(earliest)!r}\n"
            f"require_latest_uploaded = {bool(require_latest_uploaded)!r}\n") + """from pathlib import Path
import fcntl, json, re
root = Path('/content/shuffle-r1-formal')
with (root/'checkpoints/qwen25vl3b_b512_seed1/.drive-upload.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    paths=[p for p in (root/'checkpoints/qwen25vl3b_b512_seed1').glob('global_step_*')
           if re.fullmatch(r'global_step_[1-9][0-9]*',p.name) and (p/'manifest.json').exists()]
    if not paths:
        raise RuntimeError('Waiting for a complete checkpoint')
    latest=max(paths,key=lambda p:int(p.name.rsplit('_',1)[1]))
    manifest=latest/'manifest.json'
    marker=json.loads((root/'evidence/persistent-checkpoint.json').read_text())
    if (manifest.stat().st_mtime < earliest or marker.get('verified') is not True
            or (require_latest_uploaded and marker.get('step') != int(latest.name.rsplit('_',1)[1]))):
        raise RuntimeError('Waiting for a newly completed and published checkpoint')
    (root/'storage-switch.pause').touch()
print('P3_STORAGE_OPERATION_OK')
"""
    run_remote(runtime, code)


def remote_route(runtime, configuration=None):
    if runtime is None:
        return
    data = None if configuration is None else base64.b64encode(configuration).decode()
    code = f"""encoded = {data!r}
import base64, fcntl, os
from pathlib import Path
root=Path('/content/shuffle-r1-formal')
with (root/'checkpoints/qwen25vl3b_b512_seed1/.drive-upload.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if encoded is not None:
        target=Path('/content/.p3-overnight-rclone.conf')
        pending=target.with_suffix('.switch-pending')
        pending.write_bytes(base64.b64decode(encoded))
        pending.chmod(0o600)
        os.replace(pending,target)
    (root/'storage-switch.pause').unlink(missing_ok=True)
print('P3_STORAGE_OPERATION_OK')
"""
    run_remote(runtime, code)


def remote_transfer(runtime):
    """Copy back inside the existing VM while publication is paused."""
    deployment = {
        name: base64.b64encode(data).decode()
        for name, data in {
            "storage_transfer.py": (STATE / "storage_transfer.py").read_bytes(),
            "base/formal_validation.py": (BASE / "formal_validation.py").read_bytes(),
            "base/formal/evidence/first-step-verified-manifest.json":
                (BASE / "formal/evidence/first-step-verified-manifest.json").read_bytes(),
        }.items()
    }
    code = f"deployment = {deployment!r}\n" + """
import base64, subprocess
from pathlib import Path
root=Path('/content/p3-storage-return')
root.mkdir(exist_ok=True)
pidfile=root/'pid'
running=False
if pidfile.exists():
    proc=Path('/proc')/pidfile.read_text().strip()
    running=proc.exists() and proc.joinpath('stat').read_text().split(') ',1)[1].split()[0]!='Z'
if not running:
    for name,encoded in deployment.items():
        path=root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(base64.b64decode(encoded))
    result=root/'transfer-p3temporary-to-p3original.json'
    result.unlink(missing_ok=True)
    entry=root/'entry.py'
    lines=[
        'from pathlib import Path',
        'import storage_transfer as t',
        "t.BASE=Path('/content/p3-storage-return/base')",
        "t.CONFIG=Path('/content/.p3-overnight-rclone.conf')",
        "t.transfer('p3temporary','p3original',26)",
    ]
    entry.write_text(chr(10).join(lines)+chr(10))
    with (root/'return.log').open('wb') as output:
        process=subprocess.Popen(['python3','-B','-u',str(entry)],cwd=root,
            stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
    pidfile.write_text(str(process.pid))
print('P3_STORAGE_OPERATION_OK')
"""
    run_remote(runtime, code)
    while True:
        time.sleep(30)
        reply = run_remote(runtime, """
from pathlib import Path
root=Path('/content/p3-storage-return')
result=root/'transfer-p3temporary-to-p3original.json'
proc=Path('/proc')/(root/'pid').read_text().strip()
if result.exists():
    print('P3_RETURN_COPY_VERIFIED')
elif not proc.exists() or proc.joinpath('stat').read_text().split(') ',1)[1].split()[0]=='Z':
    print('P3_RETURN_COPY_FAILED')
print('P3_STORAGE_OPERATION_OK')
""")
        if "P3_RETURN_COPY_VERIFIED" in reply:
            return
        if "P3_RETURN_COPY_FAILED" in reply:
            raise RuntimeError("The remote storage return needs a retry")


def watch_switchback(immediate=False):
    route = json.loads(ROUTE.read_text())
    if route.get("active_remote") == "p3original":
        log("Project storage is already on the original account")
        return
    due = datetime.now(TZ) if immediate else datetime.fromisoformat(route["switchback_due"])
    earliest = datetime.fromtimestamp(0,TZ) if immediate else due - timedelta(hours=1)
    if immediate:
        log("Immediate storage return requested after upload throttling")
    else:
        log(f"Observing checkpoints from {earliest.isoformat(timespec='seconds')}, target around {due.isoformat(timespec='seconds')}")
    while datetime.now(TZ) < earliest:
        time.sleep(min(60, max(1, (earliest - datetime.now(TZ)).total_seconds())))
    while True:
        runtime = None
        try:
            probe = STATE / "return-probe.txt"
            probe.write_text("Project three storage return write/read probe\n")
            destination = f"p3original:{RELATIVE}/storage-migration/return-probe.txt"
            command("copyto", str(probe), destination, timeout=45)
            if command("cat", destination) != probe.read_bytes():
                raise RuntimeError("The original Drive write/read probe did not match")
            runtime = current_runtime()
            if runtime is None and datetime.now(TZ) < due:
                time.sleep(60)
                continue
            pause_publication(runtime, earliest.timestamp(), require_latest_uploaded=not immediate)
            # Copy on an independent profile so the live alias keeps its current identity until verified.
            if runtime is None:
                transfer("p3temporary", "p3original", 26)
            else:
                remote_transfer(runtime)
            current = current_runtime()
            if current and (runtime is None or current["endpoint"] != runtime["endpoint"]):
                raise RuntimeError("The runtime changed while storage was copied")
            runtime = current
            activate("p3original")
            remote_route(runtime, CONFIG.read_bytes())
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
            log(f"Storage return pending, keeping the temporary account active: {type(error).__name__}")
            if json.loads(ROUTE.read_text()).get("active_remote") == "p3original":
                activate("p3temporary")
            try:
                remote_route(runtime, CONFIG.read_bytes())
            except (OSError, RuntimeError, subprocess.SubprocessError):
                log("Remote publication routing will be reconciled on the next check")
            time.sleep(60)
        else:
            log("P3_STORAGE_RETURNED_TO_ORIGINAL after checkpoint and validation readback")
            return


if __name__ == "__main__":
    if sys.argv[1] == "activate":
        print(json.dumps(activate(sys.argv[2]), indent=2))
    elif sys.argv[1] in ("switchback", "switchback-now"):
        with (STATE / ".switchback.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            watch_switchback(immediate=sys.argv[1] == "switchback-now")
    else:
        raise SystemExit("Expected activate or switchback")
