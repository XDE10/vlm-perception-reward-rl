"""One evaluation code path for every model and every condition (docs/plan/S3设计_20261109.md sections 1-4).

An *item* is a dict with ``id``, ``problem``, ``answer`` (reference), ``cluster`` (pixel hash of the source image),
``image`` (PIL, the original diagram) and optionally:

* ``answer_set``: references that all count as correct (CF-Geo rounded items, S3 design section 3.1);
* ``gold_tokens``, ``negative_tokens``, ``geometry``: certified facts for E1 (perception), scored on the original image;
* ``cf`` and ``cf_images``: the CF-Geo record (src/evaluation/cfgeo.py) and its rebuilt "k1" / "k2" images.

Conditions: ``original``, ``blind`` (no image), ``swap`` (the image of another item, fixed pairing), ``cf_k1`` and
``cf_k2``. Decoding is greedy (src/evaluation/generate_v3.py) with batches of 32 in the given item order, so every model
is evaluated in exactly the same batches: on GPU the ViT output depends on the batch composition (S2 acceptance,
section 3.4). Answers are graded by the training verifier; a reference with ``answer_set`` is correct when the answer
matches any member.
"""
import hashlib
import json
from pathlib import Path

CONDITIONS = ("original", "blind", "swap", "cf_k1", "cf_k2")
BATCH_SIZE = 32
MAX_NEW_TOKENS = 1024
HARNESS_VERSION = "eval-harness-v1-20261109"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inputs(item, condition, swap_items):
    """(image or None, reference) for one item under one condition."""
    from src.evaluation.cfgeo import references

    if condition in ("cf_k1", "cf_k2"):
        variant = condition[3:]
        return item["cf_images"][variant], references(item["cf"], variant)
    if condition == "original":
        image = item["image"]
    elif condition == "blind":
        image = None
    elif condition == "swap":
        image = swap_items[item["id"]]["image"]
    else:
        raise ValueError("unknown condition %r; known: %s" % (condition, ", ".join(CONDITIONS)))
    return image, {"answer": item["answer"], "answer_set": item.get("answer_set")}


def run_condition(model, processor, items, condition, verifier, v5_config=None, prompt_variant="p0",
                  max_new_tokens=MAX_NEW_TOKENS, batch_size=BATCH_SIZE, swap=None, progress=None, model_name=None):
    """Generate, grade and annotate one record per item. ``swap`` maps item id -> id of the item whose image is shown."""
    from src.evaluation.generate_v3 import generate, score, verify_answers

    by_id = {item["id"]: item for item in items}
    swap_items = {i: by_id[j] for i, j in (swap or {}).items()} if condition == "swap" else {}
    if condition == "swap":
        missing = [item["id"] for item in items if item["id"] not in swap_items]
        if missing:
            raise ValueError("no swap partner for %s" % missing[:5])
        same = [i for i, partner in swap_items.items() if partner["cluster"] == by_id[i]["cluster"]]
        if same:
            raise ValueError("swapped images must differ from the item's own image: %s" % same[:5])
    requests, references = [], {}
    for item in items:
        image, reference = _inputs(item, condition, swap_items)
        rid = "%s|%s" % (condition, item["id"])
        perception = condition == "original"
        references[rid] = {"answer": reference["answer"], "answer_set": reference.get("answer_set"),
                           "gold_tokens": list(item.get("gold_tokens") or []) if perception else [],
                           "negative_tokens": list(item.get("negative_tokens") or []) if perception else [],
                           "geometry": item.get("geometry") if perception else None}
        requests.append({"id": rid, "problem": item["problem"], "image": image})
    results = generate(model, processor, requests, max_new_tokens=max_new_tokens, batch_size=batch_size,
                       progress=progress, prompt_variant=prompt_variant)
    scored = score(results, references, verifier, v5_config)
    if condition == "cf_k2":  # "old answer": the model gave the answer of the unedited diagram
        old = verify_answers([r["answer"]["extracted"] for r in scored],
                             [{"answer": by_id[r["id"].split("|", 1)[1]]["answer"]} for r in scored], verifier)
    for n, record in enumerate(scored):
        item = by_id[record["id"].split("|", 1)[1]]
        record.update(condition=condition, item=item["id"], cluster=item["cluster"], model=model_name,
                      gold_count=len(references[record["id"]]["gold_tokens"]), harness=HARNESS_VERSION)
        if condition == "swap":
            record["shown_image_of"] = swap_items[item["id"]]["id"]
        if condition == "cf_k2":
            record["old_answer"] = bool(old[n].get("correct")) and not record["answer"]["correct"]
    return scored


def summarize(records):
    """Per-condition numbers for reports (single model; comparisons use src/evaluation/stats.py)."""
    n = len(records)
    if not n:
        return {"n": 0}
    out = {"n": n, "accuracy": sum(r["answer"]["correct"] for r in records) / n,
           "protocol_ok_rate": sum(bool(r["protocol_ok"]) for r in records) / n,
           "format_rate": sum(r["format"] for r in records) / n,
           "budget_exhausted_rate": sum(bool(r["budget_exhausted"]) for r in records) / n,
           "no_answer_rate": sum(r["answer"]["extracted"] is None for r in records) / n,
           "clusters": len({r["cluster"] for r in records})}
    scored = [r for r in records if r.get("v5") is not None]
    if scored:
        tp = sum(r["v5"]["tp"] for r in scored)
        false = sum(r["v5"]["false"] for r in scored)
        unknown = sum(r["v5"]["unknown"] for r in scored)
        claims = tp + false + unknown
        gold = sum(r["gold_count"] for r in scored)
        out["e1"] = {"items": len(scored), "verified_precision": tp / (tp + false) if tp + false else None,
                     "recall": tp / gold if gold else None, "claims_per_output": claims / len(scored),
                     "unknown_share": unknown / claims if claims else None,
                     "false_share": false / claims if claims else None,
                     "over_cap_rate": sum(r["v5"]["status"] == "over_cap" for r in scored) / len(scored)}
    if any("old_answer" in r for r in records):
        out["old_answer_rate"] = sum(bool(r.get("old_answer")) for r in records) / n
    return out


# ---- items ---------------------------------------------------------------------------------------------------------

def _row_image(root, row):
    from PIL import Image

    path = Path(root) / row["image_path"]
    if Path(row["image_path"]).is_absolute() or not path.is_file():
        raise ValueError("image path invalid: %s" % row["image_path"])
    if sha256_file(path) != row["image_sha256"]:
        raise ValueError("image bytes changed: %s" % row["image_path"])
    return Image.open(path).convert("RGB")


def _release_item(root, row, index):
    from src.evaluation.public_sources import image_pixel_sha256

    image = _row_image(root, row)
    pixel = image_pixel_sha256(image)
    if row.get("image_pixel_sha256") and row["image_pixel_sha256"] != pixel:
        raise ValueError("release row %s: pixel hash differs from its image" % row["sample_id"])
    geometry = index[str(row["original_id"])]
    if geometry.image_pixel_sha256 and geometry.image_pixel_sha256 != pixel:
        raise ValueError("release row %s does not match InterGPS record %s" % (row["sample_id"], row["original_id"]))
    return {"id": row["sample_id"], "problem": row["problem"], "answer": str(row["reference_answer"]), "cluster": pixel,
            "image": image, "gold_tokens": list(row["certified_positive_tokens"]),
            "negative_tokens": list(row.get("certified_negative_tokens") or []), "geometry": geometry}


def val82_items(root, config):
    """The approved evaluation rows (E1), in sample_id order, with image byte and pixel checks."""
    from src.data.intergps_index import load_index

    manifest = Path(root) / config["data"]["manifest"]
    release = json.loads(manifest.read_text(encoding="utf-8"))
    rows = []
    for name in release.get("approved_evaluation_files", []):
        path = manifest.parent / name
        digest = release["files"][name]
        digest = digest.get("sha256") if isinstance(digest, dict) else digest
        if sha256_file(path) != digest:
            raise ValueError("approved evaluation file changed: %s" % name)
        rows += [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not rows:
        raise ValueError("the release lists no approved evaluation rows")
    if any(not r.get("evaluation_approved") for r in rows):
        raise ValueError("an evaluation row is not evaluation_approved")
    rows.sort(key=lambda r: r["sample_id"])
    index = load_index(Path(root) / config["data"]["intergps_annotations"], [r["original_id"] for r in rows])
    return [_release_item(root, row, index) for row in rows]


def train_items(root, config, n=None):
    """Approved training rows (gated by src/training/rl_data.load_training_rows), first ``n`` by sample_id."""
    from src.training.rl_data import load_training_rows

    rows, index = load_training_rows(dict(config, smoke={}), root)
    rows = sorted(rows, key=lambda r: r["sample_id"])[:n]
    return [_release_item(root, row, index) for row in rows]


def wrapper_items(sources, split, ids=None):
    """Items from a pinned Geometry3K wrapper parquet (``<split>:<row>`` ids); ``ids`` keeps that order."""
    from src.evaluation.public_sources import read_wrapper

    rows = read_wrapper(Path(sources) / ("geometry3k/data/%s-00000-of-00001.parquet" % split), with_images=True)
    items = [{"id": "%s:%d" % (split, n), "problem": row["problem"], "answer": str(row["answer"]), "cluster": row["pixel"],
              "image": row["image"]} for n, row in enumerate(rows)]
    if ids is None:
        return items
    by_id = {item["id"]: item for item in items}
    return [by_id[i] for i in ids]


def cfgeo_items(spec, sources):
    """CF-Geo items (in specification order) with the original image and both rebuilt edits, pixel-checked."""
    from src.evaluation.cfgeo import rebuild

    spec = json.loads(Path(spec).read_text(encoding="utf-8")) if not isinstance(spec, dict) else spec
    cache, out = {}, []
    for record in spec["items"]:
        split = record["id"].split(":")[0]
        if split not in cache:
            cache[split] = {item["id"]: item for item in wrapper_items(sources, split)}
        base = cache[split][record["id"]]
        if base["cluster"] != record["pixel"]:
            raise ValueError("%s: the pinned image differs from the CF-Geo specification" % record["id"])
        item = dict(base, answer=record["answer"], cf=record,
                    cf_images={v: rebuild(record, base["image"], v) for v in ("k1", "k2")})
        if record.get("answer_set"):
            item["answer_set"] = list(record["answer_set"])
        out.append(item)
    return out


def load_model(model_path, config, adapter=None, device="cuda"):
    """Base model plus an optional LoRA adapter (kept unmerged: exactly the policy that was trained, no bf16 merge
    rounding), with the experiment's image resolution, in eval mode."""
    import torch
    from transformers import AutoProcessor

    from src.training.hf_compat import vision_model_class

    m = config["model"]
    processor = AutoProcessor.from_pretrained(str(model_path), max_pixels=m["max_pixels"], min_pixels=m["min_pixels"])
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    model = vision_model_class().from_pretrained(str(model_path), dtype=dtype, attn_implementation=m["attn_implementation"])
    if adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, str(adapter))
    return model.to(device).eval(), processor


def write_jsonl(path, records):
    """Predictions without images; one JSON object per line."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


__all__ = ["BATCH_SIZE", "CONDITIONS", "HARNESS_VERSION", "MAX_NEW_TOKENS", "cfgeo_items", "load_model", "run_condition",
           "summarize", "train_items", "val82_items", "wrapper_items", "write_jsonl"]
