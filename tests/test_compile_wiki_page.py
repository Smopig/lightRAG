import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compile_wiki_page as cwp  # noqa: E402


# ---------- slugify ----------

def test_slugify_basic_ascii():
    assert cwp.slugify("Hello World") == "hello_world"


def test_slugify_mixed_chinese_english():
    s = cwp.slugify("LightRAG 架構介紹")
    assert s == "lightrag_架構介紹"


def test_slugify_special_chars():
    s = cwp.slugify("foo/bar:baz?  *qux*")
    # special chars collapse to underscores, no leading/trailing underscore
    assert s == "foo_bar_baz_qux"
    assert not s.startswith("_")
    assert not s.endswith("_")


def test_slugify_empty_string_fallback():
    assert cwp.slugify("") == "untitled"


def test_slugify_only_special_chars_fallback():
    assert cwp.slugify("!!!???") == "untitled"


def test_slugify_length_truncation():
    long_title = "a" * 200
    s = cwp.slugify(long_title)
    assert len(s) <= 80


# ---------- normalize_content ----------

def test_normalize_content_none():
    assert cwp.normalize_content(None) == ""


def test_normalize_content_list():
    assert cwp.normalize_content(["a", "b", 1]) == "a b 1"


def test_normalize_content_str():
    assert cwp.normalize_content("hello") == "hello"


def test_normalize_content_int():
    assert cwp.normalize_content(42) == "42"


# ---------- refs_to_markdown ----------

def test_refs_to_markdown_dict_with_file_path_and_content():
    refs = [{"file_path": "doc1.pdf", "content": "some chunk text"}]
    md = cwp.refs_to_markdown(refs)
    assert "[^src1]: doc1.pdf" in md
    assert "some chunk text" in md


def test_refs_to_markdown_dict_missing_fields():
    refs = [{}]
    md = cwp.refs_to_markdown(refs)
    assert "[^src1]: unknown" in md


def test_refs_to_markdown_dict_alternate_keys():
    refs = [{"source": "doc2.pdf", "chunk_content": "alt text"}]
    md = cwp.refs_to_markdown(refs)
    assert "doc2.pdf" in md
    assert "alt text" in md

    refs2 = [{"document": "doc3.pdf", "text": "text field"}]
    md2 = cwp.refs_to_markdown(refs2)
    assert "doc3.pdf" in md2
    assert "text field" in md2

    refs3 = [{"id": "id123"}]
    md3 = cwp.refs_to_markdown(refs3)
    assert "id123" in md3


def test_refs_to_markdown_plain_string():
    refs = ["just a raw string reference"]
    md = cwp.refs_to_markdown(refs)
    assert "[^src1]: just a raw string reference" in md


def test_refs_to_markdown_empty_list():
    assert cwp.refs_to_markdown([]) == ""


def test_refs_to_markdown_none():
    assert cwp.refs_to_markdown(None) == ""


def test_refs_to_markdown_content_is_list():
    refs = [{"file_path": "doc4.pdf", "content": ["chunk one", "chunk two"]}]
    md = cwp.refs_to_markdown(refs)
    assert "chunk one chunk two" in md


def test_refs_to_markdown_content_with_newlines_truncated():
    long_content = "line1\nline2\n" + ("x" * 400)
    refs = [{"file_path": "doc5.pdf", "content": long_content}]
    md = cwp.refs_to_markdown(refs)
    assert "\n" not in md.split("摘錄：")[1]
    # truncated to 300 chars
    excerpt = md.split("摘錄：")[1]
    assert len(excerpt) <= 300


# ---------- compile_page ----------

def test_compile_page_creates_md_with_frontmatter_and_sources(tmp_path, monkeypatch):
    fake_wiki = tmp_path / "wiki"
    monkeypatch.setattr(cwp, "WIKI", fake_wiki)

    fake_result = {
        "response": "這是測試回答內容。",
        "references": [
            {"file_path": "raw_sources/test.pdf", "content": "片段內容 A"},
            {"file_path": "raw_sources/test2.pdf", "content": "片段內容 B"},
        ],
    }

    def fake_query_lightrag(question, mode="mix"):
        return fake_result

    monkeypatch.setattr(cwp, "query_lightrag", fake_query_lightrag)

    cwp.compile_page("測試標題", "這是一個測試問題？")

    out_file = fake_wiki / "queries" / "測試標題.md"
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "title: 測試標題" in content
    assert "source_count: 2" in content
    assert "## Sources" in content
    assert "raw_sources/test.pdf" in content
    assert "片段內容 A" in content
    assert "這是測試回答內容。" in content

    log_file = fake_wiki / "log.md"
    assert log_file.exists()
    log_content = log_file.read_text(encoding="utf-8")
    assert "compile | 測試標題" in log_content
    assert "這是一個測試問題？" in log_content


def test_compile_page_handles_empty_references(tmp_path, monkeypatch):
    fake_wiki = tmp_path / "wiki2"
    monkeypatch.setattr(cwp, "WIKI", fake_wiki)

    def fake_query_lightrag(question, mode="mix"):
        return {"response": "答案", "references": []}

    monkeypatch.setattr(cwp, "query_lightrag", fake_query_lightrag)

    cwp.compile_page("空引用測試", "問題")

    out_file = fake_wiki / "queries" / "空引用測試.md"
    content = out_file.read_text(encoding="utf-8")
    assert "source_count: 0" in content


def test_compile_page_fallback_response_key(tmp_path, monkeypatch):
    fake_wiki = tmp_path / "wiki3"
    monkeypatch.setattr(cwp, "WIKI", fake_wiki)

    # no "response" key, falls back to "answer"
    def fake_query_lightrag(question, mode="mix"):
        return {"answer": "備用回答", "sources": [{"id": "x1"}]}

    monkeypatch.setattr(cwp, "query_lightrag", fake_query_lightrag)

    cwp.compile_page("備用測試", "問題2")

    out_file = fake_wiki / "queries" / "備用測試.md"
    content = out_file.read_text(encoding="utf-8")
    assert "備用回答" in content
    assert "source_count: 1" in content
    assert "x1" in content
