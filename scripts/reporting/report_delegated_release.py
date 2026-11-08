"""Report measured delegated audits and precisely scoped training releases."""
import json,hashlib
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2];REPORT=ROOT/'reports/data_release_preparation_20261024'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):
    with Path(p).open(encoding='utf-8') as f:return [json.loads(l) for l in f if l.strip()]
def link(p,title=None):return '['+(title or Path(p).name)+'](<'+Path(p).resolve().as_posix()+'>)'
def dump(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run():
    native=read(ROOT/'data/project1_native_v5/summary.json');gen=read(ROOT/'reports/project1_batch500_20261024/generation_summary.json')
    ver=read(ROOT/'reports/project1_batch500_20261024/verification_summary.json');p2=read(ROOT/'reports/project2_ai_review_20261024/summary.json')
    pairs=read(ROOT/'reports/math_pair_delegated_review_20261024/summary.json');geo=read(ROOT/'reports/project3_all_split_candidates_v2/summary.json')
    vision=read(ROOT/'reports/project3_grounding_ai_review_20261024/summary.json');release=read(ROOT/'data/delegated_ai_releases_20261024/summary.json')
    ledger=read(REPORT/'shared_api_cache/ledger.json');assert all(r['state']!='reserved' for r in ledger)
    budget={'cap_usd':5,'provider_dispatch_attempts':len(ledger),'completed_requests':sum(r['state']=='complete' for r in ledger),
        'completed_usage_peak_estimate_usd':sum(r.get('charged_upper_usd',0) for r in ledger if r['state']=='complete'),
        'retained_unknown_error_reserve_usd':sum(r['reserved_usd'] for r in ledger if r['state']!='complete'),
        'committed_upper_usd':sum(r.get('charged_upper_usd',r['reserved_usd']) for r in ledger),
        'not_actual_account_balance_delta':True,'error_requests_not_assumed_free':True}
    assert budget['committed_upper_usd']<=5
    dispatch={}
    for r in ledger:
        task=r['task_id'];base=task.removesuffix('/transport2');dispatch.setdefault(base,[]).append(r)
    p2rows=rows(ROOT/'reports/project2_ai_review_20261024/results.jsonl');enriched=[]
    for r in p2rows:
        ds=dispatch.get('p2/review/'+r['record_key'],[])
        enriched.append({**r,'api_dispatched':bool(ds),'provider_attempt_count':len(ds),'received_response_count':sum(d['state']=='complete' for d in ds),
            'dispatch_evidence':'ledger; original worker api_called flag on errors denotes response-success, not proof of zero dispatch/cost'})
    with (ROOT/'reports/project2_ai_review_20261024/results_with_dispatch_evidence.jsonl').open('w',encoding='utf-8') as f:
        for r in enriched:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    dump(REPORT/'budget_summary.json',budget)
    lines=['# 三项目委托 AI 审核、批量构建与批准范围（2026-10-24）','',
        '本轮授权：用户允许以 DeepSeek 审核代替逐题人工审阅，并将总 API 硬上限明确为 $5。所有批准记录写明 user_delegated_AI，不声称个人逐题人工签字。','',
        '**当前可训练范围仅为新 release manifest 的 approved_training_files 列表。候选全集、AI待定/隔离项和未核验视觉标签不随之整体批准。**','',
        link(ROOT/'data/delegated_ai_releases_20261024/manifest.json','批准子集 manifest')+'；'+link(REPORT/'DeepSeek审核条件与批准范围.md','完整审核条件')+'。','',
        '## 1. 项目一：原生候选补齐与 500 题批次','',
        f"原生 v5 候选池 {native['count']} 题，保留旧池 {native['retained_from_original_1500']} 题，替补 {native['refilled']} 题；不是简单1182+318。六类配额保持525/300/300/225/100/50。",
        '对实际选中源轨迹重新读固定revision的parquet、核对回答SHA和每条源验证flag；再次执行源题清洗、范围/结构隔离、显式ANSWER排除、heldout和内部Jaccard>=.85排除、Qwen实际长度/完整上下文检查。',
        '**这1500题是通过固定规则的原生候选，不是1500条逐题过程金标或整体批准训练集。** 仅批准子集文件中的明确行获得工程准入。','',
        f"批次目标500题，按六类175/100/100/75/33/17选题，每题一次请求；实际响应{ver['generation_completed']}条、传输错误{gen['statuses'].get('uncertain_transport',0)}条。未补抽一个更好看的结果。",
        f"有效JSON/质量格式{ver['schema_valid']}条，保守Math-Verify答案通过{ver['answer_verified']}条，自动准入与原生共同交集{ver['common_pairs']}对。",
        '193条记录的JSON质量检查和最终答案验证都通过，但低于150 Qwen tokens；不能把这些一概叫水题。当前协议保持150~1500，不在看完结果后改规则或分母。',
        f"新{ver['common_pairs']}对加上此前v4由Codex AI判pass的10对，交给DeepSeek重新审两条完整轨迹：{json.dumps(pairs['by_cohort'],ensure_ascii=False)}。旧10对不伪称用户已逐题确认。",
        f"实际批准同题对子集 {release['project1_ai_approved_paired_count']} 对，两个arm题目ID完全相同。组成：{json.dumps(release['project1_cohorts'],ensure_ascii=False)}。原生1500全集未批准。",
        '原v4 30题结果和未通过的70%门槛原样保留；本批次由用户另行授权为有预算上限的工程批次，不是把旧门槛改成通过。',
        '该A/B同时改变教师、提示词和长度，只能比较两种数据管线；尚无GPU训练/截断率/准确率/速度结果，不能单独归因于消除过度思考。','',
        link(ROOT/'data/project1_native_v5/manifest.json','1500题候选与来源')+'；'+link(ROOT/'reports/project1_batch500_20261024/verification_summary.json','500题冻结统计')+'；'+link(ROOT/'reports/math_pair_delegated_review_20261024/reviews.json','逐对过程审核')+'。','',
        '## 2. 项目二：四个固定池逐题审核','',
        f"共{p2['items']}条：数学2500 train+256 dev，代码2500 train+200 dev。实际结论：{json.dumps(p2['verdicts'],ensure_ascii=False)}。分池：{json.dumps(p2['by_pool'],ensure_ascii=False)}。",
        '发送完整题目、完整参考解答/程序、明确标注的用例节选与已存在的执行证据。若输入超过声明上限则留待定，不暗中截断后判pass。审核条件覆盖规格、接口、缺图/歧义/泄漏、定义域/分支/算术、复杂度、测试与源参考的一致性。',
        '输出格式或finish不完整、pass与issues/视觉依赖/答案泄漏冲突时转待定；只有URLError可额外尝试一次，保留两次费用预留。不会因为语义判决失败而反复抽一个pass。','',
        '上轮新增3道dev确实通过53个源用例和6个常量mutant检查；25道train替补是OPD题面，未声称全部执行过容器。本轮AI审阅不改写原执行状态。','',
        '**独立反查显示AI裁判也会错。** DeepSeek声称code/vfc_19821在N=2、A=B=[1,1]时错误打印Yes；受限容器实测打印No，该指控不成立。保留原始AI结论，并将分歧记为待定，不改写源程序或强行批准。',
        'math/train/04117的辅助参考解答确有sqrt(3)/sqrt(2)中间笔误，但最终答案sqrt(3)经Cauchy和等号点验证正确。参考推导质量和dev最终答案有效性分别记录。',
        '构造题允许多个正确输出时，参考程序通过固定stdout用例并不构成通用学生输出判分器；此类dev另标语义checker需求。原来的容器测试及mutant证据仍保留。','',
        f"批准的OPD训练子集：数学{release['project2_approved_train_counts']['math']}题、代码{release['project2_approved_train_counts']['code']}题；代码接口分布{json.dumps(release['project2_code_interfaces'],ensure_ascii=False)}。这不是原2500+2500全量封板。",
        f"固定dev的{release['project2_original_dev_ids_preserved']}个ID均保留，问题/答案不重写、不转训练种子；审阅状态逐项附加。原先50/50域采样等实验配置需针对新子集版本声明，不能悄悄改配额。",
        link(ROOT/'reports/project2_ai_review_20261024/results_with_dispatch_evidence.jsonl','全部逐题结论及请求次数')+'；'+link(ROOT/'reports/project2_ai_review_20261024/independent_counterexample_checks.json','容器反查')+'。','',
        '## 3. 项目三：全分割候选、内部ID隔离及200题视觉复核','',
        f"源数据train2101/validation300/test601；唯一关联实际为{json.dumps(geo['unique_matched_split_sizes'],ensure_ascii=False)}，另train5/test1关联歧义隔离，未强行补配。",
        'Schema v2已用于全2996个唯一关联题，分割文件分开保存；validation/test候选仅供标注/诊断，不作训练输入或合成种子。',
        '内部source_radius_id保留在审计JSON作身份追踪，绝不进入模型perception字符串。未印出的圆心/点名保持待接地；同心圆不按圆心或统一Circle合并。单圆仅在图像确认和身份无歧义时可用通用Circle。',
        f"固定200道原型实际发送原图给DeepSeek视觉审核：{json.dumps(vision['verdicts'],ensure_ascii=False)}。通过图像审核及本地可见标签/圆身份/序列化检查的感知监督原型为{vision['approved_grounded_train_prototypes']}题。",
        'ID742继续隔离。144/1285/1987/742的可见点名还与此前直接像素核查交叉校验；AI若把未印的A/B等名字说成可见，会转待定。',
        '**批准仅限感知监督原型。** 只有problem+image_path进入模型输入，model_perception作监督目标；原始标注、答案和审计事实不进入输入。未伪造reasoning轨迹；部分标签未宣称完整类别覆盖，感知RL奖励仍禁用。',
        '这是用户委托AI审核的原型子集，不是200题人工精度估计，也不是全量Geometry3K训练数据或VLM主循环验收。',
        link(ROOT/'reports/project3_grounding_ai_review_20261024/reviews.json','200题原图审核')+'；'+link(ROOT/'data/project3_all_split_candidates_v2/manifest.json','全分割候选')+'。','',
        '## 4. 费用、版本和执行边界','',
        f"API派发尝试总数{budget['provider_dispatch_attempts']}；已完成用量按峰值价估算${budget['completed_usage_peak_estimate_usd']:.8f}，未知/失败保留预留${budget['retained_unknown_error_reserve_usd']:.8f}，合计费用上界${budget['committed_upper_usd']:.8f} <= $5。这不是账户实扣差额。",
        '定价依据：[DeepSeek官方价格页](https://api-docs.deepseek.com/quick_start/pricing/)；视觉格式和每图token上限依据：[官方Vision文档](https://api-docs.deepseek.com/guides/vision/)（2026-10-24核查）。',
        '统一费用账本在shared_api_cache/ledger.json；错误请求不能当成免费。单一跨进程文件锁防止两个进程各自记账突破总额度。密钥仅在内存/隐藏输入中使用，未写入请求缓存。','',
        '旧v3/v4数据、已冻结pilot结果及项目二v2/v3源版本保留；所有批准由新子集manifest、文件SHA和逐项请求证据限定。',
        '实际CPU批准输入预检见 '+link(REPORT/'approved_input_preflight.json')+'；最终测试/旧版保护/本地链接检查见 '+link(REPORT/'final_checks.json')+'。',
        '本轮没有加载GPU权重、没有运行7B/VLM训练或基准评测。已编写真实HF SFT、TRL GRPO/Dr.GRPO、双教师分时OPD、VLM感知SFT及数学/视觉诊断入口；并提供批准子集的2步A100 smoke配置。',
        'CPU小模型实际优化、恢复及教师冻结的测试见pytest.log。训练说明见 '+link(ROOT/'docs/blueprints/批准子集训练入口与A100验收.md')+'。',
        '**核心VL感知GRPO尚未放行。** 原始目标配额的全量封板未完成，项目三只有感知监督原型；完整VL reasoning/奖励覆盖与语义代码判分仍需后续技术工作。已实现入口不等于A100/GPU端到端验收完成。','']
    (REPORT/'执行报告.md').write_text('\n'.join(lines),encoding='utf-8')
    dump(REPORT/'summary.json',{'native_pool':native,'generation':gen,'local_verification':ver,'project2_review':p2,'pair_review':pairs,
        'geometry_full_candidates':geo,'geometry_visual_review':vision,'approved_release':release,'budget':budget,
        'gpu_training_runs':0,'training_entries_implemented':['HF_SFT','TRL_GRPO','TRL_DrGRPO','sequential_teacher_OPD','VLM_perception_SFT','math_evaluation','paired_vision_diagnostic'],
        'core_visual_perception_GRPO_approved':False,'a100_smoke_completed':False})
    # A concise review pack points to all complete source/evidence, without
    # duplicating thousands of reference programs into another huge document.
    pack=['# 委托AI审核后的批准子集与抽检入口','',link(REPORT/'执行报告.md','实测报告')+'；'+link(ROOT/'data/delegated_ai_releases_20261024/manifest.json','批准范围')+'。','',
        'AI工程批准不等于人工逐题签字或全量金标。所有源数据及非pass记录均保留。','',
        '## 项目一：10对代表性批准样本','']
    a=rows(ROOT/'data/delegated_ai_releases_20261024/project1_raw_paired_ai_approved.jsonl');b={r['sample_id']:r for r in rows(ROOT/'data/delegated_ai_releases_20261024/project1_compact_paired_ai_approved.jsonl')}
    for r in sorted(a,key=lambda r:r['sample_id'])[:10]:
        pack += [f"### {r['sample_id']}",'',r['problem'],'',f"审核请求：`{r['approval_evidence_request_id']}`；cohort：{r['cohort']}。",'',
            '精炼全文：','','````text',b[r['sample_id']]['solution'],'````','',
            '原生全文：','','````text',r['solution'],'````','']
    pack+=['## 项目二：全部审核与独立反查','',link(ROOT/'reports/project2_ai_review_20261024/results_with_dispatch_evidence.jsonl')+'。','',
        link(ROOT/'reports/project2_ai_review_20261024/independent_counterexample_checks.json')+'；'+link(ROOT/'reports/project2_ai_review_20261024/independent_math_checks.json')+'。','',
        '批准训练文件与dev审阅台账均在 '+link(ROOT/'data/delegated_ai_releases_20261024/manifest.json')+' 的明确范围内。','',
        '## 项目三：前10个批准原型（原图+模型目标）','']
    for r in sorted(rows(ROOT/'data/delegated_ai_releases_20261024/project3_perception_prototype_ai_approved.jsonl'),key=lambda r:r['sample_id'])[:10]:
        pack += [f"### {r['sample_id']} / original {r['original_id']}",'',r['problem'],'',f"![审核原图](<{Path(r['image_path']).as_posix()}>)",'',
            '```text',r['model_perception'],'```','',f"审核请求：`{r['approval_request_id']}`。仅感知监督，感知RL奖励未启用。",'']
    (ROOT/'reports/data_review_delegated_release.md').write_text('\n'.join(pack),encoding='utf-8')
    print(json.dumps({'release':release,'budget':budget},ensure_ascii=False),flush=True)


if __name__=='__main__':run()
