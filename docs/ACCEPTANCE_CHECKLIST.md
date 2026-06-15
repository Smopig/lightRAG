# 最小可行驗收清單

## A. 專案結構

```bash
test -d ~/hybrid-knowledge-lab/raw_sources
test -d ~/hybrid-knowledge-lab/lightrag_workspace
test -d ~/hybrid-knowledge-lab/wiki
test -d ~/hybrid-knowledge-lab/schema
test -d ~/hybrid-knowledge-lab/scripts
test -d ~/hybrid-knowledge-lab/outputs
```

## B. 安全檢查

```bash
cd ~/hybrid-knowledge-lab
! grep -R "sk-\|API_KEY=.*[^X]\|token" .env.example README.md schema scripts 2>/dev/null
```

注意：不得把真實 API key 寫進 Git。

## C. 工具檢查

```bash
git --version
python3 --version
uv --version
ollama list
lightrag-server --help
```

## D. Wiki 檢查

```bash
cd ~/hybrid-knowledge-lab
python scripts/wiki_lint.py
```

允許初期有 orphan page 提醒；不允許 verified page 沒有 Sources。

## E. LightRAG 健康檢查

啟動 server 後：

```bash
curl http://localhost:9621/health
```

## F. 查詢測試

```bash
cd ~/hybrid-knowledge-lab
source .venv/bin/activate
python scripts/query_lightrag.py "請整理這批文件中的系統架構與主要模組"
```

## G. Wiki 編譯測試

```bash
cd ~/hybrid-knowledge-lab
source .venv/bin/activate
python scripts/compile_wiki_page.py "LightRAG 系統架構" "請整理 LightRAG 的系統架構、儲存層與查詢模式"
```

預期：產生 `wiki/queries/light_rag_系統架構.md` 或類似檔案，且 `wiki/log.md` 有 append 紀錄。
