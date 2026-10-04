#!/usr/bin/env bash
# Vyomaraj change desk — post-deployment upgrade controller (skeleton, dry-run by design).
#
# Owner instruction -> ShriYantra alignment -> Vyomaraj/Jarvis coordination -> version-controlled
# change -> separate testing -> OWNER PERMISSION -> upgrade, with a backup plan that rolls back
# and continues on the current version if any verification fails.
#
# This script never contains secrets, never pushes, never restarts a live service and never
# deletes history. Every stage is logged; the permission gate is a file the owner writes by
# hand (APPROVED or REJECTED). Run with --dry-run (default) to see the plan only.
set -euo pipefail

MODE="${1:---dry-run}"
WORKDIR="$(cd "$(dirname "$0")" && pwd)"
GATE_FILE="${WORKDIR}/OWNER_PERMISSION.txt"
SNAPSHOT_DIR="${WORKDIR}/snapshots"
LOG_FILE="${WORKDIR}/upgrade-controller.log"

log() { printf '%s | %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"; }

stage() { log "STAGE $1: $2"; }

require_owner_permission() {
  if [[ ! -f "$GATE_FILE" ]]; then
    log "GATE: $GATE_FILE absent — change stays PENDING_OWNER_PERMISSION. Nothing is applied."
    exit 0
  fi
  if grep -q '^APPROVED by Deepak Goyal' "$GATE_FILE"; then
    log "GATE: owner permission APPROVED found."
  elif grep -q '^REJECTED' "$GATE_FILE"; then
    log "GATE: owner REJECTED the change. Current version continues; nothing is applied."
    exit 0
  else
    log "GATE: $GATE_FILE must contain 'APPROVED by Deepak Goyal' or 'REJECTED'. Nothing is applied."
    exit 1
  fi
}

engage_backup_plan() {
  log "FAILURE at stage: $1"
  log "BACKUP PLAN ENGAGED: roll back to the snapshot; continue with the current version."
  log "Current version keeps serving. Version control retains the full history."
  exit 2
}

[[ "$MODE" == "--execute" || "$MODE" == "--dry-run" ]] || { echo "usage: $0 [--dry-run|--execute]" >&2; exit 64; }
[[ "$MODE" == "--dry-run" ]] && log "DRY-RUN: stages are printed; nothing is applied."

stage 1 "intake — owner instruction only (authority: ShriYantra)"
stage 2 "alignment — Vyomaraj/Bharath and Jarvis/Laxman align with ShriYantra"
stage 3 "coordination — inform every affected agent; no silent behaviour changes"
stage 4 "version control — change rides a dedicated branch; no history deleted"

if [[ "$MODE" == "--execute" ]]; then
  stage 5 "backup first — snapshot the current running version"
  mkdir -p "$SNAPSHOT_DIR"
  git -C "$WORKDIR/../../.." rev-parse HEAD > "$SNAPSHOT_DIR/current-version.txt" \
    || engage_backup_plan "snapshot"
  stage 5 "separate testing — offline suites on the change branch"
  (cd "$WORKDIR/../../.." && python3 -m unittest discover -s ops/dr -p 'test_*.py' -q) \
    || engage_backup_plan "offline suite"
  (cd "$WORKDIR/../../.." && python3 -m unittest discover -s ops/vyomaraj-core/handover -p 'test_*.py' -q) \
    || engage_backup_plan "handover suite"
  (cd "$WORKDIR/../../.." && python3 -m unittest discover -s ops/vyomaraj-core/approvals -p 'test_*.py' -q) \
    || engage_backup_plan "approvals suite"
  (cd "$WORKDIR/../../.." && python3 -m unittest discover -s ops/vyomaraj-core/finance -p 'test_*.py' -q) \
    || engage_backup_plan "finance suite"
  (cd "$WORKDIR/../.." && true) 2>/dev/null || true
  stage 6 "permission gate"
  require_owner_permission
  stage 7 "upgrade — apply the approved change and verify business health"
  log "NOTE: the actual application step is executed by the deployment owner; this controller stops at the gate."
  stage 8 "post-upgrade verification — any failure engages the backup plan"
else
  stage 5 "separate testing — (dry-run) offline suites would run here"
  stage 6 "permission gate — (dry-run) $GATE_FILE would be checked here"
  stage 7 "upgrade — (dry-run) snapshot first, apply, verify health"
  stage 8 "post-upgrade verification — (dry-run) backup plan is rollback-ready"
fi

log "DONE: change lifecycle completed without touching the running business."
