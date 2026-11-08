"""Read-only, mutually exclusive geometry exits and full-pool image overlap."""
import hashlib,json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
REASONS=['格式失败','题答 uncertain','题答 isolate','全部事实被文字蕴含剔除','无剩余认证事实','同图隔离','其他']
TEXT_STATUSES={'text','deterministic_text_entailment_guard'}

def classify(row,with_val,with_test):
    review=row.get('review',{});p=row.get('pruning',{})
    if not row.get('response_received') or not review.get('valid'):
        return '格式失败','missing_response' if not row.get('response_received') else 'invalid_review_schema_or_finish'
    status=review.get('task_status')
    if row.get('independent_task_resolution'):status='pass'
    if row.get('original_id')=='742':status='isolate'
    if status=='uncertain':return '题答 uncertain','effective_task_status_uncertain'
    if status=='isolate':return '题答 isolate','effective_task_status_isolate'
    if status!='pass':return '其他','unexpected_effective_task_status'
    if not p.get('positive_tokens'):
        n=len(review.get('facts',[]))
        text_indices={m['index'] for m in p.get('masked',[]) if isinstance(m,dict) and type(m.get('index')) is int and m.get('status') in TEXT_STATUSES}
        if n>0 and text_indices==set(range(n)):
            return '全部事实被文字蕴含剔除','every_candidate_index_masked_as_text'
        return '无剩余认证事实','no_positive_after_all_fact_guards'
    if not p.get('accepted'):return '其他','quality_pruning_not_accepted_despite_positive_facts'
    if (row['split']=='train' and (with_val or with_test)) or (row['split']=='validation' and with_test):
        return '同图隔离','pixel_identity_reserved_by_heldout_split'
    if row.get('image_split_guard_exclusion'):return '其他',row['image_split_guard_exclusion']
    if row.get('release_approved'):return '批准','release_approved'
    return '其他','unexplained_release_rejection'

def rows(path):
    with path.open(encoding='utf-8') as f:return [json.loads(line) for line in f if line.strip()]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def overlap_counts(records):
    return {'checked_questions':len(records),'with_validation':sum(r['same_image_as_validation'] is True for r in records),
        'with_test':sum(r['same_image_as_test'] for r in records),
        'with_both':sum(r['same_image_as_validation'] is True and r['same_image_as_test'] for r in records),
        'validation_only':sum(r['same_image_as_validation'] is True and not r['same_image_as_test'] for r in records),
        'test_only':sum(r['same_image_as_test'] and r['same_image_as_validation'] is not True for r in records),
        'union':sum(r['same_image_as_validation'] is True or r['same_image_as_test'] for r in records)}

def run():
    audit=ROOT/'data/strict_v8_20261024/geometry/all_case_audit.jsonl'
    linkfile=ROOT/'data/project3_audit/geometry3k_intergps_links.jsonl'
    source=rows(audit);links=rows(linkfile);by={r['wrapper_locator']:r for r in links}
    assert len(by)==len(links) and len({r['sample_id'] for r in source})==len(source)
    val={r['image_pixel_sha256'] for r in links if r['wrapper_split']=='validation'}
    test={r['image_pixel_sha256'] for r in links if r['wrapper_split']=='test'}
    per_case=[]
    for r in source:
        image=by[r['sample_id']]
        assert image.get('original_id')==r.get('original_id') and image['wrapper_split']==r['split']
        pixel=image['image_pixel_sha256'];assert isinstance(pixel,str) and len(pixel)==64
        with_val=pixel in val if r['split']=='train' else None
        with_test=pixel in test;reason,detail=classify(r,with_val,with_test)
        assert (reason=='批准')==bool(r.get('release_approved')),r['sample_id']
        per_case.append({'sample_id':r['sample_id'],'original_id':r['original_id'],'split':r['split'],
            'primary_reason':reason,'detail':detail,'raw_task_status':r.get('review',{}).get('task_status'),
            'independent_task_resolution':r.get('independent_task_resolution'),
            'remaining_positive_count':len(r.get('pruning',{}).get('positive_tokens',[])),
            'image_pixel_sha256':pixel,'same_image_as_validation':with_val,'same_image_as_test':with_test})
    splits={}
    for split,total in [('train',2096),('validation',300)]:
        rs=[r for r in per_case if r['split']==split];assert len(rs)==total
        counts=Counter(r['primary_reason'] for r in rs);remaining=total;stages=[]
        for reason in REASONS:
            removed=counts[reason];stages.append({'reason':reason,'entering':remaining,'exited':removed,'remaining':remaining-removed});remaining-=removed
        assert remaining==counts['批准'] and sum(counts.values())==total
        isolated=[r for r in rs if r['primary_reason']=='同图隔离']
        splits[split]={'total':total,'approved':counts['批准'],'exited':total-counts['批准'],
            'exit_counts':{k:counts[k] for k in REASONS},'sequential_funnel':stages,
            'image_isolation_breakdown':overlap_counts(isolated),
            'all_rows_independent_image_check':overlap_counts(rs),
            'partition_validated':True}
    result={'schema_version':'geometry_funnel_v1','sources':{str(p.relative_to(ROOT)):sha(p) for p in [audit,linkfile]},
        'definitions':{'primary_reason_priority':REASONS,
            'all_text_rule':'Only when every indexed candidate fact (nonempty list) is masked as text or deterministic_text_entailment_guard. Checked before generic no-positive to avoid double counting.',
            'no_remaining_rule':'No certified positive remains, excluding the all-text case; mixed text/uncertain/grounding/parser removals belong here.',
            'format_rule':'Missing response or invalid strict schema/finish; takes precedence over the parser-generated uncertain status.',
            'task_resolution_rule':'Use recorded independent task resolution when present; preserve raw status separately; ID742 remains isolate.',
            'image_equality':'Exact decoded-pixel SHA256 from source linkage; not perceptual or semantic similarity.',
            'image_reference_scope':'All official validation300/test601 image identities, including annotation-unmatched items; no evaluation answers/facts used.',
            'same_image_as_validation_for_validation':None,
            'image_overlap_note':'with_validation and with_test overlap; union=validation_only+test_only+with_both. Exit counts are conditional on passing earlier gates, full-pool overlap ignores all earlier gates.',
            'approved_is_not_an_exit':True},
        'reference_image_counts':{'validation_rows':sum(r['wrapper_split']=='validation' for r in links),'test_rows':sum(r['wrapper_split']=='test' for r in links),'validation_unique_pixel_images':len(val),'test_unique_pixel_images':len(test)},
        'splits':splits,'all_2096_train_image_check':splits['train']['all_rows_independent_image_check'],
        'cases':per_case,'api_calls':0,'input_files_modified':False}
    out=ROOT/'reports/strict_v8_20261024/geometry_funnel.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert result['sources'][str(audit.relative_to(ROOT))]==sha(audit)
    print(json.dumps({'output':str(out),'splits':splits,'all_train_image_check':result['all_2096_train_image_check']},ensure_ascii=False),flush=True)

if __name__=='__main__':run()
