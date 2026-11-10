"""Registered runs (S4 pre-registration): the exact configuration each formal run must have.

``configs/experiments/s4_runs_20261110.json`` lists the formal runs in their pre-registered order. Its derived fields
are computed here and never typed by hand: each run's resolved ``config_sha256``, run name, output directory and step
budget; the content hash of the frozen runtime; the SHA256 of the three data files as recorded in
``migration_manifest.json``; the SHA256 of the copied S3 decision file. ``python -m scripts.training.register_runs``
writes them (``--write``) or fails when the file and the configs have drifted apart (``--check``, also a test).

At training time ``train_rl --registered`` passes ``expectation(...)`` to ``rl_entry.run``, which refuses to start when
the resolved config, the data, the row count or the GPU differ from the registration (``check``); ``train_rl`` itself
compares the runtime file. Smoke overrides and output-directory overrides are refused for registered runs, so a
formal run's ``run_identity.json`` carries exactly the registered ``config_sha256``.
"""
import copy
import hashlib
from pathlib import Path

from src.training.rl_config import canonical_sha256, read_json, registered_runs, resolve

SCHEMA = "p3-registered-runs-v1"
RUN_GROUPS = ("runs", "optional_runs")
DERIVED_RUN_KEYS = ("run_name", "output_dir", "max_steps", "config_sha256")


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def runtime_sha256(runtime):
    """Content hash of a runtime file as loaded (formatting does not matter, every key does)."""
    return canonical_sha256(runtime)


def data_paths(config):
    """Repository-relative paths of the three data files a run reads (the keys of ``run_identity.data_sha256``)."""
    data = config["data"]
    manifest = Path(data["manifest"])
    return {"manifest": manifest.as_posix(), "train_file": (manifest.parent / data["train_file"]).as_posix(),
            "intergps_annotations": Path(data["intergps_annotations"]).as_posix()}


def recorded_data_sha256(root, paths):
    """SHA256 of each data file as recorded in migration_manifest.json (data/ is not in git, its ledger is)."""
    recorded = {f["path"]: f["sha256"] for f in read_json(Path(root) / "migration_manifest.json")["files"]}
    missing = sorted(p for p in paths.values() if p not in recorded)
    if missing:
        raise ValueError("data files not recorded in migration_manifest.json: %s" % missing)
    return {key: recorded[path] for key, path in paths.items()}


def entries(registry):
    return [entry for group in RUN_GROUPS for entry in registry.get(group, [])]


def validate(registry, root="."):
    """Structure: schema, consecutive order, every registered (arm, seed) exactly once, optional arms last."""
    root = Path(root)
    if registry.get("schema") != SCHEMA:
        raise ValueError("registered-runs schema mismatch: %r" % registry.get("schema"))
    arms = read_json(root / registry["arms"]["path"])
    optional = set(arms.get("optional_arms", []))
    main = [(e["arm"], e["seed"]) for e in registry["runs"]]
    extra = [(e["arm"], e["seed"]) for e in registry.get("optional_runs", [])]
    if sorted(main) != sorted(registered_runs(root / registry["arms"]["path"])):
        raise ValueError("runs must list every registered (arm, seed) of the main arms exactly once")
    if sorted(main + extra) != sorted(registered_runs(root / registry["arms"]["path"], include_optional=True)):
        raise ValueError("optional_runs must list every registered (arm, seed) of the optional arms exactly once")
    if any(arm in optional for arm, _ in main) or any(arm not in optional for arm, _ in extra):
        raise ValueError("optional arms belong in optional_runs only")
    orders = [e["order"] for e in entries(registry)]
    if orders != list(range(1, len(orders) + 1)):
        raise ValueError("run order must be 1..%d without gaps: %s" % (len(orders), orders))
    if not registry.get("gpu_name") or int(registry.get("rows", 0)) <= 0:
        raise ValueError("gpu_name and rows are required")
    return registry


def resolve_registered(registry, arm, seed, root="."):
    """The config the training entry builds for a registered run: base + arm + seed, the registered runtime's
    micro-batch split and the registered row count (``rl_entry.run`` applies the same two steps)."""
    from src.training.rl_entry import apply_runtime, finalize_budget, load_runtime

    root = Path(root)
    config = resolve(root / registry["experiment"]["path"], arm, seed, arms_path=root / registry["arms"]["path"])
    apply_runtime(config, load_runtime(root / registry["runtime"]["path"]))
    return finalize_budget(config, int(registry["rows"]))


def derive(registry, root="."):
    """A copy of ``registry`` with every derived field recomputed from the files it names."""
    root = Path(root)
    out = copy.deepcopy(registry)
    validate(out, root)
    out["decisions"]["sha256"] = sha256_file(root / out["decisions"]["path"])
    out["runtime"].pop("sha256", None)
    out["runtime"]["content_sha256"] = runtime_sha256(read_json(root / out["runtime"]["path"]))
    paths = None
    for entry in entries(out):
        config = resolve_registered(out, entry["arm"], entry["seed"], root)
        if config["protocol"] != out["protocol"]:
            raise ValueError("experiment protocol %s differs from the registered %s" % (config["protocol"], out["protocol"]))
        paths = paths or data_paths(config)
        entry.update(run_name=config["run_name"], output_dir=config["output_dir"],
                     max_steps=config["train"]["max_steps"], config_sha256=config["config_sha256"])
    out["data_sha256"] = recorded_data_sha256(root, paths)
    return out


def load(path, root="."):
    registry = read_json(path)
    return validate(registry, root)


def find(registry, arm, seed):
    for entry in entries(registry):
        if entry["arm"] == arm and int(entry["seed"]) == int(seed):
            return entry
    raise ValueError("%s seed %s is not a registered run in %s" % (arm, seed, registry.get("name")))


def expectation(registry, arm, seed):
    """What ``rl_entry.run`` checks before it loads the model."""
    entry = find(registry, arm, seed)
    return {"registry": registry["name"], "order": entry["order"], "arm": entry["arm"], "seed": int(entry["seed"]),
            "optional": entry in registry.get("optional_runs", []), "config_sha256": entry["config_sha256"],
            "rows": int(registry["rows"]), "data_sha256": dict(registry["data_sha256"]),
            "gpu_name": registry["gpu_name"]}


def check(expected, config, data_sha256, rows, gpu_name):
    """Every way a run can differ from its registration (empty list = it matches)."""
    problems = []
    if config.get("smoke"):
        problems.append("smoke overrides %s" % sorted(config["smoke"]))
    if (config["arm"]["name"], int(config["seed"])) != (expected["arm"], expected["seed"]):
        problems.append("run %s/seed%s is registered as %s/seed%s" % (config["arm"]["name"], config["seed"],
                                                                     expected["arm"], expected["seed"]))
    if config["config_sha256"] != expected["config_sha256"]:
        problems.append("config_sha256 %s != registered %s" % (config["config_sha256"], expected["config_sha256"]))
    if int(rows) != expected["rows"]:
        problems.append("%s training rows, registered %s" % (rows, expected["rows"]))
    if dict(data_sha256) != expected["data_sha256"]:
        changed = sorted(k for k in expected["data_sha256"] if data_sha256.get(k) != expected["data_sha256"][k])
        problems.append("data files differ from the registration: %s" % changed)
    if gpu_name != expected["gpu_name"]:
        problems.append("GPU %r, registered %r" % (gpu_name, expected["gpu_name"]))
    return problems


__all__ = ["SCHEMA", "check", "data_paths", "derive", "entries", "expectation", "find", "load", "recorded_data_sha256",
           "resolve_registered", "runtime_sha256", "sha256_file", "validate"]
