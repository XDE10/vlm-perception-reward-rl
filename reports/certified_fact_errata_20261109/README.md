# 认证事实勘误（2026-11-09）

机器可读版本：[errata.json](errata.json)（15 条，涉及 22 行）。决策见
[决策记录](../../docs/plan/决策记录.md) D42。

## 来源与方法

- 对象：第三次预检 `preflight-20261109T122305Z-e6cd` 的 v5 校准（`calibration/calibration.json`，提交 7afad4a42150）中，
  默认阈值下被几何检验否定的认证正例（train 28 条，分布在 15 张图上），加上 validation 中被门控的 2 张图。
- 方法：我（Kiro）逐张查看公开 Geometry3K 包装数据（`hiyouga/geometry3k@fd21e53`）中的原图，对照认证事实、InterGPS
  坐标的测量值和 InterGPS 原始逻辑式，判断是哪一方错了。InterGPS 编号通过“像素哈希 + 规范化题面”与包装数据行对应。
- 这是 AI 看图核对，不是人工金标。已批准数据（release）没有任何改动，训练奖励也不变。

## 分类

| 类别 | 条目 | 行 | 含义 |
|---|---|---|---|
| `certified_fact_error` | 7 | 12（全在 train） | 认证事实本身与图不符，几何检验否定它是对的 |
| `coordinate_error` | 7 | 9（train 8，validation:179） | 认证事实与图相符，InterGPS 坐标偏了，几何检验误杀 |
| `unverifiable_no_point_labels` | 1 | 1（validation:165） | 图上没有印点名，认证事实里的点名无法从图上读出 |

`certified_fact_error` 的条目：

| 行 | 认证事实 | 图上实际 |
|---|---|---|
| train:425、598、1471、1488、1957、2090（同一张平面直角三角形图，像素哈希 `bb5f8a09…`，InterGPS 386/561/652/716/1738/1943） | `Perpendicular((A,C),(C,E))` | 直角在 C（CA 与 CB 之间），CE 是斜边 AB 上的高，∠ACE 画成 60°。InterGPS 原始逻辑式 `Perpendicular(Line(E, C), Line(A, C))` 就是错的，应为 CA ⊥ CB |
| train:1598（InterGPS 1209） | `Perpendicular((B,C),(C,D))` | 同一类错误：直角在 C，CD 是斜边上的高 |
| train:1251（1122） | `Perpendicular((K,L),(L,M))` | 同上：直角在 L（LJ 与 LK 之间），LM 是高 |
| train:335（1656） | `Perpendicular((T,U),(U,W))` | 同上：直角在 U（UV 与 UT 之间），UW 是高 |
| train:1729（913） | `Perpendicular((A,F),(F,H))` | 两个分开的直角三角形，图上没有线段 AF；F 处的直角在 FG 与 FH 之间，A 是 G 的笔误 |
| train:919（1217、1557） | `Perpendicular((Q,T),(R,S))` | RS 与 QT 画有相同的箭头（平行标记），夹角 0.75°；应为平行 |
| train:1783（80） | `PointLiesOnCircle(A,Circle(B))` 等 4 条 | 弦 AC 与 DE 交于圆内的 B，B 不是圆心 |

## 对校准结论的影响

- 留一法残余误杀共 16 条（D35，比例 1.2%）。其中垂直类 11 条全部属于 `certified_fact_error`，几何检验否定它们是正确的。
  其余 5 条（点在线上 2 条、点在圆上 3 条，来自 3 张图）属于 `coordinate_error`，是真正的误杀。
  所以几何检验对真实断言的误杀率约为 5 / 1314 ≈ 0.4%，低于 D35 报告的 1.2%（垂直类 4.2%）。
- 这只核对了被几何检验标出的事实。其他认证事实（例如长度、角度数值）没有用这种方式核对过，所以 12 行是错误行数的下限。
- 同一张图的多行（例如上表第一行的 6 行）不是独立证据。以后报告误杀时，同时给出按图计数。

## 对实验的影响与处理

- 训练：12 行（609 行的 2.0%）里共 15 条错误事实。v5 在模型声称这些事实时记 TRUE，不声称时少一份召回；
  每行的影响约为 λ × 1/|G+| ≈ 0.1 × 0.2 = 0.02 的奖励。v4、v5、安慰剂组用的是同一份 release，影响相同，不改。
- 评测（E1，validation 82 题）：validation:165 的认证点名无法从图上读出，任何模型都拿不到这部分召回；
  validation:179 只是坐标问题（已被门控）。E1 的主分析照原样使用 release；预注册的敏感性分析去掉这两行
  （见 [S3 设计](../../docs/plan/S3设计_20261109.md) 第 4 节）。
- 生成脚本：[build_errata.py](build_errata.py) 是在沙箱里运行过的原样副本（路径是沙箱路径）。它读取公开的固定版本数据和
  预检的 `calibration.json`；其中 `VERDICTS` 是我的看图结论，测量值都来自 `calibration.json`，可以逐条复核。
