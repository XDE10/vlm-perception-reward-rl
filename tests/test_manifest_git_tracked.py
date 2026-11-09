import hashlib
import json
import shutil
import subprocess

import pytest

from tools.build_migration_manifest import build_git_tracked

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not available")


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def test_git_tracked_mode_refreshes_code_and_keeps_data_entries(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("/data/*\n", encoding="utf8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/a.py").write_text("new", encoding="utf8")
    (tmp_path / "src/b.py").write_text("same", encoding="utf8")
    (tmp_path / "src/new.py").write_text("added", encoding="utf8")
    entry = lambda path, text, **extra: {"path": path, "bytes": len(text), "sha256": sha(text),  # noqa: E731
                                          "source_sha256": sha(text), "changed_for_portability": False, **extra}
    previous = {
        "project": "p",
        "files": [entry(".gitignore", "/data/*\n"), entry("src/a.py", "old"), entry("src/b.py", "same", added_in="x"),
                  entry("data/big.bin", "payload-not-present-here"), entry("src/deleted.py", "gone")],
        "documentation_updates": [{"date": "2026-11-08"}],
    }
    manifest_path = tmp_path / "migration_manifest.json"
    manifest_path.write_text(json.dumps(previous), encoding="utf8")
    manifest, stats = build_git_tracked(manifest_path, "2026-11-09", "stage1", "test", root=tmp_path)
    by_path = {e["path"]: e for e in manifest["files"]}
    assert by_path["data/big.bin"] == previous["files"][3]  # untracked payload kept verbatim
    assert by_path["src/a.py"]["sha256"] == sha("new") and by_path["src/a.py"]["source_sha256"] == sha("old")
    assert by_path["src/a.py"]["updated_in"] == "stage1" and by_path["src/a.py"]["changed_for_portability"]
    assert by_path["src/b.py"] == previous["files"][2]
    assert by_path["src/new.py"]["added_in"] == "stage1"
    assert "src/deleted.py" not in by_path
    update = manifest["documentation_updates"][-1]
    assert update["dropped_tracked_paths"] == ["src/deleted.py"] and update["untracked_entries_kept_verbatim"] == 1
    assert stats == {"files": 5, "git_visible": 4, "changed": 1, "added": 1, "kept_untracked": 1, "dropped": 1}
    # a second refresh in the same stage accumulates into one ledger entry
    manifest_path.write_text(json.dumps(manifest), encoding="utf8")
    (tmp_path / "src/later.py").write_text("later", encoding="utf8")
    again, _ = build_git_tracked(manifest_path, "2026-11-09", "stage1", "test", root=tmp_path)
    entry_paths = [c["path"] for c in again["documentation_updates"][-1]["changes"]]
    assert entry_paths == ["src/a.py", "src/later.py", "src/new.py"]
    assert again["documentation_updates"][-1]["dropped_tracked_paths"] == ["src/deleted.py"]
    # another stage on the same date gets its own entry and leaves the earlier stage's entry untouched
    manifest_path.write_text(json.dumps(again), encoding="utf8")
    (tmp_path / "src/b.py").write_text("changed in stage2", encoding="utf8")
    third, _ = build_git_tracked(manifest_path, "2026-11-09", "stage2", "test", root=tmp_path)
    assert [(u.get("date"), u.get("label")) for u in third["documentation_updates"]] == [
        ("2026-11-08", None), ("2026-11-09", "stage1"), ("2026-11-09", "stage2")]
    assert third["documentation_updates"][1] == again["documentation_updates"][-1]
    assert [c["path"] for c in third["documentation_updates"][-1]["changes"]] == ["src/b.py"]
