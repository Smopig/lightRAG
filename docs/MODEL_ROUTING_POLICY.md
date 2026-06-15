# Claude Code 模型路由政策

## 目標

主模型使用最強模型負責規劃與審查；實作、搜尋、測試與重複工作交給 Haiku / Sonnet，以降低 token 成本。

## 啟動建議

```bash
claude --model best
```

若帳號或版本不支援 `best`：

```bash
claude --model opus
```

在 Claude Code 內也可以使用：

```text
/model best
```

或：

```text
/model opus
```

## 重要警告

不要設定：

```bash
export CLAUDE_CODE_SUBAGENT_MODEL=inherit
```

也不要設定成 `opus`、`best`、`fable`。

原因：`CLAUDE_CODE_SUBAGENT_MODEL` 會覆蓋每個 subagent 檔案中的 `model` frontmatter，導致所有子代理被迫使用同一模型，破壞省 token 設計。

## 任務分配表

| 任務類型 | 指定模型 | 指定子代理 | 原因 |
|---|---:|---|---|
| PDF 章節掃描、命令抽取 | haiku | haiku-pdf-explorer | 低成本、快速、讀取型工作 |
| 系統環境檢查 | haiku | haiku-environment-auditor | 命令多但推理低 |
| 建立專案檔案與 Python 腳本 | sonnet | sonnet-implementer | 需要可靠實作能力 |
| 測試、lint、錯誤排除 | sonnet | sonnet-tester | 需要讀錯誤與修正建議 |
| Wiki 編譯器與 schema | sonnet | sonnet-wiki-compiler | 需要穩定產出結構化檔案 |
| 架構取捨、重大風險、最後驗收 | best / opus | 主模型 | 需要最高推理品質 |

## 主模型不可做的事

- 不要親自大量掃描整份 PDF。
- 不要親自逐檔檢查所有生成檔案。
- 不要親自反覆執行測試直到通過。
- 不要親自產生大量 boilerplate 後又自己審查。

## 主模型必須做的事

- 拆任務。
- 指派子代理。
- 收斂子代理輸出。
- 對重大風險做決策。
- 要求缺失的 API key 或使用者確認。
- 最終驗收。
