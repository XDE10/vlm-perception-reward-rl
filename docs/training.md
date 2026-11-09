# 训练与诊断入口

本页给出环境、配置和命令。**当前没有 GPU 训练产物**，所有 GPU/CUDA 行为仍未验收。
历史 CPU 通过与 ZIP 完整性不能证明真实 VL 前后向或视觉 rollout 可用。

## 协议 v3 统一入口（2026-11-09 起的正式实验）

所有实验组共用一个入口和一份基础配置，组别只改白名单字段（见
[configs/README.md](../configs/README.md)）：

```bash
python -m scripts.training.train_rl --arm rl_v5 --seed 1 \
  [--runtime runs/frozen_runtime.json] [--model-path <本地固定 revision 快照>] [--resume <checkpoint>]
```

- 组别与种子登记在 `configs/experiments/arms.json`：`rl_ans`（答案 + 格式）、`rl_v4`、`rl_v5`、
  `rl_v5_placebo`、`rl_blind`，以及可选的 `rl_v5_groupnorm`。
- 输出 `runs/rl_v3_20261109/<组>/seed<k>/`：`rollouts.jsonl`（逐条 rollout、答案判定、v4/v5 明细、
  加权奖励）、`run_identity.json`（配置哈希、包版本、源码与数据 SHA、运行时决策）、
  `trainable_parameters.json`、`checkpoint-*`、`final/`（LoRA adapter）、`train_summary.json`。
- 已有 checkpoint 的目录拒绝重跑；`--resume` 要求运行身份完全一致，否则失败。
- `--smoke` 只用于工程检查（例如 `max_steps=2,num_generations=2,prompts_per_step=2,per_device_train_batch_size=2`），
  会记录在运行身份里，不能用于报告结果。
- `--runtime` 指向预检冻结的 `frozen_runtime.json`。其中只有不改变算法的选项（生成后端、微批切分、
  梯度检查点、ViT 缓存）；出现其他键时入口直接报错。
- CPU 开发与测试环境见 [requirements/dev-cpu.txt](../requirements/dev-cpu.txt)。

## 在 Colab 上运行（S2 起）

在 WSL2 中运行 `bash colab/launch.sh check`，然后 `bash colab/launch.sh preflight`，详见
[colab/README.md](../colab/README.md)。运行器会建 VM，上传当前提交的代码和经过校验的私有数据，按驱动的 CUDA
版本从 [requirements/locks/](../requirements/locks/) 选锁文件建隔离环境，下载固定 revision 的模型，运行任务，
取回结果并释放 VM，最后把结果推到 `results/<run_id>` 分支。

预检（`preflight`）依次执行：

1. 环境报告与私有数据复核。
2. 完整 CPU 测试套件（在 VM 上运行，隐藏 GPU）。
3. 在全部认证事实上做 v5 阈值校准。
4. 真实 3B 权重的 GPU 探针：LoRA 范围、提示长度、峰值显存、生成吞吐、ViT 缓存等价性。
5. V0 小探针：16 道 validation，有图与无图各一遍。
6. 五个实验组各跑 1 步 GRPO。
7. 按正式形状（8 题 × 8 条）跑 3 步，测步时与显存。
8. 断点恢复。
9. 可选的 vLLM 对比。
10. 冻结运行时决策（`frozen_runtime.json`）。

决策规则见 [决策记录](plan/决策记录.md) D20–D27。

以下是旧入口（感知 SFT → 稀疏 GRPO）的说明，作为历史保留。

## 环境

| 环境 | 事实 |
| --- | --- |
| 本机 CPU 检查（2026-11-08） | Python 3.11.4，pip 25.1.1，pytest 8.3.5，已装 torch/transformers；**未装** `trl`、`math_verify`。项目文档记载的历史 CPU 验证使用 Python 3.12，本机未复验。 |
| 目标 GPU | 未验收。需要与驱动匹配的 PyTorch/CUDA 和 TRL/PEFT/Accelerate 版本，自行固定并做 import/API 验收。 |

[requirements/cpu-snapshot.txt](../requirements/cpu-snapshot.txt) 是旧 CPU 环境
的包版本记录，**不是锁文件**；[requirements/project3-cpu.txt](../requirements/project3-cpu.txt)
是项目三 CPU 审计/测试的参考依赖。二者都不覆盖 CUDA 安装。GPU 环境请单独
固定版本，不能据 CPU 包安装成功宣称 GPU 可运行。

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS:        source .venv/bin/activate
python -m pip install -r requirements/cpu-snapshot.txt
```

## 配置

| 文件 | 阶段 | 关键参数 |
| --- | --- | --- |
| [configs/project3_fact_sft_smoke.json](../configs/project3_fact_sft_smoke.json) | 感知 SFT | 2 步、`learning_rate=2e-5`、LoRA rank 16、BF16、`max_length=3800`、`max_pixels=802816`、`output_dir=runs/strict_v8_project3_perception_sft_smoke` |
| [configs/project3_sparse_v4_grpo_smoke.json](../configs/project3_sparse_v4_grpo_smoke.json) | 稀疏 GRPO | 从 SFT merged 权重起跑、每题 4 条回答、最多 2048 生成 token、`beta=0.04`、感知奖励权重 0.2 |

两份配置都使用相对路径，必须从仓库根目录执行；模型固定为
`Qwen/Qwen2.5-VL-3B-Instruct` revision
`66285546d2b821cf421d4f5eb2576359d3770cd3`。这些值是工程默认，不是已验证的
最优超参数。

## 命令

```bash
# 1) 感知 SFT（需要 GPU；预期输出 runs/strict_v8_project3_perception_sft_smoke/merged/）
python -m scripts.training.train_project3 --config configs/project3_fact_sft_smoke.json

# 2) 稀疏 GRPO（依赖上一步实际导出的 merged 权重与身份清单）
python -m scripts.training.train_project3 --config configs/project3_sparse_v4_grpo_smoke.json

# 3) 固定 validation 视觉诊断（先建输出目录；默认诊断原始 VL 模型）
python -c "from pathlib import Path; Path('runs').mkdir(exist_ok=True)"
python -m scripts.training.diagnose_project3_vision \
  --data data/portable_release/project3_validation_fact_pruned.jsonl \
  --output runs/vision_validation_diagnostic.jsonl
```

诊断脚本对同一批固定 ID 生成原图、无图、黑图、中央遮挡条件。无图条件会真正
移除 image 与视觉占位；中央遮挡只是输入扰动，不能当作几何真值测试。检查训练
后模型时按脚本接口显式传入 adapter/模型身份。

GRPO 的数学检查通过子进程
`python -m scripts.training.math_verify_v3_strict_worker` 调用 pip 包
`math_verify`（未列入 requirements 快照，属于既有事实）。目标环境需实际安装，
否则相关奖励检查会失败。

## 输出与恢复

- SFT 输出：`runs/strict_v8_project3_perception_sft_smoke/merged/`（本次迁移包不含）。
- RL 输出：配置中的相对 `output_dir`；`runs/` 被 git 忽略。
- 重新实验使用新的输出目录；恢复训练必须核对完整 checkpoint 身份与优化器
  状态，不能只加载 adapter 就声称恢复。
- 当前入口检查单张可见 GPU，不能当作多卡配置。

## GPU 验收清单（尚未执行）

1. 在真实 GPU 加载固定 revision 的 VL 模型/processor，检查图像 token 数与
   chat template。
2. 取最长图片+题目做前后向，检查 assistant mask、损失/梯度有限、峰值显存。
3. 保存/恢复 SFT checkpoint，导出 merged 权重并核对身份清单。
4. 验证稀疏 GRPO 的奖励接线、视觉 rollout 与 `math_verify` 子进程可用。
5. 对固定 validation 建立原图/无图/黑图/遮挡的 V0 基线，再谈 V0～V4 对照。

每一步都要记录配置、数据/模型身份、原始预测、评分版本、恢复记录、显存和成本；
“已实现代码”“CPU 通过”“真实模型跑通”“能力提升”必须分开陈述。
