# 夜间 CPU 基础设施开发记录

执行日期：2026-10-23（Asia/Shanghai）。状态：四项 CPU 交付已完成，最终验收通过。

约束：CPU；禁止模型权重下载；禁止付费 API；所有合成测试使用 Mock。
开发顺序：任务 3 → 任务 1 → 任务 2 → 任务 4。

运行环境复用 `python`（CPU PyTorch），不修改旧实验。
各项完成后追加实测结果，最终附完整 pytest 日志。

## 任务 3：核心算子首轮完成

- 实现：`src/losses/reference.py`；测试：`tests/test_losses_and_masks.py`。
- `pytest -q tests/test_losses_and_masks.py`：11 passed（5.22 秒），完整输出 `reports/task3_pytest.log`。
- 覆盖 SFT target shift、prompt/padding 零梯度、回答/EOS 梯度；全同奖励无 NaN；长短回答两种归一化的精确梯度；FKL/RKL、大矩阵形状、教师停止梯度、固定权重融合梯度一致及双精度 gradcheck。
- 首轮大矩阵测试使用合成支持集；任务 1 完成后必须用真实审计共同 ID 集再次验收。

## 任务 1：真实词表审计完成，任务 3 二次验收完成

- 四模型 tokenizer/config 已下载到 `data/tokenizers/`，精确 revision 与文件 SHA256 在 `reports/tokenizer_alignment_report.json`。
- 共同支持 151665，ID 0～151664，完整 token→ID 映射无差异；64 条裸文本编码一致，chat template 编码不全一致。
- 学生 config 151936；Math/Coder/通用 7B config 152064；四者 len(tokenizer) 均 151665。
- 有效边界可切片 [:151665]，但须统一前缀编码、屏蔽无效输出行并在共同支持上重新归一化；未加载权重，未测尾部真实概率质量。
- 已用真实共同支持重跑 151936/152064 大矩阵 FKL/RKL 测试。
- 14 passed（4.90 秒），日志 `reports/task1_real_pytest.log`；可读报告 `reports/tokenizer_alignment_summary.md`。

## 任务 2：真实数学数据与判分器完成

- 下载 GSM8K train/test=7473/1319；MATH-lighteval train/test=7500/5000；MATH-500 test=500，revision/字段见 `data/math_manifest.json`。
- MATH train 封存 dev=256，保留 train=7184，隔离=60（49 条内部重复/近重复，11 条命中评测参考集）。全部隔离证据保存在 `data/math/math_quarantine.jsonl`。
- 规范化 SHA256＋token 三元组 Jaccard>=0.85；固定 seed=42；不宣称消除语义或预训练污染。
- 两条源数据使用单 token TeX `\\boxed 2/9`，新增显式支持及回归测试，没有从普通推理正文猜答案。
- 判分器包含受限 AST 表达式解析、数值/表达式等价、平衡花括号、冲突答案和截断拒绝；无 eval；不是完整官方 MATH 判分协议。
- 43 passed（4.07 秒），含 39 项判分器用例和真实产物验收，日志 `reports/task2_real_pytest.log`。
- 数据脚本执行日志 `reports/math_data_execution.log`；JSONL 在 `data/math/`，所有文件 SHA256 在 manifest。
- 验证时修正 JSONL 读取方式：使用 LF 文件迭代，避免 str.splitlines 将源文本合法的 Unicode U+2028 错拆为新记录。

## 任务 4：客户端与几何解析器首轮完成

- `src/synthesis/async_client.py`：默认 dry-run，不包含网络/API 实现；非 dry-run 仅接受本地 MockTransport。SQLite 主缓存、原子 JSONL 快照及恢复、有限重试、速率限制、跨重启预算账本、每题最多三次盲生成。
- `src/evaluation/geometry_perception_parser.py`：三段结构、固定关系优先级/实体字典序、无向关系规范化、顶点/有向角色保持、冲突拒绝、去重与覆盖范围内感知 F1。
- 客户端 9 passed（0.45 秒），日志 `reports/task4_client_pytest.log`；几何 19 passed（0.08 秒），日志 `reports/task4_geometry_pytest.log`。
- 无图像、无人工视觉标注被自动宣布可信；几何评分只衡量给定可信标注的一致性。

<!-- FINAL_AUDIT -->
## 最终验收

完整命令 `python -m pytest tests -v`：**87 passed in 7.72s**，无失败、无跳过。
真实数据与词表脚本均已执行；Mock 端到端示例已执行并保存 SQLite/JSONL 缓存。
付费 API 调用 0；模型权重下载 0；GPU 训练 0。使用 CPU 专版 torch（CUDA version=None）。
最终核验结果：`reports/completion_audit.json`；环境：`reports/cpu_environment.json`。

### 最终数据行数

- `math_train`：7184 行，路径 `data/math/math_train.jsonl`。
- `math_dev`：256 行，路径 `data/math/math_dev.jsonl`。
- `math_quarantine`：60 行，路径 `data/math/math_quarantine.jsonl`。
- `gsm8k_train`：7473 行，路径 `data/math/gsm8k_train.jsonl`。
- `gsm8k_test`：1319 行，路径 `data/math/gsm8k_test.jsonl`。
- `math500_test`：500 行，路径 `data/math/math500_test.jsonl`。
- `math_source_test`：5000 行，路径 `data/math/math_source_test.jsonl`。

### 词表核心结论

四模型 len(tokenizer)=151665；学生输出矩阵 151936 行，其余三模型 152064 行。共同有效 ID 为 0～151664。
64 条裸文本编码一致，64 条应用各自 chat template 后均出现组间差异。必须固定学生原始 token 前缀，不能独立渲染模板后直接对齐。
共同支持上切片并重新归一化；生成前屏蔽已确认无效行。没有加载权重，尚无尾部概率质量的真实测量。

### 额外恢复与边界检查

- 验证器崩溃后复用已落盘输出；跨重启预算累计；JSONL 可恢复 SQLite；重复并发任务只执行一次 Mock。
- 原文 SHA256、规范化 SHA256 与近重复检测分别留证；独立测试检查 train 与 dev/test 仍无当前规则下重叠。
- 受限表达式解析防止 eval、恶意调用和嵌套大整数幂；不是覆盖所有数学对象的官方判分器。
- 几何 F1 防重复刷分，支持关系反序规范化、冲突拒绝；不完整标注按覆盖类别处理，无可信标签时感知项关闭。
- 四个设计文件未修改，旧 tiny_posttrain 源码和历史结果未改动；当前借用其现有 CPU 虚拟环境。

### 文件清单

以下为源文件、测试、脚本、数据与报告的实际路径（不列 Python bytecode 和下载器内部 .cache）；逐文件 SHA256 见 `reports/artifact_inventory.json`。

- `src/__init__.py`
- `src/data/__init__.py`
- `src/data/prepare_math_data.py`
- `src/evaluation/__init__.py`
- `src/evaluation/geometry_perception_parser.py`
- `src/evaluation/math_verifier.py`
- `src/losses/__init__.py`
- `src/losses/reference.py`
- `src/synthesis/__init__.py`
- `src/synthesis/async_client.py`
- `src/teachers/__init__.py`
- `src/teachers/tokenizer_audit.py`
- `tests/test_delivery_artifacts.py`
- `tests/test_geometry_parser.py`
- `tests/test_losses_and_masks.py`
- `tests/test_math_data.py`
- `tests/test_math_data_integration.py`
- `tests/test_math_verifier.py`
- `tests/test_synthesis_client.py`
- `tests/test_tokenizer_audit.py`
- `tests/test_tokenizer_integration.py`
- `scripts/finalize_overnight_report.py`
- `scripts/run_cpu_demo.py`
- `data/math/gsm8k_test.jsonl`
- `data/math/gsm8k_train.jsonl`
- `data/math/math500_test.jsonl`
- `data/math/math_dev.jsonl`
- `data/math/math_quarantine.jsonl`
- `data/math/math_source_test.jsonl`
- `data/math/math_train.jsonl`
- `data/math_manifest.json`
- `data/raw_math_cache/DigitalLearningGmbH___math-lighteval/default/0.0.0/0530c78699ea5e8eb5530600900e1f328b48acad/dataset_info.json`
- `data/raw_math_cache/DigitalLearningGmbH___math-lighteval/default/0.0.0/0530c78699ea5e8eb5530600900e1f328b48acad/math-lighteval-test.arrow`
- `data/raw_math_cache/DigitalLearningGmbH___math-lighteval/default/0.0.0/0530c78699ea5e8eb5530600900e1f328b48acad/math-lighteval-train.arrow`
- `data/raw_math_cache/HuggingFaceH4___math-500/default/0.0.0/6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be/dataset_info.json`
- `data/raw_math_cache/HuggingFaceH4___math-500/default/0.0.0/6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be/math-500-test.arrow`
- `data/raw_math_cache/openai___gsm8k/main/0.0.0/740312add88f781978c0658806c59bc2815b9866/dataset_info.json`
- `data/raw_math_cache/openai___gsm8k/main/0.0.0/740312add88f781978c0658806c59bc2815b9866/gsm8k-test.arrow`
- `data/raw_math_cache/openai___gsm8k/main/0.0.0/740312add88f781978c0658806c59bc2815b9866/gsm8k-train.arrow`
- `data/synthesis_mock/cache.jsonl`
- `data/synthesis_mock/cache.sqlite`
- `data/tokenizers/Qwen2.5-1.5B-Instruct/config.json`
- `data/tokenizers/Qwen2.5-1.5B-Instruct/merges.txt`
- `data/tokenizers/Qwen2.5-1.5B-Instruct/tokenizer.json`
- `data/tokenizers/Qwen2.5-1.5B-Instruct/tokenizer_config.json`
- `data/tokenizers/Qwen2.5-1.5B-Instruct/vocab.json`
- `data/tokenizers/Qwen2.5-7B-Instruct/config.json`
- `data/tokenizers/Qwen2.5-7B-Instruct/merges.txt`
- `data/tokenizers/Qwen2.5-7B-Instruct/tokenizer.json`
- `data/tokenizers/Qwen2.5-7B-Instruct/tokenizer_config.json`
- `data/tokenizers/Qwen2.5-7B-Instruct/vocab.json`
- `data/tokenizers/Qwen2.5-Coder-7B-Instruct/config.json`
- `data/tokenizers/Qwen2.5-Coder-7B-Instruct/merges.txt`
- `data/tokenizers/Qwen2.5-Coder-7B-Instruct/tokenizer.json`
- `data/tokenizers/Qwen2.5-Coder-7B-Instruct/tokenizer_config.json`
- `data/tokenizers/Qwen2.5-Coder-7B-Instruct/vocab.json`
- `data/tokenizers/Qwen2.5-Math-7B-Instruct/config.json`
- `data/tokenizers/Qwen2.5-Math-7B-Instruct/merges.txt`
- `data/tokenizers/Qwen2.5-Math-7B-Instruct/tokenizer.json`
- `data/tokenizers/Qwen2.5-Math-7B-Instruct/tokenizer_config.json`
- `data/tokenizers/Qwen2.5-Math-7B-Instruct/vocab.json`
- `reports/completion_audit.json`
- `reports/cpu_demo.json`
- `reports/cpu_demo_execution.log`
- `reports/cpu_environment.json`
- `reports/hardening_pytest.log`
- `reports/hf_connectivity.log`
- `reports/math_data_execution.log`
- `reports/math_reference_diagnostic.log`
- `reports/metadata_hardening_pytest.log`
- `reports/pytest_full.log`
- `reports/task1_real_pytest.log`
- `reports/task1_unit_pytest.log`
- `reports/task2_real_pytest.log`
- `reports/task2_source_fix_pytest.log`
- `reports/task2_unit_pytest.log`
- `reports/task2_verifier_pytest.log`
- `reports/task3_pytest.log`
- `reports/task4_client_pytest.log`
- `reports/task4_geometry_pytest.log`
- `reports/tokenizer_alignment_report.json`
- `reports/tokenizer_alignment_summary.md`
- `reports/tokenizer_audit_execution.log`
- `pytest.ini`
- `OVERNIGHT_CPU_README.md`
- `reports/artifact_inventory.json`
- `reports/overnight_execution_summary.md`

### pytest -v 完整原始输出

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-8.4.2, pluggy-1.7.0 -- D:\Users\Mr.Z\Desktop\modern_genai\python
cachedir: .pytest_cache
rootdir: D:\Users\Mr.Z\Desktop\modern_genai
configfile: pytest.ini
plugins: anyio-4.15.1, platformdirs-4.13.5
collecting ... collected 87 items

tests/test_delivery_artifacts.py::test_offline_demo_and_cpu_environment PASSED [  1%]
tests/test_geometry_parser.py::test_canonical_order_permutations_roundtrip_idempotence PASSED [  2%]
tests/test_geometry_parser.py::test_duplicate_and_reverse_entity_attack PASSED [  3%]
tests/test_geometry_parser.py::test_hallucination_penalty_in_complete_categories PASSED [  4%]
tests/test_geometry_parser.py::test_uncovered_relations_and_missing_labels_not_rewarded_as_full_score PASSED [  5%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Length(A,B)=5;Length(B,A)=6] PASSED [  6%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Angle(A,B,C)=30;Angle(C,B,A)=60] PASSED [  8%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Parallel(AB,CD);Perpendicular(DC,BA)] PASSED [  9%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[FakeRelation(AB,CD)] PASSED [ 10%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Length(A,A)=5] PASSED [ 11%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Angle(A,A,B)=30] PASSED [ 12%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Length(A,B)=-2] PASSED [ 13%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Length(A,B)=1/0] PASSED [ 14%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Length(A,B)=5deg] PASSED [ 16%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Tangent(O,AB)] PASSED [ 17%]
tests/test_geometry_parser.py::test_invalid_and_conflicting_facts_cannot_score[Perpendicular(AB,AB)] PASSED [ 18%]
tests/test_geometry_parser.py::test_vertex_directed_roles_and_tangent_roles_preserved PASSED [ 19%]
tests/test_geometry_parser.py::test_units_values_and_normalization PASSED [ 20%]
tests/test_geometry_parser.py::test_response_three_sections PASSED       [ 21%]
tests/test_geometry_parser.py::test_empty_predictions_and_coverage_errors PASSED [ 22%]
tests/test_losses_and_masks.py::test_shift_prompt_padding_eos_gradients PASSED [ 24%]
tests/test_losses_and_masks.py::test_equal_rewards[grpo-0.0] PASSED      [ 25%]
tests/test_losses_and_masks.py::test_equal_rewards[grpo-1.0] PASSED      [ 26%]
tests/test_losses_and_masks.py::test_equal_rewards[dr_grpo-0.0] PASSED   [ 27%]
tests/test_losses_and_masks.py::test_equal_rewards[dr_grpo-1.0] PASSED   [ 28%]
tests/test_losses_and_masks.py::test_advantage_and_length_gradient PASSED [ 29%]
tests/test_losses_and_masks.py::test_ratio_clipping PASSED               [ 31%]
tests/test_losses_and_masks.py::test_large_vocabulary_alignment[forward] PASSED [ 32%]
tests/test_losses_and_masks.py::test_large_vocabulary_alignment[reverse] PASSED [ 33%]
tests/test_losses_and_masks.py::test_weighted_teacher_fkl_gradient_identity PASSED [ 34%]
tests/test_losses_and_masks.py::test_kl_mapping_padding_and_gradcheck PASSED [ 35%]
tests/test_math_data.py::test_exact_and_similarity_and_distinct_questions PASSED [ 36%]
tests/test_math_data.py::test_partition_is_reproducible_disjoint_and_excludes_test_near_duplicates PASSED [ 37%]
tests/test_math_data.py::test_source_answer_nested_box_and_missing_gold PASSED [ 39%]
tests/test_math_data_integration.py::test_real_data_manifest_and_sealed_splits PASSED [ 40%]
tests/test_math_verifier.py::test_adversarial_answers[#### 1/2-0.5-True] PASSED [ 41%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{\\frac{1}{2}}-0.5-True] PASSED [ 42%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{\\sqrt{2}}-sqrt(2)-True] PASSED [ 43%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{\\frac{\\sqrt{8}}{2}}-sqrt(2)-True] PASSED [ 44%]
tests/test_math_verifier.py::test_adversarial_answers[#### -42--42-True] PASSED [ 45%]
tests/test_math_verifier.py::test_adversarial_answers[#### \u22123.5--7/2-True] PASSED [ 47%]
tests/test_math_verifier.py::test_adversarial_answers[#### $1,234.50-1234.5-True] PASSED [ 48%]
tests/test_math_verifier.py::test_adversarial_answers[#### 25 cm-25-True] PASSED [ 49%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{12\\text{ ounces}}-12-False] PASSED [ 50%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{12\\text{ounces}}-12-True] PASSED [ 51%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{\\boxed{2}}-2-True] PASSED [ 52%]
tests/test_math_verifier.py::test_adversarial_answers[#### 2\n#### 3-2-False] PASSED [ 54%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{2} and \\boxed{3}-2-False] PASSED [ 55%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{\\frac{1}{2}} and \\boxed{0.5}-1/2-True] PASSED [ 56%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{\\frac{1}{2}-1/2-False] PASSED [ 57%]
tests/test_math_verifier.py::test_adversarial_answers[####-0-False] PASSED [ 58%]
tests/test_math_verifier.py::test_adversarial_answers[-0-False] PASSED   [ 59%]
tests/test_math_verifier.py::test_adversarial_answers[#### 1,2-12-False] PASSED [ 60%]
tests/test_math_verifier.py::test_adversarial_answers[#### 1/0-0-False] PASSED [ 62%]
tests/test_math_verifier.py::test_adversarial_answers[#### 2 or 3-2-False] PASSED [ 63%]
tests/test_math_verifier.py::test_adversarial_answers[The answer is 2 or 3-2-False] PASSED [ 64%]
tests/test_math_verifier.py::test_adversarial_answers[#### Final Answer: $26-26-True] PASSED [ 65%]
tests/test_math_verifier.py::test_adversarial_answers[#### 5\nExplanation follows.-5-True] PASSED [ 66%]
tests/test_math_verifier.py::test_adversarial_answers[Working: 2+3=5-5-False] PASSED [ 67%]
tests/test_math_verifier.py::test_adversarial_answers[#### __import__("os").system("whoami")-0-False] PASSED [ 68%]
tests/test_math_verifier.py::test_adversarial_answers[#### 9**999999-9-False] PASSED [ 70%]
tests/test_math_verifier.py::test_adversarial_answers[#### nan-0-False] PASSED [ 71%]
tests/test_math_verifier.py::test_adversarial_answers[#### 1e309-0-False] PASSED [ 72%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{x^2+2*x+1}-(x+1)^2-True] PASSED [ 73%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{-\\frac{3}{4}}--0.75-True] PASSED [ 74%]
tests/test_math_verifier.py::test_adversarial_answers[#### 50%-0.5-False] PASSED [ 75%]
tests/test_math_verifier.py::test_adversarial_answers[#### 2 cm-0.02-False] PASSED [ 77%]
tests/test_math_verifier.py::test_adversarial_answers[#### 2-3-False] PASSED [ 78%]
tests/test_math_verifier.py::test_adversarial_answers[#### 2 and 2-2-False] PASSED [ 79%]
tests/test_math_verifier.py::test_adversarial_answers[\\boxed{\\frac{1}{\\frac{2}{3}}}-3/2-True] PASSED [ 80%]
tests/test_math_verifier.py::test_adversarial_answers[#### True-1-False] PASSED [ 81%]
tests/test_math_verifier.py::test_adversarial_answers[#### [2]-2-False] PASSED [ 82%]
tests/test_math_verifier.py::test_truncation_is_not_success PASSED       [ 83%]
tests/test_math_verifier.py::test_bound_and_unsupported_syntax PASSED    [ 85%]
tests/test_synthesis_client.py::test_dry_run_never_dispatches_and_rejects_reference_fields PASSED [ 86%]
tests/test_synthesis_client.py::test_blind_resampling_caps_and_persistent_cache PASSED [ 87%]
tests/test_synthesis_client.py::test_wrong_generations_stop_at_three_and_do_not_send_verifier_feedback PASSED [ 88%]
tests/test_synthesis_client.py::test_retry_backoff_rate_limit_and_transport_count PASSED [ 89%]
tests/test_synthesis_client.py::test_persistent_budget_ceiling[1-100] PASSED [ 90%]
tests/test_synthesis_client.py::test_persistent_budget_ceiling[100-10] PASSED [ 91%]
tests/test_synthesis_client.py::test_jsonl_restores_cache_and_budget PASSED [ 93%]
tests/test_synthesis_client.py::test_concurrent_duplicate_jobs_only_dispatch_once PASSED [ 94%]
tests/test_synthesis_client.py::test_cache_identity_changes_with_model_sampling_verifier PASSED [ 95%]
tests/test_synthesis_client.py::test_verifier_failure_restarts_from_saved_output_without_regeneration PASSED [ 96%]
tests/test_tokenizer_audit.py::test_audit_corpus_and_download_allowlist PASSED [ 97%]
tests/test_tokenizer_audit.py::test_mapping_detects_gaps_misalignments_and_extra_tokens PASSED [ 98%]
tests/test_tokenizer_integration.py::test_real_four_model_audit PASSED   [100%]

============================= 87 passed in 7.72s ==============================
```

### 尚未验证边界

不包含 GPU 训练、真实 logits 尾部质量、付费合成、真实图像标签质量、真实 OPD 性能或训练收益。
词法去重不能证明消除语义/预训练污染；几何 parser 仅注册 schema；数学 verifier 有意拒绝不支持的对象和不明确的答案。
后续运行说明：`OVERNIGHT_CPU_README.md`。
