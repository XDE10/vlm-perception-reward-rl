"""Build review-only delivery from actual versioned artifacts; no API or training."""
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
P1=ROOT/'reports/compact_distillation_v4_20261024'
REPORT=ROOT/'reports/data_revision_v4_20261024'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):return [json.loads(l) for l in Path(p).read_text(encoding='utf-8').splitlines() if l.strip()]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,value):Path(p).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def link(p,label=None):return f'[{label or Path(p).name}](<{Path(p).resolve().as_posix()}>)'


# Explicit AI reviewer notes after reading all 15 full raw+compact pairs in this
# chat. They are not rules that infer mathematical correctness from the answer.
NOTES={
 '00e1e3ba':('pass','pass','pass','4!/2! times 7!/(2!2!)=15120; both derivations count identical letters correctly.'),
 '0724ff1f':('pass','pass','pass','Dot products b^2 and b^2-c^2 give c^2=2b^2,a^2=3b^2; distance ratio sqrt(2)/2.'),
 '075203e6':('uncertain','uncertain_prose_operation','pass','Compact handles denominator signs correctly and gives -3<r<-3/2. Raw says multiply numerator AND denominator by -1 and reverse inequality, but displays denominator unchanged. Displayed algebra is correct; inaccurate operation wording needs review.'),
 '1a158258':('isolate','isolate_nonessential_false_equality','pass','Both final proofs use lcm(2,3,4,5)-1=59. Raw additionally states 59 - LCM(2,3,4,5)=60-1=59, a false equality (59-60=-1), not corrected in place. Isolate source trajectory for clean process supervision, not a wrong final answer.'),
 '2c3322a1':('pass','pass','pass','Candy equality gives 5y=4x; nonzero integer solution x=5k,y=4k and cost3750k.'),
 '2d3dbe31':('uncertain','uncertain_cost_assumption','uncertain_cost_assumption','480 bags*14=6720 and remaining420 bags give price16, increase2 IF total costs unchanged or profit means revenue. Problem only states profit; packaging/damage reimbursement assumptions unspecified. Raw incorrectly says regardless of whether costs are fixed; retain conventional-school-problem interpretation for human review only.'),
 '39083fca':('pass','pass','pass','120/v=7/6+(120-v)/(v+6) gives v^2+42v-4320=0; v=48 satisfies v<120 and time2.5h.'),
 '3d627537':('pass','pass','pass','Axial triangle area Rh; pi*R*l=pi*R^2+Rh, h>0 gives h=2*pi*R/(pi^2-1), desired volume. Compact explicitly rejects degenerate h=0.'),
 '406fe592':('pass','pass','pass','527=17*31. Student count positive multiple5; n+1 must be a divisor congruent1 mod5, yielding31 and n30.'),
 '7918f333':('isolate','math_correct_but_source_answer_leak','isolate_invalid_divisibility','Source problem explicitly contains ANSWER:324 and was sent unchanged in frozen request. Compact unjustifiably assumes m ending in7 is divisible by7 and k coprime7. Counterexample N=1115370 ends70, has72 divisors, and N/10 is not divisible7. Correct general proof uses d(N/10)=18, so d(80N)=18*18=324. Do not repair or count this as a blind success.'),
 '7cf91555':('pass','pass_with_minor_linear_case_warning','pass','Denominator x^2+x+1 positive. Discriminant -3y^2+10y-3>=0 gives [1/3,3]; compact explicitly checks y=1 linear case. Raw checks x=0 in full trajectory although final exposition omits separate linear case; endpoints attained.'),
 '8704447d':('isolate','isolate_nonessential_arithmetic','isolate_malformed_intermediate_formula','Correct Cauchy argument gives k9, but compact emits \\frac{(u+v+w)(1/u+1/v+1/w)}{} with empty denominator. Raw numerical side-check claims1002*2.001≈2004.002 instead of2005.002. Core bound/final answer correct; keep malformed/incorrect trajectory text isolated.'),
 '9bd47a9d':('pass','pass','pass','Reciprocal logs sum ln14/ln196=1/2. Full raw includes exploratory doubts but final deduction is correct.'),
 '9ee2fc09':('pass','pass','pass','Repeated squares modulo100 give89,21,41,81 then77. Raw CRT modulo4 and25 is consistent.'),
 'b900f776':('pass','pass','pass','Unique (a,d),1<=d<=1004, count sum(2009-2d)=1004^2=1008016; no ordering overcount.')}


def review_pairs():
    pairs=read(P1/'common_candidates.json');reviews=[]
    assert len(pairs)==15 and len(NOTES)==15
    for r in pairs:
        entry=next(v for p,v in NOTES.items() if r['sample_id'].startswith(p))
        reviews.append({'sample_id':r['sample_id'],'pair_decision':entry[0],'raw_process_decision':entry[1],
            'compact_process_decision':entry[2],'evidence_and_checks':entry[3],
            'raw_text_sha256':hashlib.sha256(r['raw_solution'].encode()).hexdigest(),
            'compact_text_sha256':hashlib.sha256(r['compact_solution'].encode()).hexdigest(),
            'source_answer_leak':r['sample_id'].startswith('7918f333'),'reviewer':'Codex AI process review; not human certification',
            'human_review':'pending','training_approved':False})
    summary={'pairs_reviewed':len(reviews),'pair_decisions':dict(Counter(r['pair_decision'] for r in reviews)),
        'source_answer_leak_pilot_questions':1,'frozen_denominator':30,'reviewed_pending_pairs':sum(r['pair_decision']=='pass' for r in reviews),
        'frozen_gate_rewritten':False,'blindness_gate_passed':False,'all_question_process_accuracy':None,
        'interpretation':'Read all 15 full raw+compact trajectories. 10 pass is an AI assessment of selected pairs, not a human gold precision estimate or a causal v3/v4 comparison.'}
    dump(P1/'ai_process_review.json',{'summary':summary,'reviews':reviews})
    dump(P1/'reviewed_common_candidates.json',[{**r,'candidate_status':next(x['pair_decision'] for x in reviews if x['sample_id']==r['sample_id']),
        'training_approved':False,'human_review':'pending'} for r in pairs])
    return pairs,reviews,summary


def build():
    pairs,reviews,reviewsummary=review_pairs()
    pilot=read(P1/'summary.json');cache=read(P1/'cache_reaudit_summary.json')
    pool=read(ROOT/'data/project1_textonly_v4/summary.json');geo=read(ROOT/'reports/project3_perception_v2/summary.json')
    ga=read(ROOT/'reports/project3_perception_v2/accuracy_audit.json');code=read(ROOT/'reports/project2_code_v3/summary.json')
    verified=ROOT/'data/project2_code_v3_dev_verified/manifest.json'
    cv=read(verified) if verified.exists() else None
    lines=['# 三项目本地修订与 v4 独立 Pilot 实测（2026-10-24）','',
        '全程数据任务；没有 GPU 训练、没有全量 API 请求。旧版均保留。训练批准仍为 false。','',
        '## 项目一：冻结结果与复核','',
        f"30题、{pilot['generation_requests']}次请求；格式{pilot['schema_valid']}/30，答案验证{pilot['answer_verified']}/30，自动准入{pilot['automatic_candidates']}/30，同题{pilot['common_pairs']}对。",
        f"耗时{pilot['wall_seconds']:.2f}秒；峰值价格用量估算 ${pilot['usage_estimated_peak_usd']:.9f}，最坏预留 ${pilot['reserved_usd']:.7f}，硬上限$0.095。不是账户实扣账单。",
        '价格及 alias 对应版本依据：[DeepSeek 官方价格页](https://api-docs.deepseek.com/quick_start/pricing/)（2026-10-24核查）；thinking disabled、每题一次、4路并发。','',
        '独立性：排除旧50/40/30题、anchors/calibration、项目一人工预览ID、79题标记队列；与旧题、heldout及本轮题按Jaccard>=.85检查。未声称语义或预训练污染完全排除。',
        '**新发现**：7918f333源题自带ANSWER:324，且精炼推导错误地从末位7推出可被7整除；这道请求不能算作盲生成成功。保留30题冻结分母，不删题重算成功率、不补发第31次请求。',
        '15对完整原生+精炼轨迹AI复核：10 pass、3 isolate、2 uncertain；这10对仍待人工，不能称为金标。另有空分母公式、原生轨迹错误等式、利润/成本语义待审。',
        '工程门槛未通过，盲性审核也未通过；禁止自动扩量。不同题目和实验范围下的v3/v4通过率变化不能归因于解析器或教师改进。','',
        f"本地v3缓存30条：数值型答案规范化救回解析{cache['parsing_recovered']}条；已知数学错误隔离{cache['known_mathematical_error_isolated']}条（b800f924、0e10fb1c）。既有144条文本格式缓存没有JSON字段，其原格式重审保留，不伪造JSON修复增益。",
        '数值转换只接受有限int/decimal，排除bool和非有限数；未做全局反斜杠替换。源题清洗不把事后清洗后的题面当作当时发送的请求。','',
        f"1500题中清洗{pool['cleaned_questions']}题，质量隔离{pool['quality_isolated']}题，实验范围排除{pool['experiment_scope_excluded']}题，人工结构待审{pool['manual_review']}题；类别可能重叠。自动范围候选{pool['automatic_scope_candidates']}题，尚未补齐新1500题，更不是1200条已验收合成数据。",
        '完整选择题/单字母选项答案按预声明开放求解范围排除，不标坏题；多boxed分重复答案、不同分量/集合待审、格式残缺。',
        f"7184道MATH train的媒体分类：{json.dumps(pool['math_train_media_classes'],ensure_ascii=False)}。含完整asy仍待正文充分性/绘图依赖复核；未放入本轮自动题池。",
        '补充扫描发现8道源题含显式ANSWER标记，进入事后审查overlay；冻结池与请求不回写。','',
        link(P1/'results.json','冻结原始结果')+'；'+link(P1/'ai_process_review.json','逐题AI复核')+'；'+link(P1/'posthoc_source_answer_audit.json','源答案泄漏标记')+'。','',
        '## 项目二：AceCode精确包装函数筛查','',
        '原样返回、常量返回、纯参数字典/序列封装按AST静态识别；一行公式、位运算不按行数剔除；有循环/分支也不自动称为中高难度。',
        f"隔离 train {code['isolated_by_split']['train']}题、dev {code['isolated_by_split']['dev']}题；从原已审计AceCode候选中替补25题train及3题dev，没有加入Magicoder。",
        '旧train/dev不跨split回收；保留官方最终测试及旧dev保护、ID/家族/主体AST/入口名/Jaccard .85过滤，以及Qwen输入<=2560预算。',
        ('Docker最初不可用，用户恢复引擎后重新运行3道新dev的全部源用例和常量mutant门槛，已通过。最终独立版2500 train（1250+1250）、200 dev（100+100）。' if cv else 'Docker运行时socket故障导致3道新dev仍待测；当前候选版2500 train、197已验证dev，另3道只在pending计划中，不能算已验收。'),
        '源测试通过不等于用例完备或参考实现语义全对。所有版本仍待人工训练批准。','',
        link(verified if cv else ROOT/'data/project2_code_v3/manifest.json','当前版本manifest')+'；'+link(ROOT/'data/project2_code_v3/isolated_wrappers.jsonl','隔离明细')+'。','',
        '## 项目三：同200题Schema v2','',
        f"原始diagram条目1922，v1支持454（23.62%），v2支持{geo['v2_supported']}（{geo['v2_supported']/1922:.2%}）；非空视觉候选162→199题；隔离742后198题非空待审。",
        '支持PointLiesOnLine、PointLiesOnCircle、安全AST符号/根式/分数、等长/等角、面积、ArcMeasure与ArcLength。保留点-圆角色、角顶点、弧经过点及多边形边界顺序；仅可交换部分规范排序。',
        f"v1原有{ga['v1_supported_entries_checked']}条支持事实逐项比较，语义保留{ga['semantics_preserved']}条。余下123条uncertain均保留，包括角标号尚未解析、未知点名、空源条目等。",
        'AI查看原图144、1285、742、1987：前两题恢复关键条件；742保留原答案并因蓝→绿4/3与源3/4约定冲突隔离；1987圆上关系可见但中心/点别名不是都印在图上，仍待复核。',
        '**没有200题图像独占准确率测量**；1795条visual_candidate只是有限text-form未命中，可能包含正文可推出事实，不是金标。','',
        link(ROOT/'reports/project3_perception_v2/200题预览.md','200题v2预览')+'；'+link(ROOT/'reports/project3_perception_v2/accuracy_audit.json','准确性边界与原图抽查')+'。','',
        '## 复现与验证','',
        '`python -m scripts.compact_distillation_v4 prepare` 校验冻结输入；付费run已完成，不能重复执行。',
        '`python -m scripts.resume_code_v3_dev` 默认只报告状态；--execute会先执行全部待测题再生成独立verified版本，已有版本拒绝覆盖。',
        '新增10项单元/集成检查与其余测试一起运行：182 passed in 103.78s。'+link(REPORT/'pytest.log','完整日志')+'。',
        '最终文件哈希、旧版保护和本地链接核验见 '+link(REPORT/'final_checks.json')+'。','']
    (REPORT/'执行报告.md').write_text('\n'.join(lines),encoding='utf-8')
    dump(REPORT/'summary.json',{'project1_frozen':pilot,'project1_cache_reaudit':cache,'project1_ai_review':reviewsummary,
        'project1_pool':pool,'project2_wrapper_revision':code,'project2_fresh_dev_release':cv,'project3_schema_comparison':geo,
        'training_runs':0,'bulk_requests':0,'human_review':'pending','training_approved':False})
    # Append-only new review pack; preserve the earlier 90-item pack and its IDs.
    pack=['# 三项目修订版人工抽检包 v4','',link(REPORT/'执行报告.md','先读实测报告')+'；'+link(ROOT/'reports/data_human_review_pack.md','上一版90条完整抽检')+'。','',
        '所有内容待人工，未封板。以下样本按固定ID顺序显示，不挑选成功故事。','',
        '## 项目一：30题完整冻结结果入口','',link(P1/'results.json')+'；'+link(P1/'ai_process_review.json')+'。','',
        '## 项目一：全部15对自动同题候选（含隔离和待定）','']
    for r,v in zip(pairs,reviews):
        pack += [f"### {r['sample_id']} — {v['pair_decision']}",'',r['problem'],'',f"源参考答案：`{r['reference_answer']}`",'',
            v['evidence_and_checks'],'','精炼解答全文：','','````text',r['compact_solution'],'````','',
            '原生解答全文：','','````text',r['raw_solution'],'````','',
            '人工：accept / isolate / uncertain：____；理由：____。','']
    poolrows=rows(ROOT/'data/project1_textonly_v4/native_candidates.jsonl')
    pack+=['## 项目一：净化后范围候选10题','']
    for r in sorted(poolrows,key=lambda r:r['sample_id'])[:10]:
        pack += [f"### {r['sample_id']}",'',r['problem'],'',f"源答案：`{r['reference_answer']}`；范围筛查通过，非过程正确性认证。",'']
    funcs={r['sample_id']:r for r in rows(ROOT/'data/project2_code_v2/function_candidates.jsonl')}
    pack+=['## 项目二：5道训练替补与全部3道dev替补','']
    selected=[('train',sid) for sid in code['new_train_ids'][:5]]+[('dev',sid) for sid in code['new_dev_pending_container_ids']]
    devlookup={r['sample_id']:r for r in rows(ROOT/'data/project2_code_v3_dev_verified/dev_verification.jsonl')} if cv else {}
    for split,sid in selected:
        r=funcs[sid];status='new reference only; OPD prompt training' if split=='train' else 'fresh container tests passed' if sid in devlookup else 'pending container'
        pack += [f'### {sid} / {split} / {status}','',r['problem'],'','````python',r['reference_code'],'````','',f"源用例数：{len(r['test_cases'])}；不代表穷尽正确性。",'']
    pack+=['## 项目三：v2全部200题与四道原图复核','',link(ROOT/'reports/project3_perception_v2/200题预览.md')+'。','']
    for r in rows(ROOT/'data/project3_perception_v2/prototype_200.jsonl'):
        if r['original_id'] not in {'144','1285','742','1987'}:continue
        pack += [f"### ID {r['original_id']} / {r['case_status']}",'',r['question'],'',f"![原图](<{Path(r['image_path']).as_posix()}>)",'','```json',json.dumps(r['canonical_facts'],ensure_ascii=False,indent=2),'```','']
    out=ROOT/'reports/data_human_review_pack_v4.md';out.write_text('\n'.join(pack),encoding='utf-8')
    print(json.dumps({'report':str(REPORT/'执行报告.md'),'review_pack':str(out),'AI_pair_review':reviewsummary,'verified_code_dev':bool(cv)},ensure_ascii=False))


if __name__=='__main__':build()
