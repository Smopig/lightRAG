---
title: Operation Log
type: log
---
# Operation Log

## [2026-06-15] init | 建立 Hybrid Knowledge Wiki
- 建立 index.md 與基本資料夾。

## [2026-06-15] build | 完成系統骨架建置（PR #1）
- 建立 P1–P7 全部產出：骨架、.env.example（MiniMax Minimax-M2.5 + Ollama bge-m3，key 用佔位符）、scripts、運維腳本、Wiki 種子頁、v1.2 運維手冊、CI、離線測試。
- 決策：成果建在 repo 根（remote 容器需 git 保存，非 ~/hybrid-knowledge-lab）；WORKING_DIR 用相對路徑；不在容器安裝系統套件（只建檔）。
- PostgreSQL / Rerank 第一版不採用；MCP 化列為下一階段第一任務（詳見 docs/V1.2_ADVANCED_OPERATIONS.md）。
- 驗證：pytest 23 passed、wiki_lint 0 problems、smoke_test PASS=5/FAIL=0/SKIP=5、CI success。
- 保留：真實 server 端到端驗收需於本機執行 setup_env.sh + smoke_test.sh。
