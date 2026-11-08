"""Local score probes; every completion here is constructed, not a model output."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.data.perception_v4 import scoped_score,token_key,conflicts_with_certified_constant
from src.training.approved_hf import check_math
from src.data.project3_perception_v2 import ORDER
from src.evaluation.geometry_perception_parser import canonicalize

def main():
    release=ROOT/'data/portable_release'
    allrows=[json.loads(l) for name in ['project3_train_fact_pruned.jsonl','project3_validation_fact_pruned.jsonl'] for l in (release/name).read_text(encoding='utf8').splitlines() if l.strip()]
    r=allrows[0];positive=r['certified_positive_tokens']
    output=r'<perception>Length(A,C)=1; Length(C,D)=6; Length(A,C)=2; Parallel((A,B),(D,E))</perception>\boxed{4}'
    probes={
      'constructed_trace':{'sample_id':r['sample_id'],'completion':output,'origin':'HAND-CONSTRUCTED FROM KNOWN LABELS. NOT A MODEL PREDICTION.','perception':scoped_score(output,positive,[]),'answer':check_math(output,r['reference_answer'])},
      'empty_output':scoped_score('<perception></perception>',positive,[]),
      'no_trusted_gold':scoped_score('<perception></perception>',[],[]),
      'wrong_arity_not_rejected':scoped_score('<perception>Angle(A,B)=60 deg</perception>',positive,[]),
      'unknown_negative_length_not_rejected':scoped_score('<perception>Length(X,Y)=-3</perception>',positive,[]),
      'legacy_parser_example':canonicalize('Perpendicular(BA,DC); Length(B,A)=3; Angle(C,B,A)=60deg'),
      'current_release':{},
      'extended_order':ORDER,
    }
    checks={'rows':len(allrows),'target_equals_tokens':0,'lexical_sorted_tokens':0,'semantic_unique':0,'constant_conflict_rows':[],'bad_parse_rows':[],'model_visible_source_id_rows':[]}
    for row in allrows:
        p=row['certified_positive_tokens']
        checks['target_equals_tokens']+=row['model_perception']=='<perception>'+'; '.join(p)+'</perception>'
        checks['lexical_sorted_tokens']+=p==sorted(set(p))
        try:checks['semantic_unique']+=len({token_key(t) for t in p})==len(p)
        except Exception as e:checks['bad_parse_rows'].append({'sample_id':row['sample_id'],'error':str(e)})
        if any(conflicts_with_certified_constant(t,[x for x in p if x!=t]) for t in p):checks['constant_conflict_rows'].append(row['sample_id'])
        if any(x in row['problem']+row['model_perception'] for x in ['radius_','source_radius_id']):checks['model_visible_source_id_rows'].append(row['sample_id'])
    probes['current_release']=checks
    (Path(__file__).parent/'reward_probes.json').write_text(json.dumps(probes,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(probes,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
