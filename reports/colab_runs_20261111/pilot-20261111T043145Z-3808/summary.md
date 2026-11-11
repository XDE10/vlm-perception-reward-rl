# Colab 运行摘要：pilot-20261111T043145Z-3808（pilot）

总体结论：**通过**

## 步骤

| 步骤 | 状态 | 用时（秒） | 计入结论 |
|---|---|---|---|
| env_report | passed | 2 | 是 |
| verify_pack | passed | 0 | 是 |
| pytest | passed | 264 | 是 |
| register_check | passed | 1 | 是 |
| drive_probe | passed | 76 | 是 |
| vllm_env | passed | 28 | 是 |
| pilot_v5 | passed | 2587 | 是 |
| pilot_resume | passed | 388 | 是 |
| pilot_rl_ans | passed | 259 | 是 |
| pilot_rl_v4 | passed | 230 | 是 |
| pilot_rl_v5_placebo | passed | 246 | 是 |
| pilot_rl_blind | passed | 162 | 是 |
| pilot_v5_retry | passed | 0 | 是 |
| decide_pilot | passed | 29 | 是 |

## 检查

- ✅ 试跑门槛 G1–G6 全部通过（S4 预注册第 11 节）
- ✅ 试跑结论 PILOT_LATEST.json 已写到 Google Drive
- ✅ pytest 无失败
- ✅ 私有数据与锚点一致

## 环境

- GPU：NVIDIA A100-SXM4-40GB，42.41 GB；驱动 580.82.07
- torch 2.13.0+cu130（CUDA 13.0，后端 cu130），transformers 5.19.0，trl 1.17.1，peft 0.21.2
- 模型：Qwen/Qwen2.5-VL-3B-Instruct@66285546d2b8

## CPU 测试（VM 上，GPU 已隐藏）

314 项：302 通过，0 失败，0 错误，12 跳过（261.2 秒）

## GRPO 冒烟

| 运行 | 步数 | rollout 数 | 步时中位数（秒） | 峰值显存（GB） | 答案正确 | 格式 | 每条断言数 | 对齐检查：前向 / 左填充行 |
|---|---|---|---|---|---|---|---|---|
| pilot_resume | 2 | 8 | 6.5 | 19.0 | 0.000 | 0.000 | 2.12 | 6 / 6 |
| pilot_rl_ans | 3 | 192 | 54.1 | 24.2 | 0.031 | 0.589 | 6.27 | 72 / 504 |
| pilot_rl_blind | 3 | 192 | 30.6 | 22.5 | 0.010 | 0.573 | 5.91 | 0 / 0 |
| pilot_rl_v4 | 3 | 192 | 48.6 | 23.6 | 0.042 | 0.589 | 5.98 | 72 / 504 |
| pilot_rl_v5_placebo | 3 | 192 | 56.5 | 24.6 | 0.031 | 0.604 | 5.93 | 72 / 504 |
| pilot_v5 | 40 | 2560 | 55.5 | 27.2 | 0.065 | 0.606 | 6.02 | 960 / 6720 |

## S4 试跑门槛（`pilot_gates.json`，规则见 S4 预注册第 11 节；只用 train，冒烟标记，不进入任何分析）

结论：**全部通过，可以开始正式任务**；PILOT_LATEST.json 已写到 Drive（`s4/rl_v3_p1_20261110/PILOT_LATEST.json`）

| 门槛 | 结果 | 依据 |
|---|---|---|
| G1 重要性采样 | ✅ | pilot_rl_ans：权重 0.999–1.001，log-prob 差最大 0.0643，不合格步 无；pilot_rl_blind：权重 1.000–1.001，log-prob 差最大 0.0201，不合格步 无；pilot_rl_v4：权重 0.998–1.001，log-prob 差最大 0.0667，不合格步 无；pilot_rl_v5_placebo：权重 0.998–1.001，log-prob 差最大 0.0653，不合格步 无；pilot_v5：权重 0.997–1.003，log-prob 差最大 0.0807，不合格步 无 |
| G2 显存 | ✅ | 上限 38.17 GB；峰值 pilot_rl_ans 24.2，pilot_rl_blind 22.5，pilot_rl_v4 23.6，pilot_rl_v5_placebo 24.6，pilot_v5 27.2 |
| G3 稳定 | ✅ | pilot_resume：跑完；pilot_rl_ans：跑完，判分错误率 0.0000；pilot_rl_blind：跑完，判分错误率 0.0000；pilot_rl_v4：跑完，判分错误率 0.0000；pilot_rl_v5_placebo：跑完，判分错误率 0.0000；pilot_v5：跑完，判分错误率 0.0000 |
| G4 学习信号 | ✅ | pilot_v5 第 1–10 步格式率 0.592 → 第 31–40 步 0.605 |
| G5 checkpoint 与恢复 | ✅ | pilot_v5 checkpoint 核对 {'20': True, '40': True}，final 已核对；从 Drive 恢复 通过（16 秒） |
| G6 协议 | ✅ | pilot_resume：perception-think-answer-v3-p1-20261109，提示最长 1176 token；pilot_rl_ans：perception-think-answer-v3-p1-20261109，提示最长 1176 token；pilot_rl_blind：perception-think-answer-v3-p1-20261109，提示最长 319 token；pilot_rl_v4：perception-think-answer-v3-p1-20261109，提示最长 1176 token；pilot_rl_v5_placebo：perception-think-answer-v3-p1-20261109，提示最长 1176 token；pilot_v5：perception-think-answer-v3-p1-20261109，提示最长 1176 token |

- 各试跑的训练代码 SHA256 一致：True；包版本一致：True；`train` 用的代码核对在这台 VM 上可用且与试跑一致

只记录、不设门槛（正式形状的试跑）：

| 试跑 | 步时中位数 / p90（秒） | 截断比例 | 平均补全长度 | 答案准确率 | 格式率 | 每条断言数 | KL | 熵 |
|---|---|---|---|---|---|---|---|---|
| pilot_rl_ans | 51.2 / 58.5 | 0.000 | 220 | 0.031 | 0.589 | 6.27 | 0.0004 | 1.131 |
| pilot_rl_blind | 28.7 / 36.7 | 0.005 | 239 | 0.010 | 0.573 | 5.91 | 0.0002 | 1.002 |
| pilot_rl_v4 | 49.7 / 50.8 | 0.000 | 219 | 0.042 | 0.589 | 5.98 | 0.0005 | 1.160 |
| pilot_rl_v5_placebo | 51.0 / 63.2 | 0.005 | 221 | 0.031 | 0.604 | 5.93 | 0.0005 | 1.131 |
| pilot_v5 | 55.1 / 70.2 | 0.002 | 214 | 0.065 | 0.606 | 6.02 | 0.0008 | 1.048 |

- 供 `train` 估计用时：启动约 206 秒，checkpoint 上传最长 61 秒，final 上传 42 秒，恢复 16 秒

## Google Drive（可选；rclone，见 `drive_probe.json`）

- 结论：可用，写入/读回/校验/删除均成功
- rclone：rclone v1.60.1-DEV；远端 `mydrive:` 已配置：是；挂载点 `/content/mydrive` 存在：是
- 16 MB 随机文件：上传 6.1 秒（2.6 MB/s），下载 7.4 秒（2.2 MB/s），MD5 一致 True，`rclone check` 一致 True
- 经挂载写入的文件在 16.1 秒后出现在远端（挂载写入是异步的，所以持久化只用 `rclone copy` + `rclone check`）
- 探针文件已删除：probe.txt, probe.bin, via_mount.txt

## 结果推送到 GitHub（D37）

- 由 VM 直接推送到 `results/pilot-20261111T043145Z-3808`（运行开始时已用 dry-run 验证写权限）
