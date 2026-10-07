#!/usr/bin/env bash
# Compatibility wrapper for the old status script. Metadata is not a live capability fabric.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMMAND="${1:-status}"
exec python3 "$SCRIPT_DIR/capability_status.py" "$COMMAND"
