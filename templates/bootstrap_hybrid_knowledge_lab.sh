#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="${LAB_DIR:-$HOME/hybrid-knowledge-lab}"

if [ -e "$LAB_DIR" ]; then
  echo "[STOP] $LAB_DIR already exists. Please inspect it before running bootstrap."
  exit 1
fi

mkdir -p "$LAB_DIR"/{raw_sources/{lightrag,project_docs,papers,inbox},lightrag_workspace,wiki/{entities,concepts,sources,synthesis,comparisons,queries},schema,scripts,outputs,docs}
cd "$LAB_DIR"

git init
cat > .gitignore <<'GITIGNORE'
.env
lightrag_workspace/
__pycache__/
.venv/
*.log
outputs/
.DS_Store
GITIGNORE

cat > wiki/index.md <<'WIKIINDEX'
---
title: Hybrid Knowledge Wiki Index
type: index
updated: 2026-06-11
---
# Hybrid Knowledge Wiki Index

## 核心入口
- [[concepts/system_architecture]]
- [[concepts/lightrag_layer]]
- [[concepts/wiki_layer]]
- [[concepts/agent_routing]]

## 最近更新
請查看 [[log]]。
WIKIINDEX

cat > wiki/log.md <<'WIKILOG'
---
title: Operation Log
type: log
---
# Operation Log

## [2026-06-11] init | 建立 Hybrid Knowledge Wiki
- 建立 index.md 與基本資料夾。
WIKILOG

cat > schema/AGENTS.md <<'AGENTS'
# Hybrid Knowledge Wiki Maintainer Rules

You maintain the wiki directory as a long-term knowledge base.

Rules:
1. Never overwrite raw_sources.
2. Every factual claim added to wiki pages must include a source note.
3. Prefer updating existing pages over creating near-duplicate pages.
4. Use full-path [[wikilink]] for related entities, concepts, projects, tools, and decisions.
5. If evidence is insufficient, add the statement under "Open Questions" instead of writing it as fact.
6. Append every ingest/query/lint/update action to wiki/log.md using this format:
   ## [YYYY-MM-DD] action | title
7. When new evidence contradicts old content, do not silently replace it. Add a "Conflict / Revision" section.
8. Use Traditional Chinese for human-facing explanations unless the source title/code/API name is English.
AGENTS

cat > schema/wiki_page_template.md <<'TEMPLATE'
---
title: 頁面標題
type: concept | entity | source | synthesis | comparison | query
status: draft | verified | needs_review
updated: YYYY-MM-DD
source_count: 0
related:
- [[concepts/example]]
---
# 頁面標題

## 摘要
用 3-5 句話說明這頁的核心內容。

## 核心知識
- 事實 A。[^src1]

## 與其他頁面的關係
- 參見 [[concepts/xxx]]。

## 開放問題
- [ ] 哪些地方需要回查原始資料？

## Sources
[^src1]: raw_sources/... 或 LightRAG reference id / file path / chunk 摘要
TEMPLATE

cat > schema/lint_rules.yml <<'LINT'
required_sections:
  - Sources
verified_requires_citations: true
wikilink_style: full_path
allow_orphan_pages:
  - index.md
  - log.md
LINT

cat > .env.example <<ENVEXAMPLE
# Server
HOST=0.0.0.0
PORT=9621
WORKING_DIR=$LAB_DIR/lightrag_workspace

# Language and extraction
SUMMARY_LANGUAGE=Chinese
ENTITY_EXTRACTION_USE_JSON=true
MAX_ASYNC_LLM=4
MAX_PARALLEL_INSERT=1
TIMEOUT=180

# Parser
LIGHTRAG_PARSER=*:native-teP,*:legacy-R
VLM_PROCESS_ENABLE=false

# LLM: MiniMax OpenAI-compatible. Confirm host/model in MiniMax console.
LLM_BINDING=openai
LLM_BINDING_HOST=https://api.minimax.io/v1
LLM_BINDING_API_KEY=YOUR_MINIMAX_API_KEY
LLM_MODEL=CONFIRM_WITH_MINIMAX_CONSOLE
KEYWORD_LLM_MODEL=CONFIRM_WITH_MINIMAX_CONSOLE
QUERY_LLM_MODEL=CONFIRM_WITH_MINIMAX_CONSOLE

# Embedding: Ollama local bge-m3
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
EMBEDDING_FUNC_MAX_ASYNC=4
EMBEDDING_BATCH_NUM=16

# Query references/debug
RERANK_BINDING=null
RERANK_BY_DEFAULT=false

# Optional auto-scan inbox
INPUT_DIR=$LAB_DIR/raw_sources/inbox
ENVEXAMPLE

cat > README.md <<'README'
# Hybrid Knowledge Lab

LightRAG + LLM Wiki 混合知識系統。

## 啟動流程

1. 複製 `.env.example` 為 `.env`。
2. 在 `.env` 填入 MiniMax API key 與確認後的 model ID。
3. 啟動 Ollama 並確認 `bge-m3` 已安裝。
4. 啟動 LightRAG Server。
5. 把原始資料放入 `raw_sources/`，再上傳或 scan 到 LightRAG。
6. 用 `scripts/compile_wiki_page.py` 把查詢結果編譯成 Wiki。
7. 用 `scripts/wiki_lint.py` 檢查 Wiki 品質。

## 安全規則

- `raw_sources/` 是不可變真相來源。
- `.env` 不得提交。
- `lightrag_workspace/` 是索引加工品，可備份但不要手改。
README

printf '[OK] Created %s\n' "$LAB_DIR"
