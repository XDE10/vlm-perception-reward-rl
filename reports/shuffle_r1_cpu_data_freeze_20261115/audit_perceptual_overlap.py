#!/usr/bin/env python3
"""Fast dHash screen using visible pixels after alpha compositing over white.

Candidates are for review only. Exact pixel matches are separately excluded.
"""
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from PIL import Image

ROOT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
CLEAN = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-decontaminated/train.parquet")
REPORT = Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
TESTS = [
    ("geo3k_test", ROOT / "data/geo3k_test-00000-of-00001.parquet"),
    ("k12_test", ROOT / "data/k12_test-00000-of-00001.parquet"),
]
BATCH = 64
RADIUS = 5
LUT = np.array([int(i).bit_count() for i in range(256)], dtype=np.uint8)


def visible_image(image):
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(background, rgba).convert("RGB")


def dhash(payload):
    with Image.open(io.BytesIO(payload)) as image:
        pixels = list(visible_image(image).convert("L").resize((9, 8), Image.Resampling.LANCZOS).getdata())
    value = 0
    for y in range(8):
        off = y * 9
        for x in range(8):
            value = (value << 1) | int(pixels[off + x] > pixels[off + x + 1])
    return value


def visible_rgb_hash(payload):
    with Image.open(io.BytesIO(payload)) as image:
        rgb = visible_image(image)
        digest = hashlib.sha256(f"{rgb.width}x{rgb.height}:".encode())
        digest.update(rgb.tobytes())
    return digest.hexdigest()


def iter_rows(path):
    index = 0
    for batch in pq.ParquetFile(path).iter_batches(batch_size=BATCH, columns=["images", "source"]):
        images = batch.column(0).to_pylist()
        sources = batch.column(1).to_pylist()
        for image_list, source in zip(images, sources):
            index += 1
            yield index, source, image_list[0]["bytes"]


def distances(values, holdout):
    xor = np.bitwise_xor(np.asarray(values, dtype=np.uint64)[:, None], holdout[None, :])
    byte_view = xor.view(np.uint8).reshape(xor.shape[0], xor.shape[1], 8)
    return LUT[byte_view].sum(axis=2, dtype=np.uint8)


def main():
    holdout_hashes = []
    holdout_labels = []
    holdout_rgb = set()
    counts = Counter()
    for split, path in TESTS:
        for index, source, payload in iter_rows(path):
            counts[split] += 1
            holdout_hashes.append(dhash(payload))
            holdout_labels.append(f"{split}:{index}:{source}")
            holdout_rgb.add(visible_rgb_hash(payload))
        print(f"indexed {split}: {counts[split]}", flush=True)
    holdout = np.asarray(holdout_hashes, dtype=np.uint64)

    candidates = []
    train_count = 0
    train_sources = Counter()
    candidate_sources = Counter()
    for index, source, payload in iter_rows(CLEAN):
        train_count += 1
        train_sources[source] += 1
        if visible_rgb_hash(payload) in holdout_rgb:
            raise RuntimeError(f"Exact visible RGB overlap survived filtering at clean train row {index}")
        value = dhash(payload)
        dist = distances([value], holdout)[0]
        best = int(dist.min())
        if best <= RADIUS:
            for match_index in np.flatnonzero(dist == best):
                candidates.append({
                    "clean_train_row": index,
                    "source": source,
                    "holdout": holdout_labels[int(match_index)],
                    "dhash_hamming": best,
                })
                candidate_sources[source] += 1
        if train_count % 2048 == 0:
            print(f"screened clean train rows: {train_count}", flush=True)

    result = {
        "source_revision": "b362381652529d67ebc26f5e140bd0a54ba4647d",
        "method": "64-bit dHash on 9x8 grayscale image after RGBA alpha compositing over white; vectorized Hamming distance; candidate threshold <=5; exact visible RGB collisions rejected",
        "threshold": RADIUS,
        "holdout_rows": dict(counts),
        "holdout_unique_visible_rgb": len(holdout_rgb),
        "clean_train_rows_screened": train_count,
        "clean_train_by_source": dict(train_sources),
        "near_duplicate_candidate_pairs": len(candidates),
        "candidate_pairs_by_train_source": dict(candidate_sources),
        "interpretation": "dHash candidates are review leads only. No row is automatically removed. Transparent pixels are rendered over white before hashing.",
    }
    (REPORT / "perceptual_overlap_candidates.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in candidates),
        encoding="utf-8",
    )
    (REPORT / "perceptual_overlap_audit.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
