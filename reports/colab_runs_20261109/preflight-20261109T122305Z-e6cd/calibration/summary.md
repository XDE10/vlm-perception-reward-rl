# v5 几何证伪校准（geometry-oracle-v1-20261109）

train 行数 609，validation 行数 82。阈值只按 train 选择；validation 只报告。数字由脚本生成，未手工修改。

| 关系 | 阈值字段 | 阈值 | train 认证正例 | train 误杀 | val 误杀 | 罗列断言被证伪比例 |
|---|---|---|---|---|---|---|
| PointLiesOnLine | line_distance | 0.02 | 538 | 10 | 2 | 0.816 |
| PointLiesOnLine | line_distance | 0.03 | 538 | 8 | 0 | 0.805 |
| PointLiesOnLine | line_distance | 0.04 | 538 | 8 | 0 | 0.798 |
| PointLiesOnLine | line_distance | 0.06 | 538 | 5 | 0 | 0.790 |
| PointLiesOnLine | line_distance | 0.08 | 538 | 3 | 0 | 0.785 |
| PointLiesOnLine | line_distance | 0.1 | 538 | 3 | 0 | 0.778 |
| Parallel | parallel_deg | 5.0 | 19 | 2 | 0 | 0.920 |
| Parallel | parallel_deg | 8.0 | 19 | 1 | 0 | 0.915 |
| Parallel | parallel_deg | 10.0 | 19 | 1 | 0 | 0.911 |
| Parallel | parallel_deg | 15.0 | 19 | 1 | 0 | 0.899 |
| Parallel | parallel_deg | 20.0 | 19 | 1 | 0 | 0.880 |
| Parallel | parallel_deg | 25.0 | 19 | 1 | 0 | 0.852 |
| Perpendicular | perpendicular_deg | 5.0 | 264 | 13 | 3 | 0.869 |
| Perpendicular | perpendicular_deg | 8.0 | 264 | 11 | 2 | 0.848 |
| Perpendicular | perpendicular_deg | 10.0 | 264 | 11 | 2 | 0.834 |
| Perpendicular | perpendicular_deg | 15.0 | 264 | 11 | 2 | 0.796 |
| Perpendicular | perpendicular_deg | 20.0 | 264 | 11 | 2 | 0.753 |
| Perpendicular | perpendicular_deg | 25.0 | 264 | 9 | 2 | 0.710 |
| PointLiesOnCircle | circle_relative | 0.05 | 493 | 49 | 19 | — |
| PointLiesOnCircle | circle_relative | 0.08 | 493 | 19 | 16 | — |
| PointLiesOnCircle | circle_relative | 0.1 | 493 | 14 | 9 | — |
| PointLiesOnCircle | circle_relative | 0.15 | 493 | 11 | 1 | — |
| PointLiesOnCircle | circle_relative | 0.2 | 493 | 9 | 1 | — |
| PointLiesOnCircle | circle_relative | 0.25 | 493 | 8 | 1 | — |
| Angle | angle_value_deg | 10.0 | 427 | 24 | 1 | 0.467 |
| Angle | angle_value_deg | 15.0 | 427 | 15 | 0 | 0.449 |
| Angle | angle_value_deg | 25.0 | 427 | 4 | 0 | 0.386 |
| Angle | angle_value_deg | 35.0 | 427 | 3 | 0 | 0.282 |
| Angle | angle_value_deg | 45.0 | 427 | 3 | 0 | 0.218 |
| CongruentLength | congruent_length_ratio | 1.1 | 91 | 6 | 1 | — |
| CongruentLength | congruent_length_ratio | 1.2 | 91 | 0 | 1 | — |
| CongruentLength | congruent_length_ratio | 1.35 | 91 | 0 | 0 | — |
| CongruentLength | congruent_length_ratio | 1.5 | 91 | 0 | 0 | — |
| CongruentLength | congruent_length_ratio | 2.0 | 91 | 0 | 0 | — |
| CongruentAngle | congruent_angle_deg | 5.0 | 36 | 2 | 2 | — |
| CongruentAngle | congruent_angle_deg | 10.0 | 36 | 0 | 1 | — |
| CongruentAngle | congruent_angle_deg | 15.0 | 36 | 0 | 0 | — |
| CongruentAngle | congruent_angle_deg | 25.0 | 36 | 0 | 0 | — |
| CongruentAngle | congruent_angle_deg | 40.0 | 36 | 0 | 0 | — |

## 一致性门控（D35，奖励实际使用的口径）

若一张图的标注否定了它自己的某条认证事实，这张图上同一类检验（坐标类或存在性类）不再用来证伪其他断言。

| | 被门控的图 | 按类别 | 门控后仍被证伪的认证正例（默认开启的四类） |
|---|---|---|---|
| train | 20 / 609 | {'coordinates': 20} | 0 |
| validation | 2 / 82 | {'coordinates': 2} | 0 |

## 留一法残余误杀率（train；上限 5%，由 α、β 推出）

把每条认证事实当作没见过的真实断言：门控只用同一张图的其他认证事实计算，看这条事实是否仍被证伪。这估计了奖励对未认证的真实断言的误杀率。

| 关系 | 认证正例 | 残余误杀 | 比例 | 95% 区间 | 不超过上限 |
|---|---|---|---|---|---|
| PointLiesOnLine | 538 | 2 | 0.004 | 0.001–0.013 | 是 |
| Parallel | 19 | 0 | 0.000 | 0.000–0.168 | 是 |
| Perpendicular | 264 | 11 | 0.042 | 0.023–0.073 | 是 |
| PointLiesOnCircle | 493 | 3 | 0.006 | 0.002–0.018 | 是 |
| 合计 | 1314 | 16 | 0.012 | 0.007–0.020 | |

## 原始误杀明细（train，默认阈值，门控前）

| 题 | 认证事实 | 原因 | 测量值 |
|---|---|---|---|
| train:1218 | `PointLiesOnLine(E,(B,C))` | not_collinear | {"line_distance": 0.0707, "position_on_segment": 0.8086, "segment_relative_length": 0.8116} |
| train:1251 | `Perpendicular((K,L),(L,M))` | not_perpendicular | {"angle_between_deg": 54.4293, "deviation_deg": 35.5707, "segment_relative_lengths": [0.4248, 0.7332]} |
| train:1471 | `Perpendicular((A,C),(C,E))` | not_perpendicular | {"angle_between_deg": 60.4304, "deviation_deg": 29.5696, "segment_relative_lengths": [0.4337, 0.8678]} |
| train:1488 | `Perpendicular((A,C),(C,E))` | not_perpendicular | {"angle_between_deg": 60.4304, "deviation_deg": 29.5696, "segment_relative_lengths": [0.4337, 0.8678]} |
| train:1542 | `Parallel((A,B),(C,D))` | not_parallel | {"angle_between_deg": 39.0402, "deviation_deg": 39.0402, "segment_relative_lengths": [0.6567, 0.8372]} |
| train:1542 | `PointLiesOnLine(E,(G,H))` | not_collinear | {"line_distance": 0.7963, "position_on_segment": 1.316, "segment_relative_length": 0.1587} |
| train:1542 | `PointLiesOnLine(F,(C,D))` | not_collinear | {"line_distance": 0.2341, "position_on_segment": 0.258, "segment_relative_length": 0.8372} |
| train:1542 | `PointLiesOnLine(F,(H,I))` | not_collinear | {"line_distance": 0.2139, "position_on_segment": 0.7136, "segment_relative_length": 0.4387} |
| train:1593 | `PointLiesOnCircle(A,Circle(D))` | off_circle | {"relative_deviation": 0.5277, "reference_points": 2, "radius_relative": 0.7386} |
| train:1593 | `PointLiesOnCircle(C,Circle(D))` | off_circle | {"relative_deviation": 0.5182, "reference_points": 2, "radius_relative": 0.7386} |
| train:1598 | `Perpendicular((B,C),(C,D))` | not_perpendicular | {"angle_between_deg": 60.7762, "deviation_deg": 29.2238, "segment_relative_lengths": [0.438, 0.8563]} |
| train:1729 | `Perpendicular((A,F),(F,H))` | not_perpendicular | {"angle_between_deg": 65.609, "deviation_deg": 24.391, "segment_relative_lengths": [0.4122, 0.9982]} |
| train:1783 | `PointLiesOnCircle(A,Circle(B))` | off_circle | {"relative_deviation": 0.5323, "reference_points": 3, "radius_relative": 0.5383} |
| train:1783 | `PointLiesOnCircle(C,Circle(B))` | off_circle | {"relative_deviation": 1.1518, "reference_points": 3, "radius_relative": 0.2878} |
| train:1783 | `PointLiesOnCircle(D,Circle(B))` | off_circle | {"relative_deviation": 0.8701, "reference_points": 3, "radius_relative": 0.2878} |
| train:1783 | `PointLiesOnCircle(E,Circle(B))` | off_circle | {"relative_deviation": 0.4653, "reference_points": 3, "radius_relative": 0.5383} |
| train:1878 | `PointLiesOnCircle(J,Circle(K))` | off_circle | {"relative_deviation": 0.1686, "reference_points": 1, "radius_relative": 0.5646} |
| train:1878 | `PointLiesOnCircle(L,Circle(K))` | off_circle | {"relative_deviation": 0.2028, "reference_points": 1, "radius_relative": 0.4694} |
| train:1957 | `Perpendicular((A,C),(C,E))` | not_perpendicular | {"angle_between_deg": 60.4304, "deviation_deg": 29.5696, "segment_relative_lengths": [0.4337, 0.8678]} |
| train:2049 | `PointLiesOnCircle(G,Circle(B))` | off_circle | {"relative_deviation": 0.4031, "reference_points": 1, "radius_relative": 0.4161} |
| train:2090 | `Perpendicular((A,C),(C,E))` | not_perpendicular | {"angle_between_deg": 60.4304, "deviation_deg": 29.5696, "segment_relative_lengths": [0.4337, 0.8678]} |
| train:329 | `PointLiesOnCircle(G,Circle(B))` | off_circle | {"relative_deviation": 0.4031, "reference_points": 1, "radius_relative": 0.4161} |
| train:335 | `Perpendicular((T,U),(U,W))` | not_perpendicular | {"angle_between_deg": 67.8548, "deviation_deg": 22.1452, "segment_relative_lengths": [0.339, 0.9273]} |
| train:380 | `PointLiesOnLine(E,(B,C))` | not_collinear | {"line_distance": 0.0707, "position_on_segment": 0.8086, "segment_relative_length": 0.8116} |
| train:425 | `Perpendicular((A,C),(C,E))` | not_perpendicular | {"angle_between_deg": 60.4304, "deviation_deg": 29.5696, "segment_relative_lengths": [0.4337, 0.8678]} |
| train:523 | `PointLiesOnCircle(U,Circle)` | off_circle | {"relative_deviation": 0.1555, "reference_points": 2, "radius_relative": 0.5384} |
| train:598 | `Perpendicular((A,C),(C,E))` | not_perpendicular | {"angle_between_deg": 60.4304, "deviation_deg": 29.5696, "segment_relative_lengths": [0.4337, 0.8678]} |
| train:919 | `Perpendicular((Q,T),(R,S))` | not_perpendicular | {"angle_between_deg": 0.7544, "deviation_deg": 89.2456, "segment_relative_lengths": [0.3509, 0.5052]} |

## 罗列攻击（train，每题一组探针；奖励实际口径，含门控）

| 探针 | 题数 | v4 均值 | v5 均值 | v4 高于诚实读一半的比例 | v5 高于诚实读一半的比例 |
|---|---|---|---|---|---|
| honest_full | 609 | 1.000 | 1.000 | 0.941 | 0.941 |
| honest_half | 609 | 0.719 | 0.569 | 0.000 | 0.000 |
| incidence_spray | 608 | 0.176 | -0.916 | 0.031 | 0.003 |
| pair_spray | 608 | 0.080 | -0.925 | 0.000 | 0.000 |
| value_spray | 449 | 0.591 | 0.065 | 0.203 | 0.143 |
| combined_spray | 608 | 0.404 | -0.944 | 0.155 | 0.000 |
| combined_spray_with_gold | 609 | 0.969 | -0.725 | 0.905 | 0.043 |

## 罗列攻击（同上，但关闭门控，对照用）

| 探针 | 题数 | v4 均值 | v5 均值 | v4 高于诚实读一半的比例 | v5 高于诚实读一半的比例 |
|---|---|---|---|---|---|
| honest_full | 609 | 1.000 | 1.000 | 0.941 | 0.941 |
| honest_half | 609 | 0.719 | 0.569 | 0.000 | 0.000 |
| incidence_spray | 608 | 0.176 | -0.944 | 0.031 | 0.000 |
| pair_spray | 608 | 0.080 | -0.948 | 0.000 | 0.000 |
| value_spray | 449 | 0.591 | 0.065 | 0.203 | 0.143 |
| combined_spray | 608 | 0.404 | -0.973 | 0.155 | 0.000 |
| combined_spray_with_gold | 609 | 0.969 | -0.767 | 0.905 | 0.016 |

认证正例被存在性规则否定的计数（train）：{}
