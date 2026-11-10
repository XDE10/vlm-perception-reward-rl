import json
from pathlib import Path

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


def test_s4_config_builds_p1_prompts(tmp_path):
    """S3 chose P1 (configs/experiments/s3_decisions_20261110.json): the S4 config names the P1 protocol and every
    training prompt carries the P1 sentence; the older rl_v3.json keeps P0 so recorded hashes stay reproducible."""
    from src.training.protocol_v3 import P1_SUFFIX, protocol_id

    make_release(tmp_path)
    s4 = mini_config(tmp_path, "rl_v5", experiment="configs/experiments/rl_v3_p1_20261110.json")
    assert s4["protocol"] == protocol_id("p1")
    rows, index = load_training_rows(s4, tmp_path)
    items, _ = build_items(s4, rows, index, tmp_path, load_images=False)
    assert all(i["prompt"] == [{"role": "system", "content": SYSTEM_PROMPT},
                               {"role": "user", "content": "Find x.\n\n" + P1_SUFFIX}] for i in items)
    p0_items, _ = build_items(mini_config(tmp_path, "rl_v5"), rows, index, tmp_path, load_images=False)
    assert p0_items[0]["prompt"][1]["content"] == "Find x."


def test_answer_only_protocol_cannot_train(tmp_path):
    from src.training.protocol_v3 import protocol_id
    from src.training.rl_config import resolve

    repo = Path(__file__).resolve().parents[1]
    base = json.loads((repo / "configs/experiments/rl_v3_p1_20261110.json").read_text(encoding="utf-8"))
    (tmp_path / "arms.json").write_text((repo / "configs/experiments/arms.json").read_text(encoding="utf-8"))
    for protocol, message in [(protocol_id("answer_only"), "cannot be used for training"), ("v9", "unknown protocol")]:
        (tmp_path / "exp.json").write_text(json.dumps(dict(base, protocol=protocol)), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            resolve(tmp_path / "exp.json", "rl_v5", 1)


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
