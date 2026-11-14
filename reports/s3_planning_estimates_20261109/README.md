# S3 规划估计（2026-11-09，只用 train）

[S3 设计](../../docs/plan/S3设计_20261109.md) 中的数量估计和 CF-Geo 可行性数字来自这里。四个脚本都只读 Geometry3K
**train**（公开包装数据 `hiyouga/geometry3k@fd21e53` 的 train parquet，InterGPS `@99e6b52` 的 `train.zip` 和逻辑式），
没有打开 validation 或 test 的题目、图片和答案。脚本是在沙箱里运行过的原样副本（路径是沙箱路径），`.out` 是那次运行的完整输出。

| 脚本 | 内容 | 结果 |
|---|---|---|
| [estimate_cf_exact_train.py](estimate_cf_exact_train.py) | S3 设计第 2 节和第 3.1 节第 1–4 条（用包装数据的真实题面；包装行与 InterGPS 记录按像素哈希加规范化题面对应），第 5 条用的是只收答案精确题的草案 | 视觉必需 1427/2101（67.9%）；CF 第 1–4 条 521（24.8%）；只收答案精确的题 312（14.9%） |
| [estimate_cf_rounding_train.py](estimate_cf_rounding_train.py) | 同上，但第 5 条改为 S3 设计的定稿版本：允许“nearest tenth / hundredth / thousandth”的取整题 | 满足 1–5 的 520 题：答案精确 312 题，取到十分位 191 题、百分位 17 题；只出现了这两种取整说法 |
| [estimate_subsets_train.py](estimate_subsets_train.py) | 较早的粗估：用 InterGPS 文本逻辑式代替题面判断数字 | 视觉必需 73.3%，CF 候选 26.2%。已被上一行取代，保留是因为下面两个脚本引用它 |
| [ocr_feasibility_train.py](ocr_feasibility_train.py) | 在 60 道随机 CF 候选上，OCR（rapidocr-onnxruntime 1.4.4）能否按标注找到每个长度数字 | 56/60 全部找到且次数一致 |
| [cfgeo_prototype_train.py](cfgeo_prototype_train.py) | 擦除并重画数字（k=1 原样重画，k=2 乘 2），再用 OCR 核验 | 40 道中 36 道 k=1 与 k=2 都通过 |

原型的已知问题（S3 设计第 3.2 节的规则已经针对它们修改）：擦除用的是灰度中位数，彩色背景上会留下灰块；
重画的字号按 OCR 框高估算，和原图字号不一致；字的颜色固定为黑色。

按题数折算（只是期望，不是 validation 或 test 上的统计）：test 中视觉必需约 408 题；CF-Geo 候选在 test 中约 149 题，
在 validation 公开 300 题中约 74 题，合计约 220 题，编辑核验后预计 160–200 题。
