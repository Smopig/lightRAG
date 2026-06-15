# Implementation Notes

## [2026-06-15] 骨架建置記錄

### 1. 為何建在 repo 根目錄而非 `~/hybrid-knowledge-lab`

`templates/bootstrap_hybrid_knowledge_lab.sh` 原本的設計是在 `$HOME/hybrid-knowledge-lab` 建立一個全新的 git repo。但本次任務是在 remote 容器環境中進行，且需要讓所有產出（wiki、scripts、schema、設定範本）能被現有的 `/home/user/lightRAG` git repo 保存與提交。因此改為：

- 直接以 `/home/user/lightRAG` repo 根目錄作為專案根目錄。
- 所有路徑改為相對 repo 根目錄，不再使用 `$HOME/hybrid-knowledge-lab` 字面值。
- 不執行 bootstrap script、不額外 `git init`（沿用既有 repo）。

### 2. `.env` 路徑調整

`.env.example` 中的路徑已從原本的絕對路徑（`$LAB_DIR/...`）改為相對 repo 根目錄的相對路徑：

- `WORKING_DIR=./lightrag_workspace`
- `INPUT_DIR=./raw_sources/inbox`

啟動 LightRAG Server 時，請確保工作目錄為 repo 根目錄，這樣相對路徑才會正確解析。

### 3. MiniMax model ID

使用者已確認 model ID 為 `Minimax-M2.5`，已填入 `.env.example` 的 `LLM_MODEL` / `KEYWORD_LLM_MODEL` / `QUERY_LLM_MODEL`。`LLM_BINDING_API_KEY` 維持佔位符 `YOUR_MINIMAX_API_KEY`（不寫入真實 key）。使用者需自行：

1. 複製 `.env.example` 為 `.env`（`.env` 已加入 `.gitignore`，不會被提交）。
2. 填入實際的 API key；若控制台顯示的 API host 與 `https://api.minimax.io/v1` 不同（例如中國站網域），一併更新 `LLM_BINDING_HOST`。

### 4. Ollama / LightRAG 尚未安裝

本次僅建立檔案骨架（資料夾結構、wiki 模板、schema 規則、scripts），並未：

- 安裝 `lightrag-hku` 或任何 Python 套件。
- 安裝或啟動 Ollama / `bge-m3` embedding 模型。
- 執行任何 LightRAG Server 或 ingest 流程。

後續安裝與啟動步驟見 `README.md`。

### 5. 新增的 golden check

新增 `scripts/golden_check.py` 與 `scripts/golden_questions.yml`，用於對一組「黃金問題」呼叫 `query_lightrag`，檢查回應是否含 `references`，並輸出 PASS/FAIL 摘要。可在 LightRAG Server 啟動並完成 ingest 後執行，作為基本的健全度檢查（smoke test）。

### 6. 審查後補強（2026-06-15）

依主控審查提出的弱點，補強三項：

- **`scripts/ingest_sources.py`**：補上 `raw_sources/` → LightRAG 的匯入工具。預設 dry-run，列出檔案數與粗略 token 估算；`--execute` 才實際上傳，含 `--batch-size` / `--max-files` 保護。**待驗證**：上傳端點預設 `/documents/upload`（multipart），實際端點與 payload 須以實機 LightRAG 的 `/docs` 或 `openapi.json` 確認後調整（已於檔頭註解標註）。
- **`scripts/golden_check.py` 升級**：`golden_questions.yml` 每題可帶 `expected_keywords`，檢查回應是否命中關鍵詞（命中率低於門檻 → WARN），能抓「答得不對」而非只抓「沒回應」。向後相容：無關鍵詞的題目行為等同舊版。
- **CI 強化**：以 `gitleaks`（搭配 `.gitleaks.toml` 白名單放行 `.env.example` 佔位符）取代只抓 `sk-` 的簡易掃描，因 MiniMax 金鑰非 `sk-` 格式；新增 `ruff` lint（`pyproject.toml`，規則 E/F/I、line-length 120）。

驗證：`ruff check` 全通過、`pytest` 49 passed、`wiki_lint` 0 problems。
