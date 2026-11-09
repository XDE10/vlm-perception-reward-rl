"""A stand-in for the `rclone` CLI used by the Drive tests.

Maps the remote ``mydrive:`` onto the directory $FAKE_DRIVE_ROOT. Supports the
subset scripts/colab/drive.py uses: version, listremotes, copyto, copy, cat,
check (--one-way, --exclude), deletefile, rmdir, plus ``--config <file>``.
FAKE_DRIVE_CORRUPT=1 makes `copy` drop the last byte of every file so `check`
must fail; FAKE_RCLONE_CONFIG=<file> lists the remote only under that config.
"""
import fnmatch
import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(os.environ["FAKE_DRIVE_ROOT"])
REMOTE = "mydrive:"


def local(path):
    if path.startswith(REMOTE):
        return ROOT / path[len(REMOTE):].lstrip("/")
    return Path(path)


def excludes(args):
    return [args[i + 1] for i, a in enumerate(args) if a == "--exclude"]


def positional(args):
    out, skip = [], False
    for i, a in enumerate(args):
        if skip:
            skip = False
            continue
        if a in ("--exclude", "--transfers", "--checkers", "--retries", "--low-level-retries", "--stats",
                 "--stats-log-level", "--config"):
            skip = True
            continue
        if a.startswith("--"):
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


def main():
    command, args = sys.argv[1], sys.argv[2:]
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
            sys.exit(3)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(source), str(target))
    elif command == "copy":
        source, target = local(pos[0]), local(pos[1])
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
            sys.exit(3)
        sys.stdout.write(path.read_text())
    elif command == "check":
        source, target = local(pos[0]), local(pos[1])
        bad = [p for p in files_under(source, excludes(args))
               if not (target / p.relative_to(source)).is_file() or digest(target / p.relative_to(source)) != digest(p)]
        if bad:
            sys.stderr.write("%d differences found\n" % len(bad))
            sys.exit(1)
    elif command == "deletefile":
        path = local(pos[0])
        if not path.is_file():
            sys.exit(3)
        path.unlink()
    elif command == "rmdir":
        try:
            local(pos[0]).rmdir()
        except OSError:
            sys.exit(1)
    else:
        sys.exit("rclone stub: unsupported command " + command)


if __name__ == "__main__":
    main()
