import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ingest_sources as ing  # noqa: E402

# ---------- token estimation ----------

def test_estimate_tokens_english():
    text = "a" * 40  # 40 chars / 4 = 10 tokens
    assert ing.estimate_tokens(text) == 10


def test_estimate_tokens_chinese():
    text = "中" * 10  # 10 chars / 2 = 5 tokens
    assert ing.estimate_tokens(text) == 5


def test_estimate_tokens_mixed():
    text = "中" * 10 + "a" * 40  # 5 + 10 = 15
    assert ing.estimate_tokens(text) == 15


def test_estimate_tokens_for_file_text(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("a" * 40, encoding="utf-8")
    assert ing.estimate_tokens_for_file(f) == 10


def test_estimate_tokens_for_file_binary(tmp_path):
    f = tmp_path / "doc.pdf"
    f.write_bytes(b"x" * 400)
    assert ing.estimate_tokens_for_file(f) == 100


# ---------- scan_files ----------

def test_scan_files_filters_by_extension(tmp_path, monkeypatch):
    raw = tmp_path / "raw_sources"
    raw.mkdir()
    (raw / "a.pdf").write_bytes(b"123")
    (raw / "b.md").write_text("hello", encoding="utf-8")
    (raw / "c.exe").write_bytes(b"123")
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)

    files = ing.scan_files()
    names = {p.name for p in files}
    assert names == {"a.pdf", "b.md"}


def test_scan_files_subdir(tmp_path, monkeypatch):
    raw = tmp_path / "raw_sources"
    sub = raw / "papers"
    sub.mkdir(parents=True)
    (sub / "p1.pdf").write_bytes(b"123")
    (raw / "other.txt").write_text("x", encoding="utf-8")
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)

    files = ing.scan_files(subdir="papers")
    names = {p.name for p in files}
    assert names == {"p1.pdf"}


def test_scan_files_missing_dir(tmp_path, monkeypatch):
    raw = tmp_path / "does_not_exist"
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)
    assert ing.scan_files() == []


# ---------- dry-run / main ----------

def test_dry_run_main_no_files(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "raw_sources"
    raw.mkdir()
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)

    rc = ing.main([])
    captured = capsys.readouterr()
    assert rc == 0
    assert "找不到" in captured.out


def test_dry_run_main_lists_files(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "raw_sources"
    raw.mkdir()
    (raw / "a.txt").write_text("a" * 40, encoding="utf-8")
    (raw / "b.md").write_text("中" * 10, encoding="utf-8")
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)

    rc = ing.main([])
    captured = capsys.readouterr()
    assert rc == 0
    assert "a.txt" in captured.out
    assert "b.md" in captured.out
    assert "檔案數：2" in captured.out
    assert "--execute" in captured.out


def test_max_files_truncate_with_yes(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "raw_sources"
    raw.mkdir()
    for i in range(5):
        (raw / f"f{i}.txt").write_text("hello", encoding="utf-8")
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)

    rc = ing.main(["--max-files", "2", "--yes"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "檔案數：2" in captured.out
    assert "超過 --max-files=2 上限" in captured.out


def test_max_files_cancel_without_yes(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "raw_sources"
    raw.mkdir()
    for i in range(3):
        (raw / f"f{i}.txt").write_text("hello", encoding="utf-8")
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)

    # EOFError on input() -> treated as "n" -> cancel
    monkeypatch.setattr("builtins.input", lambda *a, **k: (_ for _ in ()).throw(EOFError()))

    rc = ing.main(["--max-files", "1"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "已取消" in captured.out


# ---------- execute path (monkeypatched upload) ----------

def test_execute_calls_upload_document(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "raw_sources"
    raw.mkdir()
    (raw / "a.txt").write_text("hello", encoding="utf-8")
    (raw / "b.txt").write_text("world", encoding="utf-8")
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)

    calls = []

    def fake_upload(path):
        calls.append(path)
        return {"status": "uploaded"}

    monkeypatch.setattr(ing, "upload_document", fake_upload)

    rc = ing.main(["--execute"])
    captured = capsys.readouterr()
    assert rc == 0
    assert len(calls) == 2
    assert "成功：2 / 2" in captured.out
    assert "失敗：0" in captured.out


def test_execute_collects_failures(tmp_path, monkeypatch, capsys):
    raw = tmp_path / "raw_sources"
    raw.mkdir()
    (raw / "good.txt").write_text("hello", encoding="utf-8")
    (raw / "bad.txt").write_text("world", encoding="utf-8")
    monkeypatch.setattr(ing, "RAW_SOURCES", raw)

    def fake_upload(path):
        if path.name == "bad.txt":
            raise RuntimeError("boom")
        return {"status": "uploaded"}

    monkeypatch.setattr(ing, "upload_document", fake_upload)

    rc = ing.main(["--execute"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "成功：1 / 2" in captured.out
    assert "失敗：1" in captured.out
    assert "bad.txt" in captured.out
    assert "boom" in captured.out
