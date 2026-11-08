# 30 题包装记录与原始标注关联核查（全部 pending）

`wrapper_locator` 是 Geometry3K 包装 parquet 的 split:行偏移定位；包装不含原始官方 ID，不能将行偏移当作官方 ID。`intergps_original_id` 才是 InterGPS 原始 data.json ID。

原图为真实 InterGPS train 原图；下面展示的是待审工作单，不代表已完成人工或 AI 复核。

## InterGPS 原始 ID 863 / Geometry3K 包装定位 train:815

原始源定位：`train.zip::train/863/data.json`；题面：<image>What is the length of $R T ?$

参考答案：`5 \sqrt { 2 }`

[打开原图](<../../data/project3_perception_prototype/images/863.png>)

![原图 863](<../../data/project3_perception_prototype/images/863.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1656 / Geometry3K 包装定位 train:335

原始源定位：`train.zip::train/1656/data.json`；题面：<image>Find the measure of the altitude drawn to the hypotenuse.

参考答案：`\sqrt { 26 }`

[打开原图](<../../data/project3_perception_prototype/images/1656.png>)

![原图 1656](<../../data/project3_perception_prototype/images/1656.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 867 / Geometry3K 包装定位 train:1820

原始源定位：`train.zip::train/867/data.json`；题面：<image>Find $m \angle MRP$.

参考答案：`60`

[打开原图](<../../data/project3_perception_prototype/images/867.png>)

![原图 867](<../../data/project3_perception_prototype/images/867.png>)

原始 diagram logic forms：

```text
Equals(LengthOf(Line(M, P)), LengthOf(Line(M, R)))
Equals(LengthOf(Line(M, R)), LengthOf(Line(R, P)))
```

原始 text logic forms：

```text
Find(MeasureOf(Angle(M,R,P)))
```

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 191 / Geometry3K 包装定位 train:619

原始源定位：`train.zip::train/191/data.json`；题面：<image>$J$ is the incenter of $\angle ABC$. Find $m \angle JAC$.

参考答案：`24`

[打开原图](<../../data/project3_perception_prototype/images/191.png>)

![原图 191](<../../data/project3_perception_prototype/images/191.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1704 / Geometry3K 包装定位 train:2038

原始源定位：`train.zip::train/1704/data.json`；题面：<image>Find $x$.

参考答案：`3`

[打开原图](<../../data/project3_perception_prototype/images/1704.png>)

![原图 1704](<../../data/project3_perception_prototype/images/1704.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1025 / Geometry3K 包装定位 train:1216

原始源定位：`train.zip::train/1025/data.json`；题面：<image>Find $QR$ if $\triangle QRS$ is an equilateral triangle.

参考答案：`2`

[打开原图](<../../data/project3_perception_prototype/images/1025.png>)

![原图 1025](<../../data/project3_perception_prototype/images/1025.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 467 / Geometry3K 包装定位 train:2078

原始源定位：`train.zip::train/467/data.json`；题面：<image>Find y.

参考答案：`10`

[打开原图](<../../data/project3_perception_prototype/images/467.png>)

![原图 467](<../../data/project3_perception_prototype/images/467.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 2044 / Geometry3K 包装定位 train:33

原始源定位：`train.zip::train/2044/data.json`；题面：<image>Find x.

参考答案：`24 \sqrt { 2 }`

[打开原图](<../../data/project3_perception_prototype/images/2044.png>)

![原图 2044](<../../data/project3_perception_prototype/images/2044.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1904 / Geometry3K 包装定位 train:1793

原始源定位：`train.zip::train/1904/data.json`；题面：<image>$H$ is the incenter of $\triangle ABC$. Find $BD$.

参考答案：`7 \sqrt 3`

[打开原图](<../../data/project3_perception_prototype/images/1904.png>)

![原图 1904](<../../data/project3_perception_prototype/images/1904.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 2099 / Geometry3K 包装定位 train:768

原始源定位：`train.zip::train/2099/data.json`；题面：<image>Find x.

参考答案：`13 \sqrt { 2 }`

[打开原图](<../../data/project3_perception_prototype/images/2099.png>)

![原图 2099](<../../data/project3_perception_prototype/images/2099.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 967 / Geometry3K 包装定位 train:1631

原始源定位：`train.zip::train/967/data.json`；题面：<image>Find $PW$, if $XZ = 18$ and $PY = 3$

参考答案：`15`

[打开原图](<../../data/project3_perception_prototype/images/967.png>)

![原图 967](<../../data/project3_perception_prototype/images/967.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 638 / Geometry3K 包装定位 train:660

原始源定位：`train.zip::train/638/data.json`；题面：<image>Find x

参考答案：`7 \sqrt { 3 }`

[打开原图](<../../data/project3_perception_prototype/images/638.png>)

![原图 638](<../../data/project3_perception_prototype/images/638.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 924 / Geometry3K 包装定位 train:641

原始源定位：`train.zip::train/924/data.json`；题面：<image>Find x

参考答案：`3`

[打开原图](<../../data/project3_perception_prototype/images/924.png>)

![原图 924](<../../data/project3_perception_prototype/images/924.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 943 / Geometry3K 包装定位 train:1872

原始源定位：`train.zip::train/943/data.json`；题面：<image>Find $XA$.

参考答案：`4`

[打开原图](<../../data/project3_perception_prototype/images/943.png>)

![原图 943](<../../data/project3_perception_prototype/images/943.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 990 / Geometry3K 包装定位 train:338

原始源定位：`train.zip::train/990/data.json`；题面：<image>Find y.

参考答案：`3 \sqrt { 13 }`

[打开原图](<../../data/project3_perception_prototype/images/990.png>)

![原图 990](<../../data/project3_perception_prototype/images/990.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1647 / Geometry3K 包装定位 train:1515

原始源定位：`train.zip::train/1647/data.json`；题面：<image>Find the area of the figure. Round to the nearest tenth.

参考答案：`87.5`

[打开原图](<../../data/project3_perception_prototype/images/1647.png>)

![原图 1647](<../../data/project3_perception_prototype/images/1647.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 538 / Geometry3K 包装定位 train:929

原始源定位：`train.zip::train/538/data.json`；题面：<image>Find the area of the parallelogram. Round to the nearest tenth if necessary.

参考答案：`259.8`

[打开原图](<../../data/project3_perception_prototype/images/538.png>)

![原图 538](<../../data/project3_perception_prototype/images/538.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1822 / Geometry3K 包装定位 train:809

原始源定位：`train.zip::train/1822/data.json`；题面：<image>Find x.

参考答案：`0.5`

[打开原图](<../../data/project3_perception_prototype/images/1822.png>)

![原图 1822](<../../data/project3_perception_prototype/images/1822.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 272 / Geometry3K 包装定位 train:1305

原始源定位：`train.zip::train/272/data.json`；题面：<image>$\odot  C \cong \odot D$, Find $x$.

参考答案：`27`

[打开原图](<../../data/project3_perception_prototype/images/272.png>)

![原图 272](<../../data/project3_perception_prototype/images/272.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1163 / Geometry3K 包装定位 train:1223

原始源定位：`train.zip::train/1163/data.json`；题面：<image>A square with 5-centimeter sides is inscribed in a circle. What is the circumference of the circle? Round your answer to the nearest

tenth of a centimeter.

参考答案：`22.2`

[打开原图](<../../data/project3_perception_prototype/images/1163.png>)

![原图 1163](<../../data/project3_perception_prototype/images/1163.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 888 / Geometry3K 包装定位 train:2034

原始源定位：`train.zip::train/888/data.json`；题面：<image>In $\odot S$, find $PR$.

参考答案：`12`

[打开原图](<../../data/project3_perception_prototype/images/888.png>)

![原图 888](<../../data/project3_perception_prototype/images/888.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 562 / Geometry3K 包装定位 train:998

原始源定位：`train.zip::train/562/data.json`；题面：<image>Find y

参考答案：`10`

[打开原图](<../../data/project3_perception_prototype/images/562.png>)

![原图 562](<../../data/project3_perception_prototype/images/562.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 725 / Geometry3K 包装定位 train:281

原始源定位：`train.zip::train/725/data.json`；题面：<image>Find $CP$.

参考答案：`8`

[打开原图](<../../data/project3_perception_prototype/images/725.png>)

![原图 725](<../../data/project3_perception_prototype/images/725.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 36 / Geometry3K 包装定位 train:67

原始源定位：`train.zip::train/36/data.json`；题面：<image>Find $x$.

参考答案：`135`

[打开原图](<../../data/project3_perception_prototype/images/36.png>)

![原图 36](<../../data/project3_perception_prototype/images/36.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1749 / Geometry3K 包装定位 train:949

原始源定位：`train.zip::train/1749/data.json`；题面：<image>$\overline{XY}$ and $\overline{XZ}$ are midsegments of $\triangle RST$. Find $XZ$.

参考答案：`6.5`

[打开原图](<../../data/project3_perception_prototype/images/1749.png>)

![原图 1749](<../../data/project3_perception_prototype/images/1749.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1007 / Geometry3K 包装定位 train:326

原始源定位：`train.zip::train/1007/data.json`；题面：<image>In the figure, $m ∠ 12 = 64$. Find the measure of $ \angle 8$.

参考答案：`116`

[打开原图](<../../data/project3_perception_prototype/images/1007.png>)

![原图 1007](<../../data/project3_perception_prototype/images/1007.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 304 / Geometry3K 包装定位 train:1795

原始源定位：`train.zip::train/304/data.json`；题面：<image>$\overline{JH}, \overline{JP},$ and $\overline{PH}$ are midsegments of $\triangle KLM$. Find $x$.

参考答案：`1.35`

[打开原图](<../../data/project3_perception_prototype/images/304.png>)

![原图 304](<../../data/project3_perception_prototype/images/304.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 14 / Geometry3K 包装定位 train:400

原始源定位：`train.zip::train/14/data.json`；题面：<image>Find $x$.

参考答案：`48`

[打开原图](<../../data/project3_perception_prototype/images/14.png>)

![原图 14](<../../data/project3_perception_prototype/images/14.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1743 / Geometry3K 包装定位 train:1360

原始源定位：`train.zip::train/1743/data.json`；题面：<image>Find $x$ so that $ m \parallel n $.

参考答案：`- 8`

[打开原图](<../../data/project3_perception_prototype/images/1743.png>)

![原图 1743](<../../data/project3_perception_prototype/images/1743.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

## InterGPS 原始 ID 1289 / Geometry3K 包装定位 train:1948

原始源定位：`train.zip::train/1289/data.json`；题面：<image>Find x.

参考答案：`6`

[打开原图](<../../data/project3_perception_prototype/images/1289.png>)

![原图 1289](<../../data/project3_perception_prototype/images/1289.png>)

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

人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。

