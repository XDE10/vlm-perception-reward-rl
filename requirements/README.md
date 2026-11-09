# requirements/ 目录说明

这些文件是**环境记录/参考依赖**，不是锁文件，也不覆盖 CUDA 安装。

| 文件 | 来源 | 用途 |
| --- | --- | --- |
| `cpu-snapshot.txt` | 旧 CPU 环境导出（迁移前） | 复现历史 CPU 审计/测试环境；含 torch/transformers 等的当时版本 |
| `project3-cpu.txt` | 项目三 CPU 审计/测试的参考依赖 | 只跑数据准入、序列化、解析等 CPU 测试 |
| `dev-cpu.txt` | 2026-11-09 协议 v3 RL 代码的 CPU 开发/测试环境（Python 3.12.13 实测） | 跑全部 CPU 测试，含 tiny Qwen2.5-VL + TRL GRPO 端到端；版本选择理由见 [决策记录 D1](../docs/plan/决策记录.md) |
| `colab-gpu.txt` / `colab-gpu-vllm.txt` | 2026-11-10 Colab GPU 环境的直接依赖（vLLM 版本另放一份，只在单独的 venv 中探测） | 锁文件的来源，不直接安装 |
| `locks/colab-gpu-<cu130\|cu129\|cu126>.txt`、`locks/colab-gpu-vllm-cu130.txt` | 用 `uv pip compile`（Linux x86_64、Python 3.12）预先解析出的完整依赖集 | Colab 运行器按驱动的 CUDA 版本选其一，用 `uv pip install --torch-backend <后端> -r <锁文件>` 安装；见 [决策记录 D20、D21](../docs/plan/决策记录.md) |

重新生成锁文件（只在有意升级依赖时）：

```bash
uv pip compile requirements/colab-gpu.txt --python-version 3.12 --python-platform x86_64-unknown-linux-gnu \
  --torch-backend cu130 --no-header -o requirements/locks/colab-gpu-cu130.txt   # cu129、cu126 同理
```

- 历史 CPU 验证基于 Python 3.12；本机（2026-11-08）用 Python 3.11.4 复跑得到
  68 passed / 2 failed（缺 `math_verify`、`trl`）。两者都要如实记录，不能把
  其一当成另一环境的结果。
- GPU 环境（PyTorch/CUDA、TRL、PEFT、Accelerate）需按目标机器另行固定版本并在
  该机器验收；CPU 包清单不能证明 GPU 可运行。
- 安装示例与训练入口见 [docs/training.md](../docs/training.md)；测试基线与
  报告规范见 [docs/verification.md](../docs/verification.md)。
- 不通过修改本目录跳过依赖检查；缺包就记录缺包。
