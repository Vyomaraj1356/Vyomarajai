#!/usr/bin/env bash
set -Eeuo pipefail

# VYOMARAJ ONE-SHOT LEFTOVER CONSOLIDATOR
# Purpose:
#   Inventory all open PRs/branches, preserve every source ref,
#   consolidate non-conflicting work into ONE branch/PR, and never
#   silently overwrite or force-push main.
#
# Primary: Vyomaraj1356/Vyomarajai
# DR:      deepakGoyal1356/Vyomaraj-Agent-6d64e
#
# Requirements: git, gh, authenticated gh token with repo write access.
#
# Usage:
#   ./ops/consolidate-all-leftovers.sh inventory
#   ./ops/consolidate-all-leftovers.sh consolidate
#   ./ops/consolidate-all-leftovers.sh merge
#
# Optional:
#   ARENA_EXPORT_DIR=/path/to/Arena/exports ./ops/consolidate-all-leftovers.sh consolidate
#   ALLOW_MAIN_MERGE=1 ./ops/consolidate-all-leftovers.sh merge
#
# SAFETY:
# - never force-pushes
# - never deletes source branches
# - never resets main
# - never uses blind overwrite
# - conflicts are preserved as artifacts and reported
# - main is changed only through the final PR / explicit merge step

OWNER="Vyomaraj1356"
REPO="Vyomarajai"
FULL_REPO="${OWNER}/${REPO}"
MAIN="main"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
WORK_BRANCH="one-shot-consolidation-${STAMP}"
REPORT_DIR="ops/consolidation-reports/${STAMP}"
ARENA_EXPORT_DIR="${ARENA_EXPORT_DIR:-}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "[FAIL] Missing: $1"; exit 2; }; }
need git
need gh

mkdir -p "${REPORT_DIR}"

inventory() {
  echo "=== VYOMARAJ LEFTOVER INVENTORY ==="
  echo "Repository: ${FULL_REPO}"
  echo "Main: ${MAIN}"
  echo

  gh pr list --repo "${FULL_REPO}" --state open --limit 100 \
    --json number,title,headRefName,baseRefName,state,isDraft,mergeable,updatedAt \
    > "${REPORT_DIR}/open-prs.json"

  gh api "repos/${FULL_REPO}/branches?per_page=100" > "${REPORT_DIR}/branches.json"

  echo "[PRs]"
  gh pr list --repo "${FULL_REPO}" --state open --limit 100 \
    --json number,title,headRefName,baseRefName,isDraft,mergeable,updatedAt \
    --jq '.[] | "#\\(.number) | \\(.headRefName) -> \\(.baseRefName) | draft=\\(.isDraft) | mergeable=\\(.mergeable) | \\(.title)"'

  if [[ -n "${ARENA_EXPORT_DIR}" && -d "${ARENA_EXPORT_DIR}" ]]; then
    echo
    echo "[Arena exports]"
    find "${ARENA_EXPORT_DIR}" -type f -maxdepth 4 -print | sort \
      > "${REPORT_DIR}/arena-export-files.txt" || true
    cat "${REPORT_DIR}/arena-export-files.txt"
  fi
}

prepare() {
  git fetch --all --prune

  if git show-ref --verify --quiet "refs/heads/${WORK_BRANCH}"; then
    git branch -D "${WORK_BRANCH}"
  fi

  git checkout "${MAIN}"
  git pull --ff-only origin "${MAIN}"

  # Immutable recovery point for this consolidation run.
  git tag -a "pre-consolidation-${STAMP}" -m "Vyomaraj pre-consolidation checkpoint ${STAMP}"
  git push origin "pre-consolidation-${STAMP}"

  git checkout -b "${WORK_BRANCH}"
}

consolidate() {
  prepare
  inventory

  mapfile -t PRS < <(
    gh pr list --repo "${FULL_REPO}" --state open --limit 100 \
      --json number,headRefName,baseRefName,isDraft \
      --jq '.[] | select(.baseRefName=="main") | select(.isDraft==false) | "\(.number) \(.headRefName)"'
  )

  : > "${REPORT_DIR}/merged.txt"
  : > "${REPORT_DIR}/skipped.txt"
  : > "${REPORT_DIR}/conflicts.txt"

  for row in "${PRS[@]}"; do
    PR="${row%% *}"
    HEAD="${row#* }"

    echo
    echo "=== PR #${PR}: ${HEAD} ==="

    git fetch origin "${HEAD}" || {
      echo "#${PR} ${HEAD} — fetch failed" | tee -a "${REPORT_DIR}/skipped.txt"
      continue
    }

    # Already represented in main/consolidation: no duplicate merge.
    if git merge-base --is-ancestor "origin/${HEAD}" HEAD; then
      echo "#${PR} ${HEAD} — already contained" | tee -a "${REPORT_DIR}/skipped.txt"
      continue
    fi

    # Attempt a normal merge. If it conflicts, abort only this merge and
    # preserve the exact source branch for later human/Arena resolution.
    if git merge --no-commit --no-ff "origin/${HEAD}"; then
      git commit -m "consolidate: absorb PR #${PR} ${HEAD}" || true
      echo "#${PR} ${HEAD}" | tee -a "${REPORT_DIR}/merged.txt"
    else
      git diff --binary > "${REPORT_DIR}/PR-${PR}-conflict.patch" || true
      git status --short > "${REPORT_DIR}/PR-${PR}-conflict-status.txt" || true
      git merge --abort
      echo "#${PR} ${HEAD}" | tee -a "${REPORT_DIR}/conflicts.txt"
    fi
  done

  # Preserve inventory/report inside the consolidation branch.
  git add "${REPORT_DIR}" || true
  git commit -m "chore: record one-shot consolidation inventory" || true

  git push -u origin "${WORK_BRANCH}"

  gh pr create --repo "${FULL_REPO}" \
    --base "${MAIN}" \
    --head "${WORK_BRANCH}" \
    --title "ONE-SHOT: consolidate all safe leftover Vyomaraj work" \
    --body "$(cat <<EOF
## One-shot consolidation

This PR consolidates all currently open, non-draft PR branches targeting main that can be merged without conflict.

### Safety
- No source branch was deleted.
- No force push was used.
- A pre-consolidation tag was created.
- Conflicting PRs were aborted individually and preserved as source refs.
- Main is changed only by this PR.

### Result
Merged safely:
$(cat "${REPORT_DIR}/merged.txt" 2>/dev/null || true)

Conflicts requiring resolution:
$(cat "${REPORT_DIR}/conflicts.txt" 2>/dev/null || true)

Skipped/already contained:
$(cat "${REPORT_DIR}/skipped.txt" 2>/dev/null || true)

Arena exports, if supplied, are inventory-only until their contents are explicitly reconciled:
${ARENA_EXPORT_DIR:-not supplied}
EOF
)"

  echo
  echo "=== CONSOLIDATION COMPLETE ==="
  echo "Branch: ${WORK_BRANCH}"
  echo "Review the generated PR before merge."
  echo "Reports: ${REPORT_DIR}"
}

merge_final() {
  [[ "${ALLOW_MAIN_MERGE:-0}" == "1" ]] || {
    echo "[STOP] Set ALLOW_MAIN_MERGE=1 to permit the final merge."
    exit 3
  }

  PR="$(gh pr list --repo "${FULL_REPO}" --state open --limit 20 \
    --json number,title,headRefName \
    --jq '.[] | select(.title | startswith("ONE-SHOT: consolidate all safe leftover Vyomaraj work")) | .number' | head -n1)"

  [[ -n "${PR}" ]] || { echo "[FAIL] One-shot consolidation PR not found."; exit 4; }

  gh pr ready "${PR}" --repo "${FULL_REPO}" || true
  gh pr merge "${PR}" --repo "${FULL_REPO}" --auto --squash

  echo "[OK] Final consolidation PR #${PR} queued for merge."
  echo "GitHub branch protection/status checks remain authoritative."
}

case "${1:-inventory}" in
  inventory) inventory ;;
  consolidate) consolidate ;;
  merge) merge_final ;;
  *)
    echo "Usage: $0 inventory|consolidate|merge"
    exit 1
    ;;
esac
