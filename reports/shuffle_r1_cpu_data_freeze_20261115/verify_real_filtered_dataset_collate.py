#!/usr/bin/env python3
"""Exercise the actual Shuffle-R1 RLHFDataset and Qwen2.5-VL processor on filtered data."""
import json
from pathlib import Path

import numpy as np

from verl.utils.dataset import RLHFDataset, collate_fn
from verl.utils.tokenizer import get_processor, get_tokenizer

MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"
REVISION = "66285546d2b821cf421d4f5eb2576359d3770cd3"
DATA = "/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-visible-clean/train.parquet"
OUT = Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115/real-filtered-data-collate.txt")

processor = get_processor(MODEL, revision=REVISION, local_files_only=True, use_fast=True, max_pixels=4194304)
tokenizer = get_tokenizer(MODEL, revision=REVISION, local_files_only=True)
if processor is None:
    raise RuntimeError("Pinned Qwen2.5-VL processor is not available in local cache")

dataset = RLHFDataset(
    data_path=DATA,
    tokenizer=tokenizer,
    processor=processor,
    prompt_key="problem",
    answer_key="answer",
    image_key="images",
    max_prompt_length=2048,
    truncation="right",
    max_pixels=4194304,
    min_pixels=262144,
)
n = min(16, len(dataset))
features = [dataset[i] for i in range(n)]
batch = collate_fn(features)
position_ids = batch["position_ids"]
if tuple(position_ids.shape[:2]) != (n, 3):
    raise RuntimeError(f"Unexpected Qwen M-RoPE shape: {tuple(position_ids.shape)}")

image_extrema = []
nonwhite_ratios = []
for feature in features:
    images = feature["multi_modal_data"]["image"]
    if len(images) != 1:
        raise RuntimeError("Expected one image per MMRL30k row")
    image = images[0]
    if image.mode != "RGB":
        raise RuntimeError(f"Image not normalized to RGB: {image.mode}")
    arr = np.asarray(image)
    nonwhite = float(np.any(arr < 245, axis=2).mean())
    pure_black = float(np.all(arr == 0, axis=2).mean())
    if pure_black > 0.99:
        raise RuntimeError("Transparent image was incorrectly reduced to a black canvas")
    image_extrema.append(image.getextrema())
    nonwhite_ratios.append(nonwhite)

result = {
    "dataset_path": DATA,
    "dataset_rows": len(dataset),
    "tested_rows": n,
    "processor": processor.image_processor.__class__.__name__,
    "position_ids_shape": list(position_ids.shape),
    "image_extrema": image_extrema,
    "nonwhite_pixel_ratios": nonwhite_ratios,
    "status": "PASS",
}
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
