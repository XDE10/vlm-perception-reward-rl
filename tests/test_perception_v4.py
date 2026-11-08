import pytest
from src.data.perception_v4 import parse_review,prune,scoped_score,token_key
from src.training.perception_reward_v4 import validate_reward_rows
import json

def test_unknown_mask_not_false_positive_and_real_negative_penalty():
    gold=['Length(A,B)=3','Angle(A,B,C)=60 deg'];negative=['Length(A,B)=4']
    good=scoped_score('<perception>Length(B,A)=3; Length(X,Y)=8</perception>',gold,negative)
    assert good['precision']==1 and good['recall']==.5 and good['masked_predictions']==1
    bad=scoped_score('<perception>Length(A,B)=3; Length(A,B)=4</perception>',gold,negative)
    assert bad['precision']==.5 and bad['certified_false_positive']==1
    duplicate=scoped_score('<perception>Length(A,B)=3; Length(B,A)=3</perception>',gold,[])
    assert duplicate['true_positive']==1

def test_vertex_units_and_expression_semantics():
    assert token_key('Angle(A,B,C)=60 deg')==token_key('Angle(C,B,A)=60 deg')
    assert token_key('Angle(A,B,C)=60 deg')!=token_key('Angle(B,A,C)=60 deg')
    assert token_key('Length(A,B)=2*x+1')==token_key('Length(B,A)=1+2*x')
    assert token_key('ArcLength(minorArc(A,B))=3')!=token_key('ArcMeasure(minorArc(A,B))=3 deg')
    with pytest.raises(ValueError):token_key('__import__(A)')

def test_fact_pruning_does_not_inherit_unprinted_label():
    facts=[{'relation':'Length','entities':['A','B'],'value':'3','unit':''},{'relation':'Length','entities':['X','Y'],'value':'5','unit':''}]
    review={'valid':True,'task_status':'pass','task_issues':[],'visible_labels':['A','B'],'circle_count':0,'facts':[{'index':0,'status':'certified','evidence':'printed AB3'},{'index':1,'status':'certified','evidence':'untrusted XY5'}]}
    out=prune({'original_id':'other','canonical_candidates_with_audit_provenance':facts},review)
    assert out['accepted'] and out['positive_tokens']==['Length(A,B)=3'] and len(out['masked'])==1
    review['task_status']='isolate';assert not prune({'original_id':'other','canonical_candidates_with_audit_provenance':facts},review)['accepted']

def test_schema_partition_and_scope_fail_closed():
    d={'task_status':'pass','task_issues':[],'visible_labels':['A'],'circle_count':0,'facts':[{'index':0,'status':'certified','evidence':'A printed'}]}
    assert parse_review(json.dumps(d),1,'stop')['valid']
    assert not parse_review(json.dumps(d),2,'stop')['valid']
    assert not parse_review(json.dumps(d),1,'length')['valid']
    with pytest.raises(ValueError):validate_reward_rows([{'split':'validation'}])
    assert scoped_score('<perception>broken</perception>',['Length(A,B)=3'],[])['reward']==0
    d['type']='json_object';assert parse_review(json.dumps(d),1,'stop')['normalization']
    d['type']='other';assert not parse_review(json.dumps(d),1,'stop')['valid']

def test_nested_roles_and_batch_alignment():
    from src.data.perception_v4 import perception_reward
    assert token_key('Parallel((A,B),(C,D))')==token_key('Parallel((D,C),(B,A))')
    assert token_key('PointLiesOnLine(A,(B,C))')==token_key('PointLiesOnLine(A,(C,B))')
    assert token_key('CongruentAngle((A,B,C),(D,E,F))')==token_key('CongruentAngle((F,E,D),(C,B,A))')
    with pytest.raises(ValueError):perception_reward(['anything'],[],[])
    metrics={}
    score=perception_reward(['<perception>Length(A,B)=3</perception>'],[['Length(A,B)=3']],[[]],log_metric=lambda k,v:metrics.update({k:v}))
    assert score==[1.] and metrics['perception_v4/recall']==1 and all(isinstance(v,float) for v in metrics.values())

def test_prose_entailment_counterexamples_are_masked():
    from src.data.perception_text_guards import entailed_by_prose
    p='The diagonals of rhombus FGHJ intersect at K. Find angle KHJ.'
    assert entailed_by_prose(p,{'relation':'PointLiesOnLine','entities':['K',['F','H']]})
    assert entailed_by_prose(p,{'relation':'Perpendicular','entities':[['F','H'],['G','J']]})
    assert entailed_by_prose(r'In $\odot P, m\widehat{E N}=66$',{'relation':'PointLiesOnCircle','entities':['E',{'center':'P','source_radius_id':'hidden'}]})
    assert not entailed_by_prose(r'In $\odot P, m\widehat{E N}=66$',{'relation':'PointLiesOnCircle','entities':['G',{'center':'P','source_radius_id':'hidden'}]})
    assert entailed_by_prose('WXYZ is a square. If WT=3, find angle WTZ.',{'relation':'Perpendicular','entities':[['W','X'],['W','Z']]})

def test_only_certified_constant_slots_can_prove_false_predictions():
    assert scoped_score('<perception>Length(A,B)=4</perception>',['Length(A,B)=3'],[])['certified_false_positive']==1
    result=scoped_score('<perception>Length(X,Y)=4</perception>',['Length(A,B)=3'],['Length(X,Y)=4'])
    assert result['certified_false_positive']==0 and result['masked_predictions']==1
    assert scoped_score('<perception>Length(A,B)=x+4</perception>',['Length(A,B)=2*x+1'],[])['masked_predictions']==1
