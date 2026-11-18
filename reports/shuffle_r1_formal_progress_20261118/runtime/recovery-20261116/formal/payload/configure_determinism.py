"""Apply the training worker settings verified by the B16 replay probe."""
import torch


def apply():
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
