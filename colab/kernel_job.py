# Executed inside the Colab kernel by colab/launch.sh via `colab exec -f` (standard library only).
# Runs the requested task's steps from the extracted repo (scripts.colab.runner); keeps the kernel busy
# with heartbeat lines until the job finishes, then prints JOB_DONE.
#
# A run starts at most once per VM: out/<run_id>.lock is created atomically before the job starts. The launcher
# may send this file again when its exec failed before the job began (S3, "Connection was lost."); a repeated
# exec then either starts the job (no lock yet), reports that it already finished (JOB_DONE), or reports that it
# was started and never finished (a crashed or restarted kernel), without starting it twice.
import json
import os
import sys
import time
from pathlib import Path


def _claim(root, run_id):
    """True if this call may start the job; False if an earlier call already did."""
    lock = root / "out" / (run_id + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as handle:
        handle.write(json.dumps({"run_id": run_id, "pid": os.getpid(),
                                 "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))
    return True


def _p3_kernel_job():
    root = Path(os.environ.get("P3_REMOTE_ROOT", "/content/p3"))
    request = json.loads((root / "inbox" / "request.json").read_text(encoding="utf-8"))
    run_id = request["run_id"]
    if not _claim(root, run_id):
        done = root / "out" / (run_id + ".done.json")
        if done.is_file():
            overall = json.loads(done.read_text(encoding="utf-8")).get("overall")
            print("[p3] job %s already finished on this VM; JOB_DONE overall=%s" % (run_id, overall), flush=True)
        else:
            print("[p3] JOB_ALREADY_STARTED %s: started earlier on this VM and not finished; not starting it again "
                  "(see out/%s/status.json)" % (run_id, run_id), flush=True)
        return
    repo = root / "repo"
    for name in list(sys.modules):
        if name == "scripts" or name.startswith(("scripts.", "src.")) or name == "src":
            del sys.modules[name]
    if str(repo) in sys.path:
        sys.path.remove(str(repo))
    sys.path.insert(0, str(repo))
    from scripts.colab.runner import run_job

    run_job(root, request)


_p3_kernel_job()
