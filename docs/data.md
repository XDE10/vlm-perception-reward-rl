# 数据目录与使用边界

本页说明 `data/` 的组织、批准范围和校验方式。**目录物理布局冻结**：移动会
破坏 `migration_manifest.json`、release manifest 的 `inputs` 溯源和清理记录，
因此不要在整理目录时移动 `data/` 下的文件（新增说明文件除外）。

## 目录总览

`data/` 约 1.4 GB、2800+ 文件，按“当前发布 / 来源与审计 / 历史版本 / 第三方来源”
混排。带日期的目录是当时的数据版本，不是“最新更好”的排序。

| 路径 | 作用 | 当前用途 |
| --- | --- | --- |
| `data/portable_release/` | 便携发布副本：609 训练行 + 82 validation 行 + dev 保护 ID + manifest | **唯一训练/评测数据入口** |
| `data/project3_sources/` | Geometry3K/InterGPS 原始材料（约 400 MB） | 来源审计 |
| `data/project3_audit/` | 题目-图像-标注关联审计证据 | 证据 |
| `data/tokenizers/` | 固定 revision 的 tokenizer/config 元数据（约 44 MB） | 离线审计 |
| `data/strict_v8_20261024/` | Strict v8 封板数据与 release 快照 | 历史版本 |
| `data/topup_v6_20261024/` | Topup v6 感知奖励补充数据与图片（约 55 MB） | 历史版本/图片源 |
| `data/finalfill_v7_20261024/`、`data/project3_perception_*`、`data/project3_all_split_candidates_v2/` | 中间构造与复核版本 | 历史版本 |
| `data/project3_grounding_ai_review_20261024/`、`data/delegated_ai_releases_20261024/` | AI 审核记录 | 证据 |
| `data/synthesis_mock/` | 合成接口的本地 mock 产物 | 测试样例 |
| `data/screening_sources/` | 项目一/二时代的不完整筛选来源残留（约 934 MB） | 待决定是否删除，当前保留 |

`data/` 不在 git 版本控制内（见 [.gitignore](../.gitignore)），但完整性由
[`migration_manifest.json`](../migration_manifest.json) 跟踪；数据准入由
release manifest 单独保护，两者不能互相替代。

## 批准范围（release manifest）

[`data/portable_release/manifest.json`](../data/portable_release/manifest.json)
是当前数据准入的唯一机器可读来源：

- `approved_training_files`：`["project3_train_fact_pruned.jsonl"]`（609 行）。
- `approved_evaluation_files`：`["project3_validation_fact_pruned.jsonl"]`（82 行）。
- `protected_dev_ids_file`：`reserved_dev_ids_never_train.json`。
- `files`：每个发布文件的 SHA256。
- `inputs`：把发布文件回溯到 `reports/...`、`data/...`、`src/...` 的输入哈希，
  是溯源链的一部分。

当前批准的是**部分认证事实**，不是 Geometry3K 全量金标：609 训练行涉及 458 幅
不同图像，82 validation 行涉及 77 幅；历史阶段的 531、928 等计数不代表最终值。
候选、隔离、存疑数据不能通过手改批准字段或重算哈希进入训练。

## 行格式与模型可见性

- 训练输入白名单：`problem`、`image_path`（相对路径，指向包内图片）。
- 感知 SFT 目标白名单：`model_perception`，只含认证且图像独占的部分事实。
- `reference_answer`、认证正负事实、审核意见、内部符号身份只用于评测/奖励，
  不进入问题提示。
- 事实规范化顺序：Angle → Length → Parallel → Perpendicular → Tangent；角的
  顶点角色不能机械按字母重排。
- 认证范围之外的事实视为未知（mask）；稀疏 Recall/有限范围 FP 不等于全图
  事实 Precision，也不能宣称完整防幻觉。

## 校验

从仓库根目录运行：

```bash
python tools/verify_migration.py --full
```

它会检查：manifest 文件存在/大小/SHA、release 文件 SHA、批准行数、逐行
`training_approved` 与输入白名单、`image_path` 相对性与 `image_sha256`、配置中
的数据/tokenizer 相对路径。校验通过只证明**离线完整性**，不证明 GPU 可训练。

## 修改规则

- 不手改已批准数据、批准字段、图片或哈希来“修复”问题。
- 不把 validation/测试题用于训练、调奖励或挑选视觉必需子集。
- 新数据版本应保留来源证据与重新封板流程；验证内容不能进入合成生成器。
- 不改写历史版本目录；新版本使用新的带日期目录。
- 需要核对旧版本时查 [docs/migration/](migration/) 中的封板清单与清理记录。
