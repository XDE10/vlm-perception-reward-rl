"""Tiny or local-only real structure probe, no optimizer or GPU execution."""
import argparse,json
from pathlib import Path
from .project3_v2 import parameter_identity,attach_language_lora

def main():
    p=argparse.ArgumentParser();p.add_argument('--tiny',action='store_true');p.add_argument('--model');p.add_argument('--revision');p.add_argument('--output',required=True);a=p.parse_args()
    import torch
    if a.tiny:
        class Tiny(torch.nn.Module):
            def __init__(self):
                super().__init__();self.visual=torch.nn.ModuleDict({'encoder':torch.nn.Linear(2,2),'merger':torch.nn.Linear(2,2)});self.language_lora=torch.nn.Linear(2,2)
        model=Tiny()
        for v in model.visual.parameters():v.requires_grad=False
        context='tiny_structure_only; formal_VL_未验证'
    else:
        if not a.model or not a.revision or a.revision=='main':raise ValueError('Pinned local model required')
        from transformers import AutoModelForVision2Seq
        model=AutoModelForVision2Seq.from_pretrained(a.model,revision=a.revision,local_files_only=True,torch_dtype=torch.bfloat16)
        model,_=attach_language_lora(model);context='local_structure_only; no forward/GPU'
    result=parameter_identity(model);result['context']=context
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(result['context'])

if __name__=='__main__':main()
