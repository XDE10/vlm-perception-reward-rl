# Shuffle-R1 单卡正式训练与存储切回记录

记录日期：2026-11-18，UTC+8。本目录补齐此前留在隔离开发副本和运行目录中的源码与证据。
这是独立的 Shuffle-R1 复现轨道；S4/S5 感知奖励实验仍遵循原有协议 v3。

## 当前结论与边界

- 正式运行是 `qwen25vl3b_b512_seed1`，账号 B、单张 G4，目标 150 个逻辑步。
  控制器使用 `--until-complete --stop-after-step 150`，没有沿用早期测试的八小时限制。
- 2026-11-18 09:06:32 已独立读回原网盘第 43 步完整断点：17 个载荷文件、40,967,383,104 字节，
  `optimizer_steps=172`、`scheduler_steps=43`，marker 与 manifest 一致。
  本轮另于 10:42:35 从存活 G4 独立核对原网盘第 45 步，计数为 45/180/45；
  见[最新核验快照](evidence/latest-checkpoint.json)。
- 第 25 步的 256 题内部 dev 聚合指标：`accuracy_reward=0.582`、`format_reward=0.984`、
  `overall_reward=0.622`；这是日志保留精度下的读数。[原始记录](evidence/validation-step-25.json)
  不代表 Geometry3K/K12 的公开测试分数，也不足以证明 150 步的泛化结果或排除过拟合。
- 本次提交整理和运行 CPU 检查；没有重启训练、申请新 GPU、变更正式学习率或扩大训练目标。
  150 步尚未完成，同预算 PTS 对照和正式公开测试结果尚未得出。

## 数据与训练身份

原始 MMRL30k revision 为 `b362381652529d67ebc26f5e140bd0a54ba4647d`，原始数据和公开测试保留。
按图剔除测试重叠后，在 27,802 行候选中再次排除 74 行确认重复、隔离 36 行待审，余 27,692 行；
按图像家族划分为 27,436 train / 256 内部 dev。逐对复核与证据边界见
[CPU 完成报告](../shuffle_r1_cpu_completion_20261115/README.md)和[分区清单](evidence/split_manifest.json)。
该数据不是主项目 `portable_release` 的 609/82 条认证事实，也没有改写其批准清单。

| 身份 | 固定值 |
| --- | --- |
| 模型 | Qwen2.5-VL-3B-Instruct，revision `66285546d2b821cf421d4f5eb2576359d3770cd3` |
| 作者基线 | `b863694f25d38d0e118761363dc5897bb9625e82` |
| 正式单卡代码 | `1a7fb4b67e02a6b41cde437d7edc074ddd5a22e6` |
| 配置身份 SHA256 | `c5b0fedce12601a5ef9818563e81b5adefb1f401f57aa8bb64a5b367ebe61eb4` |
| 源码身份 SHA256 | `3d509aee1eea723ebf07121a8b39aaae45d8aef8e61c555219ff7fdfe7176da2` |
| train SHA256 | `e8e9a905119da70c75ce870d2fd5d5d2113693e4f2d0f9023690e246bf1276ef` |
| dev SHA256 | `4608d8413e81031eb54433232426f6044d865c083fd1620745aac8f429c674d7` |

单卡保留 B512/G128/n16、PTS pairwise、ABS replay=8 和每逻辑步 4 次 optimizer / 1 次 scheduler 更新；
物理 rollout 每块 16 prompts，参考 DP=8、参考微批=4，物理微批=1。
学习率 `1e-6`、零 warmup、constant，与作者对应配置和调度器一致。
内部 dev 每 25 步评估，temperature=0、n=1；训练和推理采用相同白底合成图像预处理。

## 可复查源码与配置

- [Git bundle](source/shuffle-r1.bundle)保留正式训练提交及其 Git 对象；
  [完整补丁](source/shuffle-r1-single-gpu.patch)是作者基线到正式提交的可读差异。
  修改涉及实际 `shuffle_r1.main` / FSDP worker、逻辑批次、参考微批权重、RNG、checkpoint、图像处理与回归测试。
  上游出处为 [xiaomi-research/shuffle-r1](https://github.com/xiaomi-research/shuffle-r1)，许可证副本见
  [UPSTREAM-LICENSE](source/UPSTREAM-LICENSE)。
- [实际运行配置](runtime/active-payload/probe.yaml)保留 VM 绝对路径，用于审查和重建，不能直接在主项目根目录运行。
  [实际 launcher](runtime/active-launch.py)、[恢复控制器](runtime/recovery-20261116/resume_formal.py)、
  [发布与保留逻辑](runtime/recovery-20261116/formal_validation.py)、
  [实际发布脚本](runtime/active-payload/persist_checkpoint.sh)均为本轮从运行目录读回的源码快照。
  [实际目标文件](runtime/active-payload/run-target.txt)的三个字段依次是 deadline、目标步、恢复步。
- [存储路由](runtime/storage-switch-20261117/storage_route.py)和
  [迁移核验](runtime/storage-switch-20261117/storage_transfer.py)记录切换实现。
  `switchback-now` 使用已核验的云端断点作为迁移锚点，允许更新的本地完整断点在切换后补传。
- [ARTIFACTS.json](ARTIFACTS.json)记录各快照的来源路径、字节数与 SHA256；这些来源路径是当时的本机/VM 布局。
  本目录中的脚本保留运行时布局依赖，属于审计快照，主项目训练入口没有改为这些脚本。

可在独立目录恢复 Git 源码；这组命令不启动训练：

```bash
git init shuffle-r1-restored
git -C shuffle-r1-restored fetch /path/to/shuffle-r1.bundle g4-logical-batch-prep-20261115
git -C shuffle-r1-restored checkout --detach 1a7fb4b67e02a6b41cde437d7edc074ddd5a22e6
```

bundle 的实际 refs 和完整性、本地补丁重建后的 tree 是否与正式提交相同，见
[源码验证记录](verification/source-reconstruction.json)。

## 断点、验证和环境保存

本地每步保存、每步尝试上传；新产生的完整断点滚动保留最近两份，1–8 步历史保留。
25/50/75/100/125 等评估步在两个后续完整断点核验后，保留模型权重、HF 配置/处理器和评估 JSON，
删除对应旧优化器与 RNG 全量状态。最终 149/150 步保留全量恢复状态。
恢复必须先核对 marker、身份、manifest、文件清单与更新计数；模型加载时进一步检查文件 SHA256。
训练结束后先确认断点和评估持久化，再释放 GPU。

2026-11-18 因临时网盘再次 403，用户授权提前切回原网盘。
迁移先核验第 41、42 步，云端逐文件比对均为零差异，再复制完成标记、dev 结果、环境归档和输入数据。
08:55 切换本机及存活 G4 的项目专用 rclone 别名，恢复上传；随后第 43 步补传并独立核验通过。
[迁移记录](evidence/transfer-p3temporary-to-p3original.json) ·
[第 43 步读回与环境核验](evidence/return-original-verification-20261118.json)

环境重建归档 SHA256 为 `1f7aedc06a2972548194f906a703335abd18918dc4f6f79fb68d71fd54a2e19f`，
25,811,856 字节，保存 Python 3.12.3、201 个包的版本和安装/源码材料。
[依赖版本](environment/current-environment.json) · [安装要求](environment/requirements-install.txt) ·
[归档核验](evidence/drive-environment-verified.json)。
它是需要重新下载模型/依赖的重建材料，不是整机镜像；模型、全量断点、数据 Parquet 和 rclone 授权文件不进入本次 Git 提交。

## 本轮提交验证

本轮结果记录在 [verification/README.md](verification/README.md)。CPU 通过不代表已经完成新一轮 GPU 训练或公开测试。
11 月 15 日的 CPU 报告、早期单卡审查和[外部复审输入](../项目三_最新进展审查与下一步执行裁决_20261115.md)
按原文保存，其中未上卡或预算限制属于当时状态；
当前执行以本页的冻结身份和带时间的核验记录为准。
