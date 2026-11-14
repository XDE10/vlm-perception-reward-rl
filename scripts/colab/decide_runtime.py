"""Freeze runtime decisions from preflight measurements (standard library only).

    python -m scripts.colab.decide_runtime --out-dir <preflight out>

Writes ``frozen_runtime.json``. Every key is algorithm-neutral (see
``src/training/rl_entry.py:ALGORITHM_NEUTRAL_RUNTIME_KEYS``); all arms of the
experiment use the same file. Rules (conservative, recorded with the numbers):

* micro-batch: largest of 8/4/2 whose measured peak (longest prompts + full
  completion, fwd+bwd) is <= 80% of GPU memory;
* generation backend: vLLM only if its 3-step smoke passed and its median step
  time is <= 0.7x the HF smoke's; otherwise HF;
* frozen-ViT cache: only if cached and uncached completion log-probs agree
  (max abs diff <= 0.02) and the ViT is >= 10% of a forward pass.
"""
import argparse
import json
import statistics
import time
from pathlib import Path

from scripts.colab.common import write_json

SCHEMA = "p3-frozen-runtime-v1"


def _load(path):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def step_time(run_dir):
    """Median TRL step_time over steps after the first (warm-up), else wall/steps."""
    run_dir = Path(run_dir)
    history = _load(run_dir / "log_history.json") or []
    times = [h["step_time"] for h in history if isinstance(h, dict) and "step_time" in h]
    if len(times) > 1:
        return round(statistics.median(times[1:]), 2)
    if times:
        return round(times[0], 2)
    summary = _load(run_dir / "train_summary.json")
    if summary and summary.get("global_step"):
        return round(summary["wall_seconds"] / summary["global_step"], 2)
    return None


def decide(out_dir):
    out = Path(out_dir)
    env = _load(out / "env.json") or {}
    probe = _load(out / "gpu_probe.json") or {}
    hf = _load(out / "smoke_full_hf" / "train_summary.json")
    vllm = _load(out / "smoke_full_vllm" / "train_summary.json")
    request = _load(out / "request.json") or {}
    total = (probe.get("gpu") or env.get("gpu") or {}).get("total_gb")
    rationale, measured = [], {}

    micro = 8
    sizes = probe.get("micro_batch") or {}
    if total and sizes:
        fits = [int(s) for s, r in sizes.items() if not r.get("oom") and r.get("peak_gb") is not None
                and r["peak_gb"] <= 0.8 * total]
        if fits:
            micro = max(fits)
            rationale.append("micro-batch %d: measured fwd+bwd peak %.1f GB <= 80%% of %.1f GB" % (
                micro, sizes[str(micro)]["peak_gb"], total))
        else:
            micro = 2
            rationale.append("micro-batch 2: no measured size fit within 80%% of %s GB; verify in the pilot" % total)
    else:
        rationale.append("micro-batch 8: registered default (no GPU memory measurement available)")
    measured["micro_batch"] = sizes

    hf_time, vllm_time = (step_time(out / "smoke_full_hf") if hf else None), (step_time(out / "smoke_full_vllm") if vllm else None)
    measured.update(hf_step_seconds=hf_time, vllm_step_seconds=vllm_time,
                    hf_peak_gb=(hf or {}).get("peak_gpu_memory_gb"), vllm_peak_gb=(vllm or {}).get("peak_gpu_memory_gb"))
    backend = "hf"
    if vllm and hf_time and vllm_time and vllm_time <= 0.7 * hf_time:
        backend = "vllm"
        rationale.append("generation vLLM: smoke passed, %.1fs/step vs HF %.1fs/step (<= 0.7x)" % (vllm_time, hf_time))
    elif vllm and hf_time and vllm_time:
        rationale.append("generation HF: vLLM %.1fs/step is not <= 0.7x HF %.1fs/step" % (vllm_time, hf_time))
    else:
        vllm_env = _load(out.parent.parent / "state" / "vllm_env.json") if out.parent.name == "out" else None
        reason = (vllm_env or {}).get("reason") or ("vLLM smoke did not produce a result" if hf else "no HF smoke result")
        rationale.append("generation HF: " + reason)

    vit = probe.get("vit") or {}
    cache = bool(vit.get("equivalent")) and (vit.get("vit_fraction_of_forward") or 0) >= 0.10
    rationale.append("frozen-ViT cache %s: ViT is %s of a forward pass, cached-vs-uncached max |dlogp| = %s" % (
        "on" if cache else "off", vit.get("vit_fraction_of_forward"), vit.get("cache_logprob_max_abs_diff")))
    measured["vit"] = vit
    measured["generation_probe"] = probe.get("generation")

    decided = bool(hf) and bool(probe) and not request.get("options", {}).get("dry_run")
    runtime = {
        "schema": SCHEMA,
        "generation_backend": backend,
        "vllm_gpu_memory_utilization": 0.3,
        "vllm_max_model_length": 4096,
        "vision_cache": cache,
        "per_device_train_batch_size": micro,
        "gradient_checkpointing": True,
        "gpu": {"name": (probe.get("gpu") or env.get("gpu") or {}).get("name"), "total_gb": total},
        "torch_backend": (env.get("env") or {}).get("torch_backend"),
        "env_lock_sha256": (env.get("env") or {}).get("lock_sha256"),
        "measured": measured,
        "rationale": rationale,
        "decided_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "preflight %s%s" % (request.get("run_id", "?"), "" if decided else " (NOT DECIDED: missing measurements)"),
    }
    return runtime, decided


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)
    runtime, decided = decide(args.out_dir)
    write_json(Path(args.out_dir) / "frozen_runtime.json", runtime)
    print(json.dumps({k: runtime[k] for k in ["generation_backend", "per_device_train_batch_size", "vision_cache",
                                               "rationale", "source"]}, ensure_ascii=False))
    request = _load(Path(args.out_dir) / "request.json") or {}
    return 0 if decided or request.get("options", {}).get("dry_run") else 1


if __name__ == "__main__":
    raise SystemExit(main())
