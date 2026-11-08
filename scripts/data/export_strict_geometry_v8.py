"""Reparse every original-pixel response without further API calls."""
from collections import Counter
from scripts.common.strict_v8_common import *
from src.data.perception_v4 import parse_review, prune, token_key

def run():
    old=ROOT/'data/topup_v6_20261024'
    cases={r['sample_id']:r for r in rows(old/'project3/cases.jsonl')+rows(old/'project3_reserve/cases.jsonl')}
    sources=[ROOT/'reports/topup_v6_20261024/p3_fact_review.jsonl',ROOT/'reports/topup_v6_20261024/p3_reserve_fact_review.jsonl',ROOT/'reports/finalfill_v7_20261024/p3_reviews.jsonl',REPORT/'geometry_transport_recovery.jsonl']
    latest={}
    for path in sources:
        if path.exists():
            for r in rows(path):
                sid=r.get('sample_id',r.get('id'))
                if sid not in latest or r.get('request_id'):latest[sid]=r
    ledger={r.get('request_id'):r for r in read(BUDGET/'ledger.json') if r.get('request_id')}
    proof=read(ROOT/'reports/finalfill_v7_20261024/geometry_1683_independent_proof.json')
    audited=[];approved={'train':[],'validation':[]}
    for sid,c in sorted(cases.items()):
        raw=latest.get(sid,{});entry=ledger.get(raw.get('request_id'))
        if not entry:
            audited.append({'sample_id':sid,'split':c['split'],'response_received':False,'training_approved':False});continue
        cached=read(BUDGET/(entry['cache_key']+'.json'));ch=cached['response']['choices'][0]
        assert ch['message'].get('content','')==raw['raw_review']
        review=parse_review(raw['raw_review'],len(c['canonical_candidates_with_audit_provenance']),ch.get('finish_reason'))
        effective=review;resolution=None
        if c['original_id']=='1683' and review.get('valid'):
            assert c['image_sha256']==proof['image_sha256'] and c['problem']==proof['question'] and str(c['reference_answer'])=='90'
            effective={**review,'task_status':'pass','task_issues':[]};resolution='geometry_1683_independent_proof.json; original AI verdict preserved'
        p=prune(c,effective)
        for name in ['positive_tokens','negative_tokens']:
            valid=[]
            for t in p[name]:
                try:token_key(t);valid.append(t)
                except Exception:p['masked'].append({'token':t,'status':'unsupported_reward_fact_parser'})
            p[name]=valid
        if resolution:
            p['positive_tokens']=[t for t in p['positive_tokens'] if t in proof['certified_image_only_tokens']]
        p['accepted']=bool(p['positive_tokens']) and effective.get('valid',False) and effective['task_status']=='pass' and c['original_id']!='742'
        p['model_perception']='<perception>'+'; '.join(p['positive_tokens'])+'</perception>' if p['positive_tokens'] else None
        audited.append({'sample_id':sid,'split':c['split'],'original_id':c['original_id'],'response_received':True,'review':review,'independent_task_resolution':resolution,'pruning':p,'request_id':raw['request_id'],'actual_finish_reason':ch.get('finish_reason')})
        if not p['accepted']:continue
        r={k:c[k] for k in ['sample_id','original_id','split','problem','reference_answer','image_path','image_sha256']}
        train=c['split']=='train'
        r.update(model_perception=p['model_perception'],certified_positive_tokens=p['positive_tokens'],certified_negative_tokens=p['negative_tokens'],masked_uncertain_facts=p['masked'],certified_fact_evidence=[x for x in p['certified_facts'] if x['token'] in p['positive_tokens']],training_approved=train,evaluation_approved=not train,perception_reward_enabled=train,perception_reward_mode='sparse_certified_v4',perception_reward_complete_categories=[],model_input_whitelist=['problem','image_path'],model_target_whitelist=['model_perception'],approval_request_id=raw['request_id'],human_review_performed=False,certification_scope='delegated AI plus deterministic guards; partial visual supervision',independent_task_resolution=resolution)
        approved[c['split']].append(r)
    out=DATA/'geometry';out.mkdir(exist_ok=True)
    from src.data.geometry_split_guard import guard
    quality_counts={k:len(v) for k,v in approved.items()};excluded=[]
    links=rows(ROOT/'data/project3_audit/geometry3k_intergps_links.jsonl')
    if (out/'summary.json').exists() and not (out/'pre_image_split_guard_summary.json').exists():
        (out/'pre_image_split_guard_summary.json').write_bytes((out/'summary.json').read_bytes())
    for split,rs in approved.items():
        approved[split],rejected=guard(rs,links);excluded+=rejected
    excluded_ids={r['sample_id']:r['image_split_guard_reason'] for r in excluded}
    for r in audited:
        r['image_split_guard_exclusion']=excluded_ids.get(r['sample_id'])
        r['release_approved']=r.get('pruning',{}).get('accepted',False) and r['sample_id'] not in excluded_ids
    write(out/'fact_quality_pass_but_image_overlap_isolated.jsonl',excluded)
    write(out/'all_case_audit.jsonl',audited)
    for split,rs in approved.items():write(out/(split+'_fact_pruned.jsonl'),rs)
    summary={'unique_cases':len(cases),'coverage_by_split':dict(Counter(c['split'] for c in cases.values())),'responses_by_split':dict(Counter(r['split'] for r in audited if r['response_received'])),'valid_reviews_by_split':dict(Counter(r['split'] for r in audited if r.get('review',{}).get('valid'))),'approved_by_split':{k:len(v) for k,v in approved.items()},'task_status':dict(Counter(r.get('review',{}).get('task_status','no_response') for r in audited)),'independent_task_resolutions':sum(bool(r.get('independent_task_resolution')) for r in audited),'api_calls':0,'text_guard_sha':sha(ROOT/'src/data/perception_text_guards.py'),'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sources if p.exists()},'no_test_used':True,'gold_precision':None}
    summary.update(fact_quality_approved_before_image_guard=quality_counts,image_split_exclusions_by_split=dict(Counter(r['split'] for r in excluded)),train_unique_pixel_images=len({r['image_pixel_sha256'] for r in approved['train']}),validation_unique_pixel_images=len({r['image_pixel_sha256'] for r in approved['validation']}),pixel_group_source_sha=sha(ROOT/'data/project3_audit/geometry3k_intergps_links.jsonl'))
    dump(out/'summary.json',summary);print(summary,flush=True)
if __name__=='__main__':run()
