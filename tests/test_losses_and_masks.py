import json
from pathlib import Path
import pytest
import torch
import torch.nn.functional as F
from src.losses import sft_loss, group_advantages, policy_loss, aligned_kl, mixture_fkl

torch.set_num_threads(2)


def test_shift_prompt_padding_eos_gradients():
    x = torch.randn(1, 7, 8, dtype=torch.double, requires_grad=True)
    labels = torch.tensor([[-100, -100, -100, 3, 4, 2, -100]]) # 2=EOS
    loss = sft_loss(x, labels)
    expected = sum(-x[0, i-1].log_softmax(-1)[labels[0,i]] for i in [3,4,5])/3
    torch.testing.assert_close(loss, expected)
    loss.backward()
    assert torch.count_nonzero(x.grad[0,[0,1,5,6]]) == 0
    assert all(x.grad[0,i].abs().sum() > 0 for i in [2,3,4])


@pytest.mark.parametrize('value', [0., 1.])
@pytest.mark.parametrize('mode', ['grpo', 'dr_grpo'])
def test_equal_rewards(value, mode):
    a = group_advantages(torch.full((2,4), value), mode)
    assert torch.isfinite(a).all() and torch.count_nonzero(a) == 0


def test_advantage_and_length_gradient():
    r = torch.tensor([[1.,0.,0.,0.]])
    a, b = group_advantages(r), group_advantages(r,'dr_grpo')
    torch.testing.assert_close(a, torch.tensor([[1.5,-.5,-.5,-.5]]))
    torch.testing.assert_close(b, torch.tensor([[.75,-.25,-.25,-.25]]))
    x = torch.zeros(1,4,4, requires_grad=True)
    mask = torch.tensor([[[1.,0,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,1]]])
    g = torch.autograd.grad(policy_loss(x,x.detach(),a,mask),x)[0]
    d = torch.autograd.grad(policy_loss(x,x.detach(),b,mask,'dr_grpo',4),x)[0]
    torch.testing.assert_close(g[0,:,0],torch.tensor([-.375,.0625,1/24,.03125]))
    torch.testing.assert_close(d[0,:,0],torch.tensor([-.046875,.015625,.015625,.015625]))
    assert torch.count_nonzero(g[mask == 0]) == 0
    assert not torch.allclose(g,d)


def test_ratio_clipping():
    x = torch.tensor([[2.,-2.]],requires_grad=True)
    mask = torch.ones_like(x)
    loss = policy_loss(x,torch.zeros_like(x),torch.ones(1),mask)
    loss.backward()
    assert x.grad[0,0] == 0 and x.grad[0,1] < 0


@pytest.mark.parametrize('direction',['forward','reverse'])
def test_large_vocabulary_alignment(direction):
    report = Path('reports/tokenizer_alignment_report.json')
    # First task uses a synthetic support. Final rerun uses actual audited IDs.
    ids = json.loads(report.read_text(encoding='utf-8'))['common_support']['ids'] if report.exists() else list(range(17))
    torch.manual_seed(2)
    s = torch.randn(1,3,151936,requires_grad=True)
    t = torch.randn(1,3,152064,requires_grad=True)
    mask = torch.tensor([[0,1,0]])
    with torch.no_grad(): t[:,:,:151936].copy_(s)
    equal = aligned_kl(s,t,mask,ids,ids,direction)
    assert abs(equal.item()) < 1e-6
    equal.backward()
    assert s.grad.abs().max() < 1e-7 and t.grad is None
    s.grad = None
    with torch.no_grad(): t[:,:,ids[0]] += 2
    loss = aligned_kl(s,t,mask,ids,ids,direction)
    loss.backward()
    assert loss > 0 and torch.isfinite(s.grad).all() and s.grad.abs().sum() > 0
    assert torch.count_nonzero(s.grad[:,1:]) == 0 and t.grad is None
    removed = list(set(range(151936))-set(ids))
    assert torch.count_nonzero(s.grad[:,:,removed]) == 0


def test_weighted_teacher_fkl_gradient_identity():
    torch.manual_seed(9)
    s = torch.randn(2,3,7,dtype=torch.double,requires_grad=True)
    teachers = [torch.randn_like(s,requires_grad=True) for _ in range(2)]
    weights = [.3,.7]
    weighted = sum(w*(t.detach().softmax(-1)*(t.detach().log_softmax(-1)-s.log_softmax(-1))).sum(-1).mean() for w,t in zip(weights,teachers))
    mixture = mixture_fkl(s,teachers,weights)
    g1 = torch.autograd.grad(weighted,s)[0]
    g2 = torch.autograd.grad(mixture,s)[0]
    assert (g1-g2).abs().max() < 1e-6
    assert weighted > mixture
    assert all(t.grad is None for t in teachers)


def test_kl_mapping_padding_and_gradcheck():
    s = torch.randn(1,3,3,dtype=torch.double,requires_grad=True)
    t = torch.randn_like(s,requires_grad=True)
    m = torch.tensor([[0,1,0]])
    ids = [0,1,2]
    a = aligned_kl(s,t,m,ids,ids)
    b = aligned_kl(s,t[:,:,[2,0,1]],m,ids,[1,2,0])
    torch.testing.assert_close(a,b)
    assert torch.autograd.gradcheck(lambda z: aligned_kl(z,t,m,ids,ids),(s,))
    with pytest.raises(ValueError): aligned_kl(s,t,torch.zeros_like(m),ids,ids)
    with pytest.raises(ValueError): sft_loss(s,torch.full((1,3),-100))
