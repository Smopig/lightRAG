"""Golden question check for LightRAG.

讀取 scripts/golden_questions.yml（若不存在則使用內建範例），
針對每個問題呼叫 query_lightrag，檢查：
  (a) response 是否非空
  (b) 是否含 references
  (c) 若題目有 expected_keywords，檢查回應文字是否包含這些關鍵詞，輸出命中比例

判定規則：
  - response 為空，或無 references -> FAIL
  - 有 expected_keywords 但命中率 < --keyword-threshold（預設 0.5） -> WARN
  - 其餘 -> PASS

輸出最後印出 PASS/WARN/FAIL 統計。
WARN 不影響 exit code；只有 FAIL 或無法連線（例外）才會讓整體判定失敗。
"""

import argparse
from pathlib import Path

from query_lightrag import query_lightrag

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_FILE = Path(__file__).resolve().parent / "golden_questions.yml"

DEFAULT_KEYWORD_THRESHOLD = 0.5

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


def extract_response_text(result: dict) -> str:
    response = result.get("response") or result.get("answer") or ""
    if isinstance(response, list):
        return " ".join(str(x) for x in response)
    return str(response)


def check_keywords(response_text: str, expected_keywords: list[str]):
    """回傳 (命中數, 總數, 命中率, 未命中清單)。"""
    if not expected_keywords:
        return 0, 0, 1.0, []

    text = response_text or ""
    missing = [kw for kw in expected_keywords if kw not in text]
    hit = len(expected_keywords) - len(missing)
    total = len(expected_keywords)
    ratio = hit / total if total else 1.0
    return hit, total, ratio, missing


def evaluate_item(item: dict, keyword_threshold: float):
    """執行單一題目並回傳結果 dict。"""
    title = item.get("title", "未命名問題")
    question = item.get("question", "")
    expected_keywords = item.get("expected_keywords") or []

    try:
        result = query_lightrag(question)
    except Exception as exc:  # noqa: BLE001
        return {
            "title": title,
            "question": question,
            "status": "FAIL",
            "error": str(exc),
            "ref_count": 0,
            "keyword_info": None,
        }

    response_text = extract_response_text(result)
    refs = extract_references(result)

    if not response_text.strip() or not refs:
        return {
            "title": title,
            "question": question,
            "status": "FAIL",
            "error": None,
            "ref_count": len(refs),
            "empty_response": not response_text.strip(),
            "keyword_info": None,
        }

    keyword_info = None
    status = "PASS"
    if expected_keywords:
        hit, total, ratio, missing = check_keywords(response_text, expected_keywords)
        keyword_info = {"hit": hit, "total": total, "ratio": ratio, "missing": missing}
        if ratio < keyword_threshold:
            status = "WARN"

    return {
        "title": title,
        "question": question,
        "status": status,
        "error": None,
        "ref_count": len(refs),
        "keyword_info": keyword_info,
    }


def run_golden_check(keyword_threshold: float = DEFAULT_KEYWORD_THRESHOLD):
    questions = load_questions()
    results = [evaluate_item(item, keyword_threshold) for item in questions]

    print("=" * 60)
    print("Golden Check 結果")
    print("=" * 60)

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for r in results:
        status = r["status"]
        counts[status] += 1
        print(f"[{status}] {r['title']}")
        print(f"  Question: {r['question']}")
        if r["error"]:
            print(f"  Error: {r['error']}")
        else:
            print(f"  References: {r['ref_count']}")
            if r.get("empty_response"):
                print("  Response: (empty)")
            kw = r["keyword_info"]
            if kw:
                print(f"  Keyword hits: {kw['hit']}/{kw['total']} (ratio={kw['ratio']:.2f})")
                if kw["missing"]:
                    print(f"  Missing keywords: {', '.join(kw['missing'])}")
        print("-" * 60)

    total = len(results)
    print(f"Summary: PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']} (total={total})")

    return counts["FAIL"] == 0


if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(description="LightRAG golden question check")
    parser.add_argument(
        "--keyword-threshold",
        type=float,
        default=DEFAULT_KEYWORD_THRESHOLD,
        help="expected_keywords 命中率門檻，低於此值判定為 WARN（預設 0.5）",
    )
    args = parser.parse_args()

    ok = run_golden_check(keyword_threshold=args.keyword_threshold)
    sys.exit(0 if ok else 1)
