# Colab 运行摘要：train-20261111T160222Z-a456（train）

总体结论：**未通过**

## 步骤

| 步骤 | 状态 | 用时（秒） | 计入结论 |
|---|---|---|---|
| env_report | passed | 2 | 是 |
| verify_pack | passed | 0 | 是 |
| register_check | passed | 1 | 是 |
| drive_probe | passed | 46 | 是 |
| vllm_env | passed | 5 | 是 |
| train_runs | failed | 10 | 是 |

## 检查

- ❌ 没有设置、代码冻结、Drive 或磁盘空间问题阻止训练
- ✅ 本次运行的任务都完成、按规则中断或跳过（没有失败）
- ✅ 私有数据与锚点一致

## 环境

- GPU：NVIDIA A100-SXM4-40GB，42.41 GB；驱动 580.82.07
- torch 2.13.0+cu130（CUDA 13.0，后端 cu130），transformers 5.19.0，trl 1.17.1，peft 0.21.2
- 模型：Qwen/Qwen2.5-VL-3B-Instruct@66285546d2b8

## S4 正式任务（`train_job.json`）

- 试跑：pilot-20261111T142648Z-a507（通过：True）；代码基准：train-20261111T064626Z-27c7
- 计划在 None 前结束，None 停止仍在运行的任务；计划步时 None 秒
- 结束原因：setup（training code differs from the code baseline of the first formal run (job train-20261111T064626Z-27c7, 2026-11-11T06:49:49Z); a code change during S4 needs a new decision (pre-registration section 9)）
- 阻止训练的问题：training code differs from the code baseline of the first formal run (job train-20261111T064626Z-27c7, 2026-11-11T06:49:49Z); a code change during S4 needs a new decision (pre-registration section 9)

## Google Drive（可选；rclone，见 `drive_probe.json`）

- 结论：可用，写入/读回/校验/删除均成功
- rclone：rclone v1.60.1-DEV；远端 `mydrive:` 已配置：是；挂载点 `/content/mydrive` 存在：是
- 16 MB 随机文件：上传 3.1 秒（5.2 MB/s），下载 3.4 秒（4.8 MB/s），MD5 一致 True，`rclone check` 一致 True
- 经挂载写入的文件在 11.2 秒后出现在远端（挂载写入是异步的，所以持久化只用 `rclone copy` + `rclone check`）
- 探针文件已删除：probe.txt, probe.bin, via_mount.txt

## 结果推送到 GitHub（D37）

- 由 VM 直接推送到 `results/train-20261111T160222Z-a456`（运行开始时已用 dry-run 验证写权限）

## 未通过的步骤（日志末尾）

### train_runs（failed）

```text
[p3] 16:04:59 train: stop (setup): training code differs from the code baseline of the first formal run (job train-20261111T064626Z-27c7, 2026-11-11T06:49:49Z); a code change during S4 needs a new decision (pre-registration section 9)
```

