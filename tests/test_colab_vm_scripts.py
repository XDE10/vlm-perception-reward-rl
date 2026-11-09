"""CPU checks of the VM-side probe, decision and summary scripts (real code paths, tiny model)."""
import importlib.util
import json

import pytest

from scripts.colab.bootstrap import backend_candidates
from scripts.colab.decide_runtime import decide
from scripts.colab.summarize_run import build, markdown
from tests._mini_release import make_release
from tests._qwen import processor_dir, tiny_model

HAS_MODEL_DEPS = processor_dir() is not None and all(importlib.util.find_spec(m) for m in ["trl", "peft", "math_verify"])


def test_backend_candidates_follow_driver_cuda():
    assert backend_candidates([13, 0]) == ["cu130", "cu129", "cu126"]
    assert backend_candidates([12, 9]) == ["cu129", "cu126"]
    assert backend_candidates([12, 4]) == ["cu126", "cu129"]
    assert backend_candidates(None) == ["cu126"]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def fake_preflight(out, vllm_step=None, micro_peaks=(30.0, 18.0, 12.0), total=80.0, vit=(0.04, 0.001)):
    write(out / "request.json", {"run_id": "preflight-x", "options": {}})
    write(out / "env.json", {"gpu": {"name": "NVIDIA A100-SXM4-80GB", "total_gb": total},
                             "env": {"torch_backend": "cu130", "lock_sha256": "abc"}})
    write(out / "gpu_probe.json", {"gpu": {"name": "NVIDIA A100-SXM4-80GB", "total_gb": total},
                                   "parameters": {"vision_frozen": True, "trainable_parameters": 29933568},
                                   "prompt_tokens": {"budget": 1600, "train": {"max": 900}, "train_over_budget": []},
                                   "micro_batch": {str(s): {"peak_gb": p} for s, p in zip([8, 4, 2], micro_peaks)},
                                   "vit": {"vit_fraction_of_forward": vit[0], "cache_logprob_max_abs_diff": vit[1],
                                           "equivalent": vit[1] <= 0.02},
                                   "generation": {"tokens_per_second": 1500.0}})
    for name, step in [("smoke_full_hf", 60.0), ("smoke_full_vllm", vllm_step)]:
        if step is None:
            continue
        write(out / name / "train_summary.json", {"global_step": 3, "wall_seconds": 3 * step, "peak_gpu_memory_gb": 40.0})
        write(out / name / "log_history.json", [{"step_time": step * 1.5}, {"step_time": step}, {"step_time": step}])


def test_decide_runtime_rules(tmp_path):
    fake_preflight(tmp_path / "a")
    runtime, decided = decide(tmp_path / "a")
    assert decided and runtime["generation_backend"] == "hf" and runtime["per_device_train_batch_size"] == 8
    assert runtime["vision_cache"] is False  # ViT is only 4% of a forward pass
    fake_preflight(tmp_path / "b", vllm_step=30.0)
    assert decide(tmp_path / "b")[0]["generation_backend"] == "vllm"  # 30s <= 0.7 x 60s
    fake_preflight(tmp_path / "c", vllm_step=50.0)
    assert decide(tmp_path / "c")[0]["generation_backend"] == "hf"  # 50s > 0.7 x 60s
    fake_preflight(tmp_path / "d", micro_peaks=(36.0, 30.0, 20.0), total=40.0)
    assert decide(tmp_path / "d")[0]["per_device_train_batch_size"] == 4  # 30 GB <= 0.8 x 40 GB
    fake_preflight(tmp_path / "d2", micro_peaks=(36.0, 34.0, 20.0), total=40.0)
    assert decide(tmp_path / "d2")[0]["per_device_train_batch_size"] == 2  # only 20 GB fits
    fake_preflight(tmp_path / "e", vit=(0.2, 0.001))
    assert decide(tmp_path / "e")[0]["vision_cache"] is True
    fake_preflight(tmp_path / "f", vit=(0.2, 0.5))
    assert decide(tmp_path / "f")[0]["vision_cache"] is False  # not equivalent


def test_summary_renders_all_sections(tmp_path):
    out = tmp_path / "run"
    fake_preflight(out)
    write(out / "status.json", {"run_id": "preflight-x", "task": "preflight", "steps": [
        {"name": "gpu_probe", "state": "passed", "seconds": 120, "required": True},
        {"name": "v0_probe", "state": "failed", "seconds": 5, "required": False, "log_tail": "Traceback ..."}]})
    write(out / "v0_probe" / "summary.json", {"n": 16, "with_image": {"protocol_ok_rate": 0.25, "format_rate": 0.2,
                                                                     "answer_accuracy": 0.3, "completion_tokens_p50": 300,
                                                                     "completion_tokens_p90": 700,
                                                                     "completion_tokens_max": 1024,
                                                                     "budget_exhausted_rate": 0.06}, "blind": {}})
    rollout = {"global_step": 1, "completion_tokens": 100, "protocol_ok": True,
               "rewards": {"answer": 1.0, "format": 1.0, "perception": 0.5},
               "v5_own": {"reward": 0.5, "unique": 3}, "answer": {"status": "equivalent"}}
    (out / "smoke_full_hf" / "rollouts.jsonl").write_text(json.dumps(rollout) + "\n", encoding="utf-8")
    write(out / "drive_probe.json", {"ok": True, "size_mb": 16, "deleted_probe_files": ["probe.txt", "probe.bin"],
                                     "detect": {"rclone_version": "rclone v1.71.0", "remote": "mydrive:",
                                                "remote_configured": True, "mount": "/content/mydrive",
                                                "mount_present": True},
                                     "steps": {"upload_blob": {"seconds": 4.0, "mb_per_s": 4.0},
                                               "download_blob": {"seconds": 2.0, "mb_per_s": 8.0, "md5_matches": True},
                                               "rclone_check": {"identical": True},
                                               "mount_write": {"visible_on_remote": True, "seconds_until_visible": 35.0}}})
    summary = build(out)
    text = markdown(summary)
    for heading in ["## 步骤", "## GPU 探针", "## V0 探针", "## GRPO 冒烟", "## Google Drive", "## 未通过的步骤"]:
        assert heading in text, heading
    assert "在 35.0 秒后出现在远端" in text and "上传 4.0 秒（4.0 MB/s）" in text
    assert summary["overall"] == "passed"  # the only failed step is optional; Drive never gates a preflight


@pytest.mark.skipif(not HAS_MODEL_DEPS, reason="needs pinned processor files, trl, peft, math_verify")
def test_gpu_probe_code_path_on_cpu_with_tiny_model(tmp_path):
    from transformers import AutoProcessor

    from scripts.colab.gpu_probe import probe

    rows = make_release(tmp_path)
    report = probe(tiny_model(), AutoProcessor.from_pretrained(processor_dir()), rows, rows[:2], tmp_path,
                   completion_len=8, micro_sizes=(2, 1), gen_rows=2, gen_repeats=2, prompt_budget=1600, lora=(4, 8))
    assert report["parameters"]["vision_frozen"] and report["parameters"]["lora_target_modules"] == 14
    assert report["prompt_tokens"]["train"]["n"] == 4 and not report["prompt_tokens"]["train_over_budget"]
    assert report["micro_batch"]["2"]["grads_finite"] and report["micro_batch"]["2"]["nonzero_grad_tensors"] > 0
    assert report["generation"]["sequences"] == 4 and report["generation"]["new_tokens"] == 8
    assert report["vit"]["cache_hits"] > 0 and report["vit"]["cache_logprob_max_abs_diff"] < 1e-4


@pytest.mark.skipif(not HAS_MODEL_DEPS, reason="needs pinned processor files, trl, peft, math_verify")
def test_v0_probe_code_path_on_cpu_with_tiny_model(tmp_path):
    from transformers import AutoProcessor

    from scripts.colab.v0_probe import run_probe
    from src.data.intergps_index import load_index
    from src.rewards.answer import AnswerVerifier

    rows = make_release(tmp_path)
    index = load_index(tmp_path / "data/project3_audit/intergps_annotations.jsonl")
    verifier = AnswerVerifier(workers=1, timeout=60)
    try:
        result = run_probe(tiny_model().eval(), AutoProcessor.from_pretrained(processor_dir()), rows[:2], index, tmp_path,
                           max_new_tokens=6, batch_size=2, verifier=verifier)
    finally:
        verifier.close()
    assert result["summary"]["with_image"]["n"] == 2 and result["summary"]["blind"]["n"] == 2
    assert all(r["has_image"] for r in result["with_image"]) and not any(r["has_image"] for r in result["blind"])
