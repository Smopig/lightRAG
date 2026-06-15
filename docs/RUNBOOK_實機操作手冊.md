# 實機操作手冊（Runbook）— 從零到查詢

> 給「第一次實機」的你。照著章節順序做，每一步都有：**做什麼 → 指令 → 預期看到什麼 → 出錯怎麼辦**。
> 適用：Ubuntu / WSL / macOS。指令以 Linux 為主，macOS 差異會特別標註。
>
> 整個流程分九步：
> 0. 前置檢查 → 1. 安裝工具 → 2. 設定 `.env` → 3. 啟動 Ollama 與 bge-m3 → 4. 啟動 LightRAG Server → 5. 放原始資料 → 6. 匯入（ingest）→ 7. 查詢 → 8. 編譯 Wiki → 9. 品質檢查與備份

---

## 重要前提（先讀 30 秒）

- 本 repo 的成果建在 **repo 根目錄**。下面所有指令都假設你**已經 `cd` 到 repo 根目錄**（也就是有 `scripts/`、`wiki/`、`.env.example` 的那層）。
- **絕對不要**把真實 API key 提交進 git。`.env` 已被 `.gitignore` 忽略，照手冊做就安全。
- 任何一步「卡住」，把終端機輸出整段貼給我，我幫你判斷。

確認你在正確目錄：

```bash
ls .env.example scripts/ wiki/    # 三個都要看得到，否則先 cd 到 repo 根目錄
```

---

## 步驟 0：前置檢查（2 分鐘）

**做什麼**：確認基本工具在不在。

```bash
git --version
python3 --version      # 需要 3.11 或 3.12
curl --version
```

**預期**：三個都印出版本號。
**出錯**：若 `python3` 不是 3.11/3.12，到步驟 1 一起處理。

---

## 步驟 1：安裝工具（uv）

**做什麼**：裝 `uv`（現代 Python 套件管理器，速度快）。

```bash
# Linux / macOS / WSL 通用
curl -LsSf https://astral.sh/uv/install.sh | sh

# 裝完後讓終端機認得它（或直接關掉終端機重開）
source ~/.bashrc 2>/dev/null || source ~/.zshrc 2>/dev/null || true

uv --version
```

**預期**：印出 `uv 0.x.x`。
**出錯**：若 `uv: command not found`，關閉終端機重新打開再試一次 `uv --version`。

接著用 uv 建立本專案專用的虛擬環境並安裝 LightRAG 與腳本依賴：

```bash
# 在 repo 根目錄
uv venv                              # 建立 .venv（已被 gitignore）
source .venv/bin/activate            # 啟用（之後每開新終端機都要先做這行）
uv pip install "lightrag-hku[api]"   # LightRAG Server 本體
uv pip install requests pyyaml python-frontmatter rich   # 腳本依賴

lightrag-server --help               # 驗證安裝成功
```

**預期**：`lightrag-server --help` 印出一長串參數說明。
**出錯**：
- 安裝失敗多半是網路或套件名問題，把錯誤貼給我。
- ⚠️ **重點**：`--help` 印出的參數，請大致看一下你這個版本支援哪些。我們的 `.env` 是依手冊寫的，**個別變數名可能因版本不同而要微調**（見步驟 2 的提醒）。

> 💡 我們也準備了 `scripts/setup_env.sh` 自動做上面這些檢查與安裝。你想自動跑的話：`bash scripts/setup_env.sh`。但第一次建議手動跑、看清楚每一步。

---

## 步驟 2：設定 `.env`（填入你的 MiniMax 金鑰）

**做什麼**：把範本複製成正式設定檔，填入真實金鑰。

```bash
cp .env.example .env
```

然後用編輯器（`nano .env` 或 `vim .env`）打開 `.env`，**只改這一行**，把佔位符換成你的真實 MiniMax API key：

```ini
LLM_BINDING_API_KEY=這裡貼上你的真實金鑰
```

其餘預設值（已幫你填好）：

| 變數 | 預設值 | 說明 |
|---|---|---|
| `LLM_MODEL` | `Minimax-M2.5` | 你確認過的 model ID |
| `LLM_BINDING_HOST` | `https://api.minimax.io/v1` | ⚠️ 若你是**中國站**帳號，網域可能不同，以控制台為準 |
| `EMBEDDING_MODEL` | `bge-m3:latest` | 由本地 Ollama 提供 |
| `WORKING_DIR` | `./lightrag_workspace` | LightRAG 的資料夾（相對 repo 根） |
| `PORT` | `9621` | Server 連接埠 |

保護金鑰不被別人讀（建議）：

```bash
chmod 600 .env
```

**驗證沒填錯、也沒不小心要提交金鑰**：

```bash
git status            # .env 不應該出現在清單裡（被 gitignore 了）
grep LLM_BINDING_API_KEY .env   # 確認已換成真實值、不是 YOUR_MINIMAX_API_KEY
```

**⚠️ 版本相容提醒**：若步驟 4 啟動 server 時報「未知變數」或「啟動失敗」，通常是某個 `.env` 變數名你的版本不認得（手冊頁 8-9 就警告過 `ENTITY_TYPES` 這類舊變數）。把報錯貼給我，我幫你對照修正，並會記到 `docs/IMPLEMENTATION_NOTES.md`。

---

## 步驟 3：啟動 Ollama 並下載 bge-m3（embedding 模型）

**做什麼**：LightRAG 需要把文字轉成向量，這由本地的 Ollama + bge-m3 負責。

```bash
# 安裝 Ollama（Linux）
curl -fsSL https://ollama.com/install.sh | sh
# macOS：請改到 https://ollama.com/download 下載 App 安裝
```

開**一個新的終端機分頁**，啟動 Ollama 服務並保持它開著：

```bash
ollama serve
```

回到**原本的終端機**，下載 embedding 模型並確認：

```bash
ollama pull bge-m3
ollama list            # 應該看到 bge-m3
```

**預期**：`ollama list` 列表中有 `bge-m3`。
**出錯**：
- `ollama: command not found` → 安裝沒成功或要重開終端機。
- macOS 上 `ollama serve` 若說 already running，代表 App 已在背景跑，直接做 `ollama pull bge-m3` 即可。

---

## 步驟 4：啟動 LightRAG Server

**做什麼**：把設定載入環境變數後啟動 server。**這個終端機要一直開著**（server 在前景跑）。

```bash
# 在 repo 根目錄、且已 source .venv/bin/activate
set -a
source .env       # 載入 .env 所有變數到環境
set +a
lightrag-server
```

**預期**：印出啟動日誌，最後停在「listening / running on 0.0.0.0:9621」之類的訊息，游標不會跳回（代表它在持續運作）。

**驗證健康**（再開一個新終端機分頁）：

```bash
curl http://localhost:9621/health
```

**預期**：回傳一段 JSON，狀態類似 `{"status":"healthy"...}`。
**出錯**：
- 連不上 → server 那個終端機是不是有報錯停掉了？把它的輸出貼給我。
- 報「未知變數 / 啟動失敗」→ 見步驟 2 的版本相容提醒。

> 💡 開瀏覽器到 `http://localhost:9621/docs` 可以看到互動式 API 文件與 WebUI——之後步驟 6 的「真實 API 端點」就用這裡確認。

---

## 步驟 5：放入原始資料

**做什麼**：把你要建知識庫的檔案放進 `raw_sources/`（PDF、Markdown、txt 等）。

```bash
# 範例：把檔案放到 inbox 子資料夾
cp ~/我的文件/某報告.pdf raw_sources/inbox/
ls raw_sources/inbox/
```

**規則**：`raw_sources/` 是「不可變真相來源」，只放不刪改。

---

## 步驟 6：匯入（ingest）— 先估算，再實際匯入

**做什麼**：把 `raw_sources/` 的檔案送進 LightRAG。我們的腳本**預設只估算、不真的上傳**，避免你一次丟太多、帳單爆掉。

**第一步：先 dry-run 看看會處理幾個檔、大約多少 token**

```bash
python scripts/ingest_sources.py
# 只掃某個子資料夾：
python scripts/ingest_sources.py --subdir inbox
```

**預期**：列出檔案數、總大小、粗略 token 估算，最後提示「加 `--execute` 才會真的上傳」。

**第二步：確認沒問題後，實際上傳**

```bash
python scripts/ingest_sources.py --subdir inbox --execute --batch-size 5
```

**⚠️ 非常重要**：這支腳本的**上傳端點是預設值 `/documents/upload`，尚未在你的版本實測過**。第一次跑 `--execute` 若報 404 / 400，**先別慌**，這是預期內的「待驗證」項目：
1. 打開 `http://localhost:9621/docs`，找上傳文件的真實端點名稱與參數。
2. 把端點資訊貼給我，我幫你把 `scripts/ingest_sources.py` 的 `upload_document()` 改成正確的，並記錄到 `IMPLEMENTATION_NOTES.md`。

**第三步：確認匯入狀態**

到 `http://localhost:9621/docs` 或 WebUI 看文件狀態是否變成 `processed`（完成）。若卡在 `processing`，見 `docs/V1.2_ADVANCED_OPERATIONS.md` 第 5 節 SOP。

---

## 步驟 7：第一次查詢

**做什麼**：問知識庫一個問題，確認查得到、且有附來源。

```bash
python scripts/query_lightrag.py "請整理這批文件中的系統架構與主要模組"
```

**預期**：印出一段 JSON，裡面有 `response`（答案）和 `references`（來源）。

**⚠️ 待驗證**：若 JSON 的欄位名不是 `response` / `references`（不同 LightRAG 版本可能叫別的名字），把實際 JSON 貼給我，我幫你校準 `query_lightrag.py` 與 `compile_wiki_page.py` 的欄位對應——這是手冊頁 15 特別警告過的點。

---

## 步驟 8：把查詢結果編譯成 Wiki 頁

**做什麼**：把一次查詢整理成一頁可長期保存、可驗證的 Markdown。

```bash
python scripts/compile_wiki_page.py "LightRAG 系統架構" "請整理 LightRAG 的系統架構、儲存層與查詢模式"
```

**預期**：
- 在 `wiki/queries/` 下產生一個 `.md` 檔（檔名依標題）。
- `wiki/log.md` 自動多一筆 `compile` 紀錄。

**檢視**：

```bash
ls wiki/queries/
cat wiki/queries/*.md | head -40
```

---

## 步驟 9：品質檢查與備份

**Wiki 品質檢查**（不需 server）：

```bash
python scripts/wiki_lint.py
```

**預期**：`Total problems: 0`（初期允許 orphan 提醒，但不允許 verified 頁缺 Sources）。

**黃金問題集回歸測試**（需 server，已 ingest）：

```bash
python scripts/golden_check.py
# 想嚴格一點看關鍵詞命中：
python scripts/golden_check.py --keyword-threshold 0.6
```

**預期**：每題印 `PASS` / `WARN`（關鍵詞命中偏低）/ `FAIL`（沒回應或無來源），最後一行統計。

**整套 smoke test 一鍵跑**：

```bash
bash scripts/smoke_test.sh
```

**備份（含自動還原演練）**：

```bash
bash scripts/backup_lab.sh
# 備份檔在 outputs/backups/ 下，腳本會自動解開驗證，看到 [OK] 才算成功
```

---

## 常見問題速查

| 症狀 | 可能原因 | 怎麼辦 |
|---|---|---|
| `command not found: uv / ollama / lightrag-server` | 沒裝或終端機沒重載 | 關掉終端機重開，或回對應步驟重裝 |
| `curl /health` 連不上 | server 沒起來或報錯停了 | 看 server 終端機輸出，貼給我 |
| server 啟動報「未知變數」 | `.env` 有你版本不認得的變數 | 貼錯誤給我，對照修正 |
| ingest `--execute` 報 404/400 | 上傳端點待驗證 | 到 `/docs` 找真實端點，貼給我改 |
| query JSON 欄位對不上 | 不同版本欄位名不同 | 貼實際 JSON 給我校準腳本 |
| 想刪掉某份已匯入文件 | 圖譜清理有眉角 | 見 `V1.2_ADVANCED_OPERATIONS.md` §1 |

---

## 每次重新開機後的最短啟動流程

```bash
cd <你的 repo 根目錄>
source .venv/bin/activate
ollama serve            # 另一個分頁，保持開著（macOS 用 App 則免）
set -a; source .env; set +a
lightrag-server         # 另一個分頁，保持開著
# 然後就能 query / compile / golden_check
```

---

## 需要我陪你走嗎？

你可以照這份手冊自己做；**任何一步卡住或輸出看不懂，把終端機內容整段貼給我**，我會：
1. 判斷是哪一步、什麼原因。
2. 給你下一個明確指令。
3. 若是腳本要配合你的版本調整（ingest 端點、query 欄位），我直接改好程式並更新文件。

兩個「待驗證」的點（ingest 上傳端點、query 回傳欄位）幾乎一定需要依你的實機版本微調一次，這是正常的，不是出錯。
