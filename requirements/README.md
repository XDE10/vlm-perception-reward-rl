# 协议 v3 依赖

基础仓库校验使用 Python 3.10+ 标准库。模型相关路径使用 Python 3.12。Linux 或 WSL 维护者可以用 CPU 环境运行测试。

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --torch-backend cpu -r requirements/dev-cpu.txt
.venv/bin/python -m pytest -q
```

Colab 的 [bootstrap](../scripts/colab/bootstrap.py) 按驱动选择 [locks/](locks/) 内的 GPU 锁文件。登记任务使用冻结的 vLLM CUDA 13.0 环境。本地相同硬件可使用下面的命令安装。

```bash
uv venv --python 3.12 .venv-gpu
uv pip install --python .venv-gpu/bin/python --torch-backend cu130 -r requirements/locks/colab-gpu-vllm-cu130.txt
```

Shuffle-R1 使用单独的 CUDA 12.8 环境，见 [安装说明](../shuffle_r1/README.md)。
