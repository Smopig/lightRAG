import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import golden_check as gc  # noqa: E402

# ---------- check_keywords ----------

def test_check_keywords_all_hit():
    hit, total, ratio, missing = gc.check_keywords("這裡有 chunk 和 entity", ["chunk", "entity"])
    assert hit == 2
    assert total == 2
    assert ratio == 1.0
    assert missing == []


def test_check_keywords_partial_hit():
    hit, total, ratio, missing = gc.check_keywords("這裡有 chunk", ["chunk", "entity"])
    assert hit == 1
    assert total == 2
    assert ratio == 0.5
    assert missing == ["entity"]


def test_check_keywords_empty_expected():
    hit, total, ratio, missing = gc.check_keywords("任何文字", [])
    assert (hit, total, ratio, missing) == (0, 0, 1.0, [])


# ---------- evaluate_item ----------

def test_evaluate_item_pass(monkeypatch):
    def fake_query(question, mode="mix"):
        return {"response": "這裡有 chunk 和 entity 的說明", "references": [{"id": "1"}]}

    monkeypatch.setattr(gc, "query_lightrag", fake_query)

    item = {"title": "T1", "question": "Q1", "expected_keywords": ["chunk", "entity"]}
    result = gc.evaluate_item(item, keyword_threshold=0.5)

    assert result["status"] == "PASS"
    assert result["ref_count"] == 1
    assert result["keyword_info"]["ratio"] == 1.0


def test_evaluate_item_warn_low_keyword_hit(monkeypatch):
    def fake_query(question, mode="mix"):
        return {"response": "只有 chunk", "references": [{"id": "1"}]}

    monkeypatch.setattr(gc, "query_lightrag", fake_query)

    item = {"title": "T2", "question": "Q2", "expected_keywords": ["chunk", "entity", "relation", "graph"]}
    result = gc.evaluate_item(item, keyword_threshold=0.5)

    assert result["status"] == "WARN"
    assert result["keyword_info"]["ratio"] == 0.25


def test_evaluate_item_fail_no_references(monkeypatch):
    def fake_query(question, mode="mix"):
        return {"response": "有回答內容", "references": []}

    monkeypatch.setattr(gc, "query_lightrag", fake_query)

    item = {"title": "T3", "question": "Q3"}
    result = gc.evaluate_item(item, keyword_threshold=0.5)

    assert result["status"] == "FAIL"
    assert result["ref_count"] == 0


def test_evaluate_item_fail_empty_response(monkeypatch):
    def fake_query(question, mode="mix"):
        return {"response": "", "references": [{"id": "1"}]}

    monkeypatch.setattr(gc, "query_lightrag", fake_query)

    item = {"title": "T4", "question": "Q4"}
    result = gc.evaluate_item(item, keyword_threshold=0.5)

    assert result["status"] == "FAIL"
    assert result.get("empty_response") is True


def test_evaluate_item_fail_on_exception(monkeypatch):
    def fake_query(question, mode="mix"):
        raise ConnectionError("cannot connect")

    monkeypatch.setattr(gc, "query_lightrag", fake_query)

    item = {"title": "T5", "question": "Q5"}
    result = gc.evaluate_item(item, keyword_threshold=0.5)

    assert result["status"] == "FAIL"
    assert "cannot connect" in result["error"]


def test_evaluate_item_pass_without_expected_keywords(monkeypatch):
    """向後相容：沒有 expected_keywords 的題目，行為等同舊版（不做關鍵詞檢查）。"""

    def fake_query(question, mode="mix"):
        return {"response": "任意內容", "references": [{"id": "1"}]}

    monkeypatch.setattr(gc, "query_lightrag", fake_query)

    item = {"title": "T6", "question": "Q6"}
    result = gc.evaluate_item(item, keyword_threshold=0.5)

    assert result["status"] == "PASS"
    assert result["keyword_info"] is None


# ---------- run_golden_check ----------

def test_run_golden_check_overall_pass(monkeypatch):
    def fake_query(question, mode="mix"):
        return {"response": "包含 chunk 與 entity", "references": [{"id": "1"}]}

    monkeypatch.setattr(gc, "query_lightrag", fake_query)
    monkeypatch.setattr(
        gc,
        "load_questions",
        lambda: [{"title": "T1", "question": "Q1", "expected_keywords": ["chunk"]}],
    )

    assert gc.run_golden_check() is True


def test_run_golden_check_warn_does_not_fail(monkeypatch):
    def fake_query(question, mode="mix"):
        return {"response": "只有 chunk", "references": [{"id": "1"}]}

    monkeypatch.setattr(gc, "query_lightrag", fake_query)
    monkeypatch.setattr(
        gc,
        "load_questions",
        lambda: [{"title": "T1", "question": "Q1", "expected_keywords": ["chunk", "entity", "relation", "graph"]}],
    )

    # WARN should not cause overall failure
    assert gc.run_golden_check() is True


def test_run_golden_check_fail_overall(monkeypatch):
    def fake_query(question, mode="mix"):
        return {"response": "answer", "references": []}

    monkeypatch.setattr(gc, "query_lightrag", fake_query)
    monkeypatch.setattr(
        gc,
        "load_questions",
        lambda: [{"title": "T1", "question": "Q1"}],
    )

    assert gc.run_golden_check() is False
