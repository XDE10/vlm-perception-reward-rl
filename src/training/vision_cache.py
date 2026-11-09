"""Optional cache of frozen ViT outputs, keyed by each image's exact pixel tensor.

Valid only while every vision/merger parameter is frozen and deterministic. The
cache wraps ``Qwen2_5_VLModel.get_image_features`` (transformers 5.x returns a
``BaseModelOutputWithPooling`` whose ``pooler_output`` is a tuple of per-image
embeddings). Keys hash the raw bytes of every image's patch rows plus its grid,
so two different images can never share an entry. The experiment enables it
only after a GPU equivalence check in preflight (D-entries in 决策记录).
"""
import hashlib
from collections import OrderedDict

VERSION = "frozen-vit-cache-v1-20261109"


def _inner_vl_model(model):
    candidates = [model]
    for attr in ["get_base_model"]:
        if hasattr(model, attr):
            candidates.append(getattr(model, attr)())
    for candidate in list(candidates):
        if hasattr(candidate, "model"):
            candidates.append(candidate.model)
    for candidate in candidates:
        if hasattr(candidate, "visual") and hasattr(candidate, "get_image_features"):
            return candidate
    raise ValueError("Could not locate the vision-language core model with .visual and .get_image_features")


class FrozenVisionCache:
    def __init__(self, model, max_items=4096):
        self.inner = _inner_vl_model(model)
        trainable = [n for n, p in self.inner.visual.named_parameters() if p.requires_grad]
        if trainable:
            raise ValueError("Vision cache requires a frozen vision tower; trainable: " + ", ".join(trainable[:3]))
        self.original = self.inner.get_image_features
        self.max_items = max_items
        self.entries = OrderedDict()
        self.hits = self.misses = 0
        self.inner.get_image_features = self.get_image_features

    @staticmethod
    def _key(chunk, grid):
        data = chunk.detach().contiguous().view(-1).view(dtype=__import__("torch").uint8).cpu().numpy().tobytes()
        return hashlib.blake2b(data, digest_size=16).hexdigest() + ":" + ",".join(str(int(x)) for x in grid.tolist())

    def get_image_features(self, pixel_values, image_grid_thw=None, **kwargs):
        import torch
        from transformers.modeling_outputs import BaseModelOutputWithPooling

        if image_grid_thw is None:
            return self.original(pixel_values, image_grid_thw, **kwargs)
        sizes = image_grid_thw.prod(-1).tolist()
        chunks = torch.split(pixel_values, sizes)
        keys = [self._key(chunk, grid) for chunk, grid in zip(chunks, image_grid_thw)]
        missing = [i for i, key in enumerate(keys) if key not in self.entries]
        self.hits += len(keys) - len(missing)
        self.misses += len(missing)
        if missing:
            kwargs = {**kwargs, "return_dict": True}
            with torch.no_grad():
                output = self.original(torch.cat([chunks[i] for i in missing]), image_grid_thw[missing], **kwargs)
            for i, embedding in zip(missing, output.pooler_output):
                self.entries[keys[i]] = embedding.detach()
                if len(self.entries) > self.max_items:
                    self.entries.popitem(last=False)
        for key in keys:
            self.entries.move_to_end(key)
        return BaseModelOutputWithPooling(pooler_output=tuple(self.entries[key] for key in keys))

    def stats(self):
        return {"version": VERSION, "hits": self.hits, "misses": self.misses, "entries": len(self.entries)}

    def remove(self):
        self.inner.get_image_features = self.original


__all__ = ["FrozenVisionCache", "VERSION"]
