"""Apply the pre-registered pilot gates G1-G6 to a ``pilot`` run (standard library only, VM side).

    python -m scripts.colab.decide_pilot --out-dir <run dir> --repo <repo> --job <run id> [--python <training python>]
        [--drive-remote ... --drive-dir ... --drive-mount ...] [--allow-missing]

Rules: docs/plan/S4预注册_20261110.md section 11, numbers from the registry's ``pilot.gates``. Writes
``pilot_gates.json`` in the run directory and, unless --allow-missing (dry runs), ``PILOT_LATEST.json`` on Drive
whether the gates passed or not: ``train`` starts formal runs only when the latest pilot passed with the same
registry, runtime, training code and package versions (S4 pre-registration section 9, code freeze).
The exit code is 0 when the decision was written (pass or fail); the gates' verdict is a summary check.
"""
import argparse
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path

from scripts.colab import s4_state
from scripts.colab.common import log, read_json, sha256_file, write_json

SCHEMA = "p3-pilot-gates-v1"
FORMAL = ["pilot_v5", "pilot_rl_ans", "pilot_rl_v4", "pilot_rl_v5_placebo", "pilot_rl_blind"]
ARM_NAMES = {"rl_ans": "pilot_rl_ans", "rl_v4": "pilot_rl_v4", "rl_v5_placebo": "pilot_rl_v5_placebo",
             "rl_blind": "pilot_rl_blind"}
RETRY = "pilot_v5_retry"
RESUME = "pilot_resume"
G3_RUN_CHECKS = ("completed", "finite_loss_and_grad_norm", "verifier_ok", "image_grid_ok", "alignment_checked")
IDENTITY_SNIPPET = ("import json; from src.training.rl_entry import ROOT, SOURCE_FILES, package_versions, sha256_file; "
                    "print(json.dumps({'source_sha256': {p: sha256_file(ROOT / p) for p in SOURCE_FILES "
                    "if (ROOT / p).is_file()}, 'versions': package_versions()}))")


def _load(path):
    path = Path(path)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def rollouts(path):
    path = Path(path)
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_view(directory):
    """Everything the gates read from one pilot run directory (missing files are None / empty)."""
    directory = Path(directory)
    history = _load(directory / "log_history.json") or []
    steps = [h for h in history if isinstance(h, dict) and "step" in h and "loss" in h]
    return {"dir": str(directory), "present": directory.is_dir(), "supervisor": _load(directory / "supervisor.json"),
            "summary": _load(directory / "train_summary.json"), "identity": _load(directory / "run_identity.json"),
            "steps": steps, "rollouts": rollouts(directory / "rollouts.jsonl")}


def window_mean(steps, first, last, key="p3/format_rate"):
    values = [h[key] for h in steps if first <= int(h["step"]) <= last and isinstance(h.get(key), (int, float))]
    return (sum(values) / len(values), len(values)) if values else (None, 0)


def finite(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def completed(view):
    sup, summary = view["supervisor"] or {}, view["summary"] or {}
    max_steps = (((view["identity"] or {}).get("config") or {}).get("train") or {}).get("max_steps")
    return (sup.get("outcome") == "completed" and summary.get("global_step") is not None
            and summary.get("global_step") == max_steps)


def g1(views, gate):
    detail, ok = {}, True
    for name, view in views.items():
        rows = [h for h in view["steps"] if "sampling/importance_sampling_ratio/mean" in h]
        bad = [int(h["step"]) for h in rows
               if not (gate["ratio_mean_min"] <= h["sampling/importance_sampling_ratio/mean"] <= gate["ratio_mean_max"])
               or not finite(h.get("sampling/sampling_logp_difference/mean"))
               or h["sampling/sampling_logp_difference/mean"] > gate["logp_difference_mean_max"]]
        measured = bool(rows) and len(rows) == len(view["steps"])
        detail[name] = {"steps": len(view["steps"]), "measured_steps": len(rows), "failing_steps": bad,
                        "ratio_mean_range": [min(h["sampling/importance_sampling_ratio/mean"] for h in rows),
                                             max(h["sampling/importance_sampling_ratio/mean"] for h in rows)] if rows else None,
                        "logp_difference_mean_max": max(h["sampling/sampling_logp_difference/mean"] for h in rows)
                        if rows else None}
        ok = ok and measured and not bad
    return ok, detail


def g2(views, gate, total_gb):
    limit = gate["peak_fraction_of_gpu_max"] * total_gb
    detail = {name: (view["summary"] or {}).get("peak_gpu_memory_gb") for name, view in views.items()}
    ok = all(isinstance(v, (int, float)) and v <= limit for v in detail.values())
    return ok, {"limit_gb": round(limit, 2), "total_gb": total_gb, "peak_gb": detail}


def g3(views, resume, gate):
    detail, ok = {}, True
    for name, view in views.items():
        rows = view["rollouts"]
        errors = sum((r.get("answer") or {}).get("status") in ("verifier_timeout", "verifier_crashed") for r in rows)
        rate = errors / len(rows) if rows else None
        nonfinite = [int(h["step"]) for h in view["steps"] if not (finite(h.get("loss")) and finite(h.get("grad_norm")))]
        summary = view["summary"] or {}
        grid = summary.get("vllm_image_grid") or {}
        images = ((view["identity"] or {}).get("config") or {}).get("arm", {}).get("train_with_image")
        checks = {"completed": completed(view), "finite_loss_and_grad_norm": not nonfinite and bool(view["steps"]),
                  "verifier_error_rate": rate, "verifier_ok": rate is not None and rate <= gate["verifier_error_rate_max"],
                  "image_grid_ok": (not images) or grid.get("mismatches") == 0,
                  "alignment_checked": (not images) or ((summary.get("mm_alignment") or {}).get("checked_forwards") or 0) > 0}
        detail[name] = dict(checks, nonfinite_steps=nonfinite, outcome=(view["supervisor"] or {}).get("outcome"),
                            detail=(view["supervisor"] or {}).get("detail"))
        ok = ok and all(checks[k] for k in G3_RUN_CHECKS)
    resumed = bool((resume or {}).get("ok"))
    detail[RESUME] = {"completed": resumed}
    return ok and resumed, detail


def g4(pilot_v5, retry, reg):
    window = reg["pilot"]["gates"]["G4_learning"]["window_steps"]

    def judge(view, max_steps):
        early, n_early = window_mean(view["steps"], 1, window)
        late, n_late = window_mean(view["steps"], max_steps - window + 1, max_steps)
        ok = n_early == window and n_late == window and late > early
        return {"steps": [1, window, max_steps - window + 1, max_steps], "early_mean": early, "late_mean": late,
                "early_steps": n_early, "late_steps": n_late, "ok": ok}

    first = judge(pilot_v5, reg["pilot"]["learning_run"]["smoke"]["max_steps"])
    result = {"pilot_v5": first, "retry": None}
    if not first["ok"] and retry is not None and (retry["supervisor"] or {}).get("skipped") is not True and retry["steps"]:
        result["retry"] = judge(retry, reg["pilot"]["learning_retry"]["smoke"]["max_steps"])
    ok = first["ok"] or bool((result["retry"] or {}).get("ok"))
    return ok, result


def g5(pilot_v5, resume, gate):
    sup = pilot_v5["supervisor"] or {}
    saved = sorted(set(sup.get("checkpoints_saved") or []))
    uploads = {u.get("step"): u for u in sup.get("uploads") or []}
    per_checkpoint = {str(step): bool((uploads.get(step) or {}).get("ok")) for step in saved}
    final = bool((sup.get("final_upload") or {}).get("ok"))
    resume_ok = bool((resume or {}).get("ok"))
    restore = (resume or {}).get("restore") or {}
    ok = bool(saved) and all(per_checkpoint.values()) and final and resume_ok
    return ok, {"pilot_v5_checkpoints_verified": per_checkpoint, "pilot_v5_final_verified": final,
                "resume_ok": resume_ok, "resume_reason": (resume or {}).get("reason"),
                "restore_seconds": restore.get("seconds"), "restore_files": restore.get("files")}


def g6(views, protocol, max_prompt_tokens):
    detail, ok = {}, True
    for name, view in views.items():
        protocols = sorted({str(r.get("protocol")) for r in view["rollouts"]})
        tokens = ((view["identity"] or {}).get("prompt_report") or {}).get("max_tokens")
        good = protocols == [protocol] and isinstance(tokens, int) and tokens <= max_prompt_tokens
        detail[name] = {"protocols": protocols, "rollouts": len(view["rollouts"]), "max_prompt_tokens": tokens,
                        "ok": good}
        ok = ok and good
    return ok, detail


def recorded(view):
    """Pre-registered "record only" numbers of one formal-shape pilot (section 11)."""
    steps = view["steps"]

    def mean(key):
        values = [h[key] for h in steps if finite(h.get(key))]
        return round(sum(values) / len(values), 4) if values else None

    times = [h["step_time"] for h in steps if finite(h.get("step_time"))]
    rows = view["rollouts"]
    return {"step_seconds_median": round(statistics.median(times), 2) if times else None,
            "step_seconds_p90": s4_percentile(times, 0.9),
            "truncated_fraction": mean("completions/clipped_ratio"), "completion_length_mean": mean("completions/mean_length"),
            "answer_acc": mean("p3/answer_acc"), "format_rate": mean("p3/format_rate"),
            "claims_per_completion": mean("p3/claims_per_completion"), "kl": mean("kl"), "entropy": mean("entropy"),
            "rollouts": len(rows)}


def s4_percentile(values, q):
    value = s4_state.percentile(values, q)
    return round(value, 2) if value is not None else None


def gpu_total_gb(out_dir, repo, reg):
    """GPU memory (GB) as torch reported it in env.json; the frozen runtime's value when env.json is missing."""
    env = _load(Path(out_dir) / "env.json") or {}
    return (env.get("gpu") or {}).get("total_gb") or read_json(Path(repo) / reg["runtime"]["path"])["gpu"]["total_gb"]


def code_identity(python, repo, env=None):
    """source_sha256 and package versions of the training environment, by the same functions rl_entry records."""
    try:
        proc = subprocess.run([python, "-c", IDENTITY_SNIPPET], cwd=str(repo), capture_output=True, text=True,
                              timeout=600, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, "%s: %s" % (type(exc).__name__, exc)
    lines = [line for line in proc.stdout.splitlines() if line.startswith("{")]
    if proc.returncode != 0 or not lines:
        return None, (proc.stderr or proc.stdout)[-800:]
    return json.loads(lines[-1]), None


def decide(out_dir, repo, job, python=None):
    out, repo = Path(out_dir), Path(repo)
    reg = read_json(repo / "configs/experiments/s4_runs_20261110.json")
    experiment = read_json(repo / reg["experiment"]["path"])
    gates = reg["pilot"]["gates"]
    env = _load(out / "env.json") or {}
    total_gb = gpu_total_gb(out, repo, reg)
    views = {name: run_view(out / name) for name in FORMAL}
    retry = run_view(out / RETRY) if (out / RETRY).is_dir() else None
    resume = _load(out / (RESUME + ".supervisor.json"))
    resume_view = run_view(out / RESUME)
    formal = dict(views)
    if retry is not None and (retry["supervisor"] or {}).get("skipped") is not True and retry["present"]:
        formal[RETRY] = retry
    all_runs = dict(formal, **{RESUME: resume_view})
    result = {"schema": SCHEMA, "job": job, "rules": "docs/plan/S4预注册_20261110.md section 11", "gates": {}}
    for name, (ok, detail) in [("G1_importance_sampling", g1(formal, gates["G1_importance_sampling"])),
                               ("G2_memory", g2(formal, gates["G2_memory"], total_gb)),
                               ("G3_stability", g3(formal, resume, gates["G3_stability"])),
                               ("G4_learning", g4(views["pilot_v5"], retry, reg)),
                               ("G5_checkpoint_resume", g5(views["pilot_v5"], resume, gates["G5_checkpoint_resume"])),
                               ("G6_protocol", g6(all_runs, gates["G6_protocol"]["rollout_protocol"],
                                                  gates["G6_protocol"]["max_prompt_tokens"]))]:
        result["gates"][name] = {"ok": bool(ok), "detail": detail}
    result["passed"] = all(g["ok"] for g in result["gates"].values())
    result["recorded"] = {name: recorded(view) for name, view in formal.items()}
    identities = {name: view["identity"] for name, view in all_runs.items() if view["identity"]}
    sources = {json.dumps(i.get("source_sha256"), sort_keys=True) for i in identities.values()}
    versions = {json.dumps(i.get("versions"), sort_keys=True) for i in identities.values()}
    result["consistency"] = {"runs_with_identity": sorted(identities), "one_source": len(sources) == 1,
                             "one_package_set": len(versions) == 1}
    if len(sources) != 1 or len(versions) != 1:
        result["passed"] = False
    reference = (views["pilot_v5"]["identity"] or {})
    # the check ``train`` runs before every formal run (code freeze): it must work here and agree with the pilot
    current, error = code_identity(python or sys.executable, repo)
    result["code_now"] = {"error": error, "matches_pilot": bool(current) and current.get("source_sha256") ==
                          reference.get("source_sha256") and current.get("versions") == reference.get("versions")}
    if not result["code_now"]["matches_pilot"]:
        result["passed"] = False
    sup = views["pilot_v5"]["supervisor"] or {}
    uploads = [u.get("seconds") for u in sup.get("uploads") or [] if u.get("ok")]
    result["timing"] = dict(result["recorded"].get("pilot_v5", {}), startup_seconds=sup.get("startup_seconds"),
                            checkpoint_upload_seconds=max(uploads) if uploads else None,
                            final_upload_seconds=(sup.get("final_upload") or {}).get("seconds"),
                            restore_seconds=((resume or {}).get("restore") or {}).get("seconds"))
    result["latest"] = {"schema": "p3-pilot-latest-v1", "passed": result["passed"], "job": job,
                        "decided_utc": s4_state.utc(), "registry_sha256": sha256_file(repo / "configs/experiments/s4_runs_20261110.json"),
                        "runtime_content_sha256": reg["runtime"]["content_sha256"], "experiment": experiment["name"],
                        "protocol": reg["protocol"], "gpu_name": (env.get("gpu") or {}).get("name"),
                        "source_sha256": reference.get("source_sha256"), "versions": reference.get("versions"),
                        "git_commit": reference.get("git_commit"), "timing": result["timing"],
                        "gates": {k: v["ok"] for k, v in result["gates"].items()}}
    return result, reg, experiment


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--python", help="training environment interpreter (code identity check)")
    parser.add_argument("--drive-remote")
    parser.add_argument("--drive-dir")
    parser.add_argument("--drive-mount")
    parser.add_argument("--allow-missing", action="store_true", help="dry runs: decide from what exists, no Drive")
    args = parser.parse_args(argv)
    result, reg, experiment = decide(args.out_dir, args.repo, args.job, args.python)
    if args.allow_missing:
        result["drive"] = {"written": False, "reason": "dry run"}
    else:
        store, info = s4_state.Store.open(Path(args.out_dir) / ".drive_scratch", remote=args.drive_remote,
                                          base_dir=args.drive_dir, mount=args.drive_mount)
        if store is None:
            result["drive"] = {"written": False, "reason": "Drive is not usable: %s" % "; ".join(info["notes"])}
        else:
            base = s4_state.experiment_base(reg, experiment["name"])
            per_job = store.put_json("%s/pilot/%s/RESULT.json" % (base, args.job), result["latest"])
            latest = store.put_json("%s/PILOT_LATEST.json" % base, result["latest"])
            result["drive"] = {"written": bool(per_job.get("ok") and latest.get("ok")),
                               "path": "%s/PILOT_LATEST.json" % base,
                               "reason": None if latest.get("ok") else latest.get("reason")}
    write_json(Path(args.out_dir) / "pilot_gates.json", result)
    log("pilot gates: %s | %s | PILOT_LATEST.json on Drive: %s" % (
        "PASSED" if result["passed"] else "NOT PASSED",
        ", ".join("%s %s" % (k.split("_")[0], "ok" if v["ok"] else "FAIL") for k, v in result["gates"].items()),
        "written" if result["drive"]["written"] else "not written (%s)" % result["drive"].get("reason")))
    if not args.allow_missing and not result["drive"]["written"]:
        return 1
    return 0


def retry_needed(pilot_v5_dir, reg, repo):
    """(True, reason) when pilot_v5's G4 failed while its G1, G2, G3 and G6 passed (section 11: retry with 76 steps)."""
    pilot_v5_dir = Path(pilot_v5_dir)
    view = run_view(pilot_v5_dir)
    if not view["steps"]:
        return False, "pilot_v5 has no training log (it did not run or did not finish)"
    gates = reg["pilot"]["gates"]
    one = {"pilot_v5": view}
    learning, _ = g4(view, None, reg)
    if learning:
        return False, "G4 passed on pilot_v5"
    run_checks = g3(one, None, gates["G3_stability"])[1]["pilot_v5"]  # G3 on pilot_v5 itself (pilot_resume aside)
    others = {"G1": g1(one, gates["G1_importance_sampling"])[0],
              "G3": all(run_checks[k] for k in G3_RUN_CHECKS),
              "G6": g6(one, gates["G6_protocol"]["rollout_protocol"], gates["G6_protocol"]["max_prompt_tokens"])[0]}
    others["G2"] = g2(one, gates["G2_memory"], gpu_total_gb(pilot_v5_dir.parent, repo, reg))[0]
    failing = sorted(k for k, ok in others.items() if not ok)
    if failing:
        return False, "G4 failed, but so did %s: the pilot fails without a retry" % ", ".join(failing)
    return True, "G4 failed on pilot_v5 while G1, G2, G3 and G6 passed"


if __name__ == "__main__":
    sys.exit(main())
