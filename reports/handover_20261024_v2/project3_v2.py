"""Versioned paired protocol, read-only views and unconditional local reward logs."""
import hashlib
import json
import re
import threading
from pathlib import Path
from collections import defaultdict
from src.data.approved_training_inputs import model_view
from src.training.approved_hf import check_math
from .strict_geometry import parallel_scores, validate_completion

PROTOCOL = 'paired-perception-answer-v2-20261024'
INSTRUCTION = ('Use the diagram and question. Output exactly <perception>semicolon-separated typed visual facts</perception>'
               '<answer>final answer</answer>. Use actual printed labels, preserve the angle vertex, and use deg for angles. '
               'Examples of syntax only: Length(A,B)=3; Angle(A,B,C)=60 deg; Parallel((A,B),(C,D)). '
               'You may leave perception empty. Do not output a reasoning section.')


def prompt(row):
    return [{'role': 'system', 'content': INSTRUCTION},
            {'role': 'user', 'content': row['problem'].removeprefix('<image>').strip()}]


def rl_view(row, config):
    if config['protocol'] != PROTOCOL or config['initial_state'] != 'V0':raise ValueError('Paired V0 protocol required')
    base=model_view(row,'perception_sft')
    return {'prompt':prompt(row),'image_path':base['input']['image_path'],'sample_id':row['sample_id'],
        'reference_answer':row['reference_answer'],'certified_positive_tokens':row['certified_positive_tokens'],
        'certified_negative_tokens':row['certified_negative_tokens']}


def supervised_view(row, mode):
    # Inherited approval and model-visible fact guards; never mutate the source.
    base = model_view(row, 'perception_sft')
    if mode not in {'answer_v1', 'perception_answer_v2'}: raise ValueError('supervision mode')
    answer = str(row['reference_answer'])
    if re.search(r'</?(?:answer|perception|reasoning)>', answer): raise ValueError('answer tag injection')
    target = (base['target'] if mode == 'perception_answer_v2' else '<perception></perception>')
    return {'input': base['input'], 'target': target + '<answer>' + answer + '</answer>'}


def messages(row, target=None):
    m = prompt(row)
    m[-1]['content'] = [{'type': 'image'}, {'type': 'text', 'text': m[-1]['content']}]
    return m + ([{'role': 'assistant', 'content': target}] if target is not None else [])


class PairedVisualCollator:
    def __init__(self, processor, max_length, mode):
        self.processor, self.max_length, self.mode = processor, max_length, mode

    def __call__(self, rows):
        import torch
        from PIL import Image
        images, texts, prefixes = [], [], []
        for r in rows:
            v = supervised_view(r, self.mode)
            image = Image.open(v['input']['image_path']).convert('RGB'); images.append(image)
            prefixes.append(self.processor.apply_chat_template(messages(r), tokenize=False, add_generation_prompt=True))
            texts.append(self.processor.apply_chat_template(messages(r, v['target']), tokenize=False, add_generation_prompt=False))
        batch = self.processor(text=texts, images=images, padding=True, return_tensors='pt')
        labels = batch['input_ids'].clone(); labels[batch['attention_mask'] == 0] = -100
        for i, (image, prefix) in enumerate(zip(images, prefixes)):
            p = self.processor(text=[prefix], images=[image], return_tensors='pt')['input_ids'][0]
            if int(batch['attention_mask'][i].sum()) > self.max_length or not torch.equal(batch['input_ids'][i, :len(p)], p):
                raise ValueError('VL prefix/length violation; no truncation')
            labels[i, :len(p)] = -100
        batch['labels'] = labels
        return batch


def completion_text(c):
    return c[-1]['content'] if isinstance(c, list) else c


def answer_score(text, reference):
    match = re.fullmatch(r'\s*<perception>.*?</perception>\s*<answer>(.*?)</answer>\s*', text, re.S)
    if not match or not match[1].strip() or '<answer>' in match[1]:
        return {'correct': False, 'status': 'invalid_answer_protocol'}
    # Verify only the explicit answer, never a box buried in perception.
    answer = match[1].strip()
    if '\\boxed' not in answer: answer = r'\boxed{' + answer + '}'
    return check_math(answer, reference)


def format_score(text):
    match = re.fullmatch(r'\s*<perception>.*?</perception>\s*<answer>([^<>]+)</answer>\s*', text, re.S)
    return float(bool(match and match[1].strip() and validate_completion(text)['valid']))


class LoggedRewards:
    """The answer callback writes all components. No TRL metric forwarding needed."""
    def __init__(self, path, perception_weight, format_weight=.05, verifier=answer_score, origin='trainer_rollout'):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.perception_weight, self.format_weight, self.verifier = perception_weight, format_weight, verifier
        self.origin=origin
        self.lock = threading.Lock(); self.calls = 0

    def answer_reward(self, completions, reference_answer, sample_id, certified_positive_tokens, certified_negative_tokens, **kwargs):
        n = len(completions)
        if any(len(x) != n for x in [reference_answer, sample_id, certified_positive_tokens, certified_negative_tokens]):
            raise ValueError('Reward metadata alignment')
        output, records = [], []
        for c, ref, sid, pos, neg in zip(completions, reference_answer, sample_id, certified_positive_tokens, certified_negative_tokens):
            text = completion_text(c); score = parallel_scores(text, pos, neg)
            p = score['frozen_v4']; verification = self.verifier(text, ref)
            answer = float(verification.get('correct', False)); fmt = format_score(text)
            records.append({'sample_id': sid, 'raw_output': text, 'verification': verification,'origin':self.origin,
                'scoring_protocol': PROTOCOL, 'perception_mask': p['mask'],
                'TP': p.get('true_positive', 0), 'FP': p.get('certified_false_positive', 0), 'masked': p['masked_predictions'],
                'P': p['precision'], 'R': p['recall'], 'F1': p['f1'],
                'facts_raw': score['strict_validation']['fact_count'], 'facts_unique': p.get('true_positive', 0) + p.get('certified_false_positive', 0) + p['masked_predictions'],
                'answer_reward': answer, 'format_reward': fmt, 'perception_reward': p['reward'],
                'reward_weights': [1., self.format_weight, self.perception_weight],
                'weighted_reward': answer + self.format_weight * fmt + self.perception_weight * p['reward'],
                'parallel_scores': score})
            output.append(answer)
        with self.lock, self.path.open('a', encoding='utf8') as f:
            for r in records:
                r['callback_batch_index'] = self.calls
                state = kwargs.get('trainer_state'); r['global_step'] = getattr(state, 'global_step', None)
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
            self.calls += 1
        return output

    def format_reward(self, completions, **kwargs):
        return [format_score(completion_text(c)) for c in completions]

    def perception_reward(self, completions, certified_positive_tokens, certified_negative_tokens, **kwargs):
        if not len(completions) == len(certified_positive_tokens) == len(certified_negative_tokens): raise ValueError('reward alignment')
        return [parallel_scores(completion_text(c), p, n)['frozen_v4']['reward'] for c, p, n in zip(completions, certified_positive_tokens, certified_negative_tokens)]


def summarize_rollouts(records):
    n = len(records); bins = defaultdict(list)
    for r in records:
        if not r['perception_mask']: label = 'no_gold_masked'
        elif r['F1'] == 0: label = 'F1=0'
        elif r['F1'] <= .5: label = '0<F1<=0.5'
        elif r['F1'] < 1: label = '0.5<F1<1'
        else: label = 'F1=1'
        bins[label].append(r)
    valid = [r for r in records if r['perception_mask']]
    total = sum(r['facts_unique'] for r in records)
    return {'rollouts': n, 'mean_facts_raw': sum(r['facts_raw'] for r in records) / max(1, n),
        'mean_certified_recall': sum(r['R'] for r in valid) / max(1, len(valid)),
        'masked_fact_fraction': sum(r['masked'] for r in records) / total if total else 0.,
        'no_predictions': total == 0,
        'answer_accuracy_by_F1': {b: {'n': len(rs), 'answer_accuracy_all': sum(r['answer_reward'] for r in rs)/len(rs),
            'verification_status': dict(__import__('collections').Counter(r['verification'].get('status') for r in rs))} for b, rs in bins.items()}}


def parameter_identity(model, path=None):
    rows = [{'name': n, 'numel': p.numel(), 'requires_grad': p.requires_grad} for n, p in model.named_parameters()]
    visual = [r for r in rows if re.search(r'(?:^|\.)(?:visual|vision_model|vision_tower|vision_encoder|merger|multi_modal_projector|mm_projector)(?:\.|$)', r['name'])]
    merger=[r for r in visual if re.search(r'(?:^|\.)(?:merger|multi_modal_projector|mm_projector)(?:\.|$)',r['name'])]
    encoder=[r for r in visual if r not in merger]
    if not encoder or not merger: raise ValueError('Cannot establish both visual encoder and merger; explicit architecture mapping required')
    bad = [r['name'] for r in visual if r['requires_grad']]
    if bad: raise ValueError('Visual encoder/merger is trainable: ' + ', '.join(bad))
    active = [r for r in rows if r['requires_grad']]
    if not active: raise ValueError('No trainable parameters')
    result = {'parameters': rows, 'trainable_full_names': [r['name'] for r in active],
        'trainable_count': sum(r['numel'] for r in active), 'visual_parameter_tensors': len(visual),
        'visual_encoder_tensors':len(encoder),'merger_tensors':len(merger),
        'visual_frozen': True,'encoder_frozen':True,'merger_frozen':True, 'formal_VL_verification': '未验证'}
    result['sha256'] = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    if path: Path(path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    return result


def attach_language_lora(model, rank=16, alpha=32):
    from peft import LoraConfig, get_peft_model
    names=[n for n,_ in model.named_modules() if n.rsplit('.',1)[-1] in {'q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'} and not any(x in n.lower() for x in ['visual','vision','merger'])]
    if not names:raise ValueError('Language LoRA mapping absent')
    return get_peft_model(model,LoraConfig(r=rank,lora_alpha=alpha,lora_dropout=0.,target_modules=names,task_type='CAUSAL_LM')),names
