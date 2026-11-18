import io,json
from pathlib import Path
import pyarrow.parquet as pq
from PIL import Image,ImageDraw

ROOT=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
CLEAN=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-decontaminated/train.parquet")
REPORT=Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
scores=[json.loads(x) for x in (REPORT/"perceptual_candidate_scores.jsonl").open()]
selected=[r for r in scores if r["ssim_global"]>=0.99 and r["ink_iou_0.95"]<0.90]
train_ids={r["clean_train_row"] for r in selected}
train={}
for bi,b in enumerate(pq.ParquetFile(CLEAN).iter_batches(batch_size=128,columns=["images"])):
    base=bi*128
    for j,items in enumerate(b.column(0).to_pylist()):
        idx=base+j+1
        if idx in train_ids: train[idx]=items[0]["bytes"]
    if len(train)==len(train_ids): break

tests={}
for split,fn in [("geo3k_test","geo3k_test-00000-of-00001.parquet"),("k12_test","k12_test-00000-of-00001.parquet")]:
    needed={r["holdout"] for r in selected if r["holdout"].startswith(split+":")}
    if not needed: continue
    for bi,b in enumerate(pq.ParquetFile(ROOT/"data"/fn).iter_batches(batch_size=64,columns=["images","source"])):
        base=bi*64
        for j,(items,src) in enumerate(zip(b.column(0).to_pylist(),b.column(1).to_pylist())):
            label=f"{split}:{base+j+1}:{src}"
            if label in needed: tests[label]=items[0]["bytes"]
        if needed.issubset(tests): break

def vis(payload):
    with Image.open(io.BytesIO(payload)) as im:
        rgba=im.convert("RGBA")
        bg=Image.new("RGBA",rgba.size,(255,255,255,255))
        return Image.alpha_composite(bg,rgba).convert("RGB")

W,H=1000,330
sheet=Image.new("RGB",(W,H*len(selected)),"white")
d=ImageDraw.Draw(sheet)
for i,r in enumerate(selected):
    y=i*H
    a=vis(train[r["clean_train_row"]]); b=vis(tests[r["holdout"]])
    a.thumbnail((460,280)); b.thumbnail((460,280))
    sheet.paste(a,(10,y+35)); sheet.paste(b,(510,y+35))
    d.text((10,y+5),f'TRAIN {r["clean_train_row"]} SSIM={r["ssim_global"]:.4f} IoU={r["ink_iou_0.95"]:.3f}',fill="black")
    d.text((510,y+5),f'TEST {r["holdout"]}',fill="black")
sheet.save(REPORT/"perceptual_borderline_contact_sheet.jpg",quality=88)
print(f"borderline pairs={len(selected)}, unique train={len(train_ids)}")
