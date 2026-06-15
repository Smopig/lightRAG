import json
from pathlib import Path

from query_lightrag import query_lightrag

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"


def search_wiki(keyword: str):
    hits = []
    for p in WIKI.rglob("*.md"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if keyword.lower() in txt.lower():
            hits.append((p, txt[:800]))
    return hits[:5]


def answer(question: str):
    key = question[:8]
    hits = search_wiki(key)
    if hits:
        return {"route": "wiki", "hits": [str(h[0]) for h in hits]}
    return {"route": "lightrag", "result": query_lightrag(question)}


if __name__ == "__main__":
    import sys

    print(json.dumps(answer(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))
