"""VM-side verification of the extracted private data pack (standard library only).

    python -m scripts.colab.verify_pack --repo /content/p3/repo --out <file>
"""
import argparse
import json
import sys

from scripts.colab.common import write_json
from scripts.colab.pack_private_data import ROOT, verify_tree


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(ROOT))
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = verify_tree(args.repo)
    if args.out:
        write_json(args.out, result)
    print(json.dumps({k: v for k, v in result.items() if k != "missing_optional"}, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
