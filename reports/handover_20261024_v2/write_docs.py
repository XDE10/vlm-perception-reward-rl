"""Generate review documentation from measured v2 artifacts, no external access."""
import ast
import json
import re
from pathlib import Path
OUT=Path(__file__).resolve().parent


def main():
    scale=json.loads((OUT/'answer_pool_scale.json').read_text(encoding='utf8'))
    token=json.loads((OUT/'supervision_token_counts.json').read_text(encoding='utf8'))['counts']
    sample=json.loads((OUT/'sampling_report.json').read_text(encoding='utf8'))
    prompts=json.loads((OUT/'audit_prompts.json').read_text(encoding='utf8'))
    readme='''# 多模态几何推理 v2：配对协议、离线校验与盲审交付

日期：2026-10-24。根目录命令均为 bash，从项目根执行。此目录是新版本；原始训练器、评分器、数据、manifest、批准字段、图片、划分与 SHA 不修改。原 README 保留为历史入口，本 README 是本轮新入口。

本轮未下载模型、未调用付费 API、未启动 GPU 训练。api_calls=0。代码和 tiny/结构检查通过不代表真实 VL、CUDA、Colab 或研究效果已经验收；这些均为 **未验证**。盲审包尚未填写，当前不能给误杀率/误放率结果。

## 1. 入口与交付

- `configs/v3_v0_answer_format.json` / `v4_v0_perception.json`：V0 起点的配对 smoke 草稿，只有 perception_reward_weight 不同。
- `train.py`：新版本入口，三项独立奖励，逐条落盘；原训练器保留。
- `project3_v2.py`：共享 prompt、V1/V2 监督视图、collator、奖励记录与参数身份。
- `strict_geometry.py`：独立 strict-v5；冻结 v4 未改。运行时并行记录新旧结果。
- `blind/` 与 `blind_review_only.zip`：唯一可发给外部审查者的材料。不要附带父目录文件。
- `key/key.jsonl`、sample_manifest.json、sampling_report.json、numeric_id_coincidences_PRIVATE.json：**私有揭盲材料，不得发给外部审查者**。
- `规模与审核口径.md`、`Colab运行说明.md`、`CHANGELOG.md`：规模、部署与边界说明。
- 测试、安装、pip check/freeze、迁移和采样日志保存在本目录。早期失败日志保留，最终结果以验收记录为准。

## 2. genai-test 环境

实际解释器为 `D:/anaconda3/envs/genai-test/python.exe`，Python 3.12.15。本轮只对此环境安装。前两次安装分别遇 NumPy 和 PEFT 的 WinError32 文件锁；后续安装命令正常结束、import/API 检查通过。未设置 --user、未修改其他环境、未改 PATH。

固定主要版本：torch 2.14.1+cpu、transformers 4.57.6、TRL 1.16.0、PEFT 0.19.0、Pillow 11.2.1。最终 `pip_check.log` 为 No broken requirements found；完整版本为 pip_freeze.txt。README 原四文件测试已从上一轮 14/1 恢复为 **15 passed**，未修改原测试。新增测试及最终合并结果见验收记录。

```bash
conda activate genai-test
python -m pip check
python -m pytest tests/test_approved_training_inputs.py tests/test_training_entries_cpu.py tests/test_perception_v4.py tests/test_geometry_model_serialization.py -q
python -m pytest reports/handover_20261024_v2/test_project3_v2.py -q
python tools/verify_migration.py --full
```

Windows 的 conda shell 函数若未初始化，应显式使用上述 genai-test 解释器。禁止回到旧 modern_genai 环境。Linux/CUDA 依赖另见 Colab 文档，不能用本地 CPU 安装成功替代它。

## 3. V3/V4 如何保证可比

配置共享同一 V0 模型/revision、609 train、processor、prompt 函数、语言 LoRA 范围、种子、max_pixels、生成长度/组大小、batch、梯度累积、更新预算、KL 与格式项。V3 λp=0，V4 λp=0.2。两份 JSON 除此字段逐项相同，连 output_root 也相同；运行时按 λ 派生隔离的子目录，避免覆盖。

所有组都要求 `<perception>…</perception><answer>…</answer>`。V3 也输出相同协议，但事实匹配分不进入其加权奖励。配置中不再存在按 reward_mode 拼接提示的分支。三个回调分别返回答案、格式和感知项：`R = R_answer + 0.05 R_format + λp R_perception`。格式项要求两段结构、非空答案和 strict-v5 几何格式，所有组相同；不是给多列事实额外格式分。

感知项仍采用冻结 v4 稀疏评分；strict-v5 是并行校验与格式检查，未替换已冻结事实评分。若未来将 strict-v5 事实分用于优化，必须另注册实验版本，并成对改 V3/V4。三个分项、权重、加权原始奖励、原始输出和新旧评分全部写入 rollouts.jsonl；KL/组标准化另属 TRL 目标，不能把原始加权奖励冒充优势。

lambda 0.1/0.2/0.4 的草稿共用上述条件，都是2步工程预算；不是可得出最优 λ 的实验。正式预算和种子仍待预注册，不根据最终 test 选 λ。当前仅允许批准的609题，1472/1045等分析计数不进入配置。

```bash
# 下阶段有固定本地模型后才能执行；本轮未运行。
python -m reports.handover_20261024_v2.train --config reports/handover_20261024_v2/configs/v3_v0_answer_format.json
python -m reports.handover_20261024_v2.train --config reports/handover_20261024_v2/configs/v4_v0_perception.json
```

旧 `感知SFT→稀疏RL` 单独命名为 `engineering_perception_sft_to_sparse_rl.json`，仍使用原 `scripts.train_project3`，保留原格式和旧接线行为用于历史工程溯源，**不属于新的公平配对**。不能用它替代 V3/V4。

## 4. V1/V2：不捏造 reasoning

V1 监督目标是 `<perception></perception><answer>标准答案</answer>`；空 perception 是统一输出协议的包装，不提供事实监督。V2 为已有 `<perception>认证事实</perception><answer>标准答案</answer>`。两者使用相同609题、共享 system/user 模板和 V0；只改变监督内容。reference_answer 只用于 assistant target，不进入 user prompt。认证与原数据白名单继续由原 model_view 检查，新增视图不改原行的批准或白名单。

没有经过验证的 reasoning，故不增加 reasoning 段。答案可能正确而解题过程错误，当前协议不能直接研究完整过程监督，也不能把生成的外显事实当内部推理解释。V1/V2 的有效监督 token 预算并不相等，比较时须报告成本，不能把更多监督信息的收益全归因于方法。

本轮 target-only 文本 token 实测（不含聊天模板结束 token）为：
'''
    for mode in ['answer_v1','perception_answer_v2']:
        r=token[mode];readme+=f"\n- {mode}：{r['rows']}题，总计 **{r['total']}**，均值 {r['mean']:.4f}，最大 {r['maximum']}。"
    readme+='''

这是包内 `data/tokenizers/Qwen2.5-7B-Instruct` 的**文本 tokenizer 代理计数**，tokenizer 文件 SHA 已保存。不是实际 VL processor 的 assistant-label 计数；两者是否完全一致及模板终止 token 数 **未验证**，不能直接作为正式训练 token 成本。没有为补数字下载 processor。实际计数入口如下，仅使用已缓存 processor、不加载模型：

```bash
python -m reports.handover_20261024_v2.count_vl_supervision --processor Qwen/Qwen2.5-VL-3B-Instruct --revision 66285546d2b821cf421d4f5eb2576359d3770cd3 --output reports/handover_20261024_v2/vl_supervision_counts.json
```

## 5. 奖励校验与监控

strict-v5 显式校验点数、退化实体、线段/角/圆角色、单位和值，拒绝 `Angle(A,B)=60 deg`、未知负长度、同一线段对等；保留角的顶点以及源 schema 允许的反角（上界360度），不擅自把大于180度当错。冻结 v4 文件未改。

对当前691条发布 target 自评分，新旧 reward/format_valid/F1 差异为 **0**，strict_invalid=0。此结果说明格式兼容，不证明事实真值或 AI 审核精度。详见 label_score_comparison.json。初稿曾用180度上界触发两条反角，检查源 schema 后在独立 v5 内改为兼容360度；没有改标签、批准或冻结评分。

G为空时新返回结构显式 mask=False、分数0；现有训练仍拒绝无正事实行，不扩池。未知事实不当负例；同已认证常量属性冲突才产生有限FP。正事实 Recall/有限范围 F1 不是全图准确率。严格格式也不能证明未知事实正确。

answer 回调无条件把所有分项和 TP/FP/masked/P/R/F1/原文写本地 JSONL，不依赖 TRL 是否转发 log_metric。monitoring.json 包含平均原始事实条数、认证Recall、masked/全部去重预测事实的比例、按F1分层答案正确率和 verifier 状态；G为空单独分层。评分失败状态保留，不能和数学错误混为一谈。平均事实条数含重复，masked比例的分母去重，两个口径都已写清。

constructed_reward_log.jsonl / constructed_monitoring.json 是**人工构造 CPU 测试输入**，不是模型预测或训练结果。实际 TRL dispatch 的新增测试也不调用 train/generate/backward，仅检验私有字段路由和三分项返回。真实视觉 rollout 对齐和恢复 **未验证**。

## 6. 参数探针

新训练入口枚举实际模块全名，仅对排除 visual/vision/merger 的语言目标模块注入 LoRA，随后要求视觉模块存在且全部 requires_grad=False；无法定位则失败，不静默宣称冻结。每个参数完整名称、numel、requires_grad、可训练全名清单和指纹进入 requires_grad.json 与 run_identity.json。

```bash
python -m reports.handover_20261024_v2.probe_parameters --tiny --output reports/handover_20261024_v2/tiny_parameter_identity.json
```

tiny 结构已执行；将 merger 改为可训练会被测试拒绝。真实 Qwen 模块映射、前后向、显存、恢复 **未验证**。Colab 上可用同探针对已缓存模型做 CPU 结构检查，随后才安排最长多模态前后向；不以结构检查代替 GPU 验收。

## 7. 盲审抽样：审核模型、像素与完整提示词

本次75题的真实缓存 request/response model 均为 `deepseek-flash`，thinking=disabled。它是 API 别名，服务背后的不可变模型快照 **未验证**，不能声称锁定了某一内部模型版本。请求实际包含 `data:image/png;base64,...` 且 detail=original；本轮逐个解码并与官方原图字节比较，75/75一致。因此可确认请求提供了原图像素，但不能由缓存证明模型真正使用了这些像素。

完整提示词来自实际75个请求缓存（共1个版本），不是根据解析结果重构。完整原文如下：

'''
    for h,prompt in prompts.items():readme+=f'提示词 SHA256：`{h}`。\n\n```text\n{prompt}\n```\n\n'
    readme+='''
其中明确含保守倾向措辞：`uncertain=not established`、`uncertain if answer correctness cannot be established`、`pass only if question and stored answer are consistent`。另有 `Never force the stored answer`。这些措辞旨在限制凭空放行，但也可能提高拒绝/uncertain率；是否误杀需独立盲审测量。不能把保守提示等同已证明“审核更准确”。

题答字段判断 QUESTION 与 stored ANSWER 的有效性，而不是事实候选是否完整：具体答案/方向/条件冲突→isolate；无法建立答案正确性→uncertain；题目与存储答案一致→pass。审查者看到标准答案，故原AI任务不是盲解题；pass并非独立求解的保证。格式/finish失败优先单列，不能算作真实语义uncertain。

抽样使用 seed=20261024、random.Random(seed)。按 A/B/C、每组 train/validation 的固定顺序，对 sample_id 排序后 random.sample；最后同一个 RNG shuffle 分配 B001~B075。未使用任何 test 题干/答案/事实/图片作导出。A为有效题答uncertain（按存档解析状态，含原pass但task_issues非空后被守卫降级的情况）；B为漏斗“无剩余认证事实”且AI pass（全被文字剔除的单独类别不混入B）；C为最终批准。每组人数为25+5、25+5、12+3，总计75，没有替换挑题。

geometry_funnel.json 已存在且其来源SHA匹配，本轮未重新生成。真实缓存为 reports/data_release_preparation_20261024/shared_api_cache.zip；不是重新调用审核接口。sample_manifest.json及独立SHA保存抽样，sampling_report.json保存前后哈希和选图来源。未找到的必需输入为0。

blind/只有五个批次、75张去元数据并限长边1200的图、填表模板及审查说明。题干用官方 original_data.problem_text，答案用官方解码标准答案；候选为缓存请求中的修剪前完整 indexed candidate_facts，自然语言逐条翻译；另保留对应InterGPS完整图示与文字原始逻辑条件。未解析条件也在原始列表保留，不凭空补候选。

key/保留身份、组别、原始AI响应、剔除原因和最终保留事实。raw_task_status来自缓存响应原文，parsed_task_status来自all_case_audit的解析结果；本次75题有1条原始pass但因task_issues非空被守卫降为uncertain，原抽样不变。不能把解析后状态冒称AI原始判决。泄漏测试禁止身份元数据、带标识的ID、AI判决/理由、组别；按用户明确确认，纯数字与数学题面的巧合单独记录，不删题、不改答案、不重抽。文本中1个被选数字ID在必需内容里巧合出现，见私有数字报告；图片数字未做OCR身份巧合审计，**未验证**。盲审不能阻止熟悉原数据的人从题本身识别来源。

误杀/误放率要等独立填写：A中题答其实成立的比例估计uncertain误杀；B中题答成立且至少存在可合法认证的图像独占候选比例估计事实级误杀（B无标签并不必然是审核错误）；C中题答或已认证事实有实质错误比例估计误放。三者不可混为一个比例。按 train/validation 分层报告，并给分母、不清晰数和置信区间；n=30/30/15很小，不可外推为全量人工金标。

## 8. 未验证与后续门槛

真实VL的processor/assistant mask、实际监督token、最长样本前后向、视觉模块映射、TRL视觉rollout、完整checkpoint恢复、A100显存和Colab安装均 **未验证**。新配置只是2步smoke草稿。未完成正式V0基线与V1～V4训练，也没有能力提升结果。先验收环境与输入，再跑同条件实验，不根据最终test改子集或评分。
'''
    (OUT/'README.md').write_text(readme,encoding='utf8')
    scale_doc=f'''# 认证子集与答案监督池：只读规模分析

当前全量唯一关联 train 为 {scale['train_total']}。按全部官方 validation/test 像素身份（不是仅82条批准validation），并集排除 {scale['overlap_removed']} 道，剩 **{scale['remaining']}**。

剩余行按真实审核结构/题答状态分层：

- pass：**1045**。
- uncertain：**372**。
- isolate：**33**。
- 格式/finish失败或缺响应：**22**。

合计1472。audit.review.task_status解析状态与记录中的independent_task_resolution生效后计数本次相同；这里不是重新读取缓存得到的原始AI状态分布。不手动重判。原全池重叠为validation267、test479、两者122，故并集267+479−122=624。624是全池无条件图像排除；最终事实质量通过后的train同图隔离319是有条件漏斗退出，二者不矛盾。

1045是**潜在待决策的题答pass规模**，不是批准训练池。既有manifest仅允许609 train/82 validation；本轮新配置仍只读609。若未来考虑扩答案奖励池，需要单独数据版本、审核授权和准入，不能直接拿此计数更新SHA。

task_status审查对象是题目、图片条件/方向与stored answer的一致性/有效性。完整真实提示词见本目录README；关键原文：

> task_status is about QUESTION and stored ANSWER validity, not annotation completeness

> isolate concrete answer/direction/condition conflicts; uncertain if answer correctness cannot be established; pass only if question and stored answer are consistent.

只有有限事实、不支持的标注或未印点名不应自动推翻题答，提示词另要求：`Missing/unprinted labels or unparsed source facts do NOT invalidate unrelated certified facts: mark only that fact uncertain.` 原审核仍可能有误；pass不是人工金标，也不是独立解题。格式失败由严格响应schema/finish规则先识别，不混入语义uncertain。

来源与可复核输出：answer_pool_scale.json（含输入SHA）；原 all_case_audit.jsonl；原 geometry_funnel.json；原geometry3k_intergps_links.jsonl。本轮未使用留出答案/事实扩大训练，仅用像素身份排除。
'''
    (OUT/'规模与审核口径.md').write_text(scale_doc,encoding='utf8')
    notebook={'nbformat':4,'nbformat_minor':5,'metadata':{},'cells':[
      {'cell_type':'markdown','metadata':{},'source':['# Project3 Colab 环境准备（不下载模型、不训练）\n','此Notebook未在Colab执行；CUDA/安装均未验证。先上传完整迁移包到自己的Drive。']},
      {'cell_type':'code','execution_count':None,'outputs':[],'metadata':{},'source':["from google.colab import drive\n","drive.mount('/content/drive')\n"]},
      {'cell_type':'code','execution_count':None,'outputs':[],'metadata':{},'source':["import os, subprocess\n","os.environ['PROJECT3_DRIVE_ROOT']='/content/drive/MyDrive/project3'  # 改成自己的完整项目目录\n","subprocess.run(['bash', os.environ['PROJECT3_DRIVE_ROOT']+'/reports/handover_20261024_v2/colab_bootstrap.sh'], check=True)\n"]} ]}
    (OUT/'colab_bootstrap.ipynb').write_text(json.dumps(notebook,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':main()
