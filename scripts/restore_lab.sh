#!/usr/bin/env bash
# restore_lab.sh
# 將 backup_lab.sh 產生的備份檔還原到指定目錄。
#
# 用法：
#   bash scripts/restore_lab.sh <backup.tar.gz>                 # 預設還原到暫存目錄做演練
#   bash scripts/restore_lab.sh <backup.tar.gz> --target <dir>  # 指定還原目標
#   bash scripts/restore_lab.sh <backup.tar.gz> --target <dir> --force  # 覆寫既有目錄
#
# 對既有非空目錄會先警告不覆寫，需 --force 才會覆寫。

set -euo pipefail

usage() {
  echo "用法: $0 <backup.tar.gz> [--target <dir>] [--force]" >&2
  exit 1
}

if [ $# -lt 1 ]; then
  usage
fi

BACKUP_FILE="$1"
shift

TARGET_DIR=""
FORCE=false

while [ $# -gt 0 ]; do
  case "$1" in
    --target)
      shift
      [ $# -gt 0 ] || usage
      TARGET_DIR="$1"
      ;;
    --force)
      FORCE=true
      ;;
    *)
      echo "[WARN] 未知參數：$1，忽略。"
      ;;
  esac
  shift
done

if [ ! -f "$BACKUP_FILE" ]; then
  echo "[FAIL] 找不到備份檔：${BACKUP_FILE}" >&2
  exit 1
fi

# 預設目標為暫存目錄（還原演練模式）
DRILL_MODE=false
if [ -z "$TARGET_DIR" ]; then
  TARGET_DIR="$(mktemp -d "${TMPDIR:-/tmp}/lab_restore.XXXXXX")"
  DRILL_MODE=true
  echo "[INFO] 未指定 --target，使用暫存目錄做還原演練：${TARGET_DIR}"
fi

# ---- 既有目錄保護 -----------------------------------------------------------
if [ -d "$TARGET_DIR" ] && [ "$(ls -A "$TARGET_DIR" 2>/dev/null)" ]; then
  if [ "$DRILL_MODE" = true ]; then
    : # 暫存目錄本來就是空的新目錄，不會觸發這裡
  elif [ "$FORCE" != true ]; then
    echo "[FAIL] 目標目錄非空：${TARGET_DIR}" >&2
    echo "       為避免覆寫既有資料，請改用其他目錄，或加上 --force 確認覆寫。" >&2
    exit 1
  else
    echo "[WARN] --force 已指定，將解壓到既有非空目錄：${TARGET_DIR}"
  fi
fi

mkdir -p "$TARGET_DIR"

# ---- 列出備份內容 ------------------------------------------------------------
echo "[INFO] 備份內容："
tar tzf "$BACKUP_FILE"

# ---- 解壓 -------------------------------------------------------------------
echo "[INFO] 解壓到：${TARGET_DIR}"
tar xzf "$BACKUP_FILE" -C "$TARGET_DIR"

# ---- 驗證關鍵檔案 ------------------------------------------------------------
VERIFY_OK=true

check_path() {
  local rel_path="$1"
  if [ -e "${TARGET_DIR}/${rel_path}" ]; then
    echo "[OK]   找到 ${rel_path}"
  else
    echo "[WARN] 缺少 ${rel_path}（若該項目本來就不在備份範圍內，可忽略）"
  fi
}

check_path "wiki/index.md"
check_path "schema/lint_rules.yml"
check_path ".env.example"

if [ -d "${TARGET_DIR}/wiki" ]; then
  echo "[OK]   wiki/ 目錄已還原"
else
  echo "[WARN] 備份中似乎沒有 wiki/ 目錄"
fi

# ---- .env 提醒 --------------------------------------------------------------
if [ ! -f "${TARGET_DIR}/.env" ]; then
  echo "[INFO] 備份不含 .env（依設計）。還原後請依 .env.example 手動建立 .env，並填入實際金鑰。"
fi

if [ "$VERIFY_OK" = true ]; then
  echo "[OK] 還原完成：${TARGET_DIR}"
  if [ "$DRILL_MODE" = true ]; then
    echo "[INFO] 此為演練用暫存目錄，可自行檢查後手動刪除：rm -rf ${TARGET_DIR}"
  fi
  exit 0
else
  echo "[FAIL] 還原驗證未通過。" >&2
  exit 1
fi
