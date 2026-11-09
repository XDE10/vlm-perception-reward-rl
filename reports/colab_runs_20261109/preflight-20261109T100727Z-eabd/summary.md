# Colab 运行摘要：preflight-20261109T100727Z-eabd（preflight）

总体结论：**通过**

## 步骤

| 步骤 | 状态 | 用时（秒） | 计入结论 |
|---|---|---|---|
| env_report | passed | 2 | 是 |
| verify_pack | passed | 0 | 是 |
| drive_probe | passed | 0 | 否 |
| pytest | passed | 165 | 是 |
| calibration | passed | 161 | 是 |
| gpu_probe | passed | 185 | 是 |
| v0_probe | passed | 115 | 否 |
| smoke_rl_ans | passed | 57 | 是 |
| smoke_rl_v4 | passed | 57 | 是 |
| smoke_rl_v5 | passed | 57 | 是 |
| smoke_rl_v5_placebo | passed | 58 | 是 |
| smoke_rl_blind | passed | 46 | 是 |
| smoke_full_hf | passed | 403 | 是 |
| resume_a | passed | 60 | 是 |
| resume_b | passed | 44 | 是 |
| vllm_env | passed | 68 | 否 |
| smoke_full_vllm | passed | 301 | 否 |
| decide_runtime | passed | 0 | 是 |

## 检查

- ✅ pytest 无失败
- ✅ 私有数据与锚点一致
- ✅ 门控后奖励不证伪任何认证正例（train 与 validation）
- ✅ 门控后每类默认开启的几何检验，留一法残余误杀率不超过 5%（由 α、β 推出，D35）
- ✅ ViT/merger 冻结且只训练 LoRA
- ✅ 所有训练提示不超过预算
- ✅ 断点恢复后到达第 2 步
- ✅ 评分前向的图像 token 类型与 input_ids 一致，且检查覆盖了左填充的行（D33）

## 环境

- GPU：NVIDIA A100-SXM4-40GB，42.41 GB；驱动 580.82.07
- torch 2.13.0+cu130（CUDA 13.0，后端 cu130），transformers 5.19.0，trl 1.17.1，peft 0.21.2
- 模型：Qwen/Qwen2.5-VL-3B-Instruct@66285546d2b8

## CPU 测试（VM 上，GPU 已隐藏）

218 项：212 通过，0 失败，0 错误，6 跳过（162.5 秒）

## v5 几何证伪校准（默认阈值）

| 关系 | 默认开启 | 阈值 | train 认证正例 | train 误杀（门控前） | val 误杀（门控前） | 罗列断言被证伪比例 |
|---|---|---|---|---|---|---|
| PointLiesOnLine | 是 | 0.06 | 538 | 5 | 0 | 0.790 |
| Parallel | 是 | 15.0 | 19 | 1 | 0 | 0.899 |
| Perpendicular | 是 | 15.0 | 264 | 11 | 2 | 0.796 |
| PointLiesOnCircle | 是 | 0.15 | 493 | 11 | 1 | — |
| Angle | 否 | 35.0 | 427 | 3 | 0 | 0.282 |
| CongruentLength | 否 | 1.5 | 91 | 0 | 0 | — |
| CongruentAngle | 否 | 25.0 | 36 | 0 | 0 | — |

一致性门控（D35）：train 有 20 / 609 张图、validation 有 2 / 82 张图的标注否定了自己的认证事实，这些图上同类检验不再用来证伪（按类别：train {'coordinates': 20}，validation {'coordinates': 2}）。门控后仍被证伪的认证正例：train 0 条，validation 0 条。

| 关系（留一法，train） | 认证正例 | 残余误杀 | 比例 | 95% 区间 | ≤ 5% |
|---|---|---|---|---|---|
| PointLiesOnLine | 538 | 2 | 0.004 | 0.001–0.013 | 是 |
| Parallel | 19 | 0 | 0.000 | 0.000–0.168 | 是 |
| Perpendicular | 264 | 11 | 0.042 | 0.023–0.073 | 是 |
| PointLiesOnCircle | 493 | 3 | 0.006 | 0.002–0.018 | 是 |
| 合计 | 1314 | 16 | 0.012 | 0.007–0.020 | |

| 罗列探针（含门控） | 题数 | v4 均值 | v5 均值 | v4 高于诚实读一半 | v5 高于诚实读一半 | v5 均值（关闭门控） |
|---|---|---|---|---|---|---|
| honest_full | 609 | 1.000 | 1.000 | 0.941 | 0.941 | 1.000 |
| honest_half | 609 | 0.719 | 0.569 | 0.000 | 0.000 | 0.569 |
| incidence_spray | 608 | 0.176 | -0.916 | 0.031 | 0.003 | -0.944 |
| pair_spray | 608 | 0.080 | -0.925 | 0.000 | 0.000 | -0.948 |
| value_spray | 449 | 0.591 | 0.065 | 0.203 | 0.143 | 0.065 |
| combined_spray | 608 | 0.404 | -0.944 | 0.155 | 0.000 | -0.973 |
| combined_spray_with_gold | 609 | 0.969 | -0.725 | 0.905 | 0.043 | -0.767 |

## GPU 探针（真实 3B 权重）

- 可训练参数 29933568（LoRA 目标模块 112 个），视觉参数 668684288 全部冻结：True
- 提示 token（含图像）：train 最大 1153 / p95 707，val 最大 746；预算 1600，超预算 0 条
- 微批 8（最长提示 + 1024 token 补全，前向+反向）：峰值 18.04 GB，14.36 秒，梯度有限 True
- 微批 4（最长提示 + 1024 token 补全，前向+反向）：峰值 13.09 GB，5.3 秒，梯度有限 True
- 微批 2（最长提示 + 1024 token 补全，前向+反向）：峰值 10.43 GB，2.7 秒，梯度有限 True
- HF 生成：64 条 × 1024 token，128.86 秒，508.6 token/s，峰值 24.06 GB
- ViT 占一次前向的 0.4182；缓存与不缓存的补全 log-prob 最大差 0.40537071228027344、平均差 0.02792（等价：False）
- 同一张图单独过 ViT 与成批过 ViT 的特征：最大绝对差 2.5137，相对差（L2）0.035212，特征最大绝对值 34.5

## V0 探针（16 道 validation，贪心解码；工程信号，不是评测结果）

| 条件 | 协议合规 | 格式奖励 | 答案正确 | 补全长度 p50 / p90 / max | 触达长度上限 |
|---|---|---|---|---|---|
| 有图 | 0.250 | 0.250 | 0.062 | 198 / 1024 / 1024 | 0.375 |
| 无图 | 0.562 | 0.562 | 0.062 | 313 / 1024 / 1024 | 0.375 |

## GRPO 冒烟

| 运行 | 步数 | rollout 数 | 步时中位数（秒） | 峰值显存（GB） | 答案正确 | 格式 | 每条断言数 | 对齐检查：前向 / 左填充行 |
|---|---|---|---|---|---|---|---|---|
| rl_ans | 1 | 4 | 30.9 | 8.8 | 0.000 | 0.000 | 4.25 | 5 / 6 |
| rl_blind | 1 | 4 | 28.9 | 8.4 | 0.000 | 0.250 | 1.75 | 1 / 2 |
| rl_v4 | 1 | 4 | 30.8 | 8.8 | 0.000 | 0.000 | 4.25 | 5 / 6 |
| rl_v5 | 1 | 4 | 30.9 | 8.8 | 0.000 | 0.000 | 4.25 | 5 / 6 |
| rl_v5_placebo | 1 | 4 | 31.6 | 8.8 | 0.000 | 0.000 | 4.25 | 5 / 6 |
| smoke_full_hf | 3 | 192 | 126.1 | 16.4 | 0.010 | 0.182 | 2.74 | 51 / 504 |
| smoke_full_vllm | 3 | 192 | 50.1 | 23.7 | 0.010 | 0.167 | 1.80 | 72 / 504 |
| resume | 2 | 12 | 17.2 | 8.8 | 0.000 | 0.000 | 2.92 | 5 / 6 |

## Google Drive（可选；rclone，见 `drive_probe.json`）

- 结论：不可用或未通过：rclone is not on PATH (Drive persistence needs the rclone CLI, not only the mount)
- rclone：未安装；远端 `mydrive:` 已配置：否；挂载点 `/content/mydrive` 存在：否

## 冻结的运行时决策（`frozen_runtime.json`）

- 生成后端 vllm；微批 8；ViT 缓存 False；梯度检查点 True
- 理由：micro-batch 8: measured fwd+bwd peak 18.0 GB <= 80% of 42.4 GB
- 理由：generation vLLM: smoke passed, 50.1s/step vs HF 126.1s/step (<= 0.7x)
- 理由：frozen-ViT cache off: ViT is 0.4182 of a forward pass, cached-vs-uncached max |dlogp| = 0.40537071228027344
