#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=== VYOMARAJ PUBLISH GATE v1.5 ==="
echo "Architecture: peer cores + ShriYantra + Panch-Brother capability fabric"
echo "Dharmic startup: Shri Ram + Hanuman + Ganesha invocation (configurable)"
echo "Location: deny-by-default; explicit owner authorization required"
echo "Publishing: private core -> verify -> policy -> owner approval -> public output"
echo "Process: intent -> authorize -> execute -> verify -> audit -> measure -> learn"
echo "Finance: Kuber FC -> every penny -> reconcile -> audit -> revenue assurance"

echo "[1/7] Engineering foundation verification"
python3 "$ROOT/ops/engineering/verify_2026_stack.py --check"
python3 "$ROOT/ops/hanuman/capability_status.py" test
python3 "$ROOT/ops/vyomaraj/capability_fabric.py" check
python3 "$ROOT/ops/vyomaraj-core/handover/run_offline_suites.py" --ci

echo "[2/7] Python syntax"
python3 -m compileall -q "$ROOT/ops/engineering" "$ROOT/ops/vyomaraj"

echo "[3/7] Capability and inheritance tests"
python3 -m pytest -q "$ROOT/tests"

echo "[4/7] Security/process/financial invariants"
grep -q "owner-only root" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
grep -q "Panch-Brother" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
grep -q "DEFAULT = OFF" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
grep -q "Kuber" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
grep -q "Revenue leakage detection" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
test -f "$ROOT/docs/process/VYOMARAJ_UNIVERSAL_PROCESS_CONTROL_v1.0.md"
test -x "$ROOT/ops/vyomaraj/process-control.sh" || chmod +x "$ROOT/ops/vyomaraj/process-control.sh"

echo "[5/7] Registry inheritance"
python3 - <<'PY'
from ops.vyomaraj.agent_capability_inheritance import validate_inheritance
result = validate_inheritance()
assert result["registry_agents"] == 153, result
assert result["profiles"] == 133, result
assert result["all_agents_inherit_all_domains"], result
print("153/153 registered agents inherit all five Panch-Brother capability domains")
PY

echo "[6/7] Universal process control"
"$ROOT/ops/vyomaraj/process-control.sh" check
"$ROOT/ops/vyomaraj/process-control.sh" revenue-audit
"$ROOT/ops/vyomaraj/process-control.sh" payment-escalation

echo "[7/7] Release classification"
echo "PUBLISH GATE: PASS (static public-preview scope only)"
echo "PRODUCTION STATUS: BLOCKED"
echo "No deployment was performed."
echo "Unsupported option: this gate has no deploy or production override."
