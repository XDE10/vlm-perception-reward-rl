"""Check the current source ledger and, optionally, the frozen runtime data pack."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.colab.pack_private_data import plan_entries, verify_entries
from tools.build_migration_manifest import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="check SHA256 in addition to file sizes")
    parser.add_argument("--data-root", type=Path, help="also verify the supplied runtime data/ directory")
    args = parser.parse_args()
    ledger = json.loads((ROOT / "migration_manifest.json").read_text(encoding="utf-8"))
    code = [item for item in ledger["files"]
            if item["path"] == "data/README.md" or not item["path"].startswith("data/")]
    errors = []
    for entry in code:
        rel = entry["path"]
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing: {rel}")
        elif path.stat().st_size != entry["bytes"]:
            errors.append(f"size changed: {rel}")
        elif args.full and sha256(path) != entry["sha256"]:
            errors.append(f"hash changed: {rel}")
    data_files = None
    if args.data_root is not None:
        try:
            entries, _ = plan_entries(args.data_root, ROOT)
            errors.extend(verify_entries(entries, args.data_root))
            data_files = len(entries)
        except (OSError, ValueError, KeyError) as exc:
            errors.append(f"data pack: {exc}")
    print(json.dumps({"repository_files": len(code), "data_files_checked": data_files,
                      "full_hash_check": args.full, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
