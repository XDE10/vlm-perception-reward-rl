# Colab 运行摘要：train-20261112T151735Z-1bb3（train）

总体结论：**通过**

## 步骤

| 步骤 | 状态 | 用时（秒） | 计入结论 |
|---|---|---|---|
| env_report | passed | 2 | 是 |
| verify_pack | passed | 0 | 是 |
| register_check | passed | 3 | 是 |
| drive_probe | passed | 42 | 是 |
| vllm_env | passed | 86 | 是 |
| train_runs | passed | 66943 | 是 |

## 检查

- ✅ 没有设置、代码冻结、Drive 或磁盘空间问题阻止训练
- ✅ 本次运行的任务都完成、按规则中断或跳过（没有失败）
- ✅ 私有数据与锚点一致

## 环境

- GPU：NVIDIA A100-SXM4-40GB，42.41 GB；驱动 580.82.07
- torch 2.13.0+cu130（CUDA 13.0，后端 cu130），transformers 5.19.0，trl 1.17.1，peft 0.21.2
- 模型：Qwen/Qwen2.5-VL-3B-Instruct@66285546d2b8

## S4 正式任务（`train_job.json`）

- 试跑：pilot-20261111T142648Z-a507（通过：True）；代码基准：train-20261111T161741Z-2bf5
- 计划在 2026-11-13T14:25:43Z 前结束，2026-11-13T14:40:43Z 停止仍在运行的任务；计划步时 75.6 秒
- 结束原因：time（rl_v5/seed3 needs about 5h00m53s, 4h24m59s left before the deadline）

| 顺序 | 任务 | Drive 上的状态 | 本次 | 说明 |
|---|---|---|---|---|
| 1 | rl_v5/seed1 | new | start |  |
| 2 | rl_ans/seed1 | completed | skip | completed |
| 3 | rl_blind/seed1 | completed | skip | completed |
| 4 | rl_v4/seed1 | completed | skip | completed |
| 5 | rl_v5_placebo/seed1 | completed | skip | completed |
| 6 | rl_v5/seed2 | started | resume | from checkpoint-38 |
| 7 | rl_ans/seed2 | new | start |  |
| 8 | rl_blind/seed2 | new | start |  |
| 9 | rl_v4/seed2 | new | start |  |
| 10 | rl_v5_placebo/seed2 | new | start |  |
| 11 | rl_v5/seed3 | new | stop | rl_v5/seed3 needs about 5h00m53s, 4h24m59s left before the deadline |

| 任务 | 结果 | 尝试次数 | 最后一步 | 用时 | checkpoint 上传（成功/全部） | final 已核对 |
|---|---|---|---|---|---|---|
| rl_v5/seed1 | 完成 | 1 | 228/228 | 12345 | 6/6 | 是 |
| rl_v5/seed2 | 完成 | 1 | 228/228 | 10316 | 5/5 | 是 |
| rl_ans/seed2 | 完成 | 1 | 228/228 | 12651 | 6/6 | 是 |
| rl_blind/seed2 | 完成 | 1 | 228/228 | 5857 | 6/6 | 是 |
| rl_v4/seed2 | 完成 | 1 | 228/228 | 12700 | 6/6 | 是 |
| rl_v5_placebo/seed2 | 完成 | 1 | 228/228 | 12420 | 6/6 | 是 |

## Google Drive（可选；rclone，见 `drive_probe.json`）

- 结论：可用，写入/读回/校验/删除均成功
- rclone：rclone v1.60.1-DEV；远端 `mydrive:` 已配置：是；挂载点 `/content/mydrive` 存在：是
- 16 MB 随机文件：上传 3.1 秒（5.2 MB/s），下载 3.1 秒（5.1 MB/s），MD5 一致 True，`rclone check` 一致 True
- 经挂载写入的文件在 10.1 秒后出现在远端（挂载写入是异步的，所以持久化只用 `rclone copy` + `rclone check`）
- 探针文件已删除：probe.txt, probe.bin, via_mount.txt

## 结果推送到 GitHub（D37）

- 由你本机的运行器推送；VM 端未推送的原因：no credential file at /content/gh_credentials, so the launcher pushes the results from your machine (to let the VM push, see colab/README.md section 8)
