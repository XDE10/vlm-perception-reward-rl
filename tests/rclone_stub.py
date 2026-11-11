"""A stand-in for the `rclone` CLI used by the Drive tests.

Maps the remote ``mydrive:`` onto the directory $FAKE_DRIVE_ROOT. Supports the
subset scripts/colab/drive.py uses: version, listremotes, copyto, copy, cat,
check (--one-way, --exclude), deletefile, rmdir, lsjson (-R, --max-depth,
--dirs-only), purge, about (--json), plus ``--config <file>``. Like rclone, a
missing directory or file exits with code 3.
FAKE_DRIVE_CORRUPT=1 makes `copy` drop the last byte of every file so `check`
must fail; FAKE_RCLONE_CONFIG=<file> lists the remote only under that config;
FAKE_DRIVE_FAIL=<command> makes every call of that command fail (exit 1), e.g.
"copy" for a Drive that stops accepting uploads; FAKE_DRIVE_LOG=<file> appends
one line per call.
"""
import fnmatch
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(os.environ["FAKE_DRIVE_ROOT"])
REMOTE = "mydrive:"
VALUE_OPTIONS = ("--exclude", "--transfers", "--checkers", "--retries", "--low-level-retries", "--stats",
                 "--stats-log-level", "--config", "--max-depth")


def local(path):
    if path.startswith(REMOTE):
        return ROOT / path[len(REMOTE):].lstrip("/")
    return Path(path)


def excludes(args):
    return [args[i + 1] for i, a in enumerate(args) if a == "--exclude"]


def option(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def positional(args):
    out, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a in VALUE_OPTIONS:
            skip = True
            continue
        if a.startswith("-"):
            continue
        out.append(a)
    return out


def files_under(root, patterns):
    for path in sorted(Path(root).rglob("*")):
        if path.is_file() and not any(fnmatch.fnmatch(path.name, p) or fnmatch.fnmatch(str(path.relative_to(root)), p)
                                      for p in patterns):
            yield path


def digest(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def missing(what):
    sys.stderr.write("ERROR : %s: directory not found\n" % what)
    sys.exit(3)


def lsjson(args):
    base = local(positional(args)[0])
    if not base.is_dir():
        missing(positional(args)[0])
    recursive = "-R" in args or "--recursive" in args
    depth = int(option(args, "--max-depth", "0" if not recursive else "-1"))
    entries = []
    for path in sorted(base.rglob("*") if recursive else base.iterdir()):
        rel = path.relative_to(base)
        if recursive and depth > 0 and len(rel.parts) > depth:
            continue
        if "--dirs-only" in args and not path.is_dir():
            continue
        entries.append({"Path": rel.as_posix(), "Name": path.name, "Size": -1 if path.is_dir() else path.stat().st_size,
                        "IsDir": path.is_dir(), "ModTime": "2026-11-10T00:00:00Z"})
    print(json.dumps(entries))


def main():
    command, args = sys.argv[1], sys.argv[2:]
    if os.environ.get("FAKE_DRIVE_LOG"):
        with open(os.environ["FAKE_DRIVE_LOG"], "a") as handle:
            handle.write(" ".join([command] + positional(args)) + "\n")
    if os.environ.get("FAKE_DRIVE_FAIL") == command:
        sys.stderr.write("ERROR : stub: %s fails on request\n" % command)
        sys.exit(1)
    pos = positional(args)
    if command == "version":
        print("rclone v0-stub")
    elif command == "listremotes":
        required = os.environ.get("FAKE_RCLONE_CONFIG")  # the remote exists only in this config file
        given = args[args.index("--config") + 1] if "--config" in args else None
        if not required or given == required:
            print(REMOTE)
    elif command == "copyto":
        source, target = local(pos[0]), local(pos[1])
        if not source.is_file():
            missing(pos[0])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(source), str(target))
    elif command == "copy":
        source, target = local(pos[0]), local(pos[1])
        if not source.is_dir():
            missing(pos[0])
        for path in files_under(source, excludes(args)):
            out = target / path.relative_to(source)
            out.parent.mkdir(parents=True, exist_ok=True)
            data = path.read_bytes()
            if os.environ.get("FAKE_DRIVE_CORRUPT") == "1" and data:
                data = data[:-1]
            out.write_bytes(data)
        sys.stderr.write("Transferred: stub\n")
    elif command == "cat":
        path = local(pos[0])
        if not path.is_file():
            missing(pos[0])
        sys.stdout.write(path.read_text())
    elif command == "check":
        source, target = local(pos[0]), local(pos[1])
        if not source.is_dir():
            missing(pos[0])
        bad = [p for p in files_under(source, excludes(args))
               if not (target / p.relative_to(source)).is_file() or digest(target / p.relative_to(source)) != digest(p)]
        if bad:
            sys.stderr.write("%d differences found\n" % len(bad))
            sys.exit(1)
    elif command == "deletefile":
        path = local(pos[0])
        if not path.is_file():
            missing(pos[0])
        path.unlink()
    elif command == "rmdir":
        try:
            local(pos[0]).rmdir()
        except OSError:
            sys.exit(1)
    elif command == "lsjson":
        lsjson(args)
    elif command == "purge":
        if "--drive-use-trash=false" not in args:  # Drive's trash still counts against the quota
            sys.exit("rclone stub: purge without --drive-use-trash=false frees no Drive quota")
        path = local(pos[0])
        if not path.is_dir():
            missing(pos[0])
        shutil.rmtree(str(path))
    elif command == "about":
        usage = shutil.disk_usage(str(ROOT))
        print(json.dumps({"total": usage.total, "used": usage.used, "free": usage.free}))
    else:
        sys.exit("rclone stub: unsupported command " + command)


if __name__ == "__main__":
    main()
