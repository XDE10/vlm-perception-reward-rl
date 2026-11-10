# Colab 运行摘要：v0-20261110T023008Z-60fc（v0）

总体结论：**通过**

## 步骤

| 步骤 | 状态 | 用时（秒） | 计入结论 |
|---|---|---|---|
| env_report | passed | 2 | 是 |
| verify_pack | passed | 0 | 是 |
| pytest | passed | 171 | 是 |
| public_sources | passed | 4 | 是 |
| eval_sets | passed | 14 | 是 |
| cfgeo_build | passed | 13 | 是 |
| prompt_select | passed | 760 | 是 |
| v0_val82 | passed | 467 | 是 |
| harness_check | passed | 329 | 是 |
| vllm_env | passed | 26 | 否 |
| is_check | passed | 291 | 否 |
| decide_s3 | passed | 0 | 是 |

## 检查

- ✅ 评测集规则在 VM 上复现了提交的定义（eval_sets.json）
- ✅ 全部 CF-Geo 图像由补丁重建，像素哈希一致
- ✅ 评测代码路径检查通过（train 输入，五种条件与统计）
- ✅ S3 决策完整（s3_decisions.json，输入检查全部通过）
- ✅ pytest 无失败
- ✅ 私有数据与锚点一致

## 环境

- GPU：NVIDIA A100-SXM4-40GB，42.41 GB；驱动 580.82.07
- torch 2.13.0+cu130（CUDA 13.0，后端 cu130），transformers 5.19.0，trl 1.17.1，peft 0.21.2
- 模型：Qwen/Qwen2.5-VL-3B-Instruct@66285546d2b8

## CPU 测试（VM 上，GPU 已隐藏）

276 项：265 通过，0 失败，0 错误，11 跳过（168.3 秒）

## GRPO 冒烟

| 运行 | 步数 | rollout 数 | 步时中位数（秒） | 峰值显存（GB） | 答案正确 | 格式 | 每条断言数 | 对齐检查：前向 / 左填充行 |
|---|---|---|---|---|---|---|---|---|
| is_check | 3 | 192 | 47.1 | 23.2 | 0.016 | 0.146 | 1.65 | 72 / 504 |

## S3 决策（`s3_decisions.json`，规则见 S3 设计第 6 节，只用 train 测量）

- 提示：**P1**（P1 相对 P0：格式率 +0.363，答案准确率 +0.027；64 道 train 题）
- 格式预热：不需要（选定提示在温度 1.0 下的格式率 0.531，阈值 0.50）
- 生成长度上限：1024（写完 `</answer>` 的补全 215 条，第 95 百分位 361）
- S4 生成后端：**vllm**（重要性采样检查通过）
- 分辨率：max_pixels 保持 802816；会被缩小的评测图 validation 0/300、test 0/601

| 步 | 平均权重 | 每 token log-prob 差（平均 / 最大） |
|---|---|---|
| 1 | 1.000 | 0.0647 / 3.22 |
| 2 | 0.997 | 0.0614 / 2.75 |
| 3 | 0.998 | 0.0677 / 4.43 |

## 提示选择的测量（64 道已批准 train 题，每题 4 个温度 1.0 样本 + 1 个贪心）

| 提示 | 格式率（采样） | 答案准确率（采样） | 写到上限 | 写完 `</answer>` 条数 / p95 | 答案奖励有差别的题 | 格式率（贪心） | 答案（贪心） |
|---|---|---|---|---|---|---|---|
| P0 | 0.168 | 0.016 | 0.012 | 82 / 415 | 4 / 64 | 0.141 | 0.016 |
| P1 | 0.531 | 0.043 | 0.000 | 215 / 361 | 11 / 64 | 0.469 | 0.031 |

## V0 诊断（validation 82 题，贪心；只测量，不用于任何决策）

| 条件 | 答案正确 | 三段协议完整 | 格式奖励 | 写到上限 | 重复循环 | 失败类别 |
|---|---|---|---|---|---|---|
| P0 有图 | 0.024 | 0.159 | 0.159 | 0.598 | 40 | facts_without_tags 39，perception_only 16，complete 13，perception_and_think_no_answer 11，answer_but_malformed 2，no_tags 1 |
| P0 无图 | 0.049 | 0.476 | 0.451 | 0.439 | 30 | complete 39，perception_and_think_no_answer 23，perception_only 12，facts_without_tags 3，no_tags 3，answer_but_malformed 2 |
| 只要答案，有图 | 0.134 | 0.000 | 0.000 | 0.049 | 0 | answer_but_malformed 52，no_tags 26，other 4 |

## 评测输入（不运行模型）

- 评测集定义：与提交的 eval_sets.json 完全相同；test 视觉必需 388 题，CF 候选 224 题
- `cfgeo.json`：158/158 题由补丁重建，像素一致
- `cfgeo_dev_train.json`：40/40 题由补丁重建，像素一致

## 评测代码路径检查（只用 train；V0 的数字只说明代码能跑）

| 条件 | 题数 | 答案正确 | 写到上限 |
|---|---|---|---|
| e1_original | 16 | 0.000 | 0.750 |
| original | 32 | 0.031 | 0.594 |
| blind | 32 | 0.000 | 0.344 |
| swap | 32 | 0.000 | 0.688 |
| cf_k1 | 32 | 0.062 | 0.562 |
| cf_k2 | 32 | 0.031 | 0.562 |
- original_vs_blind：差 0.031，95% 区间 0.000–0.094，p = 1.0000（32 个图簇）
- cf_k2_vs_cf_k1：差 -0.031，95% 区间 -0.094–0.000，p = 1.0000（32 个图簇）
- 检查：e1_scored ✅，all_conditions_complete ✅，blind_has_no_image ✅，swap_shows_other_images ✅，cf_k2_old_answer_measured ✅，statistics_ran ✅

## 结果推送到 GitHub（D37）

- 由 VM 直接推送到 `results/v0-20261110T023008Z-60fc`（运行开始时已用 dry-run 验证写权限）
