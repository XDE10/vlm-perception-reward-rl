# 项目入口

适用范围：本项目根目录及其子目录。

- 当前项目：项目三：多模态几何推理的视觉依赖与稀疏感知奖励。
- 主模型是 Qwen2.5-VL-3B-Instruct。当前是609 train/82 validation的部分认证事实；SFT只监督model_perception，稀疏RL从感知SFT起点运行，不能冒充完整V0～V4或EasyR1已跑通。
- 先读 [README.md](README.md)，再按任务读取 [configs/](configs) 和 [data/portable_release/manifest.json](data/portable_release/manifest.json)。无需先遍历全部原始数据、缓存或历史报告。
- 当前执行配置在根目录 configs/；project_blueprints/ 和原始发布目录中的旧配置保留溯源，可能带旧绝对路径。
- 本项目独立于旧 modern_genai 和其他项目目录；旧原仓库项目环境已清理，不能引用其 .venv。
- 数据范围以 approved_training_files / approved_evaluation_files 和逐行批准为准。候选不等于批准，AI 审核不等于人工金标；不要手改批准或哈希以绕过检查。
- 代码能力查看实际源码，状态查看 README 与版本化报告。当前 GPU 尚未验收，2 步 smoke 和历史 CPU 通过不代表正式训练成功。
- 命令从项目根目录执行；离线入口为 python tools/verify_migration.py。依赖与相关测试命令见 README。
- 文档/代码变更保留来源和验证记录；固定模型、数据、划分和评测身份，报告未运行的检查。
