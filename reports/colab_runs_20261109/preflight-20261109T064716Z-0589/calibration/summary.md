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

## 罗列攻击（train，每题一组探针）

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
