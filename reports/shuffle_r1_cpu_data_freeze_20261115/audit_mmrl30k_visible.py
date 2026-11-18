#!/usr/bin/env python3
"""Re-audit MMRL30k using the visible image (alpha composited on white)."""
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq
from PIL import Image

ROOT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
REPORT = Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
COLUMNS = ("problem", "images", "answer", "source")
SPLITS = {
    "geo3k_test": ["data/geo3k_test-00000-of-00001.parquet"],
    "geo3k_train": ["data/geo3k_train-00000-of-00000.parquet"],
    "k12_test": ["data/k12_test-00000-of-00001.parquet"],
    "k12_train": ["data/k12_train-00000-of-00000.parquet"],
    "train": ["data/train-00000-of-00003.parquet", "data/train-00001-of-00003.parquet", "data/train-00002-of-00003.parquet"],
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def normalized(text):
    import unicodedata
    return " ".join(unicodedata.normalize("NFKC", text).split())


def visible_rgb(payload):
    with Image.open(io.BytesIO(payload)) as opened:
        rgba = opened.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        return Image.alpha_composite(background, rgba).convert("RGB")


def visible_hash(payload):
    rgb = visible_rgb(payload)
    h = hashlib.sha256(f"{rgb.width}x{rgb.height}:".encode())
    h.update(rgb.tobytes())
    return h.hexdigest()


def audit():
    metadata = json.loads((ROOT / "upstream-metadata.json").read_text(encoding="utf-8"))
    declared = json.loads((ROOT / "dataset_dict.json").read_text(encoding="utf-8"))["splits"]
    if set(declared) != set(SPLITS):
        raise ValueError(f"Dataset split metadata mismatch: {declared}")

    report = {
        "repo": "XenoZLH/MMRL30k",
        "revision": metadata["sha"],
        "rendering": "PIL RGBA alpha composite over opaque white, then RGB pixels",
        "splits": {},
        "shards": {},
    }
    counters = {}
    row_manifest = REPORT / "rows-visible.jsonl"
    pending = row_manifest.with_suffix(".jsonl.part")
    with pending.open("w", encoding="utf-8") as output:
        for split, files in SPLITS.items():
            counts = defaultdict(Counter)
            sources = Counter()
            rows = 0
            errors = []
            alpha_rows = 0
            for relative in files:
                path = ROOT / relative
                siblings = {x["rfilename"]: x for x in metadata["siblings"]}
                item = siblings[relative]
                digest = file_sha(path)
                if path.stat().st_size != item["size"] or digest != item["lfs"]["sha256"]:
                    raise ValueError(f"Publisher SHA/size mismatch: {relative}")
                pf = pq.ParquetFile(path)
                if set(pf.schema_arrow.names) != set(COLUMNS):
                    raise ValueError(f"Unexpected schema: {relative} {pf.schema_arrow.names}")
                report["shards"][relative] = {
                    "bytes": path.stat().st_size,
                    "rows": pf.metadata.num_rows,
                    "sha256": digest,
                }
                for batch in pf.iter_batches(batch_size=32, columns=COLUMNS):
                    for row in batch.to_pylist():
                        rows += 1
                        try:
                            problem = normalized(row["problem"])
                            answer = normalized(row["answer"])
                            source = normalized(row["source"])
                            images = row["images"]
                            if not problem or not answer or not source or len(images) != 1:
                                raise ValueError("invalid problem/answer/source or image count")
                            image = images[0]
                            if not isinstance(image, dict) or not image.get("bytes"):
                                raise ValueError("missing embedded image bytes")
                            with Image.open(io.BytesIO(image["bytes"])) as opened:
                                has_alpha = "A" in opened.getbands() or "transparency" in opened.info
                            alpha_rows += int(has_alpha)
                            image_visible = visible_hash(image["bytes"])
                        except Exception as error:
                            errors.append({"row": rows, "shard": relative, "error": str(error)})
                            continue
                        ids = {
                            "image_bytes": sha(images[0]["bytes"]),
                            "image_visible_rgb": image_visible,
                            "problem": sha(problem.encode()),
                            "problem_image": sha(f"{image_visible}\n{problem}".encode()),
                            "problem_image_answer": sha(f"{image_visible}\n{problem}\n{answer}".encode()),
                        }
                        for key, value in ids.items():
                            counts[key][value] += 1
                        sources[source] += 1
                        output.write(json.dumps({
                            "split": split,
                            "row": rows,
                            "shard": relative,
                            "source": source,
                            **ids,
                        }, ensure_ascii=False, sort_keys=True) + "\n")
            counters[split] = counts
            report["splits"][split] = {
                "rows": rows,
                "by_source": dict(sources),
                "rows_with_alpha_or_transparency": alpha_rows,
                "errors": errors,
                "duplicate_rows_by_identity": {
                    key: counter.total() - len(counter) for key, counter in counts.items()
                },
            }
            print(f"{split}: rows={rows}, alpha={alpha_rows}, errors={len(errors)}", flush=True)
    pending.replace(row_manifest)
    report["row_manifest_sha256"] = file_sha(row_manifest)

    train = counters["train"]["image_visible_rgb"]
    holdout = counters["geo3k_test"]["image_visible_rgb"] + counters["k12_test"]["image_visible_rgb"]
    holdout_hashes = set(holdout)
    removed_train = []
    for relative in SPLITS["train"]:
        pf = pq.ParquetFile(ROOT / relative)
        for batch in pf.iter_batches(batch_size=32, columns=["images", "source"]):
            for row in batch.to_pylist():
                image_hash = visible_hash(row["images"][0]["bytes"])
                if image_hash in holdout_hashes:
                    removed_train.append({"shard": relative, "source": row["source"], "image_visible_rgb": image_hash})
    report["exact_visible_pixel_overlap"] = {
        "holdout_unique_visible_images": len(holdout_hashes),
        "matching_train_rows": len(removed_train),
        "matching_train_rows_by_source": dict(Counter(row["source"] for row in removed_train)),
        "matching_train_rows_by_shard": dict(Counter(row["shard"] for row in removed_train)),
        "matched_test_rows": {
            split: sum(1 for image_hash in counters[split]["image_visible_rgb"] if image_hash in set(train))
            for split in ("geo3k_test", "k12_test")
        },
    }
    (REPORT / "mmrl30k-visible-audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (REPORT / "visible_exact_overlap_train_rows.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in removed_train),
        encoding="utf-8",
    )
    print(json.dumps(report["exact_visible_pixel_overlap"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    audit()
