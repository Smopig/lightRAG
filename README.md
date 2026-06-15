# LightRAG + LLM Wiki Hybrid Knowledge Lab

LightRAG + LLM Wiki 混合知識系統。本專案直接建在此 git repo 根目錄，所有設定檔、腳本與 wiki 內容都會被版本控制（除 `.gitignore` 排除的項目外）。

## 目錄結構

```text
raw_sources/          不可變原始資料（lightrag / project_docs / papers / inbox）
lightrag_workspace/   LightRAG 索引加工品（不進 git）
wiki/                 長期知識庫（entities / concepts / sources / synthesis / comparisons / queries）
schema/               Wiki 維護規則、頁面模板、lint 規則
scripts/              查詢、編譯、lint、路由與 golden check 腳本
outputs/              暫存輸出（不進 git）
docs/                 規格文件、實作筆記
```

## 環境建置（使用 uv）

```bash
# 安裝 uv（若尚未安裝）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 建立虛擬環境
uv venv

# 啟用虛擬環境
source .venv/bin/activate

# 安裝 lightrag-server 與相關套件
uv pip install "lightrag-hku[api]" requests pyyaml
```

## 啟動流程

1. 複製 `.env.example` 為 `.env`：
   ```bash
   cp .env.example .env
   ```
2. 在 `.env` 填入 MiniMax API key 與確認後的 model ID（`LLM_MODEL` / `KEYWORD_LLM_MODEL` / `QUERY_LLM_MODEL`）。
3. 啟動 Ollama 並確認 `bge-m3` 已安裝：
   ```bash
   ollama pull bge-m3
   ```
4. 啟動 LightRAG Server（`WORKING_DIR=./lightrag_workspace`、`INPUT_DIR=./raw_sources/inbox`）。
5. 把原始資料放入 `raw_sources/`，再上傳或 scan 到 LightRAG。

## 使用 scripts/

所有腳本皆假設於 repo 根目錄執行，且 LightRAG Server 已啟動於 `LIGHTRAG_URL`（預設 `http://localhost:9621`）。

```bash
# 直接查詢 LightRAG
python3 scripts/query_lightrag.py "請整理主要架構"

# 把查詢結果編譯成 wiki 頁面（會寫入 wiki/queries/ 並更新 wiki/log.md）
python3 scripts/compile_wiki_page.py "LightRAG 整體架構" "請說明 LightRAG 的整體架構"

# 先查 wiki，不足再查 LightRAG
python3 scripts/route_query.py "LightRAG 整體架構是什麼？"

# 執行 golden questions 檢查（檢查回應是否含 references）
python3 scripts/golden_check.py
```

## Lint 檢查

```bash
python3 scripts/wiki_lint.py
```

會檢查每個 wiki 頁面是否有 `## Sources` 區塊、YAML title，以及是否為孤立頁面（orphan page）。規則定義於 `schema/lint_rules.yml`，維護規範見 `schema/AGENTS.md`。

## 備份 lightrag_workspace

`lightrag_workspace/` 是索引加工品，不進 git，但建議定期備份：

```bash
tar -czf outputs/lightrag_workspace_$(date +%Y%m%d).tar.gz lightrag_workspace/
```

## 安全規則

- `raw_sources/` 是不可變真相來源，不得修改、刪除或覆寫。
- `.env`、API key、token、密碼不得提交。
- `lightrag_workspace/` 是索引加工品，可備份但不要手動修改內容。
