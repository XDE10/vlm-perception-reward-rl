# 协议 v3 训练与终评

所有试验组从同一个 Qwen2.5-VL-3B-Instruct 版本开始（`66285546d2b821cf421d4f5eb2576359d3770cd3`），冻结视觉模块，只训练语言侧 LoRA。协议统一输出 `<perception>`、`<think>` 和 `<answer>`。格式与答案分别计分，v5 额外奖励认证正事实，惩罚与认证事实冲突或能被几何证伪的断言，对 UNKNOWN 只给较小惩罚。

[组别配置](../configs/experiments/arms.json)涵盖答案奖励、v4 稀疏 F1、v5 感知奖励、错配图事实和无图对照。批准数据为 609 条训练事实和 82 条验证事实。认证只覆盖图中部分事实，全文只报告认证范围内的感知指标。[S4 预注册](plan/S4预注册_20261110.md)

## 本地 Linux GPU

准备 Python 3.12、与 GPU 驱动对应的[依赖](../requirements/README.md)及[批准数据包](../data/README.md)。在仓库根目录检查和启动。

```bash
python tools/verify_migration.py --full --data-root data
python -m scripts.training.register_runs --check
python -m scripts.training.train_rl --arm rl_v5 --seed 1 --smoke max_steps=2,num_generations=2,prompts_per_step=2,per_device_train_batch_size=2 --output-dir runs/smoke
```

登记运行使用固定数据、配置和运行时，在 A100-SXM4-40GB 上执行。运行时为 vLLM。按依赖说明安装对应 GPU 环境。

```bash
python -m scripts.training.train_rl --registered configs/experiments/s4_runs_20261110.json --arm rl_v5 --seed 1
```

可用 `--model-path` 指向固定 revision 的本地快照。续跑使用 `--resume` 指向完整 checkpoint，训练器核对源代码、包版本、模型和数据身份。历史任务以原训练提交和环境恢复。

## Colab 与 S5

[Colab 指南](../colab/README.md)提供 `preflight`、`v0`、`pilot`、`train` 和 `final-eval`。S5 使用 S4 的已核验最终 adapter 与 V0，报告认证感知、CF-Geo 读图和 Geometry3K 视觉必需子集三类主终点。[S3 评测设计](plan/S3设计_20261109.md)

历史 S4 共 12 个正式任务、每个 228 步。S5 最近核验 67/117 个条件，继续同一批预测时使用原提交 `2bc87709bc30578441b7c08f38e0477b96002b26` 及原环境、数据和 Drive 目录。[S5 恢复记录](https://github.com/XDE10/vlm-perception-reward-rl/blob/e2a4919326a1125eabe942ecfe10729f03aa3120/reports/shuffle_r1_cpu_data_freeze_20261115/s5-resume-verification.json)
