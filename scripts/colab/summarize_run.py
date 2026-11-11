"""Summarise a Colab run directory into summary.json and summary.md (standard library only).

    python -m scripts.colab.summarize_run --out-dir <run dir>

Every number in the Markdown comes from a file in the same directory; missing
inputs are reported as missing, never filled in.
"""
import argparse
import json
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.colab.common import write_json

DEFAULT_THRESHOLDS = {"PointLiesOnLine": 0.06, "Parallel": 15.0, "Perpendicular": 15.0, "PointLiesOnCircle": 0.15,
                      "Angle": 35.0, "CongruentLength": 1.5, "CongruentAngle": 25.0}
ON_BY_DEFAULT = {"PointLiesOnLine", "Parallel", "Perpendicular", "PointLiesOnCircle"}
# scripts/colab/train_s4.py PROBLEM_STATES (kept here so the summary stays importable without the VM modules)
TRAIN_PROBLEM_STATES = ("failed", "failed_once", "completed_drive_failed", "restore_failed", "setup", "not_started")
GATE_LABELS = {"G1_importance_sampling": "G1 重要性采样", "G2_memory": "G2 显存", "G3_stability": "G3 稳定",
               "G4_learning": "G4 学习信号", "G5_checkpoint_resume": "G5 checkpoint 与恢复", "G6_protocol": "G6 协议"}
RUN_STATE_LABELS = {"completed": "完成", "completed_drive_failed": "完成，但 Drive 上的 final 未核对", "interrupted": "中断",
                    "failed": "失败（第二次计算失败）", "failed_once": "计算失败一次，本次没有时间重启",
                    "restore_failed": "从 Drive 恢复失败", "setup": "设置问题", "not_started": "未开始", "skipped": "跳过"}


def _brief_supervisor(sup):
    if not sup:
        return None
    return {k: sup.get(k) for k in ("outcome", "detail", "skipped", "reason", "last_step", "max_steps", "wall_seconds",
                                    "startup_seconds", "checkpoints_saved")} if sup else None


def _load(path):
    path = Path(path)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def pytest_summary(path):
    path = Path(path)
    if not path.is_file():
        return None
    root = ET.parse(str(path)).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    total = {k: sum(int(s.get(k, 0)) for s in suites) for k in ["tests", "failures", "errors", "skipped"]}
    failed = []
    for case in root.iter("testcase"):
        if case.find("failure") is not None or case.find("error") is not None:
            failed.append("%s::%s" % (case.get("classname"), case.get("name")))
    total["passed"] = total["tests"] - total["failures"] - total["errors"] - total["skipped"]
    total["failed_tests"] = failed[:50]
    total["seconds"] = round(sum(float(s.get("time", 0)) for s in suites), 1)
    return total


def rollout_stats(path):
    path = Path(path)
    if not path.is_file():
        return None
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not rows:
        return {"rollouts": 0}
    n = len(rows)
    tokens = [r["completion_tokens"] for r in rows if r.get("completion_tokens") is not None]
    return {"rollouts": n, "steps": len({r.get("global_step") for r in rows}),
            "answer_acc": round(sum(r["rewards"]["answer"] for r in rows) / n, 4),
            "format_rate": round(sum(r["rewards"]["format"] for r in rows) / n, 4),
            "protocol_ok": round(sum(bool(r.get("protocol_ok")) for r in rows) / n, 4),
            "perception_reward_mean": round(sum(r["rewards"]["perception"] for r in rows) / n, 4),
            "v5_own_mean": round(sum(r["v5_own"]["reward"] for r in rows) / n, 4),
            "claims_per_completion": round(sum(r["v5_own"].get("unique") or 0 for r in rows) / n, 2),
            "completion_tokens_mean": round(statistics.fmean(tokens), 1) if tokens else None,
            "completion_tokens_max": max(tokens) if tokens else None,
            "verifier_errors": sum(r["answer"]["status"] in ("verifier_timeout", "verifier_crashed") for r in rows),
            **perception_monitor(rows)}


def perception_monitor(rows):
    """Descriptive reward-hacking monitors (not gates): broken perception blocks, unknown share, gated diagrams, and
    completions whose valid format plus negative perception reward totals below a broken block (0)."""
    n = len(rows)
    v5 = [r.get("v5") or {} for r in rows]
    counted = sum((x.get("tp") or 0) + (x.get("false") or 0) + (x.get("unknown") or 0) for x in v5)
    def below_broken(r):
        rewards, weights = r.get("rewards") or {}, r.get("weights") or {}
        if rewards.get("format") != 1.0 or "format" not in weights or "perception" not in weights:
            return False
        return weights["format"] + weights["perception"] * (rewards.get("perception") or 0.0) < 0

    below = sum(below_broken(r) for r in rows)
    return {"block_fail_rate": round(sum(str(x.get("status") or "").startswith("block_") for x in v5) / n, 4),
            "unknown_share": round(sum(x.get("unknown") or 0 for x in v5) / counted, 4) if counted else None,
            "gated_rate": round(sum(bool(x.get("gated")) for x in v5) / n, 4),
            "valid_format_below_broken_rate": round(below / n, 4)}


def run_summary(run_dir):
    run_dir = Path(run_dir)
    train = _load(run_dir / "train_summary.json")
    identity = _load(run_dir / "run_identity.json") or {}
    history = _load(run_dir / "log_history.json") or []
    times = [h["step_time"] for h in history if isinstance(h, dict) and "step_time" in h]
    return {"train": train, "rollouts": rollout_stats(run_dir / "rollouts.jsonl"),
            "mm_alignment": (train or {}).get("mm_alignment"),
            "step_time_median": round(statistics.median(times[1:] or times), 2) if times else None,
            "trainable_parameters": (identity.get("parameters") or {}).get("trainable_parameters"),
            "vision_frozen": (identity.get("parameters") or {}).get("vision_frozen"),
            "config_sha256": identity.get("config_sha256"), "prompt_report": identity.get("prompt_report")}


def calibration_summary(path):
    data = _load(path)
    if not data:
        return None
    if "gate" not in data["train"]:  # v1 output (before D35): no gate, no leave-one-out estimate
        return None
    relations = {}
    for relation, block in data["train"]["sweep"].items():
        default = DEFAULT_THRESHOLDS.get(relation)
        entry = next((e for e in block["entries"] if e["threshold"] == default), None)
        val = next((e for e in data["validation"]["sweep"][relation]["entries"] if e["threshold"] == default), None)
        if entry:
            relations[relation] = {"threshold": default, "enabled_by_default": relation in ON_BY_DEFAULT,
                                   "certified_train": entry["certified"], "false_refutations_train": entry["false_refutations"],
                                   "false_refutation_ids": entry["false_refutation_ids"],
                                   "false_refutations_validation": val["false_refutations"] if val else None,
                                   "spray_refuted_fraction": entry["spray_refuted_fraction"]}
    train, val = data["train"], data["validation"]
    return {"train_rows": data["train_rows"], "validation_rows": data["validation_rows"], "relations": relations,
            "existence_refutations_of_certified": train["existence_refutations_of_certified"],
            "gate": {"train_rows_gated": train["gate"]["rows"], "validation_rows_gated": val["gate"]["rows"],
                     "train_by_family": train["gate"]["by_family"], "validation_by_family": val["gate"]["by_family"]},
            "after_gate": {"train": train["after_gate"], "validation": val["after_gate"]},
            "loo": train["loo"], "attacks": data["attacks_train"],
            "attacks_without_gate": data.get("attacks_train_without_gate")}


def build(out_dir):
    out = Path(out_dir)
    status = _load(out / "status.json") or {}
    summary = {"run_id": status.get("run_id"), "task": status.get("task"), "steps": status.get("steps", []),
               "error": status.get("error"), "env": _load(out / "env.json"),
               "pack": _load(out / "pack_verification.json"), "pytest": pytest_summary(out / "pytest.xml"),
               "calibration": calibration_summary(out / "calibration" / "calibration.json"),
               "gpu_probe": _load(out / "gpu_probe.json"), "v0_probe": _load(out / "v0_probe" / "summary.json"),
               "smoke": {p.name: run_summary(p) for p in sorted((out / "smoke").glob("*")) if p.is_dir()},
               "smoke_full_hf": run_summary(out / "smoke_full_hf") if (out / "smoke_full_hf").is_dir() else None,
               "smoke_full_vllm": run_summary(out / "smoke_full_vllm") if (out / "smoke_full_vllm").is_dir() else None,
               "resume": run_summary(out / "resume") if (out / "resume").is_dir() else None,
               "frozen_runtime": _load(out / "frozen_runtime.json"), "drive_probe": _load(out / "drive_probe.json"),
               "github_check": _load(out / "github_check.json"),
               "public_sources": _load(out / "public_sources.json"), "eval_sets_check": _load(out / "eval_sets_check.json"),
               "cfgeo_build": _load(out / "cfgeo_build.json"),
               "prompt_select": _load(out / "prompt_select" / "summary.json"),
               "v0_val82": _load(out / "v0_val82" / "summary.json"),
               "harness_check": _load(out / "harness_check" / "summary.json"),
               "is_check": run_summary(out / "is_check") if (out / "is_check").is_dir() else None,
               "s3_decisions": _load(out / "s3_decisions.json"),
               "pilot_gates": _load(out / "pilot_gates.json"),
               "pilot_runs": {p.name: dict(run_summary(p), supervisor=_brief_supervisor(_load(p / "supervisor.json")))
                              for p in sorted(out.glob("pilot_*")) if p.is_dir() and "." not in p.name},
               "pilot_resume": _load(out / "pilot_resume.supervisor.json"),
               "train_job": _load(out / "train_job.json")}
    checks = []
    dry = bool(((_load(out / "request.json") or {}).get("options") or {}).get("dry_run"))
    if summary["task"] == "pilot":
        gates = summary["pilot_gates"] or {}
        if dry:
            checks.append(("写出了试跑门槛的判定（dry run：没有训练，不写 Drive）", bool(gates)))
        else:
            checks.append(("试跑门槛 G1–G6 全部通过（S4 预注册第 11 节）", bool(gates.get("passed"))))
            checks.append(("试跑结论 PILOT_LATEST.json 已写到 Google Drive", bool((gates.get("drive") or {}).get("written"))))
    if summary["task"] == "train":
        job = summary["train_job"] or {}
        stop = job.get("stop") or {}
        if dry:
            checks.append(("写出了训练计划（dry run：没有训练，不写 Drive）", bool(job)))
        else:
            checks.append(("没有设置、代码冻结、Drive 或磁盘空间问题阻止训练",
                           bool(job) and stop.get("kind") not in ("setup", "space")))
            checks.append(("本次运行的任务都完成、按规则中断或跳过（没有失败）",
                           bool(job) and not any(r.get("state") in TRAIN_PROBLEM_STATES for r in job.get("runs") or [])))
    if summary["task"] == "drive-check":
        checks.append(("Drive 写入、读回、哈希校验、删除全部成功", bool((summary["drive_probe"] or {}).get("ok"))))
    if summary["eval_sets_check"] is not None:
        checks.append(("评测集规则在 VM 上复现了提交的定义（eval_sets.json）", bool(summary["eval_sets_check"].get("ok"))))
    if summary["cfgeo_build"] is not None:
        checks.append(("全部 CF-Geo 图像由补丁重建，像素哈希一致", bool(summary["cfgeo_build"].get("ok"))))
    if summary["harness_check"] is not None:
        checks.append(("评测代码路径检查通过（train 输入，五种条件与统计）", bool(summary["harness_check"].get("ok"))))
    if summary["task"] == "v0":
        decisions = summary["s3_decisions"] or {}
        checks.append(("写出了 S3 决策文件" if dry else "S3 决策完整（s3_decisions.json，输入检查全部通过）",
                       bool(decisions) and (dry or bool(decisions.get("complete")))))
    if summary["pytest"] is not None:
        checks.append(("pytest 无失败", summary["pytest"]["failures"] == 0 and summary["pytest"]["errors"] == 0))
    if summary["pack"] is not None:
        checks.append(("私有数据与锚点一致", bool(summary["pack"].get("ok"))))
    cal = summary["calibration"]
    if cal:
        after = list(cal["after_gate"]["train"].values()) + list(cal["after_gate"]["validation"].values())
        checks.append(("门控后奖励不证伪任何认证正例（train 与 validation）", all(n == 0 for n in after)))
        loo = cal["loo"]["relations"]
        checks.append(("门控后每类默认开启的几何检验，留一法残余误杀率不超过 %d%%（由 α、β 推出，D35）"
                       % round(100 * cal["loo"]["limit"]),
                       all(r["within_limit"] is not False for r in loo.values())))
    elif (out / "calibration" / "calibration.json").is_file():
        checks.append(("校准输出为新版格式（含门控与留一法）", False))
    probe = summary["gpu_probe"] or {}
    if probe:
        checks.append(("ViT/merger 冻结且只训练 LoRA", bool((probe.get("parameters") or {}).get("vision_frozen"))))
        checks.append(("所有训练提示不超过预算", not (probe.get("prompt_tokens") or {}).get("train_over_budget")))
    resume = summary["resume"] or {}
    if resume.get("train"):
        checks.append(("断点恢复后到达第 2 步", resume["train"].get("global_step") == 2))
    if summary["smoke_full_hf"] is not None:  # D33: the guard must have checked padded rows, not just run
        guard = summary["smoke_full_hf"].get("mm_alignment") or {}
        checks.append(("评分前向的图像 token 类型与 input_ids 一致，且检查覆盖了左填充的行（D33）",
                       guard.get("checked_forwards", 0) > 0 and guard.get("left_padded_rows", 0) > 0))
    summary["checks"] = [{"check": name, "ok": bool(ok)} for name, ok in checks]
    required = [s for s in summary["steps"] if s.get("required", True)]
    summary["overall"] = "passed" if (required and all(s.get("state") == "passed" for s in required)
                                      and all(c["ok"] for c in summary["checks"]) and not summary["error"]) else "failed"
    return summary


def _fmt(value, digits=3):
    if value is None:
        return "—"
    if isinstance(value, float):
        return ("%." + str(digits) + "f") % value
    return str(value)


def markdown(s):
    lines = ["# Colab 运行摘要：%s（%s）" % (s.get("run_id"), s.get("task")), "",
             "总体结论：**%s**%s" % ("通过" if s["overall"] == "passed" else "未通过",
                                ("；编排错误：" + s["error"]) if s.get("error") else ""), "",
             "## 步骤", "", "| 步骤 | 状态 | 用时（秒） | 计入结论 |", "|---|---|---|---|"]
    for step in s["steps"]:
        lines.append("| %s | %s | %s | %s |" % (step["name"], step.get("state"), _fmt(step.get("seconds"), 0),
                                              "是" if step.get("required", True) else "否"))
    if s["checks"]:
        lines += ["", "## 检查", ""] + ["- %s %s" % ("✅" if c["ok"] else "❌", c["check"]) for c in s["checks"]]
    env = s.get("env") or {}
    if env:
        gpu, torch, pk = env.get("gpu") or {}, env.get("torch") or {}, env.get("packages") or {}
        lines += ["", "## 环境", "",
                  "- GPU：%s，%s GB；驱动 %s" % (gpu.get("name"), gpu.get("total_gb"), (env.get("driver") or {}).get("driver")),
                  "- torch %s（CUDA %s，后端 %s），transformers %s，trl %s，peft %s" % (
                      torch.get("version"), torch.get("cuda_runtime"), (env.get("env") or {}).get("torch_backend"),
                      pk.get("transformers"), pk.get("trl"), pk.get("peft")),
                  "- 模型：%s@%s" % ((env.get("model") or {}).get("repo"), ((env.get("model") or {}).get("revision") or "")[:12])]
    if s.get("pytest"):
        p = s["pytest"]
        lines += ["", "## CPU 测试（VM 上，GPU 已隐藏）", "",
                  "%d 项：%d 通过，%d 失败，%d 错误，%d 跳过（%s 秒）" % (p["tests"], p["passed"], p["failures"], p["errors"],
                                                          p["skipped"], p["seconds"])]
        lines += ["- 失败：" + x for x in p["failed_tests"]]
    cal = s.get("calibration")
    if cal:
        lines += ["", "## v5 几何证伪校准（默认阈值）", "",
                  "| 关系 | 默认开启 | 阈值 | train 认证正例 | train 误杀（门控前） | val 误杀（门控前） | 罗列断言被证伪比例 |",
                  "|---|---|---|---|---|---|---|"]
        for name, r in cal["relations"].items():
            lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (name, "是" if r["enabled_by_default"] else "否", r["threshold"],
                                                                r["certified_train"], r["false_refutations_train"],
                                                                _fmt(r["false_refutations_validation"]),
                                                                _fmt(r["spray_refuted_fraction"])))
        gate = cal["gate"]
        lines += ["", "一致性门控（D35）：train 有 %s / %s 张图、validation 有 %s / %s 张图的标注否定了自己的认证事实，"
                      "这些图上同类检验不再用来证伪（按类别：train %s，validation %s）。门控后仍被证伪的认证正例："
                      "train %s 条，validation %s 条。" % (
                          gate["train_rows_gated"], cal["train_rows"], gate["validation_rows_gated"], cal["validation_rows"],
                          gate["train_by_family"], gate["validation_by_family"], sum(cal["after_gate"]["train"].values()),
                          sum(cal["after_gate"]["validation"].values())),
                  "", "| 关系（留一法，train） | 认证正例 | 残余误杀 | 比例 | 95%% 区间 | ≤ %d%% |" % round(100 * cal["loo"]["limit"]),
                  "|---|---|---|---|---|---|"]
        for name, r in cal["loo"]["relations"].items():
            ci = r.get("ci95")
            lines.append("| %s | %s | %s | %s | %s | %s |" % (name, r["certified"], r["residual"], _fmt(r["rate"]),
                                                          "—" if not ci else "%.3f–%.3f" % tuple(ci),
                                                          "—" if r["within_limit"] is None else ("是" if r["within_limit"] else "否")))
        pooled = cal["loo"]["pooled"]
        if pooled.get("ci95"):
            lines.append("| 合计 | %s | %s | %s | %.3f–%.3f | |" % (pooled["certified"], pooled["residual"], _fmt(pooled["rate"]),
                                                                pooled["ci95"][0], pooled["ci95"][1]))
        lines += ["", "| 罗列探针（含门控） | 题数 | v4 均值 | v5 均值 | v4 高于诚实读一半 | v5 高于诚实读一半 | v5 均值（关闭门控） |",
                  "|---|---|---|---|---|---|---|"]
        without = cal.get("attacks_without_gate") or {}
        for name, a in cal["attacks"].items():
            lines.append("| %s | %d | %s | %s | %s | %s | %s |" % (
                name, a["rows"], _fmt(a["mean_v4"]), _fmt(a["mean_v5"]), _fmt(a["share_beating_honest_half_v4"]),
                _fmt(a["share_beating_honest_half_v5"]), _fmt((without.get(name) or {}).get("mean_v5"))))
    probe = s.get("gpu_probe")
    if probe:
        par, pt, gen, vit = probe.get("parameters") or {}, probe.get("prompt_tokens") or {}, probe.get("generation") or {}, probe.get("vit") or {}
        lines += ["", "## GPU 探针（真实 3B 权重）", "",
                  "- 可训练参数 %s（LoRA 目标模块 %s 个），视觉参数 %s 全部冻结：%s" % (
                      par.get("trainable_parameters"), par.get("lora_target_modules"), par.get("vision_parameters"),
                      par.get("vision_frozen")),
                  "- 提示 token（含图像）：train 最大 %s / p95 %s，val 最大 %s；预算 %s，超预算 %d 条" % (
                      (pt.get("train") or {}).get("max"), (pt.get("train") or {}).get("p95"),
                      (pt.get("validation") or {}).get("max"), pt.get("budget"), len(pt.get("train_over_budget") or []))]
        for size, r in sorted((probe.get("micro_batch") or {}).items(), key=lambda kv: -int(kv[0])):
            lines.append("- 微批 %s（最长提示 + %s token 补全，前向+反向）：%s" % (
                size, probe.get("completion_len"), "OOM" if r.get("oom") else "峰值 %s GB，%s 秒，梯度有限 %s" % (
                    r.get("peak_gb"), r.get("seconds"), r.get("grads_finite"))))
        if gen:
            lines.append("- HF 生成：%s 条 × %s token，%s 秒，%s token/s，峰值 %s GB" % (
                gen.get("sequences"), gen.get("new_tokens"), gen.get("seconds"), gen.get("tokens_per_second"), gen.get("peak_gb")))
        if vit:
            lines.append("- ViT 占一次前向的 %s；缓存与不缓存的补全 log-prob 最大差 %s、平均差 %s（等价：%s）" % (
                vit.get("vit_fraction_of_forward"), vit.get("cache_logprob_max_abs_diff"),
                _fmt(vit.get("cache_logprob_mean_abs_diff"), 5), vit.get("equivalent")))
            lines.append("- 同一张图单独过 ViT 与成批过 ViT 的特征：最大绝对差 %s，相对差（L2）%s，特征最大绝对值 %s" % (
                _fmt(vit.get("batched_vs_single_image_max_abs_diff"), 4), _fmt(vit.get("batched_vs_single_image_max_rel_diff"), 6),
                _fmt(vit.get("image_feature_max_abs"), 1)))
    v0 = s.get("v0_probe")
    if v0:
        lines += ["", "## V0 探针（%d 道 validation，贪心解码；工程信号，不是评测结果）" % v0["n"], "",
                  "| 条件 | 协议合规 | 格式奖励 | 答案正确 | 补全长度 p50 / p90 / max | 触达长度上限 |", "|---|---|---|---|---|---|"]
        for cond, label in [("with_image", "有图"), ("blind", "无图")]:
            x = v0.get(cond) or {}
            lines.append("| %s | %s | %s | %s | %s / %s / %s | %s |" % (
                label, _fmt(x.get("protocol_ok_rate")), _fmt(x.get("format_rate")), _fmt(x.get("answer_accuracy")),
                x.get("completion_tokens_p50"), x.get("completion_tokens_p90"), x.get("completion_tokens_max"),
                _fmt(x.get("budget_exhausted_rate"))))
    rows = []
    for name, run in sorted((s.get("smoke") or {}).items()):
        rows.append((name, run))
    for name in ["smoke_full_hf", "smoke_full_vllm", "resume", "is_check"]:
        if s.get(name):
            rows.append((name, s[name]))
    for name, run in sorted((s.get("pilot_runs") or {}).items()):
        if run.get("train"):
            rows.append((name, run))
    if rows:
        lines += ["", "## GRPO 冒烟", "",
                  "| 运行 | 步数 | rollout 数 | 步时中位数（秒） | 峰值显存（GB） | 答案正确 | 格式 | 每条断言数 | 对齐检查：前向 / 左填充行 |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for name, run in rows:
            train, ro = run.get("train") or {}, run.get("rollouts") or {}
            guard = run.get("mm_alignment") or {}
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                name, train.get("global_step"), ro.get("rollouts"), _fmt(run.get("step_time_median"), 1),
                _fmt(train.get("peak_gpu_memory_gb"), 1), _fmt(ro.get("answer_acc")), _fmt(ro.get("format_rate")),
                _fmt(ro.get("claims_per_completion"), 2),
                "%s / %s" % (guard["checked_forwards"], guard["left_padded_rows"]) if guard else "—"))
    lines += s3_lines(s)
    lines += pilot_lines(s)
    lines += train_lines(s)
    lines += drive_lines(s.get("drive_probe"))
    gh = s.get("github_check") or {}
    if gh and gh.get("mode") != "off":
        lines += ["", "## 结果推送到 GitHub（D37）", "",
                  "- %s" % ("由 VM 直接推送到 `%s`（运行开始时已用 dry-run 验证写权限）" % gh.get("branch") if gh.get("ok")
                            else "由你本机的运行器推送；VM 端未推送的原因：%s" % gh.get("reason"))]
        if gh.get("warning"):
            lines.append("- 注意：%s" % gh["warning"])
    runtime = s.get("frozen_runtime")
    if runtime:
        lines += ["", "## 冻结的运行时决策（`frozen_runtime.json`）", "",
                  "- 生成后端 %s；微批 %s；ViT 缓存 %s；梯度检查点 %s" % (
                      runtime["generation_backend"], runtime["per_device_train_batch_size"], runtime["vision_cache"],
                      runtime["gradient_checkpointing"])] + ["- 理由：" + r for r in runtime.get("rationale", [])]
    failed = [x for x in s["steps"] if x.get("state") not in ("passed", "pending")]
    if failed:
        lines += ["", "## 未通过的步骤（日志末尾）", ""]
        for step in failed:
            lines += ["### %s（%s）" % (step["name"], step.get("state")), "", "```text", (step.get("log_tail") or step.get("reason") or "")[-3000:], "```", ""]
    return "\n".join(lines) + "\n"


def s3_lines(s):
    """Sections of a ``v0`` run (docs/plan/S3设计_20261109.md sections 6-7)."""
    lines = []
    decisions = s.get("s3_decisions")
    if decisions:
        lines += ["", "## S3 决策（`s3_decisions.json`，规则见 S3 设计第 6 节，只用 train 测量）", ""]
        prompt = decisions.get("prompt")
        if prompt:
            lines.append("- 提示：**%s**（P1 相对 P0：格式率 %+.3f，答案准确率 %+.3f；%d 道 train 题）" % (
                prompt["chosen"].upper(), prompt["format_gain"], prompt["answer_change"], prompt["problems"]))
            warmup = decisions["warmup"]
            lines.append("- 格式预热：%s（选定提示在温度 1.0 下的格式率 %.3f，阈值 %.2f）" % (
                "需要" if warmup["needed"] else "不需要", warmup["format_rate"], warmup["threshold"]))
            length = decisions["max_completion_length"]
            lines.append("- 生成长度上限：%s（写完 `</answer>` 的补全 %s 条，第 95 百分位 %s）%s" % (
                length["value"], length["finished"], _fmt(length.get("p95")),
                "" if length["decided"] else "；样本不足，未按规则决定，S4 试跑时再测"))
        else:
            lines.append("- 提示、格式预热、长度：没有测量（prompt_select 未运行或未完成）")
        backend = decisions["generation_backend"]
        lines.append("- S4 生成后端：**%s**（%s）" % (backend["value"], "重要性采样检查通过" if backend.get("passed") else
                                                 backend.get("reason") or "重要性采样检查未通过"))
        evaluation = (decisions.get("resolution") or {}).get("evaluation_images") or {}
        if evaluation:
            lines.append("- 分辨率：max_pixels 保持 %s；会被缩小的评测图 validation %s/%s、test %s/%s" % (
                decisions["resolution"]["max_pixels"], evaluation["validation"]["shrunk"],
                evaluation["validation"]["images"], evaluation["test"]["shrunk"], evaluation["test"]["images"]))
        steps = backend.get("steps") or []
        if steps:
            lines += ["", "| 步 | 平均权重 | 每 token log-prob 差（平均 / 最大） |", "|---|---|---|"]
            lines += ["| %s | %s | %s / %s |" % (r["step"], _fmt(r["ratio_mean"]), _fmt(r["logp_difference_mean"], 4),
                                               _fmt(r["logp_difference_max"], 2)) for r in steps]
    prompt = s.get("prompt_select")
    if prompt:
        lines += ["", "## 提示选择的测量（%d 道已批准 train 题，每题 4 个温度 1.0 样本 + 1 个贪心）" % prompt["problems"], "",
                  "| 提示 | 格式率（采样） | 答案准确率（采样） | 写到上限 | 写完 `</answer>` 条数 / p95 | 答案奖励有差别的题 | 格式率（贪心） | 答案（贪心） |",
                  "|---|---|---|---|---|---|---|---|"]
        for name, v in sorted(prompt["variants"].items()):
            a, g = v["sampled"], v["greedy"]
            lines.append("| %s | %s | %s | %s | %s / %s | %s / %s | %s | %s |" % (
                name.upper(), _fmt(a["format_rate"]), _fmt(a["answer_accuracy"]), _fmt(a["budget_exhausted_rate"]),
                a["finished"], _fmt((a.get("finished_tokens") or {}).get("p95")), a["problems_with_mixed_answer_reward"],
                a["problems"], _fmt(g["format_rate"]), _fmt(g["answer_accuracy"])))
    v0 = s.get("v0_val82")
    if v0:
        lines += ["", "## V0 诊断（validation 82 题，贪心；只测量，不用于任何决策）", "",
                  "| 条件 | 答案正确 | 三段协议完整 | 格式奖励 | 写到上限 | 重复循环 | 失败类别 |", "|---|---|---|---|---|---|---|"]
        labels = {"p0_image": "P0 有图", "p0_blind": "P0 无图", "answer_only_image": "只要答案，有图"}
        for name, c in v0["conditions"].items():
            classes = "，".join("%s %d" % (k, n) for k, n in c["failure_classes"].items())
            lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                labels.get(name, name), _fmt(c["answer_accuracy"]), _fmt(c["protocol_ok_rate"]), _fmt(c["format_rate"]),
                _fmt(c["budget_exhausted_rate"]), c["repetition_loops"], classes))
    checks = s.get("eval_sets_check")
    cfgeo = s.get("cfgeo_build")
    if checks or cfgeo:
        lines += ["", "## 评测输入（不运行模型）", ""]
        if checks:
            lines.append("- 评测集定义：%s；test 视觉必需 %s 题，CF 候选 %s 题" % (
                "与提交的 eval_sets.json 完全相同" if checks.get("ok") else "**与提交的不同**：%s" % checks.get("differences"),
                (checks.get("counts") or {}).get("test_vn"), (checks.get("counts") or {}).get("cf_candidates")))
        for name, f in sorted(((cfgeo or {}).get("files") or {}).items()):
            lines.append("- `%s`：%s/%s 题由补丁重建，像素一致%s" % (name, f["rebuilt"], f["items"],
                                                       "" if not f["failures"] else "；失败：%s" % f["failures"][:3]))
    harness = s.get("harness_check")
    if harness:
        summary = harness.get("summary") or {}
        lines += ["", "## 评测代码路径检查（只用 train；V0 的数字只说明代码能跑）", "",
                  "| 条件 | 题数 | 答案正确 | 写到上限 |", "|---|---|---|---|"]
        for name, c in summary.items():
            lines.append("| %s | %s | %s | %s |" % (name, c.get("n"), _fmt(c.get("accuracy")), _fmt(c.get("budget_exhausted_rate"))))
        for name, c in (harness.get("comparisons") or {}).items():
            lines.append("- %s：差 %s，95%% 区间 %s–%s，p = %s（%s 个图簇）" % (
                name, _fmt(c["estimate"]), _fmt(c["ci95"][0]), _fmt(c["ci95"][1]), _fmt(c["p_value"], 4), c["clusters"]))
        lines.append("- 检查：%s" % "，".join("%s %s" % (k, "✅" if v else "❌") for k, v in (harness.get("checks") or {}).items()))
    return lines


def pilot_lines(s):
    """Sections of a ``pilot`` run (docs/plan/S4预注册_20261110.md section 11)."""
    gates = s.get("pilot_gates")
    if not gates:
        return []
    detail = {k: v.get("detail") or {} for k, v in gates["gates"].items()}
    lines = ["", "## S4 试跑门槛（`pilot_gates.json`，规则见 S4 预注册第 11 节；只用 train，冒烟标记，不进入任何分析）", "",
             "结论：**%s**；PILOT_LATEST.json %s" % (
                 "全部通过，可以开始正式任务" if gates.get("passed") else "未通过，不能开始正式任务",
                 "已写到 Drive（`%s`）" % gates["drive"].get("path") if (gates.get("drive") or {}).get("written")
                 else "没有写到 Drive（%s）" % (gates.get("drive") or {}).get("reason")), "",
             "| 门槛 | 结果 | 依据 |", "|---|---|---|"]
    g1 = detail.get("G1_importance_sampling", {})
    lines.append("| %s | %s | %s |" % (GATE_LABELS["G1_importance_sampling"], _ok(gates, "G1_importance_sampling"), "；".join(
        "%s：权重 %s，log-prob 差最大 %s，不合格步 %s" % (
            name, "—" if not d.get("ratio_mean_range") else "%.3f–%.3f" % tuple(d["ratio_mean_range"]),
            _fmt(d.get("logp_difference_mean_max"), 4), d.get("failing_steps") or "无") for name, d in sorted(g1.items()))))
    g2 = detail.get("G2_memory", {})
    lines.append("| %s | %s | 上限 %s GB；峰值 %s |" % (GATE_LABELS["G2_memory"], _ok(gates, "G2_memory"), g2.get("limit_gb"),
                                                 "，".join("%s %s" % (k, _fmt(v, 1)) for k, v in
                                                          sorted((g2.get("peak_gb") or {}).items()))))
    g3 = detail.get("G3_stability", {})
    lines.append("| %s | %s | %s |" % (GATE_LABELS["G3_stability"], _ok(gates, "G3_stability"), "；".join(
        "%s：%s" % (name, "跑完" if d.get("completed") else "未跑完（%s）" % (d.get("detail") or d.get("outcome")))
        + ("，判分错误率 %s" % _fmt(d.get("verifier_error_rate"), 4) if "verifier_error_rate" in d else "")
        for name, d in sorted(g3.items()))))
    g4 = detail.get("G4_learning", {})
    first = g4.get("pilot_v5") or {}
    text = "pilot_v5 第 %s–%s 步格式率 %s → 第 %s–%s 步 %s" % (
        (first.get("steps") or [None] * 4)[0], (first.get("steps") or [None] * 4)[1], _fmt(first.get("early_mean")),
        (first.get("steps") or [None] * 4)[2], (first.get("steps") or [None] * 4)[3], _fmt(first.get("late_mean")))
    if g4.get("retry"):
        text += "；76 步重试：%s → %s" % (_fmt(g4["retry"].get("early_mean")), _fmt(g4["retry"].get("late_mean")))
    lines.append("| %s | %s | %s |" % (GATE_LABELS["G4_learning"], _ok(gates, "G4_learning"), text))
    g5 = detail.get("G5_checkpoint_resume", {})
    lines.append("| %s | %s | pilot_v5 checkpoint 核对 %s，final %s；从 Drive 恢复 %s%s |" % (
        GATE_LABELS["G5_checkpoint_resume"], _ok(gates, "G5_checkpoint_resume"), g5.get("pilot_v5_checkpoints_verified"),
        "已核对" if g5.get("pilot_v5_final_verified") else "未核对", "通过" if g5.get("resume_ok") else "未通过",
        "（%s 秒）" % _fmt(g5.get("restore_seconds"), 0) if g5.get("restore_seconds") else ""))
    g6 = detail.get("G6_protocol", {})
    lines.append("| %s | %s | %s |" % (GATE_LABELS["G6_protocol"], _ok(gates, "G6_protocol"), "；".join(
        "%s：%s，提示最长 %s token" % (name, "/".join(d.get("protocols") or ["无 rollout"]), d.get("max_prompt_tokens"))
        for name, d in sorted(g6.items()))))
    consistency = gates.get("consistency") or {}
    code = gates.get("code_now") or {}
    lines += ["", "- 各试跑的训练代码 SHA256 一致：%s；包版本一致：%s；`train` 用的代码核对在这台 VM 上%s" % (
        consistency.get("one_source"), consistency.get("one_package_set"),
        "可用且与试跑一致" if code.get("matches_pilot") else "未通过（%s）" % code.get("error"))]
    recorded = gates.get("recorded") or {}
    if recorded:
        lines += ["", "只记录、不设门槛（正式形状的试跑）：", "",
                  "| 试跑 | 步时中位数 / p90（秒） | 截断比例 | 平均补全长度 | 答案准确率 | 格式率 | 每条断言数 | KL | 熵 |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for name, r in sorted(recorded.items()):
            lines.append("| %s | %s / %s | %s | %s | %s | %s | %s | %s | %s |" % (
                name, _fmt(r.get("step_seconds_median"), 1), _fmt(r.get("step_seconds_p90"), 1),
                _fmt(r.get("truncated_fraction")), _fmt(r.get("completion_length_mean"), 0), _fmt(r.get("answer_acc")),
                _fmt(r.get("format_rate")), _fmt(r.get("claims_per_completion"), 2), _fmt(r.get("kl"), 4),
                _fmt(r.get("entropy"))))
    timing = gates.get("timing") or {}
    if timing:
        lines += ["", "- 供 `train` 估计用时：启动约 %s 秒，checkpoint 上传最长 %s 秒，final 上传 %s 秒，恢复 %s 秒" % (
            _fmt(timing.get("startup_seconds"), 0), _fmt(timing.get("checkpoint_upload_seconds"), 0),
            _fmt(timing.get("final_upload_seconds"), 0), _fmt(timing.get("restore_seconds"), 0))]
    return lines


def _ok(gates, name):
    return "✅" if (gates["gates"].get(name) or {}).get("ok") else "❌"


def train_lines(s):
    """Sections of a ``train`` run (docs/plan/S4预注册_20261110.md sections 8-12)."""
    job = s.get("train_job")
    if not job:
        return []
    checks = job.get("checks") or {}
    stop = job.get("stop") or {}
    lines = ["", "## S4 正式任务（`train_job.json`）%s" % ("：dry run，只读 Drive，没有训练" if job.get("dry_run") else ""), "",
             "- 试跑：%s（通过：%s）；代码基准：%s" % (checks.get("pilot"), checks.get("pilot_passed"),
                                            checks.get("baseline") or "本次写入或尚无"),
             "- 计划在 %s 前结束，%s 停止仍在运行的任务；计划步时 %s 秒" % (
                 checks.get("finish_by_utc"), checks.get("stop_at_utc"), checks.get("planned_step_seconds")),
             "- 结束原因：%s（%s）" % (stop.get("kind"), stop.get("reason"))]
    for problem in checks.get("problems") or []:
        lines.append("- 阻止训练的问题：%s" % problem)
    if job.get("plan"):
        lines += ["", "| 顺序 | 任务 | Drive 上的状态 | 本次 | 说明 |", "|---|---|---|---|---|"]
        for p in job["plan"]:
            lines.append("| %s | %s | %s | %s | %s |" % (p["order"], p["run"], p["state"], p["action"], p.get("reason") or ""))
    if job.get("runs"):
        lines += ["", "| 任务 | 结果 | 尝试次数 | 最后一步 | 用时 | checkpoint 上传（成功/全部） | final 已核对 |",
                  "|---|---|---|---|---|---|---|"]
        for r in job["runs"]:
            attempts = r.get("attempts") or []
            last = attempts[-1] if attempts else {}
            uploads = [u for a in attempts for u in a.get("uploads") or []]
            lines.append("| %s | %s | %d | %s/%s | %s | %d/%d | %s |" % (
                r["run"], RUN_STATE_LABELS.get(r.get("state"), r.get("state")), len(attempts), last.get("last_step"),
                last.get("max_steps"), _fmt(sum(a.get("wall_seconds") or 0 for a in attempts), 0),
                sum(1 for u in uploads if u.get("ok")), len(uploads),
                "是" if (last.get("final_upload") or {}).get("ok") else "否"))
            if r.get("reason"):
                lines.append("|  | %s |  |  |  |  |  |" % r["reason"][:300])
    return lines


def drive_lines(probe):
    if not probe:
        return []
    det = probe.get("detect") or {}
    lines = ["", "## Google Drive（可选；rclone，见 `drive_probe.json`）", "",
             "- 结论：%s" % ("可用，写入/读回/校验/删除均成功" if probe.get("ok") else "不可用或未通过：%s" % (
                 probe.get("reason") or "见 drive_probe.json")),
             "- rclone：%s；远端 `%s` 已配置：%s%s；挂载点 `%s` 存在：%s" % (
                 det.get("rclone_version") or "未安装", det.get("remote"), "是" if det.get("remote_configured") else "否",
                 "（配置文件取自正在运行的 rclone mount）" if det.get("config_source") == "running rclone mount" else "",
                 det.get("mount"), "是" if det.get("mount_present") else "否")]
    steps = probe.get("steps") or {}
    up, down, check = steps.get("upload_blob") or {}, steps.get("download_blob") or {}, steps.get("rclone_check") or {}
    if up or down:
        lines.append("- %s MB 随机文件：上传 %s 秒（%s MB/s），下载 %s 秒（%s MB/s），MD5 一致 %s，`rclone check` 一致 %s" % (
            probe.get("size_mb", "?"), _fmt(up.get("seconds"), 1), _fmt(up.get("mb_per_s"), 1), _fmt(down.get("seconds"), 1),
            _fmt(down.get("mb_per_s"), 1), down.get("md5_matches"), check.get("identical")))
    mount = steps.get("mount_write")
    if mount:
        if mount.get("error"):
            lines.append("- 经挂载写入失败：%s" % mount["error"])
        else:
            lines.append("- 经挂载写入的文件%s（挂载写入是异步的，所以持久化只用 `rclone copy` + `rclone check`）" % (
                "在 %s 秒后出现在远端" % _fmt(mount.get("seconds_until_visible"), 1) if mount.get("visible_on_remote")
                else "120 秒内未出现在远端"))
    if probe.get("deleted_probe_files") is not None:
        lines.append("- 探针文件已删除：%s" % (", ".join(probe["deleted_probe_files"]) or "无"))
    return lines


def minimal(out_dir):
    """Fallback when the full summary cannot run: status-only summary."""
    out = Path(out_dir)
    status = _load(out / "status.json") or {}
    summary = {"run_id": status.get("run_id"), "task": status.get("task"), "steps": status.get("steps", []),
               "error": status.get("error"), "checks": [], "overall": "failed", "minimal": True}
    write_json(out / "summary.json", summary)
    (out / "summary.md").write_text(markdown(summary), encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)
    summary = build(args.out_dir)
    write_json(Path(args.out_dir) / "summary.json", summary)
    (Path(args.out_dir) / "summary.md").write_text(markdown(summary), encoding="utf-8")
    print("summary:", summary["overall"])


if __name__ == "__main__":
    main()
