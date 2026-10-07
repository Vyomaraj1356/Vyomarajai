#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="${1:-scan}"
case "$MODE" in
  scan|weekly|monthly|merge-plan) ;;
  *) echo "Usage: $0 scan|weekly|monthly|merge-plan"; exit 2 ;;
esac
exec python3 "$ROOT/ops/vyomaraj/maintenance/content_alignment_cleaner.py" "$MODE"
