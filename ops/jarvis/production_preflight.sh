#!/usr/bin/env bash
# Vyomaraj/Jarvis production release preflight.
# Repository verification only: never deploys, publishes, writes business data,
# synchronizes DR, or triggers failover/failback.
set -Eeuo pipefail
umask 077

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "BLOCKED: run this script inside a cloned Vyomarajai Git repository." >&2
  exit 2
}
cd "$ROOT"
PYTHON="\${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null 2>&1 || { echo "BLOCKED: Python 3.10+ is required." >&2; exit 2; }

"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 10):
    raise SystemExit("BLOCKED: Python 3.10+ is required.")
print(f"PASS: Python {sys.version_info.major}.{sys.version_info.minor}")
PY

echo "== 1/5: Validate prompt registry =="
"$PYTHON" - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("config/ai/PROMPT_REGISTRY_V1.json").read_text(encoding="utf-8"))
assert data.get("schema_version") == 1, "unsupported schema_version"
presets = data.get("presets")
assert isinstance(presets, dict) and presets, "presets must be a non-empty object"
allowed = {"vyomaraj", "jarvis"}
for name, item in presets.items():
    assert isinstance(name, str) and name, "empty preset ID"
    assert isinstance(item, dict), f"{name}: preset must be an object"
    assert isinstance(item.get("prompt"), str) and item["prompt"].strip(), f"{name}: missing prompt"
    roles = item.get("roles")
    assert isinstance(roles, list) and roles and set(roles) <= allowed, f"{name}: invalid roles"
required = {
    "truthmode", "research", "firstprinciple", "blackswan", "signalvsnoise",
    "predict", "tldr", "x10think", "kidseducation", "childsafecontent",
    "socialpublish", "collaboration", "legalreview", "audit", "deploygate",
    "executeverify", "transparent"
}
missing = required - set(presets)
assert not missing, "missing required presets: " + ", ".join(sorted(missing))
print(f"PASS: registry v{data.get('version', 'unknown')} — {len(presets)} presets validated")
print("PASS: core research, child-safety, publishing, legal and release-gate presets exist")
PY

echo "== 2/5: Run offline LLM harness tests =="
"$PYTHON" -m unittest ops/jarvis/test_llm_harness.py

echo "== 3/5: Check private environment-file hygiene =="
for f in ops/jarvis/llm-harness.env ops/jarvis/jarvis.env ops/dr/dr.local.env; do
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    echo "BLOCKED: private environment file is tracked: $f" >&2
    exit 3
  fi
  if ! git check-ignore -q "$f"; then
    echo "BLOCKED: private environment path is not ignored: $f" >&2
    exit 3
  fi
done
echo "PASS: private environment files are not tracked and are Git-ignored"

echo "== 4/5: Verify preset discovery is offline =="
"$PYTHON" ops/jarvis/llm_harness.py --list-presets >/dev/null
echo "PASS: --list-presets runs without provider configuration"

echo "== 5/5: Provider smoke test (opt-in only) =="
if [[ "\${1:-}" == "--provider-smoke-test" ]]; then
  [[ "$#" -eq 1 ]] || { echo "Usage: $0 [--provider-smoke-test]" >&2; exit 2; }
  if [[ -z "\${JARVIS_LLM_ENDPOINT:-}" && ! -f ops/jarvis/llm-harness.env ]]; then
    echo "BLOCKED: configure an approved provider in the ignored local env file or secret manager." >&2
    exit 4
  fi
  printf '%s\n' 'Reply with exactly: VYOMARAJ_JARVIS_SMOKE_OK' |
    "$PYTHON" ops/jarvis/llm_harness.py --role jarvis --preset truthmode
  echo "NOTE: A response proves only that this request returned, not deployment, tool access, security approval, DR health, or production readiness."
elif [[ "$#" -gt 0 ]]; then
  echo "Usage: $0 [--provider-smoke-test]" >&2
  exit 2
else
  echo "SKIP: provider smoke test not requested; no provider request was sent."
fi

echo
echo "PREFLIGHT PASS: repository checks completed."
echo "NOT A DEPLOYMENT: merge, provider configuration, hosting, monitoring, DR validation and owner approval remain separate gates."
