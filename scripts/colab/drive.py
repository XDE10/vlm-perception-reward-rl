"""Optional Google Drive persistence through the user's rclone setup (standard library only).

The user mounts another account's Drive on Colab with rclone + FUSE at
``/content/mydrive`` (rclone remote ``mydrive:``). That mount is created by the
user's own tooling, so everything here is optional and detected at run time.

Design (D31 in docs/plan/决策记录.md):

* Durable copies always go through the ``rclone`` CLI (``rclone copy`` + ``rclone
  check``), never through the FUSE mount: a write to the mount returns before the
  asynchronous upload finishes, so it is not proof of persistence. ``rclone copy``
  returns only after the upload, and ``rclone check --one-way`` compares sizes and
  hashes on the remote.
* Training reads and writes only the local disk (/content); Drive receives verified
  copies at the end of a run (and, from S4 on, at checkpoint boundaries).
* Nothing outside ``<remote><base dir>`` is touched; the probe deletes only the exact
  files it created a moment earlier. The S4 helpers (``copy_verify`` ... ``purge``) take
  paths relative to that directory and refuse anything that is not a plain relative path.

    python -m scripts.colab.drive probe   --out <json> [--remote mydrive:] [--dir ColabProjects/...] [--mount /content/mydrive]
    python -m scripts.colab.drive persist --src <dir> --dest runs/<run_id> --out <json> [...]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_REMOTE = "mydrive:"
DEFAULT_DIR = "ColabProjects/vlm-perception-reward-rl"
DEFAULT_MOUNT = "/content/mydrive"
COPY_FLAGS = ["--transfers", "4", "--checkers", "8", "--retries", "5", "--low-level-retries", "10",
              "--stats", "30s", "--stats-one-line", "--stats-log-level", "NOTICE"]


def _settings(remote=None, base_dir=None, mount=None):
    remote = remote or os.environ.get("P3_DRIVE_REMOTE") or DEFAULT_REMOTE
    if not remote.endswith(":") and ":" not in remote:
        remote += ":"
    base_dir = (base_dir or os.environ.get("P3_DRIVE_DIR") or DEFAULT_DIR).strip("/")
    mount = mount or os.environ.get("P3_DRIVE_MOUNT") or DEFAULT_MOUNT
    return remote, base_dir, mount


def _run(cmd, timeout=600, input_bytes=None):
    """Run a command; never raises (timeout -> rc 124, not runnable -> rc 127)."""
    started = time.time()
    try:
        proc = subprocess.run(cmd, input=input_bytes, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "timed out after %ss" % timeout, time.time() - started
    except OSError as exc:
        return 127, "", "%s: %s" % (type(exc).__name__, exc), time.time() - started
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace"), time.time() - started


def remote_path(remote, base_dir, rel=""):
    rel = rel.strip("/")
    return remote + base_dir + ("/" + rel if rel else "")


def mount_process_config(proc_root="/proc"):
    """``--config`` of a running ``rclone mount``: the user's mount may use a non-default config file."""
    for cmdline in sorted(Path(proc_root).glob("[0-9]*/cmdline")):
        try:
            args = [a.decode("utf-8", "replace") for a in cmdline.read_bytes().split(b"\0") if a]
        except OSError:
            continue
        if not args or not os.path.basename(args[0]).startswith("rclone") or not {"mount", "nfsmount"} & set(args):
            continue
        for i, arg in enumerate(args):
            if arg == "--config" and i + 1 < len(args):
                return args[i + 1]
            if arg.startswith("--config="):
                return arg.split("=", 1)[1]
    return None


def rclone_cmd(info, *args):
    """argv for an rclone call, with the config file detected by ``detect`` (if any) appended."""
    return [info["rclone"]] + [str(a) for a in args] + (["--config", info["config"]] if info.get("config") else [])


def _list_remotes(info):
    rc, out, err, _ = _run(rclone_cmd(info, "listremotes"), timeout=60)
    if rc != 0:
        info["notes"].append("rclone listremotes failed: " + err.strip()[:200])
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def detect(remote=None, base_dir=None, mount=None, proc_root="/proc"):
    """What persistence is available on this VM. Never raises."""
    remote, base_dir, mount = _settings(remote, base_dir, mount)
    info = {"remote": remote, "base_dir": base_dir, "mount": mount, "rclone": shutil.which("rclone"),
            "rclone_version": None, "config": None, "config_source": "default", "remote_configured": False,
            "mount_present": False, "usable": False, "method": None, "notes": []}
    mount_path = Path(mount)
    info["mount_present"] = os.path.ismount(str(mount_path)) or (mount_path.is_dir() and any(True for _ in _safe_iter(mount_path)))
    if info["rclone"]:
        rc, out, err, _ = _run(rclone_cmd(info, "version"), timeout=60)
        info["rclone_version"] = out.splitlines()[0] if rc == 0 and out else None
        if rc == 127:
            info["notes"].append("rclone not runnable: " + err[:200])
        remotes = _list_remotes(info)
        if remote not in remotes:
            config = mount_process_config(proc_root)
            if config:  # fall back to the config file of the user's running mount
                info.update(config=config, config_source="running rclone mount")
                remotes = _list_remotes(info)
                if remote not in remotes:
                    info.update(config=None, config_source="default")
        info["remotes"] = remotes
        info["remote_configured"] = remote in remotes
    else:
        info["notes"].append("rclone is not on PATH (Drive persistence needs the rclone CLI, not only the mount)")
    if info["remote_configured"]:
        info.update(usable=True, method="rclone")
    elif info["rclone"]:
        info["notes"].append("rclone remote %s is not configured on this VM" % remote)
    if info["mount_present"] and not info["usable"]:
        info["notes"].append("a mount exists, but mount writes are asynchronous and cannot be verified, so they are "
                             "not used for persistence")
    return info


def _safe_iter(path):
    try:
        for item in path.iterdir():
            yield item
    except OSError:
        return


def _md5(path):
    digest = hashlib.md5()
    with open(str(path), "rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def probe(run_id, scratch, remote=None, base_dir=None, mount=None, size_mb=16):
    """Write, read back, verify and delete two probe files under <dir>/_p3_probe/<run_id>/; time the transfers."""
    info = detect(remote, base_dir, mount)
    result = {"schema": "p3-drive-probe-v1", "detect": info, "ok": False}
    if not info["usable"]:
        result["reason"] = "; ".join(info["notes"]) or "Drive not configured"
        return result
    remote, base_dir = info["remote"], info["base_dir"]
    scratch = Path(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    text_file, blob_file = scratch / "probe.txt", scratch / "probe.bin"
    text = "p3 drive probe %s %s\n" % (run_id, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    text_file.write_text(text, encoding="utf-8")
    blob_file.write_bytes(os.urandom(size_mb * 1024 * 1024))
    target = remote_path(remote, base_dir, "_p3_probe/" + run_id)
    steps = {}
    rc, out, err, seconds = _run(rclone_cmd(info, "copyto", text_file, target + "/probe.txt"), timeout=600)
    steps["upload_text"] = {"rc": rc, "seconds": round(seconds, 2), "error": err.strip()[-300:] if rc else None}
    rc, out, err, seconds = _run(rclone_cmd(info, "cat", target + "/probe.txt"), timeout=600)
    steps["read_back_text"] = {"rc": rc, "seconds": round(seconds, 2), "matches": out == text}
    rc, out, err, seconds = _run(rclone_cmd(info, "copyto", blob_file, target + "/probe.bin"), timeout=1800)
    steps["upload_blob"] = {"rc": rc, "seconds": round(seconds, 2), "mb_per_s": round(size_mb / seconds, 1) if rc == 0 and seconds else None}
    back = scratch / "probe_back.bin"
    rc, out, err, seconds = _run(rclone_cmd(info, "copyto", target + "/probe.bin", back), timeout=1800)
    steps["download_blob"] = {"rc": rc, "seconds": round(seconds, 2), "mb_per_s": round(size_mb / seconds, 1) if rc == 0 and seconds else None,
                              "md5_matches": rc == 0 and back.is_file() and _md5(back) == _md5(blob_file)}
    rc, out, err, seconds = _run(rclone_cmd(info, "check", scratch, target, "--one-way", "--exclude", "probe_back.bin"), timeout=900)
    steps["rclone_check"] = {"rc": rc, "identical": rc == 0}
    mount_file = None
    if info["mount_present"]:
        mount_file = Path(info["mount"]) / base_dir / "_p3_probe" / run_id / "via_mount.txt"
        try:
            mount_file.parent.mkdir(parents=True, exist_ok=True)
            mount_file.write_text(text, encoding="utf-8")
            started, visible = time.time(), False
            while time.time() - started < 120:
                rc, out, err, _ = _run(rclone_cmd(info, "cat", target + "/via_mount.txt"), timeout=120)
                if rc == 0 and out == text:
                    visible = True
                    break
                time.sleep(5)
            steps["mount_write"] = {"visible_on_remote": visible, "seconds_until_visible": round(time.time() - started, 1)}
        except OSError as exc:
            steps["mount_write"] = {"error": "%s: %s" % (type(exc).__name__, exc)}
    deleted = []
    for name in ["probe.txt", "probe.bin", "via_mount.txt"]:
        rc, _, _, _ = _run(rclone_cmd(info, "deletefile", target + "/" + name), timeout=300)
        if rc == 0:
            deleted.append(name)
    if mount_file is not None:
        try:  # also remove it through the mount, in case its delayed upload lands after the rclone delete
            if mount_file.exists():
                mount_file.unlink()
            mount_file.parent.rmdir()
        except OSError:
            pass
    _run(rclone_cmd(info, "rmdir", target), timeout=300)  # rmdir only removes empty directories
    _run(rclone_cmd(info, "rmdir", remote_path(remote, base_dir, "_p3_probe")), timeout=300)
    result.update(steps=steps, deleted_probe_files=deleted, target=target, size_mb=size_mb,
                  ok=all(steps[k]["rc"] == 0 for k in ["upload_text", "read_back_text", "upload_blob", "download_blob"])
                  and steps["read_back_text"]["matches"] and steps["download_blob"]["md5_matches"]
                  and steps["rclone_check"]["identical"])
    for path in [text_file, blob_file, back]:
        if path.exists():
            path.unlink()
    return result


def persist(src, dest_rel, remote=None, base_dir=None, mount=None, excludes=(), timeout=6 * 3600):
    """rclone copy ``src`` to <remote><dir>/<dest_rel> and verify with ``rclone check --one-way``.

    ``attempted`` is False when Drive is not set up on this VM (nothing was tried)."""
    info = detect(remote, base_dir, mount)
    result = {"schema": "p3-drive-persist-v1", "detect": info, "ok": False, "attempted": False, "src": str(src)}
    if not info["usable"]:
        result["reason"] = "; ".join(info["notes"]) or "Drive not configured"
        return result
    result.update(copy_verify(info, src, dest_rel, excludes=excludes, timeout=timeout))
    result["attempted"] = True
    return result


# ---- relative-path operations for the S4 runner (scripts/colab/s4_state.py) ---------------------------------------
# Every path is relative to <remote><base dir> and must match SAFE_REL, so nothing outside the project directory can
# be read, written or deleted. ``info`` is the dict returned by ``detect`` (detect once, reuse it: each rclone call
# costs seconds). None of these raise on an rclone failure; they report it.
SAFE_REL = re.compile(r"^[A-Za-z0-9._@+=-]+(/[A-Za-z0-9._@+=-]+)*$")
MISSING_RC = (3, 4)  # rclone exit codes: directory not found, file not found


def check_rel(rel):
    """``rel`` stripped of surrounding slashes; raises ValueError unless it is a plain relative path."""
    rel = str(rel).strip("/")
    if not rel or not SAFE_REL.match(rel) or any(part in (".", "..") for part in rel.split("/")):
        raise ValueError("unsafe Drive path %r" % rel)
    return rel


def target_of(info, rel):
    return remote_path(info["remote"], info["base_dir"], check_rel(rel))


def copy_verify(info, src, rel, excludes=(), timeout=6 * 3600):
    """rclone copy a local directory to ``rel`` and ``rclone check --one-way`` it; {ok, verified, files, bytes, ...}."""
    src = Path(src)
    files = [p for p in src.rglob("*") if p.is_file()]
    target = target_of(info, rel)
    extra = []
    for pattern in excludes:
        extra += ["--exclude", pattern]
    result = {"ok": False, "verified": False, "target": target, "files": len(files),
              "bytes": sum(p.stat().st_size for p in files)}
    rc, out, err, seconds = _run(rclone_cmd(info, "copy", src, target, *(COPY_FLAGS + extra)), timeout=timeout)
    result.update(copy_rc=rc, copy_seconds=round(seconds, 1), copy_log=(err or out).strip()[-1500:])
    if rc != 0:
        result["reason"] = "rclone copy failed (rc %s)" % rc
        return result
    rc, out, err, check_seconds = _run(rclone_cmd(info, "check", src, target, "--one-way", *extra), timeout=timeout)
    result.update(check_rc=rc, check_seconds=round(check_seconds, 1), verified=rc == 0,
                  check_log=(err or out).strip()[-1500:], ok=rc == 0)
    if rc != 0:
        result["reason"] = "rclone check found differences or failed (rc %s)" % rc
    return result


def fetch_verify(info, rel, dest, timeout=6 * 3600):
    """rclone copy ``rel`` (a directory) into the local ``dest`` and check every remote file arrived intact."""
    target = target_of(info, rel)
    Path(dest).mkdir(parents=True, exist_ok=True)
    result = {"ok": False, "source": target, "dest": str(dest)}
    rc, out, err, seconds = _run(rclone_cmd(info, "copy", target, dest, *COPY_FLAGS), timeout=timeout)
    result.update(copy_rc=rc, copy_seconds=round(seconds, 1), copy_log=(err or out).strip()[-1500:])
    if rc != 0:
        result["reason"] = "rclone copy from Drive failed (rc %s)" % rc
        return result
    rc, out, err, check_seconds = _run(rclone_cmd(info, "check", target, dest, "--one-way"), timeout=timeout)
    result.update(check_rc=rc, check_seconds=round(check_seconds, 1), ok=rc == 0)
    if rc != 0:
        result["reason"] = "rclone check after the download failed (rc %s)" % rc
    return result


def put_text(info, rel, text, scratch, timeout=600):
    """Write a small text file to ``rel`` (copyto replaces it) and read it back; {ok, seconds, reason}."""
    scratch = Path(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    local_file = scratch / ("put-%d-%s" % (os.getpid(), Path(check_rel(rel)).name))
    local_file.write_text(text, encoding="utf-8")
    started = time.time()
    try:
        rc, out, err, _ = _run(rclone_cmd(info, "copyto", local_file, target_of(info, rel)), timeout=timeout)
        if rc != 0:
            return {"ok": False, "reason": "rclone copyto failed (rc %s): %s" % (rc, (err or out).strip()[-300:])}
        back, status = get_text(info, rel, timeout=timeout)
        if back != text:
            return {"ok": False, "reason": "read-back differs (%s)" % status}
        return {"ok": True, "seconds": round(time.time() - started, 1)}
    finally:
        try:
            local_file.unlink()
        except OSError:
            pass


def get_text(info, rel, timeout=600):
    """(text, "ok") for an existing file; (None, "missing") when it does not exist; (None, "error: ...") otherwise."""
    rc, out, err, _ = _run(rclone_cmd(info, "cat", target_of(info, rel)), timeout=timeout)
    if rc == 0:
        return out, "ok"
    if rc in MISSING_RC or "not found" in (err or "").lower():
        return None, "missing"
    return None, "error: rclone cat rc %s: %s" % (rc, (err or out).strip()[-300:])


def list_entries(info, rel, dirs_only=False, timeout=600):
    """[{"Name", "IsDir", "Size", ...}] of the entries directly under ``rel``; [] when it does not exist; None on error."""
    args = ["lsjson", target_of(info, rel)] + (["--dirs-only"] if dirs_only else [])
    rc, out, err, _ = _run(rclone_cmd(info, *args), timeout=timeout)
    if rc in MISSING_RC or (rc != 0 and "directory not found" in (err or "").lower()):
        return []
    if rc != 0:
        return None
    try:
        return json.loads(out or "[]")
    except ValueError:
        return None


def list_tree(info, rel, max_depth=4, timeout=900):
    """Every entry under ``rel`` down to ``max_depth`` levels in one rclone call ("Path" is relative to ``rel``);
    [] when ``rel`` does not exist; None on error. One call instead of one per directory: each rclone call costs
    5-10 s on Colab (drive_probe of preflight-20261109T122305Z-e6cd)."""
    rc, out, err, _ = _run(rclone_cmd(info, "lsjson", target_of(info, rel), "-R", "--max-depth", str(int(max_depth))),
                           timeout=timeout)
    if rc in MISSING_RC or (rc != 0 and "directory not found" in (err or "").lower()):
        return []
    if rc != 0:
        return None
    try:
        return json.loads(out or "[]")
    except ValueError:
        return None


def delete_file(info, rel, timeout=600):
    rc, out, err, _ = _run(rclone_cmd(info, "deletefile", target_of(info, rel)), timeout=timeout)
    return rc == 0 or rc in MISSING_RC


def purge(info, rel, timeout=1800):
    """Delete the directory ``rel`` and everything under it, permanently. Callers decide what may be deleted
    (s4_state.py only purges older checkpoint directories of the run it is writing, after a newer one was verified).
    Without --drive-use-trash=false, Google Drive moves the directory to its trash, which still counts against the
    storage quota for 30 days: the retention rule (D58) would then free nothing."""
    rc, out, err, _ = _run(rclone_cmd(info, "purge", target_of(info, rel), "--drive-use-trash=false"), timeout=timeout)
    return {"ok": rc == 0 or rc in MISSING_RC, "rc": rc, "log": (err or out).strip()[-300:]}


def about(info, timeout=300):
    """{"total", "used", "free"} bytes of the remote as rclone reports them, or None."""
    rc, out, err, _ = _run(rclone_cmd(info, "about", info["remote"], "--json"), timeout=timeout)
    if rc != 0:
        return None
    try:
        data = json.loads(out)
    except ValueError:
        return None
    return {key: data.get(key) for key in ("total", "used", "free")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["detect", "probe", "persist"])
    parser.add_argument("--out", required=True)
    parser.add_argument("--remote")
    parser.add_argument("--dir", dest="base_dir")
    parser.add_argument("--mount")
    parser.add_argument("--run-id", default="manual")
    parser.add_argument("--scratch", default="/tmp/p3_drive_probe")
    parser.add_argument("--src")
    parser.add_argument("--dest")
    parser.add_argument("--require", action="store_true", help="exit non-zero when Drive is unavailable")
    parser.add_argument("--size-mb", type=int, default=16)
    parser.add_argument("--timeout", type=int, default=6 * 3600, help="persist: seconds allowed for copy and for check")
    args = parser.parse_args(argv)
    if args.command == "detect":
        result = detect(args.remote, args.base_dir, args.mount)
        ok = result["usable"]
    elif args.command == "probe":
        result = probe(args.run_id, args.scratch, args.remote, args.base_dir, args.mount, args.size_mb)
        ok = result["ok"]
    else:
        result = persist(args.src, args.dest, args.remote, args.base_dir, args.mount, timeout=args.timeout)
        ok = result["ok"]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": ok, "reason": result.get("reason"), "target": result.get("target")}, ensure_ascii=False))
    if not ok and (args.require or args.command == "persist"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
