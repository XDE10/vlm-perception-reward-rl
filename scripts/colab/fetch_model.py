"""Download the pinned model snapshot and record every file's SHA256 (VM side, base venv).

    python -m scripts.colab.fetch_model --repo Qwen/Qwen2.5-VL-3B-Instruct --revision <sha> --dest <dir> --out <json>
"""
import argparse
import hashlib
import json
import time
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 24), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if len(args.revision) != 40:
        raise ValueError("a full 40-character revision is required")
    from huggingface_hub import snapshot_download

    started = time.time()
    path = snapshot_download(repo_id=args.repo, revision=args.revision, local_dir=args.dest,
                             allow_patterns=["*.json", "*.safetensors", "*.txt", "*.jinja", "*.model", "merges.txt",
                                             "vocab.json", "tokenizer*"])
    downloaded = time.time() - started
    root = Path(path)
    files = {str(p.relative_to(root)): {"bytes": p.stat().st_size, "sha256": sha256(p)}
             for p in sorted(root.rglob("*")) if p.is_file() and ".cache" not in p.parts}
    if not any(name.endswith(".safetensors") for name in files):
        raise RuntimeError("snapshot has no safetensors weights")
    record = {"repo": args.repo, "revision": args.revision, "local_dir": str(root), "files": files,
              "total_bytes": sum(f["bytes"] for f in files.values()), "download_seconds": downloaded,
              "hash_seconds": time.time() - started - downloaded}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in record.items() if k != "files"}))


if __name__ == "__main__":
    main()
