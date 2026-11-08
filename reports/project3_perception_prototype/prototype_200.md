# 项目三 200 题训练集感知事实原型

仅从唯一关联的 train 采样。所有自动输出均未签字，training_approved=false。visual_candidate 不是 image-only 金标。

固定采样 namespace：`project3-train-perception-200-v1-20261023`；按 SHA256(namespace|original_id) 升序取前 200。

## 原始 ID 1826（train）

题面：<image>Find the perimeter of $▱ ABCD$.

参考答案：`28`

原图：[打开](<../../data/project3_perception_prototype/images/1826.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(D, C)), 4)
Equals(LengthOf(Line(D, A)), 10)
Equals(LengthOf(Line(D, E)), 5)
PointLiesOnLine(E, Line(C, B))
Perpendicular(Line(D, E), Line(B, E))
```

原始 text logic forms：

```text
Find(PerimeterOf(Parallelogram(A,B,C,D)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(D, C)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, A)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, E)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["D", "E"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(C, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(D, E), Line(B, E))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "E"], ["D", "E"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1910（train）

题面：<image>Quadrilateral ABCD is a rectangle. Find y

参考答案：`5`

原图：[打开](<../../data/project3_perception_prototype/images/1910.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(B, N, C)), 2x+1)
Equals(MeasureOf(Angle(E, N, D)), 5x+5)
Equals(MeasureOf(Angle(B, E, C)), y^2)
Equals(MeasureOf(Angle(B, D, C)), 3y+10)
PointLiesOnLine(E, Line(D, B))
PointLiesOnLine(E, Line(C, N))
PointLiesOnLine(G, Line(E, F))
```

原始 text logic forms：

```text
Rectangle(A,B,C,D)
Find(y)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(B, N, C)), 2x+1)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, N, D)), 5x+5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, E, C)), y^2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, D, C)), 3y+10)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(D, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(C, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(E, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2013（train）

题面：<image>Solve for $x$.

参考答案：`15`

原图：[打开](<../../data/project3_perception_prototype/images/2013.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(D, C, B)), 3x+25)
Equals(MeasureOf(Angle(C, D, B)), 4x+5)
Equals(MeasureOf(Angle(D, B, C)), 5x-30)
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(D, C, B)), 3x+25)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, D, B)), 4x+5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, B, C)), 5x-30)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 498（train）

题面：<image>Find the area of the shaded sector. Round to the nearest tenth.

参考答案：`4.5`

原图：[打开](<../../data/project3_perception_prototype/images/498.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(E, D, C)), 57)
PointLiesOnCircle(E, Circle(D, radius_0_0))
PointLiesOnCircle(C, Circle(D, radius_0_0))
```

原始 text logic forms：

```text
Find(AreaOf(Shaded(Sector($))))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(E, D, C)), 57)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "D", "E"], "value": "57", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(E, Circle(D, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(D, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1571（train）

题面：<image>Find $x$. $A = 78$ cm$^2$.

参考答案：`8.0`

原图：[打开](<../../data/project3_perception_prototype/images/1571.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, D)), 6.4)
Equals(LengthOf(Line(C, B)), 13)
Equals(LengthOf(Line(D, E)), x)
PointLiesOnLine(E, Line(C, B))
Perpendicular(Line(D, E), Line(E, C))
```

原始 text logic forms：

```text
Equals(AreaOf(Shape(A)),78)
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, D)), 6.4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "32/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, B)), 13)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "13", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, E)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(C, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(D, E), Line(E, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["C", "E"], ["D", "E"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1975（train）

题面：<image>Find the area of the parallelogram. Round to the nearest tenth if necessary.

参考答案：`70`

原图：[打开](<../../data/project3_perception_prototype/images/1975.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, E)), 10)
Equals(LengthOf(Line(N, B)), 7)
Equals(LengthOf(Line(N, C)), 12.2)
PointLiesOnLine(E, Line(B, N))
Perpendicular(Line(A, E), Line(E, N))
```

原始 text logic forms：

```text
Find(AreaOf(Parallelogram($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, E)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "E"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(N, B)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "N"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(N, C)), 12.2)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "N"], "value": "61/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(B, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, E), Line(E, N))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "E"], ["E", "N"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 351（train）

题面：<image>Find $m\angle B$

参考答案：`112`

原图：[打开](<../../data/project3_perception_prototype/images/351.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(A, B, C)), x-8)
Equals(MeasureOf(Angle(F, A, B)), x+2)
Equals(MeasureOf(Angle(B, C, D)), x+7)
Equals(MeasureOf(Angle(A, F, E)), x-4)
Equals(MeasureOf(Angle(F, E, D)), x+6)
Equals(MeasureOf(Angle(C, E, D)), x-3)
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(B)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(A, B, C)), x-8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, A, B)), x+2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, C, D)), x+7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, F, E)), x-4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, E, D)), x+6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, E, D)), x-3)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1288（train）

题面：<image>Find $MN$ if $\triangle JMN$ is an isosceles triangle with $\overline{JM} \cong \overline{M N}$.

参考答案：`3`

原图：[打开](<../../data/project3_perception_prototype/images/1288.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(M, J)), 2x-5)
Equals(LengthOf(Line(M, N)), 3x-9)
Equals(LengthOf(Line(N, J)), x-2)
```

原始 text logic forms：

```text
Isosceles(Triangle(J,M,N))
Equals(LengthOf(Line(J,M)),Line(M,N))
Find(LengthOf(Line(M,N)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(M, J)), 2x-5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(M, N)), 3x-9)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(N, J)), x-2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 540（train）

题面：<image>Point $S$ is the incenter of $\triangle JPL$. Find $m \angle MPQ$.

参考答案：`56`

原图：[打开](<../../data/project3_perception_prototype/images/540.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(J, K)), 8)
Equals(LengthOf(Line(J, S)), 10)
Equals(MeasureOf(Angle(K, L, S)), 24.5)
Equals(MeasureOf(Angle(K, P, L)), 28)
PointLiesOnLine(K, Line(L, J))
PointLiesOnLine(M, Line(L, P))
PointLiesOnLine(S, Line(L, Q))
PointLiesOnLine(Q, Line(J, P))
PointLiesOnLine(S, Line(J, M))
PointLiesOnLine(S, Line(P, K))
Perpendicular(Line(J, K), Line(S, K))
Perpendicular(Line(S, Q), Line(P, Q))
Perpendicular(Line(S, M), Line(M, P))
```

原始 text logic forms：

```text
IsIncenterOf(Point(S),Triangle(J,P,L))
Find(MeasureOf(Angle(M,P,Q)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(J, K)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["J", "K"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(J, S)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["J", "S"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(K, L, S)), 24.5)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["K", "L", "S"], "value": "49/2", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(K, P, L)), 28)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["K", "P", "L"], "value": "28", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(K, Line(L, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(L, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(L, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(J, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(J, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(P, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(J, K), Line(S, K))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["J", "K"], ["K", "S"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(S, Q), Line(P, Q))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["P", "Q"], ["Q", "S"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(S, M), Line(M, P))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["M", "P"], ["M", "S"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2044（train）

题面：<image>Find x.

参考答案：`24 \sqrt { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/2044.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), x)
Equals(LengthOf(Line(C, D)), y)
Equals(LengthOf(Line(A, D)), z)
Equals(LengthOf(Line(B, C)), 12)
Equals(LengthOf(Line(B, D)), 4)
PointLiesOnLine(D, Line(A, B))
Perpendicular(Line(C, D), Line(B, D))
Perpendicular(Line(A, C), Line(B, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(C, D)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, D)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, D)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(D, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(C, D), Line(B, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "D"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(A, C), Line(B, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1603（train）

题面：<image>Find the perimeter of $\triangle D E F$ if $\triangle D E F \sim \triangle A B C$

参考答案：`24`

原图：[打开](<../../data/project3_perception_prototype/images/1603.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, A)), 7)
Equals(LengthOf(Line(C, A)), 3)
Equals(LengthOf(Line(B, C)), 6)
Equals(LengthOf(Line(E, F)), 9)
```

原始 text logic forms：

```text
Similar(Triangle(D,E,F),Triangle(A,B,C))
Find(PerimeterOf(Triangle(D,E,F)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, A)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, A)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(E, F)), 9)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["E", "F"], "value": "9", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 304（train）

题面：<image>$\overline{JH}, \overline{JP},$ and $\overline{PH}$ are midsegments of $\triangle KLM$. Find $x$.

参考答案：`1.35`

原图：[打开](<../../data/project3_perception_prototype/images/304.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(J, P)), x)
Equals(LengthOf(Line(M, L)), 2.7)
PointLiesOnLine(P, Line(K, M))
PointLiesOnLine(J, Line(K, L))
PointLiesOnLine(H, Line(M, L))
```

原始 text logic forms：

```text
IsMidsegmentOf(Line(J,H),Triangle(K,L,M))
IsMidsegmentOf(Line(J,P),Triangle(K,L,M))
IsMidsegmentOf(Line(P,H),Triangle(K,L,M))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(J, P)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(M, L)), 2.7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["L", "M"], "value": "27/10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(P, Line(K, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(K, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(M, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 990（train）

题面：<image>Find y.

参考答案：`3 \sqrt { 13 }`

原图：[打开](<../../data/project3_perception_prototype/images/990.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, D)), 4)
Equals(LengthOf(Line(B, D)), 9)
Equals(LengthOf(Line(A, C)), x)
Equals(LengthOf(Line(A, D)), z)
Equals(LengthOf(Line(A, B)), y)
PointLiesOnLine(D, Line(B, C))
Perpendicular(Line(B, D), Line(A, D))
Perpendicular(Line(A, C), Line(A, B))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, D)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, D)), 9)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "9", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, D)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, B)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(B, D), Line(A, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "D"], ["B", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(A, C), Line(A, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 734（train）

题面：<image>Find the ratio of the area of the circle to the area of the square.

参考答案：`\frac { \pi } { 4 }`

原图：[打开](<../../data/project3_perception_prototype/images/734.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(D, H)), 3r)
PointLiesOnLine(D, Line(A, C))
PointLiesOnLine(J, Line(A, F))
PointLiesOnLine(I, Line(C, E))
PointLiesOnLine(B, Line(F, E))
PointLiesOnCircle(B, Circle(H, radius_7_0))
PointLiesOnCircle(D, Circle(H, radius_7_0))
PointLiesOnCircle(I, Circle(H, radius_7_0))
PointLiesOnCircle(J, Circle(H, radius_7_0))
```

原始 text logic forms：

```text
Find(RatioOf(AreaOf(Circle($)),AreaOf(Square($))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(D, H)), 3r)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(A, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(C, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(F, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(H, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(H, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(I, Circle(H, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(J, Circle(H, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1361（train）

题面：<image>In $\odot P$, the diameter is $9$, find the length of $\widehat {QT}$. Round to the nearest hundredth.

参考答案：`8.80`

原图：[打开](<../../data/project3_perception_prototype/images/1361.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(R, P, S)), 130)
Equals(MeasureOf(Angle(T, P, Q)), 112)
PointLiesOnLine(P, Line(T, R))
PointLiesOnCircle(S, Circle(P, radius_5_0))
PointLiesOnCircle(T, Circle(P, radius_5_0))
PointLiesOnCircle(R, Circle(P, radius_5_0))
PointLiesOnCircle(Q, Circle(P, radius_5_0))
```

原始 text logic forms：

```text
Circle(P)
Equals(DiameterOf(Circle($)),9)
Find(LengthOf(Arc(Q,T)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(R, P, S)), 130)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["R", "P", "S"], "value": "130", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(T, P, Q)), 112)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["Q", "P", "T"], "value": "112", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(P, Line(T, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(S, Circle(P, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(T, Circle(P, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(R, Circle(P, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(Q, Circle(P, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1641（train）

题面：<image>Find y

参考答案：`\sqrt { 33 }`

原图：[打开](<../../data/project3_perception_prototype/images/1641.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, D)), 8)
Equals(LengthOf(Line(A, B)), x)
Equals(LengthOf(Line(A, D)), z)
Equals(LengthOf(Line(C, D)), 3)
Perpendicular(Line(B, D), Line(A, D))
Perpendicular(Line(A, B), Line(A, C))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, D)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, D)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(C, D)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, D), Line(A, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "D"], ["B", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(A, B), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 556（train）

题面：<image>Find $y$.

参考答案：`4`

原图：[打开](<../../data/project3_perception_prototype/images/556.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, W)), 17+5y)
Equals(LengthOf(Line(D, H)), 3x-5)
Equals(LengthOf(Line(C, W)), 13x+6)
Equals(LengthOf(Line(L, P)), 4x-22)
PointLiesOnLine(N, Line(B, C))
PointLiesOnLine(R, Line(B, C))
PointLiesOnLine(T, Line(B, C))
PointLiesOnLine(P, Line(B, L))
PointLiesOnLine(R, Line(B, N))
PointLiesOnLine(T, Line(B, N))
PointLiesOnLine(R, Line(B, T))
PointLiesOnLine(C, Line(B, W))
PointLiesOnLine(N, Line(B, W))
PointLiesOnLine(R, Line(B, W))
PointLiesOnLine(T, Line(B, W))
PointLiesOnLine(B, Line(C, L))
PointLiesOnLine(N, Line(C, L))
PointLiesOnLine(P, Line(C, L))
PointLiesOnLine(R, Line(C, L))
PointLiesOnLine(T, Line(C, L))
PointLiesOnLine(B, Line(C, P))
PointLiesOnLine(N, Line(C, P))
PointLiesOnLine(R, Line(C, P))
PointLiesOnLine(T, Line(C, P))
PointLiesOnLine(N, Line(C, R))
PointLiesOnLine(T, Line(C, R))
PointLiesOnLine(N, Line(C, T))
PointLiesOnLine(B, Line(L, N))
PointLiesOnLine(P, Line(L, N))
PointLiesOnLine(R, Line(L, N))
PointLiesOnLine(T, Line(L, N))
PointLiesOnLine(B, Line(L, R))
PointLiesOnLine(P, Line(L, R))
PointLiesOnLine(B, Line(L, T))
PointLiesOnLine(P, Line(L, T))
PointLiesOnLine(R, Line(L, T))
PointLiesOnLine(B, Line(L, W))
PointLiesOnLine(C, Line(L, W))
PointLiesOnLine(N, Line(L, W))
PointLiesOnLine(P, Line(L, W))
PointLiesOnLine(R, Line(L, W))
PointLiesOnLine(T, Line(L, W))
PointLiesOnLine(G, Line(N, V))
PointLiesOnLine(B, Line(N, P))
PointLiesOnLine(R, Line(N, P))
PointLiesOnLine(T, Line(N, P))
PointLiesOnLine(T, Line(N, R))
PointLiesOnLine(C, Line(N, W))
PointLiesOnLine(Q, Line(P, Y))
PointLiesOnLine(H, Line(P, O))
PointLiesOnLine(B, Line(P, R))
PointLiesOnLine(B, Line(P, T))
PointLiesOnLine(R, Line(P, T))
PointLiesOnLine(B, Line(P, W))
PointLiesOnLine(C, Line(P, W))
PointLiesOnLine(N, Line(P, W))
PointLiesOnLine(R, Line(P, W))
PointLiesOnLine(T, Line(P, W))
PointLiesOnLine(C, Line(R, W))
PointLiesOnLine(N, Line(R, W))
PointLiesOnLine(T, Line(R, W))
PointLiesOnLine(C, Line(T, W))
PointLiesOnLine(N, Line(T, W))
PointLiesOnLine(H, Line(D, I))
PointLiesOnLine(U, Line(D, I))
PointLiesOnLine(H, Line(D, J))
PointLiesOnLine(I, Line(D, J))
PointLiesOnLine(K, Line(D, J))
PointLiesOnLine(U, Line(D, J))
PointLiesOnLine(H, Line(D, K))
PointLiesOnLine(I, Line(D, K))
PointLiesOnLine(U, Line(D, K))
PointLiesOnLine(H, Line(D, U))
PointLiesOnLine(P, Line(H, Y))
PointLiesOnLine(Q, Line(H, Y))
PointLiesOnLine(U, Line(H, I))
PointLiesOnLine(I, Line(H, J))
PointLiesOnLine(K, Line(H, J))
PointLiesOnLine(U, Line(H, J))
PointLiesOnLine(I, Line(H, K))
PointLiesOnLine(U, Line(H, K))
PointLiesOnLine(P, Line(H, Q))
PointLiesOnLine(K, Line(I, J))
PointLiesOnLine(I, Line(J, U))
PointLiesOnLine(K, Line(J, U))
PointLiesOnLine(N, Line(K, G))
PointLiesOnLine(G, Line(K, V))
PointLiesOnLine(N, Line(K, V))
PointLiesOnLine(I, Line(K, U))
PointLiesOnLine(N, Line(E, G))
PointLiesOnLine(G, Line(E, V))
PointLiesOnLine(N, Line(E, V))
PointLiesOnLine(S, Line(G, F))
PointLiesOnLine(F, Line(G, A))
PointLiesOnLine(Q, Line(G, A))
PointLiesOnLine(S, Line(G, A))
PointLiesOnLine(F, Line(G, Q))
PointLiesOnLine(S, Line(G, Q))
PointLiesOnLine(H, Line(Y, O))
PointLiesOnLine(P, Line(Y, O))
PointLiesOnLine(Q, Line(Y, O))
PointLiesOnLine(H, Line(O, Q))
PointLiesOnLine(P, Line(O, Q))
PointLiesOnLine(F, Line(Q, M))
PointLiesOnLine(G, Line(Q, M))
PointLiesOnLine(S, Line(Q, M))
PointLiesOnLine(F, Line(Q, S))
PointLiesOnLine(Q, Line(F, A))
PointLiesOnLine(G, Line(F, M))
PointLiesOnLine(S, Line(F, M))
PointLiesOnLine(F, Line(A, M))
PointLiesOnLine(G, Line(A, M))
PointLiesOnLine(Q, Line(A, M))
PointLiesOnLine(S, Line(A, M))
PointLiesOnLine(F, Line(A, S))
PointLiesOnLine(Q, Line(A, S))
PointLiesOnLine(G, Line(M, S))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, W)), 17+5y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(D, H)), 3x-5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(C, W)), 13x+6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(L, P)), 4x-22)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(B, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(B, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(B, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(B, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(B, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(B, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(B, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(B, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(C, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(C, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(C, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(C, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(C, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(C, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(C, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(C, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(C, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(C, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(C, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(C, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(L, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(L, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(L, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(L, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(L, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(L, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(L, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(L, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(L, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(L, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(L, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(L, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(L, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(L, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(L, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(N, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(N, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(N, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(N, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(N, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(N, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(P, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(P, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(P, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(P, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(P, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(P, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(P, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(P, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(P, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(P, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(R, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(R, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(R, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(T, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(T, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(D, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(D, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(D, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(D, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(D, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(D, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(H, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(H, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(H, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(H, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(H, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(H, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(H, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(H, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(H, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(I, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(J, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(J, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(K, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(K, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(K, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(K, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(E, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(E, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(G, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(G, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(G, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(G, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(G, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(G, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(Y, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(Y, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(Y, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(O, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(O, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(Q, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(Q, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(Q, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(Q, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(F, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(F, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(F, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(A, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(A, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(A, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(M, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 690（train）

题面：<image>If $MNPQ \sim XYZW,$ find the perimeter of $MNPQ$.

参考答案：`34`

原图：[打开](<../../data/project3_perception_prototype/images/690.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(N, P)), 10)
Equals(LengthOf(Line(W, X)), 4)
Equals(LengthOf(Line(Q, P)), 7)
Equals(LengthOf(Line(Q, M)), 8)
Equals(LengthOf(Line(N, M)), 9)
```

原始 text logic forms：

```text
Similar(Quadrilateral(M,N,P,Q),Quadrilateral(X,Y,Z,W))
Find(PerimeterOf(Quadrilateral(M,N,P,Q)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(N, P)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["N", "P"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(W, X)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["W", "X"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(Q, P)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "Q"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(Q, M)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["M", "Q"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(N, M)), 9)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["M", "N"], "value": "9", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 924（train）

题面：<image>Find x

参考答案：`3`

原图：[打开](<../../data/project3_perception_prototype/images/924.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), 3)
Equals(LengthOf(Line(A, C)), x)
Equals(MeasureOf(Angle(A, C, B)), 45)
Equals(LengthOf(Line(B, C)), y)
Perpendicular(Line(A, C), Line(A, B))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, C, B)), 45)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "C", "B"], "value": "45", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, C), Line(A, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 124（train）

题面：<image>Polygon $BCDE$ $\cong$ polygon $RSTU$. Find $x$.

参考答案：`20`

原图：[打开](<../../data/project3_perception_prototype/images/124.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, B)), 4w-7)
Equals(LengthOf(Line(U, T)), z+16)
Equals(MeasureOf(Angle(E, B, C)), 2x+9)
Equals(MeasureOf(Angle(U, T, S)), y+11)
Equals(LengthOf(Line(R, U)), 12)
Equals(LengthOf(Line(C, D)), 11)
Equals(MeasureOf(Angle(E, D, C)), 2y-31)
Equals(MeasureOf(Angle(S, R, U)), 49)
Equals(LengthOf(Line(R, S)), 2w+13)
Equals(LengthOf(Line(E, D)), 3z+10)
```

原始 text logic forms：

```text
Congruent(Quadrilateral(B,C,D,E),Quadrilateral(R,S,T,U))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, B)), 4w-7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(U, T)), z+16)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, B, C)), 2x+9)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(U, T, S)), y+11)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(R, U)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["R", "U"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, D)), 11)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "11", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(E, D, C)), 2y-31)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(S, R, U)), 49)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["S", "R", "U"], "value": "49", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, S)), 2w+13)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(E, D)), 3z+10)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 127（train）

题面：<image>In the figure, $m \angle 1=4 p+15$, $m \angle 3=3 p-10$ and $m \angle 4=6 r+5 $. Find the value of $r$.

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/127.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(A, B, H)), MeasureOf(angle 3))
Equals(MeasureOf(Angle(J, A, E)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(I, C, A)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(I, D, H)), MeasureOf(angle 4))
PointLiesOnLine(B, Line(E, A))
PointLiesOnLine(A, Line(E, L))
PointLiesOnLine(B, Line(E, L))
PointLiesOnLine(C, Line(A, G))
PointLiesOnLine(D, Line(B, F))
PointLiesOnLine(A, Line(B, L))
PointLiesOnLine(A, Line(G, J))
PointLiesOnLine(C, Line(G, J))
PointLiesOnLine(A, Line(J, C))
PointLiesOnLine(D, Line(C, K))
PointLiesOnLine(B, Line(F, H))
PointLiesOnLine(D, Line(F, H))
PointLiesOnLine(B, Line(H, D))
PointLiesOnLine(C, Line(D, I))
PointLiesOnLine(C, Line(I, K))
PointLiesOnLine(D, Line(I, K))
Parallel(Line(A, L), Line(C, I))
Parallel(Line(B, H), Line(A, J))
```

原始 text logic forms：

```text
Equals(MeasureOf(Angle(1)),4p+15)
Equals(MeasureOf(Angle(3)),3p-10)
Equals(MeasureOf(Angle(4)),6r+5)
Find(r)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(A, B, H)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(J, A, E)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(I, C, A)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(I, D, H)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(E, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(E, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(E, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(A, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(B, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(B, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(G, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(G, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(J, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(C, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(F, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(F, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(H, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(D, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(I, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(I, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(A, L), Line(C, I))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["A", "L"], ["C", "I"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(B, H), Line(A, J))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["A", "J"], ["B", "H"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1521（train）

题面：<image>Circle $A$ has diameters $\overline{D F}$ and $\overline{P G}$

If $P A=7,$ find $P G$

参考答案：`14`

原图：[打开](<../../data/project3_perception_prototype/images/1521.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(A, Line(G, P))
PointLiesOnLine(A, Line(F, D))
PointLiesOnCircle(G, Circle(A, radius_1_0))
PointLiesOnCircle(F, Circle(A, radius_1_0))
PointLiesOnCircle(D, Circle(A, radius_1_0))
PointLiesOnCircle(P, Circle(A, radius_1_0))
PointLiesOnCircle(L, Circle(A, radius_1_0))
```

原始 text logic forms：

```text
IsDiameterOf(Line(D,F),Circle(A))
IsDiameterOf(Line(P,G),Circle(A))
Equals(LengthOf(Line(P,A)),7)
Find(LengthOf(Line(P,G)))
```

有限 schema 结果：

- `PointLiesOnLine(A, Line(G, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(F, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(G, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(P, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(L, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1849（train）

题面：<image>Find $m\angle F$

参考答案：`116`

原图：[打开](<../../data/project3_perception_prototype/images/1849.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(A, B, C)), x-8)
Equals(MeasureOf(Angle(F, A, B)), x+2)
Equals(MeasureOf(Angle(B, C, D)), x+7)
Equals(MeasureOf(Angle(A, F, E)), x-4)
Equals(MeasureOf(Angle(F, E, D)), x+6)
Equals(MeasureOf(Angle(C, E, D)), x-3)
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(F)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(A, B, C)), x-8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, A, B)), x+2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, C, D)), x+7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, F, E)), x-4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, E, D)), x+6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, E, D)), x-3)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 857（train）

题面：<image>Find y

参考答案：`\frac { 5 } { 3 }`

原图：[打开](<../../data/project3_perception_prototype/images/857.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, C)), z)
Equals(LengthOf(Line(B, A)), 15)
Equals(LengthOf(Line(A, C)), 5)
PointLiesOnLine(Y, Line(A, B))
Perpendicular(Line(B, Y), Line(C, Y))
Perpendicular(Line(B, C), Line(C, A))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, C)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, A)), 15)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "15", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(Y, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(B, Y), Line(C, Y))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "Y"], ["C", "Y"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, C), Line(C, A))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 949（train）

题面：<image>Find the exact circumference of each circle.

参考答案：`5 \pi`

原图：[打开](<../../data/project3_perception_prototype/images/949.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, D)), 3)
Equals(LengthOf(Line(A, C)), 4)
PointLiesOnLine(E, Line(A, D))
PointLiesOnCircle(A, Circle(E, radius_4_0))
PointLiesOnCircle(C, Circle(E, radius_4_0))
PointLiesOnCircle(D, Circle(E, radius_4_0))
Perpendicular(Line(C, D), Line(A, C))
```

原始 text logic forms：

```text
Find(CircumferenceOf(Circle($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, D)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(A, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(C, D), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1187（train）

题面：<image>Find x. Round the side measure to the nearest tenth.

参考答案：`117.6`

原图：[打开](<../../data/project3_perception_prototype/images/1187.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(B, A, C)), 19)
Equals(LengthOf(Line(A, C)), x)
Equals(MeasureOf(Angle(A, B, C)), 111)
Equals(LengthOf(Line(B, C)), 41)
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(B, A, C)), 19)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "A", "C"], "value": "19", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, B, C)), 111)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "B", "C"], "value": "111", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), 41)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "41", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1822（train）

题面：<image>Find x.

参考答案：`0.5`

原图：[打开](<../../data/project3_perception_prototype/images/1822.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), x+1)
Equals(LengthOf(Line(B, C)), x)
Equals(LengthOf(Line(A, C)), 2\sqrt{2})
Perpendicular(Line(B, C), Line(A, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), x+1)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, C)), 2\sqrt{2})` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(B, C), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2057（train）

题面：<image>Find the area of the trapezoid.

参考答案：`272`

原图：[打开](<../../data/project3_perception_prototype/images/2057.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, D)), 10)
Equals(LengthOf(Line(A, E)), 17)
Equals(LengthOf(Line(B, C)), 22)
PointLiesOnLine(E, Line(C, B))
Perpendicular(Line(A, E), Line(E, B))
```

原始 text logic forms：

```text
Find(AreaOf(Trapezoid($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, D)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, E)), 17)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "E"], "value": "17", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), 22)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "22", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(C, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, E), Line(E, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "E"], ["B", "E"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1607（train）

题面：<image>Find x

参考答案：`24`

原图：[打开](<../../data/project3_perception_prototype/images/1607.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(M, X)), 5)
Equals(LengthOf(Line(M, J)), 13)
PointLiesOnLine(X, Line(R, S))
PointLiesOnCircle(J, Circle(M, radius_0_0))
PointLiesOnCircle(S, Circle(M, radius_0_0))
PointLiesOnCircle(R, Circle(M, radius_0_0))
Perpendicular(Line(X, R), Line(M, X))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(M, X)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["M", "X"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(M, J)), 13)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["J", "M"], "value": "13", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(X, Line(R, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(J, Circle(M, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(S, Circle(M, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(R, Circle(M, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(X, R), Line(M, X))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["M", "X"], ["R", "X"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1656（train）

题面：<image>Find the measure of the altitude drawn to the hypotenuse.

参考答案：`\sqrt { 26 }`

原图：[打开](<../../data/project3_perception_prototype/images/1656.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(V, W)), 2)
Equals(LengthOf(Line(T, V)), 13)
PointLiesOnLine(W, Line(T, V))
Perpendicular(Line(T, W), Line(U, W))
Perpendicular(Line(U, W), Line(T, U))
```

原始 text logic forms：

```text
Equals(Line($1,$3),HypotenuseOf(Triangle($1,$2,$3)))
Find(LengthOf(AltitudeOf(Triangle($1,$2,$3))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(V, W)), 2)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["V", "W"], "value": "2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(T, V)), 13)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["T", "V"], "value": "13", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(W, Line(T, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(T, W), Line(U, W))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["T", "W"], ["U", "W"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(U, W), Line(T, U))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["T", "U"], ["U", "W"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2014（train）

题面：<image>Find x

参考答案：`22.6`

原图：[打开](<../../data/project3_perception_prototype/images/2014.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), 6.6)
Equals(MeasureOf(Angle(A, B, C)), 17)
PointLiesOnLine(x, Line(C, B))
Perpendicular(Line(A, B), Line(A, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), 6.6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "33/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, B, C)), 17)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "B", "C"], "value": "17", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(x, Line(C, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, B), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1987（train）

题面：<image>Find the measure of $m \widehat{GH}$.

参考答案：`56`

原图：[打开](<../../data/project3_perception_prototype/images/1987.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(G, A, H)), 28)
PointLiesOnCircle(A, Circle(B, radius_3_0))
PointLiesOnCircle(G, Circle(B, radius_3_0))
PointLiesOnCircle(H, Circle(B, radius_3_0))
```

原始 text logic forms：

```text
Find(MeasureOf(Arc(G,H)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(G, A, H)), 28)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["G", "A", "H"], "value": "28", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(A, Circle(B, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(G, Circle(B, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(H, Circle(B, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1964（train）

题面：<image>Find the area of the trapezoid. 

参考答案：`500`

原图：[打开](<../../data/project3_perception_prototype/images/1964.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(E, F)), 2)
Equals(LengthOf(Line(B, N)), 10)
Equals(LengthOf(Line(A, C)), 19)
Equals(LengthOf(Line(N, C)), 20)
PointLiesOnLine(F, Line(E, B))
Perpendicular(Line(A, F), Line(F, B))
PointLiesOnLine(N, Line(E, B))
Perpendicular(Line(C, N), Line(N, E))
```

原始 text logic forms：

```text
Find(AreaOf(Trapezoid($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(E, F)), 2)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["E", "F"], "value": "2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, N)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "N"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), 19)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "19", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(N, C)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "N"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(F, Line(E, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, F), Line(F, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "F"], ["B", "F"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(N, Line(E, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(C, N), Line(N, E))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["C", "N"], ["E", "N"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1943（train）

题面：<image>If $x=7 \sqrt{3},$ find $a$

参考答案：`14 \sqrt { 3 }`

原图：[打开](<../../data/project3_perception_prototype/images/1943.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(C, B, E)), 60)
Equals(LengthOf(Line(E, A)), y)
Equals(LengthOf(Line(C, B)), LengthOf(a))
Equals(MeasureOf(Angle(C, A, B)), 30)
Equals(LengthOf(Line(A, C)), LengthOf(b))
PointLiesOnLine(E, Line(A, B))
Perpendicular(Line(E, A), Line(E, C))
Perpendicular(Line(E, C), Line(A, C))
```

原始 text logic forms：

```text
Equals(x,7\sqrt{3})
Find(a)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(C, B, E)), 60)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "B", "E"], "value": "60", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(E, A)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(C, B)), LengthOf(a))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, A, B)), 30)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "A", "C"], "value": "30", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), LengthOf(b))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(E, A), Line(E, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "E"], ["C", "E"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(E, C), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["C", "E"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 636（train）

题面：<image>If $m\angle XZY = 3x + 6$ and $m\angle XZW = 5x - 12$, find $m\angle YXZ$.

参考答案：`48`

原图：[打开](<../../data/project3_perception_prototype/images/636.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(P, Line(W, Y))
PointLiesOnLine(P, Line(Z, X))
Perpendicular(Line(W, X), Line(W, Z))
```

原始 text logic forms：

```text
Equals(MeasureOf(Angle(X,Z,Y)),3x+6)
Equals(MeasureOf(Angle(X,Z,W)),5x-12)
Find(MeasureOf(Angle(Y,X,Z)))
```

有限 schema 结果：

- `PointLiesOnLine(P, Line(W, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(Z, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(W, X), Line(W, Z))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["W", "X"], ["W", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 867（train）

题面：<image>Find $m \angle MRP$.

参考答案：`60`

原图：[打开](<../../data/project3_perception_prototype/images/867.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(M, P)), LengthOf(Line(M, R)))
Equals(LengthOf(Line(M, R)), LengthOf(Line(R, P)))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(M,R,P)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(M, P)), LengthOf(Line(M, R)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(M, R)), LengthOf(Line(R, P)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 805（train）

题面：<image>Find $y$.

参考答案：`5`

原图：[打开](<../../data/project3_perception_prototype/images/805.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, R)), 4)
Equals(LengthOf(Line(G, point_26)), 20-5x)
Equals(LengthOf(Line(K, P)), 3)
Equals(LengthOf(Line(J, point_27)), 2x+6)
Equals(LengthOf(Line(H, M)), y+2)
Equals(LengthOf(Line(H, M)), 5)
PointLiesOnLine(J, Line(B, I))
PointLiesOnLine(Q, Line(B, I))
PointLiesOnLine(R, Line(B, I))
PointLiesOnLine(R, Line(B, J))
PointLiesOnLine(J, Line(B, Q))
PointLiesOnLine(R, Line(B, Q))
PointLiesOnLine(Q, Line(I, J))
PointLiesOnLine(J, Line(I, R))
PointLiesOnLine(Q, Line(I, R))
PointLiesOnLine(N, Line(J, K))
PointLiesOnLine(U, Line(J, K))
PointLiesOnLine(U, Line(J, N))
PointLiesOnLine(K, Line(J, P))
PointLiesOnLine(N, Line(J, P))
PointLiesOnLine(U, Line(J, P))
PointLiesOnLine(M, Line(Q, H))
PointLiesOnLine(S, Line(Q, H))
PointLiesOnLine(V, Line(Q, H))
PointLiesOnLine(S, Line(Q, M))
PointLiesOnLine(V, Line(Q, M))
PointLiesOnLine(J, Line(Q, R))
PointLiesOnLine(S, Line(Q, V))
PointLiesOnLine(L, Line(R, E))
PointLiesOnLine(W, Line(R, E))
PointLiesOnLine(E, Line(R, O))
PointLiesOnLine(L, Line(R, O))
PointLiesOnLine(W, Line(R, O))
PointLiesOnLine(Z, Line(R, O))
PointLiesOnLine(G, Line(R, T))
PointLiesOnLine(L, Line(R, W))
PointLiesOnLine(E, Line(R, Z))
PointLiesOnLine(L, Line(R, Z))
PointLiesOnLine(W, Line(R, Z))
PointLiesOnLine(Q, Line(X, C))
PointLiesOnLine(M, Line(X, H))
PointLiesOnLine(Q, Line(X, H))
PointLiesOnLine(S, Line(X, H))
PointLiesOnLine(V, Line(X, H))
PointLiesOnLine(Q, Line(X, M))
PointLiesOnLine(S, Line(X, M))
PointLiesOnLine(V, Line(X, M))
PointLiesOnLine(Q, Line(X, S))
PointLiesOnLine(Q, Line(X, V))
PointLiesOnLine(S, Line(X, V))
PointLiesOnLine(point_27, Line(C, F))
PointLiesOnLine(M, Line(C, H))
PointLiesOnLine(S, Line(C, V))
PointLiesOnLine(J, Line(F, D))
PointLiesOnLine(M, Line(H, S))
PointLiesOnLine(V, Line(H, S))
PointLiesOnLine(M, Line(H, V))
PointLiesOnLine(K, Line(M, E))
PointLiesOnLine(E, Line(M, A))
PointLiesOnLine(K, Line(M, A))
PointLiesOnLine(V, Line(M, S))
PointLiesOnLine(J, Line(D, K))
PointLiesOnLine(N, Line(D, K))
PointLiesOnLine(U, Line(D, K))
PointLiesOnLine(J, Line(D, N))
PointLiesOnLine(U, Line(D, N))
PointLiesOnLine(J, Line(D, P))
PointLiesOnLine(K, Line(D, P))
PointLiesOnLine(N, Line(D, P))
PointLiesOnLine(U, Line(D, P))
PointLiesOnLine(J, Line(D, U))
PointLiesOnLine(E, Line(K, A))
PointLiesOnLine(N, Line(K, U))
PointLiesOnLine(M, Line(K, Y))
PointLiesOnLine(K, Line(N, P))
PointLiesOnLine(K, Line(P, U))
PointLiesOnLine(N, Line(P, U))
PointLiesOnLine(F, Line(point_27, L))
PointLiesOnLine(L, Line(E, G))
PointLiesOnLine(R, Line(E, G))
PointLiesOnLine(W, Line(E, G))
PointLiesOnLine(W, Line(E, L))
PointLiesOnLine(Z, Line(E, O))
PointLiesOnLine(G, Line(E, T))
PointLiesOnLine(L, Line(E, T))
PointLiesOnLine(R, Line(E, T))
PointLiesOnLine(W, Line(E, T))
PointLiesOnLine(K, Line(E, Y))
PointLiesOnLine(M, Line(E, Y))
PointLiesOnLine(L, Line(E, point_26))
PointLiesOnLine(W, Line(E, point_26))
PointLiesOnLine(R, Line(G, L))
PointLiesOnLine(E, Line(G, O))
PointLiesOnLine(L, Line(G, O))
PointLiesOnLine(R, Line(G, O))
PointLiesOnLine(W, Line(G, O))
PointLiesOnLine(Z, Line(G, O))
PointLiesOnLine(L, Line(G, W))
PointLiesOnLine(R, Line(G, W))
PointLiesOnLine(E, Line(G, Z))
PointLiesOnLine(R, Line(G, Z))
PointLiesOnLine(W, Line(G, Z))
PointLiesOnLine(E, Line(L, O))
PointLiesOnLine(W, Line(L, O))
PointLiesOnLine(Z, Line(L, O))
PointLiesOnLine(G, Line(L, T))
PointLiesOnLine(R, Line(L, T))
PointLiesOnLine(E, Line(L, Z))
PointLiesOnLine(W, Line(L, Z))
PointLiesOnLine(E, Line(O, T))
PointLiesOnLine(G, Line(O, T))
PointLiesOnLine(L, Line(O, T))
PointLiesOnLine(R, Line(O, T))
PointLiesOnLine(W, Line(O, T))
PointLiesOnLine(Z, Line(O, T))
PointLiesOnLine(E, Line(O, W))
PointLiesOnLine(Z, Line(O, W))
PointLiesOnLine(E, Line(O, point_26))
PointLiesOnLine(L, Line(O, point_26))
PointLiesOnLine(Z, Line(O, point_26))
PointLiesOnLine(E, Line(A, Y))
PointLiesOnLine(K, Line(A, Y))
PointLiesOnLine(M, Line(A, Y))
PointLiesOnLine(G, Line(T, W))
PointLiesOnLine(L, Line(T, W))
PointLiesOnLine(R, Line(T, W))
PointLiesOnLine(E, Line(T, Z))
PointLiesOnLine(G, Line(T, Z))
PointLiesOnLine(L, Line(T, Z))
PointLiesOnLine(R, Line(T, Z))
PointLiesOnLine(W, Line(T, Z))
PointLiesOnLine(E, Line(W, Z))
PointLiesOnLine(L, Line(W, point_26))
PointLiesOnLine(R, Line(W, point_26))
PointLiesOnLine(E, Line(Z, point_26))
PointLiesOnLine(L, Line(Z, point_26))
PointLiesOnLine(W, Line(Z, point_26))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, R)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "R"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(G, point_26)), 20-5x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(K, P)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["K", "P"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(J, point_27)), 2x+6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(H, M)), y+2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(H, M)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["H", "M"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(J, Line(B, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(B, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(B, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(B, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(B, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(I, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(I, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(I, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(J, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(J, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(J, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(J, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(J, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(J, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(Q, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(Q, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(Q, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(Q, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(Q, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(Q, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(Q, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(R, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(R, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(R, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(R, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(R, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(R, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(R, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(R, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(R, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(R, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(R, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(X, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(X, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(X, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(X, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(X, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(X, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(X, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(X, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(X, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(X, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(X, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(point_27, Line(C, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(C, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(C, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(F, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(H, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(H, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(H, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(M, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(M, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(M, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(M, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(D, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(D, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(D, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(D, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(D, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(D, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(D, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(D, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(D, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(D, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(K, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(K, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(K, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(N, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(P, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(P, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(point_27, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(E, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(E, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(E, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(E, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(E, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(E, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(E, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(E, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(E, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(E, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(G, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(G, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(G, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(G, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(G, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(G, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(G, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(G, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(G, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(G, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(G, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(L, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(L, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(L, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(L, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(L, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(L, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(L, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(O, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(O, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(O, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(O, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(O, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(O, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(O, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(O, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(O, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(O, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(O, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(A, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(A, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(T, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(T, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(T, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(T, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(T, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(T, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(T, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(T, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(W, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(W, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(W, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(Z, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(Z, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(Z, point_26))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1852（train）

题面：<image>Use parallelogram to find $y$

参考答案：`5`

原图：[打开](<../../data/project3_perception_prototype/images/1852.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(N, K)), 2z+7)
Equals(LengthOf(Line(J, N)), 3y-5)
Equals(LengthOf(Line(L, N)), y+5)
Equals(LengthOf(Line(N, M)), z+9)
PointLiesOnLine(N, Line(L, J))
PointLiesOnLine(N, Line(M, K))
```

原始 text logic forms：

```text
Parallelogram($)
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(N, K)), 2z+7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(J, N)), 3y-5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(L, N)), y+5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(N, M)), z+9)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(L, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(M, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 933（train）

题面：<image>Find $JL$.

参考答案：`12`

原图：[打开](<../../data/project3_perception_prototype/images/933.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(J, M)), 6)
PointLiesOnLine(M, Line(K, A))
PointLiesOnLine(M, Line(L, J))
PointLiesOnLine(K, Line(M, C))
PointLiesOnLine(K, Line(A, C))
PointLiesOnLine(M, Line(A, C))
Perpendicular(Line(L, M), Line(K, M))
Equals(LengthOf(Line(K, J)), LengthOf(Line(K, L)))
```

原始 text logic forms：

```text
Find(LengthOf(Line(J,L)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(J, M)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["J", "M"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(M, Line(K, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(L, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(M, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(L, M), Line(K, M))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["K", "M"], ["L", "M"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(K, J)), LengthOf(Line(K, L)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 721（train）

题面：<image>If $LK=4,MP=3,PQ=6,KJ=2,RS=6$, and $LP=2$, find $QK$.

参考答案：`6`

原图：[打开](<../../data/project3_perception_prototype/images/721.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(K, Line(H, M))
PointLiesOnLine(K, Line(M, J))
PointLiesOnLine(K, Line(H, L))
PointLiesOnLine(K, Line(L, J))
PointLiesOnLine(J, Line(H, M))
PointLiesOnLine(J, Line(H, K))
PointLiesOnLine(J, Line(H, L))
PointLiesOnLine(L, Line(H, M))
PointLiesOnLine(L, Line(M, K))
PointLiesOnLine(L, Line(M, J))
PointLiesOnLine(Q, Line(M, S))
PointLiesOnLine(Q, Line(M, R))
PointLiesOnLine(Q, Line(P, S))
PointLiesOnLine(Q, Line(P, R))
PointLiesOnLine(R, Line(M, S))
PointLiesOnLine(R, Line(S, Q))
PointLiesOnLine(R, Line(S, P))
PointLiesOnLine(P, Line(M, S))
PointLiesOnLine(P, Line(M, Q))
PointLiesOnLine(P, Line(M, R))
Parallel(Line(J, R), Line(H, S))
Parallel(Line(H, S), Line(K, Q))
Parallel(Line(L, P), Line(K, Q))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(L,K)),4)
Equals(LengthOf(Line(M,P)),3)
Equals(LengthOf(Line(P,Q)),6)
Equals(LengthOf(Line(K,J)),2)
Equals(LengthOf(Line(R,S)),6)
Equals(LengthOf(Line(L,P)),2)
Find(LengthOf(Line(Q,K)))
```

有限 schema 结果：

- `PointLiesOnLine(K, Line(H, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(M, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(H, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(L, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(H, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(H, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(H, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(H, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(M, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(M, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(M, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(M, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(P, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(P, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(M, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(S, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(S, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(M, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(M, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(M, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(J, R), Line(H, S))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["H", "S"], ["J", "R"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(H, S), Line(K, Q))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["H", "S"], ["K", "Q"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(L, P), Line(K, Q))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["K", "Q"], ["L", "P"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1937（train）

题面：<image>Find $DF$.

参考答案：`5`

原图：[打开](<../../data/project3_perception_prototype/images/1937.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(G, D)), 10)
PointLiesOnLine(H, Line(F, L))
PointLiesOnLine(F, Line(D, G))
Perpendicular(Line(F, D), Line(H, F))
Equals(LengthOf(Line(H, D)), LengthOf(Line(H, G)))
```

原始 text logic forms：

```text
Find(LengthOf(Line(D,F)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(G, D)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["D", "G"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(H, Line(F, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(D, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(F, D), Line(H, F))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["D", "F"], ["F", "H"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(H, D)), LengthOf(Line(H, G)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 855（train）

题面：<image>Find the value of the variable $y$ in the figure.

参考答案：`14`

原图：[打开](<../../data/project3_perception_prototype/images/855.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(E, J, C)), 2x)
Equals(MeasureOf(Angle(J, C, A)), 96)
Equals(MeasureOf(Angle(A, E, J)), 3y+44)
Equals(MeasureOf(Angle(C, A, E)), 94)
Parallel(Line(C,A), Line(J,E))

```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(E, J, C)), 2x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(J, C, A)), 96)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "C", "J"], "value": "96", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, E, J)), 3y+44)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, A, E)), 94)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "A", "E"], "value": "94", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(C,A), Line(J,E))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["A", "C"], ["E", "J"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 718（train）

题面：<image>Find z.

参考答案：`20 \sqrt { 5 }`

原图：[打开](<../../data/project3_perception_prototype/images/718.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), x)
Equals(LengthOf(Line(B, C)), z)
Equals(LengthOf(Line(A, B)), 20)
Equals(LengthOf(Line(A, D)), 10)
Equals(LengthOf(Line(B, D)), y)
PointLiesOnLine(A, Line(C, D))
Perpendicular(Line(A, C), Line(A, B))
Perpendicular(Line(B, C), Line(B, D))
```

原始 text logic forms：

```text
Find(z)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, B)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, D)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, D)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(C, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, C), Line(A, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, C), Line(B, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "C"], ["B", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1704（train）

题面：<image>Find $x$.

参考答案：`3`

原图：[打开](<../../data/project3_perception_prototype/images/1704.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(U, T)), 9)
Equals(LengthOf(Line(R, T)), x)
Equals(LengthOf(Line(V, S)), 5)
Equals(LengthOf(Line(R, S)), 4)
Equals(LengthOf(Line(R, V)), 5)
PointLiesOnLine(T, Line(R, U))
PointLiesOnLine(S, Line(R, V))
PointLiesOnLine(T, Line(R, B))
PointLiesOnCircle(U, Circle(B, radius_4_0))
PointLiesOnCircle(V, Circle(B, radius_4_0))
PointLiesOnCircle(S, Circle(B, radius_4_0))
PointLiesOnCircle(T, Circle(B, radius_4_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(U, T)), 9)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["T", "U"], "value": "9", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, T)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(V, S)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["S", "V"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, S)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["R", "S"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, V)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["R", "V"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(T, Line(R, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(R, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(R, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(U, Circle(B, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(V, Circle(B, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(S, Circle(B, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(T, Circle(B, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1892（train）

题面：<image>$\overline{JH}$ is a midsegment of $\triangle KLM$. Find $x$.

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/1892.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(H, J)), 5)
Equals(LengthOf(Line(L, M)), x)
PointLiesOnLine(X, Line(M, L))
PointLiesOnLine(H, Line(M, K))
PointLiesOnLine(J, Line(K, L))
```

原始 text logic forms：

```text
IsMidsegmentOf(Line(J,H),Triangle(K,L,M))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(H, J)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["H", "J"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(L, M)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(X, Line(M, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(M, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(K, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 321（train）

题面：<image>Chords $\overline{A C}$ and $\overline{D F}$ are equidistant from the center. If the radius of $\odot G$ is 26 find $D E$

参考答案：`24`

原图：[打开](<../../data/project3_perception_prototype/images/321.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, G)), 10)
Equals(LengthOf(Line(E, G)), 10)
PointLiesOnLine(E, Line(D, F))
PointLiesOnLine(B, Line(A, C))
PointLiesOnCircle(D, Circle(G, radius_2_0))
PointLiesOnCircle(A, Circle(G, radius_2_0))
PointLiesOnCircle(F, Circle(G, radius_2_0))
PointLiesOnCircle(C, Circle(G, radius_2_0))
```

原始 text logic forms：

```text
IsChordOf(Line(A,C),Circle($))
IsChordOf(Line(D,F),Circle($))
Line(A,C)
Line(D,F)
Equals(RadiusOf(Circle(G)),26)
Find(LengthOf(Line(D,E)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, G)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "G"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(E, G)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["E", "G"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(G, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(G, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(G, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(G, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1109（train）

题面：<image>Find $x$.

参考答案：`80`

原图：[打开](<../../data/project3_perception_prototype/images/1109.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(C, B, D)), 155)
Equals(MeasureOf(Angle(A, B, D)), 125)
Equals(MeasureOf(Angle(C, B, A)), x)

PointLiesOnCircle(A, Circle(B, radius_1_0))
PointLiesOnCircle(C, Circle(B, radius_1_0))
PointLiesOnCircle(D, Circle(B, radius_1_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(C, B, D)), 155)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "B", "D"], "value": "155", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, B, D)), 125)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "B", "D"], "value": "125", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, B, A)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(B, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(B, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(B, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 476（train）

题面：<image>Find the measure of $m\angle 3$. Assume that segments that appear

tangent are tangent.

参考答案：`26`

原图：[打开](<../../data/project3_perception_prototype/images/476.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, E)), 3)
Equals(MeasureOf(Angle(F, B, E)), 28)
Equals(MeasureOf(Angle(H, M, B)), 12)
PointLiesOnLine(K, Line(A, E))
PointLiesOnLine(K, Line(A, I))
PointLiesOnLine(L, Line(B, C))
PointLiesOnLine(A, Line(B, D))
PointLiesOnLine(J, Line(B, K))
PointLiesOnLine(B, Line(C, F))
PointLiesOnLine(L, Line(C, F))
PointLiesOnLine(L, Line(C, J))
PointLiesOnLine(I, Line(D, E))
PointLiesOnLine(A, Line(D, J))
PointLiesOnLine(I, Line(E, K))
PointLiesOnLine(J, Line(E, M))
PointLiesOnLine(B, Line(F, J))
PointLiesOnLine(J, Line(F, K))
PointLiesOnLine(B, Line(F, L))
PointLiesOnLine(A, Line(K, M))
PointLiesOnCircle(B, Circle(G, radius_6_0))
PointLiesOnCircle(D, Circle(G, radius_6_0))
PointLiesOnCircle(H, Circle(G, radius_6_0))
PointLiesOnCircle(I, Circle(G, radius_6_0))
PointLiesOnCircle(L, Circle(G, radius_6_0))
```

原始 text logic forms：

```text
Tangent(Line($),Circle($))
Find(MeasureOf(Angle(3)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, E)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "E"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(F, B, E)), 28)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["E", "B", "F"], "value": "28", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(H, M, B)), 12)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "M", "H"], "value": "12", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(K, Line(A, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(A, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(C, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(C, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(C, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(D, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(E, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(E, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(F, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(F, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(F, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(K, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(G, radius_6_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(G, radius_6_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(H, Circle(G, radius_6_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(I, Circle(G, radius_6_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(L, Circle(G, radius_6_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1567（train）

题面：<image>Solve for $x$ in the figure below.

参考答案：`31`

原图：[打开](<../../data/project3_perception_prototype/images/1567.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(K, H, G)), 65)
Equals(MeasureOf(Angle(L, D, F)), 4x-9)
PointLiesOnLine(D, Line(B, L))
PointLiesOnLine(H, Line(D, G))
PointLiesOnLine(H, Line(E, K))
PointLiesOnLine(D, Line(H, F))
PointLiesOnLine(D, Line(F, G))
PointLiesOnLine(H, Line(F, G))
Parallel(Line(B,L), Line(E,K))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(K, H, G)), 65)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["G", "H", "K"], "value": "65", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(L, D, F)), 4x-9)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(B, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(D, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(E, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(H, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(F, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(F, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(B,L), Line(E,K))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["B", "L"], ["E", "K"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1606（train）

题面：<image>Find $NP$.

参考答案：`14`

原图：[打开](<../../data/project3_perception_prototype/images/1606.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(L, M)), 10)
Equals(LengthOf(Line(N, M)), 10)
Equals(LengthOf(Line(P, L)), 2x-4)
Equals(LengthOf(Line(P, N)), x+5)
PointLiesOnLine(M, Line(N, L))
PointLiesOnLine(P, Line(M, A))
Perpendicular(Line(N, M), Line(P, M))
```

原始 text logic forms：

```text
Find(LengthOf(Line(N,P)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(L, M)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["L", "M"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(N, M)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["M", "N"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(P, L)), 2x-4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(P, N)), x+5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(N, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(M, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(N, M), Line(P, M))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["M", "N"], ["M", "P"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 809（train）

题面：<image>Find $HJ$.

参考答案：`15`

原图：[打开](<../../data/project3_perception_prototype/images/809.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(P, N)), 8)
Equals(LengthOf(Line(N, Q)), 12)
Equals(LengthOf(Line(P, Q)), 20)
Equals(LengthOf(Line(J, H)), 4x+7)
Equals(LengthOf(Line(J, K)), 25)
Equals(LengthOf(Line(K, H)), 6x-2)
Equals(MeasureOf(Angle(H, J, K)), MeasureOf(Angle(P, Q, N)))
Equals(MeasureOf(Angle(J, H, K)), MeasureOf(Angle(P, N, Q)))

```

原始 text logic forms：

```text
Find(LengthOf(Line(H,J)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(P, N)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["N", "P"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(N, Q)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["N", "Q"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(P, Q)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "Q"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(J, H)), 4x+7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(J, K)), 25)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["J", "K"], "value": "25", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(K, H)), 6x-2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(H, J, K)), MeasureOf(Angle(P, Q, N)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(J, H, K)), MeasureOf(Angle(P, N, Q)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1820（train）

题面：<image>Find ST

参考答案：`\frac { 50 } { 3 }`

原图：[打开](<../../data/project3_perception_prototype/images/1820.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(P, Q)), 25)
Equals(LengthOf(Line(R, T)), x)
Equals(LengthOf(Line(R, S)), 10)
Equals(LengthOf(Line(S, Q)), 5)
PointLiesOnLine(T, Line(P, R))
PointLiesOnLine(S, Line(Q, R))
Perpendicular(Line(R, T), Line(R, S))
Parallel(Line(P, Q), Line(T, S))
```

原始 text logic forms：

```text
Find(LengthOf(Line(S,T)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(P, Q)), 25)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "Q"], "value": "25", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, T)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(R, S)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["R", "S"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(S, Q)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["Q", "S"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(T, Line(P, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(Q, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(R, T), Line(R, S))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["R", "S"], ["R", "T"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(P, Q), Line(T, S))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["P", "Q"], ["S", "T"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1584（train）

题面：<image>Find $y$ in the figure.

参考答案：`45`

原图：[打开](<../../data/project3_perception_prototype/images/1584.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(H, N, K)), 4x)
Equals(MeasureOf(Angle(N, M, O)), 56)
Equals(MeasureOf(Angle(T, L, G)), 3y-11)
PointLiesOnLine(J, Line(A, C))
PointLiesOnLine(U, Line(A, C))
PointLiesOnLine(U, Line(A, L))
PointLiesOnLine(L, Line(A, Q))
PointLiesOnLine(U, Line(A, Q))
PointLiesOnLine(A, Line(C, T))
PointLiesOnLine(J, Line(C, T))
PointLiesOnLine(U, Line(C, T))
PointLiesOnLine(L, Line(C, U))
PointLiesOnLine(L, Line(J, Q))
PointLiesOnLine(A, Line(J, T))
PointLiesOnLine(M, Line(L, H))
PointLiesOnLine(N, Line(L, H))
PointLiesOnLine(M, Line(L, N))
PointLiesOnLine(A, Line(L, T))
PointLiesOnLine(U, Line(L, T))
PointLiesOnLine(A, Line(Q, T))
PointLiesOnLine(L, Line(Q, T))
PointLiesOnLine(U, Line(Q, T))
PointLiesOnLine(L, Line(Q, U))
PointLiesOnLine(A, Line(T, U))
PointLiesOnLine(N, Line(F, K))
PointLiesOnLine(R, Line(F, K))
PointLiesOnLine(R, Line(F, N))
PointLiesOnLine(R, Line(F, S))
PointLiesOnLine(N, Line(K, R))
PointLiesOnLine(S, Line(K, R))
PointLiesOnLine(N, Line(K, S))
PointLiesOnLine(L, Line(N, G))
PointLiesOnLine(M, Line(N, G))
PointLiesOnLine(S, Line(N, R))
PointLiesOnLine(I, Line(D, E))
PointLiesOnLine(M, Line(D, E))
PointLiesOnLine(I, Line(D, M))
PointLiesOnLine(I, Line(D, P))
PointLiesOnLine(M, Line(D, P))
PointLiesOnLine(D, Line(E, O))
PointLiesOnLine(I, Line(E, O))
PointLiesOnLine(M, Line(E, O))
PointLiesOnLine(D, Line(I, O))
PointLiesOnLine(M, Line(I, P))
PointLiesOnLine(L, Line(M, G))
PointLiesOnLine(N, Line(M, H))
PointLiesOnLine(D, Line(M, O))
PointLiesOnLine(D, Line(O, P))
PointLiesOnLine(M, Line(O, P))
PointLiesOnLine(L, Line(G, H))
PointLiesOnLine(M, Line(G, H))
PointLiesOnLine(N, Line(G, H))
Parallel(Line(F, K), Line(O, P))
Parallel(Line(F, K), Line(T, Q))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(H, N, K)), 4x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(N, M, O)), 56)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["N", "M", "O"], "value": "56", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(T, L, G)), 3y-11)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(A, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(A, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(A, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(C, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(C, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(C, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(C, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(J, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(J, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(L, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(L, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(L, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(L, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(L, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(Q, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(Q, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(Q, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(Q, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(T, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(F, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(F, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(F, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(F, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(K, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(K, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(K, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(N, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(N, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(N, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(D, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(D, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(D, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(D, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(D, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(E, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(E, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(E, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(I, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(I, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(M, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(M, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(M, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(O, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(O, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(F, K), Line(O, P))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["F", "K"], ["O", "P"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(F, K), Line(T, Q))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["F", "K"], ["Q", "T"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 754（train）

题面：<image>Find the measure of the altitude drawn to the hypotenuse

参考答案：`12`

原图：[打开](<../../data/project3_perception_prototype/images/754.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(F, H)), 12)
Equals(LengthOf(Line(G, H)), 12)
PointLiesOnLine(H, Line(F, G))
Perpendicular(Line(E, H), Line(G, H))
Perpendicular(Line(F, E), Line(E, G))
```

原始 text logic forms：

```text
IsHypotenuseOf(Line($1,$3), Triangle($1,$2,$3))
Find(LengthOf(AltitudeOf(Triangle($1,$2,$3))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(F, H)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["F", "H"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(G, H)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["G", "H"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(H, Line(F, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(E, H), Line(G, H))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["E", "H"], ["G", "H"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(F, E), Line(E, G))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["E", "F"], ["E", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1725（train）

题面：<image>$\overline{JH}$ is a midsegment of $\triangle KLM$. Find $x$.

参考答案：`11`

原图：[打开](<../../data/project3_perception_prototype/images/1725.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(J, H)), x)
Equals(LengthOf(Line(K, M)), 22)
PointLiesOnLine(J, Line(L, K))
PointLiesOnLine(C, Line(L, K))
PointLiesOnLine(H, Line(L, M))
PointLiesOnLine(J, Line(L, C))
PointLiesOnLine(B, Line(K, M))
PointLiesOnLine(C, Line(K, J))
```

原始 text logic forms：

```text
IsMidsegmentOf(Line(J,H),Triangle(K,L,M))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(J, H)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(K, M)), 22)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["K", "M"], "value": "22", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(J, Line(L, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(L, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(L, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(L, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(K, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(K, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 93（train）

题面：<image>Find x

参考答案：`45`

原图：[打开](<../../data/project3_perception_prototype/images/93.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, C)), y)
Equals(LengthOf(Line(C, D)), 12)
Equals(MeasureOf(Angle(C, B, D)), x)
Equals(LengthOf(Line(B, D)), 12)
Perpendicular(Line(C, D), Line(B, D))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, C)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(C, D)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, B, D)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, D)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(C, D), Line(B, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "D"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1509（train）

题面：<image>In the figure, $\overline{FJ} \cong \overline{FH}$ and $\overline{GF} \cong \overline{GH}$. If $m∠GHJ=152$ and  $m∠G=32$, find $m∠JFH$.

参考答案：`24`

原图：[打开](<../../data/project3_perception_prototype/images/1509.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(F, J)), LengthOf(Line(F, H)))
Equals(LengthOf(Line(G, F)), LengthOf(Line(G, H)))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(F,J)),Line(F,H))
Equals(LengthOf(Line(G,F)),Line(G,H))
Equals(MeasureOf(Angle(G,H,J)),152)
Equals(MeasureOf(Angle(G)),32)
Find(MeasureOf(Angle(J,F,H)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(F, J)), LengthOf(Line(F, H)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(G, F)), LengthOf(Line(G, H)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1916（train）

题面：<image>Find $BC$.

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/1916.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, D)), 10)
Equals(LengthOf(Line(C, B)), 2x+4)
Equals(LengthOf(Line(D, B)), x+2)
Equals(LengthOf(Line(B, C)), LengthOf(Line(C, D)))
```

原始 text logic forms：

```text
Find(LengthOf(Line(B,C)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, D)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, B)), 2x+4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(D, B)), x+2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), LengthOf(Line(C, D)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 943（train）

题面：<image>Find $XA$.

参考答案：`4`

原图：[打开](<../../data/project3_perception_prototype/images/943.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, Z)), 4)
PointLiesOnLine(X, Line(Y, B))
PointLiesOnLine(Z, Line(Y, C))
PointLiesOnLine(B, Line(Y, D))
PointLiesOnLine(X, Line(Y, D))
PointLiesOnLine(E, Line(Y, D))
PointLiesOnLine(B, Line(Y, E))
PointLiesOnLine(X, Line(Y, E))
PointLiesOnLine(A, Line(Y, F))
PointLiesOnLine(B, Line(X, D))
PointLiesOnLine(E, Line(X, D))
PointLiesOnLine(B, Line(X, E))
PointLiesOnLine(E, Line(B, D))
Perpendicular(Line(Y, X), Line(A, X))
Perpendicular(Line(A, Z), Line(Y, Z))
Equals(MeasureOf(Angle(X, Y, A)), MeasureOf(Angle(A, Y, Z)))
```

原始 text logic forms：

```text
Find(LengthOf(Line(X,A)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, Z)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "Z"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(X, Line(Y, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(Y, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(Y, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(X, Line(Y, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(Y, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(Y, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(X, Line(Y, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(Y, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(X, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(X, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(X, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(Y, X), Line(A, X))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "X"], ["X", "Y"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(A, Z), Line(Y, Z))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "Z"], ["Y", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(X, Y, A)), MeasureOf(Angle(A, Y, Z)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 341（train）

题面：<image>Each pair of polygons is similar. Find x

参考答案：`71.05`

原图：[打开](<../../data/project3_perception_prototype/images/341.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(R, T)), y+3)
Equals(LengthOf(Line(T, S)), 49)
Equals(LengthOf(Line(R, S)), x)
Equals(LengthOf(Line(W, V)), 20)
Equals(LengthOf(Line(U, V)), 21)
Equals(LengthOf(Line(W, U)), 29)
Equals(MeasureOf(Angle(R, T, S)), MeasureOf(Angle(W, V, U)))
Equals(MeasureOf(Angle(T, S, R)), MeasureOf(Angle(V, W, U)))
Equals(MeasureOf(Angle(S, R, T)), MeasureOf(Angle(V, U, W)))
```

原始 text logic forms：

```text
Similar(Polygon($1),Polygon($2))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(R, T)), y+3)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(T, S)), 49)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["S", "T"], "value": "49", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, S)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(W, V)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["V", "W"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(U, V)), 21)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["U", "V"], "value": "21", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(W, U)), 29)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["U", "W"], "value": "29", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(R, T, S)), MeasureOf(Angle(W, V, U)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(T, S, R)), MeasureOf(Angle(V, W, U)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(S, R, T)), MeasureOf(Angle(V, U, W)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1960（train）

题面：<image>Find $m \widehat {PM}$.

参考答案：`144`

原图：[打开](<../../data/project3_perception_prototype/images/1960.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(P, M, Q)), 72)
PointLiesOnCircle(P, Circle(C, radius_3_0))
PointLiesOnCircle(M, Circle(C, radius_3_0))
PointLiesOnCircle(R, Circle(C, radius_3_0))
```

原始 text logic forms：

```text
Find(MeasureOf(Arc(P,M)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(P, M, Q)), 72)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["P", "M", "Q"], "value": "72", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(P, Circle(C, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(M, Circle(C, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(R, Circle(C, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 902（train）

题面：<image>Find the measure of $\angle 1$ if $m∠4= m∠5$.

参考答案：`64`

原图：[打开](<../../data/project3_perception_prototype/images/902.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(F, D, A)), MeasureOf(angle 7))
Equals(MeasureOf(Angle(A, E, C)), 63)
Equals(MeasureOf(Angle(E, A, D)), 69)
Equals(MeasureOf(Angle(E, C, A)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(C, A, E)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(D, A, B)), 47)
Equals(MeasureOf(Angle(A, F, D)), MeasureOf(angle 6))
Equals(MeasureOf(Angle(D, F, B)), 136)
Equals(MeasureOf(Angle(F, C, G)), MeasureOf(angle 5))
Equals(MeasureOf(Angle(G, A, C)), MeasureOf(angle 3))
Equals(MeasureOf(Angle(C, G, A)), MeasureOf(angle 4))
PointLiesOnLine(F, Line(A, B))
PointLiesOnLine(A, Line(B, C))
PointLiesOnLine(F, Line(B, C))
PointLiesOnLine(A, Line(C, F))
PointLiesOnLine(A, Line(E, G))
```

原始 text logic forms：

```text
Equals(MeasureOf(Angle(4)),MeasureOf(Angle(5)))
Find(MeasureOf(Angle(1)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(F, D, A)), MeasureOf(angle 7))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, E, C)), 63)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "E", "C"], "value": "63", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(E, A, D)), 69)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["D", "A", "E"], "value": "69", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(E, C, A)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, A, E)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, A, B)), 47)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "A", "D"], "value": "47", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, F, D)), MeasureOf(angle 6))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, F, B)), 136)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "F", "D"], "value": "136", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(F, C, G)), MeasureOf(angle 5))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(G, A, C)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, G, A)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(C, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1576（train）

题面：<image>In the figure, $ \overline{JM} \cong \overline{PM}$ and $ \overline{ML} \cong \overline{PL}$. If $m \angle PLJ=58$, find $m \angle PJL$.

参考答案：`30.5`

原图：[打开](<../../data/project3_perception_prototype/images/1576.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(M, Line(L, J))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(J,M)),Line(P,M))
Equals(LengthOf(Line(M,L)),Line(P,L))
Equals(MeasureOf(Angle(P,L,J)),58)
Find(MeasureOf(Angle(P,J,L)))
```

有限 schema 结果：

- `PointLiesOnLine(M, Line(L, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1493（train）

题面：<image>Find x. Round to the nearest tenth, if necessary.

参考答案：`15`

原图：[打开](<../../data/project3_perception_prototype/images/1493.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, B)), 12)
Equals(LengthOf(Line(C, F)), 6)
Equals(LengthOf(Line(B, D)), x)
Equals(LengthOf(Line(E, F)), y)
Equals(LengthOf(Line(A, E)), 3)
Equals(LengthOf(Line(E, H)), 2)
PointLiesOnLine(E, Line(A, C))
PointLiesOnLine(F, Line(A, C))
PointLiesOnLine(E, Line(A, F))
PointLiesOnLine(F, Line(C, E))
PointLiesOnLine(E, Line(H, B))
PointLiesOnLine(E, Line(H, D))
PointLiesOnCircle(A, Circle(D, radius_3_0))
PointLiesOnCircle(B, Circle(D, radius_3_0))
PointLiesOnCircle(F, Circle(D, radius_3_0))
PointLiesOnCircle(H, Circle(D, radius_3_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, B)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, F)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "F"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, D)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(E, F)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, E)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "E"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(E, H)), 2)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["E", "H"], "value": "2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(C, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(H, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(H, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(H, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1263（train）

题面：<image>Find $C D$ if $A E=8, E D=4,$ and $B E=6$

参考答案：`9`

原图：[打开](<../../data/project3_perception_prototype/images/1263.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(B, Line(A, C))
PointLiesOnLine(E, Line(A, D))
Parallel(Line(D, C), Line(E, B))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(A,E)),8)
Equals(LengthOf(Line(E,D)),4)
Equals(LengthOf(Line(B,E)),6)
Find(LengthOf(Line(C,D)))
```

有限 schema 结果：

- `PointLiesOnLine(B, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(D, C), Line(E, B))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["B", "E"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1838（train）

题面：<image>Find AC

参考答案：`9.6`

原图：[打开](<../../data/project3_perception_prototype/images/1838.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, A)), x+2)
Equals(LengthOf(Line(D, A)), 8)
Equals(LengthOf(Line(D, E)), 5)
Equals(LengthOf(Line(C, B)), 6)
PointLiesOnLine(E, Line(D, A))
PointLiesOnLine(B, Line(C, A))
Parallel(Line(E, B), Line(D, C))
```

原始 text logic forms：

```text
Find(LengthOf(Line(A,C)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, A)), x+2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(D, A)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, E)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["D", "E"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, B)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(D, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(C, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(E, B), Line(D, C))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["B", "E"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1136（train）

题面：<image>Find $m \angle TQR$.

参考答案：`43`

原图：[打开](<../../data/project3_perception_prototype/images/1136.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(Q, S)), 8)
Equals(MeasureOf(Angle(R, Q, S)), 43)
Equals(LengthOf(Line(T, Q)), 8)
PointLiesOnLine(S, Line(R, B))
PointLiesOnLine(T, Line(R, C))
PointLiesOnLine(Q, Line(R, D))
Perpendicular(Line(Q, S), Line(R, S))
Perpendicular(Line(T, Q), Line(T, R))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(T,Q,R)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(Q, S)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["Q", "S"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(R, Q, S)), 43)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["R", "Q", "S"], "value": "43", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(T, Q)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["Q", "T"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(S, Line(R, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(R, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(R, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(Q, S), Line(R, S))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["Q", "S"], ["R", "S"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(T, Q), Line(T, R))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["Q", "T"], ["R", "T"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 680（train）

题面：<image>Find the measure of the altitude drawn to the hypotenuse.

参考答案：`3 \sqrt { 5 }`

原图：[打开](<../../data/project3_perception_prototype/images/680.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(X, A)), 5)
Equals(LengthOf(Line(Y, A)), 9)
PointLiesOnLine(A, Line(Y, X))
Perpendicular(Line(X, A), Line(Z, A))
Perpendicular(Line(Z, A), Line(Z, Y))
```

原始 text logic forms：

```text
Equals(Line(A, Z),HypotenuseOf(Triangle(X, Z, Y)))
Find(LengthOf(AltitudeOf(Triangle(X, Z, Y))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(X, A)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "X"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(Y, A)), 9)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "Y"], "value": "9", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(A, Line(Y, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(X, A), Line(Z, A))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "X"], ["A", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(Z, A), Line(Z, Y))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "Z"], ["Y", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1331（train）

题面：<image>Find x

参考答案：`35`

原图：[打开](<../../data/project3_perception_prototype/images/1331.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Arc(I, G)), 100)
Equals(MeasureOf(Arc(G, B)), x)
Equals(MeasureOf(Arc(I, J)), 120)
Equals(MeasureOf(Arc(B, J)), 90)
PointLiesOnLine(G, Line(A, D))
PointLiesOnLine(B, Line(D, C))
PointLiesOnLine(J, Line(D, C))
PointLiesOnLine(B, Line(D, F))
PointLiesOnLine(C, Line(D, F))
PointLiesOnLine(J, Line(D, F))
PointLiesOnLine(G, Line(D, H))
PointLiesOnLine(I, Line(D, H))
PointLiesOnLine(G, Line(D, I))
PointLiesOnLine(B, Line(D, J))
PointLiesOnLine(I, Line(G, H))
PointLiesOnLine(J, Line(B, C))
PointLiesOnLine(C, Line(B, F))
PointLiesOnLine(J, Line(B, F))
PointLiesOnLine(C, Line(F, J))
PointLiesOnCircle(B, Circle(E, radius_4_0))
PointLiesOnCircle(G, Circle(E, radius_4_0))
PointLiesOnCircle(I, Circle(E, radius_4_0))
PointLiesOnCircle(J, Circle(E, radius_4_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Arc(I, G)), 100)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Arc(G, B)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Arc(I, J)), 120)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Arc(B, J)), 90)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(D, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(D, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(D, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(D, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(D, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(B, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(F, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(G, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(I, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(J, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1163（train）

题面：<image>A square with 5-centimeter sides is inscribed in a circle. What is the circumference of the circle? Round your answer to the nearest

tenth of a centimeter.

参考答案：`22.2`

原图：[打开](<../../data/project3_perception_prototype/images/1163.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(D, B)), 5)
PointLiesOnCircle(A, Circle(E, radius_4_0))
PointLiesOnCircle(B, Circle(E, radius_4_0))
PointLiesOnCircle(C, Circle(E, radius_4_0))
PointLiesOnCircle(D, Circle(E, radius_4_0))
```

原始 text logic forms：

```text
Equals(SideOf(Square($)),5)
InscribedIn(Square($),Circle($))
Find(CircumferenceOf(Circle($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(D, B)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(A, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 331（train）

题面：<image>Express the ratio of $\cos M$ as a decimal to the nearest hundredth.

参考答案：`0.92`

原图：[打开](<../../data/project3_perception_prototype/images/331.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(M, P)), 36)
Equals(LengthOf(Line(N, P)), 15)
Equals(LengthOf(Line(M, N)), 39)
Perpendicular(Line(M, P), Line(N, P))
```

原始 text logic forms：

```text
Find(RatioOf(CosOf(Angle(M))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(M, P)), 36)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["M", "P"], "value": "36", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(N, P)), 15)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["N", "P"], "value": "15", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(M, N)), 39)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["M", "N"], "value": "39", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(M, P), Line(N, P))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["M", "P"], ["N", "P"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1428（train）

题面：<image>If $\overline{PR} \| \overline{KL}, KN=9, LN=16,$ and $PM=2KP$, find $MN$.

参考答案：`12`

原图：[打开](<../../data/project3_perception_prototype/images/1428.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(E, F)), 3y)
Equals(LengthOf(Line(E, B)), 3y-6)
Equals(LengthOf(Line(B, F)), 2y+4)
Equals(LengthOf(Line(F, G)), \frac{1}{2}x+12)
Equals(LengthOf(Line(D, G)), \frac{3}{2}x+8)
PointLiesOnLine(G, Line(D, F))
PointLiesOnLine(B, Line(E, F))

```

原始 text logic forms：

```text
Parallel(Line(P,R),Line(K,L))
Equals(LengthOf(Line(K,N)),9)
Equals(LengthOf(Line(L,N)),16)
Equals(LengthOf(Line(P,M)),Mul(Line(K,P),2))
Find(LengthOf(Line(M,N)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(E, F)), 3y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(E, B)), 3y-6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, F)), 2y+4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(F, G)), \frac{1}{2}x+12)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(D, G)), \frac{3}{2}x+8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(E, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1366（train）

题面：<image>Find $m \angle K$.

参考答案：`117`

原图：[打开](<../../data/project3_perception_prototype/images/1366.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(K, J, M)), 59)
Equals(MeasureOf(Angle(M, L, K)), 67)
Equals(LengthOf(Line(J, M)), LengthOf(Line(J, K)))
Equals(LengthOf(Line(M, L)), LengthOf(Line(L, K)))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(K)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(K, J, M)), 59)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["K", "J", "M"], "value": "59", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(M, L, K)), 67)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["K", "L", "M"], "value": "67", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(J, M)), LengthOf(Line(J, K)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(M, L)), LengthOf(Line(L, K)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 568（train）

题面：<image>$\overline{JH}, \overline{JP},$ and $\overline{PH}$ are midsegments of $\triangle KLM$. Find $x$.

参考答案：`60`

原图：[打开](<../../data/project3_perception_prototype/images/568.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(L, J, H)), x)
Equals(MeasureOf(Angle(M, H, P)), 44)
Equals(MeasureOf(Angle(J, H, L)), 76)
PointLiesOnLine(J, Line(K, L))
PointLiesOnLine(P, Line(K, M))
PointLiesOnLine(H, Line(M, L))
```

原始 text logic forms：

```text
IsMidsegmentOf(Line(J,H),Triangle(K,L,M))
IsMidsegmentOf(Line(J,P),Triangle(K,L,M))
IsMidsegmentOf(Line(P,H),Triangle(K,L,M))
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(L, J, H)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(M, H, P)), 44)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["M", "H", "P"], "value": "44", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(J, H, L)), 76)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["J", "H", "L"], "value": "76", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(J, Line(K, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(K, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(M, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 761（train）

题面：<image>Find x.

参考答案：`5 \sqrt { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/761.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), x)
Equals(LengthOf(Line(A, B)), 5)
Equals(LengthOf(Line(B, C)), 5)
Perpendicular(Line(B, C), Line(A, B))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, B)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, C), Line(A, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 836（train）

题面：<image>Find x.

参考答案：`6`

原图：[打开](<../../data/project3_perception_prototype/images/836.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(X, B)), 12)
Equals(LengthOf(Line(X, C)), 13)
PointLiesOnLine(B, Line(C, D))
Perpendicular(Line(X, B), Line(B, C))
Equals(LengthOf(Line(Y, E)), x)
Equals(LengthOf(Line(Y, F)), 6.5)
PointLiesOnLine(E, Line(F, G))
Perpendicular(Line(Y, E), Line(E, F))
Equals(MeasureOf(Angle(B, C, X)), MeasureOf(Angle(E, F, Y)))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(X, B)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "X"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(X, C)), 13)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "X"], "value": "13", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(B, Line(C, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(X, B), Line(B, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "C"], ["B", "X"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(Y, E)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(Y, F)), 6.5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["F", "Y"], "value": "13/2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(F, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(Y, E), Line(E, F))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["E", "F"], ["E", "Y"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(B, C, X)), MeasureOf(Angle(E, F, Y)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1053（train）

题面：<image>In $\odot P, m \widehat{E N}=66$ and $m \angle G P M=89$ . 

Find $m \angle G M E$

参考答案：`57`

原图：[打开](<../../data/project3_perception_prototype/images/1053.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(B, Line(M, E))
PointLiesOnLine(B, Line(N, P))
PointLiesOnLine(P, Line(N, G))
PointLiesOnLine(B, Line(N, G))
PointLiesOnLine(P, Line(G, B))
PointLiesOnCircle(M, Circle(P, radius_4_0))
PointLiesOnCircle(E, Circle(P, radius_4_0))
PointLiesOnCircle(N, Circle(P, radius_4_0))
PointLiesOnCircle(G, Circle(P, radius_4_0))
```

原始 text logic forms：

```text
Circle(P)
Equals(MeasureOf(Arc(E,N)),66)
Equals(MeasureOf(Angle(G,P,M)),89)
Find(MeasureOf(Angle(G,M,E)))
```

有限 schema 结果：

- `PointLiesOnLine(B, Line(M, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(N, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(N, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(N, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(G, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(M, Circle(P, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(P, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(N, Circle(P, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(G, Circle(P, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 888（train）

题面：<image>In $\odot S$, find $PR$.

参考答案：`12`

原图：[打开](<../../data/project3_perception_prototype/images/888.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(R, T)), 6)
PointLiesOnLine(T, Line(R, P))
PointLiesOnLine(T, Line(Q, S))
PointLiesOnCircle(R, Circle(S, radius_2_0))
PointLiesOnCircle(Q, Circle(S, radius_2_0))
PointLiesOnCircle(P, Circle(S, radius_2_0))
Perpendicular(Line(T, Q), Line(T, P))
```

原始 text logic forms：

```text
Circle(S)
Find(LengthOf(Line(P,R)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(R, T)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["R", "T"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(T, Line(R, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(Q, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(R, Circle(S, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(Q, Circle(S, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(P, Circle(S, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(T, Q), Line(T, P))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["P", "T"], ["Q", "T"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2009（train）

题面：<image>Find $YZ$.

参考答案：`4`

原图：[打开](<../../data/project3_perception_prototype/images/2009.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(Y, X)), 4)
Equals(LengthOf(Line(Z, X)), 4)
Equals(MeasureOf(Angle(X, Y, Z)), 60)
Equals(MeasureOf(Angle(Y, Z, X)), 60)
```

原始 text logic forms：

```text
Find(LengthOf(Line(Y,Z)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(Y, X)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["X", "Y"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(Z, X)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["X", "Z"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(X, Y, Z)), 60)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["X", "Y", "Z"], "value": "60", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(Y, Z, X)), 60)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["X", "Z", "Y"], "value": "60", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 884（train）

题面：<image>Find the area of the parallelogram. Round to the nearest tenth if necessary.

参考答案：`57.9`

原图：[打开](<../../data/project3_perception_prototype/images/884.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(N, B, E)), 45)
Equals(LengthOf(Line(A, N)), 12.8)
Equals(LengthOf(Line(B, N)), 6.4)
PointLiesOnLine(E, Line(A, N))
Perpendicular(Line(B, E), Line(E, A))
```

原始 text logic forms：

```text
Find(AreaOf(Parallelogram($)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(N, B, E)), 45)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["E", "B", "N"], "value": "45", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, N)), 12.8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "N"], "value": "64/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, N)), 6.4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "N"], "value": "32/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(A, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(B, E), Line(E, A))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "E"], ["B", "E"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 459（train）

题面：<image>Find the perimeter of the triangle. Round to the nearest tenth if necessary.

参考答案：`13.2`

原图：[打开](<../../data/project3_perception_prototype/images/459.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), 3.6)
Equals(LengthOf(Line(D, C)), 2)
Equals(LengthOf(Line(A, B)), 6)
PointLiesOnLine(D, Line(A, B))
Perpendicular(Line(C, D), Line(B, D))
```

原始 text logic forms：

```text
Find(PerimeterOf(Triangle($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), 3.6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "18/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, C)), 2)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(D, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(C, D), Line(B, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "D"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1007（train）

题面：<image>In the figure, $m ∠ 12 = 64$. Find the measure of $ \angle 8$.

参考答案：`116`

原图：[打开](<../../data/project3_perception_prototype/images/1007.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(I, D, W)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(W, D, L)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(D, U, A)), MeasureOf(angle 3))
Equals(MeasureOf(Angle(A, U, L)), MeasureOf(angle 4))
Equals(MeasureOf(Angle(H, D, I)), MeasureOf(angle 5))
Equals(MeasureOf(Angle(L, D, H)), MeasureOf(angle 6))
Equals(MeasureOf(Angle(E, U, D)), MeasureOf(angle 7))
Equals(MeasureOf(Angle(L, U, E)), MeasureOf(angle 8))
Equals(MeasureOf(Angle(B, H, D)), MeasureOf(angle 9))
Equals(MeasureOf(Angle(W, H, E)), MeasureOf(angle 10))
Equals(MeasureOf(Angle(B, E, U)), MeasureOf(angle 11))
Equals(MeasureOf(Angle(A, E, N)), MeasureOf(angle 12))
Equals(MeasureOf(Angle(J, H, B)), MeasureOf(angle 13))
Equals(MeasureOf(Angle(E, H, J)), MeasureOf(angle 14))
Equals(MeasureOf(Angle(K, E, B)), MeasureOf(angle 15))
Equals(MeasureOf(Angle(N, E, K)), MeasureOf(angle 16))
PointLiesOnLine(G, Line(A, E))
PointLiesOnLine(U, Line(A, E))
PointLiesOnLine(E, Line(A, K))
PointLiesOnLine(G, Line(A, K))
PointLiesOnLine(U, Line(A, K))
PointLiesOnLine(G, Line(A, U))
PointLiesOnLine(H, Line(E, B))
PointLiesOnLine(U, Line(E, G))
PointLiesOnLine(E, Line(G, K))
PointLiesOnLine(U, Line(G, K))
PointLiesOnLine(E, Line(K, U))
PointLiesOnLine(D, Line(U, I))
PointLiesOnLine(E, Line(B, N))
PointLiesOnLine(H, Line(B, N))
PointLiesOnLine(D, Line(H, W))
PointLiesOnLine(E, Line(H, N))
PointLiesOnLine(H, Line(D, J))
PointLiesOnLine(U, Line(D, L))
PointLiesOnLine(D, Line(I, L))
PointLiesOnLine(U, Line(I, L))
PointLiesOnLine(D, Line(W, J))
PointLiesOnLine(H, Line(W, J))
Parallel(Line(W,J), Line(A,K))
Parallel(Line(I, L), Line(B,N))
```

原始 text logic forms：

```text
Equals(MeasureOf(Angle(12)),64)
Find(MeasureOf(Angle(8)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(I, D, W)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(W, D, L)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, U, A)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, U, L)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(H, D, I)), MeasureOf(angle 5))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(L, D, H)), MeasureOf(angle 6))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, U, D)), MeasureOf(angle 7))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(L, U, E)), MeasureOf(angle 8))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, H, D)), MeasureOf(angle 9))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(W, H, E)), MeasureOf(angle 10))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, E, U)), MeasureOf(angle 11))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, E, N)), MeasureOf(angle 12))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(J, H, B)), MeasureOf(angle 13))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, H, J)), MeasureOf(angle 14))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(K, E, B)), MeasureOf(angle 15))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(N, E, K)), MeasureOf(angle 16))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(A, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(A, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(E, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(G, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(G, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(K, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(U, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(B, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(B, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(H, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(H, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(D, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(I, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(I, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(W, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(W, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(W,J), Line(A,K))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["A", "K"], ["J", "W"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(I, L), Line(B,N))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["B", "N"], ["I", "L"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1904（train）

题面：<image>$H$ is the incenter of $\triangle ABC$. Find $BD$.

参考答案：`7 \sqrt 3`

原图：[打开](<../../data/project3_perception_prototype/images/1904.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, F)), 24)
Equals(LengthOf(Line(A, H)), 25)
Equals(MeasureOf(Angle(H, C, G)), 28)
Equals(LengthOf(Line(B, H)), 11)
Equals(MeasureOf(Angle(A, B, H)), 30)
PointLiesOnLine(F, Line(C, A))
PointLiesOnLine(G, Line(C, B))
PointLiesOnLine(D, Line(A, B))
Perpendicular(Line(A, F), Line(F, H))
Perpendicular(Line(H, D), Line(B, D))
Perpendicular(Line(H, G), Line(B, G))
```

原始 text logic forms：

```text
IsIncenterOf(Point(H),Triangle(A,B,C))
Find(LengthOf(Line(B,D)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, F)), 24)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "F"], "value": "24", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, H)), 25)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "H"], "value": "25", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(H, C, G)), 28)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["G", "C", "H"], "value": "28", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, H)), 11)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "H"], "value": "11", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, B, H)), 30)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "B", "H"], "value": "30", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(F, Line(C, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(C, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, F), Line(F, H))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "F"], ["F", "H"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(H, D), Line(B, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "D"], ["D", "H"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(H, G), Line(B, G))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "G"], ["G", "H"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1289（train）

题面：<image>Find x.

参考答案：`6`

原图：[打开](<../../data/project3_perception_prototype/images/1289.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), y)
Equals(LengthOf(Line(B, C)), z)
Equals(LengthOf(Line(B, D)), x)
Equals(LengthOf(Line(A, D)), 9)
Equals(LengthOf(Line(C, D)), 4)
PointLiesOnLine(D, Line(A, C))
Perpendicular(Line(A, B), Line(B, C))
Perpendicular(Line(B, D), Line(C, D))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, D)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, D)), 9)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "9", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, D)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(D, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, B), Line(B, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, D), Line(C, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "D"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 853（train）

题面：<image>Circle $L$ has a radius of 32 centimeters. $\overline{L H} \perp \overline{G J},$ and $G J=40$ centimeters. Find $L K$

参考答案：`\sqrt { 624 }`

原图：[打开](<../../data/project3_perception_prototype/images/853.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(K, Line(L, H))
PointLiesOnLine(K, Line(G, J))
PointLiesOnCircle(J, Circle(L, radius_3_0))
PointLiesOnCircle(G, Circle(L, radius_3_0))
PointLiesOnCircle(H, Circle(L, radius_3_0))
Perpendicular(Line(G, J), Line(K, L))
```

原始 text logic forms：

```text
Equals(RadiusOf(Circle(L)),32)
Perpendicular(Line(L,H),Line(G,J))
Equals(LengthOf(Line(G,J)),40)
Find(LengthOf(Line(L,K)))
```

有限 schema 结果：

- `PointLiesOnLine(K, Line(L, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(G, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(J, Circle(L, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(G, Circle(L, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(H, Circle(L, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(G, J), Line(K, L))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["G", "J"], ["K", "L"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1938（train）

题面：<image>Use parallelogram ABCD to find $m \angle FBC $

参考答案：`34`

原图：[打开](<../../data/project3_perception_prototype/images/1938.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, C)), 3y-4)
Equals(MeasureOf(Angle(D, C, A)), 54)
Equals(LengthOf(Line(B, A)), 5x)
Equals(MeasureOf(Angle(C, A, D)), 49)
Equals(LengthOf(Line(D, A)), 29)
Equals(LengthOf(Line(D, C)), 25)
Equals(MeasureOf(Angle(A, D, B)), 34)
PointLiesOnLine(F, Line(B, D))
PointLiesOnLine(F, Line(A, C))
```

原始 text logic forms：

```text
Parallelogram(A,B,C,D)
Find(MeasureOf(Angle(F,B,C)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, C)), 3y-4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, C, A)), 54)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "C", "D"], "value": "54", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, A)), 5x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, A, D)), 49)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "A", "D"], "value": "49", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, A)), 29)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "29", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, C)), 25)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "25", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, D, B)), 34)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "D", "B"], "value": "34", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(F, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1926（train）

题面：<image>Find AB

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/1926.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(E, B)), 5)
Equals(LengthOf(Line(B, C)), 2x-8)
Equals(LengthOf(Line(D, B)), 3)
Equals(LengthOf(Line(A, B)), x+3)
PointLiesOnLine(B, Line(E, D))
PointLiesOnLine(B, Line(A, C))
Parallel(Line(E, A), Line(D, C))
```

原始 text logic forms：

```text
Find(LengthOf(Line(A,B)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(E, B)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "E"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), 2x-8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(D, B)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), x+3)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(E, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(E, A), Line(D, C))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["A", "E"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 742（train）

题面：<image>For the pair of similar figures, use the given areas to find the scale factor from the blue to the green figure.

参考答案：`\frac { 3 } { 4 }`

原图：[打开](<../../data/project3_perception_prototype/images/742.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), x)
Equals(LengthOf(Line(F, K)), 15)
Equals(AreaOf(Pentagon(A, D, B, O, C)), 272)
Equals(AreaOf(Pentagon(F, G, H, J, K)), 153)

```

原始 text logic forms：

```text
Similar(Shape($1),Shape($2))
Find(ScaleFactorOf(Blue(Shape($)),Green(Shape($))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(F, K)), 15)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["F", "K"], "value": "15", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(AreaOf(Pentagon(A, D, B, O, C)), 272)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(AreaOf(Pentagon(F, G, H, J, K)), 153)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 863（train）

题面：<image>What is the length of $R T ?$

参考答案：`5 \sqrt { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/863.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(T, B)), 5)
Equals(MeasureOf(Angle(A, T, B)), 135)
PointLiesOnLine(T, Line(A, R))
```

原始 text logic forms：

```text
Find(LengthOf(Line(R,T)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(T, B)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "T"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, T, B)), 135)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "T", "B"], "value": "135", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(T, Line(A, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 538（train）

题面：<image>Find the area of the parallelogram. Round to the nearest tenth if necessary.

参考答案：`259.8`

原图：[打开](<../../data/project3_perception_prototype/images/538.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(E, C, O)), 60)
Equals(LengthOf(Line(C, O)), 20)
Equals(LengthOf(Line(B, O)), 15)
PointLiesOnLine(E, Line(C, A))
Perpendicular(Line(O, E), Line(E, A))
```

原始 text logic forms：

```text
Find(AreaOf(Parallelogram($)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(E, C, O)), 60)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["E", "C", "O"], "value": "60", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, O)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "O"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, O)), 15)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "O"], "value": "15", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(C, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(O, E), Line(E, A))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "E"], ["E", "O"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 711（train）

题面：<image>Find $DB$.

参考答案：`9.2`

原图：[打开](<../../data/project3_perception_prototype/images/711.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, A)), 15)
Equals(MeasureOf(Angle(B, D, E)), 82)
Equals(LengthOf(Line(E, F)), 9.2)
PointLiesOnLine(F, Line(C, A))
PointLiesOnLine(E, Line(C, B))
PointLiesOnLine(D, Line(B, A))
```

原始 text logic forms：

```text
Find(LengthOf(Line(D,B)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, A)), 15)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "15", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(B, D, E)), 82)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "D", "E"], "value": "82", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(E, F)), 9.2)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["E", "F"], "value": "46/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(F, Line(C, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(C, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(B, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 14（train）

题面：<image>Find $x$.

参考答案：`48`

原图：[打开](<../../data/project3_perception_prototype/images/14.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(K, I, P)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(S, N, D)), MeasureOf(angle 1))
Equals(LengthOf(Line(N, S)), y-6)
Equals(LengthOf(Line(E, O)), x+5)
Equals(MeasureOf(Angle(I, J, E)), MeasureOf(angle 4))
Equals(MeasureOf(Angle(F, L, G)), MeasureOf(angle 3))
Equals(MeasureOf(Angle(H, B, P)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(F, D, A)), MeasureOf(angle 2))
Equals(LengthOf(Line(L, G)), 66--y)
Equals(LengthOf(Line(B, H)), x-7)
Equals(MeasureOf(Angle(Y, I, K)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(G, L, D)), MeasureOf(angle 3))
PointLiesOnLine(I, Line(B, C))
PointLiesOnLine(J, Line(B, C))
PointLiesOnLine(P, Line(B, C))
PointLiesOnLine(I, Line(B, J))
PointLiesOnLine(D, Line(B, A))
PointLiesOnLine(I, Line(B, P))
PointLiesOnLine(J, Line(B, P))
PointLiesOnLine(J, Line(C, I))
PointLiesOnLine(P, Line(C, I))
PointLiesOnLine(P, Line(C, J))
PointLiesOnLine(B, Line(C, Y))
PointLiesOnLine(I, Line(C, Y))
PointLiesOnLine(J, Line(C, Y))
PointLiesOnLine(P, Line(C, Y))
PointLiesOnLine(L, Line(D, F))
PointLiesOnLine(N, Line(D, F))
PointLiesOnLine(B, Line(D, H))
PointLiesOnLine(L, Line(D, N))
PointLiesOnLine(B, Line(H, A))
PointLiesOnLine(D, Line(H, A))
PointLiesOnLine(L, Line(I, G))
PointLiesOnLine(B, Line(I, Y))
PointLiesOnLine(J, Line(I, P))
PointLiesOnLine(O, Line(J, E))
PointLiesOnLine(N, Line(J, S))
PointLiesOnLine(B, Line(J, Y))
PointLiesOnLine(I, Line(J, Y))
PointLiesOnLine(B, Line(Y, P))
PointLiesOnLine(I, Line(Y, P))
PointLiesOnLine(J, Line(Y, P))
PointLiesOnLine(N, Line(F, L))
PointLiesOnLine(D, Line(F, M))
PointLiesOnLine(L, Line(F, M))
PointLiesOnLine(N, Line(F, M))
PointLiesOnLine(I, Line(L, K))
PointLiesOnLine(D, Line(L, M))
PointLiesOnLine(D, Line(M, N))
PointLiesOnLine(L, Line(M, N))
PointLiesOnLine(J, Line(N, E))
PointLiesOnLine(O, Line(N, E))
PointLiesOnLine(J, Line(N, O))
PointLiesOnLine(J, Line(E, S))
PointLiesOnLine(N, Line(E, S))
PointLiesOnLine(O, Line(E, S))
PointLiesOnLine(J, Line(S, O))
PointLiesOnLine(N, Line(S, O))
PointLiesOnLine(I, Line(G, K))
PointLiesOnLine(L, Line(G, K))
Perpendicular(Line(J, P), Line(J, N))
Perpendicular(Line(I, J), Line(I, L))
Perpendicular(Line(B, I), Line(B, D))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(K, I, P)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(S, N, D)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(N, S)), y-6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(E, O)), x+5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(I, J, E)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, L, G)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(H, B, P)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, D, A)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(L, G)), 66--y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, H)), x-7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(Y, I, K)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(G, L, D)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(B, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(B, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(B, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(C, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(C, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(C, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(C, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(C, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(C, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(C, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(D, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(D, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(H, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(H, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(I, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(I, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(I, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(J, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(J, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(J, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(J, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(Y, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(Y, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(Y, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(F, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(F, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(F, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(F, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(L, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(L, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(M, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(M, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(N, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(N, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(N, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(E, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(E, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(E, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(S, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(S, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(G, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(L, Line(G, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(J, P), Line(J, N))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["J", "N"], ["J", "P"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(I, J), Line(I, L))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["I", "J"], ["I", "L"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, I), Line(B, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "D"], ["B", "I"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1495（train）

题面：<image>Find x

参考答案：`30`

原图：[打开](<../../data/project3_perception_prototype/images/1495.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(H, A, E)), 3x)
Equals(MeasureOf(Angle(F, A, D)), 2x)
PointLiesOnLine(A, Line(D, E))
Perpendicular(Line(A, H), Line(A, D))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(H, A, E)), 3x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, A, D)), 2x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(D, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, H), Line(A, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "D"], ["A", "H"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 209（train）

题面：<image>Find the area of the parallelogram.

参考答案：`318.7`

原图：[打开](<../../data/project3_perception_prototype/images/209.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), 16)
Equals(LengthOf(Line(C, D)), 23)
Equals(MeasureOf(Angle(B, D, E)), 60)
Perpendicular(Line(B, E), Line(D, E))
PointLiesOnLine(E, Line(C, D))
```

原始 text logic forms：

```text
Find(AreaOf(Parallelogram($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), 16)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "16", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, D)), 23)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "23", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(B, D, E)), 60)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "D", "E"], "value": "60", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, E), Line(D, E))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "E"], ["D", "E"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(C, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 955（train）

题面：<image>isosceles trapezoid TWYZ with $\angle Z \cong \angle Y, m \angle Z=30 x$, $\angle T \cong \angle W,$ and $m \angle T=20 x$, find Z

参考答案：`108`

原图：[打开](<../../data/project3_perception_prototype/images/955.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(Z, T, W)), MeasureOf(Angle(Y, W, T)))
Equals(MeasureOf(Angle(T, Z, Y)), MeasureOf(Angle(Z, Y, W)))
```

原始 text logic forms：

```text
Isosceles(Trapezoid(T,W,Y,Z))
Equals(Angle(Z),Angle(Y))
Equals(MeasureOf(Angle(Z)),30x)
Equals(Angle(T),Angle(W))
Equals(MeasureOf(Angle(T)),20x)
Find(Angle(Z))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(Z, T, W)), MeasureOf(Angle(Y, W, T)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(T, Z, Y)), MeasureOf(Angle(Z, Y, W)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1781（train）

题面：<image>Find x.

参考答案：`\frac { \sqrt { 10 } } { 5 }`

原图：[打开](<../../data/project3_perception_prototype/images/1781.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), \frac{3}{5})
Equals(LengthOf(Line(B, C)), \frac{1}{5})
Equals(LengthOf(Line(A, C)), x)
Perpendicular(Line(A, B), Line(B, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), \frac{3}{5})` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), \frac{1}{5})` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, B), Line(B, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 144（train）

题面：<image>Find $x$.

参考答案：`12`

原图：[打开](<../../data/project3_perception_prototype/images/144.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(R, T)), 2x+7)
Equals(LengthOf(Line(R, S)), 3x-5)
Equals(LengthOf(Line(S, T)), 22)
Equals(LengthOf(Line(R, T)), LengthOf(Line(R, S)))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(R, T)), 2x+7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(R, S)), 3x-5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(S, T)), 22)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["S", "T"], "value": "22", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, T)), LengthOf(Line(R, S)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 985（train）

题面：<image>Use parallelogram ABCD to find $m \angle BCF $

参考答案：`49`

原图：[打开](<../../data/project3_perception_prototype/images/985.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, C)), 3y-4)
Equals(MeasureOf(Angle(D, C, A)), 54)
Equals(LengthOf(Line(B, A)), 5x)
Equals(MeasureOf(Angle(C, A, D)), 49)
Equals(LengthOf(Line(D, A)), 29)
Equals(LengthOf(Line(D, C)), 25)
Equals(MeasureOf(Angle(A, D, B)), 34)
PointLiesOnLine(F, Line(B, D))
PointLiesOnLine(F, Line(A, C))
```

原始 text logic forms：

```text
Parallelogram(A,B,C,D)
Find(MeasureOf(Angle(B,C,F)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, C)), 3y-4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, C, A)), 54)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "C", "D"], "value": "54", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, A)), 5x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, A, D)), 49)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "A", "D"], "value": "49", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, A)), 29)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "29", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, C)), 25)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "25", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, D, B)), 34)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "D", "B"], "value": "34", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(F, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1596（train）

题面：<image>Find $m \angle A G E$

参考答案：`120`

原图：[打开](<../../data/project3_perception_prototype/images/1596.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(A, G, C)), 60)
PointLiesOnLine(G, Line(E, C))
PointLiesOnLine(G, Line(A, B))
PointLiesOnCircle(E, Circle(G, radius_0_0))
PointLiesOnCircle(C, Circle(G, radius_0_0))
PointLiesOnCircle(A, Circle(G, radius_0_0))
PointLiesOnCircle(D, Circle(G, radius_0_0))
PointLiesOnCircle(B, Circle(G, radius_0_0))
Perpendicular(Line(G, A), Line(G, D))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(A,G,E)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(A, G, C)), 60)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "G", "C"], "value": "60", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(G, Line(E, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(G, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(G, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(G, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(G, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(G, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(G, A), Line(G, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "G"], ["D", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1244（train）

题面：<image>$\triangle PQS \cong \triangle RQS$. Find $y$.

参考答案：`8`

原图：[打开](<../../data/project3_perception_prototype/images/1244.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(Q, P)), 2x)
Equals(LengthOf(Line(R, Q)), 3y+8)
Equals(LengthOf(Line(R, S)), 2y)
Equals(LengthOf(Line(P, S)), x)
PointLiesOnLine(S, Line(R, P))
Perpendicular(Line(Q, S), Line(R, S))
```

原始 text logic forms：

```text
Congruent(Triangle(P,Q,S),Triangle(R,Q,S))
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(Q, P)), 2x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(R, Q)), 3y+8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(R, S)), 2y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(P, S)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(R, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(Q, S), Line(R, S))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["Q", "S"], ["R", "S"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2099（train）

题面：<image>Find x.

参考答案：`13 \sqrt { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/2099.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), 17)
Equals(LengthOf(Line(A, C)), 7)
Equals(LengthOf(Line(B, C)), x)
Perpendicular(Line(A, B), Line(A, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), 17)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "17", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, B), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 36（train）

题面：<image>Find $x$.

参考答案：`135`

原图：[打开](<../../data/project3_perception_prototype/images/36.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(A, B, D)), 130)
Equals(MeasureOf(Angle(C, B, A)), x)
Equals(MeasureOf(Angle(D, B, C)), 95)
PointLiesOnCircle(A, Circle(B, radius_1_0))
PointLiesOnCircle(C, Circle(B, radius_1_0))
PointLiesOnCircle(D, Circle(B, radius_1_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(A, B, D)), 130)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "B", "D"], "value": "130", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, B, A)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, B, C)), 95)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "B", "D"], "value": "95", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(A, Circle(B, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(B, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(B, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1944（train）

题面：<image>Find y in the parallelogram

参考答案：`8`

原图：[打开](<../../data/project3_perception_prototype/images/1944.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), 2x+9)
Equals(LengthOf(Line(B, D)), 4x-5)
Equals(MeasureOf(Angle(C, A, E)), 42)
Equals(MeasureOf(Angle(E, B, D)), 83)
Equals(MeasureOf(Angle(E, A, B)), 23)
Equals(MeasureOf(Angle(D, C, E)), 4y)
PointLiesOnLine(E, Line(A, D))
PointLiesOnLine(E, Line(B, C))
```

原始 text logic forms：

```text
Parallelogram($)
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), 2x+9)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, D)), 4x-5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, A, E)), 42)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "A", "E"], "value": "42", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(E, B, D)), 83)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["D", "B", "E"], "value": "83", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(E, A, B)), 23)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "A", "E"], "value": "23", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(D, C, E)), 4y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1076（train）

题面：<image>Find x.

参考答案：`85`

原图：[打开](<../../data/project3_perception_prototype/images/1076.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), x)
Equals(LengthOf(Line(A, B)), 75)
Equals(LengthOf(Line(B, C)), 40)
Perpendicular(Line(A, B), Line(B, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, B)), 75)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "75", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), 40)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "40", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(A, B), Line(B, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1022（train）

题面：<image>$\overline{QS}$ is a diameter of $\odot V$. Find $m \widehat {STP}$.

参考答案：`147`

原图：[打开](<../../data/project3_perception_prototype/images/1022.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(T, V, S)), 75)
Equals(MeasureOf(Angle(P, V, T)), 72)
PointLiesOnLine(V, Line(S, Q))
PointLiesOnCircle(S, Circle(V, radius_1_0))
PointLiesOnCircle(P, Circle(V, radius_1_0))
PointLiesOnCircle(R, Circle(V, radius_1_0))
PointLiesOnCircle(T, Circle(V, radius_1_0))
PointLiesOnCircle(Q, Circle(V, radius_1_0))
Perpendicular(Line(R, V), Line(S, V))
```

原始 text logic forms：

```text
IsDiameterOf(Line(Q,S),Circle(V))
Find(MeasureOf(Arc(S,T,P)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(T, V, S)), 75)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["S", "V", "T"], "value": "75", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(P, V, T)), 72)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["P", "V", "T"], "value": "72", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(V, Line(S, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(S, Circle(V, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(P, Circle(V, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(R, Circle(V, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(T, Circle(V, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(Q, Circle(V, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(R, V), Line(S, V))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["R", "V"], ["S", "V"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 965（train）

题面：<image>Find the perimeter of the figure.

参考答案：`48`

原图：[打开](<../../data/project3_perception_prototype/images/965.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), 12)
Equals(LengthOf(Line(A, B)), 16)
```

原始 text logic forms：

```text
Find(PerimeterOf(Shape($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), 16)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "16", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 609（train）

题面：<image>In $\odot O, \overline{E C}$ and $\overline{A B}$ are diameters, and $\angle B O D \cong \angle D O E \cong \angle E O F \cong \angle F O A$

Find $m\widehat{A D C}$

参考答案：`270`

原图：[打开](<../../data/project3_perception_prototype/images/609.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(O, Line(E, C))
PointLiesOnLine(O, Line(A, B))
PointLiesOnCircle(E, Circle(O, radius_0_0))
PointLiesOnCircle(F, Circle(O, radius_0_0))
PointLiesOnCircle(A, Circle(O, radius_0_0))
PointLiesOnCircle(C, Circle(O, radius_0_0))
PointLiesOnCircle(D, Circle(O, radius_0_0))
PointLiesOnCircle(B, Circle(O, radius_0_0))
Perpendicular(Line(O, A), Line(O, C))
```

原始 text logic forms：

```text
Circle(O)
IsDiameterOf(Line(E,C),Circle(O))
IsDiameterOf(Line(A,B),Circle(O))
Equals(Angle(B,O,D),Angle(D,O,E))
Equals(Angle(D,O,E),Angle(E,O,F))
Equals(Angle(E,O,F),Angle(F,O,A))
Find(MeasureOf(Arc(A,D,C)))
```

有限 schema 结果：

- `PointLiesOnLine(O, Line(E, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(O, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(O, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(O, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(O, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(O, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(O, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(O, A), Line(O, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "O"], ["C", "O"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1921（train）

题面：<image>In $\odot D, \overline{D E} \cong \overline{E C}, m \overline{C F}=60,$ and

$\overline{D E} \perp \overline{E C} .$ Find $m \angle 4$

参考答案：`45`

原图：[打开](<../../data/project3_perception_prototype/images/1921.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(C, B, A)), MeasureOf(angle 3))
Equals(MeasureOf(Angle(B, A, C)), MeasureOf(angle 4))
Equals(MeasureOf(Angle(A, C, B)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(E, D, C)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(F, C, D)), MeasureOf(angle 6))
Equals(MeasureOf(Angle(D, A, F)), MeasureOf(angle 5))
Equals(MeasureOf(Angle(A, F, C)), MeasureOf(angle 7))
PointLiesOnLine(D, Line(C, A))
PointLiesOnLine(G, Line(C, B))
PointLiesOnLine(G, Line(D, E))
PointLiesOnCircle(C, Circle(D, radius_3_0))
PointLiesOnCircle(A, Circle(D, radius_3_0))
PointLiesOnCircle(F, Circle(D, radius_3_0))
PointLiesOnCircle(B, Circle(D, radius_3_0))
Perpendicular(Line(B, G), Line(D, G))
```

原始 text logic forms：

```text
Circle(D)
Equals(LengthOf(Line(D,E)),Line(E,C))
Equals(LengthOf(Line(C,F)),60)
Perpendicular(Line(D,E),Line(E,C))
Find(MeasureOf(Angle(4)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(C, B, A)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, A, C)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, C, B)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, D, C)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, C, D)), MeasureOf(angle 6))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, A, F)), MeasureOf(angle 5))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, F, C)), MeasureOf(angle 7))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(C, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(C, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(D, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(B, G), Line(D, G))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "G"], ["D", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1989（train）

题面：<image>Find $m\angle Z$

参考答案：`143`

原图：[打开](<../../data/project3_perception_prototype/images/1989.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(U, V, W)), 3x-11)
Equals(MeasureOf(Angle(V, U, Z)), x-8)
Equals(MeasureOf(Angle(Y, W, V)), x+8)
Equals(MeasureOf(Angle(U, Z, Y)), 2x+7)
Equals(MeasureOf(Angle(Z, Y, W)), x)
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(Z)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(U, V, W)), 3x-11)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(V, U, Z)), x-8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(Y, W, V)), x+8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(U, Z, Y)), 2x+7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(Z, Y, W)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1245（train）

题面：<image>Find x.

参考答案：`\sqrt { 11 }`

原图：[打开](<../../data/project3_perception_prototype/images/1245.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, C)), 6)
Equals(LengthOf(Line(A, C)), x)
Equals(LengthOf(Line(A, B)), 5)
Perpendicular(Line(A, C), Line(A, B))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, C)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, B)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(A, C), Line(A, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1643（train）

题面：<image>ABCD is a trapezoid.

If $AC = 3x – 7$ and $BD = 2x + 8$, find the value of $x$ so that ABCD is isosceles.

参考答案：`15`

原图：[打开](<../../data/project3_perception_prototype/images/1643.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(P, Line(B, D))
PointLiesOnLine(P, Line(A, C))
```

原始 text logic forms：

```text
Trapezoid(A,B,C,D)
Equals(LengthOf(Line(A,C)),3x-7)
Equals(LengthOf(Line(B,D)),2x+8)
Isosceles(Quadrilateral(A,B,C,D))
Find(x)
```

有限 schema 结果：

- `PointLiesOnLine(P, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 681（train）

题面：<image>Use parallelogram $JKLM$ to find JK

参考答案：`6`

原图：[打开](<../../data/project3_perception_prototype/images/681.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(L, K, J)), 109)
Equals(LengthOf(Line(L, M)), 6)
```

原始 text logic forms：

```text
Parallelogram(J,K,L,M)
Find(LengthOf(Line(J,K)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(L, K, J)), 109)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["J", "K", "L"], "value": "109", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(L, M)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["L", "M"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1647（train）

题面：<image>Find the area of the figure. Round to the nearest tenth.

参考答案：`87.5`

原图：[打开](<../../data/project3_perception_prototype/images/1647.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), 7)
Equals(LengthOf(Line(A, I)), 7)
PointLiesOnCircle(B, Circle(O, radius_0_0))
PointLiesOnCircle(I, Circle(C, radius_4_0))
PointLiesOnCircle(D, Circle(O, radius_0_0))
PointLiesOnCircle(D, Circle(C, radius_4_0))
Perpendicular(Line(A, B), Line(A, I))
PointLiesOnLine(O, Line(D, B))
PointLiesOnLine(C, Line(D, I))
```

原始 text logic forms：

```text
Find(AreaOf(Shape($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, I)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "I"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(B, Circle(O, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(I, Circle(C, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(O, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(C, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, B), Line(A, I))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "I"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(O, Line(D, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(D, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 285（train）

题面：<image>Find $RT$.

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/285.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(R, W)), x+6)
Equals(LengthOf(Line(T, R)), 2x+6)
Equals(LengthOf(Line(T, V)), 10)
Equals(LengthOf(Line(S, W)), 8)
PointLiesOnLine(R, Line(T, W))
PointLiesOnLine(R, Line(S, V))
Equals(MeasureOf(Angle(S,W,T)), MeasureOf(Angle(R,T,V)))
```

原始 text logic forms：

```text
Find(LengthOf(Line(R,T)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(R, W)), x+6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(T, R)), 2x+6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(T, V)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["T", "V"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(S, W)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["S", "W"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(R, Line(T, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(S, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(S,W,T)), MeasureOf(Angle(R,T,V)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 967（train）

题面：<image>Find $PW$, if $XZ = 18$ and $PY = 3$

参考答案：`15`

原图：[打开](<../../data/project3_perception_prototype/images/967.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(P, Line(X, Z))
PointLiesOnLine(P, Line(W, Y))
Equals(LengthOf(Line(Z, Y)), LengthOf(Line(X, W)))
Parallel(Line(X, Y), Line(W, Z))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(X,Z)),18)
Equals(LengthOf(Line(P,Y)),3)
Find(LengthOf(Line(P,W)))
```

有限 schema 结果：

- `PointLiesOnLine(P, Line(X, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(W, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(Z, Y)), LengthOf(Line(X, W)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(X, Y), Line(W, Z))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["W", "Z"], ["X", "Y"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 452（train）

题面：<image>Find $m \angle JMK$.

参考答案：`102`

原图：[打开](<../../data/project3_perception_prototype/images/452.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(H, O, J)), 79)
Equals(MeasureOf(Angle(K, O, L)), 77)
PointLiesOnLine(M, Line(K, H))
PointLiesOnLine(M, Line(L, J))
PointLiesOnCircle(L, Circle(O, radius_2_0))
PointLiesOnCircle(J, Circle(O, radius_2_0))
PointLiesOnCircle(K, Circle(O, radius_2_0))
PointLiesOnCircle(H, Circle(O, radius_2_0))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(J,M,K)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(H, O, J)), 79)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["H", "O", "J"], "value": "79", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(K, O, L)), 77)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["K", "O", "L"], "value": "77", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(M, Line(K, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(L, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(L, Circle(O, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(J, Circle(O, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(K, Circle(O, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(H, Circle(O, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 433（train）

题面：<image>If $SP=4, PT=6$, and $QR=12$, find $SQ$.

参考答案：`8`

原图：[打开](<../../data/project3_perception_prototype/images/433.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(P, Line(S, Q))
PointLiesOnLine(T, Line(S, R))
Parallel(Line(R, Q), Line(T, P))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(S,P)),4)
Equals(LengthOf(Line(P,T)),6)
Equals(LengthOf(Line(Q,R)),12)
Find(LengthOf(Line(S,Q)))
```

有限 schema 结果：

- `PointLiesOnLine(P, Line(S, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(S, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(R, Q), Line(T, P))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["P", "T"], ["Q", "R"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1604（train）

题面：<image>The degree measures of minor arc $\widehat{A C}$ and major arc $\widehat{A D C}$ are $x$ and $y$ respectively. If $m∠ABC = 70°$, find $y$.

参考答案：`250`

原图：[打开](<../../data/project3_perception_prototype/images/1604.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Minor(Arc(A,C))),x)
Equals(MeasureOf(Major(Arc(A,D,C))),y)
PointLiesOnCircle(A, Circle(E, radius_3_0))
PointLiesOnCircle(C, Circle(E, radius_3_0))
PointLiesOnCircle(D, Circle(E, radius_3_0))
```

原始 text logic forms：

```text
Arc(A,C)
Arc(A,D,C)
Equals(MeasureOf(Angle(A,B,C)),70)
Find(y)
```

有限 schema 结果：

- `Equals(MeasureOf(Minor(Arc(A,C))),x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Major(Arc(A,D,C))),y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(E, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(E, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(E, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1404（train）

题面：<image>Quadrilateral $A B C D$ is inscribed in $\odot Z$ such that $m \angle B Z A=104, m \widehat{C B}=94,$ and $\overline{A B} \| \overline{D C} .$

Find $m \angle B D A$

参考答案：`52`

原图：[打开](<../../data/project3_perception_prototype/images/1404.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(E, Line(D, B))
PointLiesOnLine(E, Line(A, C))
PointLiesOnCircle(D, Circle(Z, radius_4_0))
PointLiesOnCircle(A, Circle(Z, radius_4_0))
PointLiesOnCircle(B, Circle(Z, radius_4_0))
PointLiesOnCircle(C, Circle(Z, radius_4_0))
```

原始 text logic forms：

```text
InscribedIn(Quadrilateral(A,B,C,D),Circle(Z))
Equals(MeasureOf(Angle(B,Z,A)),104)
Equals(MeasureOf(Arc(C,B)),94)
Parallel(Line(A,B),Line(D,C))
Find(MeasureOf(Angle(B,D,A)))
```

有限 schema 结果：

- `PointLiesOnLine(E, Line(D, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(Z, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(Z, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(Z, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(Z, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 17（train）

题面：<image>parallelogram MNPQ with $m \angle M=10 x$ and $m \angle N=20 x$, find $\angle Q$

参考答案：`120`

原图：[打开](<../../data/project3_perception_prototype/images/17.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(P, N, M)), MeasureOf(Angle(P, Q, M)))
Equals(MeasureOf(Angle(Q, P, N)), MeasureOf(Angle(Q, M, N)))
```

原始 text logic forms：

```text
Parallelogram(M,N,P,Q)
Equals(MeasureOf(Angle(M)),10x)
Equals(MeasureOf(Angle(N)),20x)
Find(MeasureOf(Angle(Q)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(P, N, M)), MeasureOf(Angle(P, Q, M)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(Q, P, N)), MeasureOf(Angle(Q, M, N)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 268（train）

题面：<image>Find x

参考答案：`20`

原图：[打开](<../../data/project3_perception_prototype/images/268.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Arc(C, D)), 130)
Equals(MeasureOf(Angle(D, F, K)), x)
Equals(MeasureOf(Arc(C, G)), 45)
PointLiesOnLine(C, Line(A, D))
PointLiesOnLine(C, Line(A, F))
PointLiesOnLine(D, Line(A, F))
PointLiesOnLine(C, Line(A, I))
PointLiesOnLine(D, Line(C, F))
PointLiesOnLine(K, Line(F, E))
PointLiesOnLine(K, Line(F, G))
PointLiesOnLine(G, Line(F, H))
PointLiesOnLine(K, Line(F, H))
PointLiesOnLine(D, Line(F, J))
PointLiesOnLine(G, Line(K, H))
PointLiesOnLine(G, Line(E, H))
PointLiesOnCircle(C, Circle(E, radius_4_0))
PointLiesOnCircle(D, Circle(E, radius_4_0))
PointLiesOnCircle(G, Circle(E, radius_4_0))
PointLiesOnCircle(K, Circle(E, radius_4_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Arc(C, D)), 130)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, F, K)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Arc(C, G)), 45)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(A, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(A, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(A, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(A, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(C, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(F, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(F, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(F, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(F, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(F, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(K, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(E, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(G, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(K, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 968（train）

题面：<image>Find $x$ in the figure.

参考答案：`16`

原图：[打开](<../../data/project3_perception_prototype/images/968.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(D, G, C)), 3x)
Equals(MeasureOf(Angle(C, G, H)), 42)
Equals(MeasureOf(Angle(G, C, D)), z)
Equals(MeasureOf(Angle(G, C, H)), 48)
Equals(MeasureOf(Angle(G, H, C)), y)
Parallel(Line(G,D), Line(H,C))

```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(D, G, C)), 3x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, G, H)), 42)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "G", "H"], "value": "42", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(G, C, D)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(G, C, H)), 48)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["G", "C", "H"], "value": "48", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(G, H, C)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(G,D), Line(H,C))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["C", "H"], ["D", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1274（train）

题面：<image>Find x.

参考答案：`22`

原图：[打开](<../../data/project3_perception_prototype/images/1274.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), 11\sqrt{2})
Equals(MeasureOf(Angle(A, C, B)), 45)
Equals(LengthOf(Line(B, C)), x)
Equals(LengthOf(Line(A, B)), 11\sqrt{2})
Perpendicular(Line(A, C), Line(A, B))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), 11\sqrt{2})` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, C, B)), 45)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "C", "B"], "value": "45", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, B)), 11\sqrt{2})` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, C), Line(A, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 545（train）

题面：<image>Find the value  of $x$ in each diagram

参考答案：`93`

原图：[打开](<../../data/project3_perception_prototype/images/545.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(C, A, F)), x-11)
Equals(MeasureOf(Angle(A, B, E)), x+10)
Equals(MeasureOf(Angle(B, D, G)), 31)
Equals(MeasureOf(Angle(G, C, H)), 2x-42)
PointLiesOnLine(C, Line(A, H))
PointLiesOnLine(A, Line(B, F))
PointLiesOnLine(B, Line(D, E))
PointLiesOnLine(D, Line(C, G))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(C, A, F)), x-11)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, B, E)), x+10)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, D, G)), 31)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "D", "G"], "value": "31", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(G, C, H)), 2x-42)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(A, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(B, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(D, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(C, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 324（train）

题面：<image>Find the area of the shaded region. Assume the inscribed polygon is regular.

参考答案：`3.3`

原图：[打开](<../../data/project3_perception_prototype/images/324.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(PerimeterOf(Cirle(C))), 12)
PointLiesOnLine(C, Line(A, B))
PointLiesOnLine(C, Line(E, H))
PointLiesOnLine(C, Line(J, F))
PointLiesOnCircle(A, Circle(C, radius_2_0))
PointLiesOnCircle(B, Circle(C, radius_2_0))
PointLiesOnCircle(E, Circle(C, radius_2_0))
PointLiesOnCircle(F, Circle(C, radius_2_0))
PointLiesOnCircle(H, Circle(C, radius_2_0))
PointLiesOnCircle(J, Circle(C, radius_2_0))
```

原始 text logic forms：

```text
Regular(Polygon($))
Find(AreaOf(Shaded(Shape($))))
```

有限 schema 结果：

- `Equals(LengthOf(PerimeterOf(Cirle(C))), 12)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(E, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(J, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(C, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(C, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(C, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(C, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(H, Circle(C, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(J, Circle(C, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 638（train）

题面：<image>Find x

参考答案：`7 \sqrt { 3 }`

原图：[打开](<../../data/project3_perception_prototype/images/638.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(Z, X)), 14)
Equals(LengthOf(Line(X, Y)), 7)
Equals(LengthOf(Line(Z, Y)), x)
Perpendicular(Line(X, Y), Line(Z, Y))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(Z, X)), 14)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["X", "Z"], "value": "14", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(X, Y)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["X", "Y"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(Z, Y)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(X, Y), Line(Z, Y))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["X", "Y"], ["Y", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1206（train）

题面：<image>In $\odot R, S U=20, Y W=20,$ and $m \widehat{Y X}=45$.

Find $m\widehat{Y W}$

参考答案：`90`

原图：[打开](<../../data/project3_perception_prototype/images/1206.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(Z, Line(Y, W))
PointLiesOnLine(V, Line(U, S))
PointLiesOnLine(Z, Line(R, X))
PointLiesOnLine(V, Line(R, T))
PointLiesOnCircle(Y, Circle(R, radius_5_0))
PointLiesOnCircle(U, Circle(R, radius_5_0))
PointLiesOnCircle(S, Circle(R, radius_5_0))
PointLiesOnCircle(W, Circle(R, radius_5_0))
PointLiesOnCircle(X, Circle(R, radius_5_0))
PointLiesOnCircle(T, Circle(R, radius_5_0))
Perpendicular(Line(V, S), Line(V, R))
Perpendicular(Line(Z, R), Line(Y, Z))
```

原始 text logic forms：

```text
Circle(R)
Equals(LengthOf(Line(S,U)),20)
Equals(LengthOf(Line(Y,W)),20)
Equals(MeasureOf(Arc(Y,X)),45)
Find(MeasureOf(Arc(Y,W)))
```

有限 schema 结果：

- `PointLiesOnLine(Z, Line(Y, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(U, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(R, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(R, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(Y, Circle(R, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(U, Circle(R, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(S, Circle(R, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(W, Circle(R, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(X, Circle(R, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(T, Circle(R, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(V, S), Line(V, R))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["R", "V"], ["S", "V"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(Z, R), Line(Y, Z))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["R", "Z"], ["Y", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 935（train）

题面：<image>Find y.

参考答案：`\sqrt { 510 }`

原图：[打开](<../../data/project3_perception_prototype/images/935.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, D)), 15)
Equals(LengthOf(Line(B, D)), y)
Equals(LengthOf(Line(A, C)), 19)
Equals(LengthOf(Line(A, B)), x)
Equals(LengthOf(Line(B, C)), z)
PointLiesOnLine(A, Line(C, D))
Perpendicular(Line(A, C), Line(A, B))
Perpendicular(Line(B, D), Line(B, C))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, D)), 15)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "15", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, D)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, C)), 19)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "19", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(C, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, C), Line(A, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, D), Line(B, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "C"], ["B", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 946（train）

题面：<image>In $\triangle RST$, $Z$ is the centroid and $RZ=18$. Find $SZ$.

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/946.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(R, W)), 14)
Equals(LengthOf(Line(R, Z)), 18)
Equals(LengthOf(Line(U, Z)), 5)
PointLiesOnLine(Z, Line(U, S))
PointLiesOnLine(W, Line(S, R))
PointLiesOnLine(V, Line(S, T))
PointLiesOnLine(U, Line(R, T))
PointLiesOnLine(Z, Line(R, V))
PointLiesOnLine(Z, Line(T, W))
```

原始 text logic forms：

```text
Triangle(R,S,T)
IsCentroidOf(Point(Z),Triangle(R,S,T))
Equals(LengthOf(Line(R,Z)),18)
Find(LengthOf(Line(S,Z)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(R, W)), 14)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["R", "W"], "value": "14", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, Z)), 18)` → `text_explicit`；规范事实 `{"relation": "Length", "entities": ["R", "Z"], "value": "18", "unit": "unspecified_source_unit"}`；same_normalized_fact_in_official_text_annotation
- `Equals(LengthOf(Line(U, Z)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["U", "Z"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(Z, Line(U, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(W, Line(S, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(S, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(R, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(R, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(T, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1021（train）

题面：<image>The two polygons are similar. Find x.

参考答案：`13.5`

原图：[打开](<../../data/project3_perception_prototype/images/1021.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(T, S)), 18)
Equals(LengthOf(Line(T, U)), y+2)
Equals(LengthOf(Line(R, V)), x)
Equals(LengthOf(Line(B, C)), 4)
Equals(LengthOf(Line(C, D)), 5)
Equals(LengthOf(Line(A, E)), 3)
Equals(MeasureOf(Angle(B, A, E)), MeasureOf(Angle(V, R, S)))
Equals(MeasureOf(Angle(A, B, C)), MeasureOf(Angle(R, S, T)))
Equals(MeasureOf(Angle(B, C, D)), MeasureOf(Angle(S, T, U)))
Equals(MeasureOf(Angle(C, D, E)), MeasureOf(Angle(T, U, V)))
Equals(MeasureOf(Angle(A, E, D)), MeasureOf(Angle(U, V, R)))

```

原始 text logic forms：

```text
Similar(Polygon($1),Polygon($2))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(T, S)), 18)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["S", "T"], "value": "18", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(T, U)), y+2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(R, V)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, D)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, E)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "E"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(B, A, E)), MeasureOf(Angle(V, R, S)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, B, C)), MeasureOf(Angle(R, S, T)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, C, D)), MeasureOf(Angle(S, T, U)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, D, E)), MeasureOf(Angle(T, U, V)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, E, D)), MeasureOf(Angle(U, V, R)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1749（train）

题面：<image>$\overline{XY}$ and $\overline{XZ}$ are midsegments of $\triangle RST$. Find $XZ$.

参考答案：`6.5`

原图：[打开](<../../data/project3_perception_prototype/images/1749.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(R, T)), 13)
Equals(LengthOf(Line(X, Y)), 7)
Equals(MeasureOf(Angle(Z, X, Y)), 124)
PointLiesOnLine(Y, Line(R, T))
PointLiesOnLine(X, Line(R, S))
PointLiesOnLine(Z, Line(T, S))
```

原始 text logic forms：

```text
IsMidsegmentOf(Line(X,Y),Triangle(R,S,T))
IsMidsegmentOf(Line(X,Z),Triangle(R,S,T))
Find(LengthOf(Line(X,Z)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(R, T)), 13)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["R", "T"], "value": "13", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(X, Y)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["X", "Y"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(Z, X, Y)), 124)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["Y", "X", "Z"], "value": "124", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(Y, Line(R, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(X, Line(R, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Z, Line(T, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 191（train）

题面：<image>$J$ is the incenter of $\angle ABC$. Find $m \angle JAC$.

参考答案：`24`

原图：[打开](<../../data/project3_perception_prototype/images/191.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(G, C, B)), 32)
Equals(MeasureOf(Angle(G, B, A)), 34)
Equals(LengthOf(Line(A, G)), 15)
Equals(LengthOf(Line(A, E)), 12)
PointLiesOnLine(E, Line(B, A))
PointLiesOnLine(D, Line(B, C))
PointLiesOnLine(F, Line(A, C))
PointLiesOnLine(G, Line(A, D))
Perpendicular(Line(C, D), Line(G, D))
Perpendicular(Line(G, E), Line(A, E))
Perpendicular(Line(G, F), Line(A, F))
```

原始 text logic forms：

```text
IsIncenterOf(Point(J),Angle(A,B,C))
Find(MeasureOf(Angle(J,A,C)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(G, C, B)), 32)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "C", "G"], "value": "32", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(G, B, A)), 34)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "B", "G"], "value": "34", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, G)), 15)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "G"], "value": "15", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, E)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "E"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(B, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(C, D), Line(G, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["C", "D"], ["D", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(G, E), Line(A, E))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "E"], ["E", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(G, F), Line(A, F))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "F"], ["F", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1195（train）

题面：<image>Find x

参考答案：`59`

原图：[打开](<../../data/project3_perception_prototype/images/1195.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Arc(E, C)), 125)
Equals(MeasureOf(Angle(C, B, A)), x)
Equals(MeasureOf(Arc(A, D)), 117)
PointLiesOnLine(F, Line(A, B))
PointLiesOnLine(B, Line(A, E))
PointLiesOnLine(F, Line(A, E))
PointLiesOnLine(B, Line(E, F))
PointLiesOnLine(B, Line(C, D))
PointLiesOnCircle(A, Circle(F, radius_5_0))
PointLiesOnCircle(C, Circle(F, radius_5_0))
PointLiesOnCircle(D, Circle(F, radius_5_0))
PointLiesOnCircle(E, Circle(F, radius_5_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Arc(E, C)), 125)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, B, A)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Arc(A, D)), 117)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(A, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(E, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(C, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(F, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(F, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(F, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(F, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1547（train）

题面：<image>If the polygon shown is regular, what is $m\angle ABC$

参考答案：`140`

原图：[打开](<../../data/project3_perception_prototype/images/1547.png>)

原始 diagram logic forms：

```text

```

原始 text logic forms：

```text
Regular(Polygon($))
Find(MeasureOf(Angle(A,B,C)))
```

有限 schema 结果：

- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1089（train）

题面：<image>Solve for $x$.

参考答案：`6`

原图：[打开](<../../data/project3_perception_prototype/images/1089.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(M, C)), 4.5)
Equals(MeasureOf(Angle(A, M, E)), 4x+1)
Equals(MeasureOf(Angle(A, M, D)), 5x-5)
Equals(LengthOf(Line(M, D)), 4.5)
PointLiesOnLine(D, Line(M, B))
PointLiesOnLine(C, Line(M, E))
PointLiesOnLine(A, Line(M, F))
Equals(LengthOf(Line(C, A)), LengthOf(Line(A, D)))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(M, C)), 4.5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "M"], "value": "9/2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, M, E)), 4x+1)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, M, D)), 5x-5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(M, D)), 4.5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["D", "M"], "value": "9/2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(D, Line(M, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(M, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(M, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(C, A)), LengthOf(Line(A, D)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1683（train）

题面：<image>WXYZ is a square. If $WT = 3$, find $m \angle WTZ$

参考答案：`90`

原图：[打开](<../../data/project3_perception_prototype/images/1683.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(T, Line(Z, X))
PointLiesOnLine(T, Line(W, Y))
Perpendicular(Line(X, W), Line(X, Y))
Perpendicular(Line(X, W), Line(Z, W))
Perpendicular(Line(X, Y), Line(Z, Y))
Perpendicular(Line(Z, W), Line(Z, Y))
```

原始 text logic forms：

```text
Square(W,X,Y,Z)
Equals(LengthOf(Line(W,T)),3)
Find(MeasureOf(Angle(W,T,Z)))
```

有限 schema 结果：

- `PointLiesOnLine(T, Line(Z, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(W, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(X, W), Line(X, Y))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["W", "X"], ["X", "Y"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(X, W), Line(Z, W))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["W", "X"], ["W", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(X, Y), Line(Z, Y))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["X", "Y"], ["Y", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(Z, W), Line(Z, Y))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["W", "Z"], ["Y", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 700（train）

题面：<image>If $AB=6,BC=4$, and $AE=9$, find $ED$.

参考答案：`6`

原图：[打开](<../../data/project3_perception_prototype/images/700.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(E, Line(D, A))
PointLiesOnLine(B, Line(A, C))
Parallel(Line(E, B), Line(D, C))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(A,B)),6)
Equals(LengthOf(Line(B,C)),4)
Equals(LengthOf(Line(A,E)),9)
Find(LengthOf(Line(E,D)))
```

有限 schema 结果：

- `PointLiesOnLine(E, Line(D, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(E, B), Line(D, C))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["B", "E"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1297（train）

题面：<image>Find $x$.

参考答案：`9`

原图：[打开](<../../data/project3_perception_prototype/images/1297.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), 27)
Equals(LengthOf(Line(B, A)), 2x+5)
Equals(LengthOf(Line(B, C)), 3x-4)
Equals(LengthOf(Line(B, A)), LengthOf(Line(B, C)))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), 27)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "27", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, A)), 2x+5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), 3x-4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, A)), LengthOf(Line(B, C)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 272（train）

题面：<image>$\odot  C \cong \odot D$, Find $x$.

参考答案：`27`

原图：[打开](<../../data/project3_perception_prototype/images/272.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(K, L)), 0)
Equals(LengthOf(Line(K, L)), 0)
PointLiesOnCircle(K, Circle(A, radius_2_0))
PointLiesOnCircle(L, Circle(A, radius_2_0))
```

原始 text logic forms：

```text
Congruent(Circle(C),Circle(D))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(K, L)), 0)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(K, L)), 0)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(K, Circle(A, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(L, Circle(A, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 424（train）

题面：<image>Use rectangle LMNP, parallelogram LKMJ to solve the problem.

If $M K=6 x, K L=3 x+2 y,$ and $J N=14-x$

find $y$

参考答案：`3`

原图：[打开](<../../data/project3_perception_prototype/images/424.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(J, Line(L, N))
PointLiesOnLine(J, Line(M, P))
```

原始 text logic forms：

```text
Rectangle(L,M,N,P)
Parallelogram(L,K,M,J)
Equals(LengthOf(Line(M,K)),6x)
Equals(LengthOf(Line(K,L)),3x+2y)
Equals(LengthOf(Line(J,N)),14-x)
Find(y)
```

有限 schema 结果：

- `PointLiesOnLine(J, Line(L, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(M, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 704（train）

题面：<image>Find the value of $f$ in the parallelogram

参考答案：`14`

原图：[打开](<../../data/project3_perception_prototype/images/704.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(K, J)), 3f-6)
Equals(MeasureOf(Angle(K, J, M)), 56)
Equals(MeasureOf(Angle(J, M, L)), 3d-2)
Equals(LengthOf(Line(L, M)), 2f+8)
```

原始 text logic forms：

```text
Parallelogram($)
Find(f)
```

有限 schema 结果：

- `Equals(LengthOf(Line(K, J)), 3f-6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(K, J, M)), 56)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["K", "J", "M"], "value": "56", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(J, M, L)), 3d-2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(L, M)), 2f+8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 108（train）

题面：<image>For the pair of similar figures, use the given areas to find the scale factor of the blue to the green figure. 

参考答案：`\frac { 3 } { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/108.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(F, G)), 24)
Equals(LengthOf(Line(C, B)), x)
Equals(AreaOf(Kite(A,B,C,D)), 846)
Equals(AreaOf(Kite(E,F,G,H)), 376)
```

原始 text logic forms：

```text
Similar(Shape($1),Shape($2))
Find(ScaleFactorOf(Blue(Shape($)),Green(Shape($))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(F, G)), 24)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["F", "G"], "value": "24", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, B)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(AreaOf(Kite(A,B,C,D)), 846)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(AreaOf(Kite(E,F,G,H)), 376)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 345（train）

题面：<image>Find $x$.

参考答案：`81.5`

原图：[打开](<../../data/project3_perception_prototype/images/345.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(H, A, J)), 47)
Equals(MeasureOf(Angle(K, G, L)), x)
Equals(MeasureOf(Angle(K, A, L)), 116)
PointLiesOnLine(G, Line(J, L))
PointLiesOnLine(G, Line(H, K))
PointLiesOnCircle(J, Circle(A, radius_3_0))
PointLiesOnCircle(L, Circle(A, radius_3_0))
PointLiesOnCircle(K, Circle(A, radius_3_0))
PointLiesOnCircle(H, Circle(A, radius_3_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(H, A, J)), 47)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["H", "A", "J"], "value": "47", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(K, G, L)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(K, A, L)), 116)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["K", "A", "L"], "value": "116", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(G, Line(J, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(H, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(J, Circle(A, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(L, Circle(A, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(K, Circle(A, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(H, Circle(A, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1923（train）

题面：<image>In the figure, $ \overline{GK} \cong \overline{GH}$ and $ \overline{HK} \cong \overline{KJ}$. If $m \angle HGK=42$, find $m \angle HJK$.

参考答案：`34.5`

原图：[打开](<../../data/project3_perception_prototype/images/1923.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(K, Line(G, J))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(G,K)),Line(G,H))
Equals(LengthOf(Line(H,K)),Line(K,J))
Equals(MeasureOf(Angle(H,G,K)),42)
Find(MeasureOf(Angle(H,J,K)))
```

有限 schema 结果：

- `PointLiesOnLine(K, Line(G, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1002（train）

题面：<image>In $\odot X, A B=30, C D=30,$ and $m \widehat{C Z}=40$

Find $m\widehat{Y B}$

参考答案：`40`

原图：[打开](<../../data/project3_perception_prototype/images/1002.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(N, Line(X, Z))
PointLiesOnLine(M, Line(X, Y))
PointLiesOnLine(N, Line(C, D))
PointLiesOnLine(M, Line(A, B))
PointLiesOnCircle(Z, Circle(X, radius_0_0))
PointLiesOnCircle(A, Circle(X, radius_0_0))
PointLiesOnCircle(C, Circle(X, radius_0_0))
PointLiesOnCircle(D, Circle(X, radius_0_0))
PointLiesOnCircle(Y, Circle(X, radius_0_0))
Perpendicular(Line(Y, M), Line(M, A))
Perpendicular(Line(N, D), Line(Z, N))
```

原始 text logic forms：

```text
Circle(X)
Equals(LengthOf(Line(A,B)),30)
Equals(LengthOf(Line(C,D)),30)
Equals(MeasureOf(Arc(C,Z)),40)
Find(MeasureOf(Arc(Y,B)))
```

有限 schema 结果：

- `PointLiesOnLine(N, Line(X, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(X, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(C, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(Z, Circle(X, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(X, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(X, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(X, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(Y, Circle(X, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(Y, M), Line(M, A))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "M"], ["M", "Y"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(N, D), Line(Z, N))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["D", "N"], ["N", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1551（train）

题面：<image>Find x. Round side measures to the nearest tenth.

参考答案：`7.7`

原图：[打开](<../../data/project3_perception_prototype/images/1551.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), x)
Equals(LengthOf(Line(A, C)), 8)
Equals(MeasureOf(Angle(C, B, A)), 73)
Equals(MeasureOf(Angle(A, C, B)), 67)
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, C)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, B, A)), 73)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "B", "C"], "value": "73", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, C, B)), 67)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "C", "B"], "value": "67", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 725（train）

题面：<image>Find $CP$.

参考答案：`8`

原图：[打开](<../../data/project3_perception_prototype/images/725.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(P, A)), 8)
PointLiesOnLine(A, Line(B, Y))
PointLiesOnLine(C, Line(B, D))
PointLiesOnLine(P, Line(B, E))
Perpendicular(Line(B, C), Line(P, C))
Perpendicular(Line(B, A), Line(P, A))
Equals(MeasureOf(Angle(A, B, P)), MeasureOf(Angle(P, B, C)))
```

原始 text logic forms：

```text
Find(LengthOf(Line(C,P)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(P, A)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "P"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(A, Line(B, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(B, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(B, C), Line(P, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "C"], ["C", "P"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, A), Line(P, A))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "P"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, B, P)), MeasureOf(Angle(P, B, C)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1585（train）

题面：<image>Find the area of the shaded region. Assume that all polygons that appear to be regular are regular. Round to the nearest tenth.

参考答案：`168.2`

原图：[打开](<../../data/project3_perception_prototype/images/1585.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, D)), 8)
PointLiesOnLine(H, Line(A, B))
PointLiesOnLine(G, Line(A, C))
PointLiesOnLine(H, Line(A, J))
PointLiesOnLine(F, Line(B, C))
PointLiesOnLine(I, Line(B, C))
PointLiesOnLine(J, Line(B, C))
PointLiesOnLine(E, Line(B, D))
PointLiesOnLine(J, Line(B, D))
PointLiesOnLine(J, Line(B, E))
PointLiesOnLine(I, Line(B, F))
PointLiesOnLine(J, Line(B, F))
PointLiesOnLine(D, Line(B, G))
PointLiesOnLine(E, Line(B, G))
PointLiesOnLine(J, Line(B, G))
PointLiesOnLine(J, Line(B, I))
PointLiesOnLine(F, Line(C, I))
PointLiesOnLine(F, Line(C, J))
PointLiesOnLine(I, Line(C, J))
PointLiesOnLine(E, Line(D, J))
PointLiesOnLine(D, Line(E, G))
PointLiesOnLine(D, Line(G, J))
PointLiesOnLine(E, Line(G, J))
PointLiesOnLine(I, Line(J, F))
PointLiesOnCircle(A, Circle(D, radius_3_0))
PointLiesOnCircle(B, Circle(D, radius_3_0))
PointLiesOnCircle(C, Circle(D, radius_3_0))
PointLiesOnCircle(J, Circle(D, radius_3_0))
PointLiesOnCircle(E, Circle(D, radius_3_1))
PointLiesOnCircle(F, Circle(D, radius_3_1))
PointLiesOnCircle(G, Circle(D, radius_3_1))
PointLiesOnCircle(H, Circle(D, radius_3_1))
PointLiesOnCircle(I, Circle(D, radius_3_1))
```

原始 text logic forms：

```text
Regular(Polygon($))
Find(AreaOf(Shaded(Shape($))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, D)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(H, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(A, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(B, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(B, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(B, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(C, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(C, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(C, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(G, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(G, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(J, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(J, Circle(D, radius_3_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(D, radius_3_1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(D, radius_3_1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(G, Circle(D, radius_3_1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(H, Circle(D, radius_3_1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(I, Circle(D, radius_3_1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2031（train）

题面：<image>Find x. Assume that segments that appear to be tangent are tangent.

参考答案：`9`

原图：[打开](<../../data/project3_perception_prototype/images/2031.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(D, C)), 6)
Equals(LengthOf(Line(A, D)), x)
Equals(LengthOf(Line(D, F)), 2)
Equals(LengthOf(Line(D, B)), 3)
PointLiesOnLine(D, Line(A, F))
PointLiesOnLine(D, Line(B, C))
PointLiesOnCircle(A, Circle(E, radius_4_0))
PointLiesOnCircle(B, Circle(E, radius_4_0))
PointLiesOnCircle(C, Circle(E, radius_4_0))
PointLiesOnCircle(F, Circle(E, radius_4_0))
```

原始 text logic forms：

```text
Tangent(Line($),Circle($))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(D, C)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, D)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(D, F)), 2)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["D", "F"], "value": "2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, B)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(D, Line(A, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1846（train）

题面：<image>Find $b$ in the given parallelogram

参考答案：`8`

原图：[打开](<../../data/project3_perception_prototype/images/1846.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(Y, A)), 2)
Equals(LengthOf(Line(X, A)), a-7)
Equals(LengthOf(Line(W, A)), 10)
Equals(LengthOf(Line(A, Z)), 2b-6)
PointLiesOnLine(A, Line(Y, X))
PointLiesOnLine(A, Line(Z, W))
```

原始 text logic forms：

```text
Parallelogram($)
Find(b)
```

有限 schema 结果：

- `Equals(LengthOf(Line(Y, A)), 2)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "Y"], "value": "2", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(X, A)), a-7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(W, A)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "W"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, Z)), 2b-6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(Y, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(Z, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 901（train）

题面：<image>Find the area of the parallelogram. Round to the nearest tenth if necessary.

参考答案：`29.2`

原图：[打开](<../../data/project3_perception_prototype/images/901.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(E, C)), 5.4)
Perpendicular(Line(B, C), Line(D, B))
Equals(LengthOf(Line(E, C)), LengthOf(Line(B, C)))
Equals(LengthOf(Line(B, C)), LengthOf(Line(D, B)))
Equals(LengthOf(Line(B, C)), LengthOf(Line(D, E)))
```

原始 text logic forms：

```text
Find(AreaOf(Parallelogram($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(E, C)), 5.4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "E"], "value": "27/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, C), Line(D, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "C"], ["B", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(E, C)), LengthOf(Line(B, C)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), LengthOf(Line(D, B)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), LengthOf(Line(D, E)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1120（train）

题面：<image>If XN = t - 2, NZ = t + 1, XM = 2, and XY = 10, solve for t

参考答案：`3`

原图：[打开](<../../data/project3_perception_prototype/images/1120.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(M, Line(X, Y))
PointLiesOnLine(N, Line(X, Z))
Parallel(Line(M, N), Line(Y, Z))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(X,N)),t-2)
Equals(LengthOf(Line(N,Z)),t+1)
Equals(LengthOf(Line(X,M)),2)
Equals(LengthOf(Line(X,Y)),10)
Find(t)
```

有限 schema 结果：

- `PointLiesOnLine(M, Line(X, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(N, Line(X, Z))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(M, N), Line(Y, Z))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["M", "N"], ["Y", "Z"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1974（train）

题面：<image>Find the area of the figure. Round to the nearest tenth if necessary.

参考答案：`286`

原图：[打开](<../../data/project3_perception_prototype/images/1974.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, E)), 11)
Equals(LengthOf(Line(E, E)), 13)
PointLiesOnLine(E, Line(B, D))
PointLiesOnLine(E, Line(C, O))
```

原始 text logic forms：

```text
Find(AreaOf(Shape($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, E)), 11)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "E"], "value": "11", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(E, E)), 13)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(C, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 938（train）

题面：<image>Find $\angle 6$.

参考答案：`123`

原图：[打开](<../../data/project3_perception_prototype/images/938.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(Z, Y, W)), 58)
Equals(MeasureOf(Angle(Y, X, Z)), MeasureOf(angle 7))
Equals(MeasureOf(Angle(X, Z, Y)), 65)
Equals(MeasureOf(Angle(Z, V, W)), MeasureOf(angle 4))
Equals(MeasureOf(Angle(W, X, V)), MeasureOf(angle 5))
Equals(MeasureOf(Angle(Z, X, W)), MeasureOf(angle 6))
Equals(MeasureOf(Angle(X, Z, W)), MeasureOf(angle 9))
Equals(MeasureOf(Angle(X, W, Z)), MeasureOf(angle 8))
Equals(MeasureOf(Angle(X, W, Z)), MeasureOf(Angle(X, Z, W)))
Equals(MeasureOf(Angle(V, W, Y)), 67)
PointLiesOnLine(X, Line(W, Y))
PointLiesOnLine(X, Line(Z, V))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(6)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(Z, Y, W)), 58)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["W", "Y", "Z"], "value": "58", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(Y, X, Z)), MeasureOf(angle 7))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(X, Z, Y)), 65)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["X", "Z", "Y"], "value": "65", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(Z, V, W)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(W, X, V)), MeasureOf(angle 5))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(Z, X, W)), MeasureOf(angle 6))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(X, Z, W)), MeasureOf(angle 9))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(X, W, Z)), MeasureOf(angle 8))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(X, W, Z)), MeasureOf(Angle(X, Z, W)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(V, W, Y)), 67)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["V", "W", "Y"], "value": "67", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(X, Line(W, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(X, Line(Z, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1644（train）

题面：<image>Find x

参考答案：`\frac { 19 \sqrt { 2 } } { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/1644.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), 19)
Equals(LengthOf(Line(A, C)), x)
Equals(MeasureOf(Angle(C, B, A)), 45)
Equals(LengthOf(Line(B, C)), y)
Perpendicular(Line(A, C), Line(B, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), 19)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "19", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, B, A)), 45)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "B", "C"], "value": "45", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, C), Line(B, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1304（train）

题面：<image>The segment is tangent to the circle. Find $x$.

参考答案：`9`

原图：[打开](<../../data/project3_perception_prototype/images/1304.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, C)), 12)
Equals(LengthOf(Line(E, C)), 6)
Equals(LengthOf(Line(A, B)), x)
Equals(LengthOf(Line(A, E)), x)

PointLiesOnCircle(E, Circle(A, radius_7_0))
PointLiesOnCircle(B, Circle(A, radius_7_0))
```

原始 text logic forms：

```text
Tangent(Line($),Circle($))
Circle($)
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, C)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(E, C)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "E"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, E)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(A, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(A, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1426（train）

题面：<image>If $m \angle AED=95$ and $m \widehat{AD}=120$, what is $m \angle BAC$?

参考答案：`35`

原图：[打开](<../../data/project3_perception_prototype/images/1426.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(D, E, A)), 95)
Equals(MeasureOf(Angle(A, F, D)), 120)
PointLiesOnLine(E, Line(C, A))
PointLiesOnLine(E, Line(B, D))
PointLiesOnCircle(C, Circle(F, radius_5_0))
PointLiesOnCircle(A, Circle(F, radius_5_0))
PointLiesOnCircle(D, Circle(F, radius_5_0))
PointLiesOnCircle(B, Circle(F, radius_5_0))
```

原始 text logic forms：

```text
Equals(MeasureOf(Angle(A,E,D)),95)
Equals(MeasureOf(Arc(A,D)),120)
Find(MeasureOf(Angle(B,A,C)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(D, E, A)), 95)` → `text_explicit`；规范事实 `{"relation": "Angle", "entities": ["A", "E", "D"], "value": "95", "unit": "deg"}`；same_normalized_fact_in_official_text_annotation
- `Equals(MeasureOf(Angle(A, F, D)), 120)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "F", "D"], "value": "120", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(C, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(F, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(F, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(F, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(F, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 265（train）

题面：<image>The diagonals of rhombus FGHJ intersect at K. 

If $m\angle FJH = 82$, find $m\angle KHJ$.

参考答案：`49`

原图：[打开](<../../data/project3_perception_prototype/images/265.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(K, Line(G, J))
PointLiesOnLine(K, Line(H, F))
```

原始 text logic forms：

```text
Rhombus(F,G,H,J)
IsDiagonalOf(Line(F,H),Rhombus(F,G,H,J))
IsDiagonalOf(Line(G,J),Rhombus(F,G,H,J))
IntersectAt(Line(F,H),Line(G,J),Point(K))
Equals(MeasureOf(Angle(F,J,H)),82)
Find(MeasureOf(Angle(K,H,J)))
```

有限 schema 结果：

- `PointLiesOnLine(K, Line(G, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(H, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1025（train）

题面：<image>Find $QR$ if $\triangle QRS$ is an equilateral triangle.

参考答案：`2`

原图：[打开](<../../data/project3_perception_prototype/images/1025.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(R, Q)), 4x)
Equals(LengthOf(Line(R, S)), 2x+1)
Equals(LengthOf(Line(S, Q)), 6x-1)
```

原始 text logic forms：

```text
Equilateral(Triangle(Q,R,S))
Triangle($)
Find(LengthOf(Line(Q,R)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(R, Q)), 4x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(R, S)), 2x+1)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(S, Q)), 6x-1)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 103（train）

题面：<image>Find $m \angle JKL$.

参考答案：`31`

原图：[打开](<../../data/project3_perception_prototype/images/103.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(J, K, L)), 2x-11)
Equals(MeasureOf(Angle(K, J, L)), 2x+27)
Equals(MeasureOf(Angle(K, L, A)), 100)
PointLiesOnLine(L, Line(J, A))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(J,K,L)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(J, K, L)), 2x-11)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(K, J, L)), 2x+27)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(K, L, A)), 100)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "L", "K"], "value": "100", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(L, Line(J, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 467（train）

题面：<image>Find y.

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/467.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(B, A, C)), 60)
Equals(LengthOf(Line(A, B)), y)
Equals(LengthOf(Line(A, C)), 5)
Equals(LengthOf(Line(B, C)), x)
Perpendicular(Line(A, C), Line(B, C))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(B, A, C)), 60)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "A", "C"], "value": "60", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, C)), 5)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, C), Line(B, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2043（train）

题面：<image>In the figure, $a ∥ b, c ∥ d$, and $m∠4 = 57$. Find the measure of $\angle 8$.

参考答案：`57`

原图：[打开](<../../data/project3_perception_prototype/images/2043.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(H, D, A)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(A, D, E)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(H, E, B)), MeasureOf(angle 3))
Equals(MeasureOf(Angle(B, E, C)), MeasureOf(angle 4))
Equals(MeasureOf(Angle(I, D, H)), MeasureOf(angle 8))
Equals(MeasureOf(Angle(E, D, I)), MeasureOf(angle 7))
Equals(MeasureOf(Angle(G, E, D)), MeasureOf(angle 6))
Equals(MeasureOf(Angle(C, E, G)), MeasureOf(angle 5))
Equals(MeasureOf(Angle(F, I, D)), MeasureOf(angle 9))
Equals(MeasureOf(Angle(D, I, J)), MeasureOf(angle 10))
Equals(MeasureOf(Angle(F, K, E)), MeasureOf(angle 11))
Equals(MeasureOf(Angle(E, K, J)), MeasureOf(angle 12))
Equals(LengthOf(Line(I, F)), 16)
Equals(MeasureOf(Angle(J, I, L)), MeasureOf(angle 15))
Equals(MeasureOf(Angle(G, K, F)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(J, K, G)), MeasureOf(angle 13))
PointLiesOnLine(E, Line(D, C))
PointLiesOnLine(I, Line(D, L))
PointLiesOnLine(K, Line(E, G))
PointLiesOnLine(D, Line(E, H))
PointLiesOnLine(D, Line(H, C))
PointLiesOnLine(E, Line(H, C))
PointLiesOnLine(K, Line(I, J))
PointLiesOnLine(D, Line(I, A))
PointLiesOnLine(D, Line(A, L))
PointLiesOnLine(I, Line(A, L))
PointLiesOnLine(E, Line(G, B))
PointLiesOnLine(K, Line(G, B))
PointLiesOnLine(I, Line(K, F))
PointLiesOnLine(E, Line(K, B))
PointLiesOnLine(I, Line(F, J))
PointLiesOnLine(K, Line(F, J))
```

原始 text logic forms：

```text
Parallel(Line(a),Line(b))
Parallel(Line(c),Line(d))
Equals(MeasureOf(Angle(4)),57)
Find(MeasureOf(Angle(8)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(H, D, A)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, D, E)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(H, E, B)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, E, C)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(I, D, H)), MeasureOf(angle 8))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, D, I)), MeasureOf(angle 7))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(G, E, D)), MeasureOf(angle 6))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, E, G)), MeasureOf(angle 5))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, I, D)), MeasureOf(angle 9))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, I, J)), MeasureOf(angle 10))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(F, K, E)), MeasureOf(angle 11))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, K, J)), MeasureOf(angle 12))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(I, F)), 16)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["F", "I"], "value": "16", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(J, I, L)), MeasureOf(angle 15))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(G, K, F)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(J, K, G)), MeasureOf(angle 13))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(D, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(D, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(E, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(H, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(H, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(I, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(I, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(A, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(A, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(G, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(G, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(K, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(K, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(F, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(F, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1055（train）

题面：<image>The two circles are congruent. Find $x$.

参考答案：`16`

原图：[打开](<../../data/project3_perception_prototype/images/1055.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, D)), 3x-7)
Equals(LengthOf(Line(A, B)), 2x+9)
PointLiesOnCircle(C, Circle(P, radius_2_0))
PointLiesOnCircle(D, Circle(P, radius_2_0))
PointLiesOnCircle(A, Circle(O, radius_2_0))
PointLiesOnCircle(B, Circle(O, radius_2_0))
```

原始 text logic forms：

```text
Congruent(Circle($),Circle($))
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, D)), 3x-7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, B)), 2x+9)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(P, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(P, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(O, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(O, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 987（train）

题面：<image>Find x

参考答案：`8 \sqrt { 41 }`

原图：[打开](<../../data/project3_perception_prototype/images/987.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, D)), 40)
Equals(LengthOf(Line(A, D)), 32)
Equals(LengthOf(Line(A, B)), x)
Perpendicular(Line(B, D), Line(A, D))
Perpendicular(Line(B, C), Line(A, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, D)), 40)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "40", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, D)), 32)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "32", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(B, D), Line(A, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "D"], ["B", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, C), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 845（train）

题面：<image>Find $x$ in the figure.

参考答案：`112`

原图：[打开](<../../data/project3_perception_prototype/images/845.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(S, C, R)), 5z+2)
Equals(MeasureOf(Angle(N, R, P)), x)
Equals(MeasureOf(Angle(R, P, M)), 68)
Equals(MeasureOf(Angle(M, P, H)), 4*y)
PointLiesOnLine(R, Line(A, I))
PointLiesOnLine(V, Line(A, I))
PointLiesOnLine(C, Line(A, N))
PointLiesOnLine(V, Line(A, Q))
PointLiesOnLine(V, Line(A, R))
PointLiesOnLine(M, Line(C, E))
PointLiesOnLine(O, Line(C, E))
PointLiesOnLine(U, Line(C, E))
PointLiesOnLine(A, Line(C, I))
PointLiesOnLine(R, Line(C, I))
PointLiesOnLine(V, Line(C, I))
PointLiesOnLine(O, Line(C, M))
PointLiesOnLine(U, Line(C, M))
PointLiesOnLine(U, Line(C, O))
PointLiesOnLine(A, Line(C, R))
PointLiesOnLine(V, Line(C, R))
PointLiesOnLine(A, Line(C, V))
PointLiesOnLine(A, Line(I, N))
PointLiesOnLine(C, Line(I, N))
PointLiesOnLine(R, Line(I, N))
PointLiesOnLine(V, Line(I, N))
PointLiesOnLine(R, Line(I, Q))
PointLiesOnLine(R, Line(I, V))
PointLiesOnLine(C, Line(N, Q))
PointLiesOnLine(A, Line(N, R))
PointLiesOnLine(C, Line(N, R))
PointLiesOnLine(V, Line(N, R))
PointLiesOnLine(A, Line(N, V))
PointLiesOnLine(C, Line(N, V))
PointLiesOnLine(V, Line(Q, S))
PointLiesOnLine(J, Line(R, B))
PointLiesOnLine(B, Line(R, H))
PointLiesOnLine(J, Line(R, H))
PointLiesOnLine(P, Line(R, H))
PointLiesOnLine(B, Line(R, P))
PointLiesOnLine(J, Line(R, P))
PointLiesOnLine(C, Line(S, E))
PointLiesOnLine(M, Line(S, E))
PointLiesOnLine(O, Line(S, E))
PointLiesOnLine(U, Line(S, E))
PointLiesOnLine(C, Line(S, M))
PointLiesOnLine(O, Line(S, M))
PointLiesOnLine(U, Line(S, M))
PointLiesOnLine(C, Line(S, O))
PointLiesOnLine(U, Line(S, O))
PointLiesOnLine(C, Line(S, U))
PointLiesOnLine(M, Line(U, E))
PointLiesOnLine(O, Line(U, E))
PointLiesOnLine(O, Line(U, M))
PointLiesOnLine(J, Line(B, G))
PointLiesOnLine(R, Line(B, G))
PointLiesOnLine(P, Line(B, H))
PointLiesOnLine(B, Line(G, H))
PointLiesOnLine(J, Line(G, H))
PointLiesOnLine(P, Line(G, H))
PointLiesOnLine(R, Line(G, H))
PointLiesOnLine(R, Line(G, J))
PointLiesOnLine(B, Line(G, P))
PointLiesOnLine(J, Line(G, P))
PointLiesOnLine(R, Line(G, P))
PointLiesOnLine(B, Line(H, J))
PointLiesOnLine(P, Line(H, J))
PointLiesOnLine(B, Line(J, P))
PointLiesOnLine(F, Line(P, D))
PointLiesOnLine(K, Line(P, D))
PointLiesOnLine(M, Line(P, D))
PointLiesOnLine(T, Line(P, D))
PointLiesOnLine(K, Line(P, F))
PointLiesOnLine(T, Line(P, F))
PointLiesOnLine(T, Line(P, K))
PointLiesOnLine(F, Line(P, M))
PointLiesOnLine(K, Line(P, M))
PointLiesOnLine(T, Line(P, M))
PointLiesOnLine(M, Line(E, O))
PointLiesOnLine(F, Line(M, K))
PointLiesOnLine(F, Line(M, L))
PointLiesOnLine(K, Line(M, L))
PointLiesOnLine(P, Line(M, L))
PointLiesOnLine(T, Line(M, L))
PointLiesOnLine(F, Line(M, T))
PointLiesOnLine(M, Line(D, F))
PointLiesOnLine(F, Line(D, K))
PointLiesOnLine(M, Line(D, K))
PointLiesOnLine(F, Line(D, L))
PointLiesOnLine(K, Line(D, L))
PointLiesOnLine(M, Line(D, L))
PointLiesOnLine(P, Line(D, L))
PointLiesOnLine(T, Line(D, L))
PointLiesOnLine(F, Line(D, T))
PointLiesOnLine(M, Line(D, T))
PointLiesOnLine(K, Line(F, L))
PointLiesOnLine(P, Line(F, L))
PointLiesOnLine(T, Line(F, L))
PointLiesOnLine(K, Line(F, T))
PointLiesOnLine(P, Line(K, L))
PointLiesOnLine(P, Line(L, T))
Parallel(Line(N,I), Line(D,L))
Parallel(Line(S,E), Line(G,H))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(S, C, R)), 5z+2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(N, R, P)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(R, P, M)), 68)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["M", "P", "R"], "value": "68", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(M, P, H)), 4*y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(A, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(A, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(A, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(A, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(A, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(C, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(C, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(C, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(C, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(C, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(C, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(C, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(C, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(C, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(C, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(C, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(C, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(I, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(I, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(I, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(I, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(I, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(I, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(N, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(N, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(N, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(N, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(N, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(N, V))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(V, Line(Q, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(R, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(R, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(R, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(R, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(R, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(R, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(S, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(S, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(S, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(S, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(S, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(S, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(S, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(S, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(S, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(S, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(U, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(U, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(O, Line(U, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(B, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(B, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(B, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(G, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(G, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(G, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(R, Line(G, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(H, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(H, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(J, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(P, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(P, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(P, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(P, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(P, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(P, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(P, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(P, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(P, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(P, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(E, O))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(M, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(M, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(M, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(M, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(M, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(M, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(D, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(D, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(D, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(D, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(D, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(D, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(D, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(D, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(M, Line(D, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(F, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(F, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(T, Line(F, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(F, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(K, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(L, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(N,I), Line(D,L))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["D", "L"], ["I", "N"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(S,E), Line(G,H))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["E", "S"], ["G", "H"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1510（train）

题面：<image>Find $m \angle ABD$.

参考答案：`103`

原图：[打开](<../../data/project3_perception_prototype/images/1510.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(D, G, B)), 154)
PointLiesOnCircle(B, Circle(G, radius_5_0))
PointLiesOnCircle(C, Circle(G, radius_5_0))
PointLiesOnCircle(D, Circle(G, radius_5_0))
Tangent(Line(A,B), Circle(G))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(A,B,D)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(D, G, B)), 154)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "G", "D"], "value": "154", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(B, Circle(G, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(G, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(G, radius_5_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Tangent(Line(A,B), Circle(G))` → `visual_candidate`；规范事实 `{"relation": "Tangent", "entities": [["A", "B"], "G"], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 417（train）

题面：<image>Find x. Round the side measure to the nearest tenth.

参考答案：`107.9`

原图：[打开](<../../data/project3_perception_prototype/images/417.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, C)), 54)
Equals(LengthOf(Line(B, C)), x)
Equals(MeasureOf(Angle(B, A, C)), 64)
Equals(LengthOf(Line(A, B)), 120)
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, C)), 54)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "54", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(B, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, A, C)), 64)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "A", "C"], "value": "64", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), 120)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "120", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 621（train）

题面：<image>In the figure, $m ∠ 12 = 64$. Find the measure of $ \angle 4$.

参考答案：`64`

原图：[打开](<../../data/project3_perception_prototype/images/621.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(I, D, W)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(W, D, L)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(D, U, A)), MeasureOf(angle 3))
Equals(MeasureOf(Angle(A, U, L)), MeasureOf(angle 4))
Equals(MeasureOf(Angle(H, D, I)), MeasureOf(angle 5))
Equals(MeasureOf(Angle(L, D, H)), MeasureOf(angle 6))
Equals(MeasureOf(Angle(E, U, D)), MeasureOf(angle 7))
Equals(MeasureOf(Angle(L, U, E)), MeasureOf(angle 8))
Equals(MeasureOf(Angle(B, H, D)), MeasureOf(angle 9))
Equals(MeasureOf(Angle(W, H, E)), MeasureOf(angle 10))
Equals(MeasureOf(Angle(B, E, U)), MeasureOf(angle 11))
Equals(MeasureOf(Angle(A, E, N)), MeasureOf(angle 12))
Equals(MeasureOf(Angle(J, H, B)), MeasureOf(angle 13))
Equals(MeasureOf(Angle(E, H, J)), MeasureOf(angle 14))
Equals(MeasureOf(Angle(K, E, B)), MeasureOf(angle 15))
Equals(MeasureOf(Angle(N, E, K)), MeasureOf(angle 16))
PointLiesOnLine(G, Line(A, E))
PointLiesOnLine(U, Line(A, E))
PointLiesOnLine(E, Line(A, K))
PointLiesOnLine(G, Line(A, K))
PointLiesOnLine(U, Line(A, K))
PointLiesOnLine(G, Line(A, U))
PointLiesOnLine(H, Line(E, B))
PointLiesOnLine(U, Line(E, G))
PointLiesOnLine(E, Line(G, K))
PointLiesOnLine(U, Line(G, K))
PointLiesOnLine(E, Line(K, U))
PointLiesOnLine(D, Line(U, I))
PointLiesOnLine(E, Line(B, N))
PointLiesOnLine(H, Line(B, N))
PointLiesOnLine(D, Line(H, W))
PointLiesOnLine(E, Line(H, N))
PointLiesOnLine(H, Line(D, J))
PointLiesOnLine(U, Line(D, L))
PointLiesOnLine(D, Line(I, L))
PointLiesOnLine(U, Line(I, L))
PointLiesOnLine(D, Line(W, J))
PointLiesOnLine(H, Line(W, J))
Parallel(Line(W,J), Line(A,K))
Parallel(Line(I, L), Line(B,N))
```

原始 text logic forms：

```text
Equals(MeasureOf(Angle(12)),64)
Find(MeasureOf(Angle(4)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(I, D, W)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(W, D, L)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, U, A)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, U, L)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(H, D, I)), MeasureOf(angle 5))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(L, D, H)), MeasureOf(angle 6))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, U, D)), MeasureOf(angle 7))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(L, U, E)), MeasureOf(angle 8))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, H, D)), MeasureOf(angle 9))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(W, H, E)), MeasureOf(angle 10))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, E, U)), MeasureOf(angle 11))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, E, N)), MeasureOf(angle 12))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(J, H, B)), MeasureOf(angle 13))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, H, J)), MeasureOf(angle 14))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(K, E, B)), MeasureOf(angle 15))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(N, E, K)), MeasureOf(angle 16))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(A, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(A, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(A, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(E, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(E, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(G, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(G, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(K, U))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(U, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(B, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(B, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(H, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(H, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(D, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(D, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(I, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(U, Line(I, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(W, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(W, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(W,J), Line(A,K))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["A", "K"], ["J", "W"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Parallel(Line(I, L), Line(B,N))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["B", "N"], ["I", "L"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 969（train）

题面：<image>In the figure, $ \overline{GK} \cong \overline{GH}$ and $ \overline{HK} \cong \overline{KJ}$. If $m \angle HGK=28$, find $m \angle HJK$.

参考答案：`38`

原图：[打开](<../../data/project3_perception_prototype/images/969.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(K, Line(J, G))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(G,K)),Line(G,H))
Equals(LengthOf(Line(H,K)),Line(K,J))
Equals(MeasureOf(Angle(H,G,K)),28)
Find(MeasureOf(Angle(H,J,K)))
```

有限 schema 结果：

- `PointLiesOnLine(K, Line(J, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1174（train）

题面：<image>What is the value of x in the figure below? Round to the nearest tenth.

参考答案：`11.1`

原图：[打开](<../../data/project3_perception_prototype/images/1174.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, D)), x)
Equals(LengthOf(Line(A, C)), 18)
Equals(MeasureOf(Angle(C, A, D)), 52)
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, D)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, C)), 18)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "18", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, A, D)), 52)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "A", "D"], "value": "52", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1003（train）

题面：<image>Find $m \widehat {WX}$.

参考答案：`66`

原图：[打开](<../../data/project3_perception_prototype/images/1003.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(A, X, W)), 57)
PointLiesOnLine(A, Line(Y, X))
PointLiesOnCircle(Y, Circle(A, radius_2_0))
PointLiesOnCircle(X, Circle(A, radius_2_0))
PointLiesOnCircle(W, Circle(A, radius_2_0))
```

原始 text logic forms：

```text
Find(MeasureOf(Arc(W,X)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(A, X, W)), 57)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "X", "W"], "value": "57", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(A, Line(Y, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(Y, Circle(A, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(X, Circle(A, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(W, Circle(A, radius_2_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1423（train）

题面：<image>Find $m\angle V$

参考答案：`193`

原图：[打开](<../../data/project3_perception_prototype/images/1423.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(U, V, W)), 3x-11)
Equals(MeasureOf(Angle(V, U, Z)), x-8)
Equals(MeasureOf(Angle(Y, W, V)), x+8)
Equals(MeasureOf(Angle(U, Z, Y)), 2x+7)
Equals(MeasureOf(Angle(Z, Y, W)), x)
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(V)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(U, V, W)), 3x-11)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(V, U, Z)), x-8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(Y, W, V)), x+8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(U, Z, Y)), 2x+7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(Z, Y, W)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1484（train）

题面：<image>The triangle is inscribed into the circle. Find the exact circumference of the circle.

参考答案：`12 \pi`

原图：[打开](<../../data/project3_perception_prototype/images/1484.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(I, Line(B, C))
PointLiesOnCircle(A, Circle(I, radius_8_0))
PointLiesOnCircle(B, Circle(I, radius_8_0))
PointLiesOnCircle(C, Circle(I, radius_8_0))
Perpendicular(Line(A, C), Line(A, B))
Equals(LengthOf(Line(A, C)), LengthOf(Line(A, B)))
Equals(LengthOf(Line(A, B)), 6\sqrt{2})
```

原始 text logic forms：

```text
InscribedIn(Triangle($),Circle($))
Find(CircumferenceOf(Circle($)))
```

有限 schema 结果：

- `PointLiesOnLine(I, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(I, radius_8_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(I, radius_8_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(I, radius_8_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, C), Line(A, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), LengthOf(Line(A, B)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, B)), 6\sqrt{2})` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2056（train）

题面：<image>For trapezoid $D E G H, X$ and $Y$ are midpoints of the legs. Find $D E$

参考答案：`8`

原图：[打开](<../../data/project3_perception_prototype/images/2056.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(X, Y)), 20)
Equals(LengthOf(Line(H, G)), 32)
PointLiesOnLine(X, Line(H, D))
PointLiesOnLine(Y, Line(G, E))
```

原始 text logic forms：

```text
Trapezoid(D,E,G,H)
IsMidpointOf(Point(X),LegOf(Trapezoid(D,E,G,H)))
IsMidpointOf(Point(Y),LegOf(Trapezoid(D,E,G,H)))
Find(LengthOf(Line(D,E)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(X, Y)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["X", "Y"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(H, G)), 32)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["G", "H"], "value": "32", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(X, Line(H, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Y, Line(G, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1112（train）

题面：<image>Find the measure of $∠T$ to the nearest tenth.

参考答案：`33.7`

原图：[打开](<../../data/project3_perception_prototype/images/1112.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(R, S)), 8)
Equals(LengthOf(Line(T, S)), 12)
Perpendicular(Line(R, S), Line(T, S))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(T)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(R, S)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["R", "S"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(T, S)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["S", "T"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(R, S), Line(T, S))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["R", "S"], ["S", "T"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1063（train）

题面：<image>Find the measure of $\angle DFB$ on $\odot F$ with diameter $\overline{AC} $.

参考答案：`165`

原图：[打开](<../../data/project3_perception_prototype/images/1063.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(B, F, C)), 72)
Equals(MeasureOf(Angle(D, F, A)), 2a-5)
Equals(MeasureOf(Angle(C, F, D)), 4a-1)
PointLiesOnCircle(D, Circle(F, radius_0_0))
PointLiesOnCircle(C, Circle(F, radius_0_0))
PointLiesOnCircle(A, Circle(F, radius_0_0))
PointLiesOnCircle(B, Circle(F, radius_0_0))
```

原始 text logic forms：

```text
Circle(F)
IsDiameterOf(Line(A,C),Circle(F))
Find(MeasureOf(Angle(D,F,B)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(B, F, C)), 72)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "F", "C"], "value": "72", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(D, F, A)), 2a-5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, F, D)), 4a-1)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(F, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(F, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(F, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(F, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 811（train）

题面：<image>If $WXYZ$ is a kite, find $ZY$.

参考答案：`8 \sqrt { 10 }`

原图：[打开](<../../data/project3_perception_prototype/images/811.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(X, P)), 8)
Equals(LengthOf(Line(W, P)), 6)
Equals(LengthOf(Line(Y, P)), 24)
Equals(LengthOf(Line(Z, P)), 8)
PointLiesOnLine(P, Line(Z, X))
PointLiesOnLine(P, Line(Y, W))
```

原始 text logic forms：

```text
Kite(W,X,Y,Z)
Find(LengthOf(Line(Z,Y)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(X, P)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "X"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(W, P)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "W"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(Y, P)), 24)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "Y"], "value": "24", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(Z, P)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "Z"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(P, Line(Z, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(P, Line(Y, W))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1498（train）

题面：<image>Find the angle measure of $\angle 1$.

参考答案：`142`

原图：[打开](<../../data/project3_perception_prototype/images/1498.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(F, E, G)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(A, F, I)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(G, E, C)), 52)
Equals(MeasureOf(Angle(C, F, A)), 38)
Equals(MeasureOf(Angle(D, E, F)), MeasureOf(angle 4))
Equals(MeasureOf(Angle(H, D, B)), MeasureOf(angle 3))
PointLiesOnLine(D, Line(A, B))
PointLiesOnLine(F, Line(A, B))
PointLiesOnLine(D, Line(A, F))
PointLiesOnLine(F, Line(B, D))
PointLiesOnLine(E, Line(D, G))
PointLiesOnLine(E, Line(F, C))
PointLiesOnLine(E, Line(C, I))
PointLiesOnLine(F, Line(C, I))
PointLiesOnLine(D, Line(E, H))
PointLiesOnLine(F, Line(E, I))
PointLiesOnLine(D, Line(G, H))
PointLiesOnLine(E, Line(G, H))
Perpendicular(Line(D, F), Line(D, E))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(1)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(F, E, G)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, F, I)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(G, E, C)), 52)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "E", "G"], "value": "52", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, F, A)), 38)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "F", "C"], "value": "38", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(D, E, F)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(H, D, B)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(A, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(D, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(F, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(C, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(C, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(E, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(E, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(D, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(G, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(D, F), Line(D, E))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["D", "E"], ["D", "F"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 598（train）

题面：<image>Find y.

参考答案：`4 \sqrt { 6 }`

原图：[打开](<../../data/project3_perception_prototype/images/598.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(D, E, A)), 45)
Equals(LengthOf(Line(A, G)), x)
Equals(LengthOf(Line(A, E)), 8)
Equals(LengthOf(Line(G, D)), y)
Equals(MeasureOf(Angle(A, D, E)), 30)
PointLiesOnLine(G, Line(D, E))
Perpendicular(Line(G, A), Line(G, D))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(D, E, A)), 45)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "E", "D"], "value": "45", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, G)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, E)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "E"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(G, D)), y)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, D, E)), 30)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "D", "E"], "value": "30", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(G, Line(D, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(G, A), Line(G, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "G"], ["D", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 860（train）

题面：<image>If PR || WX, WX = 10, XY = 6, WY = 8, RY = 5, and PS = 3, find SY

参考答案：`4`

原图：[打开](<../../data/project3_perception_prototype/images/860.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(S, Line(W, Y))
PointLiesOnLine(S, Line(Q, P))
PointLiesOnLine(Q, Line(W, X))
PointLiesOnLine(B, Line(Y, X))
PointLiesOnLine(B, Line(Q, R))
PointLiesOnLine(B, Line(Q, R))
PointLiesOnLine(Y, Line(P, R))
Perpendicular(Line(C, P), Line(Y, S))
Perpendicular(Line(Y, S), Line(Y, B))
Perpendicular(Line(C, Q), Line(Q, B))
```

原始 text logic forms：

```text
Parallel(Line(P,R),Line(W,X))
Equals(LengthOf(Line(W,X)),10)
Equals(LengthOf(Line(X,Y)),6)
Equals(LengthOf(Line(W,Y)),8)
Equals(LengthOf(Line(R,Y)),5)
Equals(LengthOf(Line(P,S)),3)
Find(LengthOf(Line(S,Y)))
```

有限 schema 结果：

- `PointLiesOnLine(S, Line(W, Y))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(S, Line(Q, P))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(W, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(Y, X))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(Q, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(Q, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Y, Line(P, R))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(C, P), Line(Y, S))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["C", "P"], ["S", "Y"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(Y, S), Line(Y, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "Y"], ["S", "Y"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(C, Q), Line(Q, B))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "Q"], ["C", "Q"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1497（train）

题面：<image>In $\triangle CDF$, $K$ is the centroid and $DK=16$. Find $FG$.

参考答案：`18`

原图：[打开](<../../data/project3_perception_prototype/images/1497.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(F, K)), 12)
Equals(LengthOf(Line(D, G)), 9)
PointLiesOnLine(K, Line(H, D))
PointLiesOnLine(J, Line(D, F))
PointLiesOnLine(G, Line(D, C))
PointLiesOnLine(H, Line(F, C))
PointLiesOnLine(K, Line(F, G))
PointLiesOnLine(K, Line(C, J))
```

原始 text logic forms：

```text
Triangle(C,D,F)
IsCentroidOf(Point(K),Triangle(C,D,F))
Equals(LengthOf(Line(D,K)),16)
Find(LengthOf(Line(F,G)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(F, K)), 12)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["F", "K"], "value": "12", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(D, G)), 9)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["D", "G"], "value": "9", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(K, Line(H, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(D, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(G, Line(D, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(H, Line(F, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(F, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(C, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 562（train）

题面：<image>Find y

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/562.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, C)), 6)
Equals(LengthOf(Line(A, C)), 8)
Equals(LengthOf(Line(S, A)), z)
Equals(LengthOf(Line(S, B)), x)
PointLiesOnLine(C, Line(S, B))
Perpendicular(Line(S, C), Line(A, C))
Perpendicular(Line(A, B), Line(S, A))
```

原始 text logic forms：

```text
Find(y)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, C)), 6)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "6", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(S, A)), z)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(S, B)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(C, Line(S, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(S, C), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["C", "S"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(A, B), Line(S, A))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["A", "S"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1480（train）

题面：<image>Use parallelogram MNPR to find $z$

参考答案：`6.1`

原图：[打开](<../../data/project3_perception_prototype/images/1480.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(P, Q)), 11.1)
Equals(MeasureOf(Angle(N, Q, P)), 83)
Equals(LengthOf(Line(R, P)), 20)
Equals(LengthOf(Line(M, N)), 3x-4)
Equals(LengthOf(Line(P, N)), 2y+5)
Equals(LengthOf(Line(N, Q)), 15.4)
Equals(MeasureOf(Angle(Q, N, M)), 33)
Equals(LengthOf(Line(M, N)), 3x-4)
Equals(LengthOf(Line(R, Q)), 3z-3)
Equals(MeasureOf(Angle(M, R, Q)), 38)
Equals(LengthOf(Line(R, M)), 17.9)
PointLiesOnLine(Q, Line(R, N))
PointLiesOnLine(Q, Line(P, M))
```

原始 text logic forms：

```text
Parallelogram(M,N,P,R)
Find(z)
```

有限 schema 结果：

- `Equals(LengthOf(Line(P, Q)), 11.1)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "Q"], "value": "111/10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(N, Q, P)), 83)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["N", "Q", "P"], "value": "83", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, P)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["P", "R"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(M, N)), 3x-4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(P, N)), 2y+5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(N, Q)), 15.4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["N", "Q"], "value": "77/5", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(Q, N, M)), 33)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["M", "N", "Q"], "value": "33", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(M, N)), 3x-4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(R, Q)), 3z-3)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(M, R, Q)), 38)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["M", "R", "Q"], "value": "38", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(R, M)), 17.9)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["M", "R"], "value": "179/10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(Q, Line(R, N))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(Q, Line(P, M))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 481（train）

题面：<image>Find $m \angle R$.

参考答案：`32`

原图：[打开](<../../data/project3_perception_prototype/images/481.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(R, S, Q)), 5x+4)
Equals(MeasureOf(Angle(S, Q, T)), 32)
Equals(MeasureOf(Angle(R, T, Q)), 6x-2)
PointLiesOnLine(A, Line(S, Q))
PointLiesOnLine(A, Line(R, T))
PointLiesOnCircle(S, Circle(C, radius_7_0))
PointLiesOnCircle(R, Circle(C, radius_7_0))
PointLiesOnCircle(T, Circle(C, radius_7_0))
PointLiesOnCircle(Q, Circle(C, radius_7_0))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(R)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(R, S, Q)), 5x+4)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(S, Q, T)), 32)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["S", "Q", "T"], "value": "32", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(R, T, Q)), 6x-2)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(S, Q))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(R, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(S, Circle(C, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(R, Circle(C, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(T, Circle(C, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(Q, Circle(C, radius_7_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1057（train）

题面：<image>What is the value of x in the figure?

参考答案：`26`

原图：[打开](<../../data/project3_perception_prototype/images/1057.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(C, X, A)), 3x)
Equals(MeasureOf(Angle(A, X, B)), 7x+10)
Equals(MeasureOf(Angle(B, X, C)), 90)
PointLiesOnCircle(A, Circle(X, radius_0_0))
PointLiesOnCircle(B, Circle(X, radius_0_0))
PointLiesOnCircle(C, Circle(X, radius_0_0))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(C, X, A)), 3x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, X, B)), 7x+10)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, X, C)), 90)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "X", "C"], "value": "90", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(A, Circle(X, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(X, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(X, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1008（train）

题面：<image>In $\triangle A B C, C D$ is an altitude and $m \angle A C B=90^{\circ}$ If $A D=12$ and $B D=3,$ find $A C$ to the nearest tenth. 

参考答案：`13.4`

原图：[打开](<../../data/project3_perception_prototype/images/1008.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, D)), 12)
Equals(LengthOf(Line(D, B)), 3)
PointLiesOnLine(D, Line(A, B))
```

原始 text logic forms：

```text
Triangle(A,B,C)
Equals(Line(C,D),AltitudeOf(Triangle(A,B,C)))
Equals(MeasureOf(Angle(A,C,B)),90)
Equals(LengthOf(Line(A,D)),12)
Equals(LengthOf(Line(B,D)),3)
Find(LengthOf(Line(A,C)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, D)), 12)` → `text_explicit`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "12", "unit": "unspecified_source_unit"}`；same_normalized_fact_in_official_text_annotation
- `Equals(LengthOf(Line(D, B)), 3)` → `text_explicit`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "3", "unit": "unspecified_source_unit"}`；same_normalized_fact_in_official_text_annotation
- `PointLiesOnLine(D, Line(A, B))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 841（train）

题面：<image>Find $m \angle 5$.

参考答案：`55`

原图：[打开](<../../data/project3_perception_prototype/images/841.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(C, F, I)), MeasureOf(angle 4))
Equals(MeasureOf(Angle(A, L, C)), 35)
Equals(MeasureOf(Angle(C, B, G)), MeasureOf(angle 1))
Equals(MeasureOf(Angle(G, B, E)), MeasureOf(angle 2))
Equals(MeasureOf(Angle(E, K, I)), MeasureOf(angle 3))
Equals(MeasureOf(Angle(H, C, F)), MeasureOf(angle 6))
Equals(MeasureOf(Angle(L, C, A)), MeasureOf(angle 5))
Equals(MeasureOf(Angle(L, D, G)), 25)
Equals(MeasureOf(Angle(L, E, G)), 51)
Equals(MeasureOf(Angle(G, C, K)), 28)
PointLiesOnLine(H, Line(A, C))
PointLiesOnLine(B, Line(A, K))
PointLiesOnLine(I, Line(B, D))
PointLiesOnLine(K, Line(B, D))
PointLiesOnLine(A, Line(B, F))
PointLiesOnLine(K, Line(B, I))
PointLiesOnLine(I, Line(B, J))
PointLiesOnLine(K, Line(B, J))
PointLiesOnLine(E, Line(C, D))
PointLiesOnLine(A, Line(F, K))
PointLiesOnLine(B, Line(F, K))
PointLiesOnLine(A, Line(F, L))
PointLiesOnLine(J, Line(I, D))
PointLiesOnLine(B, Line(I, L))
PointLiesOnLine(K, Line(I, L))
PointLiesOnLine(I, Line(J, K))
PointLiesOnLine(B, Line(J, L))
PointLiesOnLine(I, Line(J, L))
PointLiesOnLine(K, Line(J, L))
PointLiesOnLine(I, Line(K, D))
PointLiesOnLine(J, Line(K, D))
PointLiesOnLine(B, Line(K, L))
PointLiesOnLine(B, Line(L, D))
PointLiesOnLine(I, Line(L, D))
PointLiesOnLine(K, Line(L, D))
Perpendicular(Line(A, L), Line(A, H))
Perpendicular(Line(B, G), Line(C, G))
Perpendicular(Line(B, C), Line(C, F))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(5)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(C, F, I)), MeasureOf(angle 4))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(A, L, C)), 35)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "L", "C"], "value": "35", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, B, G)), MeasureOf(angle 1))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(G, B, E)), MeasureOf(angle 2))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(E, K, I)), MeasureOf(angle 3))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(H, C, F)), MeasureOf(angle 6))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(L, C, A)), MeasureOf(angle 5))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(L, D, G)), 25)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["G", "D", "L"], "value": "25", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(L, E, G)), 51)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["G", "E", "L"], "value": "51", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(G, C, K)), 28)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["G", "C", "K"], "value": "28", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(H, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(A, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(B, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(B, I))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(B, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(B, J))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(C, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(F, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(F, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(F, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(I, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(I, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(I, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(J, K))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(J, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(J, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(J, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(K, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(J, Line(K, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(K, L))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(L, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(I, Line(L, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(K, Line(L, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, L), Line(A, H))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "H"], ["A", "L"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, G), Line(C, G))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "G"], ["C", "G"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(B, C), Line(C, F))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["B", "C"], ["C", "F"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2004（train）

题面：<image>Find the area of the blue region.

参考答案：`17.5`

原图：[打开](<../../data/project3_perception_prototype/images/2004.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(DiameterOf(Circle(A))), 10)
Equals(MeasureOf(Angle(B, A, D)), 80)
Equals(MeasureOf(Angle(E, A, B)), 64)
Equals(MeasureOf(Angle(L, A, E)), 40)
Equals(MeasureOf(Angle(D, A, C)), 112)
Equals(MeasureOf(Angle(C, A, L)), 64)
PointLiesOnCircle(L, Circle(A, radius_1_0))
PointLiesOnCircle(B, Circle(A, radius_1_0))
PointLiesOnCircle(C, Circle(A, radius_1_0))
PointLiesOnCircle(D, Circle(A, radius_1_0))
PointLiesOnCircle(E, Circle(A, radius_1_0))
```

原始 text logic forms：

```text
Find(AreaOf(Blue(Shape($))))
```

有限 schema 结果：

- `Equals(LengthOf(DiameterOf(Circle(A))), 10)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, A, D)), 80)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "A", "D"], "value": "80", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(E, A, B)), 64)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["B", "A", "E"], "value": "64", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(L, A, E)), 40)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["E", "A", "L"], "value": "40", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(D, A, C)), 112)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "A", "D"], "value": "112", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, A, L)), 64)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "A", "L"], "value": "64", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnCircle(L, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(A, radius_1_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1243（train）

题面：<image>Find $x$ so that the quadrilateral is a parallelogram

参考答案：`2`

原图：[打开](<../../data/project3_perception_prototype/images/1243.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(B, C)), 2x+7)
Equals(MeasureOf(Angle(Y, B, C)), 2y-5)
Equals(MeasureOf(Angle(B, Y, A)), 2x+21)
Equals(LengthOf(Line(Y, A)), x+9)
```

原始 text logic forms：

```text
Parallelogram($)
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(B, C)), 2x+7)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(Y, B, C)), 2y-5)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, Y, A)), 2x+21)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(Y, A)), x+9)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 451（train）

题面：<image>Find the perimeter of the figure. Round to the nearest hundredth, if necessary.

参考答案：`9.2`

原图：[打开](<../../data/project3_perception_prototype/images/451.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), 3)
Equals(MeasureOf(Angle(A, N, B)), 62)
Equals(LengthOf(Line(A, B)), LengthOf(Line(D, N)))
Equals(LengthOf(Line(A, D)), LengthOf(Line(B, N)))
Perpendicular(Line(A, D), Line(N, D))
Perpendicular(Line(A, B), Line(B, N))

```

原始 text logic forms：

```text
Find(PerimeterOf(Shape($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(A, N, B)), 62)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["A", "N", "B"], "value": "62", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), LengthOf(Line(D, N)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, D)), LengthOf(Line(B, N)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(A, D), Line(N, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "D"], ["D", "N"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Perpendicular(Line(A, B), Line(B, N))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "B"], ["B", "N"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2010（train）

题面：<image>Rhombus $QRST$ has an area of 137.9 square meters. If $RT$ is 12.2 meters, find $QS$.

参考答案：`22.6`

原图：[打开](<../../data/project3_perception_prototype/images/2010.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(B, Line(Q, S))
PointLiesOnLine(B, Line(R, T))
```

原始 text logic forms：

```text
Equals(AreaOf(Rhombus(Q,R,S,T)),137.9)
Equals(Line(R,T),12.2)
Find(LengthOf(Line(Q,S)))
```

有限 schema 结果：

- `PointLiesOnLine(B, Line(Q, S))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(R, T))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1285（train）

题面：<image>Find $b$.

参考答案：`18`

原图：[打开](<../../data/project3_perception_prototype/images/1285.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, D)), 27)
Equals(LengthOf(Line(C, A)), b)
Equals(LengthOf(Line(B, D)), 15)
Equals(LengthOf(Line(C, B)), 28)
PointLiesOnLine(A, Line(B, C))
Equals(MeasureOf(Angle(B, D, A)), MeasureOf(Angle(A, D, C)))
```

原始 text logic forms：

```text
Find(b)
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, D)), 27)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "27", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, A)), b)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, D)), 15)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "D"], "value": "15", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, B)), 28)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "C"], "value": "28", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(A, Line(B, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(B, D, A)), MeasureOf(Angle(A, D, C)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1743（train）

题面：<image>Find $x$ so that $ m \parallel n $.

参考答案：`- 8`

原图：[打开](<../../data/project3_perception_prototype/images/1743.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(G, E, I)), 7x+100)
Equals(MeasureOf(Angle(D, F, E)), 4 - 5x)
PointLiesOnLine(F, Line(A, E))
PointLiesOnLine(E, Line(A, G))
PointLiesOnLine(F, Line(A, G))
PointLiesOnLine(E, Line(F, G))
PointLiesOnLine(E, Line(I, C))
PointLiesOnLine(F, Line(D, H))
```

原始 text logic forms：

```text
Parallel(Line(m),Line(n))
Find(x)
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(G, E, I)), 7x+100)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(D, F, E)), 4 - 5x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(A, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(A, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(F, G))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(E, Line(I, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(F, Line(D, H))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 187（train）

题面：<image>Find the area of the shaded region. Round to the nearest tenth.

参考答案：`7.9`

原图：[打开](<../../data/project3_perception_prototype/images/187.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, F)), 3)
Equals(MeasureOf(Angle(E, A, D)), 130)
PointLiesOnLine(A, Line(B, D))
PointLiesOnLine(A, Line(C, E))
PointLiesOnCircle(B, Circle(A, radius_0_0))
Equals(MeasureOf(Angle(C, A, D)), MeasureOf(Angle(B, A, E)))
PointLiesOnCircle(C, Circle(A, radius_0_0))
PointLiesOnCircle(D, Circle(A, radius_0_0))
PointLiesOnCircle(E, Circle(A, radius_0_0))
```

原始 text logic forms：

```text
Find(AreaOf(Shaded(Shape($))))
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, F)), 3)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "F"], "value": "3", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(E, A, D)), 130)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["D", "A", "E"], "value": "130", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(A, Line(B, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(A, Line(C, E))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(B, Circle(A, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(C, A, D)), MeasureOf(Angle(B, A, E)))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(C, Circle(A, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(D, Circle(A, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(E, Circle(A, radius_0_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1090（train）

题面：<image>Find x.

参考答案：`\frac { 4 } { 9 } \sqrt { 3 }`

原图：[打开](<../../data/project3_perception_prototype/images/1090.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, B)), \frac{8}{9})
Equals(LengthOf(Line(B, C)), \frac{4}{9})
Equals(LengthOf(Line(A, C)), x)
Perpendicular(Line(B, C), Line(A, C))
```

原始 text logic forms：

```text
Find(x)
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, B)), \frac{8}{9})` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(B, C)), \frac{4}{9})` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(LengthOf(Line(A, C)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(B, C), Line(A, C))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["A", "C"], ["B", "C"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 2050（train）

题面：<image>Find the area of the figure. Round to the nearest tenth if necessary.

参考答案：`239`

原图：[打开](<../../data/project3_perception_prototype/images/2050.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, F)), 20)
Equals(LengthOf(Line(F, B)), 7)
Equals(LengthOf(Line(A, C)), 16)
Equals(LengthOf(Line(C, D)), 11)
```

原始 text logic forms：

```text
Find(AreaOf(Shape($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, F)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "F"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(F, B)), 7)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["B", "F"], "value": "7", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, C)), 16)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "C"], "value": "16", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(C, D)), 11)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "D"], "value": "11", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1041（train）

题面：<image>Find $m\angle K$

参考答案：`62`

原图：[打开](<../../data/project3_perception_prototype/images/1041.png>)

原始 diagram logic forms：

```text
Equals(MeasureOf(Angle(J, M, L)), 2x-8)
Equals(MeasureOf(Angle(M, J, K)), 3x-6)
Equals(MeasureOf(Angle(J, K, L)), x+10)
Equals(MeasureOf(Angle(K, L, M)), x)
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(K)))
```

有限 schema 结果：

- `Equals(MeasureOf(Angle(J, M, L)), 2x-8)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(M, J, K)), 3x-6)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(J, K, L)), x+10)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Equals(MeasureOf(Angle(K, L, M)), x)` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 771（train）

题面：<image>Find the area of the parallelogram. Round to the nearest tenth if necessary.

参考答案：`288`

原图：[打开](<../../data/project3_perception_prototype/images/771.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(C, E)), 16)
Equals(LengthOf(Line(A, B)), 20)
Equals(LengthOf(Line(A, D)), 18)
PointLiesOnLine(E, Line(A, D))
Perpendicular(Line(C, E), Line(E, D))
```

原始 text logic forms：

```text
Find(AreaOf(Parallelogram($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(C, E)), 16)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "E"], "value": "16", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, B)), 20)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "B"], "value": "20", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, D)), 18)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "18", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(A, D))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Perpendicular(Line(C, E), Line(E, D))` → `visual_candidate`；规范事实 `{"relation": "Perpendicular", "entities": [["C", "E"], ["D", "E"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 16（train）

题面：<image>If $AD=27,AB=8$, and $AE=12$, find $BC$.

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/16.png>)

原始 diagram logic forms：

```text
PointLiesOnLine(E, Line(D, A))
PointLiesOnLine(B, Line(A, C))
Parallel(Line(E, B), Line(D, C))
```

原始 text logic forms：

```text
Equals(LengthOf(Line(A,D)),27)
Equals(LengthOf(Line(A,B)),8)
Equals(LengthOf(Line(A,E)),12)
Find(LengthOf(Line(B,C)))
```

有限 schema 结果：

- `PointLiesOnLine(E, Line(D, A))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnLine(B, Line(A, C))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `Parallel(Line(E, B), Line(D, C))` → `visual_candidate`；规范事实 `{"relation": "Parallel", "entities": [["B", "E"], ["C", "D"]], "value": "", "unit": ""}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。

## 原始 ID 1860（train）

题面：<image>Find the area of the figure to the nearest tenth.

参考答案：`87.5`

原图：[打开](<../../data/project3_perception_prototype/images/1860.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(A, D)), 8)
Equals(LengthOf(Line(A, E)), 4)
Equals(MeasureOf(Angle(C, F, E)), 60)
Equals(LengthOf(Line(F, C)), 10)
PointLiesOnLine(E, Line(A, F))
PointLiesOnCircle(A, Circle(E, radius_4_0))
PointLiesOnCircle(F, Circle(E, radius_4_0))
PointLiesOnCircle(G, Circle(E, radius_4_0))
```

原始 text logic forms：

```text
Find(AreaOf(Shape($)))
```

有限 schema 结果：

- `Equals(LengthOf(Line(A, D)), 8)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "D"], "value": "8", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(A, E)), 4)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["A", "E"], "value": "4", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(MeasureOf(Angle(C, F, E)), 60)` → `visual_candidate`；规范事实 `{"relation": "Angle", "entities": ["C", "F", "E"], "value": "60", "unit": "deg"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `Equals(LengthOf(Line(F, C)), 10)` → `visual_candidate`；规范事实 `{"relation": "Length", "entities": ["C", "F"], "value": "10", "unit": "unspecified_source_unit"}`；not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review
- `PointLiesOnLine(E, Line(A, F))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(A, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(F, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source
- `PointLiesOnCircle(G, Circle(E, radius_4_0))` → `uncertain`；规范事实 `null`；outside_finite_schema_or_invalid_source

人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。
