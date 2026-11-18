"""Verify the publisher's shards and audit membership without changing any split."""

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import unicodedata

from PIL import Image
import pyarrow.parquet as parquet


COLUMNS = ("problem", "images", "answer", "source")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def normalized(text):
    return " ".join(unicodedata.normalize("NFKC", text).split())


def image_hashes(image):
    if not isinstance(image, dict) or "path" not in image or not image.get("bytes"):
        raise ValueError("expected embedded image bytes")
    if image["path"] is not None and not isinstance(image["path"], str):
        raise ValueError("expected image path to be a string or null")
    payload = image["bytes"]
    with Image.open(io.BytesIO(payload)) as opened:
        rgb = opened.convert("RGB")
        pixel_hash = hashlib.sha256(f"{rgb.width}x{rgb.height}:".encode())
        pixel_hash.update(rgb.tobytes())
    return sha256(payload), pixel_hash.hexdigest()


def audit(root):
    metadata = json.loads((root / "upstream-metadata.json").read_text())
    splits = json.loads((root / "dataset_dict.json").read_text())["splits"]
    shards = defaultdict(list)
    for item in metadata["siblings"]:
        if item["rfilename"].endswith(".parquet"):
            split = Path(item["rfilename"]).name.split("-", 1)[0]
            shards[split].append(item)
    if set(shards) != set(splits):
        raise ValueError(f"split declaration {splits} differs from shards {list(shards)}")

    report = {"repo": "XenoZLH/MMRL30k", "revision": metadata["sha"], "splits": {}, "shards": {}}
    membership = {}
    manifest = root / "rows.jsonl"
    pending = manifest.with_suffix(".jsonl.part")
    with pending.open("w", encoding="utf-8") as output:
        for split in sorted(shards):
            counts = defaultdict(Counter)
            sources = Counter()
            images_with_path = 0
            errors = []
            row_count = 0
            for item in sorted(shards[split], key=lambda value: value["rfilename"]):
                name = item["rfilename"]
                path = root / name
                digest = file_sha256(path)
                if path.stat().st_size != item["size"] or digest != item["lfs"]["sha256"]:
                    raise ValueError(f"publisher's file identity mismatch: {name}")
                reader = parquet.ParquetFile(path)
                if set(reader.schema_arrow.names) != set(COLUMNS):
                    raise ValueError(f"unexpected fields in {name}: {reader.schema_arrow.names}")
                report["shards"][name] = {"bytes": item["size"], "sha256": digest, "rows": reader.metadata.num_rows}
                for batch in reader.iter_batches(batch_size=64, columns=COLUMNS):
                    for row in batch.to_pylist():
                        row_count += 1
                        try:
                            problem, answer, source = (normalized(row[key]) for key in ("problem", "answer", "source"))
                            if not problem or not answer or not source:
                                raise ValueError("empty problem, answer or source")
                            if len(row["images"]) != 1:
                                raise ValueError("expected exactly one image")
                            image_bytes, image_rgb = image_hashes(row["images"][0])
                        except (TypeError, ValueError, OSError) as error:
                            errors.append({"row": row_count, "shard": name, "error": str(error)})
                            continue
                        ids = {
                            "image_bytes": image_bytes,
                            "image_rgb": image_rgb,
                            "problem": sha256(problem.encode()),
                            "problem_image": sha256(f"{image_rgb}\n{problem}".encode()),
                            "problem_image_answer": sha256(f"{image_rgb}\n{problem}\n{answer}".encode()),
                        }
                        for key, value in ids.items():
                            counts[key][value] += 1
                        sources[source] += 1
                        images_with_path += bool(row["images"][0]["path"])
                        record = {"split": split, "row": row_count, "shard": name, "source": source, **ids}
                        output.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                print(f"{name}: {reader.metadata.num_rows} rows checked", flush=True)
            membership[split] = counts
            report["splits"][split] = {
                "rows": row_count, "by_source": dict(sources), "errors": errors,
                "embedded_images_with_path": images_with_path,
                "rows_beyond_first_occurrence": {key: counter.total() - len(counter) for key, counter in counts.items()},
            }
    pending.replace(manifest)
    report["row_manifest_sha256"] = file_sha256(manifest)
    report["train_holdout_overlap"] = {}
    for train in sorted(split for split in membership if split.endswith("train")):
        for test in sorted(split for split in membership if split.endswith("test")):
            report["train_holdout_overlap"][f"{train}/{test}"] = {
                key: sum(count for sample, count in counter.items() if sample in membership[train][key])
                for key, counter in membership[test].items()
            }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    root = parser.parse_args().root
    stats = audit(root)
    (root / "audit.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    if any(split["errors"] for split in stats["splits"].values()):
        raise SystemExit("Dataset contains invalid rows. See audit.json.")
