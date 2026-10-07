#!/usr/bin/env bash
# Final read-only integration gate. It never deploys, publishes, syncs, or starts services.
set -u -o pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

if [[ $# -gt 0 && "${1:-}" != "--help" && "${1:-}" != "-h" ]]; then
  echo "Unsupported option: $1" >&2
  echo "This gate has no deploy, publish, sync, or production override." >&2
  exit 2
fi
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'HELP'
Usage: ops/vyomaraj/final-readiness-gate.sh

Runs read-only deterministic registry, capability-reference, owner-boundary,
and resilience-activation checks. It reports known taxonomy/runtime blockers.
A static PASS is not a production verification or deployment authorization.
HELP
  exit 0
fi

python3 ops/vyomaraj-core/agents/rebuild_registry.py --check || exit $?
python3 ops/vyomaraj/capability_fabric.py check || exit $?
python3 ops/engineering/verify_2026_stack.py --check || exit $?
python3 ops/vyomaraj/agent_change.py validate || exit $?

python3 - <<'PY'
import json
import subprocess
import sys
result = subprocess.run(
    [sys.executable, "ops/engineering/verify_2026_stack.py", "--status"],
    check=True, capture_output=True, text=True,
)
data = json.loads(result.stdout)
for key in data.get("blockers", []):
    print(f"BLOCKER: {key}")
print("STATIC REPOSITORY CHECK: PASS")
print("RUNTIME / PRODUCTION READINESS: BLOCKED — runtime identity, owner-authenticated transactional mutation, peer heartbeat/fencing, external providers, DR, and release-device evidence are not verified.")
print("No deployment, publication, process restart, peer sync, or production mutation was performed.")
if data.get("production_status") != "VERIFIED" or data.get("blockers"):
    sys.exit(4)
PY
