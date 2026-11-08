"""Deterministic offline blind packet. No client, API, test export, or source edits."""
import base64
import csv
import hashlib
import io
import json
import random
import re
import zipfile
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SEED = 20261024


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''): h.update(block)
    return h.hexdigest()


def readrows(p):
    with Path(p).open(encoding='utf8') as f: return [json.loads(l) for l in f if l.strip()]


def save(p,v):
    Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def sample_cases(audit,funnel):
    reasons={r['sample_id']:r['primary_reason'] for r in funnel['cases']}
    rng=random.Random(SEED); selected=[]; populations={}
    for group,counts in [('A',{'train':25,'validation':5}),('B',{'train':25,'validation':5}),('C',{'train':12,'validation':3})]:
        for split,k in counts.items():
            def eligible(r):
                review=r.get('review',{})
                if group=='A': return review.get('valid') and review.get('task_status')=='uncertain' and reasons[r['sample_id']]=='题答 uncertain'
                if group=='B': return review.get('valid') and review.get('task_status')=='pass' and reasons[r['sample_id']]=='无剩余认证事实'
                return r.get('release_approved') is True
            pool=sorted([r for r in audit if r['split']==split and eligible(r)],key=lambda x:x['sample_id'])
            if len(pool)<k: raise ValueError(f'Insufficient pool {group}/{split}: {len(pool)}')
            populations[group+'/'+split]=len(pool)
            selected.extend({'row':r,'group':group} for r in rng.sample(pool,k))
    if len({s['row']['sample_id'] for s in selected})!=75: raise ValueError('Sampling overlaps')
    rng.shuffle(selected)
    return selected,populations


def natural_fact(f):
    def entity(e):
        if isinstance(e,str):return e
        if isinstance(e,list):return '、'.join(entity(x) for x in e)
        if 'source_radius_id' in e:
            return f"圆（源圆心名 {e['center']}；源圆区分记号 {e['source_radius_id']}，是否可见待核）"
        if 'points' in e:return f"{e['kind']} 弧（{entity(e['points'])}）"
        if 'boundary' in e:return f"{e['shape']}（边界顺序 {entity(e['boundary'])}）"
        raise ValueError('Unknown entity: '+repr(e))
    rel=f['relation'];e=f['entities'];value=f.get('value','');unit=f.get('unit','')
    args=[entity(x) for x in e] if isinstance(e,list) else [entity(e)]
    unit_text='度' if unit=='deg' else '（源未指定单位）' if unit.startswith('unspecified') else unit
    if rel=='Length':return f'线段 {args[0]}{args[1]} 的标注长度为 {value}{unit_text}'
    if rel=='Angle':return f'角 {args[0]}{args[1]}{args[2]}（顶点 {args[1]}）的标注角度为 {value}{unit_text}'
    if rel in {'Parallel','Perpendicular','CongruentLength','CongruentAngle'}:
        return args[0]+' 与 '+args[1]+{'Parallel':' 平行','Perpendicular':' 垂直','CongruentLength':' 等长','CongruentAngle':' 角度相等'}[rel]
    if rel=='PointLiesOnLine':return f'点 {args[0]} 在直线（{args[1]}）上'
    if rel=='PointLiesOnCircle':return f'点 {args[0]} 在 {args[1]} 上'
    if rel=='Tangent':return f'直线（{args[0]}）与 {args[1]} 相切'
    if rel in {'ArcMeasure','ArcLength','Area'}:return f"{args[0]} 的"+{'ArcMeasure':'弧度数','ArcLength':'弧长','Area':'面积'}[rel]+f'为 {value}{unit_text}'
    raise ValueError('Untranslated candidate '+rel)


def run():
    blind=OUT/'blind';keydir=OUT/'key'
    if blind.exists() or keydir.exists():raise FileExistsError('Packet exists; use a new version, do not resample silently')
    paths=[ROOT/p for p in ['data/strict_v8_20261024/geometry/all_case_audit.jsonl','reports/strict_v8_20261024/geometry_funnel.json',
        'data/project3_audit/geometry3k_intergps_links.jsonl','data/project3_audit/intergps_annotations.jsonl',
        'reports/data_release_preparation_20261024/shared_api_cache.zip','data/portable_release/manifest.json',
        'data/portable_release/project3_train_fact_pruned.jsonl','data/portable_release/project3_validation_fact_pruned.jsonl']]
    missing=[str(p.relative_to(ROOT)) for p in paths if not p.exists()]
    if missing:save(OUT/'sampling_report.json',{'missing':missing,'api_calls':0});raise FileNotFoundError(missing)
    before={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}
    audit=readrows(paths[0]);funnel=json.loads(paths[1].read_text(encoding='utf8'))
    for p,h in funnel['sources'].items():
        if sha(ROOT/p)!=h:raise ValueError('Funnel source identity mismatch')
    selected,populations=sample_cases(audit,funnel)
    byrequest={s['row']['request_id']:s for s in selected};cached={};prompts={}
    with zipfile.ZipFile(paths[4]) as z:
        for name in z.namelist():
            if not name.endswith('.json'):continue
            raw=z.read(name)
            # Filter by byte-level request ID before parsing irrelevant cached payloads.
            if not any(rid.encode() in raw for rid in byrequest):continue
            c=json.loads(raw)
            if not isinstance(c,dict) or not isinstance(c.get('response'),dict):continue
            rid=c['response'].get('id')
            if rid not in byrequest:continue
            if rid in cached:raise ValueError('Duplicate cached response identity')
            cached[rid]=(c,name,hashlib.sha256(raw).hexdigest())
    absent=[r for r in byrequest if r not in cached]
    if absent:save(OUT/'sampling_report.json',{'missing_request_ids':absent,'api_calls':0});raise FileNotFoundError('Missing actual responses; no fabricated text')
    annotation={r['original_id']:r for r in readrows(paths[3]) if r['split'] in {'train','validation'}}
    blind.mkdir();keydir.mkdir();(blind/'images').mkdir()
    keys=[];manifest=[];batches=[[] for _ in range(5)];archives={};image_inputs={}
    for i,s in enumerate(selected,1):
        r=s['row'];bid=f'B{i:03d}';assert r['split'] in {'train','validation'}
        c,member,cache_sha=cached[r['request_id']];payload=c['payload'];msgs=payload['messages']
        text=next(x['text'] for x in msgs[1]['content'] if x['type']=='text');q=json.loads(text)
        system=msgs[0]['content'];psha=hashlib.sha256(system.encode()).hexdigest();prompts[psha]=system
        image_url=next(x['image_url']['url'] for x in msgs[1]['content'] if x['type']=='image_url')
        supplied=base64.b64decode(image_url.split(',',1)[1])
        a=annotation[r['original_id']];archive,member0=a['original_locator'].split('::')
        if archive not in archives:
            path=ROOT/'data/project3_sources/intergps/data/geometry3k'/archive
            archives[archive]=zipfile.ZipFile(path)
            rel=str(path.relative_to(ROOT)).replace('\\','/');before[rel]=sha(path)
        image_member=member0.rsplit('/',1)[0]+'/img_diagram.png'
        original=archives[archive].read(image_member)
        if supplied!=original:raise ValueError('Cached input differs from official original bytes: '+bid)
        image_inputs[bid]={'source':archive+'::'+image_member,'sha256':hashlib.sha256(original).hexdigest()}
        im=Image.open(io.BytesIO(original)).convert('RGB');im.thumbnail((1200,1200),Image.Resampling.LANCZOS)
        im.info.clear()
        im.save(blind/'images'/f'{bid}.png')
        facts=q['candidate_facts']
        if [f['index'] for f in facts]!=list(range(len(facts))):raise ValueError('Candidate index discontinuity')
        question=a['original_data']['problem_text'];answer=a['answer']
        diagram=a['diagram_annotation']['diagram_logic_forms'];prose=a['text_annotation']['text_logic_forms']
        body=f'## {bid}\n\n![图](images/{bid}.png)\n\n### 官方题干\n\n{question}\n\n### 官方标准答案\n\n{answer}\n\n### 候选事实（逐条判断，不预设真假）\n\n'
        body+='\n'.join(f"{j+1}. {natural_fact(f['fact'])}" for j,f in enumerate(facts)) or '（候选列表为空）'
        body+='\n\n### 对应 InterGPS 原始条件（图示）\n\n```text\n'+'\n'.join(diagram)+'\n```\n\n### 对应 InterGPS 原始条件（文字）\n\n```text\n'+'\n'.join(prose)+'\n```\n'
        batches[(i-1)//15].append(body)
        ch=c['response']['choices'][0]
        keys.append({'blind_id':bid,'sample_id':r['sample_id'],'original_id':r['original_id'],'split':r['split'],'group':s['group'],
            'raw_task_status':json.loads(ch['message'].get('content','{}')).get('task_status'),
            'parsed_task_status':r.get('review',{}).get('task_status'),'raw_AI_response':ch['message'].get('content',''),
            'removed_fact_reasons':r.get('pruning',{}).get('masked',[]),'final_certified_facts':r.get('pruning',{}).get('certified_facts',[]),
            'final_certified_tokens':r.get('pruning',{}).get('positive_tokens',[]),'cache_member':member,'cache_sha256':cache_sha,
            'request_model':payload.get('model'),'response_model':c['response'].get('model'),'prompt_sha256':psha,
            'supplied_image_bytes_match_original':True,'candidate_count':len(facts),'candidate_facts_original':facts})
        manifest.append({'blind_id':bid,'sample_id':r['sample_id'],'original_id':r['original_id'],'split':r['split'],'group':s['group'],'candidate_count':len(facts)})
    for z in archives.values():z.close()
    for i,batch in enumerate(batches,1):(blind/f'batch_{i}.md').write_text(f'# 独立图题核查：批次 {i}\n\n'+'\n\n---\n\n'.join(batch),encoding='utf8')
    with (blind/'review_template.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['blind_id','题干与图一致','标准答案与图一致','候选事实逐条 T/F/看不清','备注'])
        for k in keys:w.writerow([k['blind_id'],'','','',''])
    (blind/'README.md').write_text('# 独立核查\n\n按批次查看原图、官方题干、标准答案与候选条件。候选不预设正确；逐条记录 T/F/看不清。不得从既有意见推断结论。review_template.csv 是填表模板。\n',encoding='utf8')
    (keydir/'key.jsonl').write_text(''.join(json.dumps(k,ensure_ascii=False)+'\n' for k in keys),encoding='utf8')
    save(OUT/'sample_manifest.json',{'seed':SEED,'rng':'random.Random; group order A/B/C; split order train/validation; sample(sorted(sample_id),k), then same RNG shuffle','populations':populations,'samples':manifest})
    (OUT/'sample_manifest.sha256').write_text(sha(OUT/'sample_manifest.json')+'  sample_manifest.json\n',encoding='ascii')
    save(OUT/'audit_prompts.json',prompts)
    after={p:sha(ROOT/p) for p in before}
    save(OUT/'sampling_report.json',{'api_calls':0,'missing':[],'source_sha256_before':before,'source_sha256_after':after,
        'inputs_unchanged':before==after,'sample_manifest_sha256':sha(OUT/'sample_manifest.json'),
        'counts':dict(Counter(x['group']+'/'+x['split'] for x in manifest)),'selected_image_sources_PRIVATE':image_inputs,
        'audit_models':dict(Counter(x['request_model'] for x in keys)), 'response_models':dict(Counter(str(x['response_model']) for x in keys)),
        'prompt_versions':list(prompts),'funnel_source':'existing geometry_funnel.json; source SHA matched; not regenerated',
        'blind_export_files':{str(p.relative_to(blind)).replace('\\','/'):sha(p) for p in blind.rglob('*') if p.is_file()}})
    assert before==after
    print(json.dumps({'api_calls':0,'samples':len(keys),'populations':populations,'inputs_unchanged':True},ensure_ascii=False))


if __name__=='__main__':run()
