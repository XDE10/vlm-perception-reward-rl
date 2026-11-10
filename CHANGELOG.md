# 变更记录

本文件记录仓库结构、文档与验证状态的变更。训练/数据事实的变化以
[README](README.md) 和版本化报告为准；历史细节见
[docs/migration/](docs/migration/)。

## 2026-11-09 — S3 实施：评测集、CF-Geo、统一评测路径、统计与 `v0` 任务

决策见 [决策记录](docs/plan/决策记录.md) D47–D51，阶段报告见
[docs/plan/阶段报告_S3_实施_20261109.md](docs/plan/阶段报告_S3_实施_20261109.md)，规则修订见
[S3 设计](docs/plan/S3设计_20261109.md) 第 11 节。没有 GPU 运行，没有改动已批准数据。

- 新增 `src/evaluation/eval_sets.py`、`public_sources.py`、`cfgeo.py`、`harness.py`、`stats.py` 与 `scripts/data/build_eval_sets.py`、
  `scripts/data/build_cfgeo.py`。
- 新增 `reports/eval_sets_20261109/`（test 视觉必需 388 题，CF 候选 224 题）和 `reports/cfgeo_20261109/`（CF-Geo 158 题，
  补丁与像素哈希，不含原图；两轮看图抽查）。
- 新任务 `bash colab/launch.sh v0`：评测输入核对、train 上的提示/预热/长度测量、V0 在 val82 上的诊断、评测路径检查、
  vLLM 重要性采样检查，输出 `s3_decisions.json`。
- 运行器：申请 VM 逐次重试并打印进度；任务在开始前断开时安全地重新发送（VM 端锁文件）；运行前多余的 Colab 分配会报警；
  `v0` 要求 GPU 至少 40 GB；用 vLLM 训练前检查训练图的 patch 网格。
- 提示变体 P1 与只要答案的诊断提示；`generate()` 支持提示变体，评分支持答案集合。
- 测试：274 passed / 2 failed，两项失败依赖本机 `data/`。

## 2026-11-09 — S2 验收与 S3 设计：接受冻结的运行时，修正 vLLM 重要性采样，预注册评测规则

决策见 [决策记录](docs/plan/决策记录.md) D41–D46，阶段报告见
[docs/plan/阶段报告_S2_验收_20261109.md](docs/plan/阶段报告_S2_验收_20261109.md)，评测规则见
[docs/plan/S3设计_20261109.md](docs/plan/S3设计_20261109.md)。没有 GPU 运行，没有改动已批准数据。

- 第三次预检 `preflight-20261109T122305Z-e6cd` 18/18 通过；它冻结的运行时原样复制为
  `configs/experiments/runtime_frozen_20261109.json`（vLLM、微批 8、ViT 缓存关闭、梯度检查点），只用于 A100 40/80 GB 和 H100。
- vLLM 的重要性采样修正从 TRL 默认的 `sequence_mask`（上限 3）改为 `token_truncate`（上限 2.0），写在 `rl_v3.json`，进入配置哈希。
  预检中默认设置让每步平均权重只有 0.29–0.55。
- 新增 `reports/certified_fact_errata_20261109/`：校准中被几何检验否定的认证事实逐张看图核对，12 行是认证事实本身错了，
  几何检验真正的误杀约 0.4%。release 不变。
- 新增 `reports/s3_planning_estimates_20261109/`：S3 规则在 train 上的数量估计与 CF-Geo 原型（不读 validation 和 test）。
- S3 设计：评测集、视觉必需子集、CF-Geo 规则（含取整题的集合判分）、主终点、统计方法、只用 train 的决策规则、`v0` 任务。
- 测试：228 passed / 2 failed，两项失败依赖本机 `data/`。

## 2026-11-09 — S2.3：结果由 VM 直接推送，支持准备好的 VM，命令兼容 zsh

决策见 [决策记录](docs/plan/决策记录.md) D37–D40，阶段报告见
[docs/plan/阶段报告_S2.3_20261109.md](docs/plan/阶段报告_S2.3_20261109.md)。没有 GPU 运行，没有改动已批准数据。

- 新增 `scripts/colab/vm_github.py`：你放在 VM 上的 GitHub 凭据存在时，由 VM 推送 `results/<run_id>`（开始时 dry-run
  验证写权限，推送前脱敏）；运行器从不读取凭据。凭据缺失或推送失败时由本机推送；VM 推送后，运行器再补上 `_local/`。
- `colab/launch.sh` 新增 `--session NAME`（在你准备好的 VM 上运行，不新建、默认不释放）、`--release`、`--no-vm-push`。
  VM 上已有的相同分片不再上传。任务开始前失败的运行会把日志推到 GitHub。VM 不可达时，用 GitHub 上已有的结果完成收尾。
- 脱敏新增网址中的 `用户:令牌@` 与 `github_pat_...`；二次脱敏不会重复计数。
- `colab/README.md`：命令兼容 zsh（去掉命令行末尾的 `#` 注释），新增第八节（Drive 挂载、写入 PAT、`--session`）。
  新增测试检查 README 命令块；新增 `.kiro/steering/colab-environment.md`，记录你的环境。
- 测试：226 passed / 2 failed，两项失败依赖本机 `data/`。

## 2026-11-09 — S2.2：修复第二次预检的失败，改校准口径

决策见 [决策记录](docs/plan/决策记录.md) D33–D36，阶段报告见
[docs/plan/阶段报告_S2.2_20261109.md](docs/plan/阶段报告_S2.2_20261109.md)。没有 GPU 运行，没有改动已批准数据。

- 修复 TRL 评分前向的图像 token 类型错位：TRL 1.17.1 用处理器默认（右）填充重建 `mm_token_type_ids`，`prompt_ids` 却是左填充，
  导致 M-RoPE 位置错误或 shape mismatch。入口改为先把处理器设成左填充，并新增 `src/training/multimodal_guard.py`，
  每次前向检查类型与图像 token 一致，不一致就停止。
- 修复断点恢复的身份不一致：LoRA 目标模块列表在写入运行身份前排序（PEFT 存成 set，顺序随进程变化）。
- 感知奖励 v5.1：新增一致性门控（标注否定了自身认证事实的图，同类检验不再参与证伪）。校准新增门控统计、门控后误杀、
  留一法残余误杀率（Wilson 区间）与每条误杀的测量值；预检的校准检查从“零误杀”改为“门控后零误杀，且每类留一法 ≤ 5%”。
  阈值不变。
- `decide_runtime` 在 HF 冒烟未通过时记为跳过；GPU 探针增加 ViT 成批与单张的相对误差。
- 测试：216 passed / 2 failed，两项失败依赖本机 `data/`。

## 2026-11-09 — S2.1：修复预检上传失败，加可选 Google Drive

决策见 [决策记录](docs/plan/决策记录.md) D28–D32，阶段报告见
[docs/plan/阶段报告_S2.1_20261109.md](docs/plan/阶段报告_S2.1_20261109.md)。下面 S2 条目标注的 2026-11-10
实为 2026-11-09（D28）。没有 GPU 运行，没有改动已批准数据。

- 首次真实预检在上传第 4 个 8 MiB 分片时连续 3 次约 150 秒后失败。上传与结果下载改为 2 MiB 分片；
  每片最多 6 次尝试、有退避，每次 CLI 调用有墙钟上限，CLI 输出保存到 `upload.log`；
  传完后在 VM 上逐片核对大小与 SHA256，只补传有问题的分片（新增 `colab/kernel_inbox.py`）。
- 提交已在 GitHub 上时，VM 自己下载源码包并逐文件比对 git blob SHA-1，失败时自动改为上传代码（部分取代 D18）。
- 新增可选 Google Drive 持久化 `scripts/colab/drive.py`（只用 `rclone copy` + `rclone check`，不经 FUSE 挂载写入），
  新命令 `bash colab/launch.sh drive-check`，预检新增不计入结论的 `drive_probe` 步骤，结束时可把结果包复制到 Drive。
- 推送结果分支前对日志做凭据脱敏（CLI 报错网址里带运行时代理 token），记录在 `_local/REDACTIONS.txt`。
- 修复 `tools/build_migration_manifest.py --git-tracked-only`：同一天的刷新会删掉其他阶段的 `documentation_updates`
  条目（S1 引入）。带缺陷的清单没有提交过。
- 测试：205 passed / 2 failed，两项失败依赖本机 `data/`。

## 2026-11-10 — S2：Colab 运行器

决策见 [决策记录](docs/plan/决策记录.md) D18–D27，阶段报告见
[docs/plan/阶段报告_S2_20261110.md](docs/plan/阶段报告_S2_20261110.md)。没有 GPU 运行，没有改动已批准数据。

- 新增 `colab/launch.sh`（`check`、`preflight`、`collect`、`push`、`stop`、`list`）和使用说明 `colab/README.md`；
  在 Colab 内核中执行的是 `colab/kernel_bootstrap.py` 与 `colab/kernel_job.py`。
- 新增 `scripts/colab/`：
  - 私有数据打包与复核：三类锚点，标准库实现；
  - VM 引导：按驱动的 CUDA 版本选锁文件建隔离 venv，下载固定 revision 的模型并记录每个文件的 SHA；
  - 任务执行器：独立进程组、超时、心跳、原子 `status.json`、结果分片；
  - 预检步骤：环境报告、GPU 探针、V0 探针、运行时决策、摘要。
- 新增 `requirements/colab-gpu*.txt` 与 `requirements/locks/`：用 uv 预先解析的 cu130、cu129、cu126，以及 vLLM cu130 锁文件。
- 新增 `src/evaluation/generate_v3.py`：协议 v3 的批量生成与评分，解码设置固定在代码里。
- 统一入口新增不改变算法的运行时选项（微批切分、梯度检查点、vLLM 长度），其他运行时键会被拒绝。
- ViT 缓存改为修补真正持有视觉塔的模块，不再修补外层包装。
- 新增 `.gitattributes`（`*.sh` 与 Colab 脚本固定使用 LF）；`.gitignore` 新增运行器的本地目录。
- 测试：188 passed / 2 failed，两项失败都依赖本机 `data/`。

## 2026-11-09 — S1：修复审计问题，新增协议 v3 统一 GRPO 入口

按 [执行计划](docs/plan/执行计划_20261108.md) 第 4 节逐项修复，决策见
[决策记录](docs/plan/决策记录.md) D1–D17。没有 GPU 运行，没有改动已批准数据或冻结的 v4 评分。

- 新增 `src/rewards/`：逐条断言解析（坏条只算一个 FALSE，不再整段归零）、InterGPS 几何证伪、
  可证伪感知奖励 v5、math_verify 常驻进程池、罗列攻击探针。
- 新增协议 v3（perception → think → answer，所有组共用，恢复推理段）与统一入口
  `scripts/training/train_rl.py`；`configs/experiments/` 用基础配置加组别白名单覆盖，保证组间只在声明因素上不同。
- 修复：LoRA 改为按精确模块名只挂语言模块，并在运行时断言 ViT/merger 冻结（旧入口同样修复）；
  多奖励改用 `scale_rewards=batch`，避免组内标准化抹掉 λ；每步 8 题 × 8 条采样、整批生成；
  格式奖励要求 perception 非空且可解析；每条 rollout 落盘。
- 兼容：transformers 5 移除了 `AutoModelForVision2Seq`，旧入口与诊断脚本改用兼容类。
- 新增 `scripts/data/calibrate_perception_v5.py`（阈值校准与攻击表）、`requirements/dev-cpu.txt`、
  `tools/build_migration_manifest.py --git-tracked-only`。
- 测试：沙箱（无 `data/`）下 172 passed / 2 failed，两项失败都依赖本机 `data/`，见
  [docs/verification.md](docs/verification.md)。

## 2026-11-08 — 仓库整理（目录结构、文档与校验入口）

本次只做结构、文档与元数据整理，**没有**重新训练、重新审核数据或扩大批准范围。

结构变化：

- 新增 [docs/](docs/)：当前说明页（[repo_layout](docs/repo_layout.md)、
  [architecture](docs/architecture.md)、[data](docs/data.md)、
  [training](docs/training.md)、[verification](docs/verification.md)）。
- `project_blueprints/` → [docs/blueprints/](docs/blueprints/)（历史方案与配置留档）。
- `迁移记录/` → [docs/migration/](docs/migration/)，并加入
  [整理记录](docs/migration/整理记录_20261108.md)。
- 根目录说明文档归档：`OVERNIGHT_CPU_README.md` →
  [docs/migration/overnight_cpu_20261023.md](docs/migration/overnight_cpu_20261023.md)
  （旧三项目 CPU 栈历史说明），深度审查提示词 →
  [docs/guides/argon_review_prompt.md](docs/guides/argon_review_prompt.md)。
- `requirements-cpu-snapshot.txt` / `requirements-project3-cpu.txt` →
  [requirements/cpu-snapshot.txt](requirements/cpu-snapshot.txt) /
  [requirements/project3-cpu.txt](requirements/project3-cpu.txt)。
- `scripts/` 按职责分组为 `common/`、`data/`、`training/`、`reporting/`、
  `migration/`，并补充 [scripts/README.md](scripts/README.md) 目录；
  入口命令相应变为 `python -m scripts.<group>.<name>`。
- `pytest.ini` 合并进 [pyproject.toml](pyproject.toml)。
- 新增 `data/`、`reports/`、`configs/`、`requirements/` 目录说明；
  新增 [tools/check_links.py](tools/check_links.py) 与
  [tools/build_migration_manifest.py](tools/build_migration_manifest.py)。
- `reports/` 与 `data/` 的物理布局保持冻结（追加式证据与已发布哈希引用），
  只增加索引说明。

校验与事实：

- 本机 Python 3.11.4：`pytest -q` 74 passed / 2 failed，两个失败都是环境缺包
  （`math_verify`、`trl`），不是代码回归；项目文档记载的 Python 3.12 环境
  本次未复验。
- 追加 [tests/test_repo_layout.py](tests/test_repo_layout.py) 结构回归测试（6 项），
  固定“scripts/ 无平铺脚本、分组均为包、README 覆盖全部脚本、当前入口文件存在、
  pytest 配置指向 tests/、configs 相对路径+固定 revision”；更新
  [docs/guides/argon_review_prompt.md](docs/guides/argon_review_prompt.md) 中
  的审查阅读路径到整理后布局。
- `python tools/verify_migration.py --full`：见
  [整理记录](docs/migration/整理记录_20261108.md) 的实测记录。
- 没有 GPU 训练产物；`runs/` 不存在，2 步 smoke 仍只是工程配置。

## 2026-11-08 — 与其他两个项目彻底分离（清理）

- 删除项目一/二残留 237 条路径（约 90 MB），包括 `src/synthesis/`、
  `.pilot_deps/`、`agentic_rl/`、`math/`、`tiny_posttrain/`、`video_mapping/`、
  项目一/二专用脚本与测试；保留项目三数据、脚本、报告与迁移记录。
- 详见 [清理记录](docs/migration/清理记录_20261108.md)。
- `migration_manifest.json` 当时保持封板，因此校验会对已删除路径报缺失
  （见文件内说明与 [迁移验收](docs/migration/迁移验收.md)）。

## 2026-10-24 — 从 modern_genai 迁移为独立包

- 迁移项目三代码、数据、报告与历史蓝图；`migration_manifest.json` 记录
  4258 个负载文件的大小与 SHA256（含 source_sha256 溯源字段）。
- 迁移验收（2026-10-24）：离线校验通过，CPU 相关测试 15 passed；
  当时使用 Python 3.12 环境。
- 详见 [迁移验收](docs/migration/迁移验收.md)。
