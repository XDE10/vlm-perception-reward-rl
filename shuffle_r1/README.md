# Shuffle-R1 单卡训练和公开评测

本路线使用 Qwen2.5-VL-3B-Instruct 固定 revision、清洗后 27,436 行训练和按图像家族隔离的 256 行内部 dev。逻辑批次为 B512/G128/n16，PTS、ABS replay=8，最多 150 步。依赖为 Linux x86_64、Python 3.12、CUDA 12.8 和一张与正式运行同级的 Blackwell GPU。正式运行使用 Colab G4（RTX PRO 6000 Blackwell Server Edition）。[模型与数据身份](split_manifest.json) · [150 步结果](../docs/results.md)

## 安装和训练

```bash
python shuffle_r1/run.py prepare --work-dir runs/shuffle-r1
bash shuffle_r1/install.sh .venv-shuffle
source .venv-shuffle/bin/activate
export LD_PRELOAD="$VIRTUAL_ENV/nccl/nvidia/nccl/lib/libnccl.so.2"
```

第一条命令可单独执行，无需 GPU。它从 [source.bundle](source.bundle) 还原单卡源码提交 `1a7fb4b67e02a6b41cde437d7edc074ddd5a22e6`。外部软件包、模型缓存与 checkpoint 需要留出充足的本地空间，单张卡运行原方案预留约 140 GiB。

向仓库维护者取得冻结的 `train.parquet`、`dev.parquet`，放到 `runs/shuffle-r1/data/`。启动器按清单核对 Parquet SHA256 与固定模型快照，默认从 Hugging Face 下载模型。已有快照可用 `--model` 指定。训练的输出保存在 `runs/shuffle-r1/checkpoints/`。

```bash
python shuffle_r1/run.py train --work-dir runs/shuffle-r1
```

用同一工作目录和环境重新执行，加 `--resume /path/to/global_step_N` 从完整 checkpoint 恢复。已有历史断点恢复时须匹配原绝对输入和模型路径及配置身份。可用 `--stop-after 1` 试验一次 checkpoint 写入，之后从该完整断点接着训练。

## 公开评测生成

下载 [固定版本的 MM_Eval.zip](https://huggingface.co/datasets/XenoZLH/MM_Eval/resolve/476ee7d0d3919299eeeca135548a13440bc0751c/MM_Eval.zip)，解包并定位包含 `mathverse/`、`ChartQA_test/` 等子目录的目录。准备本地 HF 格式权重目录。所维护的原第 150 步 checkpoint 可用 [导出脚本](export_step150.py)离线转成 HF 权重，输入为该 checkpoint 的 actor 目录与 manifest。

```bash
python shuffle_r1/export_step150.py --source /path/to/global_step_150 --manifest /path/to/global_step_150/manifest.json --out runs/shuffle-r1/model-150
python shuffle_r1/evaluate.py --work-dir runs/shuffle-r1 --data /path/to/extracted/data --dataset-archive /path/to/MM_Eval.zip --suite mathverse --model runs/shuffle-r1/model-150 --out runs/shuffle-r1/mathverse.jsonl
```

评测支持 `mathverse`、`mathvision`、`mathvista`、`wemath`、`hallubench`、`chartqa`。用 `--check-only` 验证题库和提示输入，无需 GPU 或模型。用 `--start`、`--stop` 运行固定顺序的区间，每个区间使用新输出文件。JSONL 保存题目 ID、种子、真实生成、参考答案、结束原因及输入哈希，供下游判分。历史测评分数包含外部判分和离线复核。

上游出处为 [xiaomi-research/shuffle-r1](https://github.com/xiaomi-research/shuffle-r1/tree/b863694f25d38d0e118761363dc5897bb9625e82)。[上游许可证](UPSTREAM-LICENSE)随源码保留。
