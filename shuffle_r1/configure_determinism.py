"""Apply the deterministic worker flags used in the formal run."""
import torch


def apply():
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
