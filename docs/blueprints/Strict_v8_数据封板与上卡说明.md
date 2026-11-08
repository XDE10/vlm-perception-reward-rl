# Strict v8 数据封板与上卡说明

项目一实际 1500 对，项目三 609 train / 82 validation。精确配额达标：True。

[实测报告](<../reports/strict_v8_20261024/执行报告.md>)；[批准范围](<../data/strict_v8_20261024/release/manifest.json>)。

不等式原生完整SFT上限4096，其他源范围及精炼150~1500门槛保持。新配置在 `data/strict_v8_20261024/training_configs/`。A100还须实际最长样本前后向、checkpoint恢复、rollout截断和教师前向Smoke；CPU测试不代替这些检查。

示例：`python -m scripts.train_project1_sft --config data/strict_v8_20261024/training_configs/project1_raw_sft_smoke.json`。项目三使用对应fact SFT或sparse_v4 GRPO配置，只监督认证部分事实。
