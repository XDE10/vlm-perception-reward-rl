"""Run S5 from registered S4 finals and V0 under the frozen P1 protocol."""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path

from scripts.colab import s4_state
from scripts.colab.common import log, read_json, sha256_file, write_json
from scripts.colab.s5_inputs import ROOT
from scripts.colab.tasks import S4_REGISTRY
from scripts.colab.train_s4 import entries, run_key
from src.evaluation.harness import BATCH_SIZE, MAX_NEW_TOKENS

SCHEMA = "p3-s5-predictions-v1"


def inventory(store, registry):
    """Keep only matching terminal runs. A stale or foreign marker cannot unlock evaluation."""
    runs = []
    experiment = read_json(ROOT / registry["experiment"]["path"])["name"]
    required, optional = entries(registry)
    for entry in required + optional:
        rel = s4_state.run_rel(registry, experiment, entry["arm"], entry["seed"])
        status = s4_state.run_status(store, rel, run_key(registry, entry))
        state, marker = status["state"], status.get("marker", {})
        if state == "completed":
            if (marker.get("schema"), marker.get("run"), marker.get("global_step")) != (
                "p3-run-completed-v1", entry["run_name"], entry["max_steps"]
            ) or not {"final/adapter_config.json", "final/adapter_model.safetensors"} <= set(marker.get("files", {})):
                raise ValueError(f"invalid final marker for {entry['run_name']}")
        if state == "failed" and (marker.get("schema"), marker.get("run")) != (
            "p3-run-failed-v1", entry["run_name"]
        ):
            raise ValueError(f"invalid failure marker for {entry['run_name']}")
        runs.append({**entry, "rel": rel, "state": state, "checkpoints": status["checkpoints"], "marker": marker})
    return runs


def restore_adapter(store, run, dest):
    expected = {path.removeprefix("final/"): info for path, info in run["marker"]["files"].items()
                if path.startswith("final/")}
    if s4_state.file_table(dest) != expected:
        got = store.fetch_verify(run["rel"] + "/final", dest)
        if not got.get("ok") or s4_state.file_table(dest) != expected:
            raise ValueError(f"Drive final failed verification for {run['run_name']}")
    return dest


def prediction_key(model, dataset, items, context):
    return {"schema": SCHEMA, "model": model["run_name"], "dataset": dataset, **context,
            "final": {p: v for p, v in model["marker"]["files"].items() if p.startswith("final/")},
            "items": [item["id"] for item in items]}


def checked_rows(directory, marker, key):
    path = directory / "predictions.jsonl"
    if marker["key"] != key or not path.is_file() or sha256_file(path) != marker["sha256"]:
        raise ValueError(f"prediction identity or digest differs at {directory}")
    with path.open(encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream]
    if [row["item"] for row in rows] != key["items"]:
        raise ValueError(f"prediction item order differs at {directory}")
    return rows


def evaluate_model(model_spec, cases, subsets, swap, geometry, args, store, config, context):
    import torch

    from scripts.colab.s5_inputs import MathVistaVerifier, intergps_false
    from src.evaluation.harness import load_model, run_condition, write_jsonl
    from src.rewards.answer import AnswerVerifier
    from src.rewards.perception_v5 import V5Config

    name = model_spec["run_name"]
    verifier = AnswerVerifier(config["rewards"]["verifier_workers"], config["rewards"]["verifier_timeout"])
    v5 = V5Config.from_dict(config["perception_v5"])
    model = processor = None
    results, manifests = {}, {}
    try:
        for dataset, (items, condition) in cases.items():
            key = prediction_key(model_spec, dataset, items, context)
            digest = hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()
            rel = f"s5/predictions/{name}/{dataset}/{digest}"
            directory = args.cache / rel
            marker, status = store.get_json(rel + "/VERIFIED.json")
            if status == "ok":
                local = directory / "predictions.jsonl"
                if not local.is_file() or sha256_file(local) != marker["sha256"]:
                    fetched = store.fetch_verify(rel, directory)
                    if not fetched.get("ok"):
                        raise RuntimeError(f"could not restore {name} {dataset}")
                rows = checked_rows(directory, marker, key)
                log(f"S5 {name} {dataset}: reused {len(rows)} verified predictions")
            elif status == "missing":
                if model is None:
                    adapter = None if model_spec["arm"] == "V0" else restore_adapter(
                        store, model_spec, args.cache / "adapters" / model_spec["config_sha256"])
                    model, processor = load_model(args.model_path, config, adapter=adapter)
                judge = MathVistaVerifier(verifier) if dataset == "mathvista" else verifier
                rows = run_condition(model, processor, items, condition, judge, v5,
                                     prompt_variant="p1", swap=swap, model_name=name,
                                     progress=lambda n, total: log(f"S5 {name} {dataset}: {n}/{total}"))
                if dataset == "test_original":
                    for row in rows:
                        row["intergps"] = intergps_false(row["text"], geometry.get(row["item"]), v5)
                output = directory / "predictions.jsonl"
                write_jsonl(output, rows)
                marker = {"key": key, "sha256": sha256_file(output), "n": len(rows)}
                checked_rows(directory, marker, key)
                copied = store.copy_verify(directory, rel)
                if not copied.get("ok") or not store.put_json(rel + "/VERIFIED.json", marker).get("ok"):
                    raise RuntimeError(f"could not persist {name} {dataset}")
            else:
                raise RuntimeError(f"could not read the verification marker for {name} {dataset}: {status}")
            results[dataset] = rows
            manifests[dataset] = {"drive_relative": rel, "sha256": marker["sha256"], "n": len(rows)}
    finally:
        verifier.close()
        if model is not None:
            del model, processor
            gc.collect()
            torch.cuda.empty_cache()
    for dataset, (source, ids) in subsets.items():
        results[dataset] = [row for row in results[source] if row["item"] in ids]
        if len(results[dataset]) != len(ids):
            raise ValueError(f"S5 subset membership differs for {dataset}")
    return results, manifests


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path")
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--drive-remote")
    parser.add_argument("--drive-dir")
    parser.add_argument("--drive-mount")
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args(argv)
    registry = read_json(ROOT / S4_REGISTRY)
    store, info = s4_state.Store.open(args.cache / "scratch", args.drive_remote, args.drive_dir, args.drive_mount)
    if store is None:
        raise RuntimeError(f"S5 needs the S4 Drive store: {info.get('reason')}")
    runs = inventory(store, registry)
    write_json(args.out / "s4_inventory.json", runs)
    pending = [run["run_name"] for run in runs if not run.get("optional") and run["state"] not in {"completed", "failed"}]
    if pending:
        log("S4 has pending registered runs: " + ", ".join(pending))
        return 0 if args.inventory_only else 1
    if args.inventory_only:
        return 0
    if not args.model_path or not os.environ.get("P3_GIT_COMMIT") or os.environ["P3_GIT_COMMIT"].endswith("-dirty"):
        parser.error("formal S5 needs the pinned model and a clean launcher snapshot")

    import torch

    from scripts.colab.s5_analysis import analyze, markdown
    from scripts.colab.s5_inputs import build
    from src.training.rl_entry import package_versions

    config = read_json(ROOT / registry["experiment"]["path"])
    context = {"commit": os.environ["P3_GIT_COMMIT"], "model_revision": config["model"]["revision"],
               "gpu": torch.cuda.get_device_name(), "packages": package_versions(),
               "prompt": "p1", "decode": "hf-greedy", "max_new_tokens": MAX_NEW_TOKENS, "batch_size": BATCH_SIZE}
    cases, subsets, swap, geometry = build(args.sources, config, args.out)
    v0 = {"run_name": "V0", "arm": "V0", "seed": 0, "marker": {"files": {}}}
    models, evidence = {}, {}
    for spec in [v0] + [run for run in runs if run["state"] == "completed"]:
        result, provenance = evaluate_model(spec, cases, subsets, swap, geometry, args, store, config, context)
        models.setdefault(spec["arm"], {})[spec["seed"]] = result
        evidence[spec["run_name"]] = provenance
        write_json(args.out / "predictions.json", evidence)
    report = analyze(models)
    report.update(context=context, evidence="predictions.json", s4_inventory="s4_inventory.json")
    write_json(args.out / "summary.json", report)
    (args.out / "README.md").write_text(markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
