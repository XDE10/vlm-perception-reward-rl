#!/usr/bin/env python3
"""Build a derived train split after exact-pixel and high-confidence visual dedup."""
import hashlib,json
from collections import Counter
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

SOURCE=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-decontaminated/train.parquet")
OUT=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-visible-clean")
REPORT=Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
THRESHOLD_SSIM=0.97
THRESHOLD_IOU=0.80


def sha(path):
    with path.open("rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()


def main():
    if OUT.exists(): raise FileExistsError(f"Refusing to overwrite existing output: {OUT}")
    d=[json.loads(x) for x in (REPORT/"perceptual_candidate_scores.jsonl").open()]
    p=[json.loads(x) for x in (REPORT/"perceptual_phash_scores.jsonl").open()]
    dhigh={r["clean_train_row"]:r for r in d if r["ssim_global"]>=THRESHOLD_SSIM and r["ink_iou_0.95"]>=THRESHOLD_IOU}
    phigh={r["clean_train_row"]:r for r in p if r["ssim_global"]>=THRESHOLD_SSIM and r["ink_iou_0.95"]>=THRESHOLD_IOU}
    remove=set(dhigh)
    if len(remove)!=286: raise RuntimeError(f"Expected 286 high-confidence dHash rows, got {len(remove)}")
    if len(phigh)!=285: raise RuntimeError(f"Expected 285 independent pHash-confirmed rows, got {len(phigh)}")
    if not set(phigh).issubset(remove): raise RuntimeError("pHash/dHash row sets are inconsistent")
    if len(remove-set(phigh))!=1: raise RuntimeError("Expected exactly one dHash-only row")
    for row in remove:
        if dhigh[row]["source"]!="mm-eureka" or not dhigh[row]["holdout"].startswith("k12_test:"):
            raise RuntimeError(f"Unexpected near-duplicate source/split for row {row}")

    OUT.mkdir(parents=True)
    source_pf=pq.ParquetFile(SOURCE)
    writer=pq.ParquetWriter(OUT/"train.parquet",source_pf.schema_arrow,compression="zstd")
    removed_count=0
    kept_count=0
    by_source=Counter()
    with (REPORT/"near_duplicate_removed_rows.jsonl").open("w",encoding="utf-8") as ledger:
        for batch_no,batch in enumerate(source_pf.iter_batches(batch_size=128)):
            start=batch_no*128+1
            indices=range(start,start+batch.num_rows)
            keep=[]
            for index in indices:
                remove_row=index in remove
                keep.append(not remove_row)
                if remove_row:
                    removed_count+=1
                    row=dhigh[index]
                    ph=phigh.get(index)
                    by_source[row["source"]]+=1
                    record={
                        "clean_train_row":index,
                        "source":row["source"],
                        "holdout":row["holdout"],
                        "dhash_hamming":row["dhash_hamming"],
                        "dhash_ssim_global":row["ssim_global"],
                        "dhash_ink_iou_0.95":row["ink_iou_0.95"],
                        "phash_independent_match":ph is not None,
                        "phash_hamming":ph["phash_hamming"] if ph else None,
                        "phash_ssim_global":ph["ssim_global"] if ph else None,
                        "phash_ink_iou_0.95":ph["ink_iou_0.95"] if ph else None,
                        "exclusion_rule":"visible-image near duplicate: SSIM>=0.97 and ink IoU>=0.80 after alpha composite over white",
                    }
                    ledger.write(json.dumps(record,ensure_ascii=False,sort_keys=True)+"\n")
            selected=batch.filter(pa.array(keep,type=pa.bool_()))
            if selected.num_rows:
                writer.write_batch(selected)
                kept_count+=selected.num_rows
            if (batch_no+1)%50==0: print(f"batches={batch_no+1} kept={kept_count} removed={removed_count}",flush=True)
    writer.close()
    output=OUT/"train.parquet"
    digest=sha(output)
    pf=pq.ParquetFile(output)
    if removed_count!=286 or kept_count!=27802 or pf.metadata.num_rows!=27802:
        raise RuntimeError(f"Row accounting failed: removed={removed_count} kept={kept_count} file={pf.metadata.num_rows}")
    manifest={
        "dataset":"XenoZLH/MMRL30k",
        "source_revision":"b362381652529d67ebc26f5e140bd0a54ba4647d",
        "source_original_train_rows":29101,
        "exact_visible_pixel_overlap_removed":1013,
        "near_duplicate_removed_after_exact_filter":removed_count,
        "near_duplicate_dhash_rows":len(dhigh),
        "near_duplicate_phash_independently_confirmed_rows":len(phigh),
        "dhash_only_high_confidence_rows":len(remove-set(phigh)),
        "near_duplicate_removed_by_source":dict(by_source),
        "final_train_rows":kept_count,
        "output":{
            "path":str(output),"bytes":output.stat().st_size,"sha256":digest,
            "rows":pf.metadata.num_rows,"schema":pf.schema_arrow.names,
        },
        "near_duplicate_rule":{
            "dhash_candidate_threshold":5,
            "phash_independent_candidate_threshold":8,
            "visible_rendering":"RGBA alpha composite over opaque white",
            "normalization":"letterbox to 256x256 grayscale",
            "ssim_global_min":THRESHOLD_SSIM,
            "ink_iou_grayscale_threshold":0.95,
            "ink_iou_min":THRESHOLD_IOU,
            "visual_manual_sample":"24 broad dHash candidate pairs and 16 high-SSIM borderline pairs inspected via contact sheets; all displayed pairs showed the same diagram/image content",
            "note":"286 unique rows were excluded; 285 were independently found by both dHash and pHash, one additional row by dHash only. This is a high-confidence near-duplicate screen, not proof that all semantic/near duplicates are absent.",
        },
        "policy":"Original published Parquet shards are unchanged. This is a separate derived train split for research; official test splits remain untouched.",
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (REPORT/"final_decontaminated_train_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2,ensure_ascii=False))


if __name__=="__main__": main()
