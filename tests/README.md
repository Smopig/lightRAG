# 離線單元測試

這些測試針對 `scripts/compile_wiki_page.py` 與 `scripts/route_query.py` 中
不需要實機 LightRAG server 的純邏輯（slugify、normalize_content、
refs_to_markdown、compile_page、search_wiki/answer 路由邏輯）。

所有對 `query_lightrag.query_lightrag` 的呼叫都用 `monkeypatch` 替換為假資料，
**不會發出任何真實 HTTP 請求**，因此不需要啟動 lightrag-server 或 ollama。

`compile_page` 的測試會用 `monkeypatch` 把 `WIKI` 路徑指向 `tmp_path`
（pytest 提供的臨時目錄），不會寫入或污染真實的 `wiki/`。

## 執行方式

```bash
python3 -m venv .venv
.venv/bin/pip install pytest requests pyyaml
.venv/bin/pytest tests/ -v
```

## 為何不需要 server

- `query_lightrag` 一律被 monkeypatch 取代，回傳測試用的假 dict。
- `compile_page`、`route_query.answer` 只測試本機檔案/字串處理邏輯。
- 這些測試專門驗證手冊警告的風險點：references 的 schema
  （dict 含 file_path/content、缺欄位、純字串、空 list）在
  `refs_to_markdown` 中都能正確處理而不丟例外。
