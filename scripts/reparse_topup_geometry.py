"""Zero-call sidecar parsing: retain raw response, actual finish and fact guards."""
from collections import Counter
from scripts.topup_common import *
from src.data.perception_v4 import parse_review,prune,token_key
def run():
    source=REPORT/'p3_fact_review.jsonl'
    if not source.exists():return
    allcases=rows(DATA/'project3/cases.jsonl')
    if (DATA/'project3_reserve/cases.jsonl').exists():allcases+=rows(DATA/'project3_reserve/cases.jsonl')
    cases={r['sample_id']:r for r in allcases};ledger=read(BUDGET/'ledger.json');by_request={r.get('request_id'):r for r in ledger if r.get('request_id')};out=[]
    records=rows(source)
    if (REPORT/'p3_reserve_fact_review.jsonl').exists():records+=rows(REPORT/'p3_reserve_fact_review.jsonl')
    for raw in records:
        sid=raw.get('sample_id',raw['id']);c=cases[sid];r=by_request.get(raw.get('request_id'))
        if not r:out.append({**raw,'sidecar_status':'no_completed_response_evidence','training_approved':False});continue
        response=read(BUDGET/(r['cache_key']+'.json'));ch=response['response']['choices'][0]
        assert ch['message'].get('content','')==raw['raw_review']
        review=parse_review(raw['raw_review'],len(c['canonical_candidates_with_audit_provenance']),ch.get('finish_reason'));p=prune(c,review)
        # A parser-unsupported proposition is masked individually, not whole-case.
        for name in ['positive_tokens','negative_tokens']:
            keep=[]
            for token in p[name]:
                try:token_key(token);keep.append(token)
                except Exception:p['masked'].append({'token':token,'status':'unsupported_reward_fact_parser'})
            p[name]=keep
        p['accepted']=bool(p['positive_tokens']) and review.get('valid',False) and review['task_status']=='pass' and c['original_id']!='742'
        p['model_perception']='<perception>'+'; '.join(p['positive_tokens'])+'</perception>' if p['positive_tokens'] else None
        out.append({**raw,'review':review,'pruning':p,'sidecar_status':'strict_reparse_with_recorded_metadata_normalization','actual_finish_reason':ch.get('finish_reason')})
    write(REPORT/'p3_fact_review_reparsed.jsonl',out);dump(REPORT/'p3_reparsed_summary.json',{'records':len(out),'accepted_by_split':dict(Counter(r['split'] for r in out if r.get('pruning',{}).get('accepted'))),'task_statuses':dict(Counter(r.get('review',{}).get('task_status','not_reviewed') for r in out)),'positive_facts':sum(len(r.get('pruning',{}).get('positive_tokens',[])) for r in out),'explicit_negative_facts':sum(len(r.get('pruning',{}).get('negative_tokens',[])) for r in out),'api_calls':0,'raw_source_sha':sha(source),'extra_raw_source_sha':sha(REPORT/'p3_reserve_fact_review.jsonl') if (REPORT/'p3_reserve_fact_review.jsonl').exists() else None,'parser_sha':sha(ROOT/'src/data/perception_v4.py')})
    print(read(REPORT/'p3_reparsed_summary.json'),flush=True)
if __name__=='__main__':run()
