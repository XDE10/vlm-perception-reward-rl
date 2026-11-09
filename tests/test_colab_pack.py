import hashlib
import json
import tarfile
from pathlib import Path

import pytest

from scripts.colab.pack_private_data import build_pack, extract_pack, plan_entries, verify_tree
from tests._mini_release import make_release

pytest.importorskip("PIL")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_repo(tmp_path):
    """Mini data root plus a repo directory whose ledger anchors the non-release files."""
    data_parent = tmp_path / "src_data"
    make_release(data_parent)
    data_root = data_parent / "data"
    (data_root / "synthesis_mock").mkdir()
    (data_root / "synthesis_mock/cache.jsonl").write_text('{"table": "jobs"}\n', encoding="utf-8")
    repo = tmp_path / "repo"
    repo.mkdir()
    ledger_files = []
    for rel in ["data/portable_release/manifest.json", "data/project3_audit/intergps_annotations.jsonl",
                "data/synthesis_mock/cache.jsonl"]:
        path = data_parent / rel
        ledger_files.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha(path)})
    ledger_files.append({"path": "data/tokenizers/Qwen2.5-7B-Instruct/tokenizer.json", "bytes": 3, "sha256": "0" * 64})
    (repo / "migration_manifest.json").write_text(json.dumps({"files": ledger_files}), encoding="utf-8")
    return data_root, repo


def test_plan_covers_release_rows_images_and_anchors(tmp_path):
    data_root, repo = make_repo(tmp_path)
    entries, missing = plan_entries(data_root, repo)
    anchors = {e["path"]: e["anchor"] for e in entries}
    assert anchors["data/portable_release/manifest.json"] == "ledger"
    assert anchors["data/portable_release/project3_train_fact_pruned.jsonl"] == "release"
    assert sum(a == "row" for a in anchors.values()) == 4
    assert anchors["data/project3_audit/intergps_annotations.jsonl"] == "ledger"
    assert anchors["data/synthesis_mock/cache.jsonl"] == "ledger"
    assert missing == ["data/tokenizers/Qwen2.5-7B-Instruct/tokenizer.json"]  # optional and absent: reported, not fatal


def test_pack_is_deterministic_extracts_and_verifies(tmp_path):
    data_root, repo = make_repo(tmp_path)
    first = build_pack(data_root, tmp_path / "out1", repo)
    second = build_pack(data_root, tmp_path / "out2", repo)
    assert first["sha256"] == second["sha256"] and first["content_sha256"] == second["content_sha256"]
    with tarfile.open(first["pack"]) as tar:
        names = tar.getnames()
    assert names[0] == "PACK_MANIFEST.json" and all(n.startswith("data/") for n in names[1:])
    vm_repo = tmp_path / "vm_repo"
    vm_repo.mkdir()
    (vm_repo / "migration_manifest.json").write_text((repo / "migration_manifest.json").read_text(), encoding="utf-8")
    extract_pack(first["pack"], vm_repo)
    result = verify_tree(vm_repo)
    assert result["ok"], result["problems"]
    image = next((vm_repo / "data/images").iterdir())
    image.write_bytes(image.read_bytes() + b"tamper")
    tampered = verify_tree(vm_repo)
    assert not tampered["ok"] and any("changed" in p for p in tampered["problems"])


def test_local_tampering_fails_before_packing(tmp_path):
    data_root, repo = make_repo(tmp_path)
    annotations = data_root / "project3_audit/intergps_annotations.jsonl"
    annotations.write_text(annotations.read_text() + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="data verification failed"):
        build_pack(data_root, tmp_path / "out", repo)


def test_unsafe_pack_members_are_rejected(tmp_path):
    bad = tmp_path / "bad.tar.gz"
    with tarfile.open(bad, "w:gz") as tar:
        payload = tmp_path / "x"
        payload.write_text("x")
        tar.add(payload, arcname="../escape.txt")
    with pytest.raises(ValueError, match="unsafe"):
        extract_pack(bad, tmp_path / "vm")
