---
title: LightRAG 層職責
type: concept
status: draft
updated: 2026-06-15
source_count: 2
related:
- [[concepts/system_architecture]]
- [[concepts/wiki_layer]]
- [[concepts/agent_routing]]
---
# LightRAG 層職責

## 摘要
LightRAG 層負責將 `raw_sources/` 中的原始資料轉換為可檢索的知識結構，包括 chunk、向量、實體、關係與圖譜，並透過 `/query` 提供多種檢索模式。embedding 與生成模型分別使用 Ollama bge-m3 與 MiniMax LLM。[^src1]

## 核心知識
- LightRAG Server 對原始資料進行 ingest，產出 chunk / vector / entity / relation / graph / references。[^src1]
- `/query` 支援多種模式：`mix`、`hybrid`、`local`、`global`。[^src2]
- Embedding 模型採用 Ollama bge-m3。[^src2]
- LLM 推論使用 MiniMax。[^src2]
- LightRAG 層的輸出是 Wiki Compiler 的輸入，Wiki Compiler 會將檢索結果整理成 Markdown 並保留來源引用。[^src1]

## 與其他頁面的關係
- 整體資料流參見 [[concepts/system_architecture]]。
- LightRAG 檢索結果如何被整理成 Wiki 頁面參見 [[concepts/wiki_layer]]。
- Agent 何時查詢 LightRAG 參見 [[concepts/agent_routing]]。

## 開放問題
- [ ] 四種 `/query` 模式（mix/hybrid/local/global）在本專案中的選用準則尚待補充。
- [ ] PDF 中的模型名稱與 `.env` 設定需以目前安裝版本為準再次確認。[^src1]

## Sources
[^src1]: CLAUDE.md（核心架構圖、操作安全規則第 6 點）
[^src2]: docs/LightRAG_LLMWiki_Hybrid_Build_Manual_v1.2.pdf（LightRAG /query 模式與 embedding/LLM 設定章節）
