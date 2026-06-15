---
title: Wiki 層職責
type: concept
status: draft
updated: 2026-06-15
source_count: 2
related:
- [[concepts/system_architecture]]
- [[concepts/lightrag_layer]]
- [[concepts/agent_routing]]
---
# Wiki 層職責

## 摘要
Wiki 層是長期知識庫，內容必須可驗證並保留來源（Sources），資料只能由 LightRAG 層單向流入，不可回流污染原始資料。所有頁面須遵循統一的 page template 與 lint 規則。[^src1][^src2]

## 核心知識
- Wiki 內容來自 Wiki Compiler 對 LightRAG 可驗證檢索結果的整理,屬於單向資料流（raw_sources → LightRAG → Wiki），Wiki 不得回頭修改 `raw_sources/`。[^src1]
- 每個頁面須符合 `schema/wiki_page_template.md` 的格式，包含 frontmatter（title、type、status、updated、source_count、related）與 `## Sources` 區。[^src3]
- lint 規則（`schema/lint_rules.yml`）要求每頁必須有 Sources 區段；`status: verified` 的頁面必須有逐句引用 [^src1] 形式的來源。[^src4]
- 維護規則（`schema/AGENTS.md`）：每筆新增事實都要附來源、優先更新既有頁面而非建立重複頁、用 full-path `[[wikilink]]` 互連、證據不足放入「開放問題」、所有動作記錄至 `wiki/log.md`。[^src5]

## 與其他頁面的關係
- Wiki 在整體架構中的位置參見 [[concepts/system_architecture]]。
- Wiki 內容來源於 [[concepts/lightrag_layer]] 的檢索結果。
- Agent 讀寫 Wiki 的順序參見 [[concepts/agent_routing]]。

## 開放問題
- [ ] `compile_wiki_page.py` 的自動化編譯流程與本頁規則的對應細節待補充。

## Sources
[^src1]: CLAUDE.md（核心架構圖、操作安全規則第 1 點）
[^src2]: docs/LightRAG_LLMWiki_Hybrid_Build_Manual_v1.2.pdf（Wiki Compiler 章節）
[^src3]: schema/wiki_page_template.md
[^src4]: schema/lint_rules.yml
[^src5]: schema/AGENTS.md
