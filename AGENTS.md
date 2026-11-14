# 项目入口与工作约定

适用范围：本仓库根目录及其子目录。

- 当前项目：项目三：多模态几何推理的视觉依赖与稀疏感知奖励。
- 主模型是 Qwen2.5-VL-3B-Instruct；当前是 609 train / 82 validation 的部分认证
  事实，不是全图金标。
- 正式实验用协议 v3 统一入口 `scripts.training.train_rl`，所有组都从 V0 出发：
  V0 是固定 revision 的 Qwen2.5-VL-3B-Instruct 原始权重，只挂语言 LoRA 做 GRPO，
  不做感知 SFT（[执行计划](docs/plan/执行计划_20261108.md) 第 2.1、4 节，
  [S4 预注册](docs/plan/S4预注册_20261110.md) 第 3 节）。
- 旧入口 `scripts.training.train_project3`（只监督 `model_perception` 的感知 SFT，
  再从 SFT 权重起跑稀疏 GRPO）只作历史保留，不用于正式实验。不能宣称完整
  V0～V4 SFT 矩阵或 EasyR1 已跑通。
- 先读 [README.md](README.md)，再按任务读 [docs/](docs/README.md) 与
  [configs/](configs/README.md)、[data/portable_release/manifest.json](data/portable_release/manifest.json)。
  无需先遍历全部原始数据、缓存或历史报告。
- 当前执行配置在 [configs/](configs/)；[docs/blueprints/](docs/blueprints/) 中的
  旧配置保留溯源，可能带旧绝对路径，不能直接执行。
- 本项目独立于旧 `modern_genai` 和其他项目目录；旧共用环境/模块已被清理，不能
  引用其 `.venv` 或旧入口。
- 数据范围以 release manifest 的 `approved_training_files` /
  `approved_evaluation_files` 和逐行批准为准。候选不等于批准，AI 审核不等于
  人工金标；不要手改批准、行内容或哈希来绕过检查。
- 代码能力看实际源码，状态看 README 与版本化报告；GPU 上跑过什么，以 README
  和 `results/<run_id>` 结果分支为准。冒烟、试跑和历史 CPU 通过都不代表正式
  训练成功或能力提升。
- 命令从项目根目录执行；离线入口为
  `python tools/verify_migration.py`（`--full` 含 SHA）。测试用
  `python -m pytest -q`（需要 3.10+）；文档链接用
  `python tools/check_links.py`。
- 结构变更后重建清单：`python tools/build_migration_manifest.py`；不要手工编辑
  `migration_manifest.json` 的哈希字段。
- 文档/代码变更保留来源和验证记录；`data/`、`reports/` 布局冻结，新增内容用
  新日期目录；历史归档不改写。报告未运行的检查。
