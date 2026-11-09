"""Build (locally) or verify (on the VM) the private data pack for Colab runs.

    python3 -m scripts.colab.pack_private_data --data-root /path/to/data --out .colab_cache [--check-only]

The pack holds only what runs need: the approved release (rows, manifest,
protected dev ids), the images those rows reference, the InterGPS audit files
and a few small files the CPU test suite reads. Every file is verified before it
is packed, against one of three anchors committed in git or sealed in the
release:

* ``release``   - SHA256 recorded in data/portable_release/manifest.json ``files``;
* ``row``       - the row's own ``image_sha256`` (images referenced by release rows);
* ``ledger``    - the entry in migration_manifest.json (everything else).

Nothing is rewritten: a mismatch fails closed. Standard library only (runs on the
user's ``python3`` >= 3.8 and in the Colab kernel).
"""
import argparse
import gzip
import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK_SCHEMA = "p3-private-pack-v1"
PACK_MANIFEST = "PACK_MANIFEST.json"
RELEASE_DIR = "data/portable_release"
REQUIRED_LEDGER = ["data/project3_audit/intergps_annotations.jsonl"]
OPTIONAL_LEDGER_PREFIXES = [
    "data/project3_audit/",  # Geometry3K <-> InterGPS links and MathVista overlap audit (evaluation stage)
    "data/project3_sources/manifest.json",  # pinned public source SHA256s (sources are re-downloaded on the VM)
    "data/tokenizers/Qwen2.5-7B-Instruct/",  # legacy config directory checked by tests/test_repo_layout.py
    "data/synthesis_mock/",  # read by tests/test_delivery_artifacts.py
]


def _sha256(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def _on_disk(data_root, rel):
    if not rel.startswith("data/"):
        raise ValueError("pack paths must start with data/: %s" % rel)
    return Path(data_root) / rel[len("data/"):]


def _ledger(repo_root):
    manifest = json.loads((Path(repo_root) / "migration_manifest.json").read_text(encoding="utf-8"))
    return {entry["path"]: entry for entry in manifest["files"]}


def _release_sha(value):
    return value["sha256"] if isinstance(value, dict) else value


def plan_entries(data_root, repo_root=ROOT):
    """Return (entries, missing_optional) where entries = [{path, bytes, sha256, anchor}] (not yet verified)."""
    ledger = _ledger(repo_root)
    release_manifest_rel = RELEASE_DIR + "/manifest.json"
    manifest_path = _on_disk(data_root, release_manifest_rel)
    if not manifest_path.is_file():
        raise FileNotFoundError("release manifest not found at %s (check --data-root / P3_DATA_ROOT)" % manifest_path)
    release = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = {}

    def add(rel, sha, anchor, size=None):
        if rel in entries and entries[rel]["sha256"] != sha:
            raise ValueError("conflicting expected SHA256 for %s" % rel)
        entries[rel] = {"path": rel, "sha256": sha, "anchor": anchor, "bytes": size}

    ledger_entry = ledger.get(release_manifest_rel)
    if ledger_entry is None:
        raise ValueError("migration_manifest.json has no entry for %s" % release_manifest_rel)
    add(release_manifest_rel, ledger_entry["sha256"], "ledger", ledger_entry["bytes"])
    for name, value in sorted(release["files"].items()):
        add(RELEASE_DIR + "/" + name, _release_sha(value), "release")
    for name in sorted(release["files"]):
        if not name.endswith(".jsonl"):
            continue
        with open(str(_on_disk(data_root, RELEASE_DIR + "/" + name)), encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                image = row.get("image_path")
                if not image:
                    continue
                if Path(image).is_absolute() or ".." in Path(image).parts:
                    raise ValueError("release row %s has a non-relative image path" % row.get("sample_id"))
                if not row.get("image_sha256"):
                    raise ValueError("release row %s has no image_sha256" % row.get("sample_id"))
                ledger_image = ledger.get(image)
                if ledger_image is not None and ledger_image["sha256"] != row["image_sha256"]:
                    raise ValueError("row and ledger disagree on %s" % image)
                add(image, row["image_sha256"], "row", ledger_image["bytes"] if ledger_image else None)
    for rel in REQUIRED_LEDGER:
        if rel not in ledger:
            raise ValueError("migration_manifest.json has no entry for required file %s" % rel)
        add(rel, ledger[rel]["sha256"], "ledger", ledger[rel]["bytes"])
    missing_optional = []
    for rel, entry in sorted(ledger.items()):
        if rel in entries or not any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in OPTIONAL_LEDGER_PREFIXES):
            continue
        if _on_disk(data_root, rel).is_file():
            add(rel, entry["sha256"], "ledger", entry["bytes"])
        else:
            missing_optional.append(rel)
    return [entries[k] for k in sorted(entries)], missing_optional


def verify_entries(entries, data_root):
    """Check presence, size and SHA256 of every planned file; return the list of problems."""
    problems = []
    for entry in entries:
        path = _on_disk(data_root, entry["path"])
        if not path.is_file():
            problems.append("missing: " + entry["path"])
            continue
        size = path.stat().st_size
        if entry["bytes"] is not None and size != entry["bytes"]:
            problems.append("size changed: %s (%d != %d)" % (entry["path"], size, entry["bytes"]))
            continue
        if _sha256(path) != entry["sha256"]:
            problems.append("hash changed: " + entry["path"])
            continue
        entry["bytes"] = size
    return problems


def content_sha256(entries):
    payload = json.dumps([[e["path"], e["sha256"]] for e in entries], separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _tarinfo(name, size):
    info = tarfile.TarInfo(name)
    info.size, info.mtime, info.mode, info.uid, info.gid = size, 0, 0o644, 0, 0
    info.uname = info.gname = ""
    return info


def build_pack(data_root, out_dir, repo_root=ROOT):
    entries, missing_optional = plan_entries(data_root, repo_root)
    problems = verify_entries(entries, data_root)
    if problems:
        raise ValueError("data verification failed (%d problems), first: %s" % (len(problems), problems[:5]))
    digest = content_sha256(entries)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pack_path = out_dir / ("p3_private_%s.tar.gz" % digest[:16])
    manifest = {"schema": PACK_SCHEMA, "content_sha256": digest, "files": entries,
                "missing_optional": missing_optional, "anchors": {
                    "release": RELEASE_DIR + "/manifest.json files[]", "row": "release row image_sha256",
                    "ledger": "migration_manifest.json"}}
    if not pack_path.is_file():
        tmp = pack_path.with_name(pack_path.name + ".tmp")
        with open(str(tmp), "wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
                with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
                    blob = json.dumps(manifest, ensure_ascii=False, indent=1).encode("utf-8")
                    tar.addfile(_tarinfo(PACK_MANIFEST, len(blob)), io.BytesIO(blob))
                    for entry in entries:
                        with open(str(_on_disk(data_root, entry["path"])), "rb") as handle:
                            tar.addfile(_tarinfo(entry["path"], entry["bytes"]), handle)
        tmp.replace(pack_path)
    return {"pack": str(pack_path), "sha256": _sha256(pack_path), "bytes": pack_path.stat().st_size,
            "content_sha256": digest, "files": len(entries), "payload_bytes": sum(e["bytes"] for e in entries),
            "missing_optional": missing_optional}


def extract_pack(pack_path, repo_root):
    """Extract into ``repo_root`` (VM side); only regular files under data/ plus the pack manifest."""
    repo_root = Path(repo_root)
    with tarfile.open(str(pack_path), mode="r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            name = member.name
            if not member.isfile() or Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError("unsafe member in data pack: %s" % name)
            if name != PACK_MANIFEST and not name.startswith("data/"):
                raise ValueError("unexpected member in data pack: %s" % name)
        for member in members:
            target = repo_root / (".colab_pack_manifest.json" if member.name == PACK_MANIFEST else member.name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source, open(str(target), "wb") as out:
                out.write(source.read())
    return json.loads((repo_root / ".colab_pack_manifest.json").read_text(encoding="utf-8"))


def verify_tree(repo_root):
    """VM-side check: the extracted data/ matches the pack manifest and the anchors in this commit."""
    repo_root = Path(repo_root)
    pack = json.loads((repo_root / ".colab_pack_manifest.json").read_text(encoding="utf-8"))
    entries, _ = plan_entries(repo_root / "data", repo_root)
    planned = {e["path"]: e for e in entries}
    packed = {e["path"]: e for e in pack["files"]}
    problems = []
    for rel in sorted(set(planned) - set(packed)):
        if planned[rel]["anchor"] != "ledger" or any(rel == r for r in REQUIRED_LEDGER):
            problems.append("required file not in pack: " + rel)
    for rel, entry in sorted(packed.items()):
        if rel in planned and planned[rel]["sha256"] != entry["sha256"]:
            problems.append("pack disagrees with anchors: " + rel)
    problems += verify_entries([dict(e) for e in pack["files"]], repo_root / "data")
    return {"schema": "p3-pack-verification-v1", "content_sha256": pack["content_sha256"],
            "recomputed_content_sha256": content_sha256(pack["files"]), "files": len(pack["files"]),
            "anchors": sorted({e["anchor"] for e in pack["files"]}), "missing_optional": pack.get("missing_optional", []),
            "problems": problems, "ok": not problems and content_sha256(pack["files"]) == pack["content_sha256"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-root", default=str(ROOT / "data"), help="directory that holds the project data/ payload")
    parser.add_argument("--out", default=str(ROOT / ".colab_cache"))
    parser.add_argument("--check-only", action="store_true", help="verify the local data without writing a pack")
    args = parser.parse_args(argv)
    if args.check_only:
        entries, missing = plan_entries(args.data_root)
        problems = verify_entries(entries, args.data_root)
        result = {"files": len(entries), "payload_bytes": sum(e["bytes"] or 0 for e in entries),
                  "problems": problems, "missing_optional": missing, "ok": not problems}
    else:
        result = build_pack(args.data_root, args.out)
        result["ok"] = True
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
