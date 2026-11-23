# 项目维护

从 [README](README.md) 开始。协议 v3 和 Shuffle-R1 使用不同的训练数据、环境和评测协议。

- 协议 v3 用 `scripts.training.train_rl`，固定模型 revision，从 V0 仅训练语言 LoRA。以 release manifest 与登记表为批准数据和训练身份来源。
- Shuffle-R1 从 [单卡指南](shuffle_r1/README.md) 启动。150 步内部验证、历史单次对照和八采样公开评测分别引用，离线复核注明来源。
- 结构变化后运行 `python tools/build_migration_manifest.py --date YYYY-MM-DD --purpose "reason"`。保留冻结数据哈希。
- 验证使用 `python tools/verify_migration.py --full`、`python tools/check_links.py` 与 `python -m pytest -q`。有批准数据时加 `--data-root data` 单独核对数据。
- 运行日志、复核明细、权重和私有数据包存到本地存档或项目存储。
