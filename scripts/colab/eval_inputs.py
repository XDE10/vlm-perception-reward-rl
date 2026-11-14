"""Rebuild the evaluation inputs on the VM and compare them with the committed specifications (no model runs).

    python -m scripts.colab.eval_inputs eval-sets --sources <public> --out <out>/eval_sets_check.json
    python -m scripts.colab.eval_inputs cfgeo --sources <public> --out <out>/cfgeo_build.json

``eval-sets`` applies the pre-registered rules (src/evaluation/eval_sets.py) to the pinned wrapper parquets and the
packed InterGPS annotations and requires the result to equal reports/eval_sets_20261109/eval_sets.json (the
``built_from`` provenance field aside). It also reports how many evaluation images the training resolution would
shrink or enlarge (S3 design section 6, resolution row). ``cfgeo`` rebuilds every CF-Geo image of the evaluation and
development files from the pinned images and the committed patches and checks every pixel SHA256.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "reports/eval_sets_20261109/eval_sets.json"
CFGEO = [ROOT / "reports/cfgeo_20261109/cfgeo.json", ROOT / "reports/cfgeo_20261109/cfgeo_dev_train.json"]
ANNOTATIONS = ROOT / "data/project3_audit/intergps_annotations.jsonl"


def _shown(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if ROOT in path.parents else str(path)


def differences(a, b, prefix=""):
    """Paths where two JSON values differ (at most 20)."""
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(prefix + str(key) + (" (missing here)" if key not in a else " (missing in the committed file)"))
            else:
                out += differences(a[key], b[key], prefix + str(key) + ".")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            out += differences(x, y, "%s%d." % (prefix, i))
    elif a != b:
        out.append(prefix.rstrip(".") or "(root)")
    return out[:20]


def resolution(sources, config):
    """Evaluation images whose patch grid the experiment's pixel limits change (exactly as the processor resizes:
    rounding to multiples of 28 can push an image just under max_pixels over it)."""
    from src.evaluation.public_sources import read_wrapper
    from src.training.vllm_guard import grid_mismatches

    low, high = config["model"]["min_pixels"], config["model"]["max_pixels"]
    out = {"max_pixels": high, "min_pixels": low}
    for split in ("validation", "test"):
        rows = read_wrapper(Path(sources) / ("geometry3k/data/%s-00000-of-00001.parquet" % split), with_images=True)
        sizes = [row["image"].size for row in rows]
        shrunk = {tuple(m["size"]) for m in grid_mismatches(sizes, (low, high), (low, 10 ** 12))}
        enlarged = {tuple(m["size"]) for m in grid_mismatches(sizes, (low, high), (28 * 28, high))}
        areas = [w * h for w, h in sizes]
        out[split] = {"images": len(sizes), "shrunk": sum(s in shrunk for s in sizes),
                      "enlarged": sum(s in enlarged for s in sizes), "max_pixels_seen": max(areas),
                      "min_pixels_seen": min(areas)}
    return out


def eval_sets(sources, out, annotations=ANNOTATIONS, committed=SPEC):
    from scripts.data.build_eval_sets import build

    config = json.loads((ROOT / "configs/experiments/rl_v3.json").read_text(encoding="utf-8"))
    rebuilt = build(sources, annotations=str(annotations))
    reference = json.loads(Path(committed).read_text(encoding="utf-8"))
    reference.pop("built_from", None)
    rebuilt.pop("built_from", None)
    diff = differences(rebuilt, reference)
    report = {"schema": "p3-eval-sets-check-v1", "ok": not diff, "differences": diff, "counts": rebuilt["counts"],
              "committed": _shown(committed), "annotations": _shown(annotations), "resolution": resolution(sources, config)}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def cfgeo(sources, out, files=CFGEO):
    from src.evaluation.cfgeo import rebuild
    from src.evaluation.public_sources import read_wrapper

    images, report = {}, {"schema": "p3-cfgeo-build-v1", "files": {}}
    for path in files:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
        rebuilt, failures = 0, []
        for item in spec["items"]:
            split, number = item["id"].split(":")
            if split not in images:
                images[split] = [r["image"] for r in read_wrapper(
                    Path(sources) / ("geometry3k/data/%s-00000-of-00001.parquet" % split), with_images=True)]
            try:
                for variant in ("k1", "k2"):
                    rebuild(item, images[split][int(number)], variant)
                rebuilt += 1
            except ValueError as exc:
                failures.append({"id": item["id"], "error": str(exc)})
        report["files"][Path(path).name] = {"items": len(spec["items"]), "rebuilt": rebuilt, "failures": failures[:20],
                                            "edit_version": spec.get("edit_version")}
    report["ok"] = all(not f["failures"] and f["rebuilt"] == f["items"] for f in report["files"].values())
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["eval-sets", "cfgeo"])
    parser.add_argument("--sources", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    report = eval_sets(args.sources, args.out) if args.command == "eval-sets" else cfgeo(args.sources, args.out)
    print(json.dumps({k: v for k, v in report.items() if k in ("ok", "differences", "counts", "files")}, ensure_ascii=False)[:3000])
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
