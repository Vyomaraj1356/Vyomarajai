#!/usr/bin/env bash
# Read-only repository integrity checks by default. No target or secrets guessed.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ACTION="${1:-status}"
case "$ACTION" in
  health|status|test)
    # dr_sync.py reads process credentials or uses authenticated gh GET requests.
    # It deliberately does not source the tracked legacy dr.env.
    exec python3 "$ROOT/ops/dr/dr_sync.py"
    ;;
  failover|failback)
    echo 'BLOCKED: production traffic changes are not part of repository sync.' >&2
    echo 'The legacy controller requires a separately reviewed fencing, endpoint and rollback runbook.' >&2
    exit 2
    ;;
  *)
    echo 'Usage: DR_REPO=confirmed-owner/repository ops/dr/run-dr.sh {health|status|test}' >&2
    echo 'These commands compare Git trees only; they do not test application recovery or switch traffic.' >&2
    exit 2
    ;;
esac
