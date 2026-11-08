"""Human-readable delivery, sourced exclusively from the sealed artifacts."""
import zipfile
from pathlib import Path
from scripts.common.strict_v8_common import *

def link(path,label):return '['+label+'](<'+Path(path).resolve().as_posix()+'>)'

def run():
    release=DATA/'release';s=read(release/'manifest.json')['summary'];b=read(REPORT/'budget_final.json');g=read(DATA/'geometry/summary.json')
    raw=rows(release/'project1_raw_paired.jsonl');compact={r['sample_id']:r for r in rows(release/'project1_compact_paired.jsonl')}
    recovered=read(REPORT/'inequality_final_recovery.json')
    text=['# 三项目严格补齐执行报告（v8，2026-10-24）','',
      f"项目一批准 **{s['project1_approved_pairs']} 对**同题 A/B。六类实际数量：{s['project1_type_counts']}。原六类精确配额是否全部达到：**{s['project1_exact_target_met']}**。没有把不等式配额分配给其他题型。",
      f"项目二沿用已封板版本，文件逐字节相同：数学 **2500 train / 256 dev**；代码 **2500 train（1250 function + 1250 stdin）/ 200 dev（100 + 100）**。dev 仍为 evaluation_approved=true、training_approved=false。",
      f"项目三已获得 **2096 train / 300 validation** 原图审核响应；其中满足严格响应结构的为 **{g['valid_reviews_by_split']['train']} / {g['valid_reviews_by_split']['validation']}**。逐事实修剪后批准 **{s['project3_train']} train / {s['project3_validation']} validation**。格式失败、题答 uncertain/isolate 以及无剩余认证事实的题均保留审核记录并排除，不把全量收到响应说成全量获准入。",'',
      '## 不等式验证与恢复','',
      '新增单变量实数/整数解集的精确等价比较，严格区分区间开闭、端点、变量名及定义域；不使用常数不等式真假代替求解，也不猜测函数族、分数部分或有序多参数答案。8937d875 等已知题答冲突继续隔离。',
      '实际答案区与 think 内的探索/格式示例分开解析；允许有明确边界的终端有限解集合分量，真实空答案、未闭合框及相互矛盾的最终框仍拒绝。答案抽取不删除原过程，完整原生和精炼轨迹仍一起交给过程审核。',
      '原 27 道验证/框解析开发题，零 API 重审有21道通过技术性检查，6道因题答结构/源条件不安全而隔离；这是开发集恢复数，不是独立 Pilot 或训练批准数。后续源质量复核另隔离2e53c7ca的残留编辑尾巴，并隔离63a30858将整数未知数约束误用于实数参数的画像，原始记录均保留。',
      '独立首批20道不等式与27道开发题不重叠：12对通过本地准入及完整双轨过程审核。首轮80道技术候选后另有55道仅从本地超时中恢复的备用来源；本地资源失败重验不产生API费用，也不重抽语义拒绝判决。',
      f"最终新增严格批准47对不等式，旧53对加新增47对正好100。原88题池/27道开发题中实际获准7对；27题最终分流为{recovered['development27_final_counts']}，8道未派发是因为配额已满，不能说它们数学错误或已经通过。新增47对中25对源轨迹超过3200 tokens，实际源长度1821~3750，精炼长度150~840。",
      '不等式新源最短正确完整轨迹1200~3800 Qwen tokens，含题干和聊天模板的原生训练序列<=4096；其他五类新源仍1200~3200、完整序列<=3800。精炼端仍150~1500、完整序列<=3800。源长度和竞赛来源仅为难度代理，不能声称长轨迹天然更难。',
      '生成只接收清洗后的题面，不提供原生答案或轨迹。只有源净化/防泄漏/去重、双方答案验证、长度与重复检查、完整双轨AI审核全部通过的行进入发布集；候选池没有整体 training_approved=true。',
      '原生与精炼两臂同时涉及教师版本、提示词和轨迹差异，不能在未训练时归因于消除过度思考，更不能填造准确率、截断率或速度收益。','',
      '## 项目三全量审核与事实修剪','',
      '2396道唯一 train/validation 记录全部留有原始像素审核响应，侧车重解析回查缓存中的真实 finish_reason。只允许有日志的冗余 type=json_object 元数据剥离，其余索引、证据、可见点名、圆身份与结构要求保持严格。test 未作为训练或合成种子。',
      '最新文字蕴含守卫也覆盖“WXYZ is a square”这类反向表述，剔除由正方形/矩形题干直接推出的边长/垂直事实。事实质量阶段：旧531道 train 中530道保留，train:318 因没有剩余图像独占事实退出；新增398道，合计928。随后另执行独立的图像分割守卫，928不是最终训练批准数。',
      f"发现官方划分存在相同图像的不同题目。按全部原始validation/test的像素SHA保留测试优先、验证次之、训练最后的原则；从质量通过行再隔离{g['image_split_exclusions_by_split']}。最终可训练{s['project3_train']}题、严格validation {s['project3_validation']}题，分别涉及{g['train_unique_pixel_images']} / {g['validation_unique_pixel_images']}幅不同图像。完整官方划分及审核记录不改写；只用留出集图像身份做排除，不以其答案/事实补训练。",
      'ID1683由原图直接核查与精确正方形坐标证明纠正旧AI题答判决；仅保留两条可见对角线交点关联事实，证明、图像SHA与原AI意见并存。ID742方向歧义、ID1423角方向/凸凹疑点仍隔离。没有把仍有正事实的题答 uncertain 自动改成 pass。',
      '输出只含认证且图像独占的部分事实，不泄漏内部 radius_3_0 等变量。V4奖励以认证正事实计 Recall，以认证常量属性位可证明的错误计有限范围 FP；未知范围 mask，不把稀疏 Precision 当作全图防幻觉证明。该数据用于部分感知SFT/诊断/保守GRPO，不是完整几何推导金标。','',
      '## 费用、测试与上卡边界','',
      f"同一账本累计 **{b['dispatch_attempts']}** 次派发；已完成用量按冻结峰值价格估算 USD {b['completed_peak_usage_usd']:.8f}，未知失败费用保留 USD {b['unknown_error_retained_reserve_usd']:.8f}，累计上界 **USD {b['committed_upper_usd']:.8f} <= USD 11**。未清零旧费用，未释放未知错误预留，无仍在途请求；这不是账户实扣金额。",
      '本轮CPU测试见下方完整日志，新增定义域绑定与像素分割守卫均有针对性测试。实际Qwen tokenizer、批准范围、配对ID、输入掩码、图像SHA、数据SHA及旧发布文件未改写均执行预检。没有下载/加载GPU模型、启动A100训练或宣称GPU端到端验收。',
      'RL官方Level3~5优先池保持4810道，新增dev及其封存候选仍不进入训练/筛题种子；这不是已完成7B rollout筛选的3000道RL训练集。',
      link(release/'manifest.json','最终批准清单')+'；'+link(REPORT/'approved_input_preflight.json','输入验收')+'；'+link(REPORT/'pytest.log','CPU测试日志')+'；'+link(DATA/'geometry/all_case_audit.jsonl','全量几何审核账本')+'；'+link(DATA/'training_configs','版本化上卡Smoke配置')+'。','']
    (REPORT/'执行报告.md').write_text('\n'.join(text),encoding='utf-8')
    chosen=[]
    for kind in s['project1_type_counts']:
        chosen += [r for r in raw if r['problem_type']==kind][-2:]
    lines=['# v8 实际批准样本预览','', '以下是完整真实记录的可读摘取。AI委托审核不等同人工逐题签字，原始审核证据可由 manifest 和 approval_request_id 追溯。','']
    for r in chosen:
        lines += ['## '+r['problem_type']+' / '+r['sample_id'],'','### 题面','',r['problem'],'','### 原生轨迹','',r['solution'],'','### 精炼轨迹','',compact[r['sample_id']]['solution'],'']
    for r in rows(release/'project3_train_fact_pruned.jsonl')[:6]:
        lines += ['## Geometry '+r['original_id'],'','!['+r['original_id']+']('+Path(r['image_path']).as_posix()+')','',r['problem'],'','认证部分事实：','',r['model_perception'],'']
    (REPORT/'审阅样本.md').write_text('\n'.join(lines),encoding='utf-8')
    docs=ROOT/'docs/blueprints';notice=docs/'Strict_v8_数据封板与上卡说明.md'
    notice.write_text('# Strict v8 数据封板与上卡说明\n\n'+f"项目一实际 {s['project1_approved_pairs']} 对，项目三 {s['project3_train']} train / {s['project3_validation']} validation。精确配额达标：{s['project1_exact_target_met']}。\n\n"+link(REPORT/'执行报告.md','实测报告')+'；'+link(release/'manifest.json','批准范围')+'。\n\n不等式原生完整SFT上限4096，其他源范围及精炼150~1500门槛保持。新配置在 `data/strict_v8_20261024/training_configs/`。A100还须实际最长样本前后向、checkpoint恢复、rollout截断和教师前向Smoke；CPU测试不代替这些检查。\n\n示例：`python -m scripts.train_project1_sft --config data/strict_v8_20261024/training_configs/project1_raw_sft_smoke.json`。项目三使用对应fact SFT或sparse_v4 GRPO配置，只监督认证部分事实。\n',encoding='utf-8')
    names=['项目一_7B数学后训练_详细实施方案.md','项目二_双教师在线蒸馏_详细实施方案.md','项目三_多模态几何推理_详细实施方案.md','共用规范_强模型合成数据与验证.md','三项目_上卡前待办与验收清单.md','项目一_sft_train_v2筛选方案.md']
    backup=REPORT/'blueprints_before_v8.zip'
    if not backup.exists():
        with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
            for name in names:z.write(docs/name,name)
        for name in names:
            p=docs/name;p.write_text('> 2026-10-24 最新批准范围与实测结果见 [Strict v8 数据说明](Strict_v8_数据封板与上卡说明.md)。历史计划数量不构成全量批准。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
    paths=list(release.iterdir())+list((DATA/'training_configs').glob('*.json'))+list(REPORT.glob('*'))+[notice]+[docs/n for n in names]+[ROOT/p for p in ['src/synthesis/typed_answers_v8.py','src/data/perception_text_guards.py','src/data/geometry_split_guard.py','scripts/run_strict_v8.py','scripts/run_strict_v8_resume.py','scripts/seal_strict_v8.py','scripts/data/export_strict_geometry_v8.py','scripts/prepare_strict_inequalities_v8.py','tests/test_typed_answers_v8.py','tests/test_finalfill_budget.py','tests/test_strict_source_domain.py','tests/test_geometry_split_guard.py']]
    paths+=list((DATA/'geometry').glob('*'))+[ROOT/'scripts/reporting/publish_strict_v8_report.py',ROOT/'scripts/strict_v8_verify_worker.py',ROOT/'src/synthesis/finalfill_budget.py']
    dump(REPORT/'delivery_manifest.json',{'files':{str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file() and p.name!='delivery_manifest.json'},'gpu_runs':0})
    print(link(REPORT/'执行报告.md','报告'),flush=True)
if __name__=='__main__':run()
