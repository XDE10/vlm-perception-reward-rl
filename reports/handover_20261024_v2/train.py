"""New paired HF/TRL entry, legacy trainers/data untouched. GPU execution unverified."""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
from importlib.metadata import version
from .project3_v2 import (prompt, PairedVisualCollator, LoggedRewards, parameter_identity,
                         summarize_rollouts, supervised_view, PROTOCOL, attach_language_lora, rl_view)
from src.data.approved_training_inputs import load_approved
from src.training.perception_reward_v4 import validate_reward_rows


def run(config_path):
    c = json.loads(Path(config_path).read_text(encoding='utf8'))
    if c['protocol'] != PROTOCOL or not c['vision']: raise ValueError('Paired protocol required')
    if c['initial_state'] != 'V0': raise ValueError('Formal paired runs require V0')
    rows = load_approved(c['data_manifest'], c['data_file'])
    import torch
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1: raise RuntimeError('One visible CUDA GPU required; 未验证')
    from transformers import AutoProcessor, AutoModelForVision2Seq, Trainer, TrainingArguments, TrainerCallback, set_seed
    from datasets import Dataset
    from trl import GRPOConfig, GRPOTrainer
    set_seed(c['seed'])
    name = ('lambda_' + str(c['perception_reward_weight']).replace('.', 'p')) if c['stage'] == 'rl' else c['supervision']
    out = Path(c['output_root']) / name
    out.mkdir(parents=True, exist_ok=True)
    if list(out.glob('checkpoint-*')) and not c.get('resume_from_checkpoint'): raise ValueError('Explicit resume or new output required')
    def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    identity = {'protocol': PROTOCOL, 'config': {k:v for k,v in c.items() if k != 'resume_from_checkpoint'},
        'versions': {k:version(k) for k in ['torch','transformers','trl','peft','datasets']},
        'data_sha256': sha(Path(c['data_manifest']).parent / c['data_file']), 'manifest_sha256':sha(c['data_manifest']),
        'source_sha256': {p.name: sha(p) for p in Path(__file__).parent.glob('*.py')},
        'VL_GPU_acceptance': '未验证'}
    ip = out/'run_identity.json'
    if ip.exists():
        prior = json.loads(ip.read_text(encoding='utf8'))
        for k,v in identity.items():
            if prior.get(k) != v: raise ValueError('Run identity mismatch: '+k)
    ip.write_text(json.dumps(identity, ensure_ascii=False, indent=2), encoding='utf8')
    processor = AutoProcessor.from_pretrained(c['model'], revision=c['model_revision'], max_pixels=c['max_pixels'], local_files_only=True)
    tok = processor.tokenizer; tok.pad_token = tok.pad_token or tok.eos_token; tok.padding_side = 'right' if c['stage']=='sft' else 'left'
    model = AutoModelForVision2Seq.from_pretrained(c['model'], revision=c['model_revision'], torch_dtype=torch.bfloat16, attn_implementation='sdpa', local_files_only=True).to('cuda')
    model.config.use_cache = False
    # Exact module paths select language-side LoRA, excluding vision/merger.
    model,names=attach_language_lora(model,c['lora_r'],c['lora_alpha'])
    identity['parameters'] = parameter_identity(model, out/'requires_grad.json')
    identity['lora_exact_modules'] = names
    ip.write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf8')
    resume = c.get('resume_from_checkpoint')
    if resume and json.loads((Path(resume)/'run_identity.json').read_text(encoding='utf8')) != identity: raise ValueError('Checkpoint identity mismatch')
    class Identity(TrainerCallback):
        def on_save(self,args,state,control,**kwargs):
            (Path(args.output_dir)/f'checkpoint-{state.global_step}'/'run_identity.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf8')
    common = dict(output_dir=str(out), max_steps=c['max_steps'], learning_rate=c['learning_rate'], per_device_train_batch_size=c['batch_size'],
        gradient_accumulation_steps=c['gradient_accumulation_steps'], bf16=True, gradient_checkpointing=True,
        gradient_checkpointing_kwargs={'use_reentrant':False}, save_steps=c['save_steps'], logging_steps=1,
        report_to='none', remove_unused_columns=False, seed=c['seed'], data_seed=c['seed'], dataloader_num_workers=0)
    if c['stage']=='sft':
        for r in rows: supervised_view(r,c['supervision'])
        trainer = Trainer(model=model,args=TrainingArguments(**common),train_dataset=Dataset.from_list(rows),
            data_collator=PairedVisualCollator(processor,c['max_length'],c['supervision']),processing_class=processor,callbacks=[Identity()])
    else:
        validate_reward_rows(rows)
        from PIL import Image
        data = []
        # Preflight actual VL prompts, fail rather than silently truncate.
        for r in rows:
            image = Image.open(r['image_path']).convert('RGB')
            from .project3_v2 import messages
            text = processor.apply_chat_template(messages(r),tokenize=False,add_generation_prompt=True)
            encoded = processor(text=[text],images=[image],return_tensors='pt')
            if encoded['input_ids'].shape[1] > c['max_prompt_length']: raise ValueError('VL prompt budget exceeded')
            item=rl_view(r,c);item.pop('image_path');item['image']=image;data.append(item)
        options = dict(**common,num_generations=c['num_generations'],generation_batch_size=c['generation_batch_size'],
            max_completion_length=c['max_new_tokens'], beta=c['beta'],loss_type='grpo',scale_rewards='group',
            mask_truncated_completions=True,disable_dropout=True,use_vllm=False,use_liger_kernel=False,
            sync_ref_model=False,reward_weights=[1.,c['format_reward_weight'],c['perception_reward_weight']])
        if 'max_prompt_length' in inspect.signature(GRPOConfig).parameters: options['max_prompt_length']=c['max_prompt_length']
        rewards = LoggedRewards(out/'rollouts.jsonl',c['perception_reward_weight'],c['format_reward_weight'])
        trainer = GRPOTrainer(model=model,args=GRPOConfig(**options),train_dataset=Dataset.from_list(data),processing_class=processor,
            reward_funcs=[rewards.answer_reward,rewards.format_reward,rewards.perception_reward],callbacks=[Identity()])
    trainer.train(resume_from_checkpoint=resume)
    trainer.save_model(out/'final'); processor.save_pretrained(out/'final')
    if (out/'rollouts.jsonl').exists():
        rs=[json.loads(x) for x in (out/'rollouts.jsonl').read_text(encoding='utf8').splitlines()]
        (out/'monitoring.json').write_text(json.dumps(summarize_rollouts(rs),ensure_ascii=False,indent=2),encoding='utf8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();run(a.config)
