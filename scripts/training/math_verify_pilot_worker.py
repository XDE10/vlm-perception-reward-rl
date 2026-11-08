"""Isolated bounded Math-Verify worker; stdout is JSON, never an API credential."""
import json
import re
import sys
from math_verify import parse, verify, LatexExtractionConfig


def boxes(text):
    values=[]
    for match in re.finditer(r'\\boxed\s*\{',text):
        start=match.end();depth=1;i=start
        while i<len(text) and depth:
            depth+=(text[i]=='{')-(text[i]=='}');i+=1
        if depth:raise ValueError('unclosed_box')
        values.append(text[start:i-1])
    return values


def run():
    data=json.load(sys.stdin)
    try:
        ref=str(data['reference']); values=boxes(data['output'])
        if not values:raise ValueError('missing_box')
        gold=parse('\\boxed{'+ref+'}',extraction_config=[LatexExtractionConfig()],extraction_mode='first_match',parsing_timeout=0)
        preds=[parse('\\boxed{'+v+'}',extraction_config=[LatexExtractionConfig()],extraction_mode='first_match',parsing_timeout=0) for v in values]
        if not gold or not any(not isinstance(x,str) for x in gold):raise ValueError('unparsed_reference')
        if any(not p or not any(not isinstance(x,str) for x in p) for p in preds):raise ValueError('unparsed_prediction')
        correct=all(verify(gold,p,timeout_seconds=0) for p in preds)
        print(json.dumps({'correct':correct,'status':'equivalent' if correct else 'mismatch','boxes':values,'parsed_reference':str(gold[0]),'version':'math-verify-0.9.0'}))
    except Exception as e:print(json.dumps({'correct':False,'status':str(e),'error_type':type(e).__name__}))

if __name__=='__main__':run()
