import hashlib,json
import pytest
from src.data.approved_training_inputs import load_approved,model_view


def test_approval_scope_and_hash_cannot_be_bypassed(tmp_path):
    row={'sample_id':'a','problem':'Find x','solution':'x=1','training_approved':True}
    f=tmp_path/'train.jsonl';f.write_text(json.dumps(row)+'\n',encoding='utf-8')
    m=tmp_path/'manifest.json';m.write_text(json.dumps({'approved_training_files':['train.jsonl'],'files':{'train.jsonl':hashlib.sha256(f.read_bytes()).hexdigest()}}),encoding='utf-8')
    assert len(load_approved(m,'train.jsonl'))==1
    with pytest.raises(ValueError):load_approved(m,'dev.jsonl')
    f.write_text('{}\n',encoding='utf-8')
    with pytest.raises(ValueError):load_approved(m,'train.jsonl')


def test_model_input_never_contains_reference_or_audit_fields():
    r={'sample_id':'a','problem':'Find x','prompt':'Exact sealed prompt','domain':'math','solution':'x=1','reference_answer':'1','raw_review':'private audit','training_approved':True}
    assert model_view(r,'opd')=={'input':{'prompt':'Find x','domain':'math'},'target':None}
    r['domain']='code';assert model_view(r,'opd')['input']['prompt']=='Exact sealed prompt'
    assert model_view(r,'math_sft')=={'input':{'problem':'Find x'},'target':'x=1'}
    r.update(image_path='x.png',model_perception='<perception>Length(A,B)=2</perception>',model_input_whitelist=['problem','image_path'],model_target_whitelist=['model_perception'])
    assert 'reference_answer' not in model_view(r,'perception_sft')['input']
    r['model_perception']='radius_3_0'
    with pytest.raises(ValueError):model_view(r,'perception_sft')
