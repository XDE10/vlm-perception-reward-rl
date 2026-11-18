# Shuffle-R1 CPU 阶段完成记录

## 数据

使用前一版 27,802 行清洗集，复看剩余 337 个训练行对应的 369 个图像配对。逐对记录图形结构、标注、表格数据或流程差异。配对中 74 个确认属于同一图像家族，37 个保留疑问，258 个目视不同。行级按同图家族整组处置。最终剔除 74 行（57 个白底可见像素家族），隔离 36 行待审；公开测试和全部原始分片按既有 SHA256 核对。[逐对决策](review_pair_decisions.jsonl)

| 数据 | 行数 |
| --- | ---: |
| 本轮输入 | 27,802 |
| 确认重复并排除 | 74 |
| 单独隔离、待复核 | 36 |
| 可用于训练或内部开发集 | 27,692 |
| 正式训练集 | 27,436 |
| 内部 dev | 256 |
| dev16（从 dev 内选取） | 16 |

用固定种子 `20261115` 按来源划 dev。dev 有 241 行 MM-EUREKA 和 15 行 Geometry3K，覆盖 246 个精确图像家族。相同白底可见图整组分配；只有在 dHash≤5 和 pHash≤8 两种候选检索下均没有跨家族近邻的组才进入 dev。训练与 dev、训练与公开测试、dev 与公开测试的精确可见像素交集均为 0。公开测试近重复复查覆盖既有候选索引；候选之外的近重复和人工判为待复核的图有各自的证据边界。

输出位于 `/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-visible-family-v2-20261115`。该目录中的 `rows.jsonl` 保存全部 27,802 行的来源、图像身份、归属和有效输入的 prompt/grid。Parquet 读回核对了图像字节、题干、答案、来源和顺序。[分区清单](split_manifest.json) · [读回验证](readback.json)

## 入口与 CPU 测试

单卡分支本地提交 `fd4e226893e10b0fd67d4231f1ea66c0eacda407`。冻结配置在单卡 worktree 的 `configs/g4_clean_seed1.yaml`，正式 `max_steps=150`，首轮 workers=0。启动时核对 train/dev 文件 SHA、行数、固定模型 revision、图像策略、prompt 模板和长度设置。内部 probe 可用 `dev16.parquet`，四种 B/G/chunk 形状均通过真实 `--print-config` 入口。

- 实际 vLLM 包装器将 `max_num_seqs=64` 和 engine seed 传到构造器。训练按逻辑步和题位派生每题 seed，调整物理分块不改变题位 seed。内部评估独立设种子并恢复训练 RNG；ABS 继续使用已保存的 driver NumPy 状态。[vLLM 0.9.2 的每请求采样参数接口](https://github.com/vllm-project/vllm/blob/v0.9.2/vllm/entrypoints/llm.py)
- 训练、rollout 输入和公开评测使用同一白底合成预处理。超长 prompt 在实际加载时抛出含文件、行号和展开长度的错误。用固定 tokenizer、processor 及尺寸规则核查最终 27,692 行，109 条走完整像素处理交叉核对。最大展开长度 1,660，未有行因超出 2,048 隔离。dev16 每行的真实 CPU processor 网格和展开长度逐条一致。
- `trainer.stop_after_step` 控制在逻辑步完整更新和 checkpoint 验证后退出，恢复时保持原定 `max_steps`。CPU 使用真实 driver 和 loader 覆盖停在第 2 步、从保存点继续到第 3 步，三种更新计数与数据顺序一致。ABS 重用只读图像张量，拼接后的轨迹和元数据可独立写入。

全仓使用冻结的 `shuffle-r1-cpu-frozen-20261115` 环境，52 项通过。实际 CUDA、vLLM 生成、FSDP 通信和 3B checkpoint 写回仍待上卡验收。本轮未分配 GPU。[pytest 日志](pytest.txt)
