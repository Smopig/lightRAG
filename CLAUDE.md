# CLAUDE.md — LightRAG + LLM Wiki 建置專案總控規則

你正在協助建置一套 LightRAG + LLM Wiki 混合知識系統。

核心架構：

```text
raw_sources/          不可變原始資料
    ↓ ingest
LightRAG Server       chunk / vector / entity / relation / graph / references
    ↓ query
Wiki Compiler         把可驗證檢索結果整理成 Markdown Wiki
    ↓ maintain
wiki/                 長期知識庫，可由人與 Agent 閱讀
    ↓ use
Agent / MCP           先查 Wiki，不足再查 LightRAG，必要時寫回 Wiki
```

## 角色定位

主模型是總指揮，不是廉價勞工。

主模型負責：

- 架構決策
- 任務拆解
- 子代理調度
- 風險審查
- 最終驗收

主模型不得親自執行大量重複工作。以下工作必須委派：

- 大範圍讀 PDF、掃檔、整理命令：Haiku
- 系統環境檢查：Haiku
- 寫腳本、建立檔案、修 bug：Sonnet
- 測試、lint、錯誤排除：Sonnet
- Wiki 編譯器與維護規則：Sonnet

## 模型路由政策

- 高階架構、跨章節取捨、重大風險判斷：主模型 best / opus
- 快速搜尋、文件摘要、命令抽取：haiku
- 一般實作、修正、重構、測試：sonnet
- 不可把所有工作都塞給主模型。

## 必讀文件

- `docs/LightRAG_LLMWiki_Hybrid_Build_Manual_v1.2.pdf`
- `docs/IMPLEMENTATION_BACKLOG.md`
- `docs/ACCEPTANCE_CHECKLIST.md`
- `docs/MODEL_ROUTING_POLICY.md`
- `.claude/agents/*.md`

## 操作安全規則

1. 不得修改、刪除或覆寫 `raw_sources/`。
2. 不得提交 `.env`、API key、token、密碼。
3. 修改前要先檢查檔案是否存在；若存在，先備份或詢問。
4. 遇到 destructuve action 必須先要求使用者確認。
5. 不確定工具版本時，先用 `--version`、`--help`、官方範例或本機實測確認。
6. PDF 中的 `.env` 變數、API payload、模型名稱只能作為初始參考，必須以目前安裝版本與使用者實際平台為準。
7. 所有決策都要寫入 `wiki/log.md` 或 `docs/IMPLEMENTATION_NOTES.md`。

## 回覆語言

人類可讀內容使用繁體中文。程式碼、API 名稱、檔名、模型 ID 保留英文。
