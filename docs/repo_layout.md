# 目录结构约定

更新：2026-11-09。本页定义仓库的物理布局和新增文件的落位规则；数据与报告
的冻结策略见 [data.md](data.md) 与 [verification.md](verification.md)。

## 顶层布局

```text
.
├── README.md              # 项目入口：目标、当前事实、快速开始
├── AGENTS.md              # AI/协作者的阅读顺序与硬性约束
├── CHANGELOG.md           # 结构、文档、验证状态变更
├── pyproject.toml         # 项目元数据 + pytest 配置
├── .editorconfig          # 编码/换行/缩进约定
├── .gitignore             # data/、runs/、缓存等本地内容不入库
├── colab/                 # Colab 运行器：launch.sh（本地入口）、kernel_*.py（在 Colab 内核中执行）、使用说明
├── configs/               # 当前执行配置；experiments/ 为协议 v3 正式实验（基础配置 + 组别）
├── data/                  # 本地数据载荷（约 1.4 GB，git 忽略，SHA 由清单校验）
├── docs/                  # 说明页 + 历史留档（见下）
├── reports/               # 只追加的版本化证据与报告
├── requirements/          # CPU 环境参考（不是锁文件）
├── scripts/               # 按生命周期分组的可执行脚本
├── src/                   # 可复用实现（被脚本和测试导入）
├── tests/                 # pytest 测试
└── tools/                 # 离线校验与仓库维护工具
```

`runs/`、`backups/`、`.venv/`、`.pilot_deps/`，以及 Colab 运行器的 `.colab_cache/`、`.colab_runs/`、
`.colab_local.env` 都是本地目录或文件，默认被 `.gitignore` 忽略，不应提交。Colab 运行的结果通过
`results/<run_id>` 分支进入 `reports/colab_runs_<日期>/`。

## scripts/ 分组

脚本按生命周期分组，组内脚本通过 `python -m scripts.<group>.<name>`
从仓库根目录执行。共享常量放 `scripts/common/`，禁止在业务脚本里复制路径常量。

| 目录 | 内容 |
| --- | --- |
| `scripts/common/` | `topup_common.py`、`finalfill_common.py`、`strict_v8_common.py`：ROOT/路径、读写、哈希等共享工具 |
| `scripts/data/` | 数据构建、审计、导出：候选划分、感知数据版本、funnel、split 校验、topup 解析 |
| `scripts/training/` | 训练入口、视觉诊断、配置生成、数学验证 worker |
| `scripts/reporting/` | 发布/执行报告、汇总与交付清单 |
| `scripts/migration/` | 历史迁移打包脚本（不随当前布局保证可运行） |
| `scripts/colab/` | Colab 运行器的本地打包工具与 VM 端步骤（引导、任务步骤、探针、运行时决策、摘要） |

完整脚本清单与状态见 [scripts/README.md](../scripts/README.md)。
历史方案文档中的 `python -m scripts.<name>` 是当时快照，当前入口以 README 和
`scripts/README.md` 为准。

## src/ 分层

| 目录 | 职责 |
| --- | --- |
| `src/data/` | 数据准入、模型输入白名单、事实序列化、split 保护、感知奖励解析 |
| `src/evaluation/` | 有限几何 schema 的解析与覆盖感知评分 |
| `src/losses/` | CPU 参考损失（正确性参照，不是 GPU 训练器） |
| `src/teachers/` | tokenizer/配置元数据审计（不下载权重） |
| `src/rewards/` | 协议 v3 的奖励组件：逐条断言解析、InterGPS 几何证伪、可证伪感知奖励 v5、答案校验进程池、罗列攻击探针 |
| `src/training/` | 统一 GRPO 入口（协议 v3、组别配置、奖励汇总与逐条日志、语言 LoRA、ViT 缓存）；旧的 manifest 门控 SFT/GRPO 入口（历史） |

新增代码优先放进 `src/`（可复用逻辑）或 `scripts/<group>/`（一次性/流水线
命令），测试放 `tests/test_*.py`，校验工具放 `tools/`。

## docs/ 与历史留档

- `docs/*.md`：当前说明页，随代码事实更新。
- `docs/guides/`：可复用的操作/审查模板。
- `docs/blueprints/`：历史研究方案与旧配置，只读留档；内部路径/命令不保证
  指向当前布局。
- `docs/migration/`：迁移、清理、整理记录与封板清单快照。
- 历史文档中的相对链接保持记录时写法，不为了“链接全绿”改写历史；
  当前页面的链接由 [tools/check_links.py](../tools/check_links.py) 检查。

## 数据与报告为什么冻结

`data/` 与 `reports/` 是证据目录：`data/portable_release/manifest.json`
的 `inputs` 以 SHA256 引用 `reports/...` 与 `data/...` 的旧路径，
`migration_manifest.json` 记录逐个文件的大小/哈希，清理记录也按路径陈述删除
范围。因此这两个目录**不因目录美化而移动**，只在其中增加 `README.md` 索引。
新增报告应使用带日期的版本目录（如 `reports/<主题>_<YYYYMMDD>/`），不要覆盖旧报告。

## 新增/移动文件时的检查

1. 新文件是否需要进入 `migration_manifest.json`：在有 `data/` 的机器上运行
   `python tools/build_migration_manifest.py`，它会保留溯源字段并记录变更；没有 `data/`
   时（如新 clone 或沙箱）改用 `--git-tracked-only`，只重算 git 可见文件，`data/` 条目原样保留。
2. 是否破坏 `python -m scripts.<group>.<name>` 或 `from scripts.` 导入：运行
   `python -m pytest -q` 并做一次导入检查。
3. 是否破坏当前文档链接：运行 `python tools/check_links.py`。
4. 结构或状态变化是否记入 [CHANGELOG.md](../CHANGELOG.md)。
