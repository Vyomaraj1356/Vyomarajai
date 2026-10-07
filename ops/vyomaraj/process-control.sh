#!/usr/bin/env bash
# Read-only process/status guard. It never starts, stops, restarts, or fails over services.
set -u -o pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"
COMMAND="${1:-status}"

case "$COMMAND" in
  status)
    exec python3 ops/engineering/verify_2026_stack.py --status
    ;;
  validate)
    exec python3 ops/engineering/verify_2026_stack.py --check
    ;;
  start|stop|restart|failover|failback)
    echo "BLOCKED: no authenticated process-control adapter, verified service identity, or owner-approved runtime transaction is configured." >&2
    echo "No legacy gateway/studio writer service was contacted or changed." >&2
    echo "PROCESS CONTROL: READ-ONLY STATUS ONLY" >&2
    exit 4
    ;;
  --help|-h)
    cat <<'HELP'
Usage: ops/vyomaraj/process-control.sh [status|validate|start|stop|restart|failover|failback]

status/validate are read-only repository checks. Mutating and recovery actions are
intentionally blocked until owner authorization, an authenticated process adapter,
peer fencing, audit, rollback, and runtime evidence are in place.
HELP
    exit 0
    ;;
  *)
    echo "Unsupported process-control command: $COMMAND" >&2
    exit 2
    ;;
esac
