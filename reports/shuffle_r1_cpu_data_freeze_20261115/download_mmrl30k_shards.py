"""Resume pinned Parquet transfers and publish a shard only after hash verification."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import shutil
import time

import requests


SEGMENT_BYTES = 64 * 1024**2


def fetch_range(url, staging, start, end):
    expected = end - start + 1
    for attempt in range(5):
        have = staging.stat().st_size if staging.exists() else 0
        if have == expected:
            return staging
        if have > expected:
            raise ValueError(f"oversize transfer section {staging}")
        offset = start + have
        try:
            with requests.get(
                url, params={"range_start": offset}, headers={"Range": f"bytes={offset}-{end}"},
                stream=True, timeout=(20, 60),
            ) as response:
                response.raise_for_status()
                if response.status_code != 206 or not response.headers.get("Content-Range", "").startswith(
                    f"bytes {offset}-{end}/"
                ):
                    raise ValueError(f"unexpected range response for {staging.name}")
                with staging.open("ab") as stream:
                    for data in response.iter_content(128 * 1024):
                        stream.write(data)
            if staging.stat().st_size == expected:
                print(f"{staging.name}: range complete", flush=True)
                return staging
        except requests.RequestException:
            time.sleep(min(2**attempt, 15))
    raise RuntimeError(f"range remains incomplete: {staging.name}")


def stage_existing_segment(work, file, start, end, segment):
    sources = [
        work / f"{file.name}.{start}{suffix}"
        for suffix in (".block", ".tmp", ".extra-tmp")
    ]
    sources.append(work / f"{file.name}.prefix-{start}.tmp")
    size = end - start + 1
    candidates = [
        (path.stat().st_size, path, 0)
        for path in sources if path.exists() and 0 < path.stat().st_size <= size
    ]
    prefix = file.with_suffix(".parquet.part")
    if prefix.exists() and prefix.stat().st_size > start:
        candidates.append((min(size, prefix.stat().st_size - start), prefix, start))
    existing_size = segment.stat().st_size if segment.exists() else 0
    if candidates:
        length, path, offset = max(candidates)
        if length > existing_size:
            with path.open("rb") as src, segment.open("wb") as dest:
                src.seek(offset)
                remaining = length
                while remaining:
                    block = src.read(min(1024**2, remaining))
                    if not block:
                        raise ValueError(f"incomplete previous transfer {path}")
                    dest.write(block)
                    remaining -= len(block)


def download(root, workers):
    metadata = json.loads((root / "upstream-metadata.json").read_text())
    work = root / ".ranges"
    work.mkdir(exist_ok=True)
    base = f"https://huggingface.co/datasets/XenoZLH/MMRL30k/resolve/{metadata['sha']}"
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = []
        for item in metadata["siblings"]:
            name = item["rfilename"]
            if not name.endswith(".parquet"):
                continue
            target = root / name
            if target.exists():
                continue  # The audit verifies existing files against publisher hashes.
            target.parent.mkdir(parents=True, exist_ok=True)
            futures = []
            for start in range(0, item["size"], SEGMENT_BYTES):
                end = min(start + SEGMENT_BYTES, item["size"]) - 1
                segment = work / f"{target.name}.{start}.resumable"
                stage_existing_segment(work, target, start, end, segment)
                futures.append(pool.submit(fetch_range, f"{base}/{name}", segment, start, end))
            jobs.append((item, target, futures))

        for item, target, futures in jobs:
            combined = work / f"{target.name}.resumable-combined"
            with combined.open("wb") as output:
                for future in futures:
                    with future.result().open("rb") as segment:
                        shutil.copyfileobj(segment, output, 1024**2)
            with combined.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            if combined.stat().st_size != item["size"] or digest != item["lfs"]["sha256"]:
                raise ValueError(f"publisher size or SHA256 differs at {target}")
            combined.replace(target)
            print(f"{target.name}: {digest}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    download(args.root, args.workers)
