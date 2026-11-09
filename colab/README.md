# Colab 运行器使用说明

一条命令完成：建 Colab GPU VM → 上传代码与私有数据 → 安装固定版本的环境 → 运行任务 →
取回结果 → 释放 VM → 把结果推到 GitHub 的 `results/<run_id>` 分支。你只需要按下面的步骤运行命令，
不需要改代码。

本地端只需要 `bash`、`git`、`tar` 和 `python3`（3.8 及以上，只用标准库）。Colab CLI 不支持原生 Windows，请在 WSL2 中运行。

## 一、一次性准备（约 10 分钟）

### 1. 在 WSL2 里准备仓库

推荐在 WSL2 的 Linux 文件系统里新 clone 一份。这样 git 更快，也不会遇到 Windows 换行符问题：

```bash
cd ~
git clone https://github.com/XDE10/vlm-perception-reward-rl.git p3
cd p3
```

如果你想直接用 Windows 上原来的项目目录（例如 `/mnt/d/...`）也可以，第 2 步可以省掉。

### 2. 告诉运行器数据在哪里

`data/` 不在 git 里。运行器只读取其中一小部分（已批准数据、相应图片、InterGPS 标注，约 40 MB），
逐个校验 SHA 后打包；**不会修改原数据**。在仓库根目录建一个本地设置文件（已被 git 忽略）：

```bash
cat > .colab_local.env <<'EOF'
# 原项目 data/ 目录的位置（Windows 盘符在 WSL 中是 /mnt/<盘符小写>/...，路径含中文或空格时保留引号）
P3_DATA_ROOT="/mnt/d/Users/Mr.Z/Desktop/项目三_多模态几何推理/data"
# 如需给 colab 传全局参数（例如认证方式），写在这里；不需要就留空
COLAB_GLOBAL_FLAGS=""
EOF
```

如果数据就在本仓库的 `data/` 下，可以不写 `P3_DATA_ROOT`。

### 3. 确认 GitHub 推送权限

运行器会把结果推到新分支 `results/<run_id>`，所以本机 git 需要能 push 到这个仓库。
最简单的方式是装好 GitHub CLI 后运行 `gh auth login`，选择 HTTPS。

### 4. 自检

```bash
bash colab/launch.sh check
```

它会检查：colab CLI 与认证（`colab sessions`）、数据是否完整且与记录的 SHA 一致、git 是否有推送权限，
并显示 `colab usage` 的计算单元余额。最后一行是 `all checks passed` 才继续。这一步不会创建 VM，也不花计算单元。

## 二、每个阶段只需要运行一条命令

```bash
bash colab/launch.sh preflight      # S2 预检：约 60–90 分钟，预计 15–25 个计算单元
```

运行期间终端会持续打印进度行。正常结束时，最后会打印摘要的前 30 行，并给出结果分支的链接。
然后在聊天里告诉我“跑完了”即可，我会从结果分支读取全部数据。

后续阶段的命令（`v0`、`train` 等）会在对应阶段加入，用法相同。

常用选项：

| 选项 | 作用 |
|---|---|
| `--gpu H100` | 申请 A100 失败（没有配额或暂时没有空闲）时改用 H100；同一批实验请保持同一种 GPU |
| `--no-vllm` | 跳过可选的 vLLM 探测（省约 15 分钟） |
| `--keep` | 结束后不释放 VM（排查问题用，记得之后 `stop`） |
| `--allow-dirty` | 允许在有未提交代码改动时运行；改动的 diff 会随结果一起上传 |

退出码：`0` 表示任务通过；`3` 表示任务跑完但未通过（结果照常推送，我来分析）；`1` 表示运行器本身出错。

## 三、断线、中断与恢复

- **按 Ctrl-C 或关掉终端**：只是断开连接，VM 上的任务会继续跑完。
- **重新连上并取回结果**：`bash colab/launch.sh collect <run_id>`。它会等任务结束，然后取回结果、释放 VM、推送结果。
- **主动释放 VM**（不要结果了）：`bash colab/launch.sh stop <run_id>`
- **查看本地记录的所有运行**：`bash colab/launch.sh list`
- **只是推送失败**（例如凭据问题）：修好后运行 `bash colab/launch.sh push <run_id>`。

`<run_id>` 形如 `preflight-20261110T093000Z-ab12`，运行开始时会打印出来，也可以用 `list` 查到。

## 四、结果在哪里

- 本地：`.colab_runs/<run_id>/results/<run_id>/`。`summary.md` 是给人看的摘要，`summary.json`
  是机器可读的全部数字，`logs/` 是每个步骤的完整日志。
- GitHub：分支 `results/<run_id>` 下的 `reports/colab_runs_<日期>/<run_id>/`。本地的启动日志与计算单元用量
  在其中的 `_local/` 目录。
- 不会上传：模型权重、LoRA adapter、checkpoint，以及超过 25 MB 的单个文件。它们会列在
  `PACKAGING.json` / `SKIPPED_LARGE_FILES.txt` 里，原件留在你本地或 VM 上。

## 五、它具体做了什么

1. **本地**：检查代码目录没有未提交改动；用 `git archive` 打包当前提交的代码；按三类锚点
   （release manifest、行内图片 SHA、`migration_manifest.json`）校验后打包私有数据；文件按 8 MB 分片。
2. **VM 引导**（`colab/kernel_bootstrap.py`）：校验分片并解包；复核数据；读取驱动支持的 CUDA 版本，
   选择 `requirements/locks/` 里对应的锁文件（cu130 / cu129 / cu126），建隔离 venv；
   下载固定 revision 的 Qwen2.5-VL-3B 并记录每个文件的 SHA256。
3. **VM 任务**（`colab/kernel_job.py`）：逐步运行任务，每个步骤是独立进程，有超时；每 60 秒打印一次心跳并更新
   `status.json`。断线时，运行器通过 Jupyter 文件接口轮询这个文件。
4. **收尾**：生成 `summary.md`，打包结果（不含权重），取回并校验，释放 VM，推送结果分支。

## 六、常见问题

| 现象 | 处理 |
|---|---|
| `could not allocate a A100 VM` | 暂时没有 A100 或没有配额。稍后重试，或加 `--gpu H100` |
| `data check` 报 `missing` / `hash changed` | `P3_DATA_ROOT` 路径不对，或数据被改动过。先确认路径；如果确实被改动，把 `check` 的输出发给我 |
| `uncommitted changes in code directories` | 你改过代码但没提交。提交后再运行，或加 `--allow-dirty` |
| `git push failed` | 结果已安全保存在本地。修好凭据后运行 `bash colab/launch.sh push <run_id>` |
| `$'\r': command not found` | 脚本被转成了 Windows 换行。按第一节第 1 步在 WSL 里新 clone 一份 |
| 长时间没有输出 | 正常情况下每 60 秒至少有一行心跳。超过 10 分钟没有输出时，按 Ctrl-C，然后用 `collect` 重新连接 |

结束后运行 `colab sessions`，确认没有遗留的 VM 在消耗计算单元。
