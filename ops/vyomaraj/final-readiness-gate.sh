#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/../.." && pwd)"
fail=0
require(){ if [[ ! -e "$ROOT/$1" ]]; then echo "MISSING: $1"; fail=1; else echo "PRESENT: $1"; fi; }
echo 'VYOMARAJ FINAL READINESS CONTRACT GATE'
require docs/architecture/VYOMARAJ_FINAL_INTEGRATION_GAP_MATRIX_v1.0.md
require docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md
require docs/architecture/VYOMARAJ_UNIVERSAL_KNOWLEDGE_MEDIA_ARCHITECTURE_v1.0.md
require docs/process/VYOMARAJ_UNIVERSAL_PROCESS_CONTROL_v1.0.md
require config/finance/KUBER_FINANCIAL_CONTROLLER_v1.0.md
require config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml
require config/engineering/SPECIAL_DOMAIN_MEDIA_CAPABILITY_INHERITANCE_v1.0.yaml
require config/engineering/GEOSPATIAL_AND_DAILY_STARTUP.yaml
require config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json
require config/knowledge/CIVILIZATION_KNOWLEDGE_INHERITANCE_v1.0.yaml
require ops/engineering/requirements-2026.txt
require ops/engineering/bootstrap-2026.sh
require ops/engineering/verify_2026_stack.py
require ops/vyomaraj/AUTONOMOUS_EXECUTION_PLAN_v1.0.json
require ops/vyomaraj/media_capability_inheritance.py
require ops/vyomaraj/process-control.sh
require ops/vyomaraj/publish-gate.sh
require ops/vyomaraj/daily_start.py
require ops/vyomaraj/geospatial_gateway.py
require ops/vyomaraj/location_authorization.py
require ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json
python3 - <<'PY'
import json, pathlib
p=pathlib.Path('ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json')
d=json.loads(p.read_text())
assert d['totals']['main_agents']==13
assert d['totals']['sub_agents']==153
assert len(d['agents'])==153
assert d['totals']['uncounted_parent_headings']==6
print('PASS: registry 14 categories / 153 agents / 6 headings')
PY
if [[ $fail -ne 0 ]]; then echo 'BLOCKED: required contract file missing'; exit 2; fi
echo 'PASS: architecture contract gate. This does NOT claim production runtime deployment.'
