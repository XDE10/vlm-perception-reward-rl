#!/usr/bin/env python3
"""Build train.parquet after exact visible-pixel dedup using alpha-composited RGB."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
OUT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-exact-visible-clean")
REPORT = Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
SHARDS = [
    "data/train-00000-of-00003.parquet",
    "data/train-00001-of-00003.parquet",
    "data/train-00002-of-00003.parquet",
]


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    records = [json.loads(line) for line in (REPORT / "rows-visible.jsonl").open(encoding="utf-8")]
    holdout = {
        row["image_visible_rgb"]
        for row in records
        if row["split"] in {"geo3k_test", "k12_test"}
    }
    train_rows = [row for row in records if row["split"] == "train"]
    remove_rows = {
        row["row"] for row in train_rows if row["image_visible_rgb"] in holdout
    }
    remove_by_source = Counter(
        row["source"] for row in train_rows if row["image_visible_rgb"] in holdout
    )
    remove_by_shard = Counter(
        row["shard"] for row in train_rows if row["image_visible_rgb"] in holdout
    )
    expected_remaining_overlap = [
        row for row in train_rows
        if row["row"] not in remove_rows and row["image_visible_rgb"] in holdout
    ]
    if expected_remaining_overlap:
        raise RuntimeError("Internal error: retained train rows still overlap exact visible test pixels")

    OUT.mkdir(parents=True)
    writer = None
    kept = removed = 0
    global_row = 0
    ledger_path = REPORT / "exact_visible_removed_rows.jsonl"
    with ledger_path.open("w", encoding="utf-8") as ledger:
        for shard in SHARDS:
            pf = pq.ParquetFile(ROOT / shard)
            if writer is None:
                writer = pq.ParquetWriter(OUT / "train.parquet", pf.schema_arrow, compression="zstd")
            shard_kept = shard_removed = 0
            for batch in pf.iter_batches(batch_size=64):
                start = global_row + 1
                stop = global_row + batch.num_rows
                keep_mask = []
                for row_number in range(start, stop + 1):
                    keep = row_number not in remove_rows
                    keep_mask.append(keep)
                    if keep:
                        kept += 1
                        shard_kept += 1
                    else:
                        removed += 1
                        shard_removed += 1
                        row = next(
                            r for r in train_rows
                            if r["row"] == row_number
                        )
                        ledger.write(json.dumps({
                            "row": row_number,
                            "shard": shard,
                            "source": row["source"],
                            "image_visible_rgb": row["image_visible_rgb"],
                        }, ensure_ascii=False, sort_keys=True) + "\n")
                selected = batch.filter(pa.array(keep_mask, type=pa.bool_()))
                if selected.num_rows:
                    writer.write_batch(selected)
                global_row = stop
            print(f"{shard}: kept={shard_kept}, removed={shard_removed}", flush=True)
    if writer is not None:
        writer.close()

    output = OUT / "train.parquet"
    pf = pq.ParquetFile(output)
    if pf.metadata.num_rows != kept or kept + removed != len(train_rows):
        raise RuntimeError("Exact-visible train row accounting failed")
    manifest = {
        "dataset": "XenoZLH/MMRL30k",
        "source_revision": "b362381652529d67ebc26f5e140bd0a54ba4647d",
        "source_train_rows": len(train_rows),
        "holdout_splits": ["geo3k_test", "k12_test"],
        "holdout_unique_visible_rgb_hashes": len(holdout),
        "exact_visible_pixel_overlap_removed_rows": removed,
        "removed_by_source": dict(remove_by_source),
        "removed_by_shard": dict(remove_by_shard),
        "remaining_train_rows": kept,
        "output": {
            "path": str(output),
            "bytes": output.stat().st_size,
            "sha256": sha(output),
            "rows": pf.metadata.num_rows,
            "schema": pf.schema_arrow.names,
        },
        "identity": "Visible RGB means RGBA composited over opaque white before hashing; exact dimensions+pixel bytes.",
        "note": "This supersedes the earlier exact filter that hashed convert('RGB') without alpha compositing.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (REPORT / "exact_visible_train_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
