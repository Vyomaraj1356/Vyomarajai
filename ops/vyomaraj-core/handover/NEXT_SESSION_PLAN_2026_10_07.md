# VYOMARAJ — NEXT-SESSION PLAN

Written 2026-10-06 in session `arena/6bc12929-vyomarajai`, for the session of/after
2026-10-07. This is the "start here" page. Every claim below was verified in this
checkout or through the GitHub API in the writing session; each section says how.
If any command in section 2 disagrees with this document, the command is right.

Marker: NEXT-SESSION PLAN (the viewer contract checks for this line).

## 0 · The state in one paragraph

`main` is `d46d8b3` (PR #31 merge, 2026-10-06 11:49 UTC, tree
`bb8632f62eb978417dc4fb39265d32c305f3942f`) and the DR secondary MATCHes it —
both verify-or-sync annotations re-read live, trees equal, one write (rollback
`42c401d2…`), one no-op. The previous session's commits `002f5ed` + `9e241e9`
NEVER reached GitHub (verified: `git ls-remote` shows that branch at `cce1074`,
fully merged via PR #31; both objects are unknown to the repository), so the
plan/routes/pack it described were rebuilt here as NEW work on branch
`arena/6bc12929-vyomarajai`, not recovered. Publish path: section 1. Issue #6 is
still OPEN with its close-out comment prepared: section 3.

## 1 · Publish the work (exact commands)

PUBLICATION RECORD (filled by the writing session before pushing):

- Branch: `arena/6bc12929-vyomarajai`
- Base: `main` at `d46d8b3705a7161938096bfc953b0cd4fd440b8c`
- Content commit: `FILL_BEFORE_PUSH_1` (rebuild: plan, update, routes, tests, DR extension, regenerated chain)
- Record commit: `FILL_BEFORE_PUSH_2` (this section filled in + AI handoff archive rebuilt)
- Recovery-index commit: `FILL_AFTER_PUSH` (12-session index + go-live brief, after the branch exists on origin)

Primary path — run from the repository root on this branch:

```bash
git status --short                                   # expect clean except intended files
git log --oneline -3                                 # expect the commits above, on d46d8b3
git push origin arena/6bc12929-vyomarajai
gh pr create --title "Rebuild next-session plan, session update, routes and DR record" \
  --body "Recovery rebuild. The prior session's commits never reached GitHub (verified absent); this re-implements the plan, the update, the viewer routes and the DR extension from live evidence. See NEXT_SESSION_PLAN_2026_10_07.md section 7."
gh pr checks <PR> --watch                            # wait for green; do not merge on red
gh pr merge <PR> --merge                             # merge commit, never squash (keeps the record chain readable)
git fetch origin main
gh run list --workflow vyomaraj-sync-both.yml --branch main --limit 3
```

Fallback — if the next session is bound to a DIFFERENT branch name:

```bash
git fetch origin '+refs/heads/arena/*:refs/remotes/origin/arena/*'
git log --oneline origin/arena/6bc12929-vyomarajai -5   # confirm the commits exist on origin
git cherry-pick <content-commit>..<record-commit>      # onto the new session branch, or:
git checkout origin/arena/6bc12929-vyomarajai -- <paths>  # re-apply file by file, then commit
```

Never force-push. Never merge with red checks. Never rewrite the frozen files
listed in section 7.

## 2 · Verify the publish

Run in order. Each line is a command and its expected result.

```bash
# 1. Privacy guard — must print OK, no identifiers.
python3 ops/vyomaraj-core/handover/sanitize_personal_data.py --check

# 2. Full offline gate — must end "0 failures".
python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci

# 3. Live stack (four terminals or background processes, from the repo root):
python3 ops/vyomaraj-core/handover/preview_reports.py --port 4174
python3 ops/vyomaraj-core/experience/studio_server.py --port 4181 --home aghor
python3 ops/vyomaraj-core/experience/studio_server.py --port 4182 --home aghor
python3 ops/availability/gateway.py --port 4176 --primary-port 4181 --secondary-port 4182

# 4. New routes — every line must print 200 on every port (4174, 4176, 4181, 4182):
for p in 4174 4176 4181 4182; do
  for r in /reports/next-session-plan /reports/session-update \
           /reports/download/next-session-plan.md /reports/download/next-session-plan.txt \
           /reports/download/session-update.md /reports/download/session-update.txt; do
    printf "%s %s " "$p" "$r"; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:$p$r"
  done
done

# 5. Recorded verifiers — must regenerate with "problems: none" / 0 problems:
python3 ops/vyomaraj-core/handover/verify_preview.py
python3 ops/vyomaraj-core/handover/verify_live_wiring.py

# 6. DR sync — after the merge, the push run must show verify-or-sync success:
gh run list --workflow vyomaraj-sync-both.yml --branch main --limit 2
gh api repos/Vyomaraj1356/Vyomarajai/commits/<new-main-sha>/check-runs \
  --jq '.check_runs[] | select(.name=="verify-or-sync") | {id, conclusion}'
gh api repos/Vyomaraj1356/Vyomarajai/check-runs/<verify-id>/annotations \
  --jq '.[] | select(.title=="DR SNAPSHOT RESULT") | .message'
# Expect: status=MATCH, primary_tree == secondary_tree == <new-main-tree>.
# Confirm locally: git rev-parse <new-main-sha>^{tree}
```

## 3 · Issue #6: prepared comment and close

Issue #6 (`[P0] Unblock private DR access and confirm the authoritative secondary
before synchronization`) is OPEN. The verification below is current through the
PR #31 merge. The writing session's connection carries admin/push/triage, so —
unlike earlier sessions — it can post and close. If this connection cannot (403),
the owner pastes the same text.

Comment text (paste-ready; also checked in at
`ops/dr/ISSUE_6_CLOSEOUT_COMMENT_2026_10_06.md`):

```text
Issue #6 close-out — evidence re-read live through the PR #31 merge (2026-10-06)

The DR verification record now holds 28 MATCH checkpoints and 20 replication
writes through PR #31 (main d46d8b3, tree bb8632f6...). The latest checkpoint is
check-run 112253587690 (workflow run 37458973059), completed 2026-10-06T11:50:21Z:

- status=MATCH
- primary tree = secondary tree = bb8632f62eb978417dc4fb39265d32c305f3942f
- rollback commit retained: 42c401d27070c037b3f3782735af0d144fe4465e
- traffic_switched=NONE

Checkpoints #21-#28 cover the #28, #27, #30 and #31 main tips (plus schedule
confirmations); every annotation tree was re-read from the GitHub API and
cross-checked against `git rev-parse <sha>^{tree}`.
One tip was never verified and is recorded as a gap, not a match: 95b2133
(PR #29 squash, tree b457b3d1...) — its only workflow run (37455387004) failed
at offline-tests (stale BUILD_AND_CONFIGURATION, check-run 112241605747) so
verify-or-sync was skipped, and no schedule run covered it before #27 merged.
The secondary moved from the #28 tree directly to the #27 tree on the next
verified write; exact-snapshot replication does not need the intermediate tip,
but the chain documents the hole.

Evidence: ops/dr/DEPLOYED_MATCH_2026_10_04.json (observations #21-#28, window C)
and the generated ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md.
Any row re-verifies without log access:
`gh api repos/Vyomaraj1356/Vyomarajai/check-runs/<id>/annotations`
-> the DR SNAPSHOT RESULT annotation carries the row verbatim.

This closes the tracked Git main-snapshot verification criteria through PR #31.
It does NOT claim independent-site disaster recovery, runtime backup/restore,
production RPO/RTO, or switched production traffic.
```

Close procedure:

```bash
gh issue view 6 --json state --jq .state                     # expect OPEN
gh issue comment 6 --body-file ops/dr/ISSUE_6_CLOSEOUT_COMMENT_2026_10_06.md
gh issue close 6 --comment "Closed with the verification above; scope remains Git-snapshot replication only."
gh issue view 6 --json state --jq .state                     # expect CLOSED
```

## 4 · Then build, in priority order

Do these AFTER sections 1–3, one pull request per item. Each item states its
first command and its done-condition. Nothing here is built yet; the plan does
not claim otherwise.

1. **Monitoring probes.** `/reports/realtime` measures per request, which is
   weaker than a monitor. Build `ops/vyomaraj-core/handover/probes.py`: probes
   each local port (listening, HTTP status, latency), appends JSONL to an
   UNTRACKED local log, writes a latest-snapshot file, and serves it read-only
   at `/reports/monitor` ("no probe has run yet" when absent). Tests use tmp
   dirs. Done when: last successful check, latency, and consecutive failures
   are readable for every port, and the gate covers the new code.
   First command: `python3 ops/vyomaraj-core/handover/probes.py --once --state /tmp/vyomaraj-probes.jsonl`.
2. **Owner authentication.** `ops/shriyantra/owner_guard.py` already verifies
   Ed25519 owner approvals fail-closed, but nothing calls it. Wire it in front
   of ONE mutating endpoint first (`/api/approvals/decide` on high-risk items),
   deny-by-default, with tests proving unauthenticated calls fail closed and
   the public viewer stays readable. The passkey/WebAuthn issuer and key
   provisioning are owner actions — document them, do not fake them.
   Done when: one endpoint enforces owner approval end-to-end in tests.
3. **One real agent workflow.** Approvals desk + owner gate: propose → owner
   step-up approve → execute once (replay-safe via consumed jti) → auditable
   record. No new lane until this loop is real. Done when: the loop runs
   against the local stack with green tests and a recorded audit entry.
4. **APK signing.** The repository cannot sign (no key, no Android project —
   `verify_live_wiring.py` states this). Owner runs, on their own machine:
   `keytool -genkeypair -keystore vyomaraj-release.keystore -alias vyomaraj -keyalg RSA -keysize 2048 -validity 10000`
   then `apksigner sign --ks vyomaraj-release.keystore Vyomaraj-App.apk`,
   then `apksigner verify --print-certs Vyomaraj-App.apk`. Never commit the
   keystore. Done when: a signed APK verifies on a real device (owner confirms).
5. **One publishing route.** Hand-publish from the owner's own account first
   (accounts, not code). Only after published content exists, add the cheapest
   automation with a credential the owner provisions. Done when: one episode is
   publicly reachable from an owner-held account and the repo links it.
6. **One monetization route.** Free analytics counter first (owner picks the
   provider; snippet slot prepared but NOT enabled without the decision),
   confirm one real visit is recorded. Done when: one genuine visit is measured.

## 5 · Rules that must not be broken

1. No force-push, ever — to any branch. Cherry-pick or re-apply instead.
2. No fabricated status: never print LIVE / ACTIVE / synced / MATCH unless a
   command on this page just measured it.
3. Recover before rebuilding: `git diff --name-status main origin/arena/<branch>`
   before re-implementing anything; a rebuild is labeled REBUILT, never "recovered".
4. Every claim reproducible: each document names the command that fails when the
   claim stops being true.
5. Lost bytes stay lost: sandbox-only commits that never reached GitHub are
   reported as unrecoverable, never re-described as "published".

## 6 · Where everything lives

| Artifact | File | Page route | Download route |
|---|---|---|---|
| This plan | `ops/vyomaraj-core/handover/NEXT_SESSION_PLAN_2026_10_07.md` | `/reports/next-session-plan` | `/reports/download/next-session-plan.md` · `.txt` |
| Session update | `ops/vyomaraj-core/handover/SESSION_UPDATE_2026_10_06.md` | `/reports/session-update` | `/reports/download/session-update.md` · `.txt` |
| Handover notepad (frozen) | `ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_2026_10_04.txt` | `/reports/handover-notepad` | `/reports/download/handover-notepad.txt` |
| Post-PR25 companion (frozen) | `ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_POST_PR25_2026_10_04.txt` | `/reports/post-pr25-handover` | `/reports/download/post-pr25-handover.txt` |
| DR sync results | `ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md` | `/reports/dr-sync` | (page only) |
| Issue #6 resolution | `ops/dr/ISSUE_6_RESOLUTION_2026_10_04.md` | `/reports/issue-6` | (page only) |
| Issue #6 close-out comment | `ops/dr/ISSUE_6_CLOSEOUT_COMMENT_2026_10_06.md` | (file only — paste into GitHub) | — |
| AI handoff pack | `ops/vyomaraj-core/handover/transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip` | `/reports/ai-handoff` | `/reports/download/ai-handoff.zip` |

All page and download routes answer on all four backends: viewer 4174, gateway
4176, lane A 4181, lane B 4182 (section 2, step 4).

## 7 · Recovery notes for this rebuild

- The prior session's work was verified ABSENT before rebuilding: `git ls-remote
  origin` shows `refs/heads/arena/582559e8-vyomarajai` at `cce1074` (merged via
  PR #31); `git cat-file -t 002f5ed` and `git cat-file -t 9e241e9` both fail.
  Nothing was pushed from that branch because there was nothing new to push.
- This branch is the 12th `origin/arena/*` ref. Two builders hardcoded "11
  sessions" (`build_recovery_index.py`, `build_go_live_brief.py`); they are now
  count-dynamic, and the viewer notices are count-neutral. The recovery index
  and go-live brief regenerate AFTER the first push (counts depend on it).
- Regeneration order (order matters): DR record → DR sync report → configuration
  report → transfer package + manifest → post-PR25 package + manifest → AI
  handoff archive → offline suites (TEST_EVIDENCE) → live verifiers (PREVIEW
  VERIFICATION, LIVE WIRING) → configuration report again (it embeds
  route-check counts) → packages again → suites again.
- Frozen files (never rewrite; add companions instead): the handover notepad
  (published SHA256), the post-PR25 companion, the issue/PR ledger snapshot
  (checkpoint #19 pins its `--check`), the DR policy approval (consumed).
- The DR extension rule used here: one checkpoint row per distinct new main tip
  plus the latest schedule confirmation, every annotation re-read live and every
  tree cross-checked with `git rev-parse`. Window C (PR #29 tip, never verified)
  is recorded as a gap. See `DEPLOYED_MATCH_2026_10_04.json`,
  `record_extension_2026_10_06_b`.
