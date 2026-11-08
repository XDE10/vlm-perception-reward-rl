"""All unique matched splits, separated for train/diagnostic-only use."""
from pathlib import Path
from collections import Counter
import json
from src.data.project3_perception_v2 import parse_record,classify,ordered_facts
from src.data.geometry_model_serialization import render
from scripts.data.build_project3_perception_prototype import rows,jsonl,dump,sha

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/project3_all_split_candidates_v2';REPORT=ROOT/'reports/project3_all_split_candidates_v2'


def run(refresh_draft=False):
    if (OUT/'manifest.json').exists():
        if not refresh_draft:raise FileExistsError('all-split proposal exists; choose new version or explicit pending-draft refresh')
        for split in ['train','validation','test']:
            assert all(not r['training_approved'] for r in rows(OUT/(split+'.jsonl')))
    OUT.mkdir(exist_ok=True);REPORT.mkdir(exist_ok=True)
    links=rows(ROOT/'data/project3_audit/geometry3k_intergps_links.jsonl');annotations={r['original_id']:r for r in rows(ROOT/'data/project3_audit/intergps_annotations.jsonl')}
    records=[];ambiguous=[]
    for l in links:
        if l['status']!='matched':ambiguous.append(l);continue
        a=annotations[l['original_id']];diagram=[parse_record(x) for x in a['diagram_annotation'].get('diagram_logic_forms',[])]
        text=[parse_record(x) for x in a['text_annotation'].get('text_logic_forms',[])];classified=classify(diagram,text);facts=ordered_facts(classified)
        try:serialized=render(facts)
        except ValueError as e:serialized={'annotation_only_preview':None,'model_perception':None,'grounding_status':'isolated','issues':[str(e)],'training_approved':False}
        if l['original_id']=='742':serialized.update(model_perception=None,grounding_status='isolated_direction_convention')
        records.append({'sample_id':l['wrapper_locator'],'original_id':l['original_id'],'split':l['wrapper_split'],'problem':l['question'],'reference_answer':l['answer'],
            'diagram_raw':a['diagram_annotation'].get('diagram_logic_forms',[]),'text_raw':a['text_annotation'].get('text_logic_forms',[]),
            'canonical_candidates_with_audit_provenance':facts,'uncertain':[r for r in classified if r['category']=='uncertain'],
            'image_source_locator':a['original_locator'].replace('data.json','img_diagram.png'),
            'source_point_positions_for_audit_only':a['diagram_annotation'].get('point_positions',{}),
            'serialization':serialized,'allowed_use':'train_candidate_only' if l['wrapper_split']=='train' else 'heldout_label_or_diagnostic_only_never_training_seed',
            'prediction_inputs_must_exclude':['reference_answer','diagram_raw','text_raw','canonical_candidates_with_audit_provenance','serialization','source_point_positions_for_audit_only'],
            'training_approved':False,'review_method':'automatic_schema_and_alias_leak_check; no full visual audit'})
    for split in ['train','validation','test']:jsonl(OUT/(split+'.jsonl'),[r for r in records if r['split']==split])
    jsonl(OUT/'ambiguous_links.jsonl',ambiguous)
    summary={'source_split_sizes':dict(Counter(l['wrapper_split'] for l in links)),'unique_matched_split_sizes':dict(Counter(r['split'] for r in records)),
        'ambiguous_by_split':dict(Counter(l['wrapper_split'] for l in ambiguous)),
        'serialized_preview_without_source_radius_ids':sum(r['serialization']['annotation_only_preview'] is not None for r in records),
        'training_ready_grounded_targets':sum(r['serialization']['model_perception'] is not None for r in records),
        'serialized_grounding_states':dict(Counter(r['serialization']['grounding_status'] for r in records)),
        'rule':'Internal identities retained solely in audit JSON; stripped from diagnostic text. Unknown center/point labels and concentric circle identities require visible grounding; never collapse all circles.',
        'training_approved':False,'test_annotations_used_for_training':False,'api_calls':0}
    dump(REPORT/'summary.json',summary)
    (REPORT/'执行说明.md').write_text('# 项目三全分割候选与模型文本隔离\n\n```json\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n```\n\nannotation_only_preview不是模型训练标签；只有图像别名绑定经过审核的model_perception才具备标签候选条件。所有训练批准仍为false。\n',encoding='utf-8')
    dump(OUT/'manifest.json',{'summary':summary,'inputs':{str(ROOT/p):sha(ROOT/p) for p in ['data/project3_audit/geometry3k_intergps_links.jsonl','data/project3_audit/intergps_annotations.jsonl','src/data/project3_perception_v2.py','src/data/geometry_model_serialization.py','scripts/data/build_project3_all_split_candidates.py']},
        'files':{p.name:sha(p) for p in OUT.glob('*.jsonl')}})
    print(json.dumps(summary,ensure_ascii=False),flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--refresh-draft',action='store_true');a=p.parse_args();run(a.refresh_draft)
