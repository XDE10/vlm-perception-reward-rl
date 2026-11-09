"""Synthetic miniature release (manifest, rows, images, InterGPS records) for CPU tests.

Mirrors the field contract of data/portable_release so the real loaders and
gates run unchanged; contents are synthetic and never used for results.
"""
import hashlib
import json
from pathlib import Path

from tests._fixtures import synthetic_record


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_release(root, n=4, duplicate_image=False):
    from PIL import Image, ImageDraw

    root = Path(root)
    release = root / "data/portable_release"
    images = root / "data/images"
    release.mkdir(parents=True)
    images.mkdir(parents=True)
    rows, records = [], []
    for i in range(n):
        oid = str(9000 + i)
        image = Image.new("RGB", (84, 56), "white")
        draw = ImageDraw.Draw(image)
        shade = 0 if duplicate_image and i == 1 else i
        draw.line((4, 50, 80, 50), fill=(shade * 40, 0, 0), width=2)
        draw.line((4, 50, 40, 6), fill=(0, 0, 0), width=2)
        path = images / f"{oid}.png"
        image.save(path)
        pixel = hashlib.sha256(str(image.size).encode() + b"\0" + image.tobytes()).hexdigest()
        rows.append({
            "sample_id": f"train:{i}",
            "original_id": oid,
            "split": "train",
            "problem": "<image>Find x.",
            "reference_answer": str(i + 2),
            "image_path": path.relative_to(root).as_posix(),
            "image_sha256": _sha(path),
            "image_pixel_sha256": pixel,
            "model_perception": "<perception>Length(A,B)=3; PointLiesOnLine(C,(A,B))</perception>",
            "certified_positive_tokens": ["Length(A,B)=3", "PointLiesOnLine(C,(A,B))"],
            "certified_negative_tokens": [],
            "training_approved": True,
            "perception_reward_enabled": True,
            "perception_reward_mode": "sparse_certified_v4",
            "model_input_whitelist": ["problem", "image_path"],
            "model_target_whitelist": ["model_perception"],
        })
        record = synthetic_record(original_id=oid, points={"A": (0, 0), "B": (10, 0), "C": (5, 0), "D": (5, 8)},
                                  lines=["AB", "AC", "BC", "CD"])
        record["image_pixel_sha256"] = pixel
        records.append(record)
    train = release / "project3_train_fact_pruned.jsonl"
    train.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    (release / "reserved_dev_ids_never_train.json").write_text(json.dumps({"sample_ids": ["validation:0"]}), encoding="utf-8")
    manifest = {
        "approved_training_files": [train.name],
        "approved_evaluation_files": [],
        "protected_dev_ids_file": "reserved_dev_ids_never_train.json",
        "files": {train.name: _sha(train)},
    }
    (release / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    audit = root / "data/project3_audit"
    audit.mkdir(parents=True)
    (audit / "intergps_annotations.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return rows


def mini_config(root, arm="rl_v5", seed=1, smoke=None):
    from src.training.rl_config import resolve

    repo = Path(__file__).resolve().parents[1]
    config = resolve(repo / "configs/experiments/rl_v3.json", arm, seed, smoke=smoke or {"max_steps": 1}, n_rows=4)
    config["output_root"] = str(Path(root) / "runs")
    config["output_dir"] = str(Path(root) / "runs" / config["run_name"])
    return config
