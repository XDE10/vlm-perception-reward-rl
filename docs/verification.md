# 校验与测试

本页说明离线校验工具、测试基线、已知环境缺口和报告规范。结论必须区分
“离线完整性通过”“CPU 测试通过”“GPU 训练跑通”“能力提升”。

## 工具

| 工具 | 作用 | 典型命令 |
| --- | --- | --- |
| [tools/verify_migration.py](../tools/verify_migration.py) | 离线完整性：manifest 文件存在/大小/SHA、release SHA、批准行数、逐行输入白名单、图片相对路径与 SHA、配置相对路径 | `python tools/verify_migration.py` / `--full` |
| [tools/build_migration_manifest.py](../tools/build_migration_manifest.py) | 合法结构变更后重建当前树清单，保留 `source_sha256`/移动溯源 | `python tools/build_migration_manifest.py` |
| [tools/check_links.py](../tools/check_links.py) | 检查当前文档的相对链接（历史留档只告警） | `python tools/check_links.py` |
| `pytest` | 数据准入、序列化、奖励、解析、训练入口 CPU 行为 | `python -m pytest -q` |

`verify_migration.py` 可在任意工作目录用绝对路径调用（脚本自行定位包根），
但 `pytest` 建议从仓库根目录执行。校验通过**不证明** CUDA 训练、模型前后向或
新环境依赖已安装。

## migration_manifest.json 语义（schema_version 2）

- `files[]`：当前工作树的每个文件，记录 `path`、`bytes`、`sha256`。
- `source_sha256`：最近历史版本（同路径或 `moved_from` 路径）的 SHA256；新文件
  等于自身 SHA。
- `changed_for_portability`：当前字节与历史源不同（例如路径可移植化或文档更新）。
- `moved_from` / `added_in` / `updated_in`：本次整理的结构来源标记。
- `documentation_updates`：按日期记录文档/代码变更与移动映射；不再把已删除文件
  留在 `files[]` 里。
- 封板历史清单保留在
  [docs/migration/migration_manifest_分离同步前_20261108.json](migration/migration_manifest_分离同步前_20261108.json)
  与
  [migration_manifest_交接补充前_20261024.json](migration/migration_manifest_交接补充前_20261024.json)；
  2026-11-08 之前的删除事实见 [清理记录](migration/清理记录_20261108.md)。

以后合法修改文档/代码应说明变更并重跑校验；不要用批量重算训练数据 SHA 的
方式绕过数据准入。

## 测试基线

2026-11-08 在 Python 3.11.4 上实测（重构前基线与目录整理后复跑一致）：

```text
python -m pytest -q
68 passed, 2 failed in 39.91s   # 重构前基线
68 passed, 2 failed in 41.89s   # 2026-11-08 整理后复跑
74 passed, 2 failed in 15.94s   # 追加仓库结构回归测试后（同日）
```

两个失败均为环境缺包，不是代码回归：

| 测试 | 原因 |
| --- | --- |
| `tests/test_training_entries_cpu.py::test_bounded_real_math_reward` | 未安装 pip 包 `math_verify` |
| `tests/test_training_entries_cpu.py::test_actual_trl_group_policy_cpu` | 未安装 pip 包 `trl` |

在目标环境执行 `pip install math_verify trl` 后应重新运行并记录；不要在未复验时
把结果写成“全部通过”。项目文档记载的 2026-10-24 验收为 Python 3.12 下
15 passed，本次未在 3.12 复验。

### 2026-11-09（S1，协议 v3 统一入口）

在没有 `data/` 的 Linux 沙箱中，用 Python 3.12.13 和
[requirements/dev-cpu.txt](../requirements/dev-cpu.txt) 实测：

```text
python -m pytest -q
172 passed, 2 failed
```

| 失败的测试 | 原因 |
| --- | --- |
| `tests/test_delivery_artifacts.py::test_offline_demo_and_cpu_environment` | 沙箱没有 `data/synthesis_mock/cache.jsonl`（`data/` 不进 git） |
| `tests/test_repo_layout.py::test_configs_use_relative_paths_and_pinned_revision` | 沙箱没有 `data/portable_release/manifest.json` |

两项都依赖本机的 `data/`，不是代码回归；装好 `trl` 与 `math_verify` 后，原先因缺包失败的两项已通过。

新增测试覆盖：逐条断言解析、几何证伪（含真实图 1670 的坐标）、v5 奖励与罗列攻击、答案校验进程池、
协议 v3（含经 TRL 渲染后提示逐字一致）、语言 LoRA 与 ViT 冻结、旧入口修复回归、组别配置差异、
数据门控与安慰剂配对、奖励汇总与日志、ViT 缓存等价性、tiny Qwen2.5-VL 上的两步 GRPO 端到端与断点恢复、
v5 校准脚本，以及 manifest 的 `--git-tracked-only` 模式。依赖固定 revision processor 文件的测试在找不到
这些文件时跳过（设置 `HF_HOME` 或 `P3_QWEN_PROCESSOR_DIR` 指向缓存）。

### 2026-11-10（S2，Colab 运行器）

同一沙箱环境：`188 passed, 2 failed`，失败的仍是上面两项依赖 `data/` 的测试。新增的测试：

- `tests/test_colab_pack.py`：私有数据包。覆盖三类锚点、确定性打包、VM 端复核、篡改检测，以及拒绝不安全的归档成员。
- `tests/test_colab_launcher.py`：用 stub `colab` CLI 端到端跑 `launch.sh preflight --dry-run`。覆盖打包、分片上传、
  内核引导、任务步骤、结果取回与校验、释放 VM、推送结果分支到本地 bare 仓库；也覆盖实时连接断开后改为轮询，
  以及有未提交改动时拒绝运行。
- `tests/test_colab_vm_scripts.py`：CUDA 后端选择、运行时决策规则、摘要渲染；在 CPU 上用 tiny 模型跑通 GPU 探针与 V0 探针的全部代码路径。
- `tests/test_rl_entry_cpu.py` 新增两项：梯度检查点与 PEFT 的组合路径（GPU 运行使用它）、运行时微批切分，
  以及拒绝可能改变算法的运行时键。
- `tests/test_generate_v3.py`：批量生成（有图与无图）与评分。

还没有在真实 Colab GPU 上运行，这要靠 `bash colab/launch.sh preflight` 的结果来确认。

### 2026-11-09（S2.1，上传修复与可选 Google Drive）

上面 S2 小节标注的 2026-11-10 实为 2026-11-09（见决策 D28）。同一沙箱环境：

```text
python -m pytest -q
205 passed, 2 failed            # git 工作树
199 passed, 6 skipped, 2 failed # git archive 导出副本（与 VM 上相同；运行器端到端测试需要 git，跳过）
```

失败的仍是上面两项依赖 `data/` 的测试。新增或扩展的测试：

- `tests/test_colab_launcher.py`：在 stub `colab` CLI 上注入故障。覆盖上传卡死被时间上限结束、504 报错重试、
  写入不完整被远端 SHA256 核对发现并补传；从 file:// 源码包取代码，以及源码包被篡改时自动改为上传；
  推送前脱敏（stub 报错里的 token 不进结果分支）；CPU VM 上的 `drive-check`（Drive 入口的输出只留在本机）。
- `tests/test_colab_drive.py`：用 stub `rclone` 测试 Drive 检测、探针、持久化。覆盖损坏副本被 `rclone check` 拒绝、
  沿用正在运行的 `rclone mount` 的配置文件、runner 复制结果包，以及 Drive 失败不影响运行。
- `tests/test_colab_local_tools.py`：脱敏规则、分片比对、`git ls-tree -z` 解析（含中文路径）、分片大小上下限。

真实 Colab 上的上传、GitHub 源码下载和 Drive 仍未验证，要看下一次 `preflight` 和 `drive-check` 的结果。

### 2026-11-09（S2.2，第二次预检的修复）

第二次预检（preflight-20261109T064716Z-0589）证实：S2.1 的分片上传与 GitHub 取代码在真实 Colab 上可用；VM 上 pytest
207 项中 201 项通过、6 项跳过。同一沙箱环境：

```text
python -m pytest -q
216 passed, 2 failed
```

失败的仍是上面两项依赖 `data/` 的测试。新增的回归测试都在旧代码上失败、修复后通过：

- `tests/test_rl_entry_cpu.py::test_scoring_pass_keeps_image_token_types_aligned_under_left_padding`：4 张不同尺寸的图，
  走真实 TRL 路径。旧代码在评分前向报 `first image token at column 288 in input_ids, 216 in mm_token_type_ids`。
- `tests/test_lora_language.py::test_lora_targets_are_identical_across_processes`：两个 PYTHONHASHSEED 不同的进程必须得到相同的 LoRA 目标列表。

其他新增：`tests/test_multimodal_guard.py`；一致性门控与留一法的单元测试（`tests/test_perception_v5.py`、`tests/test_calibrate_v5.py`）；
预检摘要的新检查与 `decide_runtime` 依赖（`tests/test_colab_vm_scripts.py`）。迷你数据新增 `sizes` 参数，可以生成不等长的提示。

### 2026-11-09（S2.3，VM 直接推送与准备好的 VM）

同一沙箱环境：

```text
python -m pytest -q
226 passed, 2 failed
```

`git archive` 导出副本中是 216 passed / 10 skipped / 2 failed（10 项运行器端到端测试需要 git 工作树）。

失败的仍是上面两项依赖 `data/` 的测试。新增的测试：

- `tests/test_vm_github.py`：在本地 bare 仓库上验证 VM 端推送。覆盖 dry-run 不写入、提交的父提交与作者、超大文件不推送、
  文件内令牌脱敏、提交不存在时的失败报告。只用临时路径，不访问 GitHub；在 VM 上运行时也不会碰到真实凭据。
- `tests/test_colab_launcher.py` 新增四个端到端场景：准备好的 VM 由 VM 推送、VM 在任务后消失、准备好的 VM 没有凭据、
  任务开始前失败时推送日志。stub CLI 现在会拒绝不存在的会话，并能模拟 VM 被回收。
- `tests/test_colab_local_tools.py`：网址中的凭据、`github_pat_`、二次脱敏不重复计数。
- `tests/test_repo_layout.py::test_colab_readme_commands_are_zsh_safe`：README 命令块兼容 zsh。

### 2026-11-09（S2 验收：第三次预检）

真实 Colab GPU 上的结果（VM 上运行 pytest 时隐藏 GPU；`git archive` 导出的副本，运行器端到端测试需要 git 工作树，所以跳过）：

| 运行 | 代码 | pytest |
|---|---|---|
| `preflight-20261109T122305Z-e6cd` | `7afad4a`（S2.3） | 228 项：218 通过、10 跳过、0 失败 |
| `preflight-20261109T100727Z-eabd` | `a189e4a`（S2.2） | 218 项：212 通过、6 跳过、0 失败 |

两次预检的全部 18 个步骤都通过，包括 GPU 上的冒烟训练、断点恢复、对齐检查和 v5 校准；
详见 [S2 验收报告](plan/阶段报告_S2_验收_20261109.md)。这证明工程链路在 A100 上可用，不代表正式训练成功或能力提升。

同一沙箱环境（S2 验收与 S3 设计的改动之后）：

```text
python -m pytest -q
228 passed, 2 failed
```

失败的仍是上面两项依赖 `data/` 的测试。新增：`tests/test_experiment_configs.py` 中重要性采样设置进入配置哈希且只对 vLLM 生效（D41），
以及冻结运行时文件只含中性字段（D43）。

### 2026-11-09（S3 实施）

同一沙箱环境：

```text
python -m pytest -q
274 passed, 2 failed            # git 工作树
263 passed, 11 skipped, 2 failed  # git archive 导出副本（与 VM 上相同）
```

失败的仍是两项依赖 `data/` 的测试；VM 上有 `data/`，预期 265 passed / 11 skipped。新增测试：

- `tests/test_eval_sets.py`：视觉必需与 CF 候选规则的每一条排除原因、取整题答案集合（随机模拟验证集合覆盖所有正确取整）、
  包装数据与 InterGPS 的对应、换图配对。
- `tests/test_cfgeo.py`：补丁只替换 alpha 为 255 的像素、重建前后核对像素哈希、编辑器拒绝无法分开的标注、k=1 原样重画、粗体加描边。
- `tests/test_eval_stats.py`：已知答案的构造数据（相同模型、完全分离、聚类使区间变宽、比率指标先求和再相除、Holm、McNemar）。
- `tests/test_eval_harness.py`：五种条件的判分（固定输出）、发布数据的图像核对，以及 tiny Qwen2.5-VL 上的完整路径和 LoRA adapter 加载。
- `tests/test_s3_vm_scripts.py`：S3 决策规则的边界、决策文件与摘要渲染、失败分类、公开数据核对、CF-Geo 重建步骤、`v0` 的步骤与依赖、
  GPU 显存检查、VM 端锁文件、`colab usage` 解析、vLLM 网格检查，以及 tiny 模型上的三个模型步骤。
- `tests/test_colab_launcher.py::test_v0_dry_run_with_queue_lost_exec_and_extra_assignment`：`v0` 端到端 dry run，同时注入 503 排队、
  任务开始前断开和多余的分配。

另外在沙箱里按 VM 的做法运行了不需要模型的步骤（评测集定义与提交的完全相同；198 题 CF-Geo 全部重建；没有评测图会被分辨率上限改变），
并从 Hugging Face 真实下载了一个固定版本文件。GPU 上的步骤还没有运行。

### 2026-11-10（S4 预注册）

S3 的 `v0` 任务（`v0-20261110T023008Z-60fc`，代码 `d85f2b8`）在 A100-SXM4-40GB 上 12 个步骤全部通过，VM 上 pytest 276 项：
265 通过、11 跳过、0 失败（跳过的是需要 git 工作树的运行器端到端测试）。

本阶段改为在你的 WSL2 上测试（不再用沙箱）：Python 3.12.3，隔离环境 `~/.venvs/p3-dev`，按 [requirements/dev-cpu.txt](../requirements/dev-cpu.txt)
的版本安装（torch 2.13.0+cpu 取自 PyTorch 的 CPU 源）；有本机 `data/`；固定 revision 的处理器文件在 Hugging Face 缓存里
（只有 json 和 txt，没有权重）；`HF_HUB_OFFLINE=1`。

```text
python -m pytest -q
276 passed                # 改动前，master d85f2b8
296 passed                # 本阶段改动后，0 失败，0 跳过
```

沙箱里一直失败的两项（依赖 `data/`）在这里通过。新增 20 项测试：

- `tests/test_s4_registration.py`（15 项）：登记表与配置一致（派生字段由脚本重算后完全相同）；顺序覆盖每个登记的组与种子各一次；
  S4 配置与 S3 决策一致（P1、不预热、1024、vLLM、802,816）；S4 配置与 `rl_v3.json` 只差三个字段；组间只差白名单字段；
  运行时与数据哈希等于记录值；checkpoint 与 Drive 目录；试跑门槛沿用 D41 的数值；登记检查报告每一种不一致；`--show`；
  `train_rl --registered` 拒绝 smoke、输出目录、别的实验配置或运行时、未登记的种子；预注册文件列出全部哈希；登记运行在加载模型前停止、
  不写任何文件；NaN/inf 检测；本机数据与登记一致（没有 `data/` 时跳过）。
- `tests/test_rl_data.py`（2 项）：S4 配置生成 P1 提示，`rl_v3.json` 仍是 P0；只要答案的协议和未知协议不能用于训练。
- `tests/test_rl_rewards.py`（1 项）：rollout 记录写实际的协议编号。
- `tests/test_protocol_v3.py`（1 项）：协议编号与提示变体一一对应。
- `tests/test_rl_entry_cpu.py`（1 项）：S4 配置走真实的 TRL 路径（tiny Qwen2.5-VL）时，奖励函数收到的提示都以 P1 句子结尾，
  rollout 和运行身份都记录 P1。

其他检查（清单按 `--git-tracked-only` 刷新之后）：`python tools/verify_migration.py --full` 核对 3,354 个文件，0 个错误，
批准行 609 / 82；`python tools/check_links.py` 检查 19 个页面的 174 个相对链接，0 个失效；
`python -m scripts.training.register_runs --check` 通过（含本机数据的 SHA256 与 609 行）。

没有验证的：新代码在 GPU 上的行为（P1 提示下 vLLM 的重要性采样、NaN 停止、登记核对中的 GPU 型号），这些由试跑检查（S4 预注册第 11 节）；
`pilot` 与 `train` 两个 Colab 任务还没有实现。

### 历史覆盖范围

测试覆盖：数据准入与白名单、几何序列化、split 守卫、感知奖励与文本蕴含、
几何解析/评分、tokenizer 审计、交付物与 funnel 脚本，以及
[tests/test_repo_layout.py](../tests/test_repo_layout.py) 的仓库结构回归
（平铺脚本、分组包、README 目录覆盖、入口文件、pytest 配置、configs 相对路径）。
GPU 行为不在测试范围内。

## 人工检查建议

1. `python -m compileall -q src scripts tests tools`：语法/字节码检查。
2. 导入检查：`python -c "import src.training.approved_hf, src.data.perception_v4"`。
3. `python tools/check_links.py`：当前页面链接全部可达。
4. `git status` 应只显示有意的改动；`data/`、`runs/` 不应被提交。

## 报告规范

每个阶段（数据、训练、评测）记录：

- 配置路径与内容哈希、模型 revision、数据 release manifest SHA。
- 原始预测/日志路径、评分脚本版本、随机种子。
- 失败、隔离、截断和未运行项要显式写出，不能用“通过”概括部分结果。
- 显存、耗时与成本（若在 GPU 上运行）。
- 结构变更同步更新 [CHANGELOG.md](../CHANGELOG.md) 与本页相关条目。

历史报告位于 [reports/](../reports/)（只追加）与 [docs/migration/](migration/)；
旧报告中的失败与隔离证据保留原样，不因新版本发布而删除。
