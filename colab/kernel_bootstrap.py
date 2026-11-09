# Executed inside the Colab kernel by colab/launch.sh via `colab exec -f` (standard library only).
# Joins and verifies the uploaded code archive, extracts it to <root>/repo, then hands over to
# scripts.colab.bootstrap (data pack, venv, model). Paths derive from P3_REMOTE_ROOT (default /content/p3).
import hashlib
import json
import os
import shutil
import sys
import tarfile
from pathlib import Path


def _p3_kernel_bootstrap():
    root = Path(os.environ.get("P3_REMOTE_ROOT", "/content/p3"))
    inbox = root / "inbox"
    request = json.loads((inbox / "request.json").read_text(encoding="utf-8"))
    code = request["code"]
    archive = inbox / code["name"]
    digest = hashlib.sha256()
    with open(str(archive) + ".joining", "wb") as out:
        for part in code["parts"]:
            data = (inbox / part["name"]).read_bytes()
            if len(data) != part["bytes"] or hashlib.sha256(data).hexdigest() != part["sha256"]:
                print("[p3] BOOTSTRAP_FAILED code part %s is corrupt" % part["name"], flush=True)
                return
            out.write(data)
            digest.update(data)
    if digest.hexdigest() != code["sha256"]:
        print("[p3] BOOTSTRAP_FAILED code archive SHA256 mismatch", flush=True)
        return
    os.replace(str(archive) + ".joining", str(archive))
    repo = root / "repo"
    marker = repo / ".colab_code.json"
    if not (marker.is_file() and json.loads(marker.read_text()).get("sha256") == code["sha256"]):
        if repo.exists():
            shutil.rmtree(str(repo))
        repo.mkdir(parents=True)
        with tarfile.open(str(archive), "r:gz") as tar:
            for member in tar.getmembers():
                if Path(member.name).is_absolute() or ".." in Path(member.name).parts or member.issym() or member.islnk():
                    print("[p3] BOOTSTRAP_FAILED unsafe member in code archive: %s" % member.name, flush=True)
                    return
            try:
                tar.extractall(str(repo), filter="data")
            except TypeError:  # Python without tarfile extraction filters
                tar.extractall(str(repo))
        marker.write_text(json.dumps({"sha256": code["sha256"], "commit": code.get("commit")}), encoding="utf-8")
    print("[p3] code %s extracted to %s" % ((code.get("commit") or "?")[:12], repo), flush=True)
    for name in list(sys.modules):  # the kernel persists across execs: never reuse modules from an older checkout
        if name == "scripts" or name.startswith(("scripts.", "src.")) or name == "src":
            del sys.modules[name]
    if str(repo) in sys.path:
        sys.path.remove(str(repo))
    sys.path.insert(0, str(repo))
    from scripts.colab.bootstrap import main

    main(root, request)


_p3_kernel_bootstrap()
