#!/usr/bin/env bash
set -Eeuo pipefail

# Vyomaraj Primary -> DR runner V15.1 ?v=151 678 LIVE 694 total
# PRIMARY:   Vyomaraj1356/Vyomarajai PUBLIC https://Vyomaraj1356.github.io/Vyomarajai/?v=151
# SECONDARY: deepakGoyal1356/Vyomaraj-Agent PRIVATE https://deepakGoyal1356.github.io/Vyomaraj-Agent/
# V15.1 Enhanced SHIV_KE_SATHI detailed KNOWLEDGE_VS_ENTERTAINMENT VYOMARAJ_JARVIS_TALK — 0.00 loss fraction-seconds
#
# This is the single operational entry point. It delegates to the hardened
# controller and prevents accidental production switching unless explicitly
# requested.
#
# Usage:
#   ./ops/dr/run-dr.sh health
#   ./ops/dr/run-dr.sh status
#   ./ops/dr/run-dr.sh test
#   ./ops/dr/run-dr.sh failover
#   ./ops/dr/run-dr.sh failback
#
# Required environment/config:
#   ops/dr/dr.env (copy from dr.env.example)
#   A real traffic-control endpoint
#   Independent DR monitor/runner for production use

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTROLLER="$ROOT/ops/dr/failover-controller.sh"
CONFIG="$ROOT/ops/dr/dr.env"

die(){ echo "ERROR: $*" >&2; exit 1; }

command -v bash >/dev/null || die "bash is required"
command -v curl >/dev/null || die "curl is required"

[[ -x "$CONTROLLER" ]] || chmod +x "$CONTROLLER"
[[ -f "$CONFIG" ]] || die "Missing $CONFIG. Copy ops/dr/dr.env.example to ops/dr/dr.env and configure secrets/endpoints."

# Enforce the intended repositories. This prevents a copied configuration
# from silently operating on an unrelated repository pair.
# shellcheck disable=SC1090
source "$CONFIG"
[[ "${PRIMARY_REPO:-}" == "Vyomaraj1356/Vyomarajai" ]] ||
  die "PRIMARY_REPO must be Vyomaraj1356/Vyomarajai"
[[ "${SECONDARY_REPO:-}" == "deepakGoyal1356/Vyomaraj-Agent" ]] ||
  die "SECONDARY_REPO must be deepakGoyal1356/Vyomaraj-Agent"

case "${1:-status}" in
  health|status|test|failover|failback)
    exec "$CONTROLLER" "$1"
    ;;
  *)
    cat <<'USAGE'
Vyomaraj DR Runner

Usage:
  ./ops/dr/run-dr.sh health
  ./ops/dr/run-dr.sh status
  ./ops/dr/run-dr.sh test
  ./ops/dr/run-dr.sh failover
  ./ops/dr/run-dr.sh failback

Safety:
  test      = non-destructive readiness check
  failover  = production traffic change; use only from the independent DR
              monitor or an explicitly authorized operator
  failback  = production traffic change after primary recovery
USAGE
    exit 2
    ;;
esac
