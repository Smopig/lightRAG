#!/usr/bin/env bash
# backup_lab.sh
# 將 wiki/、schema/、.env.example（不含 .env）、lightrag_workspace/ 打包成
# outputs/backups/lab_backup_<UTC timestamp>.tar.gz
#
# 重點：打包後立即進行「還原演練」——把備份檔解到暫存目錄並驗證關鍵檔案存在，
# 驗證成功才保留備份並印出 [OK]；驗證失敗則刪除半成品備份並以非 0 結束。
#
# 絕不備份 .env 或任何 secret。

set -euo pipefail

# ---- 設定 ----------------------------------------------------------------
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="outputs/backups"
BACKUP_NAME="lab_backup_${TIMESTAMP}.tar.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# 要打包的項目（相對 REPO_ROOT）。.env.example 一定備份，.env 絕不備份。
ITEMS_TO_BACKUP=()
for item in wiki schema .env.example lightrag_workspace; do
  if [ -e "$item" ]; then
    ITEMS_TO_BACKUP+=("$item")
  else
    echo "[WARN] 找不到 $item，略過。"
  fi
done

if [ ${#ITEMS_TO_BACKUP[@]} -eq 0 ]; then
  echo "[FAIL] 沒有任何項目可備份，中止。" >&2
  exit 1
fi

# ---- 打包 ------------------------------------------------------------------
mkdir -p "$BACKUP_DIR"
echo "[INFO] 打包以下項目：${ITEMS_TO_BACKUP[*]}"
echo "[INFO] 輸出檔案：${BACKUP_PATH}"

tar czf "$BACKUP_PATH" "${ITEMS_TO_BACKUP[@]}"

# ---- 安全檢查：確認備份內沒有 .env -----------------------------------------
if tar tzf "$BACKUP_PATH" | grep -E '(^|/)\.env$' >/dev/null 2>&1; then
  echo "[FAIL] 備份內容包含 .env，移除此備份並中止！" >&2
  rm -f "$BACKUP_PATH"
  exit 1
fi

# ---- 還原演練 ---------------------------------------------------------------
RESTORE_DRILL_DIR="$(mktemp -d "${TMPDIR:-/tmp}/lab_restore_drill.XXXXXX")"
echo "[INFO] 還原演練目錄：${RESTORE_DRILL_DIR}"

cleanup() {
  rm -rf "$RESTORE_DRILL_DIR"
}
trap cleanup EXIT

tar xzf "$BACKUP_PATH" -C "$RESTORE_DRILL_DIR"

# ---- 驗證關鍵檔案 ------------------------------------------------------------
DRILL_OK=true

check_path() {
  local rel_path="$1"
  if [ -e "${RESTORE_DRILL_DIR}/${rel_path}" ]; then
    echo "[OK]   還原演練：找到 ${rel_path}"
  else
    echo "[FAIL] 還原演練：缺少 ${rel_path}"
    DRILL_OK=false
  fi
}

# 只檢查實際打包進去的項目對應的關鍵檔案
for item in "${ITEMS_TO_BACKUP[@]}"; do
  case "$item" in
    wiki)
      check_path "wiki/index.md"
      ;;
    schema)
      check_path "schema/lint_rules.yml"
      ;;
    .env.example)
      check_path ".env.example"
      ;;
    lightrag_workspace)
      # lightrag_workspace 可能是空目錄，存在即可
      if [ -d "${RESTORE_DRILL_DIR}/lightrag_workspace" ]; then
        echo "[OK]   還原演練：找到 lightrag_workspace/"
      else
        echo "[FAIL] 還原演練：缺少 lightrag_workspace/"
        DRILL_OK=false
      fi
      ;;
  esac
done

if [ "$DRILL_OK" = true ]; then
  echo "[OK] 備份完成且還原演練通過：${BACKUP_PATH}"
  exit 0
else
  echo "[FAIL] 還原演練未通過，移除備份檔：${BACKUP_PATH}" >&2
  rm -f "$BACKUP_PATH"
  exit 1
fi
