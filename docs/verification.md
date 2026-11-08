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
