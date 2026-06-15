import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import route_query as rq  # noqa: E402


def test_answer_route_wiki_when_hit(monkeypatch, tmp_path):
    fake_wiki = tmp_path / "wiki"
    fake_wiki.mkdir()
    (fake_wiki / "page.md").write_text("這裡提到 LightRAG 架構說明", encoding="utf-8")

    monkeypatch.setattr(rq, "WIKI", fake_wiki)

    def fail_query(*args, **kwargs):
        raise AssertionError("query_lightrag should not be called when wiki hit")

    monkeypatch.setattr(rq, "query_lightrag", fail_query)

    result = rq.answer("LightRAG 架構說明 是什麼")
    assert result["route"] == "wiki"
    assert any("page.md" in h for h in result["hits"])


def test_answer_route_lightrag_when_no_hit(monkeypatch, tmp_path):
    fake_wiki = tmp_path / "wiki_empty"
    fake_wiki.mkdir()
    (fake_wiki / "page.md").write_text("無關內容", encoding="utf-8")

    monkeypatch.setattr(rq, "WIKI", fake_wiki)

    def fake_query_lightrag(question, mode="mix"):
        return {"response": "假回答", "references": []}

    monkeypatch.setattr(rq, "query_lightrag", fake_query_lightrag)

    result = rq.answer("完全沒有關聯的關鍵字XYZ")
    assert result["route"] == "lightrag"
    assert result["result"]["response"] == "假回答"
