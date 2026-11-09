import json

import pytest

from src.data.intergps_index import Geometry
from src.training.protocol_v3 import SYSTEM_PROMPT
from src.training.rl_data import build_items, load_training_rows, placebo_mapping
from tests._mini_release import make_release, mini_config

pytest.importorskip("PIL")


def test_placebo_mapping_is_a_deterministic_derangement_over_images():
    rows = [{"sample_id": f"s{i}", "image_pixel_sha256": f"p{i // 2}"} for i in range(10)]  # pairs share an image
    first = placebo_mapping(rows, 20261109)
    assert first == placebo_mapping(rows, 20261109)
    pixel = {r["sample_id"]: r["image_pixel_sha256"] for r in rows}
    assert sorted(first) == sorted(first.values())
    assert all(pixel[a] != pixel[b] for a, b in first.items())
    with pytest.raises(ValueError):
        placebo_mapping([{"sample_id": "a", "image_pixel_sha256": "x"}, {"sample_id": "b", "image_pixel_sha256": "x"}], 1)


def test_items_keep_private_metadata_out_of_the_prompt(tmp_path):
    make_release(tmp_path)
    config = mini_config(tmp_path, "rl_v5")
    rows, index = load_training_rows(config, tmp_path)
    items, mapping = build_items(config, rows, index, tmp_path)
    assert len(items) == 4 and all(k == v for k, v in mapping.items())
    item = items[0]
    # the prompt is exactly the shared system prompt plus the cleaned problem text: nothing private leaks in
    assert item["prompt"] == [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": "Find x."}]
    assert "image" in item and Geometry.from_json(item["geom_reward"]).original_id == item["original_id"]
    assert item["gold_reward"] == item["gold_own"]


def test_placebo_and_blind_arms(tmp_path):
    make_release(tmp_path)
    placebo = mini_config(tmp_path, "rl_v5_placebo")
    rows, index = load_training_rows(placebo, tmp_path)
    items, mapping = build_items(placebo, rows, index, tmp_path)
    assert all(i["meta_source"] != i["sample_id"] for i in items)
    assert all(Geometry.from_json(i["geom_reward"]).original_id != i["original_id"] for i in items)
    assert all(i["reference_answer"] == str(int(i["sample_id"].split(":")[1]) + 2) for i in items)  # answers stay own
    blind = mini_config(tmp_path, "rl_blind")
    items, _ = build_items(blind, rows, index, tmp_path)
    assert all("image" not in i for i in items)


def test_gates_fail_closed(tmp_path):
    rows = make_release(tmp_path)
    config = mini_config(tmp_path)
    image = tmp_path / rows[0]["image_path"]
    image.write_bytes(image.read_bytes() + b"x")
    with pytest.raises(ValueError, match="image bytes changed"):
        load_training_rows(config, tmp_path)


def test_annotation_link_mismatch_fails_closed(tmp_path):
    make_release(tmp_path)
    path = tmp_path / "data/project3_audit/intergps_annotations.jsonl"
    records = [json.loads(x) for x in path.read_text().splitlines()]
    records[0]["image_pixel_sha256"] = "f" * 64
    path.write_text("".join(json.dumps(r) + "\n" for r in records))
    with pytest.raises(ValueError, match="does not match InterGPS"):
        load_training_rows(mini_config(tmp_path), tmp_path)
