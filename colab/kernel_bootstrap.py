# Executed inside the Colab kernel by colab/launch.sh via `colab exec -f` (standard library only).
# Gets the code for this run, then hands over to scripts.colab.bootstrap (data pack, venv, model).
#
# Code source (decided by the launcher, recorded in request.json):
#   * "github": download the public source tarball of the exact commit and verify EVERY file against the
#     git blob SHA-1 listing of that commit sent in the request; nothing is trusted from the download itself.
#     If the download or the verification fails, print CODE_DOWNLOAD_FAILED and stop; the launcher then
#     uploads the code archive in parts and runs this script again.
#   * "upload" (or parts already present): join the uploaded parts, check the SHA256, extract.
# Paths derive from P3_REMOTE_ROOT (default /content/p3).
import hashlib
import io
import json
import os
import shutil
import sys
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path


def _safe(name):
    path = Path(name)
    return not path.is_absolute() and ".." not in path.parts


def _blob_sha1(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _parts_present(inbox, code):
    return bool(code.get("parts")) and all((inbox / p["name"]).is_file() for p in code["parts"])


def _from_parts(inbox, code, repo):
    archive = inbox / code["name"]
    digest = hashlib.sha256()
    with open(str(archive) + ".joining", "wb") as out:
        for part in code["parts"]:
            data = (inbox / part["name"]).read_bytes()
            if len(data) != part["bytes"] or hashlib.sha256(data).hexdigest() != part["sha256"]:
                return "code part %s is corrupt" % part["name"]
            out.write(data)
            digest.update(data)
    if digest.hexdigest() != code["sha256"]:
        return "code archive SHA256 mismatch"
    os.replace(str(archive) + ".joining", str(archive))
    with tarfile.open(str(archive), "r:gz") as tar:
        for member in tar.getmembers():
            if not _safe(member.name) or member.issym() or member.islnk():
                return "unsafe member in code archive: %s" % member.name
        try:
            tar.extractall(str(repo), filter="data")
        except TypeError:  # Python without tarfile extraction filters
            tar.extractall(str(repo))
    return None


def _from_github(inbox, code, repo):
    data, last_error = None, None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(code["tarball_url"], timeout=180) as response:
                data = response.read()
            break
        except Exception as exc:  # network errors are retried, then reported through the marker
            last_error = "%s: %s" % (type(exc).__name__, exc)
            print("[p3] code download attempt %d failed: %s" % (attempt, last_error), flush=True)
            if isinstance(exc, urllib.error.HTTPError) and 400 <= exc.code < 500:
                break  # e.g. 404: the commit is not public; retrying cannot help
            if attempt < 3:
                time.sleep(10 * attempt)
    if data is None:
        return "download failed: %s" % last_error
    expected = {path: (mode, sha1) for path, mode, sha1 in code["tree"]}
    found = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            if not _safe(member.name) or member.islnk():
                return "unsafe member in source tarball: %s" % member.name
            parts = member.name.split("/", 1)
            if len(parts) < 2 or not parts[1] or member.isdir() or member.name.startswith("pax_global_header"):
                continue
            rel = parts[1]
            if member.issym():
                found[rel] = ("120000", member.linkname.encode())
            elif member.isfile():
                found[rel] = ("file", tar.extractfile(member).read())
    missing = sorted(set(expected) - set(found))
    extra = sorted(set(found) - set(expected))
    if missing or extra:
        return "source tarball differs from the commit tree (missing %s, extra %s)" % (missing[:3], extra[:3])
    for rel, (mode, sha1) in expected.items():
        kind, payload = found[rel]
        if (mode == "120000") != (kind == "120000") or _blob_sha1(payload) != sha1:
            return "file %s does not match the commit (git blob SHA-1)" % rel
    for rel, (mode, _) in sorted(expected.items()):
        if mode == "120000":
            continue  # the repository has no symlinks; refuse to materialise any rather than trust them
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(found[rel][1])
        os.chmod(str(target), 0o755 if mode == "100755" else 0o644)
    return None


def _p3_kernel_bootstrap():
    root = Path(os.environ.get("P3_REMOTE_ROOT", "/content/p3"))
    inbox = root / "inbox"
    request = json.loads((inbox / "request.json").read_text(encoding="utf-8"))
    code = request["code"]
    identity = code.get("tree_sha256") or code["sha256"]
    repo = root / "repo"
    marker = repo / ".colab_code.json"
    if not (marker.is_file() and json.loads(marker.read_text()).get("identity") == identity):
        if repo.exists():
            shutil.rmtree(str(repo))
        repo.mkdir(parents=True)
        use_parts = _parts_present(inbox, code) or code.get("mode") != "github"
        error = _from_parts(inbox, code, repo) if use_parts else _from_github(inbox, code, repo)
        if error:
            shutil.rmtree(str(repo), ignore_errors=True)
            if use_parts:
                print("[p3] BOOTSTRAP_FAILED %s" % error, flush=True)
            else:
                print("[p3] CODE_DOWNLOAD_FAILED %s" % error, flush=True)
            return
        marker.write_text(json.dumps({"identity": identity, "commit": code.get("commit"),
                                      "source": "upload" if use_parts else "github"}), encoding="utf-8")
        print("[p3] code %s from %s, verified, extracted to %s" % ((code.get("commit") or "?")[:12],
                                                                  "uploaded parts" if use_parts else "GitHub", repo),
              flush=True)
    # record where the code actually came from (a GitHub request can fall back to uploaded parts)
    request = dict(request, code=dict(code, source=json.loads(marker.read_text()).get("source")))
    for name in list(sys.modules):  # the kernel persists across execs: never reuse modules from an older checkout
        if name == "scripts" or name.startswith(("scripts.", "src.")) or name == "src":
            del sys.modules[name]
    if str(repo) in sys.path:
        sys.path.remove(str(repo))
    sys.path.insert(0, str(repo))
    from scripts.colab.bootstrap import main

    main(root, request)


_p3_kernel_bootstrap()
