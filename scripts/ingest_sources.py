"""把 raw_sources/ 下的檔案匯入 LightRAG。

沿用 query_lightrag.py 的連線方式（LIGHTRAG_URL / LIGHTRAG_API_KEY、X-API-Key）。

!!! 重要 !!!
upload_document() 所使用的端點 "/documents/upload"（multipart file 上傳）
與 payload 欄位名稱「尚未對實機 LightRAG 版本驗證」。
實際使用前請先以 `curl <BASE_URL>/openapi.json` 或瀏覽 `<BASE_URL>/docs`
確認正確的上傳端點路徑、HTTP method、欄位名稱（例如可能是 "file" 或
"files"，也可能是 /documents/file 或 /documents/text 等），
再依實況調整 upload_document() 的實作。

預設為 dry-run：只統計檔案數量、總位元組數與粗略 token 估算，
不會呼叫任何 API。加上 --execute 才會真的上傳。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests
from query_lightrag import API_KEY, BASE_URL

ROOT = Path(__file__).resolve().parents[1]
RAW_SOURCES = ROOT / "raw_sources"

# 先列常見的幾種文件副檔名
SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt", ".docx", ".pptx", ".csv", ".json"}

# 上傳端點（未驗證，見檔頭說明）
UPLOAD_ENDPOINT = "/documents/upload"


def is_chinese_char(ch: str) -> bool:
    return "一" <= ch <= "鿿"


def estimate_tokens(text: str) -> int:
    """粗略 token 估算：中文約 2 chars/token，英文/其他約 4 chars/token。"""
    chinese_chars = sum(1 for ch in text if is_chinese_char(ch))
    other_chars = len(text) - chinese_chars
    return round(chinese_chars / 2 + other_chars / 4)


def estimate_tokens_for_file(path: Path) -> int:
    """對檔案內容做粗略 token 估算。

    純文字類型（.md/.txt/.csv/.json）讀取內容估算；
    二進位類型（.pdf/.docx/.pptx）則用「位元組數 / 4」粗估，
    因為實際內容需要解析才能取得，這裡只是 dry-run 的粗略上限。
    """
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".csv", ".json"}:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            return estimate_tokens(text)
        except OSError:
            return 0
    # 二進位檔案：粗略以位元組數估算
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return round(size / 4)


def scan_files(subdir: str | None = None, extensions: set[str] | None = None) -> list[Path]:
    """掃描 raw_sources/（或其子目錄）下符合副檔名的檔案。"""
    extensions = extensions or SUPPORTED_EXTENSIONS
    base = RAW_SOURCES / subdir if subdir else RAW_SOURCES
    if not base.exists():
        return []
    files = [
        p for p in sorted(base.rglob("*"))
        if p.is_file() and p.suffix.lower() in extensions
    ]
    return files


def upload_document(path: Path) -> dict:
    """呼叫 LightRAG 上傳端點，匯入單一檔案。

    !!! 此端點/payload 需依實機 LightRAG 版本以 /docs 或 openapi.json
    驗證後調整 !!!

    目前假設：
      POST {BASE_URL}/documents/upload
      multipart/form-data，欄位名稱為 "file"
    """
    headers = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    with path.open("rb") as f:
        files = {"file": (path.name, f)}
        response = requests.post(
            f"{BASE_URL}{UPLOAD_ENDPOINT}",
            headers=headers,
            files=files,
            timeout=600,
        )
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return {"status": "ok", "raw": response.text}


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def format_bytes(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"


def run_dry_run(files: list[Path]) -> None:
    total_bytes = 0
    total_tokens = 0
    print("=" * 60)
    print("Dry-run：以下檔案將被匯入（尚未實際上傳）")
    print("=" * 60)
    for p in files:
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        tokens = estimate_tokens_for_file(p)
        total_bytes += size
        total_tokens += tokens
        print(f"  {display_path(p)}  ({format_bytes(size)}, ~{tokens} tokens)")

    print("-" * 60)
    print(f"檔案數：{len(files)}")
    print(f"總位元組數：{format_bytes(total_bytes)} ({total_bytes} bytes)")
    print(f"粗略 token 估算：~{total_tokens}")
    print("-" * 60)
    print("這是 dry-run，尚未呼叫任何 API。")
    print("確認無誤後，加上 --execute 才會真的上傳。")


def run_execute(files: list[Path], batch_size: int) -> None:
    print("=" * 60)
    print(f"開始上傳 {len(files)} 個檔案（batch-size={batch_size}）")
    print("=" * 60)

    succeeded: list[Path] = []
    failed: list[tuple[Path, str]] = []

    for i in range(0, len(files), batch_size):
        batch = files[i : i + batch_size]
        print(f"\n[Batch {i // batch_size + 1}] {len(batch)} 個檔案")
        for p in batch:
            rel = display_path(p)
            try:
                result = upload_document(p)
                print(f"  [OK] {rel} -> {result}")
                succeeded.append(p)
            except Exception as exc:  # noqa: BLE001
                print(f"  [FAIL] {rel}: {exc}")
                failed.append((p, str(exc)))

    print("\n" + "=" * 60)
    print("上傳結果彙總")
    print("=" * 60)
    print(f"成功：{len(succeeded)} / {len(files)}")
    if failed:
        print(f"失敗：{len(failed)}")
        for p, err in failed:
            print(f"  - {display_path(p)}: {err}")
    else:
        print("失敗：0")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="把 raw_sources/ 下的檔案匯入 LightRAG（預設 dry-run）"
    )
    parser.add_argument(
        "--subdir",
        default=None,
        help="只掃描 raw_sources/ 下的指定子目錄（例如 papers）",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="實際呼叫 LightRAG 上傳端點（預設僅 dry-run 估算）",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="每批上傳的檔案數（預設 10）",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="最多處理的檔案數上限；超過時會要求確認或截斷",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="超過 --max-files 時不互動詢問，直接截斷至上限",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    files = scan_files(subdir=args.subdir)

    if not files:
        print("找不到符合條件的檔案（檢查 raw_sources/ 與 --subdir）。")
        return 0

    if args.max_files is not None and len(files) > args.max_files:
        print(
            f"找到 {len(files)} 個檔案，超過 --max-files={args.max_files} 上限。"
        )
        if args.yes:
            print(f"已自動截斷為前 {args.max_files} 個檔案。")
            files = files[: args.max_files]
        else:
            try:
                answer = input(
                    f"是否截斷為前 {args.max_files} 個檔案並繼續？[y/N] "
                ).strip().lower()
            except EOFError:
                answer = "n"
            if answer != "y":
                print("已取消。")
                return 1
            files = files[: args.max_files]

    if args.execute:
        run_execute(files, batch_size=args.batch_size)
    else:
        run_dry_run(files)

    return 0


if __name__ == "__main__":
    sys.exit(main())
