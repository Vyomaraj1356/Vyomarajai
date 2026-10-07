#!/usr/bin/env bash
# Compatibility entry point for the replaced V13 mock controller.
# This wrapper never sources jarvis.env, invents device state, simulates a shift,
# or describes a homepage GET as a live Jarvis heartbeat.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${JARVIS_HEARTBEAT_CONFIG:-$SCRIPT_DIR/heartbeat-config.json}"
if [[ ! -f "$CONFIG" ]]; then
  CONFIG="$SCRIPT_DIR/heartbeat-config.example.json"
fi
COMMAND="${1:-status}"
shift || true
case "$COMMAND" in
  heartbeat) COMMAND=check ;;
  status|check|run|shift) ;;
  test)
    exec python3 -m unittest discover -s "$SCRIPT_DIR" -p 'test_heartbeat_monitor.py' -v
    ;;
  *)
    echo "Usage: $0 {heartbeat|check|run|status|shift|test}" >&2
    exit 2
    ;;
esac
exec python3 "$SCRIPT_DIR/heartbeat_monitor.py" --config "$CONFIG" "$COMMAND" "$@"
