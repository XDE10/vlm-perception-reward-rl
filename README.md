# 项目三：多模态几何推理的视觉依赖与稀疏感知奖励

基于 Qwen2.5-VL-3B-Instruct 的几何图形事实感知项目：用经过认证的部分几何事实
构造可证伪的感知奖励做 GRPO，并用对照组和反事实评测研究“视觉信息是否被真正使用”。
本仓库包含可复现的数据清单、训练与评测入口及审计记录。S4 的 12 个正式任务已完成，S5 留出集终评正在运行。
执行计划与决策见 [docs/plan/](docs/plan/执行计划_20261108.md)。

## 当前状态

| 项目 | 事实（2026-11-14，UTC+8） |
| --- | --- |
| 批准数据 | 609 条训练事实（458 幅图）/ 82 条 validation 事实（77 幅图），部分认证事实，不是全图金标 |
| 模型 | `Qwen/Qwen2.5-VL-3B-Instruct` revision `66285546d2b821cf421d4f5eb2576359d3770cd3` |
| S4 正式训练 | [D66 预注册](docs/plan/S4预注册_20261110.md) 登记的 12 个正式任务全部从 V0 起跑并完成，各 228 步。已核对全部 Drive 完成标记，两个可选任务未运行。见 [完成记录](reports/s4_s5_progress_20261114/README.md) |
| S5 正式终评 | 11:38 快照为 21/117 个条件已在 Drive 写入校验标记，终评仍在运行。三类主终点与九项比较沿用 S3 预注册，正式结果待汇总。见 [评测进展](reports/s4_s5_progress_20261114/README.md#s5-正式终评) |
| GPU 验证 | A100-SXM4-40GB 上 S2 预检（18/18）、S3 `v0`（12/12）与 D66 S4 试跑（G1–G6）通过。正式训练结束状态以 D66 登记身份和 Drive 完成标记为准 |
| 测试 | 本机 WSL2（Python 3.12.3，有 `data/` 和固定 revision 的处理器文件）全部通过，见 [docs/verification.md](docs/verification.md) |
| 历史 | 2026-10-24 迁移、2026-11-08 清理与结构整理、2026-11-09 S1–S3、2026-11-10 S4 预注册与运行器，均记录在 [CHANGELOG.md](CHANGELOG.md) |

“已实现代码”“CPU 测试通过”“真实 GPU 跑通”“能力提升”是四种不同结论，报告
时必须分开陈述。2 步 smoke 或 ZIP 完整性检查不代表训练成功。

## 最小阅读顺序

1. 本页 → [docs/repo_layout.md](docs/repo_layout.md)（目录与模块地图）
2. [docs/data.md](docs/data.md)（数据准入与边界）+ [data/portable_release/manifest.json](data/portable_release/manifest.json)
3. [docs/architecture.md](docs/architecture.md)（流水线与身份链）
4. [docs/training.md](docs/training.md)（配置、命令、GPU 验收清单）
5. [docs/verification.md](docs/verification.md)（校验、测试与报告规范）

历史方案与迁移证据在 [docs/blueprints/](docs/blueprints/) 与
[docs/migration/](docs/migration/)，仅供溯源，**不可当作当前入口**。

## 快速检查（无需 GPU）

```bash
python tools/verify_migration.py --full
python -m pytest -q
python tools/check_links.py
```

三条命令依次检查：离线完整性（manifest、release、逐行批准、图片 SHA）；CPU 测试（环境见 requirements/dev-cpu.txt）；
当前文档的相对链接。命令块里不写 `#` 注释，粘贴到 zsh 里也能直接运行（D40）。

`python` 需要 3.10+（CPU 测试环境实测 3.12.13）。上述通过只证明离线/CPU 性质，不证明
CUDA、模型前后向或新环境依赖已安装。

## 目录结构

```text
.
├── README.md / AGENTS.md / CHANGELOG.md
├── pyproject.toml / .editorconfig / .gitignore
├── colab/         Colab 运行器：launch.sh（本地入口）+ 在 Colab 内核中执行的脚本 + 使用说明
├── configs/       当前执行配置：experiments/（协议 v3 正式实验）+ 旧入口 smoke
├── data/          冻结的数据载荷（约 1.4 GB，不进 git，见 data/README.md）
├── docs/          当前文档 + guides/ + 历史归档 blueprints/、migration/
├── reports/       只追加的实验与审核证据（布局冻结）
├── requirements/  环境记录（非锁文件）
├── scripts/       data/ training/ reporting/ migration/ common/ 分组脚本
├── src/           data/ evaluation/ losses/ rewards/ teachers/ training/ 库代码
├── tests/         CPU 测试
└── tools/         verify_migration.py / build_migration_manifest.py / check_links.py
```

分组说明与“为什么 data/、reports/ 不移动”见 [docs/repo_layout.md](docs/repo_layout.md)。

## 数据边界（最重要）

- 唯一训练/评测数据入口：`data/portable_release/` 中由
  [release manifest](data/portable_release/manifest.json) 的 `approved_*_files`
  列出的文件；609/82 行是当前批准范围。
- 模型输入只放行 `problem` 与相对 `image_path`。正式训练使用 V0 加语言 LoRA 的 GRPO；历史 SFT 的目标字段为 `model_perception`。
  `reference_answer`、认证正负事实、审核意见不得进入提示。
- 认证范围之外的事实视为未知（mask）；不能宣称完整防幻觉或全图 precision/recall。
- 不手改批准字段、行内容、图片或 SHA；不把 validation/测试题用于训练或调奖励。
- 新数据版本使用新的带日期目录并重新封板，保留来源证据。

## 在 Colab 上运行

在 WSL2 中运行以下命令，一次性准备与断线恢复见 [colab/README.md](colab/README.md)：

```bash
bash colab/launch.sh check
bash colab/launch.sh preflight
bash colab/launch.sh v0 --session p3
bash colab/launch.sh pilot --session p3
bash colab/launch.sh train --session p3
bash colab/launch.sh final-eval --session p3 --release
```

`check` 是本地自检（colab 认证、数据 SHA、git 推送权限，不建 VM）；`preflight` 是 S2 的 GPU 预检；`v0` 是 S3 的评测输入核对、
train 上的决策测量与 V0 诊断，在你准备好的 VM `p3` 上运行。`pilot` 是 S4 的试跑与开跑门槛，`train` 按登记顺序跑正式任务
（每次跑到 VM 的时间用完，需要多次运行）；`final-eval` 在正式任务收尾后运行。三者使用挂好 Google Drive 的 A100-SXM4-40GB（colab/README.md 第九、十节）。

## 训练入口

```bash
python -m scripts.training.train_rl --arm rl_v5 --seed 1
python -m scripts.training.train_rl --registered configs/experiments/s4_runs_20261110.json --arm rl_v5 --seed 1
```

第一条是协议 v3 统一入口，所有实验组共用，组别与种子登记在 `configs/experiments/arms.json`。第二条是 S4 正式任务的启动方式：
必须与登记表一致（配置哈希、数据、行数、GPU），不允许 `--smoke` 与 `--output-dir`。

组别：`rl_ans`（答案 + 格式）、`rl_v4`（原稀疏 F1，消融）、`rl_v5`（可证伪感知奖励，主方法）、
`rl_v5_placebo`（事实取自另一张图，对照）、`rl_blind`（训练时不给图，对照）。输出目录、运行身份与
恢复规则见 [docs/training.md](docs/training.md)。

旧入口 `python -m scripts.training.train_project3 --config configs/project3_*.json`（感知 SFT → 稀疏 GRPO）
保留为历史，只修复了 LoRA 误入 ViT 与 transformers 5 兼容两处缺陷。

## 历史与溯源

- 2026-10-24：从旧 `modern_genai` 工作区迁移本项目的便携发布数据、配置与代码，
  原始清单封板在 [docs/migration/migration_manifest_交接补充前_20261024.json](docs/migration/migration_manifest_交接补充前_20261024.json)。
- 2026-11-08：删除旧项目共用设施与残留（约 950 MB），把迁移清单改为当前树
  清单（schema_version 2），封板副本与删除记录保留在
  [docs/migration/](docs/migration/)。
- 2026-11-08：目录整理（`project_blueprints/`→`docs/blueprints/`、
  `迁移记录/`→`docs/migration/`、脚本分组、文档重写），移动映射由
  `migration_manifest.json` 的 `documentation_updates` 记录和
  [CHANGELOG.md](CHANGELOG.md) 记录。
- 历史报告中的绝对路径、失败项和隔离项保持原样，不因整理而改写。
