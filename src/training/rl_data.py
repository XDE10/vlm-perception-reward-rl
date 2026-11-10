"""Build GRPO training rows for protocol v3 from the approved release only.

Model-visible fields: the protocol prompt (problem text) and, unless the arm is
blind, the image. Everything else (reference answer, certified facts, InterGPS
geometry) travels in private columns that TRL passes to reward functions only.

Fail-closed checks: release manifest gate (``load_approved``), v4 reward-row
contract, protected dev ids, per-row image byte SHA, and agreement between the
release pixel hash and the InterGPS record (confirms the row-annotation link).
"""
import hashlib
import json
import random
from pathlib import Path

from src.data.approved_training_inputs import load_approved
from src.data.intergps_index import load_index
from src.training.perception_reward_v4 import validate_reward_rows
from src.training.protocol_v3 import training_prompt, variant_for_protocol


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def placebo_mapping(rows, seed):
    """Deterministic derangement: every row gets another row whose image pixels differ."""
    ids = sorted(r["sample_id"] for r in rows)
    pixel = {r["sample_id"]: r["image_pixel_sha256"] for r in rows}
    if len(set(pixel.values())) < 2:
        raise ValueError("placebo mapping needs at least two distinct images")
    perm = ids[:]
    rng = random.Random(seed)
    rng.shuffle(perm)

    def bad(i):
        return pixel[ids[i]] == pixel[perm[i]]

    for _ in range(20):
        changed = False
        for i in range(len(ids)):
            if not bad(i):
                continue
            order = list(range(len(ids)))
            rng.shuffle(order)
            for j in order:
                if j != i and pixel[ids[i]] != pixel[perm[j]] and pixel[ids[j]] != pixel[perm[i]]:
                    perm[i], perm[j] = perm[j], perm[i]
                    changed = True
                    break
        if not any(bad(i) for i in range(len(ids))):
            return dict(zip(ids, perm))
        if not changed:
            break
    raise ValueError("could not build a placebo derangement with distinct images")


def load_training_rows(config, root="."):
    root = Path(root)
    data = config["data"]
    manifest = root / data["manifest"]
    rows = load_approved(manifest, data["train_file"])
    validate_reward_rows(rows)
    release = json.loads(manifest.read_text(encoding="utf-8"))
    protected_file = release.get("protected_dev_ids_file")
    if protected_file:
        protected = set(json.loads((manifest.parent / protected_file).read_text(encoding="utf-8"))["sample_ids"])
        overlap = protected & {r["sample_id"] for r in rows}
        if overlap:
            raise ValueError(f"protected dev ids in training rows: {sorted(overlap)[:5]}")
    limit = config.get("smoke", {}).get("limit_rows")
    if limit:
        rows = sorted(rows, key=lambda r: r["sample_id"])[: int(limit)]
    index = load_index(root / data["intergps_annotations"], [r["original_id"] for r in rows])
    for r in rows:
        image = root / r["image_path"]
        if Path(r["image_path"]).is_absolute() or not image.is_file():
            raise ValueError(f"image path invalid: {r['image_path']}")
        if sha256_file(image) != r["image_sha256"]:
            raise ValueError(f"image bytes changed: {r['image_path']}")
        geometry = index[str(r["original_id"])]
        if r.get("image_pixel_sha256") and geometry.image_pixel_sha256 and r["image_pixel_sha256"] != geometry.image_pixel_sha256:
            raise ValueError(f"release row {r['sample_id']} does not match InterGPS record {r['original_id']}")
    return rows, index


def build_items(config, rows, index, root=".", load_images=True):
    from PIL import Image

    arm = config["arm"]
    variant = variant_for_protocol(config["protocol"])  # the prompt follows the protocol the config names (S4: P1)
    by_id = {r["sample_id"]: r for r in rows}
    mapping = placebo_mapping(rows, config["placebo_seed"]) if arm["metadata"] == "placebo" else {s: s for s in by_id}
    items = []
    for r in sorted(rows, key=lambda x: x["sample_id"]):
        source = by_id[mapping[r["sample_id"]]]
        item = {
            "prompt": training_prompt(r["problem"], variant),
            "sample_id": r["sample_id"],
            "original_id": str(r["original_id"]),
            "reference_answer": str(r["reference_answer"]),
            "gold_own": json.dumps(r["certified_positive_tokens"], ensure_ascii=False),
            "neg_own": json.dumps(r["certified_negative_tokens"], ensure_ascii=False),
            "geom_own": index[str(r["original_id"])].to_json(),
            "meta_source": source["sample_id"],
            "gold_reward": json.dumps(source["certified_positive_tokens"], ensure_ascii=False),
            "neg_reward": json.dumps(source["certified_negative_tokens"], ensure_ascii=False),
            "geom_reward": index[str(source["original_id"])].to_json(),
        }
        if arm["train_with_image"] and load_images:
            item["image"] = Image.open(Path(root) / r["image_path"]).convert("RGB")
        items.append(item)
    return items, mapping


def prompt_length_report(items, processor, max_prompt_tokens):
    """Render every prompt with the real processor; fail rather than truncate."""
    from trl.data_utils import prepare_multimodal_messages

    lengths = []
    for item in items:
        images = [item["image"]] if "image" in item else None
        messages = prepare_multimodal_messages(item["prompt"], images=images) if images else item["prompt"]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        encoded = processor(text=[text], images=images, return_tensors="pt")
        lengths.append(int(encoded["input_ids"].shape[1]))
    report = {"prompts": len(lengths), "max_tokens": max(lengths), "mean_tokens": sum(lengths) / len(lengths),
              "limit": max_prompt_tokens}
    if report["max_tokens"] > max_prompt_tokens:
        raise ValueError(f"prompt budget exceeded: {report}")
    return report


__all__ = ["build_items", "load_training_rows", "placebo_mapping", "prompt_length_report"]
