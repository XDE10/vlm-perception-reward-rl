# Colab 运行摘要：preflight-20261109T064716Z-0589（preflight）

总体结论：**未通过**

## 步骤

| 步骤 | 状态 | 用时（秒） | 计入结论 |
|---|---|---|---|
| env_report | passed | 2 | 是 |
| verify_pack | passed | 0 | 是 |
| drive_probe | passed | 0 | 否 |
| pytest | passed | 128 | 是 |
| calibration | passed | 99 | 是 |
| gpu_probe | passed | 184 | 是 |
| v0_probe | passed | 112 | 否 |
| smoke_rl_ans | passed | 57 | 是 |
| smoke_rl_v4 | passed | 56 | 是 |
| smoke_rl_v5 | passed | 56 | 是 |
| smoke_rl_v5_placebo | passed | 56 | 是 |
| smoke_rl_blind | passed | 46 | 是 |
| smoke_full_hf | failed | 115 | 是 |
| resume_a | passed | 60 | 是 |
| resume_b | failed | 15 | 是 |
| vllm_env | passed | 56 | 否 |
| smoke_full_vllm | failed | 165 | 否 |
| decide_runtime | failed | 0 | 是 |

## 检查

- ✅ pytest 无失败
- ✅ 私有数据与锚点一致
- ❌ 默认开启的几何规则在 train 认证正例上零误杀
- ✅ ViT/merger 冻结且只训练 LoRA
- ✅ 所有训练提示不超过预算
- ✅ 断点恢复后到达第 2 步

## 环境

- GPU：NVIDIA A100-SXM4-40GB，42.41 GB；驱动 580.82.07
- torch 2.13.0+cu130（CUDA 13.0，后端 cu130），transformers 5.19.0，trl 1.17.1，peft 0.21.2
- 模型：Qwen/Qwen2.5-VL-3B-Instruct@66285546d2b8

## CPU 测试（VM 上，GPU 已隐藏）

207 项：201 通过，0 失败，0 错误，6 跳过（125.8 秒）

## v5 几何证伪校准（默认阈值）

| 关系 | 默认开启 | 阈值 | train 认证正例 | train 误杀 | val 误杀 | 罗列断言被证伪比例 |
|---|---|---|---|---|---|---|
| PointLiesOnLine | 是 | 0.06 | 538 | 5 | 0 | 0.790 |
| Parallel | 是 | 15.0 | 19 | 1 | 0 | 0.899 |
| Perpendicular | 是 | 15.0 | 264 | 11 | 2 | 0.796 |
| PointLiesOnCircle | 是 | 0.15 | 493 | 11 | 1 | — |
| Angle | 否 | 35.0 | 427 | 3 | 0 | 0.282 |
| CongruentLength | 否 | 1.5 | 91 | 0 | 0 | — |
| CongruentAngle | 否 | 25.0 | 36 | 0 | 0 | — |

| 罗列探针 | 题数 | v4 均值 | v5 均值 | v4 高于诚实读一半 | v5 高于诚实读一半 |
|---|---|---|---|---|---|
| honest_full | 609 | 1.000 | 1.000 | 0.941 | 0.941 |
| honest_half | 609 | 0.719 | 0.569 | 0.000 | 0.000 |
| incidence_spray | 608 | 0.176 | -0.944 | 0.031 | 0.000 |
| pair_spray | 608 | 0.080 | -0.948 | 0.000 | 0.000 |
| value_spray | 449 | 0.591 | 0.065 | 0.203 | 0.143 |
| combined_spray | 608 | 0.404 | -0.973 | 0.155 | 0.000 |
| combined_spray_with_gold | 609 | 0.969 | -0.767 | 0.905 | 0.016 |

## GPU 探针（真实 3B 权重）

- 可训练参数 29933568（LoRA 目标模块 112 个），视觉参数 668684288 全部冻结：True
- 提示 token（含图像）：train 最大 1153 / p95 707，val 最大 746；预算 1600，超预算 0 条
- 微批 8（最长提示 + 1024 token 补全，前向+反向）：峰值 18.04 GB，14.33 秒，梯度有限 True
- 微批 4（最长提示 + 1024 token 补全，前向+反向）：峰值 13.09 GB，5.26 秒，梯度有限 True
- 微批 2（最长提示 + 1024 token 补全，前向+反向）：峰值 10.43 GB，2.48 秒，梯度有限 True
- HF 生成：64 条 × 1024 token，128.15 秒，511.4 token/s，峰值 24.06 GB
- ViT 占一次前向的 0.4057；缓存与不缓存的补全 log-prob 最大差 0.40537071228027344（等价：False）

## V0 探针（16 道 validation，贪心解码；工程信号，不是评测结果）

| 条件 | 协议合规 | 格式奖励 | 答案正确 | 补全长度 p50 / p90 / max | 触达长度上限 |
|---|---|---|---|---|---|
| 有图 | 0.250 | 0.250 | 0.062 | 198 / 1024 / 1024 | 0.375 |
| 无图 | 0.562 | 0.562 | 0.062 | 313 / 1024 / 1024 | 0.375 |

## GRPO 冒烟

| 运行 | 步数 | rollout 数 | 步时中位数（秒） | 峰值显存（GB） | 答案正确 | 格式 | 每条断言数 |
|---|---|---|---|---|---|---|---|
| rl_ans | 1 | 4 | 31.0 | 8.8 | 0.000 | 0.000 | 4.25 |
| rl_blind | 1 | 4 | 28.8 | 8.4 | 0.000 | 0.250 | 1.75 |
| rl_v4 | 1 | 4 | 30.2 | 8.8 | 0.000 | 0.000 | 4.25 |
| rl_v5 | 1 | 4 | 30.7 | 8.8 | 0.000 | 0.000 | 4.25 |
| rl_v5_placebo | 1 | 4 | 30.5 | 8.8 | 0.000 | 0.000 | 4.25 |
| smoke_full_hf | None | None | — | — | — | — | — |
| smoke_full_vllm | None | None | — | — | — | — | — |
| resume | 2 | 8 | 15.1 | 8.8 | 0.000 | 0.000 | 2.25 |

## Google Drive（可选；rclone，见 `drive_probe.json`）

- 结论：不可用或未通过：rclone is not on PATH (Drive persistence needs the rclone CLI, not only the mount)
- rclone：未安装；远端 `mydrive:` 已配置：否；挂载点 `/content/mydrive` 存在：否

## 冻结的运行时决策（`frozen_runtime.json`）

- 生成后端 hf；微批 8；ViT 缓存 False；梯度检查点 True
- 理由：micro-batch 8: measured fwd+bwd peak 18.0 GB <= 80% of 42.4 GB
- 理由：generation HF: no HF smoke result
- 理由：frozen-ViT cache off: ViT is 0.4057 of a forward pass, cached-vs-uncached max |dlogp| = 0.40537071228027344

## 未通过的步骤（日志末尾）

### smoke_full_hf（failed）

```text
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/content/p3/env/base/lib/python3.12/site-packages/trl/trainer/utils.py", line 1653, in _fused_forward
    backbone_outputs = getattr(self, backbone_attr)(*args, **kwargs)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/content/p3/env/base/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1778, in _wrapped_call_impl
    return self._call_impl(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/content/p3/env/base/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1789, in _call_impl
    return forward_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/content/p3/env/base/lib/python3.12/site-packages/transformers/utils/generic.py", line 943, in wrapper
    output = func(self, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/content/p3/env/base/lib/python3.12/site-packages/transformers/models/qwen2_5_vl/modeling_qwen2_5_vl.py", line 1243, in forward
    position_ids = self.compute_3d_position_ids(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/content/p3/env/base/lib/python3.12/site-packages/transformers/models/qwen2_5_vl/modeling_qwen2_5_vl.py", line 1153, in compute_3d_position_ids
    position_ids, rope_deltas = self.get_rope_index(
                                ^^^^^^^^^^^^^^^^^^^^
  File "/content/p3/env/base/lib/python3.12/site-packages/transformers/models/qwen2_5_vl/modeling_qwen2_5_vl.py", line 1054, in get_rope_index
    position_ids[:, batch_idx, attention_mask[batch_idx].bool()] = llm_positions.to(position_ids.device)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: shape mismatch: value tensor of shape [3, 889] cannot be broadcast to indexing result of shape [3, 870]

  0%|          | 0/3 [01:30<?, ?it/s]
```

### resume_b（failed）

```text

Loading weights:   0%|          | 0/824 [00:00<?, ?it/s]
Loading weights:  58%|█████▊    | 474/824 [00:00<00:00, 4737.63it/s]
Loading weights: 100%|██████████| 824/824 [00:00<00:00, 5817.01it/s]
/content/p3/env/base/lib/python3.12/site-packages/transformers/models/qwen2_vl/image_processing_qwen2_vl.py:129: FutureWarning: Passing `min_pixels` and `max_pixels` to a processor call is deprecated and will be removed in v5.23. Pass in `size={'longest_edge': xxx, 'shortest_edge': xxx} to override the target size.`
  warnings.warn(
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/content/p3/repo/scripts/training/train_rl.py", line 45, in <module>
    main()
  File "/content/p3/repo/scripts/training/train_rl.py", line 41, in main
    return run(config, ROOT, load_runtime(args.runtime), model_path=args.model_path, resume=args.resume)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/content/p3/repo/src/training/rl_entry.py", line 212, in run
    raise ValueError(f"Checkpoint identity mismatch in {changed}; start a new output directory")
ValueError: Checkpoint identity mismatch in ['lora_targets_sha256']; start a new output directory
```

### smoke_full_vllm（failed）

```text
[rank0]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/content/p3/env/vllm/lib/python3.12/site-packages/trl/trainer/utils.py", line 1653, in _fused_forward
[rank0]:     backbone_outputs = getattr(self, backbone_attr)(*args, **kwargs)
[rank0]:                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/content/p3/env/vllm/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1778, in _wrapped_call_impl
[rank0]:     return self._call_impl(*args, **kwargs)
[rank0]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/content/p3/env/vllm/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1789, in _call_impl
[rank0]:     return forward_call(*args, **kwargs)
[rank0]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/content/p3/env/vllm/lib/python3.12/site-packages/transformers/utils/generic.py", line 943, in wrapper
[rank0]:     output = func(self, *args, **kwargs)
[rank0]:              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/content/p3/env/vllm/lib/python3.12/site-packages/transformers/models/qwen2_5_vl/modeling_qwen2_5_vl.py", line 1243, in forward
[rank0]:     position_ids = self.compute_3d_position_ids(
[rank0]:                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/content/p3/env/vllm/lib/python3.12/site-packages/transformers/models/qwen2_5_vl/modeling_qwen2_5_vl.py", line 1153, in compute_3d_position_ids
[rank0]:     position_ids, rope_deltas = self.get_rope_index(
[rank0]:                                 ^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/content/p3/env/vllm/lib/python3.12/site-packages/transformers/models/qwen2_5_vl/modeling_qwen2_5_vl.py", line 1054, in get_rope_index
[rank0]:     position_ids[:, batch_idx, attention_mask[batch_idx].bool()] = llm_positions.to(position_ids.device)
[rank0]:     ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]: RuntimeError: shape mismatch: value tensor of shape [3, 535] cannot be broadcast to indexing result of shape [3, 516]

  0%|          | 0/3 [00:13<?, ?it/s]
```

### decide_runtime（failed）

```text
{"generation_backend": "hf", "per_device_train_batch_size": 8, "vision_cache": false, "rationale": ["micro-batch 8: measured fwd+bwd peak 18.0 GB <= 80% of 42.4 GB", "generation HF: no HF smoke result", "frozen-ViT cache off: ViT is 0.4057 of a forward pass, cached-vs-uncached max |dlogp| = 0.40537071228027344"], "source": "preflight preflight-20261109T064716Z-0589 (NOT DECIDED: missing measurements)"}
```

