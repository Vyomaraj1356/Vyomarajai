#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
usage(){ echo "Vyomaraj AI Agent OS — Company/Federation control"; echo "Usage: $0 {status|validate|test|verify|health|dr|report|start|stop}"; }
status(){ python3 - <<'PY'
import json,pathlib
r=json.loads(pathlib.Path("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json").read_text()); t=r["totals"]
print("VYOMARAJ AI — FINAL COMPANY/FEDERATION STATUS")
print(f"registry: {t['main_agents']} categories / {t['sub_agents']} counted / {t['named_sub_agents']} named / {t['unnamed_numbered_sub_agents']} legacy unnamed")
print(f"nested entertainment: {t.get('uncounted_nested_sub_agents',0)}; historical products: {t.get('historical_reported_products')}")
print("peer cores: VYOMARAJ/BHARATH <-> JARVIS/LAXMAN"); print("foundation: SHRIYANTRA")
for p in ["config/company/VYOMARAJ_COMPANY_FEDERATION_v1.0.yaml","docs/architecture/VYOMARAJ_FINAL_MASTER_ARCHITECTURE_v2.0.md","docs/architecture/VYOMARAJ_FINAL_SYSTEM_DIAGRAM_v2.0.md","config/engineering/VYOMARAJ_FULL_STACK_RUNTIME_v1.0.yaml"]:
 print(("PRESENT" if pathlib.Path(p).is_file() else "MISSING")+": "+p)
PY
}
validate(){
 local missing=0
 local required=("config/company/VYOMARAJ_COMPANY_FEDERATION_v1.0.yaml" "docs/architecture/VYOMARAJ_FINAL_MASTER_ARCHITECTURE_v2.0.md" "docs/architecture/VYOMARAJ_FINAL_SYSTEM_DIAGRAM_v2.0.md" "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json" "config/engineering/VYOMARAJ_FULL_STACK_RUNTIME_v1.0.yaml" "ops/engineering/requirements-2026.txt" "ops/engineering/requirements-2026-lock.txt" "ops/engineering/verify_2026_stack.py" "ops/dr/run-dr.sh")
 for f in "${required[@]}"; do if [[ -f "$f" ]]; then echo "PRESENT: $f"; else echo "MISSING: $f"; missing=1; fi; done
 python3 - <<'PY'
import json,pathlib
t=json.loads(pathlib.Path("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json").read_text())["totals"]
assert (t["main_agents"],t["sub_agents"],t["named_sub_agents"],t["unnamed_numbered_sub_agents"],t["uncounted_parent_headings"],t["uncounted_nested_sub_agents"],t["historical_reported_products"])==(15,168,166,2,6,48,421)
print("PASS: registry 15 / 168 / 166 / 2 / 6 / 48 / 421")
PY
 [[ "$missing" -eq 0 ]] && echo "PASS: canonical contracts present" || return 2
}
test(){ python3 -m unittest discover -s ops/vyomaraj-core/agents -p 'test*.py' -v; python3 -m unittest discover -s ops/vyomaraj-core/experience -p 'test*.py' -v; python3 tests/test_capability_fabric.py; python3 tests/test_agent_capability_inheritance.py; }
verify(){ python3 ops/engineering/verify_2026_stack.py; ./ops/vyomaraj/final-readiness-gate.sh; ./ops/vyomaraj/final-integration.sh; }
health(){ echo "LOCAL HEALTH"; validate; echo "EXTERNAL RUNTIME: no credentials are guessed; runtime evidence is required."; }
dr(){ ./ops/dr/run-dr.sh status; }
report(){ mkdir -p reports; python3 - <<'PY'
import json,pathlib
r=json.loads(pathlib.Path("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json").read_text()); t=r["totals"]
p={"system":"VYOMARAJ AI AGENT OS","brand":"Vyomaraj — The King of the Sky","organization":"private_owner_controlled_ai_company_and_federation","architecture":"v2.0","peer_cores":"VYOMARAJ/BHARATH <-> JARVIS/LAXMAN","registry":t,"education_name":"Education & Civilization Knowledge","agriculture_name":"Agriculture & Living World","external_runtime":"NOT_VERIFIED unless runtime evidence exists","dr":"repository/application distinction enforced"}
path=pathlib.Path("reports/VYOMARAJ_FINAL_OPERATIONAL_REPORT.json"); path.write_text(json.dumps(p,indent=2)+"\n"); print(path); print(json.dumps(p,indent=2))
PY
}
start(){ exec python3 ops/vyomaraj-core/experience/studio_server.py; }
stop(){ echo "STOP is supervisor-specific; no destructive process kill is performed."; }
case "${1:-}" in status) status;; validate) validate;; test) test;; verify) verify;; health) health;; dr) dr;; report) report;; start) start;; stop) stop;; *) usage; exit 2;; esac
