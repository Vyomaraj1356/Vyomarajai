#!/usr/bin/env bash
# Preview-only release gate. It verifies repository engineering evidence; it never deploys.
set -u -o pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'HELP'
Usage: ./ops/vyomaraj/publish-gate.sh

Runs the offline tests/builders and local architecture metadata checks. A PASS means
only that the static public-preview package passed its repository checks. This command
never publishes or deploys. Production status is reported separately and remains BLOCKED
until owner authorization, runtime/provider, independent DR and release-device evidence
has been collected and approved.
HELP
  exit 0
fi
if [[ $# -gt 0 ]]; then
  echo "Unsupported option: $1" >&2
  echo "This gate is verification-only; it has no deploy or production override." >&2
  echo "PUBLISH GATE: BLOCKED" >&2
  echo "PRODUCTION STATUS: NOT VERIFIED" >&2
  exit 2
fi

python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci
result=$?
if [[ $result -ne 0 ]]; then
  echo "PUBLISH GATE: BLOCKED" >&2
  echo "PRODUCTION STATUS: NOT VERIFIED" >&2
  exit "$result"
fi

python3 ops/hanuman/capability_status.py test
result=$?
if [[ $result -ne 0 ]]; then
  echo "PUBLISH GATE: BLOCKED" >&2
  echo "PRODUCTION STATUS: NOT VERIFIED" >&2
  exit "$result"
fi

# This is a deliberately explicit production block, not a missing-test shortcut.
# The repository contains no owner-signed runtime deployment evidence for these gates.
echo "PUBLISH GATE: PASS (static public-preview scope only)"
echo "PRODUCTION STATUS: BLOCKED — owner-authenticated runtime, configured provider,"
echo "  independent peer heartbeat/fencing, signed native clients and production DR"
echo "  evidence have not been verified. No deployment was performed."
exit 0
