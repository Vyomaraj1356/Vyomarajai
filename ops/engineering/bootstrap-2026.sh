#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV="${VYOMARAJ_VENV:-.venv-vyomaraj-2026}"

echo "[Vyomaraj] Creating isolated engineering environment: $VENV"
"$PYTHON_BIN" -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r ops/engineering/requirements-2026.txt
python ops/engineering/verify_2026_stack.py

echo
echo "FOUNDATION READY: dependencies + local contract checks passed."
echo "NOTE: this does not claim Temporal/MCP/A2A providers are deployed or connected."
