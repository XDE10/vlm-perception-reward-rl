# Colab A100 环境与显存预算（不训练交付）

本轮只在 Windows genai-test 安装并执行 CPU 测试。下面的 Linux/CUDA/Drive 流程、实际 VL processor、模型加载、最长样本显存、视觉 rollout 与恢复全部 **未验证**。脚本不下载模型，不自动开始训练。

## 1. 固定依赖与隔离

`requirements-colab-cu126.txt` 是 Linux x86_64 / Python3.12 的候选固定**主要依赖**清单：torch2.7.1+cu126、Transformers4.57.6、TRL1.16.0、PEFT0.19.0、Pillow11.2.1等。不是已经实测的全传递依赖锁。与本地CPU torch2.14.1不同，要单独验收。bootstrap 会将实际pip freeze、pip check和collect_env留档，不能预写安装成功。

选择 torch2.7.1 cu126 是因为官方提供该组合和 Linux wheel；并非声称新框架与此组合已经实测。来源：[PyTorch 官方历史安装命令](https://pytorch.org/get-started/previous-versions/)、[官方 cu126 wheel 索引](https://download.pytorch.org/whl/cu126/torch/)。本轮只查看官方索引/说明，没有下载这些CUDA wheel或模型。

不安装/混用 Colab 全局 torchvision/torchaudio，使用隔离 venv；若后续确实需要 torchvision，必须与torch匹配（官方2.7.1对应0.22.1），另开依赖版本并验证，不能将全局残留导入当前环境。FlashAttention/vLLM/量化不是本版依赖。processor模块如果需要额外依赖会真实失败，不能静默切普通tokenizer。

## 2. Drive 与项目同步

把完整迁移包上传到自己的Drive，如 `/content/drive/MyDrive/project3`，保持项目内目录结构。不能只复制训练JSONL而漏图片或原迁移清单对应的档案。发布副本的 image_path 已是相对路径，无需修改JSONL或SHA。不要通过改路径或重算manifest来“适配Colab”。

推荐先在Notebook的Python单元执行：

```python
from google.colab import drive
drive.mount('/content/drive')
```

然后执行bash单元：

```bash
export PROJECT3_DRIVE_ROOT=/content/drive/MyDrive/project3
export PROJECT3_SESSION_ROOT=/content/project3
bash "$PROJECT3_DRIVE_ROOT/reports/handover_20261024_v2/colab_bootstrap.sh"
```

也提供 `colab_bootstrap.ipynb`，含Drive挂载与调用bootstrap的单元。shell脚本会在未挂载时尝试挂载；如果Colab要求Notebook交互，则明确失败并提示执行上面的Python单元，不绕过登录。

bootstrap 用 rsync 把完整包复制到会话磁盘，排除虚拟环境和新增盲审/揭盲目录，避免训练期间经Drive读取大量小图片。原迁移清单对应的zip档案仍复制，确保verify_migration存在性/大小检查可通过。这样磁盘占用较大，运行前先用 `du -sh` 和 `df -h` 检查；本轮未测传输速度或磁盘容量。

不建议为节省空间删原迁移清单项；如果后续确需轻量运行包，应作为新的迁移规格实现验证器，不能在本轮改动现有manifest。blind/key并非训练输入，不需要传到Colab；发外部审查者更应只发blind_review_only.zip。

## 3. 启动前校验

```bash
cd /content/project3
PY=/content/project3-env/bin/python
"$PY" -m pip check
"$PY" -m torch.utils.collect_env
nvidia-smi
"$PY" tools/verify_migration.py
# 若时间允许，额外复核原迁移所有档案SHA：
"$PY" tools/verify_migration.py --full
```

普通verify_migration本身逐行检查691张运行图片的文件SHA；必须在每次正式运行前通过。CPU本轮完整校验4258个原清单文件通过。当前Colab执行 **未验证**，不能因为配置使用正斜杠就声称Linux已跑通。

环境产物在 `reports/handover_20261024_v2/colab_environment/`：install.log、pip_check.log、pip_freeze.txt、collect_env.txt、nvidia-smi.txt、verify_migration.log、readme_tests.log。依赖冲突时保留日志，不修改其他环境，不用 --no-deps 强行盖过约束。

bootstrap不下载模型。未来另行准备与固定revision一致的本地权重和processor缓存后，所有v2模型入口均 local_files_only=True；缓存不全会失败。可通过独立HF_HOME挂载用户自己的缓存，不能用“main”代替revision。

## 4. 最长样本和监督token

先用已缓存processor、不加载模型，枚举609题的真实assistant labels数：

```bash
"$PY" -m reports.handover_20261024_v2.count_vl_supervision \
  --processor Qwen/Qwen2.5-VL-3B-Instruct \
  --revision 66285546d2b821cf421d4f5eb2576359d3770cd3 \
  --output reports/handover_20261024_v2/vl_supervision_counts.json
```

上次接手目录的 `gpu_acceptance_probe.py` 检查的是旧perception-only collator；它不能直接代替新V1/V2协议的最终最长样本验收。本版计数器记录完整展开长度，拒绝超过3800；要在GPU上按新collator分别选最长样本，再记录前后向loss/梯度/显存。当前这项GPU检查 **未验证**，不能套旧脚本结果。

新RL入口先对全部训练题实际展开prompt并要求≤1752，生成上限2048，二者预算合计3800。当前安装的TRL1.16.0没有max_prompt_length配置参数，代码执行自己的processor预检；实际图像展开与TRL的多模态路径是否一致仍须GPU核对。超长就拒绝，不把图片/题目截断后继续。

## 5. A100 40GB 显存估算与建议配置

按40GB显存做规划；实际Colab分配何种A100及可用容量由nvidia-smi确认，本轮未验。NVIDIA官方A100资料包含40GB/80GB及BF16支持：[A100 数据表](https://images.nvidia.com/data-center/a100/a100-datasheet.pdf)。以下是工程区间估算，不是性能测量或可运行保证。

图片预算802816像素。安装的Transformers4.57.6 Qwen2-VL图像处理代码默认patch_size=14、merge_size=2（`transformers/models/qwen2_vl/image_processing_qwen2_vl.py:110–135`），按该假设每张图约不超过 `802816/(14×2)^2=1024` 个融合图像tokens；实际resize取整、processor配置与grid应实测，**未验证**。原始视觉patch还未合并时更多，不能只用融合token估算视觉encoder激活。

以总参数约3～4B量级估算BF16冻结权重约6～8GB（具体固定模型总参数未加载核实）。语言LoRA rank16的梯度/Adam状态通常远小于全参优化器，但必须用requires_grad实际计数；例如30M可训练参数，按参数/梯度/FP32双动量及可能的master copy粗算约0.4～0.5GB。这里30M是算例，不是已测参数数。

SFT：batch1、最长总序列3800、SDPA、BF16、梯度检查点，预留激活/视觉中间张量约8～18GB、logits与工作区/分配器约3～8GB，加权重后粗估 **18～35GB**。长图/框架实现可能超出该区间，不能据此承诺40GB必过。

GRPO：每题4条、prompt≤1752、completion≤2048，KV cache、四条回答的log-prob计算与激活会放大峰值。粗估 **24～40GB以上**。以词表150k、3800tokens算例，单条BF16完整logits约1.14GB，四条约4.56GB，若中间转FP32还会更多；实际TRL的chunking/保留策略未测。KL参考通过同V0底座禁用LoRA的行为也要实测，若误复制完整参考权重还会增加6～8GB。

建议先保持匹配配置：batch1、gradient_accumulation_steps8、rank16、BF16、SDPA、gradient_checkpointing、group4、无vLLM。先做最长样本及4条rollout峰值验收；若OOM，两臂一起调整生成预算、像素或分块策略并建立新版本。不能只给V4缩图/缩生成，也不能为过smoke静默删除困难样本。若降像素，必须另检查小字/角标可读性。上述显存区间 **未验证**。

## 6. 新视觉诊断与恢复身份

```bash
"$PY" -m reports.handover_20261024_v2.diagnose_project3_vision_v2 \
  --data data/portable_release/project3_validation_fact_pruned.jsonl \
  --output reports/handover_20261024_v2/runs/v0_validation_v2.jsonl
```

此版使用与新训练一致的perception/answer协议；原boxed版脚本仍保留，二者不能直接混算。v2在模型加载前写identity，失败/中断也更新状态；记录adapter目录逐文件SHA，默认adapter=null，明确区别基座/adapter。同时保存token数、EOS/预算耗尽和视觉tensor键。adapter路径或SHA改变必须新输出，不能覆盖旧身份。

实际VL诊断 **未验证**；当前只测试identity先写与权重指纹的结构行为。A100上仍需验证82×4配对、真正无图、标准答案评分失败列表和checkpoint优化器/scheduler/RNG恢复。遮挡只是输入扰动，不能当几何真值保持测试。
