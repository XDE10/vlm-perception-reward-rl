# scripts/ 脚本目录

本目录按职责分为 6 个子包：`common/`（共享路径常量与 I/O 辅助）、`data/`（数据构建、导出与审计）、
`training/`（训练与诊断入口）、`reporting/`（交付报告与发布）、`migration/`（历史迁移打包）、
`colab/`（Colab 运行器的本地打包与 VM 端步骤，入口是 [colab/launch.sh](../colab/README.md)）。
所有脚本的仓库根均由自身位置向上两级推导：
`ROOT = Path(__file__).resolve().parents[2]`（`scripts/<group>/<name>.py`），因此
**命令一律从仓库根目录执行**，统一入口形式为 `python -m scripts.<group>.<name>`。
组内共享代码放 `common/`，跨组引用使用绝对导入（如 `from scripts.common.topup_common import *`），
不再存在平铺的 `scripts/<name>.py`，旧命令 `python -m scripts.<name>` 已改为 `python -m scripts.<group>.<name>`。

状态说明：**主线** = 当前仍可复现、与现行入口/测试相关；**历史归档** = 2026-10 数据流水线、封板交付或
迁移快照的一次性脚本，仅作溯源保留，不要重跑——输出已冻结（多数脚本在输出存在时拒绝覆盖）、
引用已清理的路径/缓存，或会改写冻结报告的哈希清单。

## common/ — 共享辅助

| 脚本 | 用途 | 状态 | 典型入口 |
| --- | --- | --- | --- |
| `topup_common.py` | 仓库根/数据/报告路径常量与 `read/rows/sha/dump/write/stable` 等 I/O 辅助（导入时创建 `data/topup_v6_20261024`、`reports/topup_v6_20261024`） | 主线 | `import scripts.common.topup_common` |
| `finalfill_common.py` | finalfill 指纹册路径与首次快照辅助，复用 `topup_common` | 主线 | `import scripts.common.finalfill_common` |
| `strict_v8_common.py` | strict v8 封板路径常量，复用 `finalfill_common` | 主线 | `import scripts.common.strict_v8_common` |

## data/ — 数据构建、导出与审计

| 脚本 | 用途 | 状态 | 典型入口 |
| --- | --- | --- | --- |
| `audit_project3_overlap.py` | 本地 CPU 数据关联/重叠审计，写出 `reports/project3_cpu_20261023/`；可选依赖见 `requirements/project3-cpu.txt` | 主线 | `python -m scripts.data.audit_project3_overlap`（先运行 `python scripts/data/prepare_project3_sources.py`） |
| `calibrate_perception_v5.py` | 只读：在认证正例上扫描 v5 几何证伪阈值（误杀数与对罗列断言的证伪率）；在登记阈值下报告一致性门控、门控后误杀、留一法残余误杀率（Wilson 区间）和每条误杀的测量值；对比 v4/v5（含与不含门控）在罗列探针上的奖励；输出 JSON 与 Markdown | 主线 | `python -m scripts.data.calibrate_perception_v5 --output reports/perception_v5_calibration_<日期>` |
| `build_eval_sets.py` | 只读：按 S3 设计第 1–3 节的预注册规则（`src/evaluation/eval_sets.py`），从固定版本的公开数据生成评测集定义（视觉必需子集、CF 候选、换图配对）；先按 `migration_manifest.json` 核对每个输入文件；不运行模型 | 主线 | `python -m scripts.data.build_eval_sets --sources data/project3_sources --out reports/eval_sets_20261109/eval_sets.json` |
| `build_cfgeo.py` | 只读：用 OCR（rapidocr-onnxruntime 1.4.4）为 CF 候选生成编辑补丁（k=1 原样重画、k=2 长度乘 2）并核验；只输出补丁与像素哈希，不输出原图；`--dev-train` 只在 train 上构造开发集 | 主线 | `python -m scripts.data.build_cfgeo --sources <公开数据目录> --spec reports/eval_sets_20261109/eval_sets.json --out reports/cfgeo_20261109/cfgeo.json` |
| `build_geometry_funnel_v8.py` | 只读：几何出口互斥分类与全池图像重叠统计；`classify` 被 `tests/test_geometry_funnel.py` 直接导入 | 主线 | `python -m scripts.data.build_geometry_funnel_v8` |
| `build_project3_all_split_candidates.py` | 生成全量唯一匹配 split 候选并隔离模型文本（train/诊断分离） | 历史归档 | `python -m scripts.data.build_project3_all_split_candidates` |
| `build_project3_perception_preview.py` | 冻结 200 题原型的增量预览补充；输出已存在时拒绝覆盖 | 历史归档 | `python -m scripts.data.build_project3_perception_preview` |
| `build_project3_perception_prototype.py` | 构建冻结的 train-only 200 题感知原型与待审工作单 | 历史归档 | `python -m scripts.data.build_project3_perception_prototype` |
| `build_project3_perception_v2.py` | 按冻结 200 题重跑 schema v2，保留全部原始记录 | 历史归档 | `python -m scripts.data.build_project3_perception_v2` |
| `check_topup_source_integrity.py` | 校验 pin 住的代码/数据/数学源文件大小与 SHA256 | 历史归档 | `python -m scripts.data.check_topup_source_integrity` |
| `download_project3_train_ranges.py` | 官方源 ranged 回退下载；使用前校验 Git blob 身份 | 历史归档 | `python -m scripts.data.download_project3_train_ranges` |
| `export_strict_geometry_v8.py` | 不新增 API 调用，重解析原始像素响应并导出 strict v8 几何 | 历史归档 | `python -m scripts.data.export_strict_geometry_v8` |
| `prepare_project3_sources.py` | 下载固定 revision 的公共标注/数据文件，保留 license 与 SHA256 | 历史归档 | `python scripts/data/prepare_project3_sources.py` |
| `prepare_topup_geometry_reserve.py` | 为第二轮事实审计准备 train-only 备用池 | 历史归档 | `python -m scripts.data.prepare_topup_geometry_reserve` |
| `prepare_topup_p3.py` | 组装 topup v6 感知题目集与图片 | 历史归档 | `python -m scripts.data.prepare_topup_p3` |
| `reparse_topup_geometry.py` | zero-call 侧车解析：保留原始响应、实际 finish 与 fact guard | 历史归档 | `python -m scripts.data.reparse_topup_geometry` |
| `resolve_geometry_uncertain_v7.py` | 单题（1683）记录式像素 + 精确证明裁决，无新 API | 历史归档 | `python -m scripts.data.resolve_geometry_uncertain_v7` |

## training/ — 训练与诊断入口

| 脚本 | 用途 | 状态 | 典型入口 |
| --- | --- | --- | --- |
| `train_rl.py` | 统一 GRPO 入口（协议 v3，所有实验组共用）：`configs/experiments/` 基础配置 + 组别 + 种子，委托 `src.training.rl_entry.run`；S4 正式任务加 `--registered`，必须与登记表完全一致 | 主线 | `python -m scripts.training.train_rl --registered configs/experiments/s4_runs_20261110.json --arm rl_v5 --seed 1` |
| `register_runs.py` | 生成（`--write`）或核对（`--check`）S4 登记表的派生字段：每个任务的配置哈希、输出目录、步数，运行时内容哈希，数据与决策文件的 SHA256；有 `data/` 时还核对本机数据与批准行数。`--show <组> <种子>` 打印一个任务的完整配置 | 主线 | `python -m scripts.training.register_runs --check` |
| `train_project3.py` | 旧训练入口（感知 SFT → 稀疏 GRPO），委托 `src.training.approved_hf.cli(expected_vision=True)`；2026-11-09 只修复 LoRA 误入 ViT 与 transformers 5 兼容，新实验不再使用 | 历史归档 | `python -m scripts.training.train_project3 --config configs/...` |
| `diagnose_project3_vision.py` | 同题原图/黑图/无图/遮挡成对视觉依赖诊断 | 主线 | `python -m scripts.training.diagnose_project3_vision` |
| `configure_topup_training.py` | 为已批准 V6 行生成版本化 smoke 配置（明确不是 GPU 验收） | 历史归档 | `python -m scripts.training.configure_topup_training` |
| `write_approved_training_configs.py` | 写入初始 A100 smoke 配置，不下载权重、不执行训练 | 历史归档 | `python -m scripts.training.write_approved_training_configs` |
| `math_verify_pilot_worker.py` | 隔离的有界 Math-Verify worker，stdout 只输出 JSON；需 pip 安装 `math_verify`（已不再使用已删除的 `.pilot_deps/`） | 主线 | 由 `src/training/approved_hf.py` 以 `python -m` 子进程调用 |
| `math_verify_v3_strict_worker.py` | 更严格的有界 typed 准入补充，隔离关系型答案供任务感知复核；需 pip 安装 `math_verify` | 主线 | 由 `src/training/approved_hf.py:check_math` 以 `python -m` 子进程调用 |

## reporting/ — 交付报告与发布

| 脚本 | 用途 | 状态 | 典型入口 |
| --- | --- | --- | --- |
| `publish_strict_v8_report.py` | 仅从封板产物生成人类可读交付说明与 `delivery_manifest.json` | 历史归档 | `python -m scripts.reporting.publish_strict_v8_report` |
| `report_data_revision_v4.py` | 只从版本化产物构建 review-only 交付报告，无 API、无训练 | 历史归档 | `python -m scripts.reporting.report_data_revision_v4` |
| `report_delegated_release.py` | 汇报实测的委托审核与范围明确的数据 release | 历史归档 | `python -m scripts.reporting.report_delegated_release` |
| `finalize_delegated_release.py` | 保护旧产物、刷新入口提示并哈希新交付；仍引用项目一/项目二入口与旧目录名，重构后不能原样重跑 | 历史归档 | `python -m scripts.reporting.finalize_delegated_release` |
| `finalize_overnight_report.py` | 校验必需证据并汇总 2026-10-23 CPU 通宵交付报告与 artifact inventory；`read_json` 被 `tests/test_delivery_artifacts.py` 导入 | 历史归档 | `python -m scripts.reporting.finalize_overnight_report` |

## migration/ — 历史迁移打包

| 脚本 | 用途 | 状态 | 典型入口 |
| --- | --- | --- | --- |
| `prepare_internship_migration.py` | 生成三份自包含迁移副本；内部打包清单与 README 按 2026-10-24 重构前目录树编写，不能原样重跑 | 历史归档 | `python -m scripts.migration.prepare_internship_migration` |

## 环境与依赖

- CPU 检查环境见 `requirements/cpu-snapshot.txt`；项目三审计的可选依赖见 `requirements/project3-cpu.txt`。
- 运行依赖不在 `pyproject.toml` 声明；GPU/PyTorch 版本按目标驱动单独固定。
- 测试：从仓库根目录执行 `python -m pytest -q`（需要 Python 3.10+；`python -m` 会把仓库根放入 `sys.path`，从而可导入 `src.*` 与 `scripts.*`）。

## colab/ — Colab 运行器（2026-11-10 起）

本地脚本只用标准库（WSL2 的 `python3` ≥ 3.8 即可）；VM 端脚本由 `colab/kernel_*.py` 在 Colab 内核中调用。
用户入口是 `bash colab/launch.sh`，见 [colab/README.md](../colab/README.md)。

| 脚本 | 用途 | 状态 | 典型入口 |
| --- | --- | --- | --- |
| `common.py` | 本地与 VM 共用的标准库辅助：原子 JSON、分片/拼接校验、心跳输出 | 主线 | 被其余脚本导入 |
| `pack_private_data.py` | 本地：按 release / 行内 SHA / 迁移清单三类锚点逐个校验后，打包运行所需的私有数据；VM：解包与复核 | 主线 | `python3 -m scripts.colab.pack_private_data --data-root <data 目录> --check-only` |
| `verify_pack.py` | VM：复核解包后的数据与锚点一致 | 主线 | 预检步骤 `verify_pack` |
| `local_tools.py` | 本地：生成请求与上传清单（含提交的 git 文件清单）、比对 VM 上已收到的分片、读取远端状态、拼接并解压结果、发布前去除凭据、读出 `colab usage` 的余额与费率 | 主线 | 由 `colab/launch.sh` 调用 |
| `drive.py` | VM：Google Drive 持久化，只经 `rclone copy` + `rclone check` 写入并核对，不经 FUSE 挂载；探针只删除自己写的文件。S4 用的相对路径操作（复制核对、取回核对、小文件读写、列目录、删除旧 checkpoint）拒绝项目目录之外的路径 | 主线（S4 起必需） | 步骤 `drive_probe`、任务 `drive-check`；`python -m scripts.colab.drive probe --out <json>` |
| `s4_state.py` | VM：S4 在 Drive 上的状态：checkpoint 上传与 `DRIVE_VERIFIED.json`、只保留最新一个、逐文件核对的恢复、`STARTED`/`COMPLETED`/`FAILED` 标记、每个任务一个文件的认领（claim）与心跳 | 主线 | 被 `s4_supervise.py`、`train_s4.py`、`decide_pilot.py` 导入 |
| `s4_supervise.py` | VM：在独立进程组里运行一个训练进程，读取它的事件，checkpoint 一写完就在后台复制到 Drive，按期限或指令停止，判断结束类型（完成、中断、设置问题、计算失败）；S4 试跑的 `pilot-run` 与 `pilot-resume` | 主线 | 任务 `pilot` 的步骤 `pilot_*` |
| `decide_pilot.py` | VM：按 S4 预注册第 11 节计算试跑门槛 G1–G6，写 `pilot_gates.json`，并把结论（通过或不通过）写成 Drive 上的 `PILOT_LATEST.json` | 主线 | 任务 `pilot` 的步骤 `decide_pilot` |
| `train_s4.py` | VM：S4 正式任务：核对试跑与代码冻结，按登记顺序认领、从 Drive 恢复、训练、核对；按 VM 剩余时间和预注册的收尾规则决定开始哪些任务 | 主线 | 任务 `train` 的步骤 `train_runs` |
| `vm_github.py` | VM：用户放在 VM 上的 GitHub 凭据存在时，由 VM 推送 `results/<run_id>`。开始时 dry-run 验证写权限，推送前脱敏；从不读取凭据内容，失败时由本机推送 | 主线（可选） | 由 `runner.py` 调用（任务开始时检查，打包后推送） |
| `bootstrap.py` | VM：解包数据；任务要求时先检查 GPU（`v0` 显存至少 40 GB；`pilot`、`train` 必须是登记的 NVIDIA A100-SXM4-40GB），不符就在安装前停止；按驱动 CUDA 版本选择锁文件建隔离 venv、下载固定 revision 模型（不需要 GPU 的任务跳过 venv 与模型）；可选建 vLLM venv | 主线 | 由 `colab/kernel_bootstrap.py` 调用；`python -m scripts.colab.bootstrap vllm-env --root ...` |
| `fetch_model.py` | VM：下载固定 revision 的模型快照并记录每个文件的 SHA256 | 主线 | 由 `bootstrap.py` 调用 |
| `runner.py` | VM：逐步运行任务（独立进程组、超时、心跳、状态文件），打包并分片结果；可选把结果复制到 Drive 并核对 | 主线 | 由 `colab/kernel_job.py` 调用 |
| `tasks.py` | 各任务的步骤定义（当前：`preflight`、`v0`、`pilot`、`train`（都含 dry-run 版本）与 `drive-check`） | 主线 | 被 `runner.py` 导入 |
| `env_report.py` | VM：记录实际软件版本、GPU、内存、磁盘、环境锁与模型文件 SHA | 主线 | 预检步骤 `env_report` |
| `gpu_probe.py` | VM：真实 3B 权重下的 LoRA 范围、提示长度、峰值显存、生成吞吐、ViT 缓存等价性 | 主线 | 预检步骤 `gpu_probe` |
| `v0_probe.py` | VM：V0 在 16 道 validation 上的协议 v3 贪心生成（有图/无图），工程信号 | 主线 | 预检步骤 `v0_probe` |
| `decide_runtime.py` | VM：按预定规则把测量结果冻结成 `frozen_runtime.json` | 主线 | 预检步骤 `decide_runtime` |
| `public_sources.py` | VM：下载固定版本的 Geometry3K 包装数据，按本次提交的 `migration_manifest.json` 核对大小与 SHA256；已核对过的副本复用 | 主线 | 任务 `v0` 的步骤 `public_sources` |
| `eval_inputs.py` | VM：用数据包里的 InterGPS 标注按预注册规则重建评测集定义，要求与提交的完全相同；由补丁重建全部 CF-Geo 图像并核对像素；报告会被分辨率上限改变的评测图（不运行模型） | 主线 | 任务 `v0` 的步骤 `eval_sets`、`cfgeo_build` |
| `prompt_select.py` | VM：在 64 道已批准 train 题上测量 P0 与 P1 的格式率、答案准确率和补全长度（温度 1.0 各 4 个样本，另加贪心） | 主线 | 任务 `v0` 的步骤 `prompt_select` |
| `v0_diagnosis.py` | VM：V0 在 82 道 validation 上的贪心诊断（P0 有图、P0 无图、只要答案的提示），含失败分类；只测量 | 主线 | 任务 `v0` 的步骤 `v0_val82` |
| `harness_check.py` | VM：用 train 输入走一遍 S5 的评测代码（五种条件、E1 评分、统计模块） | 主线 | 任务 `v0` 的步骤 `harness_check` |
| `final_eval.py` | VM：核对 S4 终态和最终 adapter，运行并保存 S5 的逐题预测 | 主线 | 任务 `final-eval` |
| `s5_inputs.py` | VM：重建 S5 固定题集，处理 MathVista 判分和 InterGPS 证伪诊断 | 主线 | 由 `final_eval.py` 导入 |
| `s5_analysis.py` | VM：汇总预注册的九项比较、逐种子和次要指标 | 主线 | 由 `final_eval.py` 导入 |
| `decide_s3.py` | VM：按 S3 设计第 6 节的预注册规则写出 `s3_decisions.json`（提示、格式预热、长度上限、分辨率、生成后端） | 主线 | 任务 `v0` 的步骤 `decide_s3` |
| `summarize_run.py` | VM：把一次运行的所有产物汇总成 `summary.json` 与 `summary.md` | 主线 | 运行结束时自动调用 |
