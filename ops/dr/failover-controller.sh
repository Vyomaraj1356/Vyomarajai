#!/usr/bin/env bash
set -Eeuo pipefail

# Vyomaraj DR / Failover Controller
# Primary:   Vyomaraj1356/Vyomarajai
# Secondary: deepakgoyal1356/<DR_REPO>
#
# This controller is intentionally provider-neutral:
# - GitHub is the source/replication layer.
# - An independent monitor should run outside the primary GitHub repository.
# - DR_SWITCH_URL must point to the user's traffic/DNS/load-balancer controller.
#
# Commands:
#   health       Check primary + secondary + business probes
#   status       Print current DR state
#   failover     Validate, fence, activate secondary, verify, switch traffic
#   failback     Verify repaired primary, resync, switch traffic back
#   test         Run a non-destructive DR readiness test

CONFIG_FILE="${DR_CONFIG_FILE:-ops/dr/dr.env}"
if [[ -f "$CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
fi

: "${PRIMARY_REPO:=Vyomaraj1356/Vyomarajai}"
: "${SECONDARY_REPO:?Set SECONDARY_REPO to deepakgoyal1356/<repository>}"
: "${PRIMARY_HEALTH_URL:?Set PRIMARY_HEALTH_URL}"
: "${SECONDARY_HEALTH_URL:?Set SECONDARY_HEALTH_URL}"
: "${BUSINESS_PROBE_URL:?Set BUSINESS_PROBE_URL}"
: "${DR_SWITCH_URL:?Set DR_SWITCH_URL}"
: "${DR_SWITCH_TOKEN:?Set DR_SWITCH_TOKEN}"

CURL_TIMEOUT="${CURL_TIMEOUT:-8}"
FAILURE_THRESHOLD="${FAILURE_THRESHOLD:-3}"
RECOVERY_THRESHOLD="${RECOVERY_THRESHOLD:-3}"
STATE_FILE="${STATE_FILE:-/tmp/vyomaraj-dr-state}"
LOCK_FILE="${LOCK_FILE:-/tmp/vyomaraj-dr.lock}"

log() { printf '[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"; }
die() { log "ERROR: $*"; exit 1; }

acquire_lock() {
  if (command -v flock >/dev/null 2>&1; then
    exec 9>"$LOCK_FILE"
    flock -n 9 || die "Another DR operation is already running."
  fi
}

http_ok() {
  local url="$1"
  curl -fsS --max-time "$CURL_TIMEOUT" \
    -H 'Cache-Control: no-cache' \
    -H 'User-Agent: Vyomaraj-DR-Controller/1.0' \
    "$url" >/dev/null
}

probe() {
  local name="$1" url="$2" attempts="${3:-$FAILURE_THRESHOLD}" i
  for ((i=1; i<=attempts; i++)); do
    if http_ok "$url"; then
      log "PASS $name"
      return 0
    fi
    log "FAIL $name attempt $i/$attempts"
    sleep "${PROBE_INTERVAL_SECONDS:-2}"
  done
  return 1
}

get_state() {
  [[ -f "$STATE_FILE" ]] && cat "$STATE_FILE" || echo "PRIMARY"
}

set_state() {
  printf '%s\n' "$1" > "$STATE_FILE"
}

switch_traffic() {
  local target="$1"
  log "Requesting traffic switch -> $target"
  curl -fsS --max-time "${SWITCH_TIMEOUT:-15}" \
    -X POST "$DR_SWITCH_URL" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $DR_SWITCH_TOKEN" \
    --data-binary "$(printf '{"target":"%s","reason":"Vyomaraj automated DR controller","fencing":"enabled"}' "$target")"
  printf '\n'
}

github_repo_reachable() {
  local repo="$1"
  curl -fsS --max-time "$CURL_TIMEOUT" "https://api.github.com/repos/$repo" >/dev/null
}

verify_secondary() {
  probe "secondary application" "$SECONDARY_HEALTH_URL" "$RECOVERY_THRESHOLD" || return 1
  probe "business synthetic transaction on secondary" "${SECONDARY_BUSINESS_PROBE_URL:-$BUSINESS_PROBE_URL}" "$RECOVERY_THRESHOLD" || return 1
}

verify_primary() {
  probe "primary application" "$PRIMARY_HEALTH_URL" "$RECOVERY_THRESHOLD" || return 1
  probe "business synthetic transaction on primary" "$BUSINESS_PROBE_URL" "$RECOVERY_THRESHOLD" || return 1
}

health() {
  log "Vyomaraj DR health check; state=$(get_state)"
  github_repo_reachable "$PRIMARY_REPO" && log "PASS primary GitHub repository" || log "FAIL primary GitHub repository"
  github_repo_reachable "$SECONDARY_REPO" && log "PASS secondary GitHub repository" || log "FAIL secondary GitHub repository"
  probe "primary application" "$PRIMARY_HEALTH_URL" "$FAILURE_THRESHOLD" || true
  probe "secondary application" "$SECONDARY_HEALTH_URL" "$FAILURE_THRESHOLD" || true
  probe "primary business transaction" "$BUSINESS_PROBE_URL" "$FAILURE_THRESHOLD" || true
}

status() {
  printf 'Vyomaraj DR state: %s\n' "$(get_state)"
  printf 'Primary:   %s\n' "$PRIMARY_REPO"
  printf 'Secondary: %s\n' "$SECONDARY_REPO"
}

failover() {
  acquire_lock

  [[ "$(get_state)" == "DR" ]] && { log "Already in DR mode; refusing duplicate failover."; return 0; }

  log "FAILOVER START: primary -> secondary"
  log "1/7 Confirming primary failure with independent probes"

  if verify_primary; then
    die "Primary is healthy. Automatic failover aborted to prevent false-positive switching."
  fi

  log "2/7 Verifying secondary repository and runtime"
  github_repo_reachable "$SECONDARY_REPO" || die "Secondary GitHub repository unavailable."
  verify_secondary || die "Secondary is not ready; traffic will NOT be switched."

  log "3/7 Fencing primary writes"
  if [[ -n "${FENCE_PRIMARY_URL:-}" ]]; then
    curl -fsS --max-time 15 -X POST "$FENCE_PRIMARY_URL" \
      -H "Authorization: Bearer ${FENCE_PRIMARY_TOKEN:?Set FENCE_PRIMARY_TOKEN}" \
      -H 'Content-Type: application/json' \
      --data '{"mode":"fenced","reason":"automated DR failover"}' >/dev/null
  else
    log "WARNING: FENCE_PRIMARY_URL not configured. Configure fencing before production use."
  fi

  log "4/7 Activating secondary write mode"
  if [[ -n "${SECONDARY_ACTIVATE_URL:-}" ]]; then
    curl -fsS --max-time 15 -X POST "$SECONDARY_ACTIVATE_URL" \
      -H "Authorization: Bearer ${SECONDARY_ACTIVATE_TOKEN:?Set SECONDARY_ACTIVATE_TOKEN}" \
      -H 'Content-Type: application/json' \
      --data '{"mode":"active","reason":"automated DR failover"}' >/dev/null
  fi

  log "5/7 Final secondary verification"
  verify_secondary || die "Secondary failed final verification; traffic will NOT be switched."

  log "6/7 Switching traffic with a single idempotent control request"
  switch_traffic "secondary"

  log "7/7 Post-switch verification"
  sleep "${POST_SWITCH_WAIT_SECONDS:-5}"
  verify_secondary || {
    log "Secondary post-switch verification failed. Attempting safe rollback to primary."
    switch_traffic "primary" || true
    die "Failover verification failed; traffic rollback attempted."
  }

  set_state "DR"
  log "FAILOVER COMPLETE: secondary is active."
}

failback() {
  acquire_lock

  [[ "$(get_state)" == "DR" ]] || { log "Not in DR mode; no failback required."; return 0; }

  log "FAILBACK START: secondary -> repaired primary"
  verify_primary || die "Primary is not healthy enough for failback."
  verify_secondary || die "Secondary is not healthy enough to maintain service during failback."

  log "Re-synchronization must be complete before traffic moves."
  if [[ -n "${RESYNC_CHECK_URL:-}" ]]; then
    curl -fsS --max-time 20 "$RESYNC_CHECK_URL" >/dev/null || die "Resync check failed."
  fi

  switch_traffic "primary"
  sleep "${POST_SWITCH_WAIT_SECONDS:-5}"
  verify_primary || {
    log "Primary post-failback verification failed; returning traffic to secondary."
    switch_traffic "secondary" || true
    die "Failback failed; secondary restored if possible."
  }

  set_state "PRIMARY"
  log "FAILBACK COMPLETE: primary is active."
}

test_dr() {
  log "NON-DESTRUCTIVE DR READINESS TEST"
  github_repo_reachable "$PRIMARY_REPO" || die "Primary GitHub repo unavailable."
  github_repo_reachable "$SECONDARY_REPO" || die "Secondary GitHub repo unavailable."
  probe "primary" "$PRIMARY_HEALTH_URL" "$RECOVERY_THRESHOLD" || die "Primary readiness failed."
  probe "secondary" "$SECONDARY_HEALTH_URL" "$RECOVERY_THRESHOLD" || die "Secondary readiness failed."
  probe "business-primary" "$BUSINESS_PROBE_URL" "$RECOVERY_THRESHOLD" || die "Business probe failed."
  log "DR readiness PASS. No traffic was changed."
}

case "${1:-status}" in
  health) health ;;
  status) status ;;
  failover) failover ;;
  failback) failback ;;
  test) test_dr ;;
  *) die "Usage: $0 {health|status|failover|failback|test}" ;;
esac
