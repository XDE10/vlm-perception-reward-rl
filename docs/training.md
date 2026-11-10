# 训练与诊断入口

本页给出环境、配置和命令。**当前没有正式训练产物**。S2 预检与 S3 `v0` 已在 A100 上通过
（环境、数据核对、3 步 GRPO 冒烟、断点恢复、V0 诊断），这只证明工程链路可用，不代表正式训练成功或能力提升。
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

## S4 正式任务（登记运行）

配置、奖励、损失、终止判据和运行顺序见 [S4 预注册](plan/S4预注册_20261110.md)。正式任务一律这样启动：

```bash
python -m scripts.training.train_rl --registered configs/experiments/s4_runs_20261110.json --arm rl_v5 --seed 1 --model-path /content/p3/models/Qwen2.5-VL-3B-Instruct@66285546d2b8
```

- 这条命令由 Colab 上的 `train` 任务执行，不需要你手动运行；`--model-path` 是 VM 引导时下载的固定 revision 快照。
  从 checkpoint 恢复时再加 `--resume runs/rl_v3_p1_20261110/rl_v5/seed1/checkpoint-38`（运行身份必须一致）。
- 实验配置（`rl_v3_p1_20261110.json`，提示 P1）、组别表和冻结运行时都取自登记表；`--smoke`、`--output-dir`、
  不同的 `--experiment` 或 `--runtime` 会被拒绝。
- 加载模型前核对：完整配置哈希、609 行批准训练数据、三个数据文件的 SHA256、GPU 为 NVIDIA A100-SXM4-40GB。
  任何一项不同就停止；结果写进 `train_summary.json` 的 `registration`。
- 输出 `runs/rl_v3_p1_20261110/<组>/seed<k>/`，每 38 步一个 checkpoint，第 228 步后写 `final/`。
  loss 或梯度范数出现 NaN/inf 时立即停止，不再写 checkpoint 和 `final/`。
- 登记表的派生字段由 `python -m scripts.training.register_runs --write` 生成；改动任何实验配置后先运行 `--check`。
  `--show rl_v5 1` 打印一个任务合成后的完整配置。
- 在 Colab 上的 `pilot` 与 `train` 任务（试跑、Drive 上的 checkpoint 与恢复）在下一个 PR 中实现。

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

S3 的 `v0` 任务（`bash colab/launch.sh v0 --session p3`，只在 A100 40/80 GB 或 H100 上运行）依次执行：

1. 环境报告、私有数据复核、完整 CPU 测试套件。
2. 下载固定版本的公开数据并按 `migration_manifest.json` 核对；按预注册规则重建评测集定义，要求与提交的完全相同；
   由补丁重建全部 CF-Geo 图像并核对像素。这一步不运行模型。
3. 在 64 道已批准 train 题上测量提示 P0 与 P1、格式预热和生成长度。
4. V0 在 82 道 validation 上的贪心诊断（只测量）。
5. 用 train 输入走一遍 S5 的评测代码。
6. 用冻结的运行时跑 3 步 vLLM GRPO，检查重要性采样权重（D41）。
7. 按 [S3 设计](plan/S3设计_20261109.md) 第 6 节的规则写出 `s3_decisions.json`。

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
