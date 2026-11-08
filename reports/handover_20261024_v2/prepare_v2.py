"""Create versioned config drafts and read-only analysis artifacts. No models/API."""
import json
import hashlib
from collections import Counter
from pathlib import Path
from .strict_geometry import parallel_scores
from .project3_v2 import PROTOCOL, supervised_view

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent


def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rows(p):return [json.loads(l) for l in Path(p).read_text(encoding='utf8').splitlines() if l.strip()]


def run():
    folder=OUT/'configs';folder.mkdir(exist_ok=True)
    c={'protocol':PROTOCOL,'data_manifest':'data/portable_release/manifest.json','data_file':'project3_train_fact_pruned.jsonl',
       'model':'Qwen/Qwen2.5-VL-3B-Instruct','model_revision':'66285546d2b821cf421d4f5eb2576359d3770cd3','initial_state':'V0',
       'processor':'same_as_model_revision','vision':True,'stage':'rl','seed':42,'max_steps':2,'learning_rate':2e-5,
       'batch_size':1,'gradient_accumulation_steps':8,'save_steps':1,'lora_r':16,'lora_alpha':32,'max_pixels':802816,
       'max_length':3800,'max_prompt_length':1752,'max_new_tokens':2048,'num_generations':4,'generation_batch_size':4,'beta':.04,
       'format_reward_weight':.05,'perception_reward_weight':0.,'perception_score_version':'frozen_v4',
       'output_root':'reports/handover_20261024_v2/runs/paired_rl','status':'draft_smoke_GPU_未验证'}
    save(folder/'v3_v0_answer_format.json',c)
    for weight in [.1,.2,.4]:
        v=dict(c,perception_reward_weight=weight)
        save(folder/(('v4_v0_perception.json' if weight==.2 else f'scan_lambda_{str(weight).replace(".","p")}.json')),v)
    for mode in ['answer_v1','perception_answer_v2']:
        s={k:v for k,v in c.items() if k not in ['perception_reward_weight','format_reward_weight','num_generations','generation_batch_size','max_new_tokens','max_prompt_length','beta','perception_score_version']}
        s.update(stage='sft',supervision=mode,output_root='reports/handover_20261024_v2/runs/paired_sft')
        save(folder/(mode+'.json'),s)
    legacy=json.loads((ROOT/'configs/project3_sparse_v4_grpo_smoke.json').read_text(encoding='utf8'))
    legacy['output_dir']='reports/handover_20261024_v2/runs/engineering_perception_sft_to_sparse_rl'
    save(folder/'engineering_perception_sft_to_sparse_rl.json',legacy)
    train=rows(ROOT/'data/portable_release/project3_train_fact_pruned.jsonl');valid=rows(ROOT/'data/portable_release/project3_validation_fact_pruned.jsonl')
    diffs=[];strict_invalid=[]
    for r in train+valid:
        s=parallel_scores(r['model_perception'],r['certified_positive_tokens'],r['certified_negative_tokens'])
        if not s['strict_validation']['valid']:strict_invalid.append({'sample_id':r['sample_id'],**s['strict_validation']})
        if any(s['frozen_v4'][k]!=s['strict_v5'][k] for k in ['format_valid','reward','f1']):diffs.append({'sample_id':r['sample_id'],**s})
    save(OUT/'label_score_comparison.json',{'rows':len(train+valid),'strict_invalid':strict_invalid,'differences':diffs,'frozen_scorer_modified':False})
    # Local target-only tokenizer count is an explicit proxy, not a VL label count.
    from transformers import AutoTokenizer
    tokenizer_path=ROOT/'data/tokenizers/Qwen2.5-7B-Instruct'
    tok=AutoTokenizer.from_pretrained(tokenizer_path,local_files_only=True)
    counts={}
    for mode in ['answer_v1','perception_answer_v2']:
        per=[{'sample_id':r['sample_id'],'target_only_text_tokens':len(tok.encode(supervised_view(r,mode)['target'],add_special_tokens=False))} for r in train]
        counts[mode]={'rows':len(per),'total':sum(r['target_only_text_tokens'] for r in per),'mean':sum(r['target_only_text_tokens'] for r in per)/len(per),'maximum':max(r['target_only_text_tokens'] for r in per),'per_sample':per}
    save(OUT/'supervision_token_counts.json',{'status':'text_tokenizer_proxy_measured; actual_VL_assistant_labels_未验证','tokenizer':str(tokenizer_path.relative_to(ROOT)).replace('\\','/'),
        'tokenizer_files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tokenizer_path.iterdir() if p.is_file()},
        'includes_template_end_tokens':False,'counts':counts})
    audit=rows(ROOT/'data/strict_v8_20261024/geometry/all_case_audit.jsonl')
    links=rows(ROOT/'data/project3_audit/geometry3k_intergps_links.jsonl');by={r['wrapper_locator']:r for r in links}
    heldout={r['image_pixel_sha256'] for r in links if r['wrapper_split'] in {'validation','test'}}
    remaining=[r for r in audit if r['split']=='train' and by[r['sample_id']]['image_pixel_sha256'] not in heldout]
    def status(r):return '格式失败' if not r.get('response_received') or not r.get('review',{}).get('valid') else r['review']['task_status']
    def effective(r):return 'pass' if r.get('independent_task_resolution') and status(r)!='格式失败' else status(r)
    save(OUT/'answer_pool_scale.json',{'train_total':sum(r['split']=='train' for r in audit),'overlap_removed':2096-len(remaining),'remaining':len(remaining),
        'audit_parsed_task_status_counts':dict(Counter(status(r) for r in remaining)), 'effective_recorded_resolution_counts':dict(Counter(effective(r) for r in remaining)),
        'approval_unchanged':'609 train / 82 validation; this analysis grants no training approval',
        'sources':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'data/strict_v8_20261024/geometry/all_case_audit.jsonl',ROOT/'data/project3_audit/geometry3k_intergps_links.jsonl']}})
    print(json.dumps({'label_differences':len(diffs),'strict_invalid':len(strict_invalid),'remaining_train':len(remaining),'raw_status':dict(Counter(status(r) for r in remaining))},ensure_ascii=False))


if __name__=='__main__':run()
