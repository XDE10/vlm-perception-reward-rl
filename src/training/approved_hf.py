"""Manifest-gated HF SFT/GRPO entry points; GPU acceptance is separate."""
import argparse,hashlib,json,subprocess,sys
from importlib.metadata import version
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from src.data.approved_training_inputs import load_approved,model_view

ROOT=Path(__file__).resolve().parents[2]


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def approved_config(path):
    c=read(path);rows=load_approved(c['data_manifest'],c['data_file'])
    if not c.get('model_revision') or c['model_revision']=='main':raise ValueError('Pin model revision or explicit local snapshot identity')
    if c['stage']=='rl' and c['initial_state']=='sft':
        merged=Path(c['model'])/'merged_sft_identity.json'
        if not merged.exists():raise ValueError('SFT->RL requires merged SFT base + fresh RL LoRA; disabling a trained SFT adapter would reference the wrong base')
        checks=read(merged.parent/'weight_manifest.json')
        if not checks or any(sha(merged.parent/p)!=h for p,h in checks.items()):raise ValueError('Merged SFT weight identity changed')
    for r in rows:
        if c['stage']=='sft':model_view(r,'perception_sft' if c.get('vision') else 'math_sft')
        elif 'reference_answer' not in r:raise ValueError('RL requires private reward answer, never copied into prompt')
    stable={k:v for k,v in c.items() if k!='resume_from_checkpoint'}
    ident={'config':stable,'versions':{k:version(k) for k in ['torch','transformers','trl','peft','datasets']},
        'manifest_sha256':sha(c['data_manifest']),'data_sha256':sha(Path(c['data_manifest']).parent/c['data_file'])}
    return c,rows,ident


class CompletionCollator:
    def __init__(self,pad):self.pad=pad
    def __call__(self,rows):
        import torch
        n=max(len(r['input_ids']) for r in rows)
        return {'input_ids':torch.tensor([r['input_ids']+[self.pad]*(n-len(r['input_ids'])) for r in rows]),
            'attention_mask':torch.tensor([[1]*len(r['input_ids'])+[0]*(n-len(r['input_ids'])) for r in rows]),
            'labels':torch.tensor([r['labels']+[-100]*(n-len(r['input_ids'])) for r in rows])}


def encode_sft(rows,tokenizer,max_length):
    result=[]
    for row in rows:
        v=model_view(row,'math_sft');messages=[{'role':'system','content':r'Please reason step by step, and put your final answer within \boxed{}.'},{'role':'user','content':v['input']['problem']}]
        prefix=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True)
        full=tokenizer.apply_chat_template(messages+[{'role':'assistant','content':v['target']}],tokenize=True,add_generation_prompt=False)
        if full[:len(prefix)]!=prefix or len(full)>max_length or len(full)<=len(prefix):raise ValueError('SFT prefix/length violation; do not truncate')
        result.append({'input_ids':full,'labels':[-100]*len(prefix)+full[len(prefix):]})
    return result


class VisualCompletionCollator:
    def __init__(self,processor,max_length):self.processor=processor;self.max_length=max_length
    def __call__(self,rows):
        import torch
        from PIL import Image
        images=[];texts=[];prefixes=[]
        for row in rows:
            v=model_view(row,'perception_sft');image=Image.open(v['input']['image_path']).convert('RGB');images.append(image)
            problem=v['input']['problem'].removeprefix('<image>').strip()
            messages=[{'role':'user','content':[{'type':'image'},{'type':'text','text':problem}]}]
            prefixes.append(self.processor.apply_chat_template(messages,tokenize=False,add_generation_prompt=True))
            texts.append(self.processor.apply_chat_template(messages+[{'role':'assistant','content':v['target']}],tokenize=False,add_generation_prompt=False))
        batch=self.processor(text=texts,images=images,padding=True,return_tensors='pt')
        labels=batch['input_ids'].clone();labels[batch['attention_mask']==0]=-100
        for i,(image,prefix) in enumerate(zip(images,prefixes)):
            p=self.processor(text=[prefix],images=[image],return_tensors='pt')['input_ids'][0]
            n=int(batch['attention_mask'][i].sum())
            if n>self.max_length or not torch.equal(batch['input_ids'][i,:len(p)],p):raise ValueError('VL prefix/budget violation; do not truncate image/question')
            labels[i,:len(p)]=-100
        batch['labels']=labels;return batch


def check_math(text,answer):
    try:
        p=subprocess.run([sys.executable,'-m','scripts.training.math_verify_v3_strict_worker'],cwd=ROOT,input=json.dumps({'output':text,'reference':str(answer)}),text=True,encoding='utf-8',capture_output=True,timeout=20)
        return read_json_last(p.stdout)
    except Exception as e:return {'correct':False,'status':'verifier_error','error_type':type(e).__name__}


def read_json_last(text):return json.loads(text.strip().splitlines()[-1])


def math_reward(completions,reference_answer,**kwargs):
    texts=[c[-1]['content'] if isinstance(c,list) else c for c in completions]
    with ThreadPoolExecutor(max_workers=4) as pool:return [float(r.get('correct',False)) for r in pool.map(lambda p:check_math(*p),zip(texts,reference_answer))]


def run(config_path):
    c,rows,identity=approved_config(config_path)
    import torch
    if not torch.cuda.is_available():raise RuntimeError('Formal run requires CUDA; use CPU small-tensor smoke separately')
    if torch.cuda.device_count()!=1:raise RuntimeError('Initial configuration supports exactly one visible GPU')
    from datasets import Dataset
    from transformers import AutoModelForCausalLM,AutoModelForVision2Seq,AutoTokenizer,AutoProcessor,Trainer,TrainingArguments,TrainerCallback,set_seed
    from peft import LoraConfig,get_peft_model
    from trl import GRPOConfig,GRPOTrainer
    set_seed(c['seed']);out=Path(c['output_dir']);out.mkdir(parents=True,exist_ok=True)
    if (out/'run_identity.json').exists() and read(out/'run_identity.json')!=identity:raise ValueError('Run/data/model identity changed; choose new output')
    (out/'run_identity.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf-8')
    class IdentityCallback(TrainerCallback):
        def on_save(self,args,state,control,**kwargs):
            p=Path(args.output_dir)/f'checkpoint-{state.global_step}'/'run_identity.json';p.write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf-8')
    resume=c.get('resume_from_checkpoint')
    if not resume and list(out.glob('checkpoint-*')):raise ValueError('Existing checkpoints require explicit resume or a new output directory')
    if resume and read(Path(resume)/'run_identity.json')!=identity:raise ValueError('Checkpoint identity mismatch')
    vision=c.get('vision',False)
    loader=AutoModelForVision2Seq if vision else AutoModelForCausalLM
    model=loader.from_pretrained(c['model'],revision=c['model_revision'],torch_dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda')
    model.config.use_cache=False
    processor=(AutoProcessor.from_pretrained(c['model'],revision=c['model_revision'],max_pixels=c.get('max_pixels',802816)) if vision else AutoTokenizer.from_pretrained(c['tokenizer_path'],local_files_only=True))
    tok=processor.tokenizer if vision else processor;tok.pad_token=tok.pad_token or tok.eos_token;tok.padding_side='left' if c['stage']=='rl' else 'right'
    lora=LoraConfig(r=c.get('lora_r',16),lora_alpha=c.get('lora_alpha',32),lora_dropout=0,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],task_type='CAUSAL_LM')
    common=dict(output_dir=str(out),max_steps=c['max_steps'],learning_rate=c['learning_rate'],per_device_train_batch_size=c.get('batch_size',1),
        gradient_accumulation_steps=c.get('gradient_accumulation_steps',8),bf16=True,fp16=False,gradient_checkpointing=True,
        gradient_checkpointing_kwargs={'use_reentrant':False},report_to='none',logging_steps=1,save_steps=c.get('save_steps',20),
        save_only_model=False,seed=c['seed'],data_seed=c['seed'],dataloader_num_workers=0,remove_unused_columns=False)
    if c['stage']=='sft':
        model=get_peft_model(model,lora)
        if vision:
            fields=['problem','image_path','model_perception','image_sha256','training_approved','model_input_whitelist','model_target_whitelist']
            data=Dataset.from_list([{k:r[k] for k in fields} for r in rows]);collator=VisualCompletionCollator(processor,c['max_length'])
        else:data=Dataset.from_list(encode_sft(rows,tok,c['max_length']));collator=CompletionCollator(tok.pad_token_id)
        trainer=Trainer(model=model,args=TrainingArguments(**common),train_dataset=data,data_collator=collator,processing_class=processor,callbacks=[IdentityCallback()])
    else:
        sparse_v4=vision and c.get('reward_mode')=='sparse_certified_v4'
        if vision and c.get('reward_mode') not in {'answer_only_baseline','sparse_certified_v4'}:raise ValueError('Explicit answer-only or approved sparse V4 reward required; no full-image reward claim')
        if sparse_v4:
            from src.training.perception_reward_v4 import validate_reward_rows
            validate_reward_rows(rows)
        data=[]
        for r in rows:
            item={'prompt':[{'role':'system','content':r'Please reason step by step, and put your final answer within \boxed{}.'},{'role':'user','content':r['problem'].removeprefix('<image>').strip()}],
                'reference_answer':r['reference_answer']}
            if vision:
                from PIL import Image
                item['image']=Image.open(r['image_path']).convert('RGB')
                if sparse_v4:
                    item['prompt'][-1]['content']+=' First output <perception>semicolon-separated typed visual facts, e.g. Length(A,B)=3; Angle(A,B,C)=60 deg; Parallel((A,B),(C,D))</perception>, then solve with a final boxed answer. Use actual diagram labels and only observed facts.'
                    item['certified_positive_tokens']=r['certified_positive_tokens'];item['certified_negative_tokens']=r['certified_negative_tokens']
            data.append(item)
        args=GRPOConfig(**common,num_generations=c.get('num_generations',4),generation_batch_size=c.get('generation_batch_size',4),
            max_completion_length=c['max_new_tokens'],beta=c.get('beta',.04),loss_type=c['algorithm'],
            scale_rewards='group' if c['algorithm']=='grpo' else 'none',mask_truncated_completions=True,disable_dropout=True,
            use_vllm=False,use_liger_kernel=False,sync_ref_model=False)
        rewards=[math_reward]
        if sparse_v4:
            from src.training.perception_reward_v4 import perception_reward
            rewards.append(perception_reward);args.reward_weights=[1.,c.get('perception_reward_weight',.2)]
        trainer=GRPOTrainer(model=model,args=args,train_dataset=Dataset.from_list(data),processing_class=processor,peft_config=lora,reward_funcs=rewards,callbacks=[IdentityCallback()])
    trainer.train(resume_from_checkpoint=resume);trainer.save_model(out/'final');processor.save_pretrained(out/'final')
    if c['stage']=='sft' and c.get('export_merged_base',False):
        merged=trainer.model.merge_and_unload();merged.save_pretrained(out/'merged');processor.save_pretrained(out/'merged')
        (out/'merged'/'merged_sft_identity.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf-8')
        checks={str(p.relative_to(out/'merged')):sha(p) for p in (out/'merged').rglob('*') if p.is_file()}
        (out/'merged'/'weight_manifest.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    return trainer.state


def cli(expected_stage=None,expected_vision=None):
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();c=read(a.config)
    if expected_stage is not None and c['stage']!=expected_stage:raise ValueError('Wrong stage for this entry point')
    if expected_vision is not None and bool(c.get('vision',False))!=expected_vision:raise ValueError('Wrong model modality for this entry point')
    run(a.config)
