"""Push a run's results from the Colab VM to GitHub with a credential the user placed there (D37).

The user writes one git-credential-store line (``https://<user>:<PAT>@github.com``) to
``/content/gh_credentials`` in ``colab console`` (bash ``read -rsp``, colab/README.md section 8). The
launcher never sees or transfers it: the request only names the file and the target branch. This module
never opens the file either; git reads it through ``credential.helper=store --file=<path>``, with
``GIT_TERMINAL_PROMPT=0`` so a rejected credential fails instead of waiting for input.

* ``check``: fetch the run's commit (depth 1) and ``git push --dry-run`` it to ``results/<run_id>``. The dry
  run authenticates against receive-pack, so it proves write access, and it changes nothing.
* ``push``: unpack the results archive under ``reports/colab_runs_<day>/<run_id>/`` on top of that commit,
  drop files over the size limit (listed in SKIPPED_LARGE_FILES.txt), redact credential-like strings, commit
  as p3-colab-vm and push ``results/<run_id>``. The launcher later adds its own logs (``_local/``) on top.

Neither raises: every failure is reported, and the launcher then pushes the results itself (as before D37).
Standard library plus the ``git`` CLI.
"""
import os
import shutil
import stat
import subprocess
import tarfile
import time
from pathlib import Path

from scripts.colab.common import log, write_json

VM_NAME = "p3-colab-vm"
VM_EMAIL = "p3-colab-vm@users.noreply.github.com"
TIMEOUTS = {"local": 120, "fetch": 600, "dry_run": 300, "push": 900}


def settings(request):
    """The request's push target, or None when the launcher did not ask for a VM-side push."""
    gh = dict(request.get("github") or {})
    if gh.get("mode", "off") == "off" or not all(gh.get(k) for k in ("url", "branch", "base_commit", "day", "credentials")):
        return None
    return gh


def _redact(text):
    from scripts.colab.local_tools import redact_text

    return redact_text(text or "")[0]


def _git(gh, workdir, args, timeout):
    """Run git with only the user's credential file as helper; returns (rc, combined output). Never raises."""
    cmd = ["git", "-c", "credential.helper=", "-c", "credential.helper=store --file=" + str(gh["credentials"]),
           "-c", "init.defaultBranch=main", "-c", "advice.detachedHead=false"] + list(args)
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="", SSH_ASKPASS="")
    try:
        proc = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 124, "timed out after %ss" % timeout
    except OSError as exc:
        return 127, "%s: %s" % (type(exc).__name__, exc)
    return proc.returncode, _redact((proc.stdout or "") + (proc.stderr or "")).strip()


def _workdir(root, request):
    return Path(root) / "github" / request["run_id"]


def _explain(output, default):
    lowered = output.lower()
    if "authentication failed" in lowered or "could not read username" in lowered or "invalid username or" in lowered:
        return "the credential in the file was rejected (expired, mistyped, or the file is empty)"
    if ("permission to" in lowered and "denied" in lowered) or "403" in lowered:
        return "the credential has no write access to this repository"
    return "%s: %s" % (default, output[-400:])


def check(root, request):
    """Can this VM push the results? Prepares the work directory used by ``push``."""
    gh = settings(request)
    if gh is None:
        return {"mode": "off", "ok": False, "reason": "the launcher did not ask for a VM-side push"}
    creds = Path(gh["credentials"])
    info = {"mode": gh.get("mode"), "branch": gh["branch"], "url": gh["url"], "credentials_file": str(creds),
            "credentials_present": creds.is_file(), "ok": False}
    if not creds.is_file():
        info["reason"] = ("no credential file at %s, so the launcher pushes the results from your machine "
                          "(to let the VM push, see colab/README.md section 8)" % creds)
        return info
    mode = stat.S_IMODE(creds.stat().st_mode)
    info["credentials_mode"] = oct(mode)
    if mode & 0o077:
        info["warning"] = "the credential file is readable by other users; chmod 600 it"
    workdir = _workdir(root, request)
    shutil.rmtree(str(workdir), ignore_errors=True)
    workdir.mkdir(parents=True)
    started = time.time()
    rc, out = _git(gh, workdir, ["init", "-q"], TIMEOUTS["local"])
    if rc != 0:
        info["reason"] = "git is not usable on this VM: " + out[-300:]
        return info
    rc, out = _git(gh, workdir, ["fetch", "-q", "--depth", "1", gh["url"], gh["base_commit"]], TIMEOUTS["fetch"])
    if rc != 0:
        info["reason"] = _explain(out, "could not fetch the run's commit %s (is it pushed?)" % gh["base_commit"][:12])
        return info
    rc, out = _git(gh, workdir, ["push", "--dry-run", "-q", gh["url"], "FETCH_HEAD:refs/heads/" + gh["branch"]],
                   TIMEOUTS["dry_run"])
    info.update(push_access=rc == 0, seconds=round(time.time() - started, 1), workdir=str(workdir))
    if rc != 0:
        info["reason"] = _explain(out, "the dry-run push was refused")
        return info
    info["ok"] = True
    return info


def _extract(archive, parent):
    with tarfile.open(str(archive), "r:gz") as tar:
        for member in tar.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise ValueError("unsafe member in results archive: %s" % member.name)
        try:
            tar.extractall(str(parent), filter="data")
        except TypeError:  # Python without extraction filters
            tar.extractall(str(parent))


def _drop_large(dest, limit_bytes):
    large = sorted(p for p in dest.rglob("*") if p.is_file() and p.stat().st_size > limit_bytes)
    if large:
        (dest / "SKIPPED_LARGE_FILES.txt").write_text(
            "".join("%s\t%d\n" % (p.relative_to(dest), p.stat().st_size) for p in large), encoding="utf-8")
        for path in large:
            path.unlink()
    return len(large)


def push(root, request, archive, overall=None, prior_check=None):
    """Commit the results archive on top of the run's commit and push results/<run_id>. Never raises."""
    gh = settings(request)
    if gh is None:
        return {"attempted": False, "ok": False, "reason": "the launcher did not ask for a VM-side push"}
    started = time.time()
    result = {"attempted": False, "ok": False, "branch": gh["branch"]}
    try:
        info = prior_check if prior_check and prior_check.get("ok") else check(root, request)
        if not info.get("ok"):
            result["reason"] = info.get("reason")
            return result
        result["attempted"] = True
        workdir = _workdir(root, request)
        rc, out = _git(gh, workdir, ["checkout", "-q", "--detach", "FETCH_HEAD"], TIMEOUTS["local"])
        if rc != 0:
            result["reason"] = "could not check out the run's commit: " + out[-300:]
            return result
        parent = workdir / "reports" / ("colab_runs_" + gh["day"])
        dest = parent / request["run_id"]
        shutil.rmtree(str(dest), ignore_errors=True)
        parent.mkdir(parents=True, exist_ok=True)
        _extract(archive, parent)
        if not dest.is_dir():
            result["reason"] = "the results archive has no %s/ directory" % request["run_id"]
            return result
        result["skipped_large"] = _drop_large(dest, int(float(gh.get("max_file_mb", 25)) * 1024 * 1024))
        from scripts.colab.local_tools import redact_tree

        redacted = redact_tree(dest)
        if redacted:
            (dest / "REDACTIONS_VM.txt").write_text("credentials redacted on the VM before pushing (file: count)\n" +
                                                   "".join("%s: %d\n" % kv for kv in sorted(redacted.items())),
                                                   encoding="utf-8")
        result["redacted"] = sum(redacted.values())
        files = [p for p in dest.rglob("*") if p.is_file()]
        result.update(files=len(files), bytes=sum(p.stat().st_size for p in files))
        rel = str(dest.relative_to(workdir))
        rc, out = _git(gh, workdir, ["add", "-f", rel], TIMEOUTS["local"])  # *.log is ignored repo-wide
        message = "results(%s): %s overall=%s [pushed from the Colab VM]" % (gh.get("task", request.get("task")),
                                                                            request["run_id"], overall)
        if rc == 0:
            rc, out = _git(gh, workdir, ["-c", "user.name=" + VM_NAME, "-c", "user.email=" + VM_EMAIL, "commit", "-q",
                                         "--no-verify", "-m", message], TIMEOUTS["local"])
        if rc != 0:
            result["reason"] = "could not commit the results: " + out[-300:]
            return result
        rc, out = _git(gh, workdir, ["push", "-q", gh["url"], "HEAD:refs/heads/" + gh["branch"]], TIMEOUTS["push"])
        if rc != 0:
            result["reason"] = _explain(out, "the push was refused")
            return result
        rc, sha = _git(gh, workdir, ["rev-parse", "HEAD"], TIMEOUTS["local"])
        result.update(ok=True, commit=sha.strip() if rc == 0 else None)
        return result
    except Exception as exc:  # the launcher's own push is the fallback; never fail the job over this
        result["reason"] = "%s: %s" % (type(exc).__name__, _redact(str(exc))[:300])
        return result
    finally:
        result["seconds"] = round(time.time() - started, 1)


def report(out_dir, info):
    """Write github_check.json for the run summary and print one line for the live output."""
    write_json(Path(out_dir) / "github_check.json", info)
    if info.get("ok"):
        log("GitHub: the VM will push the results to %s itself (write access verified)" % info["branch"])
    elif info.get("mode") != "off":
        log("GitHub: %s" % info.get("reason"))


__all__ = ["VM_EMAIL", "VM_NAME", "check", "push", "report", "settings"]
