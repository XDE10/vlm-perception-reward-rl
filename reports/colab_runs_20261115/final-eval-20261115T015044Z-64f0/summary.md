# Colab 运行摘要：final-eval-20261115T015044Z-64f0（final-eval）

总体结论：**未通过**

## 步骤

| 步骤 | 状态 | 用时（秒） | 计入结论 |
|---|---|---|---|
| env_report | passed | 2 | 是 |
| verify_pack | passed | 0 | 是 |
| public_sources | passed | 4 | 是 |
| final_eval | failed | 0 | 是 |

## 检查

- ✅ 私有数据与锚点一致

## 环境

- GPU：NVIDIA A100-SXM4-40GB，42.41 GB；驱动 580.82.07
- torch 2.13.0+cu130（CUDA 13.0，后端 cu130），transformers 5.19.0，trl 1.17.1，peft 0.21.2
- 模型：Qwen/Qwen2.5-VL-3B-Instruct@66285546d2b8

## 结果推送到 GitHub（D37）

- 由你本机的运行器推送；VM 端未推送的原因：no credential file at /content/gh_credentials, so the launcher pushes the results from your machine (to let the VM push, see colab/README.md section 8)

## 未通过的步骤（日志末尾）

### final_eval（failed）

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/content/p3/repo/scripts/colab/final_eval.py", line 184, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/content/p3/repo/scripts/colab/final_eval.py", line 146, in main
    raise RuntimeError(f"S5 needs the S4 Drive store: {info.get('reason')}")
RuntimeError: S5 needs the S4 Drive store: None
```

