# Colab 运行器使用说明

一条命令完成：建 Colab GPU VM → 上传私有数据（代码由 VM 从 GitHub 取并逐文件校验）→ 安装固定版本的环境 →
运行任务 → 取回结果 → 释放 VM → 把结果推到 GitHub 的 `results/<run_id>` 分支。你只需要按下面的步骤运行命令，
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

`data/` 不在 git 里。运行器只读取其中一小部分（已批准数据、相应图片、InterGPS 标注；打包压缩后约 21 MB），
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
它还会告诉你两件不影响通过与否的事：当前提交是否已在 GitHub 上（在的话 VM 直接从 GitHub 取代码，
本机只需上传约 21 MB 私有数据），以及是否配置了可选的 Google Drive（见第七节）。

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

1. **本地**：检查代码目录没有未提交改动；按三类锚点（release manifest、行内图片 SHA、`migration_manifest.json`）
   校验后打包私有数据，按 2 MB 分片上传。每片最多试 6 次，每次有时间上限（默认 600 秒），失败原因记在
   `.colab_runs/<run_id>/upload.log`。传完后在 VM 上逐片核对大小和 SHA256，只重传缺失或损坏的分片（最多 3 轮）。
2. **代码**：当前提交已推到 GitHub 时，VM 直接下载这个提交的源码包，并把每个文件与该提交的 git blob SHA-1
   逐一比对，有任何不一致就不用它；这时（或提交还没推送、有未提交改动时）改为从本机上传 `git archive` 打包的代码，
   同样分片并核对。设 `P3_CODE_SOURCE=upload` 可强制上传。
3. **VM 引导**（`colab/kernel_bootstrap.py`）：校验并解包；复核数据；读取驱动支持的 CUDA 版本，
   选择 `requirements/locks/` 里对应的锁文件（cu130 / cu129 / cu126），建隔离 venv；
   下载固定 revision 的 Qwen2.5-VL-3B 并记录每个文件的 SHA256。
4. **VM 任务**（`colab/kernel_job.py`）：逐步运行任务，每个步骤是独立进程，有超时；每 60 秒打印一次心跳并更新
   `status.json`。断线时，运行器通过 Jupyter 文件接口轮询这个文件。
5. **收尾**：生成 `summary.md`，打包结果（不含权重）并按 2 MB 分片，取回并校验，释放 VM，推送结果分支。
   推送前会把日志里形似凭据的字符串（例如 CLI 报错网址里的 `colab-runtime-proxy-token`）替换成 `REDACTED`，
   替换记录在 `_local/REDACTIONS.txt`；你本机 `.colab_runs/` 里的原始日志不变。

## 六、常见问题

| 现象 | 处理 |
|---|---|
| `could not allocate a A100 VM` | 暂时没有 A100 或没有配额。稍后重试，或加 `--gpu H100` |
| `data check` 报 `missing` / `hash changed` | `P3_DATA_ROOT` 路径不对，或数据被改动过。先确认路径；如果确实被改动，把 `check` 的输出发给我 |
| `uncommitted changes in code directories` | 你改过代码但没提交。提交后再运行，或加 `--allow-dirty` |
| `git push failed` | 结果已安全保存在本地。修好凭据后运行 `bash colab/launch.sh push <run_id>` |
| `$'\r': command not found` | 脚本被转成了 Windows 换行。按第一节第 1 步在 WSL 里新 clone 一份 |
| 长时间没有输出 | 正常情况下每 60 秒至少有一行心跳。超过 10 分钟没有输出时，按 Ctrl-C，然后用 `collect` 重新连接 |
| `upload of ... failed` 反复出现 | 运行器会自动重试和补传。若整次运行仍停在上传，在 `.colab_local.env` 里加一行 `P3_PART_MB=1`（分片改为 1 MB）后重跑；`upload.log` 里有 CLI 的原始报错 |
| `the VM could not fetch or verify the code from GitHub` | 不用处理：运行器已自动改为上传代码 |

结束后运行 `colab sessions`，确认没有遗留的 VM 在消耗计算单元。

## 七、可选：把结果另存到 Google Drive

不配置也完全可以：每次运行的结果都会推到 GitHub 的 `results/<run_id>` 分支。Drive 的用处是给后面的长时间训练
多一份不依赖本机网络的副本（S4 起会用来保存 LoRA adapter 和 checkpoint）。

规则（理由见 `docs/plan/决策记录.md` D31）：

- 训练只读写 VM 本地盘 `/content`。写进 Drive 一律用 `rclone copy`，再用 `rclone check --one-way` 核对大小和哈希，
  核对通过才算保存成功。**不通过 FUSE 挂载写入**：往挂载点写文件，`write()` 返回时上传可能还没完成。
- 只写 `mydrive:ColabProjects/vlm-perception-reward-rl/` 之下：预检时是 `runs/<run_id>/`（结果包与 `package.json`），
  探针用 `_p3_probe/<run_id>/`，并且只删除它自己刚写的文件。
- Drive 出任何问题都不会让运行失败，只在终端里打印一行警告。

运行器不知道你平时怎么在 Colab 上挂载 Drive，所以留了两个入口，在 `.colab_local.env` 里二选一：

```bash
# A：本机上的一条命令，能给指定的 Colab 会话挂载 Drive / 配好 rclone。{session} 会被替换成本次 VM 的会话名
#    （命令里也能用环境变量 $P3_SESSION）。下面的命令名只是占位，换成你实际用的命令
P3_DRIVE_MOUNT_CMD='你的挂载命令 {session}'
# B：你平时在 Colab 笔记本里挂载 Drive 的那个单元格，原样存成文件（可以含 !rclone ... 这样的行），
#    运行器会在新 VM 上执行它
P3_DRIVE_SETUP_FILE="$HOME/colab_drive_setup.py"
# 一般不用改：rclone 远端名、Drive 上的目录、挂载点
# P3_DRIVE_REMOTE="mydrive:"
# P3_DRIVE_DIR="ColabProjects/vlm-perception-reward-rl"
# P3_DRIVE_MOUNT="/content/mydrive"
```

这两个入口的输出只写到本机的 `.colab_runs/<run_id>/drive_mount.log`，**不会推到 GitHub**，命令本身也不写进日志，
因为里面可能有凭据。

配好后先用便宜的 CPU VM 试一次（几分钟，不需要 GPU）：

```bash
bash colab/launch.sh drive-check
```

它在 Drive 上写一个小文本和一个 16 MB 随机文件，读回比对 MD5、跑 `rclone check`，再删掉；
如果有挂载点，还会测一个经挂载写入的文件要多久才出现在远端。结果在摘要的 “Google Drive” 一节。
之后每次 `preflight` 也会做同样的探测（不计入通过与否），并在结束时把结果包复制到 Drive，终端里会显示
`Drive copy verified: ...` 或一条警告。
