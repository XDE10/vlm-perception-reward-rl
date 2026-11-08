import argparse
import copy
import csv
import hashlib
import json
import re
from pathlib import Path
import pytest
from .strict_geometry import parallel_scores, validate_completion
from .project3_v2 import (prompt, supervised_view, LoggedRewards, summarize_rollouts,
                         format_score, parameter_identity, PairedVisualCollator, rl_view)
from .build_blind_pack import sample_cases, readrows, ROOT, OUT
from .diagnose_project3_vision_v2 import begin_identity


def config(name):return json.loads((OUT/'configs'/name).read_text(encoding='utf8'))
def release_rows():return readrows(ROOT/'data/portable_release/project3_train_fact_pruned.jsonl')


def test_v3_v4_differ_only_perception_weight():
    v3=config('v3_v0_answer_format.json');v4=config('v4_v0_perception.json')
    assert {k for k in v3 if v3[k]!=v4[k]}=={'perception_reward_weight'}
    assert v3['perception_reward_weight']==0 and v4['perception_reward_weight']==.2
    assert v3['initial_state']=='V0' and v3['format_reward_weight']==.05
    for c in [v3,v4]:
        assert c['model']=='Qwen/Qwen2.5-VL-3B-Instruct'
        assert c['max_prompt_length']+c['max_new_tokens']==c['max_length']
        assert not any(re.search(r'[A-Za-z]:[\\/]',str(x)) for x in c.values())
    row=release_rows()[0]
    assert rl_view(row,v3)==rl_view(row,v4)
    assert row['reference_answer'] not in json.dumps(rl_view(row,v3)['prompt'])


def test_v1_v2_same_scope_template_and_start():
    a=config('answer_v1.json');b=config('perception_answer_v2.json')
    assert {k for k in a if a[k]!=b[k]}=={'supervision'}
    r=release_rows()[0];original=copy.deepcopy(r)
    one=supervised_view(r,'answer_v1');two=supervised_view(r,'perception_answer_v2')
    assert one['input']==two['input'] and set(one['input'])=={'problem','image_path'}
    assert one['target']=='<perception></perception><answer>4</answer>'
    assert two['target']==r['model_perception']+'<answer>4</answer>'
    assert '<reasoning>' not in one['target']+two['target'] and r==original


@pytest.mark.parametrize('text',['Angle(A,B)=60 deg','Angle(A,A,C)=60 deg','Length(X,Y)=-3','Length(A,B)=0','Parallel((A,B),(B,A))','Tangent(Circle(O),(A,B))'])
def test_strict_rejects_invalid_geometry(text):
    s=parallel_scores('<perception>'+text+'</perception>',['Length(A,B)=3'],[])
    assert not s['strict_v5']['format_valid'] and s['strict_v5']['reward']==0


def test_reflex_is_not_silently_redefined_and_empty_gold_is_masked():
    assert validate_completion('<perception>Angle(A,B,C)=270 deg</perception>')['valid']
    s=parallel_scores('<perception></perception>',[],[])
    assert s['strict_v5']['mask'] is False and s['frozen_v4']['mask'] is False


def test_frozen_and_strict_label_comparison_complete():
    data=json.loads((OUT/'label_score_comparison.json').read_text(encoding='utf8'))
    assert data['rows']==691
    # Difference lists are audit output, never a test-driven reason to alter labels.
    assert data['frozen_scorer_modified'] is False


def test_logs_every_rollout_without_trl_metrics_and_monitoring(tmp_path):
    logger=LoggedRewards(tmp_path/'rollouts.jsonl',.2,verifier=lambda t,r:{'correct':True,'status':'test_stub'})
    texts=['<perception>Length(B,A)=3; Length(X,Y)=7</perception><answer>4</answer>',
           '<perception>Length(A,B)=4</perception><answer>4</answer>']
    assert logger.answer_reward(texts,['4','4'],['s1','s2'],[['Length(A,B)=3']]*2,[[],[]])==[1.,1.]
    rs=readrows(tmp_path/'rollouts.jsonl');assert len(rs)==2
    assert rs[0]['TP']==1 and rs[0]['masked']==1 and rs[1]['FP']==1
    assert rs[0]['raw_output']==texts[0] and rs[0]['format_reward']==1
    assert rs[0]['weighted_reward']==1.25
    summary=summarize_rollouts(rs)
    assert summary['masked_fact_fraction']==pytest.approx(1/3)
    assert summary['mean_certified_recall']==.5
    assert 'F1=1' in summary['answer_accuracy_by_F1']
    with pytest.raises(ValueError):logger.answer_reward(texts,['4'],['s1','s2'],[[],[]],[[],[]])


def test_requires_grad_probe_exports_and_fails_closed(tmp_path):
    import torch
    class Tiny(torch.nn.Module):
        def __init__(self):
            super().__init__();self.visual=torch.nn.ModuleDict({'encoder':torch.nn.Linear(2,2),'merger':torch.nn.Linear(2,2)})
            self.language_lora=torch.nn.Linear(2,2)
    m=Tiny()
    for p in m.visual.parameters():p.requires_grad=False
    identity=parameter_identity(m,tmp_path/'identity.json')
    assert identity['visual_frozen'] and identity['trainable_full_names']==['language_lora.weight','language_lora.bias']
    m.visual['merger'].weight.requires_grad=True
    with pytest.raises(ValueError):parameter_identity(m)


def test_visual_collator_masks_prefix_and_padding_and_rejects_budget():
    import torch
    class Processor:
        def apply_chat_template(self,messages,**kwargs):
            prefix=str(messages[0])+'<image-token>'+str(messages[1])+'ASSISTANT:'
            return prefix+(messages[-1]['content'] if messages[-1]['role']=='assistant' else '')
        def __call__(self,text,images,**kwargs):
            ids=[[ord(c) for c in s] for s in text];n=max(map(len,ids))
            return {'input_ids':torch.tensor([x+[0]*(n-len(x)) for x in ids]),
                'attention_mask':torch.tensor([[1]*len(x)+[0]*(n-len(x)) for x in ids]),'pixel_values':torch.zeros(len(ids),3,2,2)}
    r=release_rows()[0];other=dict(r,problem=r['problem']+' additional text')
    p=Processor();batch=PairedVisualCollator(p,10000,'answer_v1')([r,other])
    assert torch.all(batch['labels'][batch['attention_mask']==0]==-100)
    assert torch.any(batch['labels']!=-100) and torch.all(batch['labels'][:,:20]==-100)
    with pytest.raises(ValueError):PairedVisualCollator(p,1,'answer_v1')([r])


def test_diagnostic_identity_precedes_model_loading_and_hashes_adapter(tmp_path):
    adapter=tmp_path/'adapter';adapter.mkdir();(adapter/'adapter_model.safetensors').write_bytes(b'test-only')
    data=tmp_path/'data.jsonl';data.write_text('{}\n')
    args=argparse.Namespace(output=str(tmp_path/'out.jsonl'),data=str(data),adapter=str(adapter),model='remote/model')
    ident=begin_identity(args)
    assert ident['status']=='started'
    assert ident['adapter_sha256']['adapter_model.safetensors']==hashlib.sha256(b'test-only').hexdigest()
    assert Path(args.output+'.identity.json').exists() and not Path(args.output).exists()


def test_diagnostic_failure_preserves_started_identity(tmp_path,monkeypatch):
    import sys
    from . import diagnose_project3_vision_v2 as diagnostic
    data=tmp_path/'data.jsonl';data.write_text('{}\n')
    target=tmp_path/'out.jsonl'
    monkeypatch.setattr(sys,'argv',['diagnostic','--data',str(data),'--output',str(target)])
    def fail(args):
        assert json.loads(Path(args.output+'.identity.json').read_text(encoding='utf8'))['status']=='started'
        raise RuntimeError('test failure before any model load')
    monkeypatch.setattr(diagnostic,'run_diagnostic',fail)
    with pytest.raises(RuntimeError):diagnostic.main()
    saved=json.loads(Path(str(target)+'.identity.json').read_text(encoding='utf8'))
    assert saved['status']=='failed_or_interrupted' and saved['error_type']=='RuntimeError'


def test_blind_selection_is_seeded_sorted_and_exact():
    audit=readrows(ROOT/'data/strict_v8_20261024/geometry/all_case_audit.jsonl')
    funnel=json.loads((ROOT/'reports/strict_v8_20261024/geometry_funnel.json').read_text(encoding='utf8'))
    chosen,_=sample_cases(audit,funnel);shuffled,_=sample_cases(list(reversed(audit)),funnel)
    expected=[r['row']['sample_id'] for r in chosen]
    assert expected==[r['row']['sample_id'] for r in shuffled]
    actual=json.loads((OUT/'sample_manifest.json').read_text(encoding='utf8'))
    assert expected==[r['sample_id'] for r in actual['samples']]
    assert len(set(expected))==75 and all(r['row']['split'] in {'train','validation'} for r in chosen)
    original={r['sample_id']:r for r in audit}
    for row in readrows(OUT/'key/key.jsonl'):
        assert row['raw_task_status']==json.loads(row['raw_AI_response'])['task_status']
        assert row['parsed_task_status']==original[row['sample_id']]['review']['task_status']


def test_blind_directory_contains_no_identity_verdict_reason_or_group():
    keys=readrows(OUT/'key/key.jsonl');texts='\n'.join(p.read_text(encoding='utf-8-sig') for p in (OUT/'blind').rglob('*') if p.suffix in {'.md','.csv'})
    forbidden_fields=['sample_id','original_id','raw_task_status','primary_reason','training_approved','evaluation_approved','request_id']
    assert not any(x in texts for x in forbidden_fields)
    for row in keys:
        assert row['sample_id'] not in texts
        assert not re.search(r'(?:original_id|原始\s*ID|样本\s*ID)\s*[:=：]\s*'+re.escape(row['original_id'])+r'\b',texts)
        assert row['raw_AI_response'] not in texts
        ai=json.loads(row['raw_AI_response'])
        reasons=list(ai.get('task_issues',[]))+[f['evidence'] for f in ai.get('facts',[]) if f.get('evidence')]
        assert not any(reason in texts for reason in reasons)
        assert not re.search(r'(?:组别\s*[:：=]\s*|\bgroup\s*[:：=]\s*)'+row['group']+r'\b',texts)
    for p in (OUT/'blind/images').iterdir():assert re.fullmatch(r'B\d{3}\.png',p.name)
    report=json.loads((OUT/'sampling_report.json').read_text(encoding='utf8'))
    assert report['api_calls']==0 and report['inputs_unchanged']


def test_blind_images_and_reviews_have_exact_coverage():
    from PIL import Image
    keys=readrows(OUT/'key/key.jsonl');assert len(keys)==75
    images=list((OUT/'blind/images').glob('*.png'));assert len(images)==75
    for p in images:
        with Image.open(p) as image:
            assert max(image.size)<=1200
            assert not image.info
    for i in range(1,6):assert len(re.findall(r'^## B\d{3}$',(OUT/f'blind/batch_{i}.md').read_text(encoding='utf8'),re.M))==15
    with (OUT/'blind/review_template.csv').open(encoding='utf-8-sig') as f:assert len(list(csv.DictReader(f)))==75


def test_installed_trl_routes_private_metadata_and_three_rewards_without_training(tmp_path):
    from transformers import GPT2Config,GPT2LMHeadModel,PreTrainedTokenizerFast
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from datasets import Dataset
    from trl import GRPOConfig,GRPOTrainer
    model=GPT2LMHeadModel(GPT2Config(vocab_size=4,n_positions=32,n_embd=8,n_layer=1,n_head=1))
    local=tmp_path/'tiny_base';model.save_pretrained(local);model.config._name_or_path=str(local)
    backend=Tokenizer(WordLevel({'[UNK]':0,'[PAD]':1,'[EOS]':2,'question':3},unk_token='[UNK]'))
    tok=PreTrainedTokenizerFast(tokenizer_object=backend,unk_token='[UNK]',pad_token='[PAD]',eos_token='[EOS]')
    tok.chat_template="{% for message in messages %}{{ message['content'] }}{% endfor %}"
    args=GRPOConfig(output_dir=str(tmp_path/'out'),use_cpu=True,bf16=False,fp16=False,max_steps=1,per_device_train_batch_size=2,
        num_generations=2,generation_batch_size=2,max_completion_length=4,beta=.04,report_to='none',save_strategy='no',gradient_checkpointing=False,
        reward_weights=[1.,.05,.2])
    logger=LoggedRewards(tmp_path/'actual_trl_dispatch.jsonl',.2)
    inputs=[{'prompt':'question','sample_id':sid,'reference_answer':'4','certified_positive_tokens':['Length(A,B)=3'],'certified_negative_tokens':[]} for sid in ['s1','s2']]
    trainer=GRPOTrainer(model=model,args=args,train_dataset=Dataset.from_list(inputs),processing_class=tok,
        reward_funcs=[logger.answer_reward,logger.format_reward,logger.perception_reward])
    # No train(), generate(), backward() or optimizer update. Exercise real TRL dispatch only.
    trainer._log_metric=lambda *a,**kw:pytest.fail('Logging must not depend on TRL metric forwarding')
    outputs=['<perception>Length(A,B)=3</perception><answer>4</answer>',
             '<perception>Length(A,B)=4</perception><answer>3</answer>']
    rewards=trainer._calculate_rewards(inputs,['question']*2,outputs,[[3],[3]])
    assert rewards.tolist()==[[1.,1.,1.],[0.,1.,0.]]
    logged=readrows(tmp_path/'actual_trl_dispatch.jsonl')
    assert [r['sample_id'] for r in logged]==['s1','s2'] and logged[1]['FP']==1
