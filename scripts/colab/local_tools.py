"""Local helpers for colab/launch.sh (standard library only, python3 >= 3.8).

    python3 -m scripts.colab.local_tools make-request ...
    python3 -m scripts.colab.local_tools status-line <status.json>
    python3 -m scripts.colab.local_tools field <json> <dotted.key>
    python3 -m scripts.colab.local_tools parts <done.json>
    python3 -m scripts.colab.local_tools join <done.json> <parts dir> <out file>
    python3 -m scripts.colab.local_tools extract <archive> <dest dir>
"""
import argparse
import json
import sys
import tarfile
import time
from pathlib import Path

from scripts.colab.common import REQUEST_SCHEMA, join_parts, read_json, sha256_file, split_file, write_json


def make_request(args):
    staging = Path(args.staging)
    staging.mkdir(parents=True, exist_ok=True)
    pack = json.loads(Path(args.pack_json).read_text(encoding="utf-8"))
    uploads = []
    entries = {}
    for key, source in [("code", Path(args.code)), ("data_pack", Path(pack["pack"]))]:
        target = staging / source.name
        if source.resolve() != target.resolve():
            target.write_bytes(source.read_bytes())
        parts = split_file(target)
        entries[key] = {"name": target.name, "sha256": sha256_file(target), "bytes": target.stat().st_size, "parts": parts}
        uploads += [(str(staging / p["name"]), p["name"]) for p in parts]
    entries["code"].update(commit=args.commit, dirty=args.dirty == "1")
    entries["data_pack"]["content_sha256"] = pack["content_sha256"]
    entries["data_pack"]["files"] = pack["files"]
    options = json.loads(args.options or "{}")
    request = {"schema": REQUEST_SCHEMA, "run_id": args.run_id, "task": args.task, "options": options,
               "code": entries["code"], "data_pack": entries["data_pack"],
               "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "local": json.loads(args.local or "{}")}
    request_path = staging / "request.json"
    write_json(request_path, request)
    uploads.append((str(request_path), "request.json"))
    Path(args.uploads).write_text("".join("%s\t%s\n" % u for u in uploads), encoding="utf-8")
    print(json.dumps({"parts": len(uploads), "bytes": sum(Path(u[0]).stat().st_size for u in uploads)}))


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
    for name in ["--task", "--run-id", "--code", "--commit", "--pack-json", "--staging", "--uploads"]:
        p.add_argument(name, required=True)
    p.add_argument("--dirty", default="0")
    p.add_argument("--options", default="{}")
    p.add_argument("--local", default="{}")
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
