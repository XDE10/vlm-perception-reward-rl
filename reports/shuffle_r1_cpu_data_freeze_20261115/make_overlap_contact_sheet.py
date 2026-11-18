import io, json
from pathlib import Path
import pyarrow.parquet as pq
from PIL import Image, ImageDraw

ROOT=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
CLEAN=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381-decontaminated/train.parquet")
REPORT=Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
candidates=[json.loads(line) for line in (REPORT/"perceptual_overlap_candidates.jsonl").open()]
selected=[]
seen=set()
for distance in [0,1,2,3,4,5]:
    for row in candidates:
        if row["dhash_hamming"]==distance and row["clean_train_row"] not in seen:
            selected.append(row); seen.add(row["clean_train_row"])
            if len(selected)>=24: break
    if len(selected)>=24: break

def visible(payload):
    with Image.open(io.BytesIO(payload)) as im:
        rgba=im.convert("RGBA")
        bg=Image.new("RGBA",rgba.size,(255,255,255,255))
        return Image.alpha_composite(bg,rgba).convert("RGB")

train_targets={row["clean_train_row"]:row for row in selected}
train_images={}
for batch_no,batch in enumerate(pq.ParquetFile(CLEAN).iter_batches(batch_size=128,columns=["images","source"])):
    base=batch_no*128
    for j,(items,source) in enumerate(zip(batch.column(0).to_pylist(),batch.column(1).to_pylist())):
        index=base+j+1
        if index in train_targets: train_images[index]=(items[0]["bytes"],source)
    if len(train_images)==len(train_targets): break

test_images={}
for split,filename in [("geo3k_test","geo3k_test-00000-of-00001.parquet"),("k12_test","k12_test-00000-of-00001.parquet")]:
    needed={row["holdout"] for row in selected if row["holdout"].startswith(split+":")}
    if not needed: continue
    for batch_no,batch in enumerate(pq.ParquetFile(ROOT/"data"/filename).iter_batches(batch_size=64,columns=["images","source"])):
        base=batch_no*64
        for j,(items,source) in enumerate(zip(batch.column(0).to_pylist(),batch.column(1).to_pylist())):
            index=base+j+1
            label=f"{split}:{index}:{source}"
            if label in needed: test_images[label]=items[0]["bytes"]
        if needed.issubset(test_images): break

if set(train_images)!=set(train_targets) or {r["holdout"] for r in selected}-set(test_images):
    raise RuntimeError("Contact sheet source rows missing")
W,H=1000,330
sheet=Image.new("RGB",(W,H*len(selected)),"white")
draw=ImageDraw.Draw(sheet)
for i,row in enumerate(selected):
    y=i*H
    left=visible(train_images[row["clean_train_row"]][0])
    right=visible(test_images[row["holdout"]])
    left.thumbnail((460,280)); right.thumbnail((460,280))
    sheet.paste(left,(10,y+35)); sheet.paste(right,(510,y+35))
    draw.text((10,y+5),f'TRAIN row={row["clean_train_row"]} src={row["source"]} dh={row["dhash_hamming"]}',fill="black")
    draw.text((510,y+5),f'TEST {row["holdout"]}',fill="black")
sheet.save(REPORT/"perceptual_overlap_contact_sheet.jpg",quality=88)
print(f"saved {len(selected)} pairs; {sheet.size}")
