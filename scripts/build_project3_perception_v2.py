"""Re-run exactly the frozen 200 training topics, retaining every original record."""
import json
from collections import Counter
from pathlib import Path
from src.data.project3_perception_v2 import VERSION,ORDER,parse_record,classify,ordered_facts
from scripts.build_project3_perception_prototype import rows,dump,jsonl,sha

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/project3_perception_v2';REPORT=ROOT/'reports/project3_perception_v2'


def run(refresh_draft=False):
    if (REPORT/'manifest.json').exists():
        if not refresh_draft:raise FileExistsError('v2 exists; only explicit pending-draft refresh allowed')
        existing=rows(DATA/'prototype_200.jsonl')
        assert all(not r['training_approved'] and r['human_review']=='pending' for r in existing)
        previous=json.loads((REPORT/'manifest.json').read_text(encoding='utf-8'))
        assert all(sha(Path(p))==h for p,h in previous['inputs'].items())
    DATA.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'data/project3_perception_prototype/prototype_200.jsonl'
    cases=[];queue=[];md=['# 项目三 Schema v2：同 200 题对照','',
        '全部为训练集；解析覆盖不代表图像独占准确率。原始标注与 v1 均保留，所有样本待审。','']
    for old in rows(source):
        diagram=[parse_record(x) for x in old['diagram_raw']];text=[parse_record(x) for x in old['text_raw']]
        facts=classify(diagram,text);new=ordered_facts(facts)
        isolated=old['original_id']=='742'
        case={**old,'v1_diagram_facts':old['diagram_facts'],'diagram_facts':facts,'text_parsed':text,
              'schema_version':VERSION,'canonical_facts':new,'case_status':'isolated_direction_convention' if isolated else 'pending',
              'isolation_reason':'blue->green target/source gives sqrt(272/153)=4/3, stored answer 3/4; do not silently reverse or rewrite gold' if isolated else None,
              'human_review':'pending','training_approved':False}
        cases.append(case)
        for i,f in enumerate(facts):
            if f['category']=='uncertain':queue.append({'original_id':old['original_id'],'diagram_index':i,**f})
        md.extend([f"## ID {old['original_id']} / {old['wrapper_locator']}",'',old['question'],'',
            f"![原图](<{Path(old['image_path']).as_posix()}>)",'',f"状态：{case['case_status']}；原答案 `{old['answer']}`。",'',
            '```json',json.dumps(new,ensure_ascii=False,indent=2),'```',''])
    allfacts=[f for c in cases for f in c['diagram_facts']]
    oldfacts=[f for c in cases for f in c['v1_diagram_facts']]
    summary={'version':VERSION,'same_train_topics':len(cases),'v1_supported':sum(f['parse_status']=='supported' for f in oldfacts),
        'v2_supported':sum(f['parse_status']=='supported' for f in allfacts),'total_source_diagram_entries':len(allfacts),
        'v1_nonempty_visual_cases':sum(any(f['category']=='visual_candidate' for f in c['v1_diagram_facts']) for c in cases),
        'v2_nonempty_visual_cases':sum(bool(c['canonical_facts']) for c in cases),
        'v2_nonempty_nonisolated_visual_cases':sum(bool(c['canonical_facts']) and c['case_status']=='pending' for c in cases),
        'relations':dict(Counter(f['fact']['relation'] for f in allfacts if f['fact'])),
        'categories':dict(Counter(f['category'] for f in allfacts)),'remaining_reasons':dict(Counter(f['reason'] for f in allfacts if not f['fact'])),
        'isolated_ids':['742'],'gold_image_only_accuracy':None,'human_reviewed_count':0,'training_approved':False,
        'accuracy_boundary':'Tested schema semantics and selected image examples; no full 200-case image/prose adjudication; coverage is not precision.'}
    jsonl(DATA/'prototype_200.jsonl',cases);jsonl(DATA/'uncertain.jsonl',queue)
    dump(DATA/'schema.json',{'version':VERSION,'canonical_relation_order':ORDER,'expression_parser':'bounded Python AST -> explicit SymPy constructors; no eval or sympify',
        'ordering':'line endpoints and congruence pairs commute; preserve angle vertex, arc traversal, polygon boundary, point/circle roles',
        'arc_units':'ArcMeasure=degrees under InterGPS MeasureOf convention; ArcLength=source length units; never convert one into the other',
        'source_annotations_not_gold':True})
    dump(REPORT/'summary.json',summary)
    (REPORT/'200题预览.md').write_text('\n'.join(md),encoding='utf-8')
    (REPORT/'执行报告.md').write_text('# Schema v2 实测\n\n```json\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    dump(REPORT/'manifest.json',{'inputs':{str(source):sha(source)},'scripts':{str(ROOT/p):sha(ROOT/p) for p in ['src/data/project3_perception_v2.py','scripts/build_project3_perception_v2.py']},
        'artifacts':{str(p):sha(p) for base in (DATA,REPORT) for p in base.rglob('*') if p.is_file() and p.name!='manifest.json'}})
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--refresh-draft',action='store_true');a=p.parse_args();run(a.refresh_draft)
