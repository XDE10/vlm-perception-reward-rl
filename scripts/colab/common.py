"""Standard-library helpers shared by the local launcher and the Colab VM side.

Must stay importable on plain ``python3`` >= 3.8 (the user's WSL2 interpreter)
and inside the Colab kernel, so no third-party imports and no 3.9+ syntax.
"""
import hashlib
import json
import os
import sys
import threading
import time
from pathlib import Path

REMOTE_ROOT_DEFAULT = "/content/p3"
# `colab upload`/`download` move a whole file as one base64 JSON body through the runtime proxy; 8 MiB parts
# failed after ~150 s on a slow uplink (preflight-20261109T014903Z-9e57), so parts are 2 MiB (D29).
PART_BYTES = 2 * 1024 * 1024
REQUEST_SCHEMA = "p3-colab-request-v1"


def remote_root():
    return Path(os.environ.get("P3_REMOTE_ROOT", REMOTE_ROOT_DEFAULT))


def sha256_file(path, chunk=1 << 22):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    """Atomic JSON write (temp file + rename) so pollers never read a half-written file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(path))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def split_file(path, part_bytes=PART_BYTES):
    """Split ``path`` into ``path.partNNN`` files; return [{name, bytes, sha256}]."""
    path = Path(path)
    parts = []
    with open(str(path), "rb") as handle:
        index = 0
        while True:
            block = handle.read(part_bytes)
            if not block:
                break
            name = "%s.part%03d" % (path.name, index)
            (path.parent / name).write_bytes(block)
            parts.append({"name": name, "bytes": len(block), "sha256": hashlib.sha256(block).hexdigest()})
            index += 1
    if not parts:
        name = "%s.part000" % path.name
        (path.parent / name).write_bytes(b"")
        parts.append({"name": name, "bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()})
    return parts


def join_parts(directory, parts, out_path, expected_sha256):
    """Concatenate verified parts into ``out_path`` and check the whole-file SHA256."""
    directory, out_path = Path(directory), Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    tmp = out_path.with_name(out_path.name + ".joining")
    with open(str(tmp), "wb") as out:
        for part in parts:
            data = (directory / part["name"]).read_bytes()
            if len(data) != part["bytes"] or hashlib.sha256(data).hexdigest() != part["sha256"]:
                raise ValueError("part %s is corrupt or incomplete" % part["name"])
            out.write(data)
            digest.update(data)
    if digest.hexdigest() != expected_sha256:
        tmp.unlink()
        raise ValueError("joined file %s has the wrong SHA256" % out_path.name)
    os.replace(str(tmp), str(out_path))
    return out_path


def log(message, prefix="[p3]"):
    stamp = time.strftime("%H:%M:%S")
    sys.stdout.write("%s %s %s\n" % (prefix, stamp, message))
    sys.stdout.flush()


class Heartbeat(object):
    """Print a line every ``interval`` seconds while a long operation runs (keeps idle timers alive)."""

    def __init__(self, label, interval=30.0, detail=None):
        self.label, self.interval, self.detail = label, float(interval), detail
        self._stop = threading.Event()
        self._thread = None
        self.started = time.time()

    def __enter__(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def _run(self):
        while not self._stop.wait(self.interval):
            extra = ""
            if self.detail is not None:
                try:
                    extra = " | " + str(self.detail())
                except Exception as exc:  # heartbeat must never kill the work it reports on
                    extra = " | (detail unavailable: %s)" % type(exc).__name__
            log("%s ... %s elapsed%s" % (self.label, format_seconds(time.time() - self.started), extra))

    def __exit__(self, *exc):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
        return False


def format_seconds(seconds):
    seconds = int(seconds)
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return "%dh%02dm%02ds" % (hours, minutes, secs) if hours else "%dm%02ds" % (minutes, secs)


def tail(path, lines=20, max_bytes=65536):
    path = Path(path)
    if not path.is_file():
        return ""
    with open(str(path), "rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(0, size - max_bytes))
        data = handle.read().decode("utf-8", "replace")
    return "\n".join(data.splitlines()[-lines:])


__all__ = ["Heartbeat", "PART_BYTES", "REMOTE_ROOT_DEFAULT", "REQUEST_SCHEMA", "format_seconds", "join_parts", "log",
           "read_json", "remote_root", "sha256_file", "split_file", "tail", "write_json"]
