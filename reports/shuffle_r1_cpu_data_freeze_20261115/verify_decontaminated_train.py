#!/usr/bin/env python3
"""Verify the exact-image exclusion ledger and derived Parquet identity."""
import hashlib
import json
from pathlib import Path
import pyarrow.parquet as pq

ROOT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
OUT = Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-decontaminated")
REPORT = Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
TESTS = {"geo3k_test", "k12_test"}


def main():
    rows = [json.loads(line) for line in (ROOT / "rows.jsonl").open(encoding="utf-8")]
    holdout = {r["image_rgb"] for r in rows if r["split"] in TESTS}
    train = [r for r in rows if r["split"] == "train"]
    shard_offsets = {}
    for row in train:
        shard_offsets.setdefault(row["shard"], row["row"])
    expected = {
        (row["shard"], row["row"] - shard_offsets[row["shard"]])
        for row in train if row["image_rgb"] in holdout
    }
    removed = [json.loads(line) for line in (REPORT / "decontamination_removed_rows.jsonl").open(encoding="utf-8")]
    actual = {(row["shard"], row["row_in_shard"]) for row in removed}
    if actual != expected:
        raise AssertionError(
            f"exclusion ledger mismatch: expected={len(expected)} actual={len(actual)} "
            f"missing={len(expected-actual)} extra={len(actual-expected)}"
        )

    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    output = OUT / "train.parquet"
    parquet = pq.ParquetFile(output)
    digest = hashlib.file_digest(output.open("rb"), "sha256").hexdigest()
    checks = {
        "all_exact_overlap_rows_listed": actual == expected,
        "source_train_row_accounting": len(train) == len(expected) + parquet.metadata.num_rows,
        "manifest_row_count": manifest["output"]["rows"] == parquet.metadata.num_rows,
        "manifest_sha256": manifest["output"]["sha256"] == digest,
        "manifest_file_size": manifest["output"]["bytes"] == output.stat().st_size,
        "expected_schema": parquet.schema_arrow.names == ["problem", "images", "answer", "source"],
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    result = {
        "source_revision": manifest["source_revision"],
        "source_train_rows": len(train),
        "holdout_unique_rgb_hashes": len(holdout),
        "removed_rows": len(expected),
        "kept_rows": parquet.metadata.num_rows,
        "removed_by_source": dict(__import__("collections").Counter(row["source"] for row in removed)),
        "output_bytes": output.stat().st_size,
        "output_sha256": digest,
        "checks": checks,
        "scope": "This verifies exact decoded-RGB-pixel isolation. It does not certify perceptual/near-duplicate isolation.",
    }
    (REPORT / "decontaminated_train_verification.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
