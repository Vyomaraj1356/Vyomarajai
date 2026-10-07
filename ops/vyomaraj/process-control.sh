#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="${1:-check}"

echo "=== VYOMARAJ UNIVERSAL PROCESS CONTROL v1.0 ==="
echo "Mode: $MODE"

case "$MODE" in
  check)
    test -f "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
    test -f "$ROOT/docs/process/VYOMARAJ_UNIVERSAL_PROCESS_CONTROL_v1.0.md"
    grep -q "KUBER" "$ROOT/docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md"
    grep -q "INTENT" "$ROOT/docs/process/VYOMARAJ_UNIVERSAL_PROCESS_CONTROL_v1.0.md"
    grep -q "RECONCILE" "$ROOT/docs/process/VYOMARAJ_UNIVERSAL_PROCESS_CONTROL_v1.0.md"
    grep -q "Revenue underperformance procedure" "$ROOT/docs/process/VYOMARAJ_UNIVERSAL_PROCESS_CONTROL_v1.0.md"
    grep -q "Payment-missing procedure" "$ROOT/docs/process/VYOMARAJ_UNIVERSAL_PROCESS_CONTROL_v1.0.md"
    echo "PROCESS CONTROL STRUCTURE: PASS"
    ;;
  revenue-audit)
    echo "Revenue audit procedure:"
    echo "1. Kuber: expected vs reported vs received"
    echo "2. Vyomaraj/Jarvis: root-cause analysis"
    echo "3. Research trends/history/new opportunities"
    echo "4. Kuber: cost/risk/ROI review"
    echo "5. Owner gate where required"
    echo "6. Create -> Verify -> Publish -> Measure"
    echo "7. Kuber: reconcile -> audit -> learn"
    ;;
  payment-escalation)
    echo "Payment escalation procedure:"
    echo "1. Eligibility -> settlement period -> expected date"
    echo "2. Reconcile platform report vs Kuber ledger"
    echo "3. Verify account/payment configuration"
    echo "4. Use current official support/escalation channel"
    echo "5. Record evidence/case/reference"
    echo "6. Recover/confirm -> Kuber reconcile -> close"
    ;;
  *)
    echo "Usage: $0 {check|revenue-audit|payment-escalation}"
    exit 2
    ;;
esac
