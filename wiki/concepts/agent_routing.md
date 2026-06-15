---
title: Agent 查詢與寫回路由
type: concept
status: draft
updated: 2026-06-15
source_count: 2
related:
- [[concepts/system_architecture]]
- [[concepts/lightrag_layer]]
- [[concepts/wiki_layer]]
---
# Agent 查詢與寫回路由

## 摘要
Agent / MCP 在回答問題時遵循固定順序：先查 [[concepts/wiki_layer]]，若資訊不足再查 [[concepts/lightrag_layer]]，必要時將新知識整理後寫回 Wiki。此路由邏輯由 `scripts/route_query.py` 實作。[^src1][^src2]

## 核心知識
- 查詢優先序為 Wiki → LightRAG，避免每次都對 LightRAG 重複檢索相同問題。[^src1]
- 當 LightRAG 回傳的結果具備可驗證來源時，可由 Wiki Compiler 整理後寫回 `wiki/`，形成知識庫的持續維護循環。[^src1]
- 寫回 Wiki 時須遵循 `schema/AGENTS.md` 的維護規則，例如附來源、避免重複頁面、記錄至 `wiki/log.md`。[^src3]
- `scripts/route_query.py` 是此路由邏輯的程式實作位置。[^src2]

## 與其他頁面的關係
- 整體資料流與五層架構參見 [[concepts/system_architecture]]。
- 「不足再查」的對象即 [[concepts/lightrag_layer]]。
- 「寫回 Wiki」須符合 [[concepts/wiki_layer]] 的格式與 lint 規則。

## 開放問題
- [ ] `route_query.py` 判斷「Wiki 資訊不足」的具體條件（例如關鍵字命中率、頁面 status）尚待補充說明。

## Sources
[^src1]: CLAUDE.md（核心架構圖：Agent / MCP 先查 Wiki，不足再查 LightRAG，必要時寫回 Wiki）
[^src2]: scripts/route_query.py
[^src3]: schema/AGENTS.md
