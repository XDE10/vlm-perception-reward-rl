"""Local helpers for colab/launch.sh (standard library only, python3 >= 3.8).

    python3 -m scripts.colab.local_tools make-request ...
    python3 -m scripts.colab.local_tools inbox-diff <uploads.tsv> <kernel_inbox output>
    python3 -m scripts.colab.local_tools status-line <status.json>
    python3 -m scripts.colab.local_tools field <json> <dotted.key>
    python3 -m scripts.colab.local_tools parts <done.json>
    python3 -m scripts.colab.local_tools join <done.json> <parts dir> <out file>
    python3 -m scripts.colab.local_tools extract <archive> <dest dir>
"""
import argparse
import hashlib
import json
import re
import sys
import tarfile
import time
from pathlib import Path

from scripts.colab.common import REQUEST_SCHEMA, join_parts, read_json, sha256_file, split_file, write_json


def parse_tree(path):
    """``git ls-tree -r -z HEAD`` output -> sorted [[path, mode, blob_sha1], ...] (files and symlinks only)."""
    entries = []
    for record in Path(path).read_bytes().decode("utf-8").split("\0"):
        if not record:
            continue
        meta, rel = record.split("\t", 1)
        mode, kind, sha = meta.split(" ")
        if kind != "blob":
            raise ValueError("unsupported tree entry %s (%s)" % (rel, kind))
        entries.append([rel, mode, sha])
    return sorted(entries)


def _stage(source, staging, part_bytes):
    target = staging / source.name
    if source.resolve() != target.resolve():
        target.write_bytes(source.read_bytes())
    parts = split_file(target, part_bytes)
    return {"name": target.name, "sha256": sha256_file(target), "bytes": target.stat().st_size, "parts": parts}


def make_request(args):
    staging = Path(args.staging)
    staging.mkdir(parents=True, exist_ok=True)
    part_bytes = int(float(args.part_mb) * 1024 * 1024)
    if not 64 * 1024 <= part_bytes <= 32 * 1024 * 1024:
        raise SystemExit("part size must be between 0.0625 and 32 MB (P3_PART_MB=%s)" % args.part_mb)
    uploads, code_uploads = [], []
    code = _stage(Path(args.code), staging, part_bytes)
    code.update(commit=args.commit, dirty=args.dirty == "1", mode=args.code_mode)
    code_uploads += [(str(staging / p["name"]), p["name"]) for p in code["parts"]]
    if args.code_mode == "github":
        tree = parse_tree(args.tree_file)
        code.update(tarball_url=args.tarball_url, tree=tree,
                    tree_sha256=hashlib.sha256(json.dumps(tree, separators=(",", ":")).encode()).hexdigest())
    else:
        uploads += code_uploads
    pack = None
    if args.pack_json:
        built = json.loads(Path(args.pack_json).read_text(encoding="utf-8"))
        pack = _stage(Path(built["pack"]), staging, part_bytes)
        pack.update(content_sha256=built["content_sha256"], files=built["files"])
        uploads += [(str(staging / p["name"]), p["name"]) for p in pack["parts"]]
    request = {"schema": REQUEST_SCHEMA, "run_id": args.run_id, "task": args.task, "options": json.loads(args.options or "{}"),
               "code": code, "data_pack": pack, "part_bytes": part_bytes, "github": json.loads(args.github or "{}"),
               "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "local": json.loads(args.local or "{}")}
    request_path = staging / "request.json"
    write_json(request_path, request)
    uploads.append((str(request_path), "request.json"))
    Path(args.uploads).write_text("".join("%s\t%s\n" % u for u in uploads), encoding="utf-8")
    Path(args.code_uploads).write_text("".join("%s\t%s\n" % u for u in code_uploads), encoding="utf-8")
    print(json.dumps({"parts": len(uploads), "bytes": sum(Path(u[0]).stat().st_size for u in uploads),
                      "code_mode": args.code_mode}))


def inbox_diff(uploads_path, listing_path):
    """Lines of uploads.tsv whose remote copy is missing or differs (size or SHA256) from the local part."""
    listing = {}
    for line in Path(listing_path).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("[p3] INBOX "):
            listing = json.loads(line[len("[p3] INBOX "):])
    stale = []
    for line in Path(uploads_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        local_path, name = line.split("\t")
        remote = listing.get(name)
        if remote is None or remote[0] != Path(local_path).stat().st_size or remote[1] != sha256_file(local_path):
            stale.append(line)
    return stale


SECRET_PATTERNS = [
    # `requests` errors from `colab upload/download` print the request URL, which carries the runtime proxy token.
    # (?!REDACTED\b) keeps a second pass (VM push, then the launcher's _local/ commit) from counting old redactions.
    (re.compile(r"((?<![A-Za-z0-9_-])(?:colab-runtime-proxy-token|access_token|token|api_key|key|sig|signature)=)"
                r"(?!REDACTED\b)[^&\s'\"<>]+"), r"\1REDACTED"),
    (re.compile(r"(Bearer\s+)(?!REDACTED\b)[A-Za-z0-9._~+/=-]+"), r"\1REDACTED"),
    # credentials inside URLs, e.g. the git-credential-store line https://<user>:<PAT>@github.com (D37)
    (re.compile(r"(https?://)(?!REDACTED@)[^/\s:@'\"<>]+:[^@\s/'\"<>]+@"), r"\1REDACTED@"),
    (re.compile(r"ya29\.[0-9A-Za-z_-]{10,}"), "ya29.REDACTED"),  # Google OAuth access token
    (re.compile(r"1//[0-9A-Za-z_-]{20,}"), "1//REDACTED"),  # Google OAuth refresh token
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "github_pat_REDACTED"),  # fine-grained GitHub PAT
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "gh_REDACTED"),
    (re.compile(r"\bhf_[A-Za-z0-9]{20,}"), "hf_REDACTED"),
]
TEXT_SUFFIXES = (".log", ".txt", ".json", ".md", ".tsv", ".diff")


def redact_text(text):
    count = 0
    for pattern, replacement in SECRET_PATTERNS:
        text, n = pattern.subn(replacement, text)
        count += n
    return text, count


def redact_tree(root):
    """Redact credentials from text files under ``root`` before they are published; return {relpath: count}."""
    root = Path(root)
    changed = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not path.name.endswith(TEXT_SUFFIXES):
            continue
        original = path.read_bytes().decode("utf-8", "surrogateescape")
        text, count = redact_text(original)
        if count:
            path.write_bytes(text.encode("utf-8", "surrogateescape"))
            changed[str(path.relative_to(root))] = count
    return changed


def status_line(path):
    status = read_json(path)
    steps = status.get("steps", [])
    done = sum(s.get("state") in ("passed", "failed", "timeout", "skipped") for s in steps)
    failed = [s["name"] for s in steps if s.get("state") in ("failed", "timeout")]
    current = status.get("current") or {}
    text = "state=%s steps %d/%d" % (status.get("state"), done, len(steps))
    if current.get("step"):
        text += " | now %s (%s) %s" % (current["step"], current.get("elapsed", ""), (current.get("last") or "")[:100])
    if failed:
        text += " | failed: " + ",".join(failed)
    if status.get("overall"):
        text += " | overall=" + status["overall"]
    return text


def field(path, key):
    value = read_json(path)
    for part in key.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    return "" if value is None else (json.dumps(value) if isinstance(value, (dict, list)) else str(value))


def extract(archive, dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(str(archive), "r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            if Path(member.name).is_absolute() or ".." in Path(member.name).parts or member.issym() or member.islnk():
                raise ValueError("unsafe member in results archive: %s" % member.name)
        try:
            tar.extractall(str(dest), filter="data")
        except TypeError:
            tar.extractall(str(dest))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("make-request")
    for name in ["--task", "--run-id", "--code", "--commit", "--staging", "--uploads", "--code-uploads"]:
        p.add_argument(name, required=True)
    p.add_argument("--pack-json", default="", help="empty: the task needs no private data")
    p.add_argument("--dirty", default="0")
    p.add_argument("--options", default="{}")
    p.add_argument("--local", default="{}")
    p.add_argument("--part-mb", default="2")
    p.add_argument("--code-mode", choices=["upload", "github"], default="upload")
    p.add_argument("--tarball-url", default="")
    p.add_argument("--tree-file", default="")
    p.add_argument("--github", default="{}", help="VM-side push settings (scripts/colab/vm_github.py); {} = off")
    p = sub.add_parser("inbox-diff")
    p.add_argument("uploads")
    p.add_argument("listing")
    p = sub.add_parser("redact")
    p.add_argument("root")
    p.add_argument("--report", help="write the list of redacted files here (only if something was redacted)")
    sub.add_parser("redact-stdin")
    p = sub.add_parser("status-line")
    p.add_argument("path")
    p = sub.add_parser("field")
    p.add_argument("path")
    p.add_argument("key")
    p = sub.add_parser("parts")
    p.add_argument("done")
    p = sub.add_parser("join")
    p.add_argument("done")
    p.add_argument("parts_dir")
    p.add_argument("out")
    p = sub.add_parser("extract")
    p.add_argument("archive")
    p.add_argument("dest")
    args = parser.parse_args(argv)
    if args.command == "make-request":
        make_request(args)
    elif args.command == "inbox-diff":
        for line in inbox_diff(args.uploads, args.listing):
            print(line)
    elif args.command == "redact":
        changed = redact_tree(args.root)
        if changed and args.report:
            Path(args.report).write_text("credentials redacted before publishing (file: occurrences)\n" +
                                         "".join("%s: %d\n" % kv for kv in sorted(changed.items())), encoding="utf-8")
        print(sum(changed.values()))
    elif args.command == "redact-stdin":
        sys.stdout.write(redact_text(sys.stdin.read())[0])
    elif args.command == "status-line":
        print(status_line(args.path))
    elif args.command == "field":
        print(field(args.path, args.key))
    elif args.command == "parts":
        for part in read_json(args.done)["package"]["parts"]:
            print(part["name"])
    elif args.command == "join":
        package = read_json(args.done)["package"]
        join_parts(args.parts_dir, package["parts"], args.out, package["sha256"])
        print(args.out)
    elif args.command == "extract":
        extract(args.archive, args.dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
