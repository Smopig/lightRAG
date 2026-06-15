import re
import sys
import json
from pathlib import Path
from datetime import date
from query_lightrag import query_lightrag

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9一-鿿]+", "_", text)
    return text.strip("_")[:80] or "untitled"


def normalize_content(content):
    if content is None:
        return ""
    if isinstance(content, list):
        return " ".join(str(x) for x in content)
    return str(content)


def refs_to_markdown(refs):
    lines = []
    for i, ref in enumerate(refs or [], 1):
        if not isinstance(ref, dict):
            lines.append(f"[^src{i}]: {str(ref)[:500]}")
            continue
        fp = ref.get("file_path") or ref.get("source") or ref.get("document") or ref.get("id") or "unknown"
        preview = normalize_content(ref.get("content") or ref.get("chunk_content") or ref.get("text"))
        preview = preview[:300].replace("\n", " ")
        lines.append(f"[^src{i}]: {fp}。摘錄：{preview}")
    return "\n".join(lines)


def compile_page(title: str, question: str, folder: str = "queries"):
    result = query_lightrag(question, mode="mix")
    answer = result.get("response") or result.get("answer") or json.dumps(result, ensure_ascii=False, indent=2)
    refs = result.get("references") or result.get("refs") or result.get("sources") or []
    slug = slugify(title)
    out_dir = WIKI / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{slug}.md"
    page_type = folder.rstrip("s") if folder.endswith("s") else folder
    md = f"""---
title: {title}
type: {page_type}
status: needs_review
updated: {date.today().isoformat()}
source_count: {len(refs)}
related: []
---
# {title}

## 查詢問題
{question}

## LightRAG 整理結果
{answer}

## 待人工審核
- [ ] 檢查答案是否完全被 Sources 支撐。
- [ ] 補上必要的 [[wikilink]]。
- [ ] 若此頁應整併到既有 concept/entity 頁，請移動內容。

## Sources
{refs_to_markdown(refs)}
"""
    out.write_text(md, encoding="utf-8")
    with (WIKI / "log.md").open("a", encoding="utf-8") as f:
        f.write(f"\n## [{date.today().isoformat()}] compile | {title}\n- Question: {question}\n- Output: {out.relative_to(WIKI)}\n")
    print(out)


if __name__ == "__main__":
    title = sys.argv[1]
    question = " ".join(sys.argv[2:])
    compile_page(title, question)
