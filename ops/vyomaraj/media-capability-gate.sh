#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "VYOMARAJ MEDIA + CIVILIZATION CAPABILITY GATE"
test -f "$ROOT/config/knowledge/CIVILIZATION_KNOWLEDGE_INHERITANCE_v1.0.yaml"
test -f "$ROOT/config/engineering/SPECIAL_DOMAIN_MEDIA_CAPABILITY_INHERITANCE_v1.0.yaml"
test -f "$ROOT/ops/vyomaraj/media_capability_inheritance.py"
python3 "$ROOT/ops/vyomaraj/media_capability_inheritance.py"
echo "CONTRACT: PASS"
echo "EXTERNAL PROVIDERS: NOT_CONNECTED"
echo "LIVE 3D/4D/5D RENDERING: NOT_VERIFIED"
echo "OWNER GATE: REQUIRED BEFORE PUBLISH"
