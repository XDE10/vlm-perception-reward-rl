"""Refresh the integrity ledger for Git files and carry over frozen data hashes."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "migration_manifest.json"
CHUNK = 4 * 1024 * 1024


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_lines(root, args, stdin=None):
    result = subprocess.run(
        ["git", *args], cwd=root, input=stdin, capture_output=True, check=False
    )
    if result.returncode not in (0, 1):  # check-ignore exits 1 when nothing is ignored
        raise RuntimeError(result.stderr.decode("utf8", "replace"))
    return [p for p in result.stdout.decode("utf8").split("\0") if p]


def git_files(root=ROOT):
    """Tracked plus untracked-but-not-ignored files (new files count before staging)."""
    paths = _git_lines(root, ["ls-files", "-co", "--exclude-standard", "-z"])
    keep = []
    for rel in sorted(set(paths)):
        path = root / rel
        name = path.name
        if (
            not path.is_file()
            or rel == "migration_manifest.json"
            or name.endswith(".pyc")
            or name == "uv.lock"
            or name in {".DS_Store", "Thumbs.db", "desktop.ini"}
            or ":Zone.Identifier" in name
        ):
            continue
        keep.append(rel)
    return keep


def git_ignored(root, paths):
    if not paths:
        return set()
    stdin = "\0".join(paths).encode("utf8") + b"\0"
    return set(_git_lines(root, ["check-ignore", "--stdin", "-z", "--no-index"], stdin))


def build_git_tracked(previous_path, manifest_date, label, purpose, root=ROOT):
    """Refresh entries for git-visible files only; keep git-ignored entries (data/) verbatim.

    Used where the untracked payload is absent (for example a fresh clone or a
    CI sandbox): a full rebuild there would drop every data/ entry from the
    ledger. Previously recorded paths that are neither visible to git nor
    ignored are treated as deleted tracked files and reported.
    """
    previous = json.loads(Path(previous_path).read_text(encoding="utf8"))
    previous_by_path = {entry["path"]: entry for entry in previous.get("files", [])}
    tracked = git_files(root)
    tracked_set = set(tracked)
    files, changes = [], []
    for rel in tracked:
        path = root / rel
        current = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        old = previous_by_path.get(rel)
        if old is not None and old["sha256"] == current["sha256"] and old["bytes"] == current["bytes"]:
            files.append(dict(old))
            continue
        if old is not None:
            entry = dict(old)
            entry.update(current)
            entry["source_sha256"] = old.get("source_sha256", old["sha256"])
            entry["changed_for_portability"] = True
            entry["updated_in"] = label
            changes.append({"path": rel, "previous_sha256": old["sha256"], "current_sha256": current["sha256"]})
        else:
            entry = {"path": rel, **current, "source_sha256": current["sha256"], "changed_for_portability": False,
                     "added_in": label}
            changes.append({"path": rel, "previous_sha256": None, "current_sha256": current["sha256"]})
        files.append(entry)
    others = set(previous_by_path) - tracked_set
    kept = sorted(p for p in git_ignored(root, sorted(others)) if p.startswith("data/"))
    dropped = sorted(others - set(kept))
    files.extend(dict(previous_by_path[path]) for path in kept)
    updates = list(previous.get("documentation_updates", []))
    same = [u for u in updates if u.get("date") == manifest_date and u.get("label") == label
            and u.get("mode") == "git_tracked_only"]
    if same:
        # Repeated refreshes within one stage accumulate into a single ledger entry.
        merged = {c["path"]: c for c in same[-1].get("changes", [])}
        for change in changes:
            earlier = merged.get(change["path"])
            merged[change["path"]] = {**change, "previous_sha256": earlier["previous_sha256"]} if earlier else change
        changes = [merged[p] for p in sorted(merged)]
        dropped = sorted(set(dropped) | set(same[-1].get("dropped_tracked_paths", [])))
    # replace only this stage's own entry; other stages' entries on the same date are history and must stay
    updates = [u for u in updates if not (u.get("date") == manifest_date and u.get("label") == label
                                          and u.get("mode") == "git_tracked_only")]
    updates.append({
        "date": manifest_date,
        "label": label,
        "mode": "git_tracked_only",
        "purpose": purpose,
        "changes": changes,
        "dropped_tracked_paths": dropped,
        "untracked_entries_kept_verbatim": len(kept),
        "note": "Only git-visible files were re-hashed; git-ignored payload entries (data/) were carried over unchanged. The payload is immutable and verified separately.",
    })
    manifest = dict(previous)
    manifest["date"] = manifest_date
    manifest["files"] = sorted(files, key=lambda entry: entry["path"])
    manifest["documentation_updates"] = updates
    stats = {"files": len(files), "git_visible": len(tracked), "changed": sum(c["previous_sha256"] is not None for c in changes),
             "added": sum(c["previous_sha256"] is None for c in changes), "kept_untracked": len(kept), "dropped": len(dropped)}
    return manifest, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, default=MANIFEST)
    parser.add_argument("--date", required=True, help="ledger date (YYYY-MM-DD)")
    parser.add_argument("--label", help="stage name for the ledger")
    parser.add_argument("--purpose", default="", help="why the tracked tree changed")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--git-tracked-only", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    manifest, stats = build_git_tracked(args.previous, args.date, args.label or args.date, args.purpose)
    if not args.dry_run:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
