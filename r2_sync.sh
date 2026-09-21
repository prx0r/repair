#!/bin/bash
# Repair Garden — R2 Sync Script
# Syncs local warehouse to Cloudflare R2 for permanent storage.
#
# Usage:
#   ./r2_sync.sh              # sync all
#   ./r2_sync.sh --dry-run    # preview what would be synced
#
# Setup:
#   1. Install rclone: curl https://rclone.org/install.sh | sudo bash
#   2. Configure: rclone config create repair-r2 s3 ...
#   3. Set env: export R2_BUCKET=repair-garden

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WAREHOUSE="${SCRIPT_DIR}/warehouse"
R2_BUCKET="${R2_BUCKET:-repair-garden}"
R2_REMOTE="${R2_REMOTE:-repair-r2}"
DRY_RUN=""

if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
    echo "DRY RUN — no files will be uploaded"
fi

echo "R2 Sync — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  Source: ${WAREHOUSE}"
echo "  Target: ${R2_REMOTE}:${R2_BUCKET}"
echo ""

# Sync SQLite database
if [[ -f "${WAREHOUSE}/repair.db" ]]; then
    echo "  Syncing repair.db..."
    rclone copy "${WAREHOUSE}/repair.db" "${R2_REMOTE}:${R2_BUCKET}/db/repair.db" ${DRY_RUN} --progress
fi

# Sync JSONL raw files
if [[ -d "${WAREHOUSE}" ]]; then
    echo "  Syncing raw data..."
    rclone sync "${WAREHOUSE}" "${R2_REMOTE}:${R2_BUCKET}/warehouse/" ${DRY_RUN} \
        --exclude "*.pyc" \
        --exclude "__pycache__/" \
        --exclude ".DS_Store" \
        --progress
fi

# Sync data directory
DATA_DIR="${SCRIPT_DIR}/data"
if [[ -d "${DATA_DIR}" ]]; then
    echo "  Syncing data..."
    rclone sync "${DATA_DIR}" "${R2_REMOTE}:${R2_BUCKET}/data/" ${DRY_RUN} \
        --exclude "*.pyc" \
        --exclude "__pycache__/" \
        --progress
fi

echo ""
echo "Sync complete."
