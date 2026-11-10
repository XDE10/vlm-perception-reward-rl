"""Download the pinned public files a task needs and check them against migration_manifest.json (VM step).

    python -m scripts.colab.public_sources --dest /content/p3/public --out <out>/public_sources.json

The Geometry3K wrapper parquets (train, validation, test) come from ``hiyouga/geometry3k`` at the revision that
``scripts/data/prepare_project3_sources.py`` pinned; their sizes and SHA256 come from the ledger in this commit, so
nothing about a download is trusted. Copies that already match are reused (a prepared VM keeps ``/content/p3``).
The InterGPS annotations are not downloaded: the data pack carries ``data/project3_audit/intergps_annotations.jsonl``,
built from the pinned InterGPS archives, and the ``eval_sets`` step checks it reproduces the committed specification.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_NAMES = ["geometry3k/data/train-00000-of-00001.parquet", "geometry3k/data/validation-00000-of-00001.parquet",
                 "geometry3k/data/test-00000-of-00001.parquet"]


def run(dest, names, repo_root=ROOT, opener=None, tries=4):
    from src.evaluation.public_sources import fetch, ledger

    pins = ledger(repo_root)
    unknown = [n for n in names if n not in pins]
    if unknown:
        raise ValueError("not pinned in migration_manifest.json: %s" % unknown)
    files = [fetch(name, dest, pins[name], tries=tries, opener=opener) for name in names]
    return {"schema": "p3-public-sources-v1", "dest": str(dest), "ok": all(f["ok"] for f in files), "files": files,
            "bytes": sum(pins[n]["bytes"] for n in names)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--names", nargs="*", default=DEFAULT_NAMES)
    args = parser.parse_args(argv)
    report = run(Path(args.dest), args.names)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    for f in report["files"]:
        print("%s %s %s" % ("ok" if f["ok"] else "FAILED", f["name"], "reused" if f.get("reused") else f.get("errors", "")))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
