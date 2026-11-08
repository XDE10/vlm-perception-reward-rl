# configs/ 目录说明

这里只放**当前执行配置**。历史配置保留在
[docs/blueprints/configs/](../docs/blueprints/configs/)（溯源用，可能包含旧
绝对路径，不可直接执行）。

| 文件 | 阶段 | 说明 |
| --- | --- | --- |
| `project3_fact_sft_smoke.json` | 感知事实 SFT | 固定 Qwen2.5-VL-3B-Instruct revision，2 步工程 smoke，LoRA，输出 `runs/strict_v8_project3_perception_sft_smoke` |
| `project3_sparse_v4_grpo_smoke.json` | 稀疏 GRPO | 从 SFT merged 权重起跑，2 步 smoke，感知奖励 + `math_verify` |

## 约定

- 路径一律相对仓库根目录（`data/...`、`runs/...`），不写绝对路径和
  Windows 盘符；`verify_migration.py` 会检查 `data_manifest`、`tokenizer_path`、
  `tokenizer_audit` 的相对性，以及 `model/output_dir` 不是绝对路径。
- 模型身份固定为 `Qwen/Qwen2.5-VL-3B-Instruct`，revision
  `66285546d2b821cf421d4f5eb2576359d3770cd3`；换模型或 revision 必须同步更新
  数据 manifest、tokenizer 审计和报告，不能只改配置。
- 这些是工程默认超参数（2 步、小 batch），**不是**已验证的最优设置；真实
  训练前先完成 [docs/training.md](../docs/training.md) 中的 GPU 验收清单。
- 新实验使用新的配置文件而不是就地改 smoke；改完运行
  `python tools/verify_migration.py` 与相关测试。
