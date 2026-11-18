#!/usr/bin/env python3
"""Create a derived MMRL30k train split with exact RGB-pixel holdout overlap removed.

The upstream snapshot is read-only. This writes only to a separate derived directory.
"""
from __future__ import annotations

import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from PIL import Image

ROOT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
OUT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-decontaminated")
REPORT = Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
SHARDS = [
    "data/train-00000-of-00003.parquet",
    "data/train-00001-of-00003.parquet",
    "data/train-00002-of-00003.parquet",
]
TEST_SPLITS = {"geo3k_test", "k12_test"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rgb_hash(payload: bytes) -> str:
    with Image.open(io.BytesIO(payload)) as image:
        rgb = image.convert("RGB")
        h = hashlib.sha256(f"{rgb.width}x{rgb.height}:".encode())
        h.update(rgb.tobytes())
        return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    rows_path = ROOT / "rows.jsonl"
    holdout_hashes: set[str] = set()
    holdout_members: Counter[str] = Counter()
    for line in rows_path.open(encoding="utf-8"):
        row = json.loads(line)
        if row["split"] in TEST_SPLITS:
            holdout_hashes.add(row["image_rgb"])
            holdout_members[row["split"]] += 1

    writer = None
    kept = 0
    removed = 0
    removed_by_source: Counter[str] = Counter()
    removed_by_shard: Counter[str] = Counter()
    removed_records = []
    try:
        for shard in SHARDS:
            source_path = ROOT / shard
            parquet = pq.ParquetFile(source_path)
            if writer is None:
                writer = pq.ParquetWriter(OUT / "train.parquet", parquet.schema_arrow, compression="zstd")
            shard_row = 0
            shard_kept = 0
            shard_removed = 0
            for batch in parquet.iter_batches(batch_size=32):
                table = pa.Table.from_batches([batch])
                values = batch.column(batch.schema.get_field_index("images")).to_pylist()
                mask = []
                for local_index, image_list in enumerate(values):
                    if len(image_list) != 1 or not image_list[0].get("bytes"):
                        raise RuntimeError(f"Invalid image at {shard}:{shard_row + local_index}")
                    digest = rgb_hash(image_list[0]["bytes"])
                    mask.append(digest not in holdout_hashes)
                    if not mask[-1]:
                        removed += 1
                        shard_removed += 1
                        row = batch.slice(local_index, 1).to_pylist()[0]
                        removed_by_source[row["source"]] += 1
                        removed_by_shard[shard] += 1
                        removed_records.append({
                            "shard": shard,
                            "row_in_shard": shard_row + local_index,
                            "source": row["source"],
                            "image_rgb_sha256": digest,
                            "problem_sha256": sha(" ".join(row["problem"].split()).encode()),
                        })
                    else:
                        kept += 1
                        shard_kept += 1
                selected = table.filter(pa.array(mask, type=pa.bool_()))
                if selected.num_rows:
                    writer.write_table(selected)
                shard_row += batch.num_rows
            print(f"{shard}: rows={shard_row} kept={shard_kept} removed={shard_removed}", flush=True)
    finally:
        if writer is not None:
            writer.close()

    out_file = OUT / "train.parquet"
    digest = hashlib.file_digest(out_file.open("rb"), "sha256").hexdigest()
    manifest = {
        "source_repo": "XenoZLH/MMRL30k",
        "source_revision": "b362381652529d67ebc26f5e140bd0a54ba4647d",
        "source_train_shards": SHARDS,
        "source_train_rows": kept + removed,
        "holdout_splits": sorted(TEST_SPLITS),
        "holdout_unique_rgb_hashes": len(holdout_hashes),
        "removed_rows": removed,
        "kept_rows": kept,
        "removed_by_source": dict(removed_by_source),
        "removed_by_shard": dict(removed_by_shard),
        "output": {
            "path": str(out_file),
            "bytes": out_file.stat().st_size,
            "sha256": digest,
            "rows": pq.ParquetFile(out_file).metadata.num_rows,
        },
        "policy": "Exclude every upstream train row whose decoded RGB image dimensions+pixel bytes exactly match any geo3k_test or k12_test image. Upstream source files remain unchanged.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (REPORT / "decontamination_removed_rows.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in removed_records),
        encoding="utf-8",
    )
    (REPORT / "decontaminated_train_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Recheck output by streaming it and fail closed if any exact RGB match remains.
    remaining = 0
    for batch in pq.ParquetFile(out_file).iter_batches(batch_size=32, columns=["images"]):
        for image_list in batch.column(0).to_pylist():
            if rgb_hash(image_list[0]["bytes"]) in holdout_hashes:
                remaining += 1
    if remaining:
        raise RuntimeError(f"Post-filter exact image overlap remains: {remaining}")
    print(json.dumps({**manifest, "post_filter_exact_overlap_rows": remaining}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
