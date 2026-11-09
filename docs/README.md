# 文档索引

本目录存放项目三的当前说明页、历史留档与操作指南。先读
[根 README](../README.md) 与 [AGENTS.md](../AGENTS.md)，再按任务进入下页。

## 当前说明（随代码维护）

| 文档 | 内容 |
| --- | --- |
| [repo_layout.md](repo_layout.md) | 目录结构、命名约定、文件应放在哪里、冻结区域 |
| [architecture.md](architecture.md) | 模块分层、数据流、身份链与失败关闭设计 |
| [data.md](data.md) | 数据目录、批准范围、SHA/图片路径校验规则 |
| [training.md](training.md) | 环境、配置、SFT/RL/诊断入口、GPU 验收边界 |
| [verification.md](verification.md) | 校验工具、测试基线、已知环境缺口、报告规范 |

## 执行计划与决策（2026-11-08 起）

| 文档 | 内容 |
| --- | --- |
| [plan/执行计划_20261108.md](plan/执行计划_20261108.md) | 已批准的执行计划：验收标准、实验组、主终点、分阶段安排 |
| [plan/决策记录.md](plan/决策记录.md) | 实施中的技术决策、理由与未采用的备选，按时间追加 |
| [plan/阶段报告_S1_20261109.md](plan/阶段报告_S1_20261109.md) | S1 阶段报告：审计修复与统一训练入口 |
| [plan/阶段报告_S2_20261110.md](plan/阶段报告_S2_20261110.md) | S2 阶段报告：Colab 运行器 |
| [plan/阶段报告_S2.1_20261109.md](plan/阶段报告_S2.1_20261109.md) | S2.1 阶段报告：首次预检上传失败的原因与修复，可选 Google Drive |
| [plan/阶段报告_S2.2_20261109.md](plan/阶段报告_S2.2_20261109.md) | S2.2 阶段报告：第二次预检的三个失败（图像 token 错位、恢复身份不一致）与校准口径（一致性门控、留一法） |
| [plan/阶段报告_S2.3_20261109.md](plan/阶段报告_S2.3_20261109.md) | S2.3 阶段报告：结果由 VM 直接推送、准备好的 VM（`--session`）、命令兼容 zsh |
| [plan/阶段报告_S2_验收_20261109.md](plan/阶段报告_S2_验收_20261109.md) | S2 验收：第三次预检通过、接受冻结的运行时、vLLM 重要性采样修正、认证事实勘误、可能空转的 VM |
| [plan/S3设计_20261109.md](plan/S3设计_20261109.md) | S3 设计（预注册）：评测集、视觉必需子集、CF-Geo 规则、主终点与统计方法、只用 train 的决策规则、`v0` 任务 |
| [../colab/README.md](../colab/README.md) | Colab 运行器使用说明：一次性准备、每阶段命令、断线恢复、结果位置 |

## 指南（可复用模板）

| 文档 | 内容 |
| --- | --- |
| [guides/argon_review_prompt.md](guides/argon_review_prompt.md) | 面向外部深度审查者的项目说明与审查提示词模板 |

## 历史留档（只读，不随当前目录结构更新）

| 位置 | 内容 |
| --- | --- |
| [blueprints/](blueprints/) | 2026-10 的研究方案、共用规范、Strict v8/Topup v6 说明与旧配置。其中的命令、路径和数字是当时快照，不能替代根目录 `configs/` 与当前 README。 |
| [migration/](migration/) | 迁移验收、清理记录、封板清单、整理记录与旧 README 快照。相对链接按各自记录时的目录写就，部分指向已删除文件属于历史事实。 |
| [migration/overnight_cpu_20261023.md](migration/overnight_cpu_20261023.md) | 三项目 CPU 基础设施说明（2026-10-23），其中部分模块已在 2026-11-08 分离清理中删除。 |

历史文档中出现的旧绝对路径（例如 `D:\Users\Mr.Z\Desktop\modern_genai`）只用于
溯源，不是运行依赖；以仓库内相对路径和 `migration_manifest.json` 为准。
