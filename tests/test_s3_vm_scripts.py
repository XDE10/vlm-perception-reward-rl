"""The S3 VM steps (scripts/colab: public_sources, eval_inputs, prompt_select, v0_diagnosis, decide_s3, tasks) and
the runner guards (GPU memory, job lock, vLLM image grid, Colab usage parsing) on CPU."""
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def sampled(format_rate, answer, finished=40, p95=600, mixed=10):
    return {"sampled": {"format_rate": format_rate, "answer_accuracy": answer, "finished": finished,
                        "finished_tokens": {"p50": 300, "p90": 500, "p95": p95, "max": 900} if finished else None,
                        "problems_with_mixed_answer_reward": mixed, "problems": 64, "completions": 256,
                        "samples_per_problem": 4, "protocol_ok_rate": format_rate, "budget_exhausted_rate": 0.1},
            "greedy": {"completions": 64, "format_rate": format_rate, "answer_accuracy": answer,
                       "budget_exhausted_rate": 0.1}}


# ---- decide_s3: the pre-registered rules ------------------------------------------------------------------------

def test_prompt_rule_boundaries():
    from scripts.colab.decide_s3 import prompt_rule

    assert prompt_rule({"p0": sampled(0.20, 0.10), "p1": sampled(0.30, 0.08)})["chosen"] == "p1"  # +0.10, -0.02
    assert prompt_rule({"p0": sampled(0.20, 0.10), "p1": sampled(0.29, 0.10)})["chosen"] == "p0"  # gain too small
    assert prompt_rule({"p0": sampled(0.20, 0.10), "p1": sampled(0.60, 0.07)})["chosen"] == "p0"  # answers drop 0.03
    assert prompt_rule({"p0": sampled(0.50, 0.10), "p1": sampled(0.40, 0.20)})["chosen"] == "p0"


def test_warmup_length_and_is_rules():
    from scripts.colab.decide_s3 import is_rule, length_rule, warmup_rule

    assert warmup_rule(0.49)["needed"] and not warmup_rule(0.50)["needed"]
    assert length_rule(sampled(0.5, 0.1, p95=870)["sampled"])["value"] == 1024
    assert length_rule(sampled(0.5, 0.1, p95=871)["sampled"])["value"] == 1536
    few = length_rule(sampled(0.5, 0.1, finished=19)["sampled"])
    assert few["value"] == 1024 and few["decided"] is False
    steps = lambda *rows: [{"step": i + 1, "sampling/importance_sampling_ratio/mean": r,  # noqa: E731
                            "sampling/sampling_logp_difference/mean": d, "sampling/sampling_logp_difference/max": 3.0}
                           for i, (r, d) in enumerate(rows)]
    assert is_rule(steps((1.01, 0.06), (0.98, 0.07), (1.05, 0.065)))["value"] == "vllm"
    assert is_rule(steps((1.01, 0.06), (0.55, 0.07), (1.05, 0.065)))["value"] == "hf"  # one step outside [0.9, 1.1]
    assert is_rule(steps((1.01, 0.06), (1.0, 0.11)))["value"] == "hf"  # log-prob gap too large
    missing = is_rule(None)
    assert missing["value"] == "hf" and not missing["passed"] and "fallback" in missing["reason"]
    assert is_rule([{"loss": 1.0}])["value"] == "hf"


def test_decide_writes_complete_decisions_and_the_summary_renders(tmp_path):
    from scripts.colab.decide_s3 import decide, main
    from scripts.colab.summarize_run import build, markdown

    out = tmp_path / "run"
    write(out / "prompt_select" / "summary.json", {"problems": 64, "variants": {"p0": sampled(0.20, 0.10),
                                                                                 "p1": sampled(0.35, 0.10)}})
    write(out / "eval_sets_check.json", {"ok": True, "counts": {"test_vn": 388, "cf_candidates": 224},
                                         "resolution": {"validation": {"images": 300, "shrunk": 0},
                                                        "test": {"images": 601, "shrunk": 0}}})
    write(out / "cfgeo_build.json", {"ok": True, "files": {"cfgeo.json": {"items": 158, "rebuilt": 158, "failures": []}}})
    write(out / "harness_check" / "summary.json", {"ok": True, "checks": {"e1_scored": True}, "summary": {
        "original": {"n": 32, "accuracy": 0.1, "budget_exhausted_rate": 0.2}}, "comparisons": {
        "original_vs_blind": {"estimate": 0.0, "ci95": [-0.1, 0.1], "p_value": 1.0, "clusters": 32}}})
    write(out / "v0_val82" / "summary.json", {"conditions": {"p0_image": {
        "answer_accuracy": 0.06, "protocol_ok_rate": 0.25, "format_rate": 0.25, "budget_exhausted_rate": 0.37,
        "repetition_loops": 5, "failure_classes": {"complete": 4, "facts_without_tags": 5}}}})
    write(out / "is_check" / "log_history.json", [{"step": 1, "sampling/importance_sampling_ratio/mean": 1.0,
                                                   "sampling/sampling_logp_difference/mean": 0.06,
                                                   "sampling/sampling_logp_difference/max": 2.9}])
    decisions = decide(out)
    assert decisions["prompt"]["chosen"] == "p1" and decisions["warmup"]["needed"] is True
    assert decisions["max_completion_length"]["value"] == 1024 and decisions["generation_backend"]["value"] == "vllm"
    assert decisions["complete"] is True and decisions["v0_val82_measured_only"]["p0_image"]["answer_accuracy"] == 0.06
    assert main(["--out-dir", str(out)]) == 0 and (out / "s3_decisions.json").is_file()
    write(out / "status.json", {"run_id": "v0-x", "task": "v0", "steps": [
        {"name": "decide_s3", "state": "passed", "seconds": 1, "required": True}]})
    write(out / "request.json", {"run_id": "v0-x", "task": "v0", "options": {}})
    summary = build(out)
    text = markdown(summary)
    for heading in ["## S3 决策", "## 提示选择的测量", "## V0 诊断", "## 评测输入", "## 评测代码路径检查"]:
        assert heading in text, heading
    assert "提示：**P1**" in text and "S4 生成后端：**vllm**" in text and summary["overall"] == "passed"
    write(out / "eval_sets_check.json", {"ok": False, "differences": ["test_vn.3"], "counts": {}})
    failed = build(out)
    assert failed["overall"] == "failed" and "**与提交的不同**" in markdown(failed)
    (out / "prompt_select" / "summary.json").unlink()
    with pytest.raises(SystemExit, match="prompt_select"):
        decide(out)
    assert decide(out, allow_missing=True)["complete"] is False


# ---- measurement helpers -----------------------------------------------------------------------------------------

def test_failure_classes_and_repetition():
    from scripts.colab.v0_diagnosis import failure_class, repeats

    assert failure_class("anything", True) == "complete"
    assert failure_class("Length(A,B)=5; Angle(A,B,C)=60 deg", False) == "facts_without_tags"
    assert failure_class("The answer is five.", False) == "no_tags"
    assert failure_class("<perception>Length(A,B)=5</perception> and then", False) == "perception_only"
    assert failure_class("<perception>x</perception><think>long", False) == "perception_and_think_no_answer"
    assert failure_class("<think>t</think><answer>4</answer>", False) == "answer_but_malformed"
    assert repeats("intro " + "the angle is 30; " * 6) and not repeats("no loop here, just text " * 1)


def test_prompt_select_statistics_and_sampling():
    from scripts.colab.prompt_select import percentile, pick, variant_stats

    items = [{"id": "train:%d" % i} for i in range(100)]
    assert pick(items, 64) == pick(list(reversed(items)), 64) and len(pick(items, 64)) == 64
    assert percentile(list(range(1, 101)), 95) == 95 and percentile([7], 95) == 7

    def record(item, correct, finished, tokens):
        return {"item": item, "text": "<answer>1</answer>" if finished else "<perception>", "completion_tokens": tokens,
                "format": 1.0 if finished else 0.0, "protocol_ok": finished, "budget_exhausted": not finished,
                "answer": {"correct": correct}}

    sampled_records = [record("a", True, True, 100), record("a", False, True, 200), record("b", False, False, 1024),
                       record("b", False, False, 1024)]
    stats = variant_stats(sampled_records, [record("a", True, True, 90)], samples=2)
    assert stats["sampled"]["format_rate"] == 0.5 and stats["sampled"]["finished"] == 2
    assert stats["sampled"]["problems_with_mixed_answer_reward"] == 1 and stats["sampled"]["finished_tokens"]["max"] == 200
    assert stats["greedy"]["answer_accuracy"] == 1.0


# ---- public sources and evaluation inputs --------------------------------------------------------------------

def test_public_sources_are_checked_against_the_ledger(tmp_path):
    from scripts.colab import public_sources

    payload = b"pinned bytes"
    repo = tmp_path / "repo"
    write(repo / "migration_manifest.json", {"files": [{"path": "data/project3_sources/geometry3k/data/x.parquet",
                                                        "bytes": len(payload),
                                                        "sha256": hashlib.sha256(payload).hexdigest()}]})

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    served = {"body": payload}
    opener = lambda url, timeout: Response(served["body"])  # noqa: E731
    names = ["geometry3k/data/x.parquet"]
    first = public_sources.run(tmp_path / "public", names, repo_root=repo, opener=opener, tries=1)
    assert first["ok"] and not first["files"][0]["reused"]
    assert public_sources.run(tmp_path / "public", names, repo_root=repo, opener=opener, tries=1)["files"][0]["reused"]
    (tmp_path / "public/geometry3k/data/x.parquet").write_bytes(b"tampered")
    served["body"] = b"wrong content"
    bad = public_sources.run(tmp_path / "public", names, repo_root=repo, opener=opener, tries=1)
    assert not bad["ok"] and "differs" in bad["files"][0]["errors"][0] or "size" in bad["files"][0]["errors"][0]
    with pytest.raises(ValueError, match="not pinned"):
        public_sources.run(tmp_path / "public", ["geometry3k/data/other.parquet"], repo_root=repo, opener=opener)


def test_differences_names_the_changed_paths():
    from scripts.colab.eval_inputs import differences

    assert differences({"a": [1, 2], "b": {"c": 1}}, {"a": [1, 2], "b": {"c": 1}}) == []
    assert differences({"a": [1, 3], "b": {"c": 1}}, {"a": [1, 2], "b": {}}) == ["a.1", "b.c (missing in the committed file)"]
    assert differences({"a": [1]}, {"a": [1, 2]}) == ["a"]


def test_cfgeo_build_step_reports_every_item(tmp_path):
    pytest.importorskip("pyarrow")
    pytest.importorskip("math_verify")
    from scripts.colab.eval_inputs import cfgeo
    from tests.test_eval_harness import cf_world

    spec = cf_world(tmp_path)
    write(tmp_path / "cfgeo.json", spec)
    report = cfgeo(tmp_path / "sources", tmp_path / "out.json", files=[tmp_path / "cfgeo.json"])
    assert report["ok"] and report["files"]["cfgeo.json"] == {"items": 3, "rebuilt": 3, "failures": [],
                                                              "edit_version": None}
    spec["items"][1]["k2"]["pixel"] = "0" * 64
    write(tmp_path / "cfgeo.json", spec)
    broken = cfgeo(tmp_path / "sources", tmp_path / "out.json", files=[tmp_path / "cfgeo.json"])
    assert not broken["ok"] and broken["files"]["cfgeo.json"]["failures"][0]["id"] == "test:1"


# ---- tasks and runner guards ------------------------------------------------------------------------------------

def test_v0_task_steps_and_dependencies(tmp_path):
    from scripts.colab.tasks import Context, steps_for

    request = {"run_id": "v0-x", "task": "v0", "options": {"vllm_probe": True}}
    bootstrap = {"envs": {"base": {"python": "/env/bin/python"}}, "model": {"local_dir": "/models/q"}}
    steps = steps_for(Context(tmp_path, request, bootstrap, kernel_python="/usr/bin/python3"))
    names = [s["name"] for s in steps]
    assert names == ["env_report", "verify_pack", "pytest", "public_sources", "eval_sets", "cfgeo_build", "prompt_select",
                     "v0_val82", "harness_check", "vllm_env", "is_check", "decide_s3"]
    by = {s["name"]: s for s in steps}
    assert by["eval_sets"]["depends_on"] == ["public_sources"] and by["harness_check"]["depends_on"] == ["cfgeo_build"]
    assert by["is_check"]["required"] is False and by["is_check"]["depends_on"] == ["vllm_env"]
    assert "configs/experiments/runtime_frozen_20261109.json" in " ".join(by["is_check"]["cmd"])
    assert by["is_check"]["cmd"][0].endswith("env/vllm/bin/python") and "max_steps=3" in by["is_check"]["cmd"]
    assert by["decide_s3"]["depends_on"] == ["prompt_select"] and by["decide_s3"]["required"]
    without = steps_for(Context(tmp_path, dict(request, options={"vllm_probe": False}), bootstrap, "/usr/bin/python3"))
    assert "is_check" not in [s["name"] for s in without]
    dry = steps_for(Context(tmp_path, dict(request, options={"dry_run": True}), bootstrap, "/usr/bin/python3"))
    assert [s["name"] for s in dry] == ["env_report", "verify_pack", "pytest", "decide_s3"]
    assert "--allow-missing" in dry[-1]["cmd"]


def test_gpu_memory_guard():
    from scripts.colab.bootstrap import gpu_memory_problem

    assert gpu_memory_problem({"name": "NVIDIA A100-SXM4-40GB", "memory_mib": 40960.0}, 40) is None
    assert gpu_memory_problem({"name": "NVIDIA H100 80GB HBM3", "memory_mib": 81559.0}, 40) is None
    small = gpu_memory_problem({"name": "NVIDIA L4", "memory_mib": 23034.0}, 40)
    assert "at least 40 GB" in small and "NVIDIA L4 with 24.2 GB" in small
    assert gpu_memory_problem({"name": "NVIDIA L4", "memory_mib": 23034.0}, None) is None  # preflight: any GPU
    assert "could not be read" in gpu_memory_problem({"name": "x"}, 40)


def test_kernel_job_starts_a_run_at_most_once(tmp_path):
    root = tmp_path / "p3"
    write(root / "inbox" / "request.json", {"run_id": "v0-x", "task": "v0"})
    (root / "out").mkdir(parents=True, exist_ok=True)
    (root / "out" / "v0-x.lock").write_text("{}", encoding="utf-8")  # an earlier exec claimed the run
    env = dict(os.environ, P3_REMOTE_ROOT=str(root))
    run = lambda: subprocess.run([sys.executable, str(ROOT / "colab/kernel_job.py")], env=env, capture_output=True,  # noqa: E731
                                 text=True, timeout=60)
    first = run()
    assert first.returncode == 0 and "JOB_ALREADY_STARTED v0-x" in first.stdout and "JOB_DONE" not in first.stdout
    write(root / "out" / "v0-x.done.json", {"run_id": "v0-x", "overall": "passed"})
    second = run()
    assert "already finished" in second.stdout and "JOB_DONE overall=passed" in second.stdout
    assert not (root / "repo").exists()  # the job itself never ran


def test_kernel_job_claims_the_lock_atomically(tmp_path, monkeypatch):
    import importlib.util

    spec = importlib.util.spec_from_file_location("kernel_job_module", ROOT / "colab/kernel_job.py")
    source = (ROOT / "colab/kernel_job.py").read_text(encoding="utf-8").replace("\n_p3_kernel_job()\n", "\n")
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, "kernel_job.py", "exec"), module.__dict__)
    assert module._claim(tmp_path, "run-a") is True
    assert module._claim(tmp_path, "run-a") is False and module._claim(tmp_path, "run-b") is True
    assert json.loads((tmp_path / "out/run-a.lock").read_text())["run_id"] == "run-a"


def test_active_assignments_parsing():
    from scripts.colab.local_tools import active_assignments

    text = "Current balance: 2434.20 compute units\nUsage rate: 16.78/hr\nActive assignments: 2\n"
    assert active_assignments(text) == 2 and active_assignments("stub usage") is None


def test_vllm_image_grid_guard(tmp_path):
    pytest.importorskip("transformers")
    from PIL import Image

    from src.training.vllm_guard import check_training_images, grid_mismatches, processor_pixel_limits

    write(tmp_path / "preprocessor_config.json", {"min_pixels": 3136, "max_pixels": 12845056, "patch_size": 14,
                                                  "merge_size": 2})
    assert processor_pixel_limits(tmp_path) == (3136, 12845056, 28)
    train, vllm = (3136, 802816), (3136, 12845056)
    assert grid_mismatches([(864, 434), (298, 190), (1000, 700)], train, vllm) == []
    # 1024 x 783 has fewer pixels than 802,816, but rounding to multiples of 28 (1036 x 784) pushes it over
    assert grid_mismatches([(1024, 783)], train, vllm) == [{"size": [1024, 783], "train": [756, 1008],
                                                            "vllm": [784, 1036]}]
    big = grid_mismatches([(2000, 1500)], train, vllm)
    assert big and big[0]["size"] == [2000, 1500] and big[0]["train"] != big[0]["vllm"]
    config = {"model": {"id": "x", "revision": "y", "min_pixels": 3136, "max_pixels": 802816}}
    report = check_training_images([{"image": Image.new("RGB", (300, 200))}, {"prompt": "blind"}], config, tmp_path)
    assert report == {"images": 1, "distinct_sizes": 1, "train_limits": [3136, 802816], "vllm_limits": [3136, 12845056],
                      "factor": 28, "mismatches": 0}
    with pytest.raises(RuntimeError, match="another patch grid"):
        check_training_images([{"image": Image.new("RGB", (2000, 1500))}], config, tmp_path)


# ---- the model steps on the tiny Qwen2.5-VL ---------------------------------------------------------------------

def _model_deps():
    import importlib.util

    from tests._qwen import processor_dir

    return processor_dir() is not None and all(importlib.util.find_spec(m) for m in ["transformers", "trl", "peft",
                                                                                       "pyarrow", "math_verify"])


class _Verifier:
    def verify_many(self, answers, references):
        return [{"correct": a is not None and a == r, "status": "equivalent" if a == r else "mismatch",
                 "normalized_answer": a} for a, r in zip(answers, references)]


@pytest.mark.skipif(not _model_deps(), reason="needs pinned processor files, transformers, trl, peft, pyarrow, math_verify")
def test_model_steps_run_on_the_tiny_model(tmp_path):
    from transformers import AutoProcessor

    from scripts.colab import harness_check, prompt_select, v0_diagnosis
    from src.evaluation import harness
    from src.rewards.perception_v5 import V5Config
    from tests._mini_release import make_release, mini_config
    from tests._qwen import processor_dir, tiny_model
    from tests.test_eval_harness import cf_world

    make_release(tmp_path, evaluation=2)
    config = mini_config(tmp_path)
    model, processor = tiny_model().eval(), AutoProcessor.from_pretrained(processor_dir())
    train = harness.train_items(tmp_path, config)
    result, records = prompt_select.measure(model, processor, train[:2], _Verifier(), V5Config(), 1.0, 1.0,
                                            max_new_tokens=4, samples=2, batch_size=4)
    assert set(result) == {"p0", "p1"} and result["p1"]["sampled"]["completions"] == 4
    assert result["p0"]["greedy"]["completions"] == 2 and len(records) == 12
    assert {r["prompt_variant"] for r in records} == {"p0", "p1"} and {r["decoding"] for r in records} == {"greedy", "sampled"}
    rows, summary = v0_diagnosis.run(model, processor, harness.val82_items(tmp_path, config), _Verifier(), V5Config(),
                                     max_new_tokens=4, batch_size=2)
    assert set(summary) == {"p0_image", "p0_blind", "answer_only_image"} and len(rows) == 6
    assert all("failure_class" in r for r in rows) and not any(r["has_image"] for r in rows if r["condition"] == "p0_blind")
    items = harness.cfgeo_items(cf_world(tmp_path), tmp_path / "sources")
    records, report = harness_check.run(model, processor, train[:2], items, _Verifier(), V5Config(), 4, batch_size=2,
                                        resamples=100)
    assert report["ok"], report["checks"]
    assert set(records) == {"e1_original", "original", "blind", "swap", "cf_k1", "cf_k2"}
    assert report["comparisons"]["cf_k2_vs_cf_k1"]["items"] == 3
