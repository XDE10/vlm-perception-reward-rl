# 协议 v3 的 Colab 启动器

在 Linux 或 WSL 中运行。准备 Git、Bash、Python 3.10+ 和已登录的 `colab` CLI，按 [数据指南](../data/README.md) 提供批准的数据包。以下检查会读取数据和已有 Colab 会话。

```bash
bash colab/launch.sh check
```

启动器可申请预检会话。使用已经准备好的会话时加 `--session p3`。正式试跑、训练和终评要求 NVIDIA A100-SXM4-40GB，且 VM 已配置 rclone 的 `mydrive:` 远端或有效的 Drive 挂载。可在本地用 `P3_DRIVE_SETUP_FILE` 提供挂载脚本，或按自己的 Colab 设置手动挂载。先执行 Drive 检查。

```bash
bash colab/launch.sh preflight
bash colab/launch.sh drive-check --session p3
bash colab/launch.sh v0 --session p3
bash colab/launch.sh pilot --session p3
bash colab/launch.sh train --session p3
bash colab/launch.sh final-eval --session p3 --release
```

`pilot` 记录正式开跑门槛。`train` 只接受对应试跑和同一身份的完整 checkpoint，在完成 adapter 核验后标记任务完成。登记表仍包含历史实验的开跑截止日和预算门槛。用现成会话时，`--release` 表示在收集结果后释放。已有任务断开时用 `bash colab/launch.sh collect RUN_ID` 接回本地。

本地结果写入 `.colab_runs/`，正式训练权重与预测保存到指定 Drive。主动发布某次本地运行结果用 `bash colab/launch.sh push RUN_ID`。需要运行结束自动推送到有写权限的远端时，显式设置 `P3_PUBLISH_RESULTS=1`。个人环境设置放在忽略的 `.colab_local.env` 中。
