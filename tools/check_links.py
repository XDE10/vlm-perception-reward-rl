"""Check relative links in the documentation shipped in the repository."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^)\s]+))\s*\)")
PAGES = [
    *ROOT.glob("*.md"),
    *sorted((ROOT / "docs").rglob("*.md")),
    *(ROOT / name / "README.md" for name in ("colab", "configs", "data", "requirements", "shuffle_r1")),
]


def main():
    broken = []
    for page in PAGES:
        in_fence = False
        for line in page.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            if in_fence:
                continue
            for match in LINK.finditer(line):
                target = match.group(1) or match.group(2)
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                path = (page.parent / target.split("#", 1)[0]).resolve()
                if not path.is_relative_to(ROOT) or not path.exists():
                    broken.append(f"{page.relative_to(ROOT)} -> {target}")
    for message in broken:
        print(f"BROKEN {message}")
    print(f"Checked {len(PAGES)} Markdown files")
    return bool(broken)


if __name__ == "__main__":
    raise SystemExit(main())
