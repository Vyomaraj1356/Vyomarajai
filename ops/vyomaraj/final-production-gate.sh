#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

fail=0
require() {
  if [[ ! -e "$1" ]]; then echo "MISSING: $1"; fail=1; else echo "PRESENT: $1"; fi
}

echo "VYOMARAJ FINAL PRODUCTION GATE — architecture/evidence gate"
require docs/architecture/VYOMARAJ_FINAL_PRODUCTION_MASTER_2026_10_07.md
require docs/vyomaraj/FINAL_SESSION_CONSOLIDATION_LEDGER_2026_10_07.md
require docs/architecture/VYOMARAJ_FINAL_MASTER_ARCHITECTURE_v2.0.md
require docs/architecture/VYOMARAJ_FINAL_SYSTEM_DIAGRAM_v2.0.md
require config/company/VYOMARAJ_COMPANY_FEDERATION_v1.0.yaml
require config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml
require config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json
require config/knowledge/CIVILIZATION_KNOWLEDGE_INHERITANCE_v1.0.yaml
require config/finance/KUBER_FINANCIAL_CONTROLLER_v1.0.md
require ops/vyomaraj/vyomaraj.sh
require .github/workflows/vyomaraj-sync-both.yml

if [[ $fail -ne 0 ]]; then
  echo "BLOCKED: canonical production contract is incomplete."
  exit 2
fi

echo "PASS: canonical architecture/evidence files present."
echo "NOTE: this gate intentionally does not fake credentials, deployment, DR, failover, or runtime success."
