# Provenance copy (2026-11-09): how the spot-check samples of spot_check.md were drawn and rendered.
# Run from the repository root (PYTHONPATH=. python reports/cfgeo_20261109/render_spot_check.py ...) with the pinned
# wrapper parquets under --sources; images go to --out (never into
# the repository, they contain the source diagrams).
#   round 1: --seed 20261109                       (CF-Geo built with editor v2)
#   round 2: --seed 20261110 --exclude-round1      (CF-Geo rebuilt with editor v3, the round-1 items excluded)
import argparse
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

from src.evaluation.cfgeo import rebuild
from src.evaluation.public_sources import read_wrapper

ROUND1 = ["validation:264", "validation:96", "test:412", "test:121", "validation:223", "test:328", "test:234",
          "validation:258", "validation:46", "test:372", "validation:151", "validation:279", "test:414", "test:1",
          "test:540", "validation:242", "test:140", "test:128", "test:492", "test:230", "test:541", "test:273", "test:8",
          "test:323", "validation:134", "validation:269", "test:586", "test:63", "validation:238", "test:361"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="reports/cfgeo_20261109/cfgeo.json")
    parser.add_argument("--sources", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--exclude-round1", action="store_true")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    items = json.loads(Path(args.spec).read_text(encoding="utf-8"))["items"]
    if args.exclude_round1:
        items = [i for i in items if i["id"] not in set(ROUND1)]
    sample = random.Random(args.seed).sample(items, 30)
    rows = {s: read_wrapper(Path(args.sources) / ("geometry3k/data/%s-00000-of-00001.parquet" % s), with_images=True)
            for s in ("validation", "test")}
    Path(args.out).mkdir(parents=True, exist_ok=True)
    for n, item in enumerate(sample, 1):
        split, number = item["id"].split(":")
        source = rows[split][int(number)]["image"]
        panels = [("original", source), ("k=1", rebuild(item, source, "k1")), ("k=2", rebuild(item, source, "k2"))]
        scale = 2 if source.width < 420 else 1
        w, h = source.width * scale, source.height * scale
        canvas = Image.new("RGB", (3 * w + 20, h + 18), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        for i, (name, image) in enumerate(panels):
            canvas.paste(image.resize((w, h), Image.LANCZOS), (i * (w + 10), 18))
            draw.text((i * (w + 10) + 4, 2), "#%d %s %s" % (n, item["id"], name), fill=(200, 0, 0))
        canvas.save(Path(args.out) / ("%02d_%s.png" % (n, item["id"].replace(":", "_"))))
        print(n, item["id"], [label["from"] + " -> " + label["to"] for label in item["k2"]["labels"]])


if __name__ == "__main__":
    main()
