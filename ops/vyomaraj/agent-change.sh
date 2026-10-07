#!/usr/bin/env bash
set -euo pipefail
ROOT="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")/../.." && pwd)"
REG="\$ROOT/ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
AUDIT="\$ROOT/ops/vyomaraj/state/AGENT_CHANGE_AUDIT.jsonl"
mkdir -p "\$(dirname "\$AUDIT")"
usage(){ echo "Usage: \$0 validate | plan-add CATEGORY ID NAME | plan-remove ID"; exit 2; }
[[ -f "\$REG" ]] || { echo "MISSING registry"; exit 2; }
case "\${1:-}" in
  validate)
    python3 - "\$REG" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p))
agents=d["agents"]; cats=d["categories"]
assert len(cats)==d["totals"]["main_agents"]
assert len([a for a in agents if a.get("counted")])==d["totals"]["sub_agents"]
assert len({a["id"] for a in agents})==len(agents)
assert len({c["id"] for c in cats})==len(cats)
for a in agents:
    assert a["category_id"] in {c["id"] for c in cats}
print(f"PASS: {len(cats)} categories / {len(agents)} registry agents; unique IDs and parents valid")
PY
    ;;
  plan-add)
    [[ $# -eq 4 ]] || usage
    cat="\$2"; id="\$3"; name="\$4"
    printf '%s\n' "OWNER_APPROVAL_REQUIRED ADD category=\$cat id=\$id name=\$name" | tee -a "\$AUDIT"
    echo "PLAN ONLY: use the authenticated agent-management API/transaction runner to commit this change."
    ;;
  plan-remove)
    [[ $# -eq 2 ]] || usage
    printf '%s\n' "OWNER_APPROVAL_REQUIRED ARCHIVE id=\$2" | tee -a "\$AUDIT"
    echo "PLAN ONLY: removal defaults to archive/deactivate; destructive deletion requires explicit owner confirmation."
    ;;
  *) usage ;;
esac
