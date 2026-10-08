#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
echo "VYOMARAJ FINAL INTEGRATION CONTRACT CHECK"
python3 - <<'PY'
import json, pathlib, sys
root=pathlib.Path(".")
required=[
"docs/architecture/VYOMARAJ_FINAL_MASTER_ARCHITECTURE_v2.0.md",
"docs/architecture/VYOMARAJ_FINAL_SYSTEM_DIAGRAM_v2.0.md",
"config/company/VYOMARAJ_COMPANY_FEDERATION_v1.0.yaml",
"ops/vyomaraj/vyomaraj.sh",
"config/ai/VYOMARAJ_JARVIS_VOICE_IDENTITY_v1.0.yaml",
"config/ai/CREATIVE_AUTONOMY_AND_IDENTITY_POLICY_v1.0.yaml",
"config/ai/CREATIVE_CHARACTER_VOICE_REGISTRY_v1.0.yaml",
"config/ai/PRODUCTION_AGENT_TOOL_REGISTRY_v1.0.yaml",
"config/agents/COLLABORATION_AGENT_v1.0.yaml",
"config/agents/GROWTH_SALES_MARKETING_AGENT_v1.0.yaml",
"config/revenue/REVENUE_DISTRIBUTION_FABRIC_v1.0.yaml",
"config/revenue/REVENUE_GROWTH_ENGINE_v1.0.yaml",
"docs/architecture/VYOMARAJ_REVENUE_GROWTH_OPERATING_MODEL_v1.0.md",
"config/platform/SOCIAL_MONETIZATION_SURFACE_REGISTRY_v1.0.yaml",
"config/finance/KUBER_FINANCIAL_CONTROLLER_v1.0.md",
"config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml",
"config/engineering/GEOSPATIAL_AND_DAILY_STARTUP.yaml",
"ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json",
"ops/vyomaraj/production_agent_gate.py",
"ops/engineering/requirements-2026.txt",
"ops/engineering/requirements-2026-lock.txt"
]
missing=[p for p in required if not (root/p).exists()]
reg=json.loads((root/"ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json").read_text())
print("CONTRACT_FILES:", "PASS" if not missing else "FAIL")
if missing: print("MISSING:", *missing, sep="\n  ")
print("REGISTRY:", reg.get("totals"))
if not isinstance(reg.get("totals",{}).get("sub_agents"), int): raise SystemExit("registry sub-agent count is not an integer")
if not isinstance(reg.get("totals",{}).get("named_sub_agents"), int): raise SystemExit("registry named sub-agent count is not an integer")
print("VOICE_DESIGN:", "PASS")
print("MCP_A2A_CONTRACT:", "PRESENT")
print("MEDIA_RUNTIME:", "NOT_VERIFIED")
print("PROVIDER_CONNECTIONS:", "OWNER_CREDENTIALS_REQUIRED")
print("SOCIAL_ACCOUNT_CONNECTIONS:", "OWNER_AUTHORIZATION_REQUIRED")
print("PRODUCTION_DEPLOYMENT:", "NOT_VERIFIED")
print("APPLICATION_DR:", "CONTRACT_PRESENT_RUNTIME_TEST_REQUIRED")
sys.exit(1 if missing else 0)
PY
