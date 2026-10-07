#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "VYOMARAJ publish gate"
echo "Architecture: locked"
echo "Daily startup: Ganesha mantra + health + owner authority + peer sync"
echo "Geospatial: provider-neutral, authorized location only"
echo "Mobile-operator tracking: OFF unless explicitly authorized and lawfully available"
echo "Running engineering verification..."
python3 "$ROOT/ops/engineering/verify_2026_stack.py"
echo "Running syntax checks..."
python3 -m compileall -q "$ROOT/ops/engineering"
echo "PUBLISH GATE: PASS (repository/configuration checks only)"
echo "Production runtime/provider/credential/DR verification remains separate."
