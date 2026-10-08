#!/usr/bin/env bash
# Plan-only registry change guard. No command in this wrapper mutates a live registry.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/agent_change.py" "$@"
