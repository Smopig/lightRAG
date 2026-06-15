---
title: 整體混合架構
type: concept
status: draft
updated: 2026-06-15
source_count: 2
related:
- [[concepts/lightrag_layer]]
- [[concepts/wiki_layer]]
- [[concepts/agent_routing]]
---
# 整體混合架構

## 摘要
本專案採用 raw_sources → LightRAG → Wiki Compiler → wiki → Agent/MCP 的五層資料流。原始資料不可變，LightRAG 負責檢索與圖譜建構，Wiki Compiler 將可驗證的檢索結果整理成長期知識庫，最後由 Agent/MCP 讀取並維護。[^src1]

## 核心知識
- `raw_sources/` 為不可變的原始資料層，禁止修改、刪除或覆寫。[^src1]
- LightRAG Server 對原始資料進行 chunk、vector、entity、relation、graph 與 reference 的建構，並提供 `/query`。[^src1]
- Wiki Compiler 將 LightRAG 的可驗證檢索結果整理為 Markdown Wiki。[^src1]
- `wiki/` 是長期知識庫，供人與 Agent 閱讀,並保留來源引用。[^src1]
- Agent / MCP 的查詢順序：先查 Wiki，不足再查 LightRAG，必要時寫回 Wiki。[^src1]

## 與其他頁面的關係
- LightRAG 層細節參見 [[concepts/lightrag_layer]]。
- Wiki 層維護規則參見 [[concepts/wiki_layer]]。
- Agent 查詢與寫回流程參見 [[concepts/agent_routing]]。

## 開放問題
- [ ] 各層之間的資料格式（如 LightRAG 回傳的 reference id）是否已在實作中固定？

## Sources
[^src1]: CLAUDE.md（核心架構圖與角色定位章節）
