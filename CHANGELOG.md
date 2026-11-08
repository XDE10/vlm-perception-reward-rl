# 变更记录

本文件记录仓库结构、文档与验证状态的变更。训练/数据事实的变化以
[README](README.md) 和版本化报告为准；历史细节见
[docs/migration/](docs/migration/)。

## 2026-11-09 — S1：修复审计问题，新增协议 v3 统一 GRPO 入口

按 [执行计划](docs/plan/执行计划_20261108.md) 第 4 节逐项修复，决策见
[决策记录](docs/plan/决策记录.md) D1–D17。没有 GPU 运行，没有改动已批准数据或冻结的 v4 评分。

- 新增 `src/rewards/`：逐条断言解析（坏条只算一个 FALSE，不再整段归零）、InterGPS 几何证伪、
  可证伪感知奖励 v5、math_verify 常驻进程池、罗列攻击探针。
- 新增协议 v3（perception → think → answer，所有组共用，恢复推理段）与统一入口
  `scripts/training/train_rl.py`；`configs/experiments/` 用基础配置加组别白名单覆盖，保证组间只在声明因素上不同。
- 修复：LoRA 改为按精确模块名只挂语言模块，并在运行时断言 ViT/merger 冻结（旧入口同样修复）；
  多奖励改用 `scale_rewards=batch`，避免组内标准化抹掉 λ；每步 8 题 × 8 条采样、整批生成；
  格式奖励要求 perception 非空且可解析；每条 rollout 落盘。
- 兼容：transformers 5 移除了 `AutoModelForVision2Seq`，旧入口与诊断脚本改用兼容类。
- 新增 `scripts/data/calibrate_perception_v5.py`（阈值校准与攻击表）、`requirements/dev-cpu.txt`、
  `tools/build_migration_manifest.py --git-tracked-only`。
- 测试：沙箱（无 `data/`）下 172 passed / 2 failed，两项失败都依赖本机 `data/`，见
  [docs/verification.md](docs/verification.md)。

## 2026-11-08 — 仓库整理（目录结构、文档与校验入口）

本次只做结构、文档与元数据整理，**没有**重新训练、重新审核数据或扩大批准范围。

结构变化：

- 新增 [docs/](docs/)：当前说明页（[repo_layout](docs/repo_layout.md)、
  [architecture](docs/architecture.md)、[data](docs/data.md)、
  [training](docs/training.md)、[verification](docs/verification.md)）。
- `project_blueprints/` → [docs/blueprints/](docs/blueprints/)（历史方案与配置留档）。
- `迁移记录/` → [docs/migration/](docs/migration/)，并加入
  [整理记录](docs/migration/整理记录_20261108.md)。
- 根目录说明文档归档：`OVERNIGHT_CPU_README.md` →
  [docs/migration/overnight_cpu_20261023.md](docs/migration/overnight_cpu_20261023.md)
  （旧三项目 CPU 栈历史说明），深度审查提示词 →
  [docs/guides/argon_review_prompt.md](docs/guides/argon_review_prompt.md)。
- `requirements-cpu-snapshot.txt` / `requirements-project3-cpu.txt` →
  [requirements/cpu-snapshot.txt](requirements/cpu-snapshot.txt) /
  [requirements/project3-cpu.txt](requirements/project3-cpu.txt)。
- `scripts/` 按职责分组为 `common/`、`data/`、`training/`、`reporting/`、
  `migration/`，并补充 [scripts/README.md](scripts/README.md) 目录；
  入口命令相应变为 `python -m scripts.<group>.<name>`。
- `pytest.ini` 合并进 [pyproject.toml](pyproject.toml)。
- 新增 `data/`、`reports/`、`configs/`、`requirements/` 目录说明；
  新增 [tools/check_links.py](tools/check_links.py) 与
  [tools/build_migration_manifest.py](tools/build_migration_manifest.py)。
- `reports/` 与 `data/` 的物理布局保持冻结（追加式证据与已发布哈希引用），
  只增加索引说明。

校验与事实：

- 本机 Python 3.11.4：`pytest -q` 74 passed / 2 failed，两个失败都是环境缺包
  （`math_verify`、`trl`），不是代码回归；项目文档记载的 Python 3.12 环境
  本次未复验。
- 追加 [tests/test_repo_layout.py](tests/test_repo_layout.py) 结构回归测试（6 项），
  固定“scripts/ 无平铺脚本、分组均为包、README 覆盖全部脚本、当前入口文件存在、
  pytest 配置指向 tests/、configs 相对路径+固定 revision”；更新
  [docs/guides/argon_review_prompt.md](docs/guides/argon_review_prompt.md) 中
  的审查阅读路径到整理后布局。
- `python tools/verify_migration.py --full`：见
  [整理记录](docs/migration/整理记录_20261108.md) 的实测记录。
- 没有 GPU 训练产物；`runs/` 不存在，2 步 smoke 仍只是工程配置。

## 2026-11-08 — 与其他两个项目彻底分离（清理）

- 删除项目一/二残留 237 条路径（约 90 MB），包括 `src/synthesis/`、
  `.pilot_deps/`、`agentic_rl/`、`math/`、`tiny_posttrain/`、`video_mapping/`、
  项目一/二专用脚本与测试；保留项目三数据、脚本、报告与迁移记录。
- 详见 [清理记录](docs/migration/清理记录_20261108.md)。
- `migration_manifest.json` 当时保持封板，因此校验会对已删除路径报缺失
  （见文件内说明与 [迁移验收](docs/migration/迁移验收.md)）。

## 2026-10-24 — 从 modern_genai 迁移为独立包

- 迁移项目三代码、数据、报告与历史蓝图；`migration_manifest.json` 记录
  4258 个负载文件的大小与 SHA256（含 source_sha256 溯源字段）。
- 迁移验收（2026-10-24）：离线校验通过，CPU 相关测试 15 passed；
  当时使用 Python 3.12 环境。
- 详见 [迁移验收](docs/migration/迁移验收.md)。
