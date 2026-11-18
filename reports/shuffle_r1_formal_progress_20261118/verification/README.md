# 2026-11-18 提交验证

本轮在 WSL2、Python 3.12.3 上实际执行；没有新建 GPU 或重启正式训练。

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 主仓库 `python -m pytest -q` | 321 passed，1 warning，1788.83 秒 | [完整日志](project-pytest.txt) |
| 正式单卡提交 `1a7fb4b` 的 `python -m pytest -q` | 52 passed，21 warnings，47.45 秒 | [完整日志](shuffle-pytest.txt) |
| Git bundle 与补丁重建 | bundle 完整；在空仓库恢复到正式 commit，补丁重建 tree 一致 | [源码重建](source-reconstruction.json) |
| 归档身份与语法 | 40 个来源文件 SHA256/字节数一致；14 个 Python 源码可解析；shell 语法通过 | [完整性记录](artifact-integrity.json) |
| 主项目离线完整性 `python3 tools/verify_migration.py --full` | 逐文件 SHA256、609 train / 82 validation 检查通过，errors=[] | [完整日志](migration-full.txt) |
| 当前文档与新增报告链接 | 相对链接存在且位于仓库内 | [链接检查](links.txt) |
| 待提交文本的凭据扫描 | 未发现匹配的实际凭据；授权文件和模型/Parquet 不在提交内 | [扫描记录](publication-scan.json) |

主仓库使用 `p3-dev` 环境；单卡代码使用隔离的 `shuffle-r1-cpu-frozen-20261115` 环境。
日志保留原始告警和历史空白。源码快照与历史报告没有为格式检查改写，字节身份由来源清单核对。

清单通过 `tools/build_migration_manifest.py --git-tracked-only --date 2026-11-18
--label shuffle_r1_formal_20261118` 重建，已有 git-ignored 数据条目原样保留，随后做 full SHA 核验。
纳入该核验日志后再次刷新清单并核验，确保提交的清单覆盖最终文件。

这些检查证明本轮归档与 CPU 回归性质。CUDA/vLLM/FSDP 的新一轮验收、150 步完成和公开测试测评
不属于本轮已运行项；既有 GPU 训练进展单独见主报告中的带时间断点核验。
