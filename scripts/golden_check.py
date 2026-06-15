"""Golden question check for LightRAG.

讀取 scripts/golden_questions.yml（若不存在則使用內建範例），
針對每個問題呼叫 query_lightrag，檢查回傳結果是否包含 references，
並輸出 PASS/FAIL 摘要。
"""

from pathlib import Path

from query_lightrag import query_lightrag

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_FILE = Path(__file__).resolve().parent / "golden_questions.yml"

DEFAULT_QUESTIONS = [
    {
        "title": "LightRAG 整體架構",
        "question": "請說明 LightRAG 的整體架構，包含主要元件與資料流。",
    },
    {
        "title": "LightRAG 的索引與檢索流程",
        "question": "LightRAG 如何進行 chunk、embedding、entity/relation 抽取與圖譜建立？",
    },
    {
        "title": "LightRAG 查詢模式比較",
        "question": "LightRAG 支援哪些查詢模式（如 local/global/hybrid/mix），各自的差異與適用情境是什麼？",
    },
]


def load_questions():
    if not GOLDEN_FILE.exists():
        return DEFAULT_QUESTIONS

    try:
        import yaml
    except ImportError:
        print(f"[WARN] PyYAML not installed, falling back to default questions (ignoring {GOLDEN_FILE})")
        return DEFAULT_QUESTIONS

    with GOLDEN_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        return DEFAULT_QUESTIONS
    return data


def extract_references(result: dict):
    return result.get("references") or result.get("refs") or result.get("sources") or []


def run_golden_check():
    questions = load_questions()
    results = []

    for item in questions:
        title = item.get("title", "未命名問題")
        question = item.get("question", "")
        try:
            result = query_lightrag(question)
            refs = extract_references(result)
            passed = bool(refs)
            results.append((title, question, passed, len(refs), None))
        except Exception as exc:  # noqa: BLE001
            results.append((title, question, False, 0, str(exc)))

    print("=" * 60)
    print("Golden Check 結果")
    print("=" * 60)

    pass_count = 0
    for title, question, passed, ref_count, error in results:
        status = "PASS" if passed else "FAIL"
        if passed:
            pass_count += 1
        print(f"[{status}] {title}")
        print(f"  Question: {question}")
        if error:
            print(f"  Error: {error}")
        else:
            print(f"  References: {ref_count}")
        print("-" * 60)

    total = len(results)
    print(f"Summary: {pass_count}/{total} PASS")
    return pass_count == total


if __name__ == "__main__":
    import sys

    ok = run_golden_check()
    sys.exit(0 if ok else 1)
