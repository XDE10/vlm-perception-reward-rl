"""Future GPU acceptance ONLY; not run in handover. Never downloads weights.

Uses the production visual collator. No optimizer step and no training export.
"""
import argparse,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))

def main():
    import os
    os.chdir(ROOT)
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    import torch
    from transformers import AutoProcessor,AutoModelForVision2Seq
    from peft import LoraConfig,get_peft_model
    from src.training.approved_hf import VisualCompletionCollator
    from src.data.approved_training_inputs import load_approved
    c=json.loads(Path(a.config).read_text(encoding='utf8'))
    if c['stage']!='sft' or not c.get('vision'):raise ValueError('Use perception SFT config')
    if not torch.cuda.is_available() or torch.cuda.device_count()!=1:raise RuntimeError('One visible CUDA GPU required')
    rows=load_approved(c['data_manifest'],c['data_file'])
    processor=AutoProcessor.from_pretrained(c['model'],revision=c['model_revision'],max_pixels=c.get('max_pixels',802816),local_files_only=True)
    tok=processor.tokenizer;tok.pad_token=tok.pad_token or tok.eos_token;tok.padding_side='right'
    collator=VisualCompletionCollator(processor,10**9)
    lengths=[]
    # The longest text string need not be the longest multimodal sequence.
    for r in rows:
        b=collator([r]);lengths.append({'sample_id':r['sample_id'],'tokens':int(b['attention_mask'].sum()),'supervised_tokens':int((b['labels']!=-100).sum()),'image_grid_thw':b['image_grid_thw'].tolist() if 'image_grid_thw' in b else None})
    ranked=sorted(lengths,key=lambda x:x['tokens'],reverse=True)
    (out/'all_processor_lengths.json').write_text(json.dumps(ranked,indent=2),encoding='utf8')
    if ranked[0]['tokens']>c['max_length']:raise ValueError('Longest sample exceeds SFT budget; preserve failed lengths, no silent truncation')
    r=next(r for r in rows if r['sample_id']==ranked[0]['sample_id'])
    b=VisualCompletionCollator(processor,c['max_length'])([r])
    if (b['labels']!=-100).sum()==0:raise ValueError('No assistant supervision')
    for name in ['image_token_id','vision_start_token_id','vision_end_token_id']:
        token=tok.convert_tokens_to_ids({'image_token_id':'<|image_pad|>','vision_start_token_id':'<|vision_start|>','vision_end_token_id':'<|vision_end|>'}[name])
        if token is not None and token!=tok.unk_token_id and torch.any(b['labels'][b['input_ids']==token]!=-100):raise ValueError('Visual tokens supervised')
    pad=collator([r,rows[0]])
    if torch.any(pad['labels'][pad['attention_mask']==0]!=-100):raise ValueError('Padding supervised')
    model=AutoModelForVision2Seq.from_pretrained(c['model'],revision=c['model_revision'],torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).to('cuda')
    model.config.use_cache=False
    model=get_peft_model(model,LoraConfig(r=c.get('lora_r',16),lora_alpha=c.get('lora_alpha',32),lora_dropout=0,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],task_type='CAUSAL_LM'))
    names=[{'name':n,'parameters':v.numel()} for n,v in model.named_parameters() if v.requires_grad]
    (out/'trainable_parameters.json').write_text(json.dumps(names,indent=2),encoding='utf8')
    if any('visual' in x['name'].lower() or 'merger' in x['name'].lower() for x in names):raise ValueError('Visual/merger trainable: review against language-only LoRA design')
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.enable_input_require_grads();model.train()
    batch={k:(v.to('cuda') if hasattr(v,'to') else v) for k,v in b.items()}
    torch.cuda.reset_peak_memory_stats();loss=model(**batch).loss
    if not torch.isfinite(loss):raise ValueError('Nonfinite loss')
    loss.backward();grads=[v.grad for v in model.parameters() if v.requires_grad and v.grad is not None]
    if not grads or not all(torch.isfinite(g).all() for g in grads) or not any(torch.any(g!=0) for g in grads):raise ValueError('Nonfinite or zero gradients')
    result={'status':'pass','config_sha256':hashlib.sha256(Path(a.config).read_bytes()).hexdigest(),'model':c['model'],'revision':c['model_revision'],'sample':ranked[0],'loss':float(loss.detach()),'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'trainable_parameters':sum(x['parameters'] for x in names),'grad_parameters':len(grads),'optimizer_step':False,'note':'Forward/backward acceptance only; not an accuracy, rollout or resume result.'}
    (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))

if __name__=='__main__':main()
