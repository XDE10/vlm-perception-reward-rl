"""Conservative typed admission supplement, separate from frozen pilot verifier.

Math-Verify may consider different inequalities equivalent under its relation
heuristics. Relational answers are therefore isolated for task-aware review.
Multiple distinct boxes may encode a correct set, but are not guessed here.
"""
import json
import re
import sys
from math_verify import parse,verify,LatexExtractionConfig
from scripts.training.math_verify_pilot_worker import boxes


def relation_answer(s):
    return bool(re.search(r'[<>≤≥≠=]|\\(?:leq?|geq?|neq?|lt|gt)\b',s))


def check(data):
    values=boxes(data['output']);reference=str(data['reference'])
    if not values:raise ValueError('missing_box')
    if relation_answer(reference) or any(relation_answer(v) for v in values):
        return {'correct':False,'status':'relational_answer_requires_task_aware_manual_review',
            'classification':'unsupported_for_automatic_admission_not_proven_wrong',
            'reason':'Do not approve inequalities/equations solely from generic expression equivalence.'}
    if len(set(re.sub(r'\s+','',v) for v in values))>1:
        return {'correct':False,'status':'multiple_distinct_boxes_require_manual_collection_review',
            'classification':'may_be_valid_set_or_tuple_not_proven_wrong'}
    config=[LatexExtractionConfig()]
    gold=parse(r'\boxed{'+reference+'}',extraction_config=config,extraction_mode='first_match',parsing_timeout=0)
    preds=[parse(r'\boxed{'+v+'}',extraction_config=config,extraction_mode='first_match',parsing_timeout=0) for v in values]
    if not gold or not any(not isinstance(x,str) for x in gold):raise ValueError('unparsed_reference')
    if any(not p or not any(not isinstance(x,str) for x in p) for p in preds):raise ValueError('unparsed_prediction')
    correct=all(verify(gold,p,timeout_seconds=0) for p in preds)
    return {'correct':correct,'status':'equivalent' if correct else 'mismatch',
        'version':'math-verify-0.9.0+conservative-type-gate-v1',
        'process_correctness':'not_certified'}


if __name__=='__main__':
    try:result=check(json.load(sys.stdin))
    except Exception as e:result={'correct':False,'status':str(e),'error_type':type(e).__name__}
    print(json.dumps(result))
