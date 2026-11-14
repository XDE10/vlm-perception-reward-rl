"""Unit checks of the launcher's local helpers: credential redaction, inbox diff, part sizes, git tree parsing."""
import hashlib
import json

import pytest

from scripts.colab.local_tools import inbox_diff, main, parse_tree, redact_text, redact_tree


def test_redaction_removes_tokens_but_keeps_ordinary_text():
    line = ("[colab] Upload failed: 504 Server Error: Gateway Timeout for url: https://x.colab.dev/api/contents/c/p3/"
            "inbox/a.part001?authuser=0&colab-runtime-proxy-token=abc.DEF-123_xyz")
    text, count = redact_text(line)
    assert count == 1 and "abc.DEF-123_xyz" not in text
    assert text.endswith("authuser=0&colab-runtime-proxy-token=REDACTED")
    for secret in ["Authorization: Bearer ya29.a0AfH6SMBx-very-secret", "refresh 1//0gAbCdEfGhIjKlMnOpQrStUvWxYz",
                   "ghp_" + "a" * 36, "hf_" + "B" * 34, "https://h/p?access_token=s3cr3t&x=1"]:
        redacted, n = redact_text(secret)
        assert n >= 1 and "REDACTED" in redacted, secret
    unchanged = "max_new_tokens=6 monkey=3 smoke max_steps=1,num_generations=2 token budget 1600"
    assert redact_text(unchanged) == (unchanged, 0)


def test_redaction_covers_credentials_in_urls_and_is_idempotent():
    for secret, gone in [("https://XDE10:ghp_%s@github.com" % ("a" * 36), "ghp_"),
                         ("https://x:github_pat_11ABCDEFG0_%s@github.com/o/r.git" % ("b" * 40), "github_pat_11"),
                         ("fatal: https://user:p4ss@example.org/repo", "p4ss"),
                         ("token github_pat_11ABCDEFG0_%s in a log" % ("c" * 40), "github_pat_11")]:
        text, count = redact_text(secret)
        assert count >= 1 and gone not in text, (secret, text)
        assert redact_text(text) == (text, 0), text  # a second pass (VM push, then _local/) changes nothing
    plain = "https://github.com/XDE10/vlm-perception-reward-rl/tree/results/x and git@github.com:o/r.git"
    assert redact_text(plain) == (plain, 0)


def test_redact_tree_reports_and_skips_binary_suffixes(tmp_path):
    (tmp_path / "_local").mkdir()
    (tmp_path / "_local" / "upload.log").write_text("u?colab-runtime-proxy-token=T1\nok\n", encoding="utf-8")
    (tmp_path / "weights.bin").write_bytes(b"token=keep-binary")
    (tmp_path / "summary.md").write_text("中文 摘要 token=T2", encoding="utf-8")
    changed = redact_tree(tmp_path)
    assert changed == {"_local/upload.log": 1, "summary.md": 1}
    assert (tmp_path / "weights.bin").read_bytes() == b"token=keep-binary"
    assert (tmp_path / "summary.md").read_text(encoding="utf-8") == "中文 摘要 token=REDACTED"


def test_inbox_diff_flags_missing_and_damaged_parts(tmp_path):
    good, bad, gone = tmp_path / "a.part000", tmp_path / "a.part001", tmp_path / "request.json"
    for path, data in [(good, b"x" * 10), (bad, b"y" * 10), (gone, b"{}")]:
        path.write_bytes(data)
    uploads = tmp_path / "uploads.tsv"
    uploads.write_text("".join("%s\t%s\n" % (p, p.name) for p in [good, bad, gone]), encoding="utf-8")
    listing = {good.name: [10, hashlib.sha256(b"x" * 10).hexdigest()],
               bad.name: [10, hashlib.sha256(b"y" * 9 + b"z").hexdigest()]}
    log = tmp_path / "inbox.log"
    log.write_text("noise\n[p3] INBOX " + json.dumps(listing) + "\n", encoding="utf-8")
    stale = inbox_diff(uploads, log)
    assert [line.split("\t")[1] for line in stale] == [bad.name, gone.name]


def test_parse_tree_reads_git_ls_tree_z_output(tmp_path):
    raw = (b"100644 blob " + b"a" * 40 + b"\tdocs/\xe4\xb8\xad\xe6\x96\x87.md\0"
           b"100755 blob " + b"b" * 40 + b"\tcolab/launch.sh\0")
    (tmp_path / "tree.bin").write_bytes(raw)
    assert parse_tree(tmp_path / "tree.bin") == [["colab/launch.sh", "100755", "b" * 40],
                                                  ["docs/中文.md", "100644", "a" * 40]]
    (tmp_path / "sub.bin").write_bytes(b"160000 commit " + b"c" * 40 + b"\tvendor/x\0")
    with pytest.raises(ValueError, match="unsupported"):
        parse_tree(tmp_path / "sub.bin")


@pytest.mark.parametrize("part_mb", ["0", "0.01", "64"])
def test_make_request_rejects_unusable_part_sizes(tmp_path, part_mb):
    code = tmp_path / "code.tar.gz"
    code.write_bytes(b"code")
    with pytest.raises(SystemExit, match="part size"):
        main(["make-request", "--task", "preflight", "--run-id", "r", "--code", str(code), "--commit", "c" * 40,
              "--staging", str(tmp_path / "s"), "--uploads", str(tmp_path / "u.tsv"),
              "--code-uploads", str(tmp_path / "c.tsv"), "--part-mb", part_mb])
