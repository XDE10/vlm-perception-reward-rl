# Shuffle-R1 单卡 G4 复现：本地项目审查与上卡路线

**审查时间：** 2026-11-15（本机 WSL Ubuntu）  
**目标 GPU：** Colab G4 / NVIDIA RTX PRO 6000 Blackwell Server Edition，96 GB  
**结论：** 代码方向已经进入可验证阶段，但目前不应直接启动完整训练。下一步应先完成隔离开发副本的依赖化 CPU 回归，再进行有硬停止条件的 G4 首轮探针；不能把它与主项目既有 S4/S5 任务混为一谈。

## 1. 最重要的结论（先看）

1. 指定的项目根目录 `~/projects/vlm-perception-reward-rl` 当前位于 `master`，HEAD 为 `2bc8770`，报告创建前工作树干净（`## master...origin/master`；当前仅新增本报告目录）。它是 VLM 感知奖励 RL 项目，不是 Shuffle-R1 官方训练代码仓库；当前唯一新增未跟踪项是本报告目录。当前主项目不能直接运行 `python -m shuffle_r1.main`。
2. 最新对话中所修改的 Shuffle-R1 代码实际位于另一个隔离副本：`~/.local/state/vlm-perception-reward-rl/shuffle-r1-g4-dev`。其分支为 `g4-logical-batch-prep-20261115`，基于官方 `xiaomi-research/shuffle-r1`，HEAD `b863694`。该副本有 12 个已修改跟踪文件、2 个新模块和一组新测试，尚未提交；不能误以为这些改动已经合入主项目根目录。
3. 最新对话所述的 CPU 阶段工作与当前文件相符：分块 rollout 已写进实际入口使用的 `shuffle_r1/fsdp.py`；`shuffle_r1/main.py` 确实 import 该 worker，而不是 `verl/workers/fsdp_workers.py`。同时实际 actor 更新路径 `verl/workers/actor/dp_actor.py` 已加入参考微批的顺序与 token 权重模拟。
4. 我在当前本机环境重新执行了最独立的几何测试：`10 passed in 0.03s`；`git diff --check` 无输出（通过）。但当前 WSL 的 `~/.venvs/p3-dev` 缺少 `ray`、`omegaconf`、`torchdata`、`codetiming`，系统 Python 也没有 pytest。因此本轮**无法独立重跑全部 36 项 CPU 测试**。对话记录声称 36 项通过，不能替代本轮环境复验。
5. Colab 当前没有活动会话，`colab usage` 显示余额 **472.55 CU**、费率 0.00/hr（无活动 GPU）。尚未启动任何新 GPU 会话，也未消耗本轮 G4 训练预算。
6. 因此建议顺序是：**补齐并复验 CPU 测试 → 冻结代码与数据身份 → G4 45 分钟首轮探针 → 根据真实显存/吞吐决定 B512 → 同预算 PTS 对照 → 再决定完整训练**。不要跳过首轮探针，也不要先启动 20-epoch 训练。

## 2. 两个目录的边界（不能混淆）

| 目录 | 当前状态 | 作用 |
|---|---|---|
| `~/projects/vlm-perception-reward-rl` | `master@2bc8770`，干净 | 你指定的主项目：感知奖励 RL、S4/S5 评估与实验记录 |
| `~/.local/state/vlm-perception-reward-rl/shuffle-r1-g4-dev` | `g4-logical-batch-prep-20261115@b863694`，有未提交改动 | Shuffle-R1 官方源码的单卡适配开发副本 |

主项目的 `docs/training.md`、`docs/plan` 与 `colab/README.md` 记录的是另一条实验协议：Qwen2.5-VL-3B、S4 多组训练、S5 P1 评估，运行器默认要求 A100-SXM4-40GB。它们不是 Shuffle-R1 的 B512/n=16/PTS+ABS 配置。

主项目最近一次 S5 运行记录（`~/.local/state/vlm-perception-reward-rl/d66-finish/pause-20261115`）显示：2026-11-15 16:53:51 +08:00 已保存并释放运行时；Drive 已核验 67 个条件；当前保存点为 `rl_ans/seed2/test_blind`，已完成 544/601。该评估任务是暂停/保存状态，不是 Shuffle-R1 训练任务。**不要在恢复或清理 S5 时覆盖它的 Drive 状态或结果。**

## 3. 本轮实际检查证据

### 3.1 主项目

- `git status --short --branch`：`## master...origin/master`，无工作树改动。
- 最近提交：`2bc8770 Merge pull request #11 from XDE10/stage5/report`。
- 项目文档明确写明 S4/S5 的模型、数据、运行器和评估任务；S5 最新运行快照如上。
- 当前本机 `nvidia-smi` 不存在；这台 WSL 不是 G4 训练 VM。G4 必须由 Colab CLI 申请。

### 3.2 Shuffle-R1 开发副本

- Git 分支：`g4-logical-batch-prep-20261115`。
- 上游 remote：`https://github.com/xiaomi-research/shuffle-r1.git`。
- HEAD：`b863694 Update README title for ICLR 2026 paper`。
- `git diff --stat`：12 个跟踪文件，595 insertions / 98 deletions；另有 `shuffle_r1/single_gpu.py`、`shuffle_r1/checkpoint.py` 和 `tests/` 未跟踪。
- `git diff --check`：无空白错误。
- 训练入口 `shuffle_r1/main.py` 中实际导入：`from .fsdp import FSDPWorker`。
- 分块 rollout 已在 `shuffle_r1/fsdp.py::FSDPWorker.generate_sequences`；一次逻辑批次在一个 sharding-manager scope 内分块生成，分块输出先移到 CPU 再 concat。
- 训练器 `shuffle_r1/ray_trainer.py` 在 rollout 前记录 `policy_version`，并在逻辑批次结束时检查版本；同一批物理分块必须来自同一策略版本。
### 3.3 逻辑批次与更新语义

开发副本中的 `derive_batch_geometry` 和测试给出的 B512/G128/n=16/purning=0.5 形状为：

| 项目 | 8-rank 作者参考形状 | 单卡逻辑模拟 |
|---|---:|---:|
| 逻辑 prompts | 512 | 512 |
| 每题 rollout | 16 | 16 |
| 候选轨迹 | 8,192 | 8,192 |
| PTS 后保留轨迹 | 4,096 | 4,096 |
| PTS pair 数 | 2,048 | 2,048 |
| 每 rank actor batch | 128 | 虚拟 rank 每份 128 |
| 每 rank 保留样本 | 512 | 虚拟 rank 每份 512 |
| 每 outer step optimizer updates | 4 | 4 |
| 参考微批 | 4 | 参考微批 4，物理微批 1 |
| ABS replay | 8 次 | 8 次 |

单卡物理实现必须把完整逻辑批次拆开生成，但不能把每个物理 chunk 当成一个独立 RL batch：所有 chunk 必须由同一份策略权重生成；完整 8,192 条轨迹收齐后再统一计算 PTS/ABS；保留原作者每次 optimizer update 的样本分组、参考 rank/microbatch 排列和 token-loss 权重。单纯把 microbatch 改成 1 然后对 micro loss 做普通平均，不等价于 8-rank DDP。

`reference_layout_indices` 重建了 8 个参考 rank 的分组顺序；`dp_actor.py` 的 reference microbatch 分支按每个参考微批的有效 response token 数加权，并把 1 条样本的物理 microbatch 梯度累积到对应 optimizer step。现有固定轨迹 CPU 测试用 8-rank 独立参考实现对比 old log-prob、梯度范数、更新后权重和 AdamW 状态。这是当前最重要的语义保护。

### 3.4 ABS 失败边界

当前测试和实现按作者的无放回加权抽样约束 fail closed，不会用 uniform-fill 偷偷补样本。B512/G128/n16/保留率 0.5 时，每次 ABS replay 的抽样大小是 256 个 pair，因此正权重 pair 支持数至少必须达到 256；低于 256 必须报错并停止该逻辑步。这个限制应保留为运行时硬检查，不能为了让训练继续而放宽。

### 3.5 Checkpoint / RNG

新模块 `shuffle_r1/checkpoint.py` 提供配置、源码、模型 revision、train/dev 文件身份哈希和逐文件 SHA256 manifest；`ray_trainer.py` 保存 driver RNG、dataloader state、优化器/调度器步数；实际 `shuffle_r1/fsdp.py` 的 worker 保存 actor/rollout CUDA RNG。恢复时先验证身份与文件完整性，再加载；缺文件、损坏或身份不符应拒绝恢复。

当前测试覆盖连续运行与恢复后下一批数据、ABS 抽样、随机数、模型/优化器/调度器状态的一致性，以及写入/rename/tracker 更新过程的故障注入。注意：这些是 CPU mock / 真实训练器方法组合的恢复测试，不等于已证明真实 Colab VM、vLLM 子进程和 G4 FSDP 的 checkpoint 生命周期正确。

## 4. CPU 测试复验状态

| 检查 | 本轮结果 | 解释 |
|---|---|---|
| `git diff --check` | PASS | 开发副本无 whitespace errors |
| `tests/test_single_gpu_geometry.py` | **10 passed** | 本轮在 `~/.venvs/p3-dev` 中实际运行 |
| 完整 5 个单卡测试模块 | BLOCKED | 当前环境缺 `ray`、`omegaconf`、`torchdata`、`codetiming`；系统 Python 缺 pytest |
| 上轮对话记录 | 36 CPU tests passed | 这是前一轮执行记录；本轮不能独立重放全部结果 |
| CUDA / vLLM / FSDP 真实运行 | NOT RUN | 尚未申请 G4；当前 WSL 没有 nvidia-smi |

建议先在开发副本中用独立虚拟环境安装与上游一致的 CPU 测试依赖，再运行五个模块及完整测试集。不要把测试依赖装进主项目现有 `~/.venvs/p3-dev`，也不要用 `uv run --with torch` 让它临时解析未知的 CUDA wheel。测试环境应固定 Python、torch CPU wheel、ray、omegaconf、torchdata、transformers、pytest 等版本并记录 lock。

## 5. 与作者实现的差异和可复现目标

上游官方 README 明确：Shuffle-R1 提供 3B/7B checkpoint、数据集、训练与评估脚本；训练数据 MMRL30k 包含约 2.1k Geometry3K + 27k MM-EUREKA 样本；论文报告的训练使用 8×H800-80G。3B 脚本使用 Qwen2.5-VL-3B-Instruct、n=16、purning_ratio=0.5、PTS+ABS、20 episodes。作者没有报告单张 RTX PRO 6000 的直接训练结果。

因此“和 Shuffle-R1 保持一致，效果接近”应定义为：保持 3B backbone、作者 MMRL30k 数据、PTS/ABS 算法和 B512/G128/n16 的逻辑批次更新语义；单卡只改变物理执行方式（rollout chunk、物理 microbatch、显存 offload、checkpoint），不能把 512 prompts 改成 16 prompts 后把结果称作同等训练。首轮 B16 只作为工程探针，不是算法结果。

**尚未冻结的关键输入：** 开发副本是否已完整准备作者 MMRL30k 数据（图像 bytes/path、train/test split、数据 SHA）目前没有证据；其测试只引用 `examples/config.yaml` 并用假数据构造 DataProto。主项目的 609 行批准训练集不是 MMRL30k 的替代品，除非明确把目标改为“在自有数据上复现算法机制”，而不是作者数据设置的复现。
## 6. 建议的实施路线（按顺序，不跳步）

### 阶段 0：先把开发副本变成可重复的 CPU 构建

1. 仅在 `~/.local/state/vlm-perception-reward-rl/shuffle-r1-g4-dev` 内建立独立 venv；不要改主项目 `master`。
2. 按该 commit 的上游依赖约束安装 CPU 版本测试依赖，锁定版本并保存安装清单。
3. 重跑五个模块：`test_single_gpu_geometry.py`、`test_single_gpu_entry.py`、`test_single_gpu_semantics.py`、`test_single_gpu_update.py`、`test_single_gpu_checkpoint.py`；随后运行整个上游测试集。
4. 生成测试日志和 SHA256；如果完整测试失败，先修复，不申请 G4。
5. 审核 `git diff` 中每个改动，特别是 `shuffle_r1/fsdp.py`（实际 worker）、`ray_trainer.py`（logical batch/checkpoint）、`dp_actor.py`（loss weighting）、`config.py`（single GPU guard）。确认后再本地 commit，保留独立分支，不推送覆盖 upstream main。

### 阶段 1：冻结数据和模型身份

推荐以作者设置为主线：
- Model：`Qwen/Qwen2.5-VL-3B-Instruct`，固定 revision `66285546d2b821cf421d4f5eb2576359d3770cd3`。
- Dataset：`XenoZLH/MMRL30k`，需先下载、核对 train/test split、字段 `problem/images/answer/source`、图片 bytes/path、样本数和 SHA256。
- 训练：3B 脚本的 `n=16`、`purning_ratio=0.5`、PTS pairwise、ABS power/sum、replay=8、B512/G128、20 episodes 作为作者参考设置。
- 固定 prompt/system prompt、max prompt/response length、image min/max pixels、temperature、top_p、optimizer/LR、模型 revision、依赖锁和数据 hash；这些都写进 run manifest。
- 不允许用主项目的 609 行 S4 数据直接冒充 MMRL30k。若改用自有数据，实验命名和结论必须明确写成“Shuffle-R1 算法迁移到项目自有数据”。

### 阶段 2：G4 首轮 45 分钟工程探针（仅在阶段 0/1 通过后）

建议新建独立 session：`shuffle-r1-g4-probe`，GPU 选择 G4。第一笔最多 45 分钟，不做完整训练：
1. 环境自检：确认实际 GPU 名称为 NVIDIA RTX PRO 6000 Blackwell、显存约 96GB、CUDA/PyTorch/vLLM/FSDP/FlashAttention 可导入。
2. 下载固定 3B revision 和小份真实 MMRL30k 样本，做真实多模态 batch collate。
3. 固定轨迹 B16：实际跑一次 rollout chunking、PTS、actor update 和 strict checkpoint save/load；对比 chunk 与 no-chunk 的固定轨迹结果。
4. 记录峰值 allocated/reserved VRAM、GPU utilization、CPU RAM、生成 tok/s、每个 chunk 时间、完整 B16 时间、optimizer/scheduler step 数、checkpoint 文件清单和 SHA。
5. 完整退出并释放 G4；报告实际 CU 消耗。不要让 probe 进程在后台继续占用 GPU。

**45 分钟硬停条件：** 任一真实模型/图像加载失败、vLLM 与 FSDP 不能在同一 GPU 安全切换、chunk 输出顺序/元数据不一致、固定轨迹更新不匹配、checkpoint 无法读回、出现 NaN/Inf、显存 OOM 或预算到 45 分钟，立即停；不自动加时、不自动进入 B512。

### 阶段 3：B512 单个完整逻辑步

只有阶段 2 全部通过才做：
- 一个完整 B512/G128/n16 逻辑批次：生成 8,192 条 rollout；所有 chunk 收齐后统一 PTS/ABS；保留 4,096 条；执行作者对应的 4 次 optimizer updates；保存一次 checkpoint。
- 单独设预算上限（建议先 90 分钟，约 13.4 CU，按 8.9 CU/h 估算；实际以活动 session 的 `colab usage` 为准）。
- 重点记录每个 chunk 的时延、完整 rollout 时延、PTS/ABS 时延、old log-prob 时延、4 次更新时延、峰值显存、CPU RAM、checkpoint 大小。
- 只有实际完成完整 B512 且 optimizer_steps=4、scheduler_steps 与预期一致、ABS 支持数足够、checkpoint 恢复一致，才证明“单卡 B512 可运行”。配置解析通过不等于显存可行。

### 阶段 4：同预算 PTS 对照

- 从同一个冻结 checkpoint 和同一批冻结的首步 rollout 开始；两组必须读取完全相同的候选轨迹（逐行 hash 相同），不得重新采样或分别生成。
- 处理组：作者 pairwise PTS；对照组：同样每题保留 8/16 条的 uniform PTS。两组保持相同有效训练 token、样本行数、optimizer update 数、学习率和训练 token budget。
- 若比较“PTS 本身”，两组都关闭 ABS；若比较完整 Shuffle-R1，再单独加入 PTS+ABS 组。不要把“PTS vs PTS+ABS”称为纯 PTS 消融。
- 记录每组 GPU 秒、生成 tokens、训练 tokens、有效 pair 数、梯度范数、reward/accuracy、格式/解析失败率。先做一个冻结 batch 的机制验证，再做多 batch 的短程效果比较。
- 不能只用 GPU 时间相同却训练 token 不同的方式宣称同预算；应同时报告 wall-clock 与有效训练 token。

### 阶段 5：决定完整训练规模

作者 30k 数据、512 prompts/outer step、20 episodes 约为 `20 × ceil(30,000/512) ≈ 1,180` 个逻辑 outer steps（忽略最后一个 batch 的边界细节）。单卡是否能在当前 CU 余额内完成，不能凭 96GB 显存推断，必须用阶段 3 的真实 B512 wall-clock 外推：
`预计 CU = (B512 单步秒数 × 预计逻辑步数 + 验证/保存/环境开销) / 3600 × 实测 CU/h`。
只有预算内可完成并留有至少 20% 余量，才启动全量；否则选择清楚标注的短程/单 epoch实验，不能声称复现作者 20-episode 训练。

## 7. 算力预算和余额纪律

当前 Colab CLI 实测：余额 472.55 CU、无活动会话。第三方公开的 Colab 运行记录给出的 G4 参考费率约 8.9 CU/h（非 Google 官方保证，实际费率会随账号/时段变化）。据此：
- 45 分钟 probe ≈ 6.7 CU；
- 90 分钟 B512 单步探针 ≈ 13.4 CU；
- 当前 472.55 CU 按 8.9 CU/h 粗算约 53.1 小时总时长，尚未扣除其他用途和未来费率变化。
- 每次开卡前、运行中、结束后都读 `colab usage`；以活动 session 实际费率计算，保留至少 20% CU 作为中断恢复/最终评测余量。
- 不并行开多张卡；不让 session 空转；每个阶段达到预算或硬停条件即 `colab stop`。
- B512 完整训练的成本在真实单步耗时测量前不做承诺。

## 8. 现在具体应该做什么

**现在先做阶段 0，而不是直接启动全量训练。** 目前阻塞点是本机完整 CPU 测试环境缺依赖、MMRL30k 数据身份未在开发副本中封板、以及 CUDA/vLLM/FSDP 行为尚未实测。前一轮对话所称 36 项 CPU 通过是积极信号，但我本轮只独立复验了几何 10 项。

阶段 0 通过后，才申请 G4 45 分钟 probe。阶段 2 通过后才做 B512 单步。阶段 3 通过后才做冻结轨迹同预算 PTS 对照。对照数据有一致性证据且效果指标有意义后，才决定完整训练步数。

## 9. 不能妥协的停止条件

- 任何逻辑批次出现 rollout policy_version 不一致；
- chunk/no-chunk 固定轨迹的样本顺序、token、mask、image tensor、position ids 或答案元数据不一致；
- B512 的 optimizer update 次数不是 4，或参考微批 token weighting 与独立 8-rank 参考超出容差；
- ABS 每次无放回抽样的正权重支持数不足，或概率非有限/总和不为 1；
- checkpoint 的配置/模型/data/source identity 不符、文件 SHA 不符、恢复后的下一批数据/RNG/ABS indices/optimizer state 不一致；
- 任意 loss、gradient、reward/probability 出现 NaN/Inf；
- OOM、vLLM worker crash、NCCL/FSDP hang、连续无日志超时；
- 超过本阶段 CU 或墙钟预算。

遇到上述任一项，停止该逻辑步并保留日志/checkpoint；不改算法参数来绕过失败，不静默重采样，不将失败 run 计入结果。

## 10. 额外发现：上游示例配置不能原样作为正式训练配置

1. 官方 `examples/qwen2_5_vl_3b.sh` 把 `DATA_PATH=/your/data/path` 留作占位符；它没有替用户下载/校验 MMRL30k。
2. 官方 `examples/config.yaml` 默认值是 `hiyouga/math12k@train`、`hiyouga/math12k@test`、Qwen2.5-7B-Instruct、n=5、TP=2、8 GPUs。这不是 3B Shuffle-R1 正式配置；正式 3B 脚本只覆盖其中部分字段。
3. 上游 Dockerfile 锁定的是旧环境（torch 2.5.1、旧 nightly vLLM/FlashAttention），不能直接推断它能在 RTX PRO 6000 Blackwell / G4 上工作。尤其不能先照搬旧 Dockerfile 再把安装失败当作代码 bug。
4. 目标 G4 环境必须先读运行时驱动/CUDA、PyTorch、FlashAttention、vLLM 的实际兼容性，再生成独立 lock。建议从 Colab G4 当前镜像实测，不从主项目 A100 lock 或上游 Dockerfile直接复制版本。
5. 官方数据集页面显示 MMRL30k 约 29.1k 条、Apache-2.0；字段为 `problem`、`images`、`answer`、`source`。数据文件需要真实下载后校验，不可只凭 README 的说明宣称已就绪。

## 11. 参考来源（已核对）

- Shuffle-R1 官方代码与 README：<https://github.com/xiaomi-research/shuffle-r1>
- 官方 3B 启动脚本：<https://github.com/xiaomi-research/shuffle-r1/blob/main/examples/qwen2_5_vl_3b.sh>
- 官方默认配置（注意它并非 3B 正式配置）：<https://github.com/xiaomi-research/shuffle-r1/blob/main/examples/config.yaml>
- Shuffle-R1 论文：<https://arxiv.org/abs/2508.05612>；ICLR 2026 论文页：<https://proceedings.iclr.cc/paper_files/paper/2026/hash/c520d1cb9108a27c27227ba039229246-Abstract-Conference.html>
- 作者 MMRL30k：<https://huggingface.co/datasets/XenoZLH/MMRL30k>
- 作者 3B 模型：<https://huggingface.co/XenoZLH/Shuffle-R1-Qwen-3B>
- Google Cloud G4 官方规格（RTX PRO 6000 Blackwell，单卡 96 GB）：<https://docs.cloud.google.com/compute/docs/gpus>
- Colab 当前 CLI 能力由本机 `colab new --help` 核实：支持 `--gpu G4`；当前没有活动 session。

## 12. 本轮操作边界

- 未修改主项目训练代码、配置、数据或现有 S4/S5 结果。
- 未修改 Shuffle-R1 开发副本代码；未提交、未推送 GitHub。
- 未申请 GPU session、未启动训练、未下载完整 MMRL30k。
- 只在主项目 `reports/shuffle_r1_single_gpu_20261115/README.md` 新建了本报告。
- 本轮唯一实际执行的新增测试是几何模块 10 项，全部通过；其余 CPU 结果以历史对话为参考并明确标注未复验。

**最终裁决：** 单卡 96 GB 的技术路线值得继续，但不能据此承诺完整作者级 20-episode 复现。下一步的唯一正确动作是先补齐开发副本的 CPU 依赖并复验 36 项；通过后申请独立 G4 session 做 45 分钟 B16 工程探针。只有探针真实通过，才继续 B512 单步和同预算对照。
