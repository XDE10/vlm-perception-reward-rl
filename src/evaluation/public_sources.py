"""Pinned public sources for evaluation: download, verify against the committed ledger, read wrapper rows.

The files are the ones ``scripts/data/prepare_project3_sources.py`` pinned (same revisions). Expected sizes and
SHA256 come from ``migration_manifest.json`` (entries ``data/project3_sources/<source>/<name>``), which is part of
every commit, so the VM checks downloads against values it did not download. Nothing here trusts the download.
Public files never go into the private data pack and never into a results branch.
"""
import hashlib
import io
import json
import os
import time
import urllib.request
from pathlib import Path

BASES = {
    "geometry3k": "https://huggingface.co/datasets/hiyouga/geometry3k/resolve/fd21e533e1e50d0662a2bf7b223e60511bd5f8b7/",
    "intergps": "https://raw.githubusercontent.com/lupantech/InterGPS/99e6b5293c7bb4a5eaf2a370e6b213c79ab33ebb/",
    "mathvista": "https://huggingface.co/datasets/AI4Math/MathVista/resolve/2b6ad69445fbb5695c9b165475e8decdbeb97747/",
}
WRAPPER = {split: "geometry3k/data/%s-00000-of-00001.parquet" % split for split in ("train", "validation", "test")}
LEDGER_PREFIX = "data/project3_sources/"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ledger(repo_root):
    """{relative source name: {"bytes", "sha256"}} for every pinned public source in migration_manifest.json."""
    manifest = json.loads((Path(repo_root) / "migration_manifest.json").read_text(encoding="utf-8"))
    return {f["path"][len(LEDGER_PREFIX):]: {"bytes": f["bytes"], "sha256": f["sha256"]} for f in manifest["files"]
            if f["path"].startswith(LEDGER_PREFIX) and "/range_cache/" not in f["path"]}


def url(name):
    source, rest = name.split("/", 1)
    return BASES[source] + rest


def check_file(path, expected):
    path = Path(path)
    if not path.is_file():
        return "missing"
    if path.stat().st_size != expected["bytes"]:
        return "size %d, expected %d" % (path.stat().st_size, expected["bytes"])
    if sha256_file(path) != expected["sha256"]:
        return "SHA256 differs from the ledger"
    return None


def fetch(name, dest_root, expected, tries=4, timeout=300, opener=None):
    """Download one pinned file into dest_root/name unless a verified copy is there. Returns a report dict."""
    target = Path(dest_root) / name
    started = time.time()
    if check_file(target, expected) is None:
        return {"name": name, "ok": True, "reused": True, "bytes": expected["bytes"], "seconds": 0.0}
    target.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for attempt in range(1, tries + 1):
        part = target.with_name(target.name + ".part")
        try:
            request = urllib.request.Request(url(name), headers={"User-Agent": "p3-public-sources/1"})
            with (opener or urllib.request.urlopen)(request, timeout=timeout) as response, open(str(part), "wb") as out:
                while True:
                    block = response.read(1 << 20)
                    if not block:
                        break
                    out.write(block)
            problem = check_file(part, expected)
            if problem is None:
                os.replace(str(part), str(target))
                return {"name": name, "ok": True, "reused": False, "bytes": expected["bytes"], "attempts": attempt,
                        "seconds": round(time.time() - started, 1)}
            errors.append(problem)
        except Exception as exc:  # network errors are retried and reported, never raised
            errors.append("%s: %s" % (type(exc).__name__, str(exc)[:200]))
        part.unlink(missing_ok=True)
        if attempt < tries:
            time.sleep(min(60, 5 * attempt))
    return {"name": name, "ok": False, "errors": errors, "seconds": round(time.time() - started, 1)}


def image_pixel_sha256(image):
    """The project's pixel identity (src/data/project3_audit.image_hash) of a PIL image."""
    rgb = image.convert("RGB")
    return hashlib.sha256(str(rgb.size).encode() + b"\0" + rgb.tobytes()).hexdigest()


def read_wrapper(path, with_images=False):
    """Rows of a pinned Geometry3K wrapper parquet in file order: problem, answer, pixel (and the PIL image)."""
    import pyarrow.parquet as pq
    from PIL import Image

    rows = []
    for row in pq.read_table(str(path), columns=["images", "problem", "answer"]).to_pylist():
        image = Image.open(io.BytesIO(row["images"][0]["bytes"])).convert("RGB")
        item = {"problem": row["problem"], "answer": row["answer"], "pixel": image_pixel_sha256(image)}
        if with_images:
            item["image"] = image
        rows.append(item)
    return rows


__all__ = ["BASES", "WRAPPER", "check_file", "fetch", "image_pixel_sha256", "ledger", "read_wrapper", "sha256_file",
           "url"]
