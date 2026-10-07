#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

fail=0
require() {
  if [[ ! -e "$1" ]]; then echo "MISSING: $1"; fail=1; else echo "PRESENT: $1"; fi
}

echo "VYOMARAJ FINAL PRODUCTION GATE — current-main foundation + consolidation evidence"
require docs/architecture/VYOMARAJ_FINAL_PRODUCTION_MASTER_2026_10_07.md
require docs/vyomaraj/FINAL_SESSION_CONSOLIDATION_LEDGER_2026_10_07.md
require config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml
require config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json
require .github/workflows/vyomaraj-sync-both.yml
require ops/dr/README.md

if [[ $fail -ne 0 ]]; then
  echo "BLOCKED: canonical consolidation evidence is incomplete."
  exit 2
fi

echo "PASS: consolidation contract and current-main DR controls are present."
echo "NOTE: this gate intentionally does not fake credentials, deployment, DR, failover, or runtime success."
