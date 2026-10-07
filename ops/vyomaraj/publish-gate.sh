#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=== VYOMARAJ PUBLISH GATE v1.4 ==="
echo "Architecture: peer cores + ShriYantra + Panch-Brother capability fabric"
echo "Dharmic startup: Shri Ram + Hanuman + Ganesha invocation (configurable)"
echo "Location: deny-by-default; explicit owner authorization required"
echo "Publishing: private core -> verify -> policy -> owner approval -> public output"

echo "[1/6] Engineering foundation verification"
python3 "$ROOT/ops/engineering/verify_2026_stack.py"

echo "[2/6] Python syntax"
python3 -m compileall -q "$ROOT/ops/engineering" "$ROOT/ops/vyomaraj"

echo "[3/6] Capability and inheritance tests"
python3 -m pytest -q "$ROOT/tests"

echo "[4/6] Security/publish invariants"
grep -q "owner-only root" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
grep -q "Panch-Brother" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
grep -q "DEFAULT = OFF" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"

echo "[5/6] Registry inheritance"
python3 - <<'PY'
from ops.vyomaraj.agent_capability_inheritance import validate_inheritance
result = validate_inheritance()
assert result["registry_agents"] == 128, result
assert result["profiles"] == 128, result
assert result["all_agents_inherit_all_domains"], result
print("128/128 registered agents inherit all five Panch-Brother capability domains")
PY

echo "[6/6] Release classification"
echo "PUBLISH GATE: PASS for repository/configuration/tests"
echo "PRODUCTION RUNTIME: NOT VERIFIED until external providers, credentials, deployment, application DR and end-to-end control-plane tests are executed."
