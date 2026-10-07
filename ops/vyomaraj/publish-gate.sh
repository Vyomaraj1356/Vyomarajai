#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=== VYOMARAJ PUBLISH GATE v1.3 ==="
echo "Architecture: peer cores + ShriYantra + Panch-Brother capability fabric"
echo "Dharmic startup: Shri Ram + Hanuman + Ganesha invocation (configurable)"
echo "Location: deny-by-default; explicit owner authorization required"
echo "Publishing: private core -> verify -> policy -> owner approval -> public output"

echo "[1/5] Engineering foundation verification"
python3 "$ROOT/ops/engineering/verify_2026_stack.py"

echo "[2/5] Python syntax"
python3 -m compileall -q "$ROOT/ops/engineering" "$ROOT/ops/vyomaraj"

echo "[3/5] Capability tests"
python3 -m pytest -q "$ROOT/tests" 2>/dev/null || {
  echo "TEST RESULT: pytest unavailable or tests failed"
  exit 1
}

echo "[4/5] Security/publish invariants"
grep -q "owner-only root" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
grep -q "Panch-Brother" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
grep -q "DEFAULT = OFF" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"

echo "[5/5] Release classification"
echo "PUBLISH GATE: PASS for repository/configuration/tests"
echo "PRODUCTION RUNTIME: NOT VERIFIED until external providers, credentials, deployment and DR are tested."
