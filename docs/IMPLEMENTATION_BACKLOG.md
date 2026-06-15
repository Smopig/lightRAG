# LightRAG + LLM Wiki 建置 Backlog

## P0 — 啟動前確認

- [ ] 確認作業系統：Ubuntu / macOS / WSL。
- [ ] 確認目標路徑：`~/hybrid-knowledge-lab`。
- [ ] 確認是否已有同名資料夾；若有，不得直接覆寫。
- [ ] 確認 MiniMax API key 取得方式，但不得要求使用者把 key 貼進聊天記錄。
- [ ] 確認 Claude Code 主模型為 `best` 或 `opus`。
- [ ] 確認子代理存在且使用 `haiku` / `sonnet`。

## P1 — 專案骨架

- [ ] 建立資料夾：`raw_sources/`、`lightrag_workspace/`、`wiki/`、`schema/`、`scripts/`、`outputs/`。
- [ ] 建立 `.gitignore`。
- [ ] 建立 `README.md`。
- [ ] 建立 `docs/IMPLEMENTATION_NOTES.md`。

## P2 — 系統工具

- [ ] 檢查 Git。
- [ ] 檢查 Python 3.11/3.12。
- [ ] 檢查 uv。
- [ ] 檢查 Ollama。
- [ ] 檢查或拉取 `bge-m3`。
- [ ] 檢查 LightRAG Server 是否可安裝與啟動。

## P3 — 設定檔

- [ ] 建立 `.env.example`。
- [ ] 不建立含真實 key 的 `.env`；除非使用者在本機互動輸入。
- [ ] `WORKING_DIR` 必須用實際絕對路徑，不要留下 `$USER` 字面值。
- [ ] 不使用已被淘汰或未驗證的舊變數。
- [ ] MiniMax model ID 必須讓使用者依控制台確認。

## P4 — Wiki 層

- [ ] 建立 `wiki/index.md`。
- [ ] 建立 `wiki/log.md`。
- [ ] 建立 `schema/AGENTS.md`。
- [ ] 建立 `schema/wiki_page_template.md`。
- [ ] 建立 `schema/lint_rules.yml`。

## P5 — Scripts

- [ ] `scripts/query_lightrag.py`
- [ ] `scripts/compile_wiki_page.py`
- [ ] `scripts/wiki_lint.py`
- [ ] `scripts/route_query.py`
- [ ] 可選：`scripts/golden_check.py`

## P6 — 驗收

- [ ] `lightrag-server --help` 可執行。
- [ ] Ollama 可列出 `bge-m3`。
- [ ] `.env.example` 無真實 secret。
- [ ] Wiki lint 可執行。
- [ ] `query_lightrag.py` 能在 server 啟動後查詢 `/query`。
- [ ] `compile_wiki_page.py` 能產生 `wiki/queries/*.md`。
- [ ] README 足以讓使用者重跑流程。

## P7 — 進階補強

- [ ] 建立 golden question set。
- [ ] 建立備份與還原 SOP。
- [ ] 評估 PostgreSQL。
- [ ] 評估 Rerank。
- [ ] 評估 MCP 化。
