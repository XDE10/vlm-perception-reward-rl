"""Quantify how much direct RGB conversion changes transparent MMRL30k images."""
import io,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
from PIL import Image

ROOT=Path("/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381")
REPORT=Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
SPLITS={
 "train":["data/train-00000-of-00003.parquet","data/train-00001-of-00003.parquet","data/train-00002-of-00003.parquet"],
 "geo3k_train":["data/geo3k_train-00000-of-00000.parquet"],
 "geo3k_test":["data/geo3k_test-00000-of-00001.parquet"],
 "k12_train":["data/k12_train-00000-of-00000.parquet"],
 "k12_test":["data/k12_test-00000-of-00001.parquet"],
}


def iter_payloads(path):
 for batch in pq.ParquetFile(path).iter_batches(batch_size=32,columns=["images","source"]):
  for items,source in zip(batch.column(0).to_pylist(),batch.column(1).to_pylist()):
   yield items[0]["bytes"],source


def main():
 summary={}
 for split,files in SPLITS.items():
  counts=Counter()
  by_source=defaultdict(Counter)
  rows=0
  for rel in files:
   for payload,source in iter_payloads(ROOT/rel):
    rows+=1
    with Image.open(io.BytesIO(payload)) as im:
     has_alpha=("A" in im.getbands()) or ("transparency" in im.info)
     if not has_alpha:
      counts["no_alpha"]+=1
      by_source[source]["no_alpha"]+=1
      continue
     counts["alpha_or_transparency"]+=1
     by_source[source]["alpha_or_transparency"]+=1
     old=np.asarray(im.convert("RGB"),dtype=np.int16)
     rgba=im.convert("RGBA")
     bg=Image.new("RGBA",rgba.size,(255,255,255,255))
     new=np.asarray(Image.alpha_composite(bg,rgba).convert("RGB"),dtype=np.int16)
     diff=np.abs(old-new)
     pixel_diff=np.any(diff>5,axis=2)
     delta=float(diff.mean())
     diff_ratio=float(pixel_diff.mean())
     old_black=float(np.all(old==0,axis=2).mean())
     new_white=float(np.all(new==255,axis=2).mean())
     if diff_ratio>0.01:
      counts["visually_changed_over_1pct"]+=1
      by_source[source]["visually_changed_over_1pct"]+=1
     if diff_ratio>0.5:
      counts["visually_changed_over_50pct"]+=1
      by_source[source]["visually_changed_over_50pct"]+=1
     if old_black>0.9:
      counts["old_rgb_over_90pct_black"]+=1
      by_source[source]["old_rgb_over_90pct_black"]+=1
     counts["delta_sum"]+=delta
     counts["diff_ratio_sum"]+=diff_ratio
  alpha=counts["alpha_or_transparency"]
  summary[split]={
   "rows":rows,
   "alpha_or_transparency":alpha,
   "visually_changed_over_1pct":counts["visually_changed_over_1pct"],
   "visually_changed_over_50pct":counts["visually_changed_over_50pct"],
   "old_rgb_over_90pct_black":counts["old_rgb_over_90pct_black"],
   "mean_mae_over_alpha_images":counts["delta_sum"]/alpha if alpha else 0,
   "mean_changed_pixel_fraction_over_alpha_images":counts["diff_ratio_sum"]/alpha if alpha else 0,
   "by_source":{k:dict(v) for k,v in by_source.items()},
  }
  print(split,summary[split],flush=True)
 result={
  "method":"For every image with alpha/transparency, compare old PIL convert('RGB') with alpha-composite over opaque white at native size. Difference pixel if any RGB channel absolute delta >5.",
  "splits":summary,
  "interpretation":"Quantifies image rendering changes, not model accuracy. The correct rendering policy is to composite transparency over white before resize.",
 }
 (REPORT/"alpha_rendering_delta.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("saved",REPORT/"alpha_rendering_delta.json")


if __name__=="__main__": main()
