#!/usr/bin/env bash
# Deprecated path. "ops/vyomar/" is a typo of "ops/vyomaraj/" that was introduced by the
# 7 October consolidation commit 9ee4fbc alongside a stale copy of the readiness gate.
#
# That copy asserted an aspirational registry (15 categories / 168 sub-agents) which
# contradicts the reconciled current registry (13 categories / 128 counted sub-agents),
# so it could never agree with the canonical gate. It also had a shell-escaping defect
# that made every contract look MISSING while still exiting 0 — a gate that always
# "passed" without checking anything.
#
# Rather than keep a second, divergent gate, this forwards to the canonical one. The
# original content remains recoverable with:
#   git show 9ee4fbc:ops/vyomar/final-readiness-gate.sh
set -u -o pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
CANONICAL="$ROOT/vyomaraj/final-readiness-gate.sh"

echo "DEPRECATED PATH: ops/vyomar/final-readiness-gate.sh" >&2
echo "Use the canonical gate: ops/vyomaraj/final-readiness-gate.sh" >&2

if [[ ! -x "$CANONICAL" ]]; then
  echo "BLOCKED: canonical gate is missing or not executable: ops/vyomaraj/final-readiness-gate.sh" >&2
  exit 2
fi

exec "$CANONICAL" "$@"
