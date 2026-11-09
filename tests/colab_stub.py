"""A stand-in for the `colab` CLI used by tests/test_colab_launcher.py.

Simulates one VM per session under $STUB_ROOT: `upload`/`download` map the
remote prefix /content/p3 onto $STUB_ROOT/vm/p3, and `exec` runs the code with
P3_REMOTE_ROOT pointing there. Set STUB_DROP_JOB=1 to make the job exec start
the job in the background and return immediately (a dropped live connection),
so the launcher must poll status.json.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STUB = Path(os.environ["STUB_ROOT"])
REMOTE_PREFIX = "/content/p3"


def remote_path(path):
    if not path.startswith(REMOTE_PREFIX):
        sys.exit("stub: remote path outside %s: %s" % (REMOTE_PREFIX, path))
    return STUB / "vm" / "p3" / path[len(REMOTE_PREFIX):].lstrip("/")


def option(args, name):
    return args[args.index(name) + 1] if name in args else None


def main():
    args = sys.argv[1:]
    while args and args[0].startswith("--") and args[0] not in ("--help",):  # global flags such as --auth=adc
        args = args[1:]
    command, rest = args[0], args[1:]
    with open(str(STUB / "calls.log"), "a") as handle:
        handle.write(" ".join([command] + rest) + "\n")
    if command == "version":
        print("Version: stub")
    elif command in ("sessions", "usage"):
        print("stub " + command)
    elif command == "new":
        (STUB / "sessions" / option(rest, "-s")).mkdir(parents=True, exist_ok=True)
        print("stub: allocated")
    elif command == "stop":
        shutil.rmtree(str(STUB / "sessions" / option(rest, "-s")), ignore_errors=True)
    elif command == "upload":
        positional = [a for a in rest if a not in ("-s", option(rest, "-s"))]
        target = remote_path(positional[1])
        if not target.parent.is_dir():
            sys.exit("stub: remote directory missing: %s" % target.parent)
        shutil.copyfile(positional[0], str(target))
    elif command == "download":
        positional = [a for a in rest if a not in ("-s", option(rest, "-s"))]
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
        if source and source.endswith("kernel_job.py") and os.environ.get("STUB_DROP_JOB") == "1":
            with open(str(STUB / "background_job.log"), "ab") as log:
                subprocess.Popen([sys.executable, str(script)], env=env, cwd=str(STUB / "vm"), stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
            print("stub: connection lost")
            sys.exit(1)
        sys.exit(subprocess.call([sys.executable, str(script)], env=env, cwd=str(STUB / "vm")))
    else:
        sys.exit("stub: unsupported command %s" % command)


if __name__ == "__main__":
    main()
