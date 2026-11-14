# D66 训练完成与 S5 终评进展

快照时间为 2026-11-14 11:38（UTC+8）。S4 的 12 个正式任务已经完成。S5 终评仍在 A100 上运行，Drive 有 21/117 个正式预测条件的 `VERIFIED.json`。截至快照，尚无九项主比较的完整报告。

## S4 正式矩阵

| 组别 | 完成种子 | 步数 |
| --- | --- | --- |
| `rl_v5` | 1、2、3 | 各 228 |
| `rl_ans` | 1、2、3 | 各 228 |
| `rl_v4` | 1、2 | 各 228 |
| `rl_v5_placebo` | 1、2 | 各 228 |
| `rl_blind` | 1、2 | 各 228 |

按 [D66 登记表](../../configs/experiments/s4_runs_20261110.json) 核对了 12 个 Drive 完成标记的运行名、步数、配置哈希、运行时哈希及 final adapter 文件记录。最后一项 `rl_v5/seed3` 从已核对的第 114 步 checkpoint 恢复，第 115 步继续，完成第 228 步并写入 Drive。两个可选 `rl_v5_groupnorm` 种子未运行。见 [最后一轮训练报告](https://github.com/XDE10/vlm-perception-reward-rl/tree/bf61109/reports/colab_runs_20261113/train-20261113T180946Z-8ea4)。

`rl_v5/seed1` 的 D66 产物已独立验签，旧配置的同名产物保存在独立归档。`rl_v5/seed2` 从第 38 步恢复，第 39 步续跑。此前的 rollout 审计显示，D66 主组 seed1 的前后各 38 步中，合规全 UNKNOWN 从 88/2,432（3.62%）升至 564/2,432（23.19%），历史旧版对应窗口为 3.91% 和 35.53%。训练日志中显式空块极少。UNKNOWN 包含认证范围之外的事实，计数只能描述输出行为。见 [前一轮复核](../s4_review_snapshot_20261113/README.md) 和 [rollout 审计](../s4_rollout_audit_20261112/README.md)。

## S5 正式终评

评测固定在运行提交 `2bc87709bc30578441b7c08f38e0477b96002b26`，使用 P1、HF greedy、1024 个新 token 和 batch size 32。V0 加 12 个正式 adapter，共 13 个模型。每模型生成 9 个条件共 3,747 条预测，计划合计 117 个条件、48,711 条。S5 主终点是 val82 认证感知指标、CF-Geo k=2 答案准确率和 Geometry3K 视觉必需子集 test_vn 准确率，主比较共 9 项，使用图簇配对统计和 Holm 校正。全量 Geometry3K test601 与 MathVista 是次要指标。见 [S3 冻结评测设计](../../docs/plan/S3设计_20261109.md) 和 [S5 运行入口](../../scripts/colab/final_eval.py)。

| 模型 | Drive 已标记的条件 |
| --- | --- |
| V0 | 9/9 |
| `rl_v5/seed1` | 9/9 |
| `rl_ans/seed1` | 3/9，val82、test_vn、test_original |
| 其余十个 adapter | 0/90 |

首两次 S5 会话中断后，续评复用通过校验的既有预测条件。当前作业 `final-eval-20261114T021649Z-c912` 已进入 `rl_ans/seed1` 的无图条件。11:26 本地启动器中断，远端推理继续运行，11:37 已重新连接监控。进度数以 Drive 持久化条件为准。完整准确率、相对对照的提升、区间和校正后 p 值待终评汇总。

## Shuffle-R1 单卡对照

使用官方仓库提交 `b863694f25d38d0e118761363dc5897bb9625e82` 的题集加载、图像预处理、提示和 MathRuler 判分，在一张 G4 上对 test601 按温度 0.5、2048 个新 token、种子 0–7 复测。原始 3B revision 为 `66285546d2b821cf421d4f5eb2576359d3770cd3`，公开 Shuffle-R1 3B revision 为 `1ce00fe544ce3b23e686b58094c8f3132700ecdf`。每个模型每种设置均为八轮独立的 pass@1 取均值。来源见 [作者仓库](https://github.com/xiaomi-research/shuffle-r1/tree/b863694f25d38d0e118761363dc5897bb9625e82) 和 [公开 3B 权重](https://huggingface.co/XenoZLH/Shuffle-R1-Qwen-3B/tree/1ce00fe544ce3b23e686b58094c8f3132700ecdf)。

| 设置 | 原始 3B | 公开 Shuffle-R1 3B |
| --- | --- | --- |
| 单卡 G4，vLLM V1 / FlashAttention | 24.44% | 41.20% |
| 单卡 G4，vLLM V0 / XFormers（因 G4 兼容性关闭 FA3） | 24.69% | 41.14% |

论文 Geo3K 训练实验表 1 报告 47.88%。两种本地推理配置的公开权重结果相差约 0.06 个百分点，与论文仍分别相差约 6.68 和 6.74 个百分点。公开模型卡未确认权重与表 1 的对应关系。两套对照的逐种子汇总与评测协议见 [汇总 JSON](shuffle_r1_g4_aggregates.json)。逐题生成和判分保存在本地与项目 Drive。S5 使用单独的 P1 和判分协议，跨协议分数不能用于方法排名。见 [Shuffle-R1 论文 v6](https://arxiv.org/html/2508.05612v6)。

作者训练入口在 G4 上完成两次外层更新及 checkpoint 写入，保持 PTS、ABS、官方奖励和默认 CPU offload，冻结视觉塔并更新语言侧参数（无 LoRA）。日志记录权重同步峰值约 87.81 GiB，最终包含模型和优化器的 checkpoint 约 38.2 GiB。冒烟仅证明单卡能完成短训练和保存。完整训练时长、收敛效果和 47.88% 的复现仍待验证。

本报告依据既有训练报告、Drive 标记、当前 S5 日志及 Shuffle-R1 本地复测记录。编写报告期间未启动额外 GPU 实验。
