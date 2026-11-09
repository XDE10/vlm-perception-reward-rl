# Provenance copy (2026-11-09): the script that wrote errata.json, run once in the Kiro sandbox.
# Paths are the sandbox paths it ran with: SHA-verified public pinned sources (Geometry3K wrapper parquets,
# InterGPS train.zip and logic forms) and calibration.json from results/preflight-20261109T122305Z-e6cd.
# VERDICTS holds my visual judgements (AI check, not a human gold label). Not part of the package or tests.
"""Build reports/certified_fact_errata_20261109/errata.json from (a) my visual verdicts, (b) public pinned sources,
(c) the calibration of preflight-20261109T122305Z-e6cd. Reads train and the two flagged validation rows only."""
import hashlib
import io
import json
import zipfile

import pyarrow.parquet as pq
from PIL import Image

RUN = "/projects/sandbox/.work/scratch/r3/preflight-20261109T122305Z-e6cd/calibration/calibration.json"
OUT = "/projects/sandbox/vlm-perception-reward-rl/reports/certified_fact_errata_20261109/errata.json"
cal = json.load(open(RUN))
measured = {(e["sample_id"], e["certified"]): e for split in ("train", "validation")
            for e in cal[split]["raw_false_refutations"]}
loo = {sid for rel in cal["train"]["loo"]["relations"].values() for sid in rel["residual_ids"]}

# (sample ids sharing one image, certified fact, class, what the drawing shows, likely intended fact or None)
VERDICTS = [
    (["train:425", "train:598", "train:1471", "train:1488", "train:1957", "train:2090"], "Perpendicular((A,C),(C,E))",
     "certified_fact_error", "Right triangle ABC with the right angle marked at C (between CA and CB) and the altitude CE "
     "to AB marked at E. CE is not perpendicular to AC; the drawn angle ACE is 60 degrees (angle A is printed as 30).",
     "Perpendicular((A,C),(B,C))"),
    (["train:1598"], "Perpendicular((B,C),(C,D))", "certified_fact_error",
     "Right triangle with the right angle marked at C (between CA and CB) and the altitude CD to AB marked at D. "
     "CD is not perpendicular to CB.", "Perpendicular((A,C),(B,C))"),
    (["train:1251"], "Perpendicular((K,L),(L,M))", "certified_fact_error",
     "Right angle marked at L (between LJ and LK) and the altitude LM to JK marked at M. LM is not perpendicular to LK.",
     "Perpendicular((J,L),(K,L))"),
    (["train:335"], "Perpendicular((T,U),(U,W))", "certified_fact_error",
     "Right angle marked at U (between UV and UT) and the altitude UW to VT marked at W. UW is not perpendicular to UT.",
     "Perpendicular((T,U),(U,V))"),
    (["train:1729"], "Perpendicular((A,F),(F,H))", "certified_fact_error",
     "Two separate right triangles: ABC (right angle at A) and GFH (right angle at F). A and F belong to different "
     "triangles and no segment AF is drawn; the right angle at F is between FG and FH.", "Perpendicular((F,G),(F,H))"),
    (["train:919"], "Perpendicular((Q,T),(R,S))", "certified_fact_error",
     "RS and QT carry matching arrowheads (parallel marks); the drawn angle between them is 0.75 degrees.",
     "Parallel((R,S),(Q,T))"),
    (["train:1783"], "PointLiesOnCircle(A,Circle(B))", "certified_fact_error",
     "Chords AC and DE intersect at B inside the circle; B is not the centre (the centre is not labelled). The same "
     "holds for the certified facts with C, D and E on Circle(B).", None),
    (["train:1218", "train:380"], "PointLiesOnLine(E,(B,C))", "coordinate_error",
     "Parallelogram ABCD with the height DE drawn to side BC; E is on BC as certified. InterGPS coordinates put E at "
     "normalised distance 0.0707 from line BC (threshold 0.06).", None),
    (["train:2049", "train:329"], "PointLiesOnCircle(G,Circle(B))", "coordinate_error",
     "G is where line AC meets circle B, so it lies on circle B as certified (consistent with the printed diameters and "
     "the answer FG = 14). InterGPS coordinates disagree by 40 percent of the radius.", None),
    (["train:523"], "PointLiesOnCircle(U,Circle)", "coordinate_error",
     "U is drawn on the circle as certified; the coordinates deviate by 0.155 of the radius (threshold 0.15).", None),
    (["train:1542"], "Parallel((A,B),(C,D))", "coordinate_error",
     "AB and CD carry matching arrowheads and E-H-G, F on CD and H-F-I are drawn as certified; the InterGPS coordinates "
     "of this diagram are inconsistent with all four certified facts (gated).", None),
    (["train:1593"], "PointLiesOnCircle(A,Circle(D))", "coordinate_error",
     "BA and BC are tangent to circle D at A and C; both points are drawn on the circle as certified (gated).", None),
    (["train:1878"], "PointLiesOnCircle(J,Circle(K))", "coordinate_error",
     "J and L are drawn on circle K as certified; the coordinates deviate by 0.17 and 0.20 of the radius (gated).", None),
    (["validation:165"], "Perpendicular((B,D),(C,D))", "unverifiable_no_point_labels",
     "The diagram prints no point letters (only x, y, z, 12 and 4), so the certified point names cannot be read from "
     "the image. The coordinates put BD and CD on one line (0.22 degrees) and AC at 47 degrees to BC.", None),
    (["validation:179"], "PointLiesOnCircle(N,Circle)", "coordinate_error",
     "N is drawn on the circle as certified; the coordinates deviate by 0.65 of the radius (gated).", None),
]


def pixel_hash(data):
    image = Image.open(io.BytesIO(data)).convert("RGB")
    return hashlib.sha256(str(image.size).encode() + b"\0" + image.tobytes()).hexdigest()


rows = {"train": pq.read_table("/projects/sandbox/.work/scratch/g3k/train-00000-of-00001.parquet").to_pylist(),
        "validation": pq.read_table("/projects/sandbox/.work/scratch/g3k/validation-00000-of-00001.parquet").to_pylist()}
z = zipfile.ZipFile("/projects/sandbox/.work/scratch/g3k/train.zip")
by_hash = {}
for name in z.namelist():
    if name.endswith("/img_diagram.png"):
        by_hash.setdefault(pixel_hash(z.read(name)), []).append(int(name.split("/")[1]))
diagram = json.load(open("/projects/sandbox/.work/scratch/g3k/lf/logic_forms/diagram_logic_forms_annot.json"))
entries = []
for samples, fact, kind, drawn, intended in VERDICTS:
    split, index = samples[0].split(":")
    image = rows[split][int(index)]["images"][0]
    digest = pixel_hash(image["bytes"] if isinstance(image, dict) else image)
    for other in samples[1:]:
        s, i = other.split(":")
        im = rows[s][int(i)]["images"][0]
        assert pixel_hash(im["bytes"] if isinstance(im, dict) else im) == digest, (other, samples[0])
    ids = sorted(by_hash.get(digest, [])) if split == "train" else []
    forms = [f for f in diagram[str(ids[0])]["diagram_logic_forms"]
             if f.startswith(("Perpendicular", "Parallel", "PointLiesOn"))] if ids else None
    m = measured.get((samples[0], fact))
    entries.append({"sample_ids": samples, "image_pixel_sha256": digest, "intergps_ids": ids,
                    "certified_fact": fact, "class": kind, "drawn": drawn, "likely_intended": intended,
                    "oracle_reason": m["reason"] if m else None, "measured": m["measured"] if m else None,
                    "loo_residual": any(s in loo for s in samples) and kind != "unverifiable_no_point_labels",
                    "intergps_diagram_forms": forms})
doc = {"schema": "p3-certified-fact-errata-v1", "date": "2026-11-09",
       "source_run": "preflight-20261109T122305Z-e6cd (calibration/calibration.json, commit 7afad4a42150)",
       "method": "Kiro viewed each image (public pinned Geometry3K wrapper rows) next to the certified fact and the "
                 "measured coordinates. This is an AI visual check, not a human gold label; the approved release is "
                 "unchanged (D42).",
       "entries": entries}
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(doc, handle, ensure_ascii=False, indent=1)
    handle.write("\n")
print(len(entries), "entries;", sum(len(e["sample_ids"]) for e in entries), "rows")
for e in entries:
    print("%-34s %-30s %-28s ids %s loo %s" % (",".join(e["sample_ids"])[:34], e["certified_fact"], e["class"],
                                               e["intergps_ids"], e["loo_residual"]))
