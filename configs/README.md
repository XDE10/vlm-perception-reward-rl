# configs/ 目录说明

这里只放**当前执行配置**。历史配置保留在
[docs/blueprints/configs/](../docs/blueprints/configs/)（溯源用，可能包含旧
绝对路径，不可直接执行）。

## experiments/（2026-11-09 起的正式实验）

| 文件 | 说明 |
| --- | --- |
| `experiments/rl_v3.json` | 协议 v3 GRPO 的基础配置：固定模型 revision、数据入口、LoRA、训练预算、奖励权重、v5 几何阈值 |
| `experiments/arms.json` | 实验组覆盖表与种子登记。组别只能覆盖 `allowed_overrides` 中的字段（感知奖励类型与权重、训练时是否有图、元数据来源、奖励标准化方式） |
| `experiments/runtime_frozen_20261109.json` | 第三次预检（`preflight-20261109T122305Z-e6cd`）冻结的运行时：vLLM 生成、微批 8、ViT 缓存关闭、梯度检查点开启，附测量值与来源。只含不改变算法的字段；只用于 A100 40/80 GB 和 H100（D43）。vLLM 重要性采样的设置属于算法，写在 `rl_v3.json`（D41） |

运行方式：`python -m scripts.training.train_rl --arm <组名> --seed <种子>`。入口把基础配置、
组别和种子解析成一份完整配置，并把哈希写进运行身份文件；`tests/test_experiment_configs.py`
保证任意两组只在声明的因素上不同。设计理由见
[决策记录](../docs/plan/决策记录.md) D7、D10。

## 历史入口配置

| 文件 | 阶段 | 说明 |
| --- | --- | --- |
| `project3_fact_sft_smoke.json` | 感知事实 SFT | 固定 Qwen2.5-VL-3B-Instruct revision，2 步工程 smoke，LoRA，输出 `runs/strict_v8_project3_perception_sft_smoke` |
| `project3_sparse_v4_grpo_smoke.json` | 稀疏 GRPO | 从 SFT merged 权重起跑，2 步 smoke，感知奖励 + `math_verify` |

这两份配置属于旧入口 `scripts.training.train_project3`。2026-11-09 只修复了该入口中
LoRA 误入 ViT 和 transformers 5 不兼容两处缺陷，超参数不变；新实验不再使用。

## 约定

- 路径一律相对仓库根目录（`data/...`、`runs/...`），不写绝对路径和
  Windows 盘符；`verify_migration.py` 会检查 `data_manifest`、`tokenizer_path`、
  `tokenizer_audit` 的相对性，以及 `model/output_dir` 不是绝对路径。
- 模型身份固定为 `Qwen/Qwen2.5-VL-3B-Instruct`，revision
  `66285546d2b821cf421d4f5eb2576359d3770cd3`；换模型或 revision 必须同步更新
  数据 manifest、tokenizer 审计和报告，不能只改配置。
- 旧入口的两份 smoke 配置是工程默认超参数，**不是**已验证的最优设置。
- 新实验使用新的配置文件而不是就地改已登记的配置；改完运行
  `python tools/verify_migration.py` 与相关测试。
