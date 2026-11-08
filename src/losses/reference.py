"""Explicit CPU reference losses. These are correctness oracles, not GPU trainers.

Masks describe target token positions. In SFT/OPD position t-1 predicts token t;
zero gradient applies to ignored prediction slots, not shared model parameters.
"""
import torch
import torch.nn.functional as F


def sft_loss(logits, labels):
    if logits.shape[:2] != labels.shape or not (labels[:, 1:] != -100).any():
        raise ValueError('Invalid shapes or no supervised next tokens')
    return F.cross_entropy(logits[:, :-1].reshape(-1, logits.size(-1)),
                           labels[:, 1:].reshape(-1), ignore_index=-100)


def group_advantages(rewards, mode='grpo', eps=1e-8):
    if rewards.ndim != 2 or rewards.size(1) < 2 or not torch.isfinite(rewards).all():
        raise ValueError('Expected finite [prompts, generations>=2] rewards')
    advantage = rewards - rewards.mean(-1, keepdim=True)
    if mode == 'grpo':
        # Sample standard deviation, explicit to match the chosen reference.
        advantage = advantage / (rewards.std(-1, keepdim=True, correction=1) + eps)
    elif mode != 'dr_grpo':
        raise ValueError('Unknown normalization')
    return advantage.detach()


def policy_loss(logp, old_logp, advantages, mask, mode='grpo', constant=None, clip=0.2):
    if logp.shape != old_logp.shape or logp.shape != mask.shape:
        raise ValueError('Token shapes differ')
    if advantages.shape != logp.shape[:-1] or (mask.sum(-1) == 0).any():
        raise ValueError('Invalid advantage shape or empty response')
    ratio = (logp - old_logp.detach()).exp()
    a = advantages.detach().unsqueeze(-1)
    objective = torch.minimum(ratio*a, ratio.clamp(1-clip, 1+clip)*a)
    totals = (objective * mask).sum(-1)
    if mode == 'grpo':
        return -(totals / mask.sum(-1)).mean()
    if mode != 'dr_grpo' or constant is None or constant < mask.size(-1):
        raise ValueError('Dr.GRPO requires fixed maximum length >= token width')
    return -(totals / constant).mean()


def _distributions(student, teacher, response_mask, student_ids, teacher_ids):
    if student.shape[:2] != teacher.shape[:2] or response_mask.shape != student.shape[:2]:
        raise ValueError('Sequence shapes differ')
    if len(student_ids) != len(teacher_ids) or len(set(student_ids)) != len(student_ids) or len(set(teacher_ids)) != len(teacher_ids) or not len(student_ids):
        raise ValueError('Support must be nonempty, unique and aligned')
    mask = response_mask[:, 1:].bool()
    if not mask.any():
        raise ValueError('Empty response')
    si = torch.as_tensor(student_ids, device=student.device)
    ti = torch.as_tensor(teacher_ids, device=teacher.device)
    s = student[:, :-1].index_select(-1, si)[mask]
    t = teacher.detach()[:, :-1].index_select(-1, ti)[mask].to(s.device)
    dtype = torch.float64 if s.dtype == torch.float64 else torch.float32
    if not torch.isfinite(s).all() or not torch.isfinite(t).all():
        raise ValueError('Nonfinite logits on effective support')
    return s.to(dtype).log_softmax(-1), t.to(dtype).log_softmax(-1)


def aligned_kl(student, teacher, response_mask, student_ids, teacher_ids, direction='reverse'):
    """Renormalize on audited common token support; teachers always detached."""
    s, t = _distributions(student, teacher, response_mask, student_ids, teacher_ids)
    if direction == 'reverse':
        values = s.exp() * (s-t)
    elif direction == 'forward':
        values = t.exp() * (t-s)
    else:
        raise ValueError('Unknown KL direction')
    return values.sum(-1).mean()


def mixture_fkl(student_logits, teachers, weights):
    """Fixed-prefix arithmetic mixture; retain teacher entropy in scalar KL."""
    w = torch.as_tensor(weights, dtype=student_logits.dtype, device=student_logits.device)
    if len(teachers) != len(w) or (w < 0).any() or not torch.isclose(w.sum(), w.new_tensor(1.)):
        raise ValueError('Weights must form a probability distribution')
    targets = torch.stack([t.detach().softmax(-1) for t in teachers])
    mix = (targets * w.reshape((-1,) + (1,)*(targets.ndim-1))).sum(0)
    return (mix * (mix.log() - student_logits.log_softmax(-1))).sum(-1).mean()
