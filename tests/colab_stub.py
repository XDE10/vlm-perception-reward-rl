"""A stand-in for the `colab` CLI used by tests/test_colab_launcher.py.

Simulates one VM per session under $STUB_ROOT: `upload`/`download` map the
remote prefix /content/p3 onto $STUB_ROOT/vm/p3, and `exec` runs the code with
P3_REMOTE_ROOT pointing there. Fault injection:

* STUB_DROP_JOB=1: the job exec starts the job in the background and returns
  immediately (a dropped live connection), so the launcher must poll status.json.
* STUB_FAIL_UPLOADS=N: the first N uploads fail like the real CLI does (exit 1,
  "[colab] Upload failed: ..." on stdout, with a request URL carrying a token).
* STUB_CORRUPT_UPLOAD=<substring>: the first upload whose remote name contains
  the substring is stored truncated but reported as successful.
* STUB_HANG_UPLOADS=N: the first N uploads stall for 60 s (a request that never
  returns), so the launcher's per-call time limit has to end them.
* STUB_VANISH_AFTER_JOB=1 (with STUB_DROP_JOB=1): when the background job ends,
  the VM disappears (its files and the session), as when Colab reclaims it.
* STUB_FAIL_ALLOCATE=N: the first N `new` calls fail like an A100 queue (503); every
  `new` call records the COLAB_CLI_ASSIGN_RETRIES value it saw in calls.log.
* STUB_LOSE_JOB_EXEC=N: the first N job execs end with "RuntimeError: Connection was
  lost." before the job starts (seen after a 0-second bootstrap in the third preflight).
* STUB_USAGE: the text `colab usage` prints (default "stub usage").

Like the real CLI, exec/upload/download fail for a session that does not exist.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

STUB = Path(os.environ["STUB_ROOT"])
REMOTE_PREFIX = "/content/p3"
# Run the job, then reclaim the VM. Optionally give its session name to a different VM.
VANISH = """import os, shutil, subprocess, sys
from pathlib import Path
subprocess.call(sys.argv[1:3])
for path in sys.argv[3:]:
    shutil.rmtree(path, ignore_errors=True)
if os.environ.get("STUB_REPLACE_VM") == "1":
    session = Path(sys.argv[4])
    session.mkdir()
    (session / "replacement").touch()
"""


def remote_path(path):
    if not path.startswith(REMOTE_PREFIX):
        sys.exit("stub: remote path outside %s: %s" % (REMOTE_PREFIX, path))
    return STUB / "vm" / "p3" / path[len(REMOTE_PREFIX):].lstrip("/")


def option(args, name):
    return args[args.index(name) + 1] if name in args else None


def take(counter, limit):
    """True (and count it) while fewer than ``limit`` events were recorded in the counter file."""
    used = int(counter.read_text()) if counter.is_file() else 0
    if used >= limit:
        return False
    counter.write_text(str(used + 1))
    return True


def main():
    args = sys.argv[1:]
    while args and args[0].startswith("--") and args[0] not in ("--help",):  # global flags such as --auth=adc
        args = args[1:]
    command, rest = args[0], args[1:]
    with open(str(STUB / "calls.log"), "a") as handle:
        handle.write(" ".join([command] + rest) + "\n")
    session = option(rest, "-s")
    if command in ("exec", "upload", "download") and not (STUB / "sessions" / str(session)).is_dir():
        print("[colab] Session '%s' not found." % session)
        sys.exit(1)
    if command == "version":
        print("Version: stub")
    elif command == "usage":
        print(os.environ.get("STUB_USAGE", "stub usage").replace("\\n", "\n"))
    elif command == "sessions":
        active = sorted((STUB / "sessions").glob("*"))
        for vm in active:
            suffix = "-replacement" if (vm / "replacement").exists() else ""
            print(f"[{vm.name}] stub-{vm.name}{suffix} | Hardware: A100 | Shape: Standard | Variant: GPU")
        if not active:
            print("[colab] No active sessions.")
    elif command == "new":
        with open(str(STUB / "calls.log"), "a") as handle:
            handle.write("new-env ASSIGN_RETRIES=%s\n" % os.environ.get("COLAB_CLI_ASSIGN_RETRIES", "unset"))
        if take(STUB / "allocations_failed", int(os.environ.get("STUB_FAIL_ALLOCATE", "0"))):
            print("[colab] Creating session '%s'..." % option(rest, "-s"))
            print("requests.exceptions.HTTPError: 503 Server Error: Service Unavailable for url: "
                  "https://stub.colab.dev/tun/m/assign?authuser=0")
            sys.exit(1)
        (STUB / "sessions" / option(rest, "-s")).mkdir(parents=True, exist_ok=True)
        print("stub: allocated")
    elif command == "stop":
        shutil.rmtree(str(STUB / "sessions" / option(rest, "-s")), ignore_errors=True)
    elif command == "upload":
        positional = [a for a in rest if a not in ("-s", option(rest, "-s"))]
        target = remote_path(positional[1])
        if not target.parent.is_dir():
            sys.exit("stub: remote directory missing: %s" % target.parent)
        if take(STUB / "uploads_hung", int(os.environ.get("STUB_HANG_UPLOADS", "0"))):
            time.sleep(60)  # a stalled request: the launcher's wall-clock limit must kill this call
        if take(STUB / "uploads_failed", int(os.environ.get("STUB_FAIL_UPLOADS", "0"))):
            print("[colab] Upload failed: 504 Server Error: Gateway Timeout for url: https://stub.colab.dev/api/contents%s"
                  "?authuser=0&colab-runtime-proxy-token=SECRET-PROXY-TOKEN-123" % positional[1])
            sys.exit(1)
        corrupt = os.environ.get("STUB_CORRUPT_UPLOAD")
        if corrupt and corrupt in positional[1] and take(STUB / "uploads_corrupted", 1):
            target.write_bytes(Path(positional[0]).read_bytes()[:-7])
        else:
            shutil.copyfile(positional[0], str(target))
        print("[colab] Uploaded '%s' to '%s'" % (positional[0], positional[1]))
    elif command == "download":
        positional = [a for a in rest if a not in ("-s", option(rest, "-s"))]
        if positional[0].endswith("/status.json") and take(STUB / "status_failed", int(os.environ.get("STUB_FAIL_STATUS", "0"))):
            print("[colab] Download failed: 503 https://stub.colab.dev/?colab-runtime-proxy-token=SECRET-STATUS-TOKEN")
            sys.exit(1)
        source = remote_path(positional[0])
        if not source.is_file():
            sys.exit("stub: no such remote file %s" % positional[0])
        shutil.copyfile(str(source), positional[1])
    elif command == "exec":
        source = option(rest, "-f")
        code = Path(source).read_text() if source else sys.stdin.read()
        env = dict(os.environ, P3_REMOTE_ROOT=str(STUB / "vm" / "p3"))
        (STUB / "vm").mkdir(parents=True, exist_ok=True)
        script = Path(tempfile.mkstemp(suffix=".py", dir=str(STUB))[1])
        script.write_text(code)
        if source and source.endswith("kernel_job.py") and take(STUB / "job_execs_lost",
                                                                int(os.environ.get("STUB_LOSE_JOB_EXEC", "0"))):
            print("RuntimeError: Connection was lost.")
            sys.exit(1)
        if source and source.endswith("kernel_job.py") and os.environ.get("STUB_DROP_JOB") == "1":
            runner = [sys.executable, str(script)]
            if os.environ.get("STUB_VANISH_AFTER_JOB") == "1":
                runner = [sys.executable, "-c", VANISH, sys.executable, str(script), str(STUB / "vm"),
                          str(STUB / "sessions" / session)]
            with open(str(STUB / "background_job.log"), "ab") as log:
                subprocess.Popen(runner, env=env, cwd=str(STUB / "vm"), stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            print("stub: connection lost")
            sys.exit(1)
        sys.exit(subprocess.call([sys.executable, str(script)], env=env, cwd=str(STUB / "vm")))
    else:
        sys.exit("stub: unsupported command %s" % command)


if __name__ == "__main__":
    main()
