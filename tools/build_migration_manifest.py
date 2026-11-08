"""Rebuild migration_manifest.json as an inventory of the current tree.

The manifest is the offline integrity ledger for the payload that travelled
with the 2026-10-24 migration (code, docs, reports and data).  The sealed
historical versions are kept in docs/migration/; this tool refreshes the
working copy after a legitimate repository restructuring:

    python tools/build_migration_manifest.py

For every current file it records path, bytes and sha256.  Provenance is
carried over from the previous manifest when possible:

* unchanged file at the same path  -> source_sha256 kept, unchanged flag kept
* edited file at the same path     -> source_sha256 = previous sha256,
                                      changed_for_portability = true
* file moved to a new path         -> moved_from = previous path
* genuinely new file               -> source_sha256 = sha256, added_in marked

Files that disappeared from the tree are not silently dropped: their count and
the sealed manifest that still records them are noted in
documentation_updates.  The tool only rewrites the root manifest; run
`python tools/verify_migration.py --full` afterwards.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "migration_manifest.json"
SEALED_MANIFESTS = [
    "docs/migration/migration_manifest_分离同步前_20261108.json",
    "docs/migration/migration_manifest_交接补充前_20261024.json",
]
SKIP_DIR_NAMES = {
    ".git",
    ".pytest_cache",
    ".venv",
    ".pilot_deps",
    "__pycache__",
    "backups",
    "runs",
}
SKIP_DIR_PATHS = {"reports/backups"}
CHUNK = 4 * 1024 * 1024


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def iter_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = Path(dirpath).relative_to(ROOT)
        kept = []
        for name in sorted(dirnames):
            rel_child = (rel / name).as_posix() if rel != Path(".") else name
            if name in SKIP_DIR_NAMES or rel_child in SKIP_DIR_PATHS:
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path == MANIFEST or name.endswith(".pyc"):
                continue
            yield path


def build(previous_path, manifest_date):
    current = []
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        current.append(
            {"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path)}
        )
    current_paths = {entry["path"] for entry in current}

    previous = []
    if previous_path.is_file():
        previous = json.loads(previous_path.read_text(encoding="utf8")).get(
            "files", []
        )
    previous_by_path = {entry["path"]: entry for entry in previous}
    missing_by_sha = {}
    for entry in previous:
        if entry["path"] not in current_paths:
            missing_by_sha.setdefault(entry["sha256"], []).append(entry)
    for bucket in missing_by_sha.values():
        bucket.sort(key=lambda entry: entry["path"])
    # Flat scripts/<name>.py entries moved into scripts/<group>/<name>.py keep
    # their bytes mostly unchanged except for ROOT/import rewrites; a unique
    # basename is enough to carry the provenance when the sha changed too.
    missing_scripts_by_name = {}
    for entry in previous:
        if entry["path"] in current_paths:
            continue
        if entry["path"].startswith("scripts/") and entry["path"].count("/") == 1:
            missing_scripts_by_name.setdefault(
                entry["path"].rsplit("/", 1)[1], []
            ).append(entry)

    files = []
    changes = []
    moves = {}
    for entry in current:
        old = previous_by_path.get(entry["path"])
        if old is not None:
            if old["sha256"] == entry["sha256"]:
                source_sha256 = old.get("source_sha256", old["sha256"])
                changed = old.get("changed_for_portability", False)
            else:
                source_sha256 = old.get("source_sha256", old["sha256"])
                changed = True
                entry["updated_in"] = "2026-11-08_restructure"
                changes.append(
                    {
                        "path": entry["path"],
                        "previous_sha256": old["sha256"],
                        "current_sha256": entry["sha256"],
                    }
                )
        else:
            moved = None
            for candidate in missing_by_sha.get(entry["sha256"], []):
                if candidate["path"] not in moves.values():
                    moved = candidate
                    break
            if moved is None and entry["path"].startswith("scripts/"):
                bucket = [
                    candidate
                    for candidate in missing_scripts_by_name.get(
                        entry["path"].rsplit("/", 1)[1], []
                    )
                    if candidate["path"] not in moves.values()
                ]
                if len(bucket) == 1:
                    moved = bucket[0]
            if moved is not None:
                source_sha256 = moved.get("source_sha256", moved["sha256"])
                changed = moved.get("changed_for_portability", False)
                if moved["sha256"] != entry["sha256"]:
                    changed = True
                    entry["updated_in"] = "2026-11-08_restructure"
                    changes.append(
                        {
                            "path": entry["path"],
                            "previous_sha256": moved["sha256"],
                            "current_sha256": entry["sha256"],
                            "moved_from": moved["path"],
                        }
                    )
                entry["moved_from"] = moved["path"]
                moves[entry["path"]] = moved["path"]
            else:
                source_sha256 = entry["sha256"]
                changed = False
                entry["added_in"] = "2026-11-08_restructure"
                changes.append(
                    {
                        "path": entry["path"],
                        "previous_sha256": None,
                        "current_sha256": entry["sha256"],
                    }
                )
        entry["source_sha256"] = source_sha256
        entry["changed_for_portability"] = changed
        files.append(entry)

    old_missing = [entry for entry in previous if entry["path"] not in current_paths]
    not_carried = [
        entry for entry in old_missing if entry["path"] not in moves.values()
    ]
    documentation_updates = []
    if previous_path.is_file():
        documentation_updates = json.loads(
            previous_path.read_text(encoding="utf8")
        ).get("documentation_updates", [])
    documentation_updates = [
        update for update in documentation_updates if update.get("date") != manifest_date
    ]
    documentation_updates.append(
        {
            "date": manifest_date,
            "purpose": "Repository restructuring (docs/, requirements/, scripts/ role packages) and manifest rebuild as a current-tree inventory",
            "changes": changes,
            "moves": dict(sorted(moves.items())),
            "not_carried_over": {
                "count": len(not_carried),
                "note": "These paths were deleted in the 2026-11-08 cleanup or superseded by the new layout; they remain recorded in the sealed manifests.",
                "sealed_manifests": SEALED_MANIFESTS,
                "cleanup_records": [
                    "docs/migration/清理记录_20261108.md",
                    "docs/migration/清理记录_20261108_分离.json",
                    "docs/migration/迁移验收.md",
                ],
            },
            "note": "Manifest semantics updated: files[] is now the current tree. source_sha256 is the sha256 recorded for the nearest historical version (same path or moved_from path). changed_for_portability=true means the current bytes differ from that source version. See docs/migration/整理记录_20261108.md.",
        }
    )

    manifest = {
        "project": "项目三_多模态几何推理",
        "date": manifest_date,
        "schema_version": 2,
        "source_root": "D:\\Users\\Mr.Z\\Desktop\\modern_genai",
        "files": sorted(files, key=lambda entry: entry["path"]),
        "omitted": [
            ".git",
            "virtual environments",
            "__pycache__",
            ".pytest_cache",
            "reports/backups",
            "runs/",
            "backups/",
            ".pilot_deps/",
            "unrelated raw source shards",
        ],
        "gpu_runs_during_migration": 0,
        "documentation_updates": documentation_updates,
    }
    return manifest, {
        "files": len(files),
        "new": sum(1 for entry in files if "added_in" in entry),
        "moved": len(moves),
        "updated": len(changes) - sum(1 for entry in files if "added_in" in entry),
        "unchanged": sum(
            1
            for entry in files
            if "added_in" not in entry
            and "moved_from" not in entry
            and "updated_in" not in entry
        ),
        "previous_files": len(previous),
        "not_carried_over": len(not_carried),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--previous",
        type=Path,
        default=MANIFEST,
        help="previous manifest used for provenance matching (default: root manifest)",
    )
    parser.add_argument(
        "--date",
        default="2026-11-08",
        help="manifest date recorded in the ledger",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print summary without writing"
    )
    args = parser.parse_args()

    manifest, stats = build(args.previous, args.date)
    if not args.dry_run:
        MANIFEST.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
            encoding="utf8",
        )
        stats["manifest_sha256"] = sha256(MANIFEST)
        stats["manifest_bytes"] = MANIFEST.stat().st_size
    stats["dry_run"] = args.dry_run
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
