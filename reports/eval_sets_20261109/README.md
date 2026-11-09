# 评测集定义（2026-11-09）

[eval_sets.json](eval_sets.json) 是 [S3 设计](../../docs/plan/S3设计_20261109.md) 第 1–3 节规则的执行结果，由
`python -m scripts.data.build_eval_sets` 从固定版本的公开数据生成（规则代码 `src/evaluation/eval_sets.py`，版本
`eval-sets-v1-20261109`）。生成过程只读题面、标准答案和 InterGPS 人工标注，没有运行任何模型。

| 内容 | 数量 | 说明 |
|---|---|---|
| `test601` | 601 | test 全部题目；601 题都与 InterGPS 记录唯一对应（像素哈希 + 规范化题面） |
| `test_vn` | 388 | 视觉必需子集（E3）；另有 213 题题面含数字，被排除 |
| `swap` | 601 对 | 换图条件的固定配对（种子 20261109），每对的图像像素都不同 |
| `cf_candidates` | 224 | CF-Geo 候选：validation 77 题、test 147 题；其中取整题 84 道（十分位 72、百分位 12），面积题 63 道 |

CF 候选被排除的原因（validation 与 test 合计）：不是视觉必需 321，长度标注是表达式 173，角度标注不是纯数字 108，
目标不是长度或面积 45，没有纯数字的长度标注 22，有其他类型的数值标注 6，取整说法无法识别 1，要求取整但答案不是纯小数 1。

数量与 train 上的估计相符（[估计报告](../s3_planning_estimates_20261109/README.md)：视觉必需 67.9%，CF 第 1–5 条 24.8%）：
test 上视觉必需 388/601 = 64.6%，CF 候选 224/901 = 24.9%。

## 复核

- 输入文件的 SHA256 先与 `migration_manifest.json` 中 `data/project3_sources/...` 的记录核对，不一致就停止。
  记录在文件的 `sources` 字段里。
- 生成时 InterGPS 记录由固定版本的 InterGPS 压缩包重建（`src/data/project3_audit.original_records`）。
  Colab VM 上改用数据包里的 `data/project3_audit/intergps_annotations.jsonl`，按同一规则重算，
  除 `built_from` 字段外必须与本文件完全相同（`v0` 任务的 `eval_sets` 步骤）。
- 这个文件只含题目编号、像素哈希、InterGPS 编号、标准答案和规则字段，不含图像。
