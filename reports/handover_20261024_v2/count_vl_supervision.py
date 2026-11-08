"""Actual assistant-label token counts using a cached VL processor, no model load."""
import argparse,json
from pathlib import Path
from src.data.approved_training_inputs import load_approved
from .project3_v2 import PairedVisualCollator

def main():
    p=argparse.ArgumentParser();p.add_argument('--processor',required=True);p.add_argument('--revision',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    from transformers import AutoProcessor
    processor=AutoProcessor.from_pretrained(a.processor,revision=a.revision,local_files_only=True,max_pixels=802816)
    processor.tokenizer.padding_side='right';processor.tokenizer.pad_token=processor.tokenizer.pad_token or processor.tokenizer.eos_token
    rows=load_approved('data/portable_release/manifest.json','project3_train_fact_pruned.jsonl')
    result={}
    for mode in ['answer_v1','perception_answer_v2']:
        collator=PairedVisualCollator(processor,3800,mode);values=[]
        for r in rows:
            batch=collator([r]);values.append({'sample_id':r['sample_id'],'supervised_tokens':int((batch['labels']!=-100).sum()),'expanded_sequence_tokens':int(batch['attention_mask'].sum())})
        result[mode]={'total_supervised_tokens':sum(x['supervised_tokens'] for x in values),'per_sample':values}
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':main()
