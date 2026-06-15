#!/usr/bin/env bash
# setup_env.sh
# 冪等的環境安裝腳本：檢查並安裝 uv / ollama / bge-m3 / Python 套件 / .env
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> 工作目錄：$ROOT_DIR"

# -------------------------------------------------------------------------
# 1. 檢查 uv
# -------------------------------------------------------------------------
if command -v uv >/dev/null 2>&1; then
    echo "[SKIP] uv 已安裝：$(uv --version)"
else
    echo "[INFO] 未偵測到 uv，請手動執行以下指令安裝（不會自動安裝系統層套件）："
    echo "       curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# -------------------------------------------------------------------------
# 2. 檢查 ollama
# -------------------------------------------------------------------------
if command -v ollama >/dev/null 2>&1; then
    echo "[SKIP] ollama 已安裝：$(ollama --version 2>/dev/null || echo '版本未知')"

    # 2.1 確認 bge-m3 是否已下載
    if ollama list 2>/dev/null | grep -q "bge-m3"; then
        echo "[SKIP] bge-m3 embedding 模型已存在"
    else
        echo "[INFO] 正在下載 bge-m3 embedding 模型..."
        if ollama pull bge-m3; then
            echo "[PASS] bge-m3 下載完成"
        else
            echo "[FAIL] bge-m3 下載失敗，請確認 ollama serve 是否已啟動"
        fi
    fi
else
    echo "[INFO] 未偵測到 ollama，請手動執行以下指令安裝（不會自動 sudo 安裝）："
    echo "       curl -fsSL https://ollama.com/install.sh | sh"
    echo "[INFO] 安裝後請執行：ollama serve  以及  ollama pull bge-m3"
fi

# -------------------------------------------------------------------------
# 3. 建立 .venv 並安裝套件（需 uv）
# -------------------------------------------------------------------------
if command -v uv >/dev/null 2>&1; then
    if [ -d "$ROOT_DIR/.venv" ]; then
        echo "[SKIP] .venv 已存在"
    else
        echo "[INFO] 建立虛擬環境 .venv ..."
        uv venv
        echo "[PASS] .venv 建立完成"
    fi

    echo "[INFO] 安裝/更新 Python 套件 (lightrag-hku[api], requests, pyyaml, python-frontmatter, rich) ..."
    if uv pip install "lightrag-hku[api]" requests pyyaml python-frontmatter rich; then
        echo "[PASS] Python 套件安裝完成"
    else
        echo "[FAIL] Python 套件安裝失敗，請檢查網路或套件名稱"
    fi
else
    echo "[SKIP] 因 uv 不存在，跳過 .venv 建立與套件安裝"
fi

# -------------------------------------------------------------------------
# 4. 準備 .env
# -------------------------------------------------------------------------
if [ -f "$ROOT_DIR/.env" ]; then
    echo "[SKIP] .env 已存在，不覆寫"
else
    if [ -f "$ROOT_DIR/.env.example" ]; then
        cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
        echo "[PASS] 已從 .env.example 複製為 .env"
        echo "[INFO] 請編輯 .env，填入以下項目："
        echo "       - LLM_BINDING_API_KEY (MiniMax API key)"
        echo "       - 確認 LLM_MODEL / KEYWORD_LLM_MODEL / QUERY_LLM_MODEL 是否正確"
    else
        echo "[FAIL] 找不到 .env.example，無法建立 .env"
    fi
fi

echo "==> setup_env.sh 執行完畢"
