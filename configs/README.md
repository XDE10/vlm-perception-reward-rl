# 实验配置

- [experiments/](experiments/) 保存协议 v3 的统一配置、对照组、运行时及 S4 登记表。用 `python -m scripts.training.register_runs --show rl_v5 1` 查看已解析的一组配置。
- [evaluation/](evaluation/) 保存 S5 使用的评测集定义和 CF-Geo 补丁。Python 构建入口在 [scripts/data](../scripts/data/)。
- Shuffle-R1 单卡参数在 [shuffle_r1/train.yaml](../shuffle_r1/train.yaml)。
