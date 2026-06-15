import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
problems = []
all_pages = list(WIKI.rglob("*.md"))
all_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in all_pages)

for p in all_pages:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    rel = p.relative_to(WIKI)
    if p.name not in ["index.md", "log.md"]:
        if "## Sources" not in txt:
            problems.append((rel, "missing Sources section"))
        if "status: verified" in txt and "[^src" not in txt:
            problems.append((rel, "verified page without citations"))
    if not re.search(r"^title:\s*(.+)$", txt, re.M):
        problems.append((rel, "missing YAML title"))

    stem = p.with_suffix("").relative_to(WIKI).as_posix()
    short = p.stem
    if p.name not in ["index.md", "log.md"]:
        if f"[[{stem}]]" not in all_text and f"[[{short}]]" not in all_text:
            problems.append((rel, "possible orphan page"))

for rel, msg in problems:
    print(f"{rel}: {msg}")
print(f"Total problems: {len(problems)}")
