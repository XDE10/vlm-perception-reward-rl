"""Check relative Markdown links in the current-facing documentation.

The repository keeps historical material under docs/blueprints/ and
docs/migration/ that intentionally preserves the pre-restructure tree (some of
its links now point at files deleted during the 2026-11-08 cleanup).  This tool
therefore checks the pages that must stay navigable today:

    README.md, AGENTS.md, CHANGELOG.md, docs/README.md,
    docs/{repo_layout,architecture,data,training,verification}.md,
    docs/guides/*.md, the README.md of each top-level working directory, and the
    plan pages in force (execution plan, decision record, S4 pre-registration).

Usage:
    python tools/check_links.py            # current docs only
    python tools/check_links.py --all      # also scan archival docs (warn only)
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_TARGETS = [
    "README.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "docs/README.md",
    "docs/repo_layout.md",
    "docs/architecture.md",
    "docs/data.md",
    "docs/training.md",
    "docs/verification.md",
    "docs/guides/argon_review_prompt.md",
    "configs/README.md",
    "data/README.md",
    "reports/README.md",
    "requirements/README.md",
    "scripts/README.md",
    "colab/README.md",
    "docs/plan/执行计划_20261108.md",
    "docs/plan/决策记录.md",
    "docs/plan/S4预注册_20261110.md",
    "docs/plan/阶段报告_S4_运行器_20261110.md",
]
LINK = re.compile(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^)\s]+))\s*\)")


def links_of(text):
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK.finditer(line):
            target = (match.group(1) or match.group(2) or "").strip()
            if target:
                yield target


def check(files, warn_only=False):
    broken = []
    checked = 0
    for rel in files:
        path = ROOT / rel
        if not path.is_file():
            broken.append((rel, "file itself is missing"))
            continue
        for target in links_of(path.read_text(encoding="utf8")):
            if target.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            checked += 1
            resolved = (path.parent / clean).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                broken.append((rel, f"escapes repository: {target}"))
                continue
            if not resolved.exists():
                broken.append((rel, target))
    return checked, broken


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all",
        action="store_true",
        help="scan archival docs too (docs/blueprints, docs/migration); broken links only warn",
    )
    args = parser.parse_args()

    files = [rel for rel in CURRENT_TARGETS if (ROOT / rel).is_file()]
    checked, broken = check(files)
    print(f"checked {checked} relative links in {len(files)} current pages")
    for page, target in broken:
        print(f"BROKEN  {page}  ->  {target}")

    if args.all:
        archival = sorted(
            str(path.relative_to(ROOT)).replace("\\", "/")
            for base in (ROOT / "docs/blueprints", ROOT / "docs/migration")
            for path in base.rglob("*.md")
        )
        _, arch_broken = check(archival, warn_only=True)
        print(
            f"archival pages: {len(archival)} files, {len(arch_broken)} links pointing outside the current tree (expected for historical records)"
        )
        for page, target in arch_broken[:10]:
            print(f"HISTORICAL  {page}  ->  {target}")

    if broken:
        sys.exit(1)


if __name__ == "__main__":
    main()
