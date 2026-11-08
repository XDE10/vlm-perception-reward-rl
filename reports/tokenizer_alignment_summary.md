# 四模型真实词表审计

共同有效 ID 数量：151665；连续边界：151665。
逐项 token→ID 差异数：0；编码案例：64。
裸文本全部一致：True；chat template 编码全部一致：False。

- Qwen/Qwen2.5-1.5B-Instruct: config=151936, len=151665, revision=989aa7980e4cf806f80c7fef2b1adb7bc71aa306
- Qwen/Qwen2.5-Math-7B-Instruct: config=152064, len=151665, revision=ef9926d75ab1d54532f6a30dd5e760355eb9aa4d
- Qwen/Qwen2.5-Coder-7B-Instruct: config=152064, len=151665, revision=c03e6d358207e414f1eca0bb1891e29f1db0e242
- Qwen/Qwen2.5-7B-Instruct: config=152064, len=151665, revision=a09a35458c702b33eeacc393d103063234e8bc28

Slice [:N] only for these audited revisions; mask all other output rows BEFORE generation, then independently renormalize teacher/student probabilities on common support. Track removed probability mass on real logits before masking. No real-logit mass measured tonight.

本轮不加载模型，不能测实际尾部概率质量，也不证明 GPU 蒸馏已可运行。

## 2026-10-23 离线复验

固定revision的文件SHA、完整映射与64例编码已重新检查通过；Math默认chat模板仍与学生不同。使用学生模板产生同一前缀ID，采样前屏蔽支持集外行，再对共同支持集FP32归一化。详见 	okenizer_alignment_revalidation_20261023.json 与 project1_sft_pretraining_audit_20261023.md。没有加载权重或测真实logits尾部质量。
