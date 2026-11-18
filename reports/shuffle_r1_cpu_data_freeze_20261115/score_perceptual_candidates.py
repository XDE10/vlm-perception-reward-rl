"""Score dHash near-duplicate candidates with visible-pixel structural metrics."""
import io, json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from PIL import Image

ROOT=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
CLEAN=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-decontaminated/train.parquet")
REPORT=Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
SIZE=256


def visible(payload):
    with Image.open(io.BytesIO(payload)) as im:
        rgba=im.convert("RGBA")
        bg=Image.new("RGBA",rgba.size,(255,255,255,255))
        return Image.alpha_composite(bg,rgba).convert("RGB")


def normalized(payload):
    im=visible(payload)
    w,h=im.size
    scale=min(SIZE/w,SIZE/h)
    nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    canvas=Image.new("RGB",(SIZE,SIZE),(255,255,255))
    canvas.paste(im,((SIZE-nw)//2,(SIZE-nh)//2))
    return np.asarray(canvas.convert("L"),dtype=np.float32)/255.0, (w,h)


def metrics(a,b):
    diff=a-b
    mae=float(np.abs(diff).mean())
    mse=float(np.square(diff).mean())
    mx,my=float(a.mean()),float(b.mean())
    vx,vy=float(a.var()),float(b.var())
    cov=float(((a-mx)*(b-my)).mean())
    c1=0.01**2
    c2=0.03**2
    ssim=((2*mx*my+c1)*(2*cov+c2))/((mx*mx+my*my+c1)*(vx+vy+c2))
    out={"mae":mae,"mse":mse,"ssim_global":float(ssim)}
    for threshold in [0.90,0.95,0.98]:
        x=a<threshold; y=b<threshold
        union=int(np.logical_or(x,y).sum())
        inter=int(np.logical_and(x,y).sum())
        out[f"ink_iou_{threshold}"]=float(inter/union) if union else 1.0
    return out


def main():
    candidates=[json.loads(line) for line in (REPORT/"perceptual_overlap_candidates.jsonl").open()]
    train_ids={r["clean_train_row"] for r in candidates}
    holdout_ids=defaultdict(set)
    for r in candidates:
        split,index,source=r["holdout"].split(":",2)
        holdout_ids[split].add(int(index))
    train_data={}
    for batch_no,batch in enumerate(pq.ParquetFile(CLEAN).iter_batches(batch_size=128,columns=["images","source"])):
        base=batch_no*128
        for j,(imgs,source) in enumerate(zip(batch.column(0).to_pylist(),batch.column(1).to_pylist())):
            row=base+j+1
            if row in train_ids: train_data[row]=(imgs[0]["bytes"],source)
        if len(train_data)==len(train_ids): break
    test_data={}
    for split,filename in [("geo3k_test","geo3k_test-00000-of-00001.parquet"),("k12_test","k12_test-00000-of-00001.parquet")]:
        needed=holdout_ids.get(split,set())
        if not needed: continue
        for batch_no,batch in enumerate(pq.ParquetFile(ROOT/"data"/filename).iter_batches(batch_size=64,columns=["images","source"])):
            base=batch_no*64
            for j,(imgs,source) in enumerate(zip(batch.column(0).to_pylist(),batch.column(1).to_pylist())):
                row=base+j+1
                if row in needed: test_data[f"{split}:{row}:{source}"]=imgs[0]["bytes"]
            if len([k for k in test_data if k.startswith(split+":")])==len(needed): break

    scored=[]
    cache={}
    for candidate in candidates:
        train_row=candidate["clean_train_row"]
        holdout=candidate["holdout"]
        if train_row not in cache: cache[train_row]=normalized(train_data[train_row][0])
        test_key=holdout
        if test_key not in cache: cache[test_key]=normalized(test_data[test_key])
        a,asize=cache[train_row]; b,bsize=cache[test_key]
        score=metrics(a,b)
        scored.append({
            **candidate,
            "train_size":list(asize),
            "holdout_size":list(bsize),
            "aspect_ratio_delta":abs(asize[0]/asize[1]-bsize[0]/bsize[1]),
            **score,
        })
    scored.sort(key=lambda r:(-r["ssim_global"],-r["ink_iou_0.95"],r["mae"]))
    (REPORT/"perceptual_candidate_scores.jsonl").write_text(
        "".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in scored),encoding="utf-8")
    summary={
        "candidate_pairs":len(scored),
        "unique_train_rows":len(train_ids),
        "metrics":"visible RGB after alpha composite over white; letterboxed to 256x256; global SSIM, MAE, ink IoU at grayscale thresholds 0.90/0.95/0.98",
        "threshold_counts":{
            "ssim_ge_0.99":sum(r["ssim_global"]>=0.99 for r in scored),
            "ssim_ge_0.97":sum(r["ssim_global"]>=0.97 for r in scored),
            "ssim_ge_0.95":sum(r["ssim_global"]>=0.95 for r in scored),
            "iou95_ge_0.90":sum(r["ink_iou_0.95"]>=0.90 for r in scored),
            "iou95_ge_0.80":sum(r["ink_iou_0.95"]>=0.80 for r in scored),
        },
        "top20":scored[:20],
        "bottom20":scored[-20:],
        "policy":"Metrics prioritize candidates; no row is automatically excluded by this score file. Inspect high-confidence rows and borderline cases visually.",
    }
    (REPORT/"perceptual_candidate_scores.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="top20" and k!="bottom20"},indent=2,ensure_ascii=False))
    print("TOP 10")
    for row in scored[:10]: print(row["clean_train_row"],row["holdout"],row["dhash_hamming"],round(row["ssim_global"],5),round(row["ink_iou_0.95"],5),round(row["mae"],5))
    print("BOTTOM 10")
    for row in scored[-10:]: print(row["clean_train_row"],row["holdout"],row["dhash_hamming"],round(row["ssim_global"],5),round(row["ink_iou_0.95"],5),round(row["mae"],5))


if __name__=="__main__": main()
