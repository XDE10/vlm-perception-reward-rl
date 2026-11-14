"""Build the pre-registered evaluation-set specification from pinned public sources (no model is involved).

    python -m scripts.data.build_eval_sets --sources data/project3_sources --out reports/eval_sets_20261109/eval_sets.json

Rules: docs/plan/S3设计_20261109.md sections 1-3 (src/evaluation/eval_sets.py). Every source file is checked
against migration_manifest.json before it is read. InterGPS records are rebuilt from the pinned zips with
src/data/project3_audit.original_records, which is how data/project3_audit/intergps_annotations.jsonl was made;
``--annotations`` reads that file instead (the Colab VM does this, see scripts/colab/eval_sets_check.py).
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEEDED = ["geometry3k/data/validation-00000-of-00001.parquet", "geometry3k/data/test-00000-of-00001.parquet"]
ZIPS = ["intergps/data/geometry3k/%s.zip" % x for x in ("train", "val", "test", "logic_forms")]


def load_records(sources, annotations=None):
    if annotations:
        return [json.loads(x) for x in Path(annotations).read_text(encoding="utf-8").splitlines() if x.strip()]
    from src.data.project3_audit import original_records

    return original_records(Path(sources))


def build(sources, annotations=None, repo_root=ROOT):
    from src.evaluation.eval_sets import build_eval_sets
    from src.evaluation.public_sources import check_file, ledger, read_wrapper

    pins = ledger(repo_root)
    names = NEEDED + ([] if annotations else ZIPS)
    problems = {n: check_file(Path(sources) / n, pins[n]) for n in names}
    problems = {n: p for n, p in problems.items() if p}
    if problems:
        raise SystemExit("pinned sources do not match migration_manifest.json: %s" % problems)
    wrapper = {split: read_wrapper(Path(sources) / ("geometry3k/data/%s-00000-of-00001.parquet" % split))
               for split in ("validation", "test")}
    records = load_records(sources, annotations)
    return build_eval_sets(wrapper, records, sources={n: pins[n]["sha256"] for n in NEEDED})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", default=str(ROOT / "data/project3_sources"))
    parser.add_argument("--annotations", default=None)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    spec = build(args.sources, args.annotations)
    # provenance only; the VM compares everything except this field (it reads the packed annotations instead)
    spec["built_from"] = ("InterGPS records from %s" % args.annotations if args.annotations else
                          "InterGPS records rebuilt from the pinned zips: " + ", ".join(ZIPS))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(spec["counts"], ensure_ascii=False))
    print(json.dumps(spec["excluded"], ensure_ascii=False))


if __name__ == "__main__":
    main()
