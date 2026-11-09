# Executed inside the Colab kernel by colab/launch.sh via `colab exec -f` (standard library only).
# Lists every file in the upload inbox with its size and SHA256 so the launcher can re-upload only
# missing or damaged parts.
import hashlib
import json
import os


def _p3_inbox():
    inbox = os.path.join(os.environ.get("P3_REMOTE_ROOT", "/content/p3"), "inbox")
    os.makedirs(inbox, exist_ok=True)
    listing = {}
    for name in sorted(os.listdir(inbox)):
        path = os.path.join(inbox, name)
        if os.path.isfile(path):
            digest = hashlib.sha256()
            with open(path, "rb") as handle:
                for block in iter(lambda: handle.read(1 << 22), b""):
                    digest.update(block)
            listing[name] = [os.path.getsize(path), digest.hexdigest()]
    print("[p3] INBOX " + json.dumps(listing), flush=True)


_p3_inbox()
