# data/ 目录说明

**物理布局冻结。** 这里存放便携发布副本、来源材料、审计证据和历史数据版本，
共约 1.4 GB。移动或重命名会同时破坏 `migration_manifest.json`、发布的
[portable_release/manifest.json](portable_release/manifest.json) 中的 `inputs`
哈希溯源自以及历史清理/验收记录。需要新版本时新增带日期的目录，不要改旧目录。

## 目录

| 路径 | 内容 | 用途 |
| --- | --- | --- |
| [portable_release/](portable_release/) | 609 训练行 + 82 validation 行、dev 保护 ID、发布 manifest | 唯一训练/评测数据入口 |
| [project3_sources/](project3_sources/) | Geometry3K / InterGPS 原始材料（约 400 MB） | 来源审计 |
| [project3_audit/](project3_audit/) | 题目-图像-标注关联审计证据 | 证据 |
| [tokenizers/](tokenizers/) | 固定 revision 的 tokenizer/config 元数据 | 离线审计 |
| [strict_v8_20261024/](strict_v8_20261024/) | Strict v8 封板数据与 release 快照 | 历史版本 |
| [topup_v6_20261024/](topup_v6_20261024/) | 感知奖励补充数据与图片 | 历史版本 |
| [finalfill_v7_20261024/](finalfill_v7_20261024/)、[project3_perception_preview/](project3_perception_preview/)、[project3_perception_prototype/](project3_perception_prototype/)、[project3_perception_v2/](project3_perception_v2/)、[project3_all_split_candidates_v2/](project3_all_split_candidates_v2/) | 中间构造/复核版本 | 历史版本 |
| [delegated_ai_releases_20261024/](delegated_ai_releases_20261024/)、[project3_grounding_ai_review_20261024/](project3_grounding_ai_review_20261024/) | AI 审核记录 | 证据 |
| [synthesis_mock/](synthesis_mock/) | 合成接口本地 mock | 测试样例 |
| [screening_sources/](screening_sources/) | 旧多项目时代不完整筛选来源残留（约 934 MB） | 待决定是否删除，当前保留 |

## 使用规则

- 只把 `portable_release` 中 `approved_*_files` 列出的文件当训练/评测输入。
- 不手改批准字段、行内容、图片或 SHA256；不接受“重新哈希即通过”的修复。
- 逐行批准缺失、图像相对路径不存在、图片 SHA 不符时，流程应失败关闭。
- 内容细节与验证命令见 [docs/data.md](../docs/data.md)；删除记录见
  [docs/migration/](../docs/migration/)。
- `data/` 不进 git（`/data/*` 已忽略），完整性由根目录
  [migration_manifest.json](../migration_manifest.json) 跟踪。
