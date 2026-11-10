"""Check that vLLM and the training processor turn every training image into the same patch grid.

TRL 1.17.1 starts vLLM with the model directory's processor defaults (min_pixels 3,136, max_pixels 12,845,056 for the
pinned Qwen2.5-VL snapshot) and cannot pass the experiment's max_pixels (802,816). Generation (vLLM) and scoring
(training forward) would then see different image tokens for any image above 802,816 pixels. No approved training
image is that large (S2 acceptance report, section 3.1), and this check keeps it that way: a vLLM run stops before
training if any image would get two different grids (S3 design section 8).
"""
import json
from pathlib import Path


def processor_pixel_limits(model_dir=None, model_id=None, revision=None):
    """(min_pixels, max_pixels, patch factor) from preprocessor_config.json: what vLLM's processor uses when it gets
    no overrides; the factor is patch_size x merge_size (28 for Qwen2.5-VL)."""
    if model_dir:
        path = Path(model_dir) / "preprocessor_config.json"
    else:
        from huggingface_hub import hf_hub_download

        path = Path(hf_hub_download(model_id, "preprocessor_config.json", revision=revision))
    data = json.loads(path.read_text(encoding="utf-8"))
    size = data.get("size") or {}
    low = data.get("min_pixels", size.get("shortest_edge"))
    high = data.get("max_pixels", size.get("longest_edge"))
    if low is None or high is None:
        raise ValueError("preprocessor_config.json has no pixel limits: %s" % path)
    return int(low), int(high), int(data.get("patch_size", 14)) * int(data.get("merge_size", 2))


def grid_mismatches(sizes, train_limits, vllm_limits, factor=28):
    """Image sizes (width, height) whose resized shape differs between the two (min_pixels, max_pixels) limits."""
    from transformers.models.qwen2_vl.image_processing_qwen2_vl import smart_resize

    out = []
    for width, height in sorted(set(tuple(s) for s in sizes)):
        train = smart_resize(height, width, factor=factor, min_pixels=train_limits[0], max_pixels=train_limits[1])
        vllm = smart_resize(height, width, factor=factor, min_pixels=vllm_limits[0], max_pixels=vllm_limits[1])
        if tuple(train) != tuple(vllm):
            out.append({"size": [width, height], "train": list(train), "vllm": list(vllm)})
    return out


def check_training_images(items, config, model_dir=None):
    """Raise when any training image would be resized differently by vLLM; return a small report otherwise."""
    m = config["model"]
    low, high, factor = processor_pixel_limits(model_dir, m["id"], m["revision"])
    sizes = [item["image"].size for item in items if item.get("image") is not None]
    mismatches = grid_mismatches(sizes, (m["min_pixels"], m["max_pixels"]), (low, high), factor)
    report = {"images": len(sizes), "distinct_sizes": len(set(sizes)), "train_limits": [m["min_pixels"], m["max_pixels"]],
              "vllm_limits": [low, high], "factor": factor, "mismatches": len(mismatches)}
    if mismatches:
        raise RuntimeError("vLLM would give %d image size(s) another patch grid than training, e.g. %s; generation and "
                           "scoring would see different image tokens" % (len(mismatches), mismatches[:3]))
    return report


__all__ = ["check_training_images", "grid_mismatches", "processor_pixel_limits"]
