# 多模态几何推理：视觉依赖与稀疏感知奖励

基于 Qwen2.5-VL-3B-Instruct。协议 v3 用部分认证的几何事实给 GRPO 提供感知奖励，并通过无图、错配图与反事实图形对照检验模型是否使用视觉信息。另有一条独立的 Shuffle-R1 单卡复现路线。

- **协议 v3**：S4 总计 12 个正式任务，每个 228 步。S5 最近核验到 67/117 个条件，九项主比较待完成。[训练与终评](docs/training.md)
- **Shuffle-R1**：完成 150 步训练、内部验证和六套公开测评。13,171 个输入各采样八次，共 105,368 条作答。[单卡运行](shuffle_r1/README.md) · [150 步结果](docs/results.md)

## 下载后先跑检查

需要 Git 与 Python 3.10+。以下命令只使用 Git 仓库中的文件，可在 Windows PowerShell、Linux 或 WSL 运行。

```text
git clone --depth 1 --branch main https://github.com/XDE10/vlm-perception-reward-rl.git
cd vlm-perception-reward-rl
python tools/verify_migration.py --full
python -m scripts.training.register_runs --show rl_v5 1
python shuffle_r1/run.py prepare --work-dir runs/shuffle-r1
```

第一个检查核对仓库文件 SHA256，第二个命令输出序列化的 S4 配置，最后一个从随仓库提供的 Git bundle 还原单卡源码。GPU 环境、训练数据、检查点和公开题库的准备方法见各运行指南。

## 目录

```text
src/                  协议 v3 的数据门控、奖励、训练与评测
scripts/              协议 v3 的训练、数据处理与 Colab 命令
configs/experiments/  组别、种子、登记表、运行时
configs/evaluation/   评测集定义、CF-Geo 补丁及其试验集
colab/                协议 v3 的 Colab 启动器
shuffle_r1/           单卡源码 bundle、安装与运行、权重导出、公开评测生成
data/                 数据接入说明，运行时读取本机数据包
docs/                 训练方法与结果
requirements/         协议 v3 的 CPU/GPU 依赖与 GPU 锁文件
tests/                用真实小样本和合成数据验证核心行为
tools/                完整性与文档链接检查
```

维护者可在 Linux 或 WSL 执行 `python -m pytest -q`。依赖和适用环境见 [requirements](requirements/README.md)。
