"""Fill in or check the derived fields of a registered-runs file (S4 pre-registration).

    python -m scripts.training.register_runs --check            # exit 1 when the file and the configs disagree
    python -m scripts.training.register_runs --write            # recompute config hashes, runtime/data/decision hashes
    python -m scripts.training.register_runs --show rl_v5 1     # the full resolved config of one registered run

The hand-written fields (order, arms, seeds, GPU, Drive layout, pilot gates, stop rules) are kept; every hash and the
per-run name, output directory and step budget are recomputed by ``src.training.registry.derive``. With ``data/``
present, ``--check`` also compares the data files with the SHA256 recorded in ``migration_manifest.json`` and counts
the approved training rows.
"""
import argparse
import json
import sys
from pathlib import Path

from src.training import registry

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "configs/experiments/s4_runs_20261110.json"


def local_data_problems(ledger, root):
    """Differences between the local data/ (when present) and the registration."""
    from src.data.approved_training_inputs import load_approved
    from src.training.rl_config import read_json

    config = read_json(root / ledger["experiment"]["path"])
    paths = registry.data_paths(config)
    if not all((root / p).is_file() for p in paths.values()):
        return None
    problems = [key for key, path in paths.items() if registry.sha256_file(root / path) != ledger["data_sha256"][key]]
    rows = len(load_approved(root / config["data"]["manifest"], config["data"]["train_file"]))
    if rows != int(ledger["rows"]):
        problems.append("rows %d != registered %s" % (rows, ledger["rows"]))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", default=str(DEFAULT))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--show", nargs=2, metavar=("ARM", "SEED"), help="print the resolved config of a registered run")
    args = parser.parse_args(argv)
    path = Path(args.file)
    current = json.loads(path.read_text(encoding="utf-8"))
    if args.show:
        arm, seed = args.show[0], int(args.show[1])
        entry = registry.find(registry.validate(current, ROOT), arm, seed)
        config = registry.resolve_registered(current, arm, seed, ROOT)
        if config["config_sha256"] != entry.get("config_sha256"):
            print("warning: the registered config_sha256 is stale; run --write", file=sys.stderr)
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return 0
    derived = registry.derive(current, ROOT)
    if args.write:
        path.write_text(json.dumps(derived, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"written": str(path), "runs": len(registry.entries(derived))}))
        return 0
    drift = derived != current
    data = local_data_problems(derived, ROOT)
    print(json.dumps({"file": str(path), "derived_fields_match": not drift, "local_data_checked": data is not None,
                      "local_data_problems": data or []}, ensure_ascii=False))
    return 1 if drift or data else 0


if __name__ == "__main__":
    sys.exit(main())
