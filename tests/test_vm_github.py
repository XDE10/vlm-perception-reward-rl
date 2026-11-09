"""VM-side results push (D37) against a local bare repository: no network, explicit temporary paths only.

These tests also run on the Colab VM during preflight, where a real credential may sit at
/content/gh_credentials; they never use that default and never contact GitHub.
"""
import json
import shutil
import subprocess
import tarfile

import pytest

from scripts.colab import vm_github

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="needs git")
PAT = "ghp_" + "Q" * 36


def git(*args, cwd):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args], cwd=str(cwd),
                          check=True, capture_output=True, text=True).stdout.strip()


def world(tmp_path, credentials=True):
    origin = tmp_path / "origin.git"
    git("init", "-q", "--bare", str(origin), cwd=tmp_path)
    src = tmp_path / "src"
    src.mkdir()
    git("init", "-q", cwd=src)
    (src / "README.md").write_text("code\n")
    git("add", "-A", cwd=src)
    git("commit", "-q", "-m", "base", cwd=src)
    git("push", "-q", str(origin), "HEAD:refs/heads/master", cwd=src)
    creds = tmp_path / "gh_credentials"
    if credentials:
        creds.write_text("https://tester:%s@github.com\n" % PAT)
        creds.chmod(0o600)
    run_id = "preflight-20261109T120000Z-abcd"
    request = {"run_id": run_id, "task": "preflight",
               "github": {"mode": "auto", "url": "file://%s" % origin, "branch": "results/" + run_id,
                          "base_commit": git("rev-parse", "HEAD", cwd=src), "day": "20261109",
                          "credentials": str(creds), "task": "preflight", "max_file_mb": 0.001}}
    return origin, request


def archive(tmp_path, run_id, files):
    stage = tmp_path / "stage" / run_id
    for rel, data in files.items():
        (stage / rel).parent.mkdir(parents=True, exist_ok=True)
        (stage / rel).write_bytes(data)
    path = tmp_path / (run_id + ".results.tar.gz")
    with tarfile.open(path, "w:gz") as tar:
        tar.add(stage, arcname=run_id)
    return path


def test_without_a_request_block_nothing_happens(tmp_path):
    assert vm_github.settings({"run_id": "x"}) is None
    assert vm_github.check(tmp_path, {"run_id": "x"})["mode"] == "off"
    assert vm_github.push(tmp_path, {"run_id": "x"}, tmp_path / "none.tar.gz")["attempted"] is False


def test_missing_credentials_are_reported_without_network(tmp_path):
    _, request = world(tmp_path, credentials=False)
    info = vm_github.check(tmp_path / "vm", request)
    assert info["credentials_present"] is False and not info["ok"] and "no credential file" in info["reason"]
    assert not (tmp_path / "vm" / "github").exists()  # nothing was prepared, nothing was fetched


def test_check_then_push_commits_on_the_run_commit(tmp_path):
    origin, request = world(tmp_path)
    run_id = request["run_id"]
    info = vm_github.check(tmp_path / "vm", request)
    assert info["ok"] and info["push_access"] and info["credentials_mode"] == "0o600"
    assert subprocess.run(["git", "--git-dir", str(origin), "rev-parse", "--verify", "-q", "results/" + run_id],
                          capture_output=True).returncode != 0  # the dry run created nothing
    path = archive(tmp_path, run_id, {"summary.md": b"ok\n", "logs/step.log": ("url?token=%s\n" % PAT).encode(),
                                      "big.jsonl": b"x" * 4096})
    result = vm_github.push(tmp_path / "vm", request, path, overall="passed", prior_check=info)
    assert result["ok"] and result["attempted"] and result["skipped_large"] == 1 and result["redacted"] == 1
    prefix = "reports/colab_runs_20261109/%s/" % run_id
    names = git("ls-tree", "-r", "--name-only", "results/" + run_id, cwd=origin).splitlines()
    assert {prefix + n for n in ["summary.md", "logs/step.log", "SKIPPED_LARGE_FILES.txt", "REDACTIONS_VM.txt"]} <= set(names)
    assert "README.md" in names and prefix + "big.jsonl" not in names
    assert PAT not in git("show", "results/%s:%slogs/step.log" % (run_id, prefix), cwd=origin)
    author, subject = git("log", "-1", "--format=%an|%s", "results/" + run_id, cwd=origin).split("|", 1)
    assert author == vm_github.VM_NAME and subject.endswith("overall=passed [pushed from the Colab VM]")
    assert git("rev-parse", "results/%s^" % run_id, cwd=origin) == request["github"]["base_commit"]
    assert result["commit"] == git("rev-parse", "results/" + run_id, cwd=origin)


def test_unknown_base_commit_is_a_reported_failure(tmp_path):
    _, request = world(tmp_path)
    request["github"]["base_commit"] = "0" * 40
    info = vm_github.check(tmp_path / "vm", request)
    assert not info["ok"] and "could not fetch the run's commit" in info["reason"]
    result = vm_github.push(tmp_path / "vm", request, tmp_path / "missing.tar.gz")
    assert result["attempted"] is False and not result["ok"]
    json.dumps(result)  # serialisable for done.json
