#!/usr/bin/env bash
# smoke_test.sh
# 端到端 smoke test，對應 docs/ACCEPTANCE_CHECKLIST.md
# 設計原則：單項失敗不中止整支腳本（除非 wiki_lint 真的失敗），最後印出總結
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PASS=0
FAIL=0
SKIP=0

pass() { echo "[PASS] $1"; PASS=$((PASS+1)); }
fail() { echo "[FAIL] $1"; FAIL=$((FAIL+1)); }
skip() { echo "[SKIP] $1"; SKIP=$((SKIP+1)); }

echo "==================================================="
echo " LightRAG + LLM Wiki Smoke Test"
echo "==================================================="

# -------------------------------------------------------------------------
# C. 工具版本檢查
# -------------------------------------------------------------------------
echo "--- 工具版本檢查 ---"

if command -v git >/dev/null 2>&1; then
    pass "git: $(git --version)"
else
    fail "git 未安裝"
fi

if command -v python3 >/dev/null 2>&1; then
    pass "python3: $(python3 --version)"
else
    fail "python3 未安裝"
fi

if command -v uv >/dev/null 2>&1; then
    pass "uv: $(uv --version)"
else
    fail "uv 未安裝（請參考 scripts/setup_env.sh）"
fi

if command -v ollama >/dev/null 2>&1; then
    if ollama list 2>/dev/null | grep -q "bge-m3"; then
        pass "ollama 已安裝，且 bge-m3 模型存在"
    else
        fail "ollama 已安裝，但找不到 bge-m3 模型（請執行 ollama pull bge-m3）"
    fi
else
    skip "ollama 未安裝，跳過 bge-m3 檢查"
fi

if command -v lightrag-server >/dev/null 2>&1; then
    if lightrag-server --help >/dev/null 2>&1; then
        pass "lightrag-server --help 可正常執行"
    else
        fail "lightrag-server --help 執行失敗"
    fi
else
    skip "lightrag-server 未安裝（請執行 uv tool install \"lightrag-hku[api]\" 或 setup_env.sh）"
fi

# -------------------------------------------------------------------------
# B. 安全檢查：.env.example 不可含真實 secret
# -------------------------------------------------------------------------
echo "--- 安全檢查 ---"

if [ -f ".env.example" ]; then
    if grep -RnE "sk-[A-Za-z0-9]{10,}|API_KEY=.*[^X_]$" .env.example 2>/dev/null | grep -v "YOUR_" >/dev/null; then
        fail ".env.example 可能含有真實 secret，請手動檢查"
    else
        pass ".env.example 未發現真實 secret"
    fi
else
    fail "找不到 .env.example"
fi

# -------------------------------------------------------------------------
# E. LightRAG 健康檢查
# -------------------------------------------------------------------------
echo "--- LightRAG Server 健康檢查 ---"

SERVER_UP=0
if curl -sf --max-time 3 http://localhost:9621/health >/dev/null 2>&1; then
    pass "LightRAG server 健康檢查通過 (http://localhost:9621/health)"
    SERVER_UP=1
else
    skip "LightRAG server 未啟動或無回應，跳過健康檢查（請參考 README 啟動流程）"
fi

# -------------------------------------------------------------------------
# D. Wiki Lint 檢查（失敗會影響整體 exit code）
# -------------------------------------------------------------------------
echo "--- Wiki Lint 檢查 ---"

LINT_FAILED=0
if [ -f "scripts/wiki_lint.py" ]; then
    if python3 scripts/wiki_lint.py; then
        pass "wiki_lint.py 執行通過"
    else
        fail "wiki_lint.py 檢查失敗"
        LINT_FAILED=1
    fi
else
    skip "找不到 scripts/wiki_lint.py"
fi

# -------------------------------------------------------------------------
# F/G. 查詢與 wiki 編譯示範（僅在 server 健康時執行）
# -------------------------------------------------------------------------
echo "--- 查詢 / Wiki 編譯示範 ---"

if [ "$SERVER_UP" -eq 1 ]; then
    if [ -f "scripts/query_lightrag.py" ]; then
        if python3 scripts/query_lightrag.py "請整理主要架構"; then
            pass "query_lightrag.py 示範查詢成功"
        else
            fail "query_lightrag.py 示範查詢失敗"
        fi
    else
        skip "找不到 scripts/query_lightrag.py"
    fi

    if [ -f "scripts/compile_wiki_page.py" ]; then
        if python3 scripts/compile_wiki_page.py "Smoke Test 頁面" "請說明 LightRAG 的整體架構"; then
            pass "compile_wiki_page.py 示範編譯成功"
        else
            fail "compile_wiki_page.py 示範編譯失敗"
        fi
    else
        skip "找不到 scripts/compile_wiki_page.py"
    fi
else
    skip "LightRAG server 未啟動，跳過 query_lightrag.py 示範"
    skip "LightRAG server 未啟動，跳過 compile_wiki_page.py 示範"
fi

# -------------------------------------------------------------------------
# 總結
# -------------------------------------------------------------------------
echo "==================================================="
echo " 總結：PASS=$PASS  FAIL=$FAIL  SKIP=$SKIP"
echo "==================================================="

if [ "$LINT_FAILED" -eq 1 ]; then
    echo "wiki_lint 檢查失敗，視為整體失敗。"
    exit 1
fi

exit 0
