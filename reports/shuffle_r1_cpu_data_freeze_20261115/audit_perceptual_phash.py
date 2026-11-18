"""Independent pHash screen against holdout images, compositing alpha over white."""
import hashlib,io,json
from collections import Counter
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
from PIL import Image

ROOT=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
CLEAN=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-decontaminated/train.parquet")
REPORT=Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
TESTS=[("geo3k_test",ROOT/"data/geo3k_test-00000-of-00001.parquet"),("k12_test",ROOT/"data/k12_test-00000-of-00001.parquet")]
N=32
RADIUS=8
LUT=np.array([int(i).bit_count() for i in range(256)],dtype=np.uint8)
x=np.arange(N,dtype=np.float32)
DCT=np.cos((2*x[None,:]+1)*x[:,None]*np.pi/(2*N)).astype(np.float32)
DCT[0]*=np.sqrt(1/N)
DCT[1:]*=np.sqrt(2/N)


def visible(im):
    rgba=im.convert("RGBA")
    bg=Image.new("RGBA",rgba.size,(255,255,255,255))
    return Image.alpha_composite(bg,rgba).convert("RGB")


def phash(payload):
    with Image.open(io.BytesIO(payload)) as im:
        gray=visible(im).convert("L").resize((N,N),Image.Resampling.LANCZOS)
        a=np.asarray(gray,dtype=np.float32)
    coeff=DCT@a@DCT.T
    low=coeff[:8,:8].reshape(-1)
    med=np.median(low[1:])
    bits=low>med
    value=0
    for bit in bits: value=(value<<1)|int(bit)
    return value


def rgb_hash(payload):
    with Image.open(io.BytesIO(payload)) as im:
        rgb=visible(im)
        h=hashlib.sha256(f"{rgb.width}x{rgb.height}:".encode()); h.update(rgb.tobytes())
    return h.hexdigest()


def iter_rows(path):
    idx=0
    for batch in pq.ParquetFile(path).iter_batches(batch_size=64,columns=["images","source"]):
        for imgs,source in zip(batch.column(0).to_pylist(),batch.column(1).to_pylist()):
            idx+=1
            yield idx,source,imgs[0]["bytes"]


def main():
    hashes=[]; labels=[]; visible_set=set(); counts=Counter()
    for split,path in TESTS:
        for idx,source,payload in iter_rows(path):
            counts[split]+=1
            hashes.append(phash(payload)); labels.append(f"{split}:{idx}:{source}")
            visible_set.add(rgb_hash(payload))
        print(f"indexed {split}: {counts[split]}",flush=True)
    hold=np.asarray(hashes,dtype=np.uint64)
    candidates=[]; sources=Counter(); rows=0
    for idx,source,payload in iter_rows(CLEAN):
        rows+=1
        if rgb_hash(payload) in visible_set:
            raise RuntimeError(f"Exact visible pixel overlap remains at clean train row {idx}")
        value=np.uint64(phash(payload))
        xor=np.bitwise_xor(value,hold)
        dist=LUT[xor.view(np.uint8).reshape(-1,8)].sum(axis=1,dtype=np.uint8)
        best=int(dist.min())
        if best<=RADIUS:
            for match in np.flatnonzero(dist==best):
                candidates.append({"clean_train_row":idx,"source":source,"holdout":labels[int(match)],"phash_hamming":best})
                sources[source]+=1
        if rows%2048==0: print(f"screened clean train rows: {rows}",flush=True)
    out=REPORT/"perceptual_phash_candidates.jsonl"
    out.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in candidates),encoding="utf-8")
    summary={
      "method":"64-bit pHash (32x32 grayscale DCT low-frequency 8x8 median threshold) on visible image after alpha compositing over white",
      "threshold":RADIUS,"holdout_rows":dict(counts),"holdout_unique_visible_rgb":len(visible_set),
      "clean_train_rows_screened":rows,"candidate_pairs":len(candidates),
      "unique_train_rows":len({r["clean_train_row"] for r in candidates}),
      "candidate_pairs_by_source":dict(sources),
      "candidate_pairs_by_holdout":dict(Counter(r["holdout"].split(":")[0] for r in candidates)),
      "candidate_pairs_by_distance":dict(Counter(r["phash_hamming"] for r in candidates)),
      "candidate_file":str(out),
      "policy":"pHash candidates require subsequent visible-pixel SSIM/ink-IoU validation; no automatic removal."
    }
    (REPORT/"perceptual_phash_audit.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))


if __name__=="__main__": main()
