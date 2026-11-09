"""Keep image-token types aligned with input_ids in TRL's scoring pass, and fail closed if they are not.

TRL 1.17.1 left-pads ``prompt_ids`` for the log-prob passes (reference model, old policy, policy loss) but
rebuilds ``mm_token_type_ids`` with one ``processing_class(images=..., text=..., padding=True)`` call, i.e.
with the processor's *default* padding side. Qwen2.5-VL's tokenizer defaults to right padding, so for every
prompt shorter than the longest one in the generation batch the image span in ``mm_token_type_ids`` sits
``pad`` columns away from the real ``<|image_pad|>`` tokens. transformers 5.19 builds M-RoPE positions from
those types: a small shift silently assigns image positions to text tokens, a larger one raises
``shape mismatch`` in ``get_rope_index`` (preflight-20261109T064716Z-0589, D33). Generation is not affected
(TRL pads those fields explicitly); only scoring, i.e. every gradient.

``left_pad_processor`` sets what TRL itself sets when it loads a processor (left padding and truncation).
``MultimodalAlignmentGuard`` checks every forward of the vision-language core: types must equal 1 exactly
where ``input_ids`` holds the image placeholder (2 for video), else it raises before any logits exist.
"""

VERSION = "mm-alignment-guard-v1-20261109"


def left_pad_processor(processor):
    tokenizer = getattr(processor, "tokenizer", processor)
    tokenizer.padding_side = "left"
    tokenizer.truncation_side = "left"
    return processor


class MultimodalAlignmentGuard:
    def __init__(self, model):
        from src.training.vision_cache import _inner_vl_model

        self.inner = _inner_vl_model(model)
        config = self.inner.config
        self.image_id = int(config.image_token_id)
        video = getattr(config, "video_token_id", None)
        self.video_id = None if video is None else int(video)
        self.checked = 0
        self.padded_rows = 0
        self.max_left_padding = 0
        self.handle = self.inner.register_forward_pre_hook(self._check, with_kwargs=True)

    def expected_types(self, input_ids, dtype):
        expected = (input_ids == self.image_id).to(dtype)
        if self.video_id is not None:
            expected = expected + 2 * (input_ids == self.video_id).to(dtype)
        return expected

    def _check(self, module, args, kwargs):
        import torch

        input_ids = kwargs.get("input_ids", args[0] if args else None)
        types = kwargs.get("mm_token_type_ids")
        if input_ids is None or types is None or tuple(types.shape) != tuple(input_ids.shape):
            return None  # e.g. cached decoding steps; nothing to compare
        expected = self.expected_types(input_ids, types.dtype)
        if not torch.equal(expected, types):
            row = int((expected != types).any(dim=1).nonzero()[0])
            where = lambda t: (t[row] == 1).nonzero()  # noqa: E731
            first_ids = where(expected)
            first_types = where(types)
            raise RuntimeError(
                "mm_token_type_ids disagree with the image tokens in input_ids (row %d: first image token at column "
                "%s in input_ids, %s in mm_token_type_ids). The scoring pass would build wrong M-RoPE positions; "
                "the processor must pad on the left (src/training/multimodal_guard.py, D33)."
                % (row, int(first_ids[0]) if len(first_ids) else None, int(first_types[0]) if len(first_types) else None))
        self.checked += 1
        mask = kwargs.get("attention_mask")
        if mask is not None and mask.dim() == 2:
            leading = (mask.cumsum(dim=1) == 0).sum(dim=1)
            self.padded_rows += int((leading > 0).sum())
            self.max_left_padding = max(self.max_left_padding, int(leading.max()))
        return None

    def stats(self):
        return {"version": VERSION, "checked_forwards": self.checked, "left_padded_rows": self.padded_rows,
                "max_left_padding": self.max_left_padding}

    def remove(self):
        self.handle.remove()


__all__ = ["MultimodalAlignmentGuard", "VERSION", "left_pad_processor"]
