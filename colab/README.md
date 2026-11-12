# Colab 运行器使用说明

一条命令完成：建 Colab GPU VM → 上传私有数据（代码由 VM 从 GitHub 取并逐文件校验）→ 安装固定版本的环境 →
运行任务 → 取回结果 → 释放 VM → 把结果推到 GitHub 的 `results/<run_id>` 分支。你只需要按下面的步骤运行命令，
不需要改代码，也不需要把结果下载下来再发给我：跑完后告诉我“跑完了”，我直接从 GitHub 读取。

有两种用法：

- **新建 VM**（第二节）：不用准备，一条命令。结果由你本机取回后推到 GitHub，VM 用完即释放。
- **准备好的 VM**（第八节）：你先在 VM 上挂好 Drive、放好 GitHub 凭据，任务结束时由 VM 自己把结果推到 GitHub。
  你的电脑中途休眠或断网也不影响结果；长时间训练（S4）用这种方式。

本地端只需要 `bash`、`git`、`tar` 和 `python3`（3.8 及以上，只用标准库）。Colab CLI 不支持原生 Windows，请在 WSL2 中运行。

**关于 zsh**：运行器总是用 `bash colab/launch.sh ...` 启动，所以在 zsh 里也能运行。本文所有要在 WSL2 里粘贴的命令都可以直接用于 zsh：
命令行末尾没有 `#` 注释（zsh 默认会把它当成参数传给命令），含 `*` 的参数都加了引号。第八节标明“在 VM 里”的命令在
`colab console` 打开的 VM 终端里执行，那里是 bash。

## 一、一次性准备（约 10 分钟）

### 1. 在 WSL2 里准备仓库

仓库要放在 WSL2 的 Linux 文件系统里（你的是 `~/projects/vlm-perception-reward-rl`，在 Windows 里看是
`\\wsl.localhost\Ubuntu\home\xde10\projects\vlm-perception-reward-rl`）。这样 git 更快，也不会遇到 Windows 换行符问题。
已经有了就跳过这一步；没有的话：

```bash
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/XDE10/vlm-perception-reward-rl.git
cd vlm-perception-reward-rl
```

以后每次运行前先更新到最新的 master：

```bash
cd ~/projects/vlm-perception-reward-rl && git checkout master && git pull
```

### 2. 告诉运行器数据在哪里

`data/` 不在 git 里。运行器只读取其中一小部分（已批准数据、相应图片、InterGPS 标注；打包压缩后约 21 MB），
逐个校验 SHA 后打包；**不会修改原数据**。数据就在本仓库的 `data/` 下时（你现在就是这样），这一步可以跳过。
否则在仓库根目录建一个本地设置文件（已被 git 忽略；它由运行器的 bash 读取，里面的 `#` 行是注释）：

```bash
cat > .colab_local.env <<'EOF'
# 原项目 data/ 目录的位置（Windows 盘符在 WSL 中是 /mnt/<盘符小写>/...，路径含中文或空格时保留引号）
P3_DATA_ROOT="/mnt/d/Users/Mr.Z/Desktop/项目三_多模态几何推理/data"
# 如需给 colab 传全局参数（例如认证方式），写在这里；不需要就留空
COLAB_GLOBAL_FLAGS=""
EOF
```

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

S2 预检（约 30–60 分钟，上一次约 28 分钟）：

```bash
bash colab/launch.sh preflight
```

运行期间终端会持续打印进度行。正常结束时，最后会打印摘要的前 30 行，并给出结果分支的链接。
然后在聊天里告诉我“跑完了”即可，我会从结果分支读取全部数据，不需要你贴日志或摘要。
运行在任务开始前就失败了（例如申请不到 VM、上传或安装失败）也一样：运行器会把日志推到同一个
`results/<run_id>` 分支（附一个 `RUN_STOPPED_EARLY.txt`），告诉我“失败了”即可。

S3 的 `v0` 任务（约 1–1.5 小时，15–25 CU；只在 A100 40/80 GB 或 H100 上运行，显存不足 40 GB 时 VM 会在安装环境前停下）：

```bash
bash colab/launch.sh v0 --session p3
```

它依次检查评测输入（下载固定版本的公开数据、按预注册规则重建评测集定义、由补丁重建 CF-Geo 图像），在 train 上测量
提示、格式预热和长度的决策，做 V0 在 82 道 validation 上的诊断，走一遍 S5 的评测代码，最后用 3 步 vLLM 训练检查重要性采样，
把决策写进 `s3_decisions.json`。不用 `--session` 时运行器会新建 VM，同样可用。

S4 的试跑（约 1.5–2.5 小时）与正式训练（每次一台 VM 的剩余时间，约 23 小时以内）。两者都只在 NVIDIA A100-SXM4-40GB 上运行，
而且需要 VM 上能用 Google Drive，所以都用第八节准备好的 VM（不带 `--session` 时运行器直接拒绝，不会新建 VM）：

```bash
bash colab/launch.sh pilot --session p3
bash colab/launch.sh train --session p3
```

先运行 `pilot`，它的门槛全部通过后才运行 `train`（`train` 会自己核对）；`train` 每次跑到 VM 时间用完为止，需要再次运行。
详见第九节。

常用选项：

| 选项 | 作用 |
|---|---|
| `--gpu H100` | 申请 A100 失败（没有配额或暂时没有空闲）时改用 H100；同一批实验请保持同一种 GPU。S4 的 `pilot` 与 `train` 只在 A100-SXM4-40GB 上运行（D54），不能换 |
| `--session p3` | 在你准备好的 VM 上运行（第八节）；不新建、默认也不释放这台 VM |
| `--release` | 和 `--session` 一起用：结束后释放你那台 VM |
| `--no-vllm` | 跳过可选的 vLLM 探测（省约 15 分钟）；对 `v0` 来说，跳过后重要性采样检查记为未测量，S4 按规则改用 HF 生成。`pilot` 和 `train` 不接受这个选项 |
| `--max-hours 10` | 只用于 `train`：本次最多运行 10 小时；预计在这之前跑不完的任务不开始，到时仍在运行的任务停下（下次从 Drive 上的 checkpoint 继续） |
| `--vm-hours 24` | 只用于 `train`：VM 的最长寿命，从 VM 启动算起（默认 24）；`0` 表示不按 VM 寿命限制 |
| `--keep` | 结束后不释放运行器新建的 VM（排查问题用，记得之后 `stop`） |
| `--no-vm-push` | 即使 VM 上有 GitHub 凭据，也由本机推送结果 |
| `--allow-dirty` | 允许在有未提交代码改动时运行；改动的 diff 会随结果一起上传 |

退出码：`0` 表示任务通过；`3` 表示任务跑完但未通过（结果照常推送，我来分析）；`1` 表示运行器本身出错。

## 三、断线、中断与恢复

- **按 Ctrl-C 或关掉终端**：只是断开连接，VM 上的任务会继续跑完。在准备好的 VM 上（第八节），任务结束时 VM 会自己把结果推到 GitHub，你可以不管它。
- **重新连上并取回结果**：`bash colab/launch.sh collect <run_id>`。它会等任务结束，然后取回结果、推送结果，并释放运行器新建的 VM。
  如果 VM 已经被 Colab 回收，但 VM 在那之前推送过结果，`collect` 会直接用 GitHub 上的那份。
- **主动释放 VM**（不要结果了）：`bash colab/launch.sh stop <run_id>`
- **查看本地记录的所有运行**：`bash colab/launch.sh list`
- **只是推送失败**（例如凭据问题）：修好后运行 `bash colab/launch.sh push <run_id>`。

`<run_id>` 形如 `preflight-20261110T093000Z-ab12`，运行开始时会打印出来，也可以用 `list` 查到。

## 四、结果在哪里

- 本地：`.colab_runs/<run_id>/results/<run_id>/`。`summary.md` 是给人看的摘要，`summary.json`
  是机器可读的全部数字，`logs/` 是每个步骤的完整日志。
- GitHub：分支 `results/<run_id>` 下的 `reports/colab_runs_<日期>/<run_id>/`。本地的启动日志与计算单元用量
  在其中的 `_local/` 目录。VM 自己推送时，这个分支上有两个提交：VM 推的结果（作者 `p3-colab-vm`），
  以及运行器随后补上的 `_local/`。
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
5. **收尾**：生成 `summary.md`，打包结果（不含权重）并按 2 MB 分片。VM 上有 GitHub 凭据时，VM 先自己推送
   `results/<run_id>`（第八节）；否则运行器取回分片、校验，再从本机推送。然后释放运行器新建的 VM。
   推送前会把日志里形似凭据的字符串（例如 CLI 报错网址里的 `colab-runtime-proxy-token`、网址里的 `用户:令牌@`）
   替换成 `REDACTED`，替换记录在 `_local/REDACTIONS.txt`（VM 推送的部分在 `REDACTIONS_VM.txt`）；
   你本机 `.colab_runs/` 里的原始日志不变。

## 六、常见问题

| 现象 | 处理 |
|---|---|
| `could not allocate a A100 VM after 10 tries` | 暂时没有 A100 或没有配额。运行器每次只让 CLI 尝试一次（`COLAB_CLI_ASSIGN_RETRIES=0`），每次之间等 60 秒，并逐次打印“第几次、已经等了多久、CLI 的最后一行错误”。稍后重试，或加 `--gpu H100`；次数和间隔可用 `P3_ALLOCATE_TRIES`、`P3_ALLOCATE_WAIT` 调整。想看 CLI 自己的进度，在 `.colab_local.env` 里加 `COLAB_GLOBAL_FLAGS="--logtostderr"`，输出会进 `launch.log` |
| `WARNING: Colab reports N active assignment(s)` | 运行开始前 Colab 显示的活动分配比预期多（新建 VM 时预期 0 个，`--session` 时预期 1 个），可能有别的 VM 在消耗计算单元。按提示用 `colab sessions` 查看，`colab stop -s 名字` 停掉不用的 |
| `the job did not start on the VM (try 1/3)` | 启动任务的那次连接在任务开始前断了（例如 `RuntimeError: Connection was lost.`）。不用处理：运行器确认 VM 上没有这次运行的锁文件后会重新启动任务；VM 端保证同一次运行只启动一次 |
| `this task needs a GPU with at least 40 GB` | 这台 VM 的 GPU 太小（例如 L4、T4）。`v0` 及之后的训练、评测只在 A100 40/80 GB 或 H100 上运行：`colab stop -s p3` 后用 `colab new -s p3 --gpu A100` 重新准备 |
| `data check` 报 `missing` / `hash changed` | `P3_DATA_ROOT` 路径不对，或数据被改动过。先确认路径；如果确实被改动，把 `check` 的输出发给我 |
| `uncommitted changes in code directories` | 你改过代码但没提交。提交后再运行，或加 `--allow-dirty` |
| `git push failed` | 结果已安全保存在本地。修好凭据后运行 `bash colab/launch.sh push <run_id>` |
| `$'\r': command not found` | 脚本被转成了 Windows 换行。按第一节第 1 步在 WSL 里新 clone 一份 |
| 长时间没有输出 | 正常情况下每 60 秒至少有一行心跳。超过 10 分钟没有输出时，按 Ctrl-C，然后用 `collect` 重新连接 |
| `upload of ... failed` 反复出现 | 运行器会自动重试和补传。若整次运行仍停在上传，在 `.colab_local.env` 里加一行 `P3_PART_MB=1`（分片改为 1 MB）后重跑；`upload.log` 里有 CLI 的原始报错 |
| `the VM could not fetch or verify the code from GitHub` | 不用处理：运行器已自动改为上传代码 |
| `unknown option '#'` | 你在 zsh 里把 `# 注释` 写在了命令后面，zsh 会把它当成参数。删掉注释再运行 |
| `the VM could not push the results (...)` | 不用处理：运行器已改为从本机推送。括号里说明原因（例如凭据过期），下次准备 VM 时重新写入凭据 |
| `could not run code on session p3` | 这台 VM 不存在或已被回收。`colab sessions` 查看；需要的话按第八节重新准备 |

结束后运行 `colab sessions`，确认没有遗留的 VM 在消耗计算单元。准备好的 VM 不会被自动释放，用完运行 `colab stop -s p3`。

## 七、可选：把结果另存到 Google Drive

对 `preflight`、`v0` 等任务，不配置也完全可以：每次运行的结果都会推到 GitHub 的 `results/<run_id>` 分支。
S4 的 `pilot` 和 `train` 则必须有 Drive：checkpoint 和训练好的 adapter 存在 Drive 上，恢复也只从 Drive 恢复（第九节）。

规则（理由见 `docs/plan/决策记录.md` D31）：

- 训练只读写 VM 本地盘 `/content`。写进 Drive 一律用 `rclone copy`，再用 `rclone check --one-way` 核对大小和哈希，
  核对通过才算保存成功。**不通过 FUSE 挂载写入**：往挂载点写文件，`write()` 返回时上传可能还没完成。
- 只写 `mydrive:ColabProjects/vlm-perception-reward-rl/` 之下：预检时是 `runs/<run_id>/`（结果包与 `package.json`），
  探针用 `_p3_probe/<run_id>/`，并且只删除它自己刚写的文件。
- Drive 出任何问题都不会让运行失败，只在终端里打印一行警告。

**推荐做法**：按第八节在 VM 的终端里手动挂载（你现在的做法），然后用 `--session` 在那台 VM 上运行。
运行器在 VM 上找到 `rclone` 和远端 `mydrive:` 就会使用，不需要在本机配置任何东西。

在准备好的 VM 上先试一次 Drive 和 GitHub 凭据（约 3 分钟，不装 GPU 环境）：

```bash
bash colab/launch.sh drive-check --session p3
```

它在 Drive 上写一个小文本和一个 16 MB 随机文件，读回比对 MD5、跑 `rclone check`，再删掉；
有挂载点时，还会测一个经挂载写入的文件要多久才出现在远端。结果在摘要的 “Google Drive” 一节；
同一份摘要的 “结果推送到 GitHub” 一节说明 VM 能否自己推送。之后每次 `preflight` 也会做同样的 Drive 探测
（不计入通过与否），并在结束时把结果包复制到 Drive，终端里会显示 `Drive copy verified: ...` 或一条警告。

**备用做法**（新建 VM 时自动挂载）：在 `.colab_local.env` 里设置下面两项之一。这个文件由运行器的 bash 读取，
不要把这些行粘贴到终端里：

```bash
P3_DRIVE_MOUNT_CMD='本机上能给会话 {session} 挂载 Drive 的命令'
P3_DRIVE_SETUP_FILE="$HOME/colab_drive_setup.py"
```

`P3_DRIVE_MOUNT_CMD` 是本机上的一条命令，`{session}` 会被替换成本次 VM 的会话名（也可以用环境变量 `$P3_SESSION`）；
`P3_DRIVE_SETUP_FILE` 是一个 Python 文件，运行器会在新 VM 上执行它。两者的输出只写到本机的
`.colab_runs/<run_id>/drive_mount.log`，**不会推到 GitHub**，命令本身也不写进日志，因为里面可能有凭据。
用 `--session` 时这两项会被跳过。远端名、Drive 上的目录和挂载点一般不用改，需要时设
`P3_DRIVE_REMOTE`、`P3_DRIVE_DIR`、`P3_DRIVE_MOUNT`。

## 八、准备好的 VM：Drive 挂载 + 由 VM 直接推送结果

适合长时间任务。你在 VM 上亲手挂载 Drive、写入 GitHub 凭据；运行器在这台 VM 上跑任务，任务结束时由 VM 自己把结果推到
`results/<run_id>`，运行器还连着的话再补上本机日志 `_local/`。规则（理由见 `docs/plan/决策记录.md` D37、D38）：

- 凭据只由你输入。运行器不读取、不传输、不记录它；VM 上的 git 通过 `credential.helper=store --file=/content/gh_credentials`
  使用它，推送前会先把结果里形似凭据的字符串替换成 `REDACTED`。
- 任务开始时，VM 会先用 `git push --dry-run` 验证写权限（不写入任何东西）。凭据缺失、过期或没有写权限时，
  改由你本机推送，照常完成。
- 运行器不会释放这台 VM（加 `--release` 才释放），用完请运行 `colab stop -s p3`。
- 同一台 VM 上再跑一次时，VM 上已有且 SHA256 相同的数据分片不再上传，环境和模型也会复用。

下面的会话名用 `p3`，可以换成别的名字，前后一致即可。

**1. 新建 VM**（在 WSL2 里）：

```bash
colab new -s p3 --gpu A100
```

**2. 把 rclone 配置传到 VM**（只在要用 Drive 时需要）。用你平时的方式把它传成 `/content/.colab-drive-rclone-upload.conf`；
如果 WSL2 里的 rclone 配置在默认位置，也可以直接：

```bash
colab upload -s p3 ~/.config/rclone/rclone.conf /content/.colab-drive-rclone-upload.conf
```

**3. 进入 VM 的终端**（在 WSL2 里）：

```bash
colab console -s p3
```

出现 `root@...:/content#` 之后，下面两段**在 VM 里**执行（VM 的 shell 是 bash，可以带注释）。

挂载 Drive（只在要用 Drive 时需要），最后一行必须输出 `/content/mydrive is a mountpoint`：

```bash
mkdir -p ~/.config/rclone
mv /content/.colab-drive-rclone-upload.conf ~/.config/rclone/rclone.conf
chmod 600 ~/.config/rclone/rclone.conf
command -v rclone >/dev/null || { apt-get update && apt-get install -y rclone fuse3; }
mkdir -p /content/mydrive
rclone mount mydrive: /content/mydrive --vfs-cache-mode writes --vfs-cache-max-size 10G --daemon
mountpoint /content/mydrive && ls -la /content/mydrive
```

写入 GitHub 凭据（输入时不回显；需要对本仓库有写权限的 PAT）：

```bash
read -rsp 'Enter GitHub PAT: ' PAT; echo
printf 'https://XDE10:%s@github.com\n' "$PAT" > /content/gh_credentials
chmod 600 /content/gh_credentials
unset PAT
```

然后输入 `exit` 回到 WSL2。

**4. 可选：检查这台 VM**（约 3 分钟）：

```bash
bash colab/launch.sh drive-check --session p3
```

**5. 运行任务**（在 WSL2 里；S3 阶段的任务是 `v0`）：

```bash
bash colab/launch.sh v0 --session p3
```

终端里出现 `GitHub: the VM will push the results ... (write access verified)` 表示 VM 会自己推送；
结束时出现 `the VM pushed the results itself` 表示已推送。之后告诉我“跑完了”即可。

**6. 用完释放**：

```bash
colab stop -s p3
```

## 九、S4：试跑与正式训练

规则见 `docs/plan/S4预注册_20261110.md`（第 8–12 节）。两个任务都在第八节准备好的 VM 上运行：GPU 必须是
NVIDIA A100-SXM4-40GB（不是的话 VM 在安装环境前就停下），Drive 必须挂好（checkpoint 要复制到 Drive，恢复也只从 Drive 恢复），
最好也写入 GitHub 凭据（长任务时结果由 VM 自己推送，你的电脑可以休眠）。

**1. 准备 VM**：按第八节第 1–3 步新建 `p3`、上传 rclone 配置、在 VM 里挂载 Drive 并写入 PAT。Google Drive 要有至少
10 GB 空闲（见本节末尾）。

**2. 试跑**（约 1.5–2.5 小时，只用 train，结果不进入任何分析）：

```bash
bash colab/launch.sh pilot --session p3
```

它先跑完整 CPU 测试、核对登记表与这台 VM 上的数据、检查 Drive 和 vLLM 环境，然后依次运行：`pilot_v5`（`rl_v5` 正式形状 40 步，
第 20、40 步的 checkpoint 复制到 Drive 并核对）、`pilot_resume`（小形状，第 1 步后停下，从 Drive 取回 checkpoint-1 再恢复到第 2 步）、
另外四组各 3 步，必要时再跑 76 步的 G4 重试，最后按预注册第 11 节判定 G1–G6。结论写进结果里的 `pilot_gates.json`，
同时写成 Drive 上的 `s4/rl_v3_p1_20261110/PILOT_LATEST.json`（通过或不通过都写）。摘要的“S4 试跑门槛”一节逐条列出结果。
告诉我“试跑跑完了”，我读结果后告诉你能否开始正式训练。

**3. 正式训练**（门槛全部通过之后）：

```bash
bash colab/launch.sh train --session p3
```

- 开始前它核对：Drive 上最新的试跑通过了，登记表、冻结的运行时、训练代码和包版本都与那次试跑相同（代码冻结）；
  第一个正式任务开始时写下代码基准，之后每个任务都必须与它相同。任何一项不符就一个任务也不开始。
- 按登记顺序（种子 1 的五组，然后种子 2，最后种子 3 的两组）逐个处理：Drive 上已完成或已失败的跳过；
  另一台 VM 正在跑的跳过；跑到一半的从 Drive 上最新一个已核对的 checkpoint 恢复；其余从头开始。
- 每个任务开始前估计它要多久（按试跑实测的步时），在这台 VM 的剩余时间里跑不完就不开始，本次运行到此结束。
  VM 快到期时（默认按启动后 24 小时算，提前 30 分钟）仍在运行的任务会停下，下次从它最新的 checkpoint 继续。
- 2026-11-29 00:00 UTC 之后、或计算单元余额（按本次开始时 `colab usage` 的余额和费率推算）低于 150 时，不再开始新任务；
  已经开始的任务照常恢复和跑完。
- 每 38 步的 checkpoint 写完就在后台复制到 Drive 并核对，训练不等它；Drive 上每个任务只保留最新一个已核对的 checkpoint。
  任务结束后 `final/`（第 228 步的 adapter）和运行文件也复制到 Drive 并核对，然后写 `COMPLETED.json`。
- 训练本身出错（显存不足、loss 为 NaN 等）时，按预注册只重启一次（从最新的 checkpoint）；第二次出错记为失败（`FAILED.json`）。

一次 `train` 跑完后（或 VM 到期后），重新准备 VM（第八节第 1–3 步）并再次运行同一条命令，直到摘要里说没有任务可做了。
想同时用两台 A100 时，另准备一台（例如 `p3b`）并运行 `bash colab/launch.sh train --session p3b`：两台 VM 通过 Drive 上的认领文件
（`claims/`）分开各自的任务，不会跑同一个任务。每次运行结束后告诉我“跑完了”和 run_id，我从结果分支读取。

**Drive 上的文件**（`mydrive:ColabProjects/vlm-perception-reward-rl/s4/rl_v3_p1_20261110/`）：

| 路径 | 内容 |
|---|---|
| `PILOT_LATEST.json` | 最新一次试跑的结论；`pilot/<run_id>/` 是各次试跑的文件 |
| `code_baseline/<run_id>.json` | 第一个正式任务开始时的训练代码 SHA256 |
| `<组>/seed<k>/checkpoint-<步>/` | 最新一个 checkpoint；里面的 `DRIVE_VERIFIED.json` 在核对通过后才写，恢复只用有它的 checkpoint |
| `<组>/seed<k>/final/` 与 `COMPLETED.json` | 训练完成的 adapter；S5 只评测它 |
| `<组>/seed<k>/STARTED.json`、`failures/`、`FAILED.json`、`claims/` | 开始记录、计算失败记录、第二次失败的标记、正在运行的 VM 的认领 |

这些文件都由运行器写；请不要手动改动或删除，否则恢复和核对会出错。运行器只删除两样东西：同一任务更旧的 checkpoint
（新的核对通过后），以及它自己的认领文件。旧 checkpoint 是永久删除，不进 Drive 的回收站（回收站里的文件仍占配额）。
全部任务跑完后约占 7–9 GB（估计：每个任务保留一个约 0.36 GB 的 checkpoint、约 0.12 GB 的 `final/` 和 rollouts，另有试跑），
所以开始前请确认 Drive 至少有 10 GB 空闲；`train` 开始或恢复一个任务前检查 Drive 剩余空间，不足 2 GB 就停下并在摘要里说明。

**结果分支**：每个任务的 `runs/<组>_seed<k>/` 下有运行身份、训练摘要、日志历史、压缩后的 `rollouts.jsonl.gz` 和每次尝试的
`train.log`；`train_job.json` 是本次运行的计划和每个任务的结果。权重和 checkpoint 只在 Drive 和 VM 上。

## 十、S5 正式终评

在挂好 Drive 的 A100-SXM4-40GB 上运行 `bash colab/launch.sh final-eval --session p3 --release`。
入口先核对登记任务在 Drive 上的终态，只评测配置和运行时哈希匹配的 `final/`，并按同一协议评测 V0。正式任务仍在运行或待跑时会退出。

按 [S3 设计](../docs/plan/S3设计_20261109.md) 和 [S4 预注册](../docs/plan/S4预注册_20261110.md) 使用 P1、HF 贪心、1024 token、固定 32 条批次和未合并 LoRA。
每个模型与条件的逐题结果核对后保存在 Drive 的 `s5/predictions/`。VM 中断后，用同一代码提交和环境重跑命令会复用已核对的条件。
结果分支的 `s5/` 包含任务清单、逐题文件的 Drive 路径和 SHA256、九项主比较的区间与 Holm 校正、逐种子及次要结果。

Geometry3K 的次要 InterGPS FALSE 率以可解析的去重断言为分母，使用训练同源的几何证伪器。
MathVista testmini 使用原题、选项和单位字段组成提示，以项目的答案段抽取和确定性判分报告全量、GPS 和去 Geometry3K 来源三组结果。
