# 30 题原图核查工作单（全部 pending）

本工作单包含真实源图，但尚未开展人工或 AI 看图复核。请逐项填写 JSONL，不以模型自动标签替代签字。

## 原始 ID 863（train）

题面：<image>What is the length of $R T ?$

参考答案：`5 \sqrt { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/863.png>)

![ID 863 原图](<../../data/project3_perception_prototype/images/863.png>)

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

## 原始 ID 1656（train）

题面：<image>Find the measure of the altitude drawn to the hypotenuse.

参考答案：`\sqrt { 26 }`

原图：[打开](<../../data/project3_perception_prototype/images/1656.png>)

![ID 1656 原图](<../../data/project3_perception_prototype/images/1656.png>)

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

## 原始 ID 867（train）

题面：<image>Find $m \angle MRP$.

参考答案：`60`

原图：[打开](<../../data/project3_perception_prototype/images/867.png>)

![ID 867 原图](<../../data/project3_perception_prototype/images/867.png>)

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

## 原始 ID 191（train）

题面：<image>$J$ is the incenter of $\angle ABC$. Find $m \angle JAC$.

参考答案：`24`

原图：[打开](<../../data/project3_perception_prototype/images/191.png>)

![ID 191 原图](<../../data/project3_perception_prototype/images/191.png>)

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

## 原始 ID 1704（train）

题面：<image>Find $x$.

参考答案：`3`

原图：[打开](<../../data/project3_perception_prototype/images/1704.png>)

![ID 1704 原图](<../../data/project3_perception_prototype/images/1704.png>)

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

## 原始 ID 1025（train）

题面：<image>Find $QR$ if $\triangle QRS$ is an equilateral triangle.

参考答案：`2`

原图：[打开](<../../data/project3_perception_prototype/images/1025.png>)

![ID 1025 原图](<../../data/project3_perception_prototype/images/1025.png>)

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

## 原始 ID 467（train）

题面：<image>Find y.

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/467.png>)

![ID 467 原图](<../../data/project3_perception_prototype/images/467.png>)

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

## 原始 ID 2044（train）

题面：<image>Find x.

参考答案：`24 \sqrt { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/2044.png>)

![ID 2044 原图](<../../data/project3_perception_prototype/images/2044.png>)

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

## 原始 ID 1904（train）

题面：<image>$H$ is the incenter of $\triangle ABC$. Find $BD$.

参考答案：`7 \sqrt 3`

原图：[打开](<../../data/project3_perception_prototype/images/1904.png>)

![ID 1904 原图](<../../data/project3_perception_prototype/images/1904.png>)

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

## 原始 ID 2099（train）

题面：<image>Find x.

参考答案：`13 \sqrt { 2 }`

原图：[打开](<../../data/project3_perception_prototype/images/2099.png>)

![ID 2099 原图](<../../data/project3_perception_prototype/images/2099.png>)

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

## 原始 ID 967（train）

题面：<image>Find $PW$, if $XZ = 18$ and $PY = 3$

参考答案：`15`

原图：[打开](<../../data/project3_perception_prototype/images/967.png>)

![ID 967 原图](<../../data/project3_perception_prototype/images/967.png>)

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

## 原始 ID 638（train）

题面：<image>Find x

参考答案：`7 \sqrt { 3 }`

原图：[打开](<../../data/project3_perception_prototype/images/638.png>)

![ID 638 原图](<../../data/project3_perception_prototype/images/638.png>)

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

## 原始 ID 924（train）

题面：<image>Find x

参考答案：`3`

原图：[打开](<../../data/project3_perception_prototype/images/924.png>)

![ID 924 原图](<../../data/project3_perception_prototype/images/924.png>)

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

## 原始 ID 943（train）

题面：<image>Find $XA$.

参考答案：`4`

原图：[打开](<../../data/project3_perception_prototype/images/943.png>)

![ID 943 原图](<../../data/project3_perception_prototype/images/943.png>)

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

## 原始 ID 990（train）

题面：<image>Find y.

参考答案：`3 \sqrt { 13 }`

原图：[打开](<../../data/project3_perception_prototype/images/990.png>)

![ID 990 原图](<../../data/project3_perception_prototype/images/990.png>)

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

## 原始 ID 1647（train）

题面：<image>Find the area of the figure. Round to the nearest tenth.

参考答案：`87.5`

原图：[打开](<../../data/project3_perception_prototype/images/1647.png>)

![ID 1647 原图](<../../data/project3_perception_prototype/images/1647.png>)

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

## 原始 ID 538（train）

题面：<image>Find the area of the parallelogram. Round to the nearest tenth if necessary.

参考答案：`259.8`

原图：[打开](<../../data/project3_perception_prototype/images/538.png>)

![ID 538 原图](<../../data/project3_perception_prototype/images/538.png>)

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

## 原始 ID 1822（train）

题面：<image>Find x.

参考答案：`0.5`

原图：[打开](<../../data/project3_perception_prototype/images/1822.png>)

![ID 1822 原图](<../../data/project3_perception_prototype/images/1822.png>)

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

## 原始 ID 272（train）

题面：<image>$\odot  C \cong \odot D$, Find $x$.

参考答案：`27`

原图：[打开](<../../data/project3_perception_prototype/images/272.png>)

![ID 272 原图](<../../data/project3_perception_prototype/images/272.png>)

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

## 原始 ID 1163（train）

题面：<image>A square with 5-centimeter sides is inscribed in a circle. What is the circumference of the circle? Round your answer to the nearest

tenth of a centimeter.

参考答案：`22.2`

原图：[打开](<../../data/project3_perception_prototype/images/1163.png>)

![ID 1163 原图](<../../data/project3_perception_prototype/images/1163.png>)

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

## 原始 ID 888（train）

题面：<image>In $\odot S$, find $PR$.

参考答案：`12`

原图：[打开](<../../data/project3_perception_prototype/images/888.png>)

![ID 888 原图](<../../data/project3_perception_prototype/images/888.png>)

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

## 原始 ID 562（train）

题面：<image>Find y

参考答案：`10`

原图：[打开](<../../data/project3_perception_prototype/images/562.png>)

![ID 562 原图](<../../data/project3_perception_prototype/images/562.png>)

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

## 原始 ID 725（train）

题面：<image>Find $CP$.

参考答案：`8`

原图：[打开](<../../data/project3_perception_prototype/images/725.png>)

![ID 725 原图](<../../data/project3_perception_prototype/images/725.png>)

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

## 原始 ID 36（train）

题面：<image>Find $x$.

参考答案：`135`

原图：[打开](<../../data/project3_perception_prototype/images/36.png>)

![ID 36 原图](<../../data/project3_perception_prototype/images/36.png>)

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

## 原始 ID 1749（train）

题面：<image>$\overline{XY}$ and $\overline{XZ}$ are midsegments of $\triangle RST$. Find $XZ$.

参考答案：`6.5`

原图：[打开](<../../data/project3_perception_prototype/images/1749.png>)

![ID 1749 原图](<../../data/project3_perception_prototype/images/1749.png>)

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

## 原始 ID 1007（train）

题面：<image>In the figure, $m ∠ 12 = 64$. Find the measure of $ \angle 8$.

参考答案：`116`

原图：[打开](<../../data/project3_perception_prototype/images/1007.png>)

![ID 1007 原图](<../../data/project3_perception_prototype/images/1007.png>)

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

## 原始 ID 304（train）

题面：<image>$\overline{JH}, \overline{JP},$ and $\overline{PH}$ are midsegments of $\triangle KLM$. Find $x$.

参考答案：`1.35`

原图：[打开](<../../data/project3_perception_prototype/images/304.png>)

![ID 304 原图](<../../data/project3_perception_prototype/images/304.png>)

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

## 原始 ID 14（train）

题面：<image>Find $x$.

参考答案：`48`

原图：[打开](<../../data/project3_perception_prototype/images/14.png>)

![ID 14 原图](<../../data/project3_perception_prototype/images/14.png>)

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

## 原始 ID 1743（train）

题面：<image>Find $x$ so that $ m \parallel n $.

参考答案：`- 8`

原图：[打开](<../../data/project3_perception_prototype/images/1743.png>)

![ID 1743 原图](<../../data/project3_perception_prototype/images/1743.png>)

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

## 原始 ID 1289（train）

题面：<image>Find x.

参考答案：`6`

原图：[打开](<../../data/project3_perception_prototype/images/1289.png>)

![ID 1289 原图](<../../data/project3_perception_prototype/images/1289.png>)

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
