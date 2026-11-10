# 架构与数据流

本页说明项目三的模块分层和一次数据/训练请求经过的路径。目标不是罗列所有函数，
而是让新接手者知道“哪一层负责什么、边界在哪、哪些结论不能从当前代码推出”。
状态事实（多少批准行、哪些检查跑过）以 [README](../README.md) 与
[verification.md](verification.md) 为准。

## 端到端流水线

```text
Geometry3K / InterGPS / MathVista 原始材料
        │  (来源、许可、同图/同题重叠审计)
        ▼
data/project3_sources + data/project3_audit        src/data/project3_audit.py
        │  (有限 schema 的 AST/事实原型、文字蕴含排除、AI 审核、逐行批准)
        ▼
data/{project3_perception_*, finalfill_v7, strict_v8_*, topup_v6_*}
        │  (抽取出便携发布副本，图片改为包内相对路径)
        ▼
data/portable_release/  ← manifest.json 记录批准文件、逐文件 SHA、
        │                  dev 保护 ID 与输入溯源
        ▼
configs/*.json → scripts/training/train_project3.py
        │          → src/training/approved_hf.py（manifest 门控 + 白名单）
        ▼
runs/... SFT merged 权重 → 稀疏 GRPO（感知奖励 + math_verify 数学检查）
        │
        ▼
src/evaluation/geometry_perception_parser.py + 视觉诊断脚本 → 评测/诊断记录
```

## 协议 v3 统一 GRPO 流水线（2026-11-09 起的正式实验）

```text
configs/experiments/rl_v3.json + arms.json ──► src/training/rl_config.py（基础配置 + 组别 + 种子 → 完整配置与哈希）
        │
        ▼
src/training/rl_data.py：release manifest 门控 → v4 奖励行契约 → 受保护 dev ID → 图片字节 SHA
        │                 → 与 InterGPS 记录的像素哈希一致 → 安慰剂错位配对 / 去图（blind）
        ▼
src/training/protocol_v3.py：统一 system prompt；输出 <perception>…</perception><think>…</think><answer>…</answer>
        │
        ▼
src/training/rl_entry.py：语言 LoRA（精确模块名，ViT/merger 冻结断言）→ TRL GRPOTrainer
        │                  → 运行身份（配置/版本/源码/数据 SHA）→ checkpoint 与恢复校验
        ▼
src/training/rl_rewards.py：每批算一次，三个奖励头
        ├── 答案：src/rewards/answer.py（math_verify 常驻进程池，只认唯一 <answer>）
        ├── 格式：三段协议 + 至少 1 条可解析事实
        └── 感知：none | v4（冻结） | v5（src/rewards/perception_v5.py + geometry_oracle.py）
        ▼
runs/<实验>/<组>/seed<k>/：rollouts.jsonl（逐条 rollout 与奖励明细）、run_identity.json、final/ adapter
```

## 模块职责

| 模块 | 职责 | 关键边界 |
| --- | --- | --- |
| `src/data/approved_training_inputs.py` | 读 release manifest，校验文件级批准；`model_view` 只放行 `problem`、`image_path` | 拒绝手改批准字段/未知文件；不把答案或内部符号送进 prompt |
| `src/data/geometry_split_guard.py` | 用图像像素身份保护 dev/validation，阻止跨 split 复用 | 只比较像素身份，不读取 held-out 答案 |
| `src/data/geometry_model_serialization.py` | 把审核用事实转为模型可见文本，序列化顺序稳定 | 内部 `radius_*` 等身份字段不得泄漏 |
| `src/data/perception_text_guards.py` | 有限、保守的题面文字蕴含判断 | 不匹配 ≠ 图像独占；不能据此自动认证事实 |
| `src/data/project3_perception_prototype.py` / `project3_perception_v2.py` | 基于 InterGPS 的有限 schema AST/事实原型与复核序列化 | 原型和复核输出都不是视觉金标 |
| `src/data/perception_v4.py` | 解析审核内容、规范化 Angle→Length→Parallel→Perpendicular→Tangent，计算稀疏范围奖励 | 认证范围外的事实未知（mask），不按“缺标签”惩罚 |
| `src/data/project3_perception_preview.py` | 独立的预览序列化，供人工/模型审核 | 与生产奖励解析器解耦，避免自证 |
| `src/training/approved_hf.py` | 旧 HF/TRL SFT 与 GRPO 入口：VL processor、assistant-only labels、LoRA、合并权重身份检查 | 历史入口；2026-11-09 只修复 LoRA 误入 ViT 与 transformers 5 模型类 |
| `src/training/rl_entry.py` / `rl_config.py` / `rl_data.py` / `rl_rewards.py` | 协议 v3 统一 GRPO 入口：组别配置解析、数据门控、奖励汇总与逐条日志、运行身份与恢复 | 组别只能覆盖白名单字段；CPU 用 tiny Qwen2.5-VL 端到端测试，GPU 待 S2 预检 |
| `src/training/protocol_v3.py` | 所有组共用的 system prompt 与输出解析 | 训练与评测提示经 TRL 渲染后逐字一致（有测试） |
| `src/training/lora_language.py` / `vision_cache.py` | 只挂语言模块的 LoRA 与冻结断言；可选的冻结 ViT 输出缓存 | 缓存只在冻结且等价性检验通过时启用 |
| `src/training/multimodal_guard.py` | 让 TRL 评分前向的图像 token 类型与 input_ids 对齐（处理器左填充），并在每次前向检查 | 不一致就报错停止，不会带着错误的 M-RoPE 位置训练（D33） |
| `src/rewards/claims.py` / `geometry_oracle.py` / `perception_v5.py` | 逐条断言解析；用 InterGPS 坐标与线/圆实例证伪断言；可证伪感知奖励 v5.1 | 几何只用来否定，不用来认证；标注否定了自身认证事实的图，同类检验不参与证伪（一致性门控）；门控后每类留一法残余误杀率 ≤ 5%（D35） |
| `src/rewards/answer.py` / `attacks.py` | math_verify 常驻进程池与仅去掉表述形式的答案规范化；确定性罗列攻击探针 | 训练判定不加数值容差 |
| `src/data/intergps_index.py` | InterGPS 人工标注的只读几何视图（点坐标、线/圆实例、题型） | 坐标只用于与平移无关的相对检验 |
| `src/training/perception_reward_v4.py` | 训练器回调，把感知奖励接到 TRL | 奖励标签是私有元数据，不进入可见输入 |
| `src/evaluation/geometry_perception_parser.py` | 有限关系 schema 解析、确定性序列化、覆盖感知去重评分 | 拒绝解析不等于模型推理错误；无标签类别不惩罚 |
| `src/evaluation/eval_sets.py` / `public_sources.py` | S3 预注册的评测集规则（视觉必需子集、CF-Geo 候选、取整题的答案集合、换图配对）；固定版本公开数据的下载与按 `migration_manifest.json` 核对 | 规则只读题面、答案和 InterGPS 人工标注，不看模型输出；下载的文件不进数据包，也不进结果分支 |
| `src/evaluation/cfgeo.py` | CF-Geo 补丁格式与重建：在固定版本的原图上贴补丁，前后都核对像素哈希 | 补丁只含我们填的底色和画的数字，仓库里没有原图 |
| `src/evaluation/generate_v3.py` / `harness.py` | 批量贪心生成与评分；所有模型、所有条件（原图、无图、换图、CF k=1、CF k=2）共用一条评测路径 | 每个模型用同样的批次（32）和顺序；LoRA 不合并加载，即训练出的策略本身 |
| `src/evaluation/stats.py` | 按图聚类的配对 bootstrap 与置换检验、Holm 校正、McNemar 精确检验（D46） | “能区分”要求 Holm 校正后 p < 0.05 且区间不跨 0 |
| `src/training/vllm_guard.py` | 用 vLLM 生成时，检查每张训练图在训练处理器和 vLLM 默认设置下得到相同的 patch 网格 | 不同就在训练前停止（TRL 不能把 max_pixels 传给 vLLM） |
| `src/losses/reference.py` | SFT/GRPO/对齐 KL 的 CPU 参考实现 | 正确性参照，不是 GPU 训练器或性能结论 |
| `src/teachers/tokenizer_audit.py` | 按白名单下载 tokenizer/config 元数据并逐 token 比对 | 不下载模型权重，不产生能力结论 |

## 身份链与失败关闭

训练/评测记录必须能串起同一条身份链，任何一环缺失都应让流程失败而不是“继续跑”：

1. **模型**：`Qwen/Qwen2.5-VL-3B-Instruct` + 固定 revision
   `66285546d2b821cf421d4f5eb2576359d3770cd3`（见 `configs/`）。
2. **tokenizer/processor**：配置里的 `tokenizer_path` 与审计记录；视觉分支必须用
   对应 VL `AutoProcessor`，不能换成普通文本 tokenizer。
3. **数据文件**：release manifest 的 `files` SHA256 + `approved_*_files` 文件名。
4. **逐行批准**：`training_approved`、唯一 ID、模型输入白名单。
5. **图像**：行内 `image_path` 必须是包内相对路径，且 `image_sha256` 与文件一致。
6. **划分**：dev/validation 图像像素身份不得进入训练。
7. **输出**：配置中的 `output_dir` 必须是相对路径；恢复训练必须核对完整
   checkpoint/合并权重身份，不能只加载 adapter 就声称恢复。

## 明确不在当前实现内的东西

- 没有已验收的 CUDA 训练、显存/恢复结果；协议 v3 入口目前只在 CPU 上用 tiny 模型端到端验证。
- 没有 EasyR1 集成；详细方案中的 EasyR1 是设计路线，正式实验沿用 TRL（见决策记录）。
- 没有完整 V0～V4 SFT 矩阵；正式实验按 [执行计划](plan/执行计划_20261108.md) 的组别进行。
- 没有全图事实 precision/recall 金标；认证事实是部分覆盖，未知按 mask 处理。
- `src/losses/` 与历史 CPU 文档中的多项目共用设施已被 2026-11-08 清理分离，
  不再是本仓库运行依赖。
