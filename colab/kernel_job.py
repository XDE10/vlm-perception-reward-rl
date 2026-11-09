# Executed inside the Colab kernel by colab/launch.sh via `colab exec -f` (standard library only).
# Runs the requested task's steps from the extracted repo (scripts.colab.runner); keeps the kernel busy
# with heartbeat lines until the job finishes, then prints JOB_DONE.
import json
import os
import sys
from pathlib import Path


def _p3_kernel_job():
    root = Path(os.environ.get("P3_REMOTE_ROOT", "/content/p3"))
    request = json.loads((root / "inbox" / "request.json").read_text(encoding="utf-8"))
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
