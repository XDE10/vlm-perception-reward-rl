"""Score pHash candidates with visible-pixel structural metrics."""
import io,json
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
        rgba=im.convert("RGBA"); bg=Image.new("RGBA",rgba.size,(255,255,255,255))
        return Image.alpha_composite(bg,rgba).convert("RGB")


def normalized(payload):
    im=visible(payload); w,h=im.size
    scale=min(SIZE/w,SIZE/h); nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    canvas=Image.new("RGB",(SIZE,SIZE),(255,255,255)); canvas.paste(im,((SIZE-nw)//2,(SIZE-nh)//2))
    return np.asarray(canvas.convert("L"),dtype=np.float32)/255.0,(w,h)


def metrics(a,b):
    diff=a-b; mae=float(np.abs(diff).mean()); mse=float(np.square(diff).mean())
    mx,my=float(a.mean()),float(b.mean()); vx,vy=float(a.var()),float(b.var())
    cov=float(((a-mx)*(b-my)).mean()); c1=0.01**2; c2=0.03**2
    ssim=((2*mx*my+c1)*(2*cov+c2))/((mx*mx+my*my+c1)*(vx+vy+c2))
    out={"mae":mae,"mse":mse,"ssim_global":float(ssim)}
    for t in [0.90,0.95,0.98]:
        x=a<t; y=b<t; union=int(np.logical_or(x,y).sum()); inter=int(np.logical_and(x,y).sum())
        out[f"ink_iou_{t}"]=float(inter/union) if union else 1.0
    return out


def main():
    candidates=[json.loads(line) for line in (REPORT/"perceptual_phash_candidates.jsonl").open()]
    train_ids={r["clean_train_row"] for r in candidates}
    holdout_ids=defaultdict(set)
    for r in candidates:
        split,index,source=r["holdout"].split(":",2); holdout_ids[split].add(int(index))
    train_data={}
    for bi,b in enumerate(pq.ParquetFile(CLEAN).iter_batches(batch_size=128,columns=["images","source"])):
        base=bi*128
        for j,(imgs,source) in enumerate(zip(b.column(0).to_pylist(),b.column(1).to_pylist())):
            idx=base+j+1
            if idx in train_ids: train_data[idx]=(imgs[0]["bytes"],source)
        if len(train_data)==len(train_ids): break
    test_data={}
    for split,filename in [("geo3k_test","geo3k_test-00000-of-00001.parquet"),("k12_test","k12_test-00000-of-00001.parquet")]:
        needed=holdout_ids.get(split,set())
        if not needed: continue
        for bi,b in enumerate(pq.ParquetFile(ROOT/"data"/filename).iter_batches(batch_size=64,columns=["images","source"])):
            base=bi*64
            for j,(imgs,source) in enumerate(zip(b.column(0).to_pylist(),b.column(1).to_pylist())):
                idx=base+j+1; label=f"{split}:{idx}:{source}"
                if label in {r["holdout"] for r in candidates if r["holdout"].startswith(split+":")}:
                    test_data[label]=imgs[0]["bytes"]
            if len([k for k in test_data if k.startswith(split+":")])==len(needed): break
    cache={}; scored=[]
    for r in candidates:
        tr=r["clean_train_row"]; ho=r["holdout"]
        if tr not in cache: cache[tr]=normalized(train_data[tr][0])
        if ho not in cache: cache[ho]=normalized(test_data[ho])
        a,asz=cache[tr]; b,bsz=cache[ho]
        scored.append({**r,"train_size":list(asz),"holdout_size":list(bsz),
            "aspect_ratio_delta":abs(asz[0]/asz[1]-bsz[0]/bsz[1]),**metrics(a,b)})
    scored.sort(key=lambda x:(-x["ssim_global"],-x["ink_iou_0.95"],x["mae"]))
    (REPORT/"perceptual_phash_scores.jsonl").write_text(
        "".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in scored),encoding="utf-8")
    summary={
        "candidate_pairs":len(scored),"unique_train_rows":len(train_ids),
        "threshold_counts":{
            "ssim_ge_0.99_and_iou95_ge_0.90":sum(r["ssim_global"]>=0.99 and r["ink_iou_0.95"]>=0.9 for r in scored),
            "ssim_ge_0.99_and_iou95_ge_0.80":sum(r["ssim_global"]>=0.99 and r["ink_iou_0.95"]>=0.8 for r in scored),
            "ssim_ge_0.97_and_iou95_ge_0.80":sum(r["ssim_global"]>=0.97 and r["ink_iou_0.95"]>=0.8 for r in scored),
            "ssim_ge_0.95_and_iou95_ge_0.80":sum(r["ssim_global"]>=0.95 and r["ink_iou_0.95"]>=0.8 for r in scored),
        },
        "by_source_strict":dict(__import__("collections").Counter(r["source"] for r in scored if r["ssim_global"]>=0.97 and r["ink_iou_0.95"]>=0.8)),
        "by_holdout_strict":dict(__import__("collections").Counter(r["holdout"].split(":")[0] for r in scored if r["ssim_global"]>=0.97 and r["ink_iou_0.95"]>=0.8)),
        "policy":"Structural scores are a conservative near-duplicate screen, not semantic proof. Manually inspect uncertain cases; no row automatically removed.",
    }
    (REPORT/"perceptual_phash_scores.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print("TOP 10")
    for r in scored[:10]: print(r["clean_train_row"],r["source"],r["holdout"],r["phash_hamming"],round(r["ssim_global"],5),round(r["ink_iou_0.95"],5),round(r["mae"],5))
    print("BOTTOM 10")
    for r in scored[-10:]: print(r["clean_train_row"],r["source"],r["holdout"],r["phash_hamming"],round(r["ssim_global"],5),round(r["ink_iou_0.95"],5),round(r["mae"],5))


if __name__=="__main__": main()
