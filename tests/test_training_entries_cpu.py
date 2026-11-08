import torch
from transformers import GPT2Config,GPT2LMHeadModel,Trainer,TrainingArguments
from src.training.approved_hf import CompletionCollator,check_math

def tiny():
    return GPT2LMHeadModel(GPT2Config(vocab_size=24,n_positions=32,n_embd=16,n_layer=1,n_head=2,resid_pdrop=0,embd_pdrop=0,attn_pdrop=0))

def test_real_hf_sft_optimizer_checkpoint_resume(tmp_path):
    model=tiny();before=model.transformer.wte.weight.detach().clone()
    data=[{'input_ids':[1,2,3,4,5],'labels':[-100,-100,3,4,5]}]*2
    def trainer(steps):
        return Trainer(model=model,args=TrainingArguments(output_dir=str(tmp_path),use_cpu=True,max_steps=steps,per_device_train_batch_size=1,learning_rate=.01,save_steps=1,report_to='none',disable_tqdm=True),train_dataset=data,data_collator=CompletionCollator(0))
    t=trainer(1);t.train();assert not torch.equal(before,model.transformer.wte.weight)
    assert (tmp_path/'checkpoint-1'/'optimizer.pt').exists()
    t=trainer(2);t.train(resume_from_checkpoint=str(tmp_path/'checkpoint-1'));assert t.state.global_step==2

def test_bounded_real_math_reward():
    assert check_math(r'Here is the result: \boxed{2}', '2')['correct']
    assert not check_math(r'\boxed{3}', '2')['correct']

def test_actual_trl_group_policy_cpu(tmp_path):
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from transformers import PreTrainedTokenizerFast
    from datasets import Dataset
    from trl import GRPOConfig,GRPOTrainer
    backend=Tokenizer(WordLevel({'[UNK]':0,'[PAD]':1,'[EOS]':2,'question':3},unk_token='[UNK]'))
    tok=PreTrainedTokenizerFast(tokenizer_object=backend,unk_token='[UNK]',pad_token='[PAD]',eos_token='[EOS]')
    tok.chat_template="{% for message in messages %}{{ message['content'] }}{% endfor %}"
    for algorithm in ['grpo','dr_grpo']:
        model=tiny();model.config.eos_token_id=2;model.config.pad_token_id=1
        model.generation_config.eos_token_id=2;model.generation_config.pad_token_id=1
        local=tmp_path/(algorithm+'_base');model.save_pretrained(local);model.config._name_or_path=str(local)
        def reward(completions,**kwargs):return [float(i%2) for i in range(len(completions))]
        args=GRPOConfig(output_dir=str(tmp_path/algorithm),use_cpu=True,bf16=False,fp16=False,max_steps=1,per_device_train_batch_size=2,gradient_accumulation_steps=1,num_generations=2,generation_batch_size=2,max_completion_length=4,beta=.04,loss_type=algorithm,scale_rewards='group' if algorithm=='grpo' else 'none',report_to='none',save_strategy='no',disable_tqdm=True,use_vllm=False,gradient_checkpointing=False)
        trainer=GRPOTrainer(model=model,args=args,train_dataset=Dataset.from_list([{'prompt':'question'}]*2),processing_class=tok,reward_funcs=reward)
        trainer.train();assert trainer.state.global_step==1
        assert all(torch.isfinite(p).all() for p in model.parameters())
