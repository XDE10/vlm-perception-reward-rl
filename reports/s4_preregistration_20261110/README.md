# S4 预注册的支撑材料（2026-11-10）

[S4 预注册](../../docs/plan/S4预注册_20261110.md) 第 2 节引用的数字，在这里可以复现。只涉及 train。

## 1. S3 决策文件的副本

`configs/experiments/s3_decisions_20261110.json` 是结果分支 `results/v0-20261110T023008Z-60fc` 上
`reports/colab_runs_20261110/v0-20261110T023008Z-60fc/s3_decisions.json` 的逐字节副本（VM 推送的提交 `15ca2714ba16`）。
用 `git show` 取出后核对：

| 核对 | 值 |
|---|---|
| 结果分支上的 git blob | `6484ca02c939f6300afe3a2c3230818ea010c160` |
| 副本的 `git hash-object` | `6484ca02c939f6300afe3a2c3230818ea010c160` |
| 副本的 SHA256 | `f3541b88535a8e7cfc1ead30f12c44a64d1c2179f64597c7d55d466051863ed5` |

SHA256 同时记在登记表 `configs/experiments/s4_runs_20261110.json` 的 `decisions.sha256`，由 `tests/test_s4_registration.py` 核对。
`.gitattributes` 把这个文件标为 `-text`，换行符不会被改写。

## 2. 格式率的区间（`format_rate_interval.py`）

S3 的预热规则只比较点估计与 0.50（S3 设计第 6 节）。这里另外给出区间，只作报告，不改变任何决策。

- 数据：结果分支上 `prompt_select/predictions.jsonl` 中温度 1.0 的样本（64 道已批准 train 题，每题每个提示 4 条）。
- 方法：按题重抽（有放回），1 万次，种子 20261109，取 2.5% 与 97.5% 分位数。与 `src/evaluation/stats.py` 的 bootstrap 做法相同，
  聚类单位是题。
- 脚本先核对重算的格式率和条数与同一次运行的 `prompt_select/summary.json` 相同，不同就报错。

| 提示 | 格式奖励为 1 的条数 / 总条数 | 格式率 | 95% 区间 |
|---|---|---|---|
| P0 | 43 / 256 | 0.168 | [0.117, 0.223] |
| P1 | 136 / 256 | 0.531 | [0.461, 0.602] |

P1 的区间跨过 0.50，所以“不需要预热”这一结论的余量不大。试跑的 G4 门槛（预注册第 11 节）检查格式率在训练中是否上升，
不上升时的回退已经写定。

复现：

```bash
git fetch origin 'refs/heads/results/*:refs/remotes/origin/results/*'
python reports/s4_preregistration_20261110/format_rate_interval.py
```

输出写到同目录的 `format_rate_interval.json`（需要 numpy）。
