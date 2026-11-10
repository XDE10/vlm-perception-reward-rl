# reports/ 目录说明

`reports/` 是**只追加的实验与审核证据**，记录每次数据版本、训练入口和审计
的原始结果。这里的文件不参与训练运行时读取，但对复查实验、解释数据来源是
必需的。

**布局冻结。** 旧报告内部引用的是当时的相对路径；移动/重命名文件会让历史
记录无法按原样重放。历史报告中的失败、隔离和未完成项保留原文，不因新版本
发布而删除。新的报告使用新的带日期目录。

## 顶层索引

| 条目 | 内容 |
| --- | --- |
| `strict_v8_20261024/` | Strict v8 封板协议、release 快照、数据/训练前置审计记录（约 28 MB） |
| `topup_v6_20261024/` | Topup v6 感知奖励补充数据构造报告（约 15 MB） |
| `handover_20261024_v2/`、`handover_audit_20261024_v1/` | 交接清单与交接审计 |
| `data_release_preparation_20261024/` | 便携发布打包、数据修订与溯源记录 |
| `data_revision_v4_20261024/`、`data_human_review_pack*` | 数据修订/人工审阅包 |
| `project3_cpu_20261023/` | 旧 CPU 环境与训练可行性检查（历史环境，已不复现） |
| `project3_perception_*`、`project3_all_split_candidates_v2/`、`project3_grounding_ai_review_20261024/` | 感知数据构造/复核/AI 审核过程 |
| `training_readiness_20261023_v2.*`、`completion_audit.json`、`artifact_inventory.json` | 训练前置检查与总览 |
| `tokenizer_alignment*` | tokenizer 对齐与复审 |
| `pytest_full.log`、`blueprint_data_revision.diff`、`overnight_execution_summary.md`、`cpu_demo.json` | 测试/差异/执行摘要 |
| `certified_fact_errata_20261109/` | 第三次预检校准中被几何检验否定的认证事实的看图核对（AI 核对，release 不变） |
| `s3_planning_estimates_20261109/` | S3 评测规则在 train 上的数量估计与 CF-Geo 原型（不读 validation 和 test） |
| `eval_sets_20261109/` | 按 S3 预注册规则生成的评测集定义（test 视觉必需子集、CF 候选、换图配对），不含图像 |
| `cfgeo_20261109/` | CF-Geo 评测集与 train 开发集：编辑补丁、像素哈希、标准答案、两轮看图抽查记录（不含原图） |
| `s4_preregistration_20261110/` | S4 预注册引用数字的复现：S3 决策文件副本的核对、P0/P1 格式率按题聚类的 bootstrap 区间（只用 train） |

## 约定

- 新增报告放在新目录，文件名带日期；不覆盖旧文件。
- JSON 报告保留机器可读字段；Markdown 摘要说明运行命令、配置身份、结果和
  未运行项。
- 抽查历史结论时以原始报告为准，不要从 README/记忆重述。
- 读取时注意旧报告中的绝对路径（如 `D:\Users\Mr.Z\Desktop\modern_genai`、旧
  CPU 环境）是历史记录，不是当前可执行入口；当前入口见
  [docs/training.md](../docs/training.md) 与
  [docs/verification.md](../docs/verification.md)。
