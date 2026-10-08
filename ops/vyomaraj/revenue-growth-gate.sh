#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "VYOMARAJ REVENUE GROWTH READINESS GATE"
python3 - <<'PY'
from pathlib import Path
import sys, yaml

root = Path(".")
required = [
    "config/agents/GROWTH_SALES_MARKETING_AGENT_v1.0.yaml",
    "config/revenue/REVENUE_GROWTH_ENGINE_v1.0.yaml",
    "config/revenue/REVENUE_DISTRIBUTION_FABRIC_v1.0.yaml",
    "config/agents/COLLABORATION_AGENT_v1.0.yaml",
    "config/finance/KUBER_FINANCIAL_CONTROLLER_v1.0.md",
    "docs/architecture/VYOMARAJ_FINAL_MASTER_ARCHITECTURE_v1.5.md",
]
missing = [p for p in required if not (root / p).exists()]
if missing:
    print("REQUIRED_FILES: FAIL")
    for p in missing:
        print("  MISSING:", p)
    sys.exit(1)

for p in required[:4]:
    yaml.safe_load((root / p).read_text(encoding="utf-8"))

growth = yaml.safe_load((root / required[0]).read_text(encoding="utf-8"))
engine = yaml.safe_load((root / required[1]).read_text(encoding="utf-8"))

assert growth["authority"]["owner"] == "ultimate"
assert growth["technology_strategy"]["principles"][:2] == ["provider_neutral", "api_first"]
assert growth["revenue_truth"]["realized_revenue_requires_settlement_evidence"] is True
assert engine["architecture_change"] is False
assert engine["north_star"]["annual_revenue_aspiration_inr"] == "50000000-100000000"
assert engine["portfolio_rule"]["decision_states"]

print("FILES: PASS")
print("ARCHITECTURE_CHANGE: FALSE")
print("OWNER_ROOT: PRESERVED")
print("PROVIDER_NEUTRAL: PASS")
print("MCP_A2A: INHERITED")
print("SALES_MARKETING: CONFIGURED")
print("GROWTH_ENGINE: CONFIGURED")
print("KUBER_RECONCILIATION: REQUIRED")
print("PRODUCTION_CONNECTIONS: NOT_VERIFIED")
print("EXTERNAL_CREDENTIALS: REQUIRED")
print("PLATFORM_ACTIVATION: OWNER_AUTHORIZATION_REQUIRED")
print("REVENUE: EVIDENCE_GATED")
print("STATUS: READY_FOR_PR_VALIDATION_NOT_DEPLOYED")
PY
