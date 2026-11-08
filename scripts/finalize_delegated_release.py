"""Protect old artifacts, refresh current entry notices and hash new delivery."""
import hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];REPORT=ROOT/'reports/data_release_preparation_20261024'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):
    with Path(p).open(encoding='utf-8') as f:return [json.loads(l) for l in f if l.strip()]
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def run():
    old=read(ROOT/'reports/data_revision_v4_20261024/delivery_manifest.json');protected=[];historical_docs=[]
    for group in ['files','code']:
        for name,h in old.get(group,{}).items():
            path=ROOT/name
            if path.parent==ROOT/'project_blueprints' and path.suffix=='.md':historical_docs.append(name);continue
            assert sha(path)==h,('old artifact changed',name);protected.append(name)
    docs=[ROOT/'project_blueprints'/n for n in ['项目一_7B数学后训练_详细实施方案.md','项目二_双教师在线蒸馏_详细实施方案.md','项目三_多模态几何推理_详细实施方案.md','共用规范_强模型合成数据与验证.md','三项目_上卡前待办与验收清单.md','两个后训练项目_完整设计与实施指南.md']]
    backup=REPORT/'blueprints_before_delegated_release.zip'
    if not backup.exists():
        with zipfile.ZipFile(backup,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for p in docs:z.write(p,str(p.relative_to(ROOT)))
    notice='> **2026-10-24 委托 AI 审核后的当前状态（本段优先于下文历史记录）**：用户授权 DeepSeek 逐题审核，总预算 $5。实际批准仅限新 release：项目一213对同题轨迹、项目二数学2380/代码1662条训练题、项目三26条感知监督原型；不是原生1500题或三项目全集封板。全量候选及存疑/隔离项保留。训练入口已新增，CPU小模型检查通过；A100/GPU未运行，核心视觉感知GRPO仍未放行。详见[本轮执行报告](<D:/Users/Mr.Z/Desktop/modern_genai/reports/data_release_preparation_20261024/执行报告.md>)与[训练入口及A100验收](<D:/Users/Mr.Z/Desktop/modern_genai/project_blueprints/批准子集训练入口与A100验收.md>)。\n\n'
    for p in docs:
        s=p.read_text(encoding='utf-8')
        if not s.startswith(notice):p.write_text(notice+s,encoding='utf-8')
    release=ROOT/'data/delegated_ai_releases_20261024';m=read(release/'manifest.json')
    for name,h in m['files'].items():assert sha(release/name)==h,name
    for name,h in m['inputs'].items():assert sha(ROOT/name)==h,name
    raw=rows(release/'project1_raw_paired_ai_approved.jsonl');compact=rows(release/'project1_compact_paired_ai_approved.jsonl')
    assert len(raw)==213 and [r['sample_id'] for r in raw]==[r['sample_id'] for r in compact]
    dev=rows(release/'project2_fixed_dev_audit.jsonl');assert len(dev)==456
    for domain in ['math','code']:
        train=rows(release/f'project2_{domain}_train_ai_approved.jsonl');held=[r for r in dev if r['domain']==domain]
        assert not {r['sample_id'] for r in train}&{r['sample_id'] for r in held}
        assert all(r['training_approved'] for r in train) and all(not r['training_approved'] for r in held)
    for r in rows(release/'project3_perception_prototype_ai_approved.jsonl'):
        assert r['split']=='train' and not r['perception_reward_enabled']
        assert not re.search(r'source_radius_id|radius_\d',r['model_perception'])
        assert sha(Path(r['image_path']))==r['image_sha256']
    ledger=read(REPORT/'shared_api_cache/ledger.json');assert len(ledger)==6393 and all(x['state']!='reserved' for x in ledger)
    budget=read(REPORT/'budget_summary.json');assert budget['committed_upper_usd']<=5
    assert '193 passed' in (REPORT/'pytest.log').read_text(encoding='utf-8')
    helps={}
    for module in ['train_project1_sft','train_project1_rl','train_project2_opd','train_project3','evaluate_approved_math','diagnose_project3_vision']:
        p=subprocess.run([sys.executable,'-m','scripts.'+module,'--help'],cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert p.returncode==0,(module,p.stderr);helps[module]=True
    check={'old_version_files_unchanged':len(protected),'historical_blueprints_backed_up':str(backup),'new_release_all_hashes_match':True,
        'paired_ids_identical':213,'project2_fixed_dev_ids_preserved':456,'dev_not_train':True,'visual_internal_ids_excluded':True,
        'no_pending_api_requests':True,'api_attempts':len(ledger),'cost_upper_usd':budget['committed_upper_usd'],'tests_passed':193,
        'entry_cli_help_checks':helps,'gpu_runs':0,'core_perception_GRPO_approved':False}
    folders=[release,ROOT/'data/project1_native_v5',ROOT/'data/project1_batch500_20261024',ROOT/'data/project2_ai_review_20261024',ROOT/'data/project3_all_split_candidates_v2',ROOT/'data/project3_grounding_ai_review_20261024',REPORT,ROOT/'reports/project1_batch500_20261024',ROOT/'reports/project2_ai_review_20261024',ROOT/'reports/math_pair_delegated_review_20261024',ROOT/'reports/project3_grounding_ai_review_20261024',ROOT/'src/training',ROOT/'project_blueprints/configs/approved_release_20261024']
    files=set(docs+[ROOT/'project_blueprints/批准子集训练入口与A100验收.md',ROOT/'reports/data_review_delegated_release.md'])
    for folder in folders:files.update(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.lock')
    files.update(p for p in (ROOT/'scripts').glob('*.py') if 'release' in p.name or p.name.startswith(('train_project','evaluate_approved','diagnose_project')))
    files.update([ROOT/'src/data/approved_training_inputs.py',ROOT/'src/data/geometry_model_serialization.py',ROOT/'src/synthesis/shared_cost_client.py',ROOT/'src/synthesis/data_review_contract.py',ROOT/'tests/test_training_entries_cpu.py'])
    hits=[str(p.relative_to(ROOT)) for p in files if p.suffix in ['.py','.md','.json','.jsonl'] and re.search(r'sk-[A-Za-z0-9]{20,}',p.read_text(encoding='utf-8'))]
    assert not hits,('Possible secret pattern; paths only',hits)
    link_count=0
    for doc in [REPORT/'执行报告.md',ROOT/'reports/data_review_delegated_release.md']:
        for name in re.findall(r'\]\(<([^>]+)>\)',doc.read_text(encoding='utf-8')):
            if name.startswith(('http:','https:')):continue
            assert Path(name).exists(),('Broken current report link',name);link_count+=1
    check['current_report_local_links_checked']=link_count
    check['secret_pattern_scan_passed']=True;dump(REPORT/'final_checks.json',check);files.add(REPORT/'final_checks.json')
    files.discard(REPORT/'delivery_manifest.json')
    dump(REPORT/'delivery_manifest.json',{'files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)},'scope':'New delegated release plus entry points and preserved-source blueprint notices; no claim of GPU acceptance'})
    print(json.dumps(check,ensure_ascii=False))

if __name__=='__main__':run()
