# VYOMARAJ — NEXT-SESSION PLAN

Written 2026-10-06 in session `arena/6bc12929-vyomarajai`, for the session of/after
2026-10-07; amended 2026-10-07 in `arena/a83291a3-vyomarajai`. This is the "start
here" page. Every claim below was verified in this checkout or through the GitHub
API; each section says how. If any command in section 2 disagrees with this
document, the command is right.

Marker: NEXT-SESSION PLAN (the viewer contract checks for this line).

> **CURRENT-STATE OVERRIDE — read this before any dated steps below (7 October 2026).** This file
> was authored for a prior session; its branch, PR, DR, and close-out instructions are historical.
> Current work stays on `arena/a83291a3-vyomarajai`. Issue #6 remains OPEN/P0 and owner/admin
> blocked; the 6 October close-out draft and all issue-write commands below are stale and **must not
> be posted or run**. PR #41 is OPEN/non-draft with combined DR/preview scope; #39 and #42 are
> OPEN/DRAFT. GitHub Pages serves `main` at `04b7ae60`; this branch is not deployed. See
> `ISSUES_AND_PRS_LEDGER.json` and its 7 October live-read addendum for current status.

## 0 · The state in one paragraph (historical snapshot; superseded above)

`main` was `d46d8b3` (PR #31 merge, 2026-10-06 11:49 UTC, tree
`bb8632f62eb978417dc4fb39265d32c305f3942f`) and the DR secondary was recorded as MATCH at that
point. The previous session's commits `002f5ed` + `9e241e9` NEVER reached GitHub (verified in that
session), so its plan/routes/pack were rebuilt as new work on the then-current branch
`arena/6bc12929-vyomarajai`. These are provenance notes, not today's branch or current DR status.

## 1 · Publication record (historical; do not replay old branch commands)

The prior work and PR #32 are already recorded in Git history. The historical push/PR-create/merge
and fallback commands have been omitted here so they cannot be mistaken for current authorization.
The current Arena session branch is fixed to `arena/a83291a3-vyomarajai`; consult live GitHub state
and obtain explicit owner approval before any public merge or deployment. Never force-push or merge
without owner approval. Never rewrite the frozen files listed in section 7.

## 2 · Verify the publish

Run in order. Each line is a command and its expected result.

```bash
# 1. Privacy guard — must print OK, no identifiers.
python3 ops/vyomaraj-core/handover/sanitize_personal_data.py --check

# 2. Full offline gate — must end "0 failures".
python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci

# 3. Safe preview posture: :5310 serves the public asset allowlist and bounded,
# deterministic, ephemeral POST /api/plan for two local experiences only.
# The owner-writer studio/gateway services remain separate and must not be exposed.
# They enforce IPv4 loopback binds; privileged writes require request-scoped owner tokens,
# but no issuer/key is configured. Research workers are opt-in.

# 3a. If the sandbox preview is running, check the demo page and one local plan:
curl -fsS http://127.0.0.1:5310/demo.html >/dev/null
curl -fsS -H 'Content-Type: application/json' -d '{"experience":"bhakti","topic_id":"overview"}' http://127.0.0.1:5310/api/plan | python3 -c 'import json,sys; p=json.load(sys.stdin); assert p["ai_calls_made"] is False and p["publishing_enabled"] is False; print("local plan OK; no AI call or publishing")'

# 4. Optional local GET checks — run only against that secured isolated test stack:
for p in 4174 4176 4181 4182; do
  for r in /reports/next-session-plan /reports/session-update /reports/monitor \
           /reports/download/next-session-plan.md /reports/download/next-session-plan.txt \
           /reports/download/session-update.md /reports/download/session-update.txt; do
    printf "%s %s " "$p" "$r"; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:$p$r"
  done
done

# 4b. One-shot loopback sample; report page only reads the latest snapshot.
python3 ops/vyomaraj-core/handover/probes.py --once --state /tmp/vyomaraj-probes.jsonl

# 5. Optional live verifiers — only against the secured, isolated test stack above:
python3 ops/vyomaraj-core/handover/verify_preview.py
python3 ops/vyomaraj-core/handover/verify_live_wiring.py

# 6. Read-only DR diagnostics only after explicit owner authorization; never dispatch or write:
gh run list --workflow vyomaraj-sync-both.yml --branch main --limit 2
gh api repos/Vyomaraj1356/Vyomarajai/commits/<new-main-sha>/check-runs \
  --jq '.check_runs[] | select(.name=="verify-or-sync") | {id, conclusion}'
gh api repos/Vyomaraj1356/Vyomarajai/check-runs/<verify-id>/annotations \
  --jq '.[] | select(.title=="DR SNAPSHOT RESULT") | .message'
# Expect: status=MATCH, primary_tree == secondary_tree == <new-main-tree>.
# Confirm locally: git rev-parse <new-main-sha>^{tree}
```

## 3 · Issue #6: current owner/admin blocker; do not close

Issue #6 (`[P0] Unblock private DR access and confirm the authoritative secondary
before synchronization`) remains OPEN/P0. The 6 October comment text below is
historical and stale. A 7 October read-only audit found the connected identity
can list only the primary repository; four secondary-name probes returned 404
(which does not prove that a private repository does not exist), and Actions
variables/secrets return 403. The exact authoritative target and current access
are therefore not established. Keep the issue open; do not post a close-out
comment or run any close command.

Owner/admin next step: confirm the exact existing secondary repository and
authorize the minimum required access. Then perform a fresh read-only target and
permission check. Only after owner-approved replication and a fresh matching
checkpoint should the acceptance criteria be reassessed. Never share secret
values in chat.

**Historical 6 October close-out text (preserved for provenance only; do not post):**

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

> **Historical update, 6 October 2026 (session `arena/05152d2a-vyomarajai`):** the comment file was
> refreshed with a later checkpoint, but five comment/close attempts returned 403. The refreshed
> file remains a historical draft. The 7 October access and target blockers supersede all prior
> “paste this” or “ready to close” language. Preserve the attempt record at
> `ops/dr/ISSUE_6_ACCESS_RECHECK_2026_10_06.json`; do not post either draft.

There is no close procedure authorized in this plan. If an owner needs to recheck status, use a
read-only query only and stop if access is denied; do not issue a comment, close, dispatch, or secret
write:

```bash
gh issue view 6 --repo Vyomaraj1356/Vyomarajai --json state,labels,title
# Expected current state: OPEN, P0. Do not follow this with gh issue comment or gh issue close.
```

## 4 · Then build, in priority order

These are the remaining actions, in priority order, one pull request per item.
Items 1–3 now have local code/test progress on this working branch: manual
monitoring, the loopback/authentication hardening and a persistent local approval
slice. None is production monitoring or a deployed/verified provider-backed
agent. Real owner issuer/key configuration, agent execution, and items 4–6 still
require out-of-band owner decisions and evidence; no gate is bypassed.

1. **Monitoring probes — LOCAL BUILD COMPLETE in this working branch.**
   `ops/vyomaraj-core/handover/probes.py` makes one bounded GET to each of four
   configured loopback preview ports (defaults 4174/4176/4181/4182), disables
   proxies, refuses redirects, and keeps the host hard-wired to 127.0.0.1.
   It records listener/HTTP/latency/last-success/consecutive-failure fields,
   appends an untracked JSONL sample, and atomically replaces the latest JSON
   snapshot. `/reports/monitor` is in both the report viewer and studio server;
   its GET is read-only and says no probe has run when the snapshot is absent.
   Ten module tests cover success/failure/recovery, redirects, atomic writes,
   escaping, and missing/corrupt state. No dependency was installed. This is a
   manual preview probe only: not scheduled, alerting, production uptime,
   replication-lag, backup, or independent-site DR monitoring; `/tmp` data does
   not survive a sandbox restart. Local validation is now complete: a fresh
   stack on 5174/5176/5181/5182 returned 200 on all four monitor routes, the
   verifiers reported no problems, and the offline gate passed 48/48. Exact
   scope and sample results are in `SESSION_UPDATE_2026_10_06.md` section 9.
   Command: `python3 ops/vyomaraj-core/handover/probes.py --once --state /tmp/vyomaraj-probes.jsonl`.
2. **Owner-authenticated local slice — CODE IMPLEMENTED; TRUSTED CONFIG BLOCKED.**
   The studio now verifies request-scoped Ed25519 owner tokens bound to the exact
   action and canonical JSON payload. Approval/change decisions require step-up;
   research writes use one-time replay protection. The approvals desk atomically
   consumes JTI, updates the queue, stores the decision and appends a local hash-
   chained audit event. Tests cover missing-token denial, target binding, replay,
   concurrent writes, tampering and no publication. Real keys/issuer/security
   epoch/replay configuration are not provisioned, so privileged calls currently
   fail closed. Supply that configuration only through the owner's trusted
   control plane; never ask for keys/tokens in chat.
3. **One real agent workflow — PARTIAL, NO AGENT EXECUTION.** The owner decision
   can be persisted locally when a real signed token is configured. No creating
   agent is contacted, no message is sent, no publication/upgrade occurs, and the
   local hash chain is not an external signed audit witness. The next step needs
   owner-approved runtime/identity configuration plus an authenticated agent
   adapter; do not count a queued/approved metadata record as a live agent.
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
| Local one-shot monitor | `ops/vyomaraj-core/handover/probes.py` + untracked `/tmp` snapshot | `/reports/monitor` | no download; page is read-only |
| Handover notepad (frozen) | `ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_2026_10_04.txt` | `/reports/handover-notepad` | `/reports/download/handover-notepad.txt` |
| Post-PR25 companion (frozen) | `ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_POST_PR25_2026_10_04.txt` | `/reports/post-pr25-handover` | `/reports/download/post-pr25-handover.txt` |
| DR sync results | `ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md` | `/reports/dr-sync` | (page only) |
| Issue #6 resolution | `ops/dr/ISSUE_6_RESOLUTION_2026_10_04.md` | `/reports/issue-6` | (page only) |
| Historical issue #6 close-out draft (stale; do not post) | `ops/dr/ISSUE_6_CLOSEOUT_COMMENT_2026_10_06.md` | provenance only | — |
| Current issue #6 status | `ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json` | `/reports/issue-6` | read-only report |
| AI handoff pack | `ops/vyomaraj-core/handover/transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip` | `/reports/ai-handoff` | `/reports/download/ai-handoff.zip` |

The live-wiring snapshot at 06:11 UTC on 7 October recorded route responses from viewer
4174, gateway 4176 and lane studios 4181/4182; this is historical evidence only. A follow-up
port/process probe at 08:15 UTC found no listeners on 3000, 4174, 4176, 4181 or 4182. The
studio/gateway code has since been hardened to loopback binds and fail-closed owner-token checks,
but no trusted token issuer is configured and no writer process was started during this pass.
Do not expose the rehearsal publicly or enable research-worker egress without owner-approved
configuration and an isolated test plan.

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

## 8 · Execution result (session `arena/05152d2a-vyomarajai`, 2026-10-06)

Sections 1-3 above were executed by the session this plan was written for. The
short version is in `SESSION_UPDATE_2026_10_06.md` section 6; the record-level
evidence is in `ops/dr/DEPLOYED_MATCH_2026_10_04.json`
(`record_extension_2026_10_06_c`).

- **DR record:** checkpoints #30 (PR #33 tip, no-op MATCH), #31 (PR #34 tip,
  write + MATCH, rollback `49088063…`) and #32 (schedule confirmation on the
  PR #34 tip) recorded from live annotation re-reads; 32 checkpoints / 22
  writes. The requested rollback-commit timestamp could not be read (private
  secondary, HTTP 404 by this credential) and is recorded as a failed read with
  the public step interval `12:54:21Z-12:54:47Z` as the bounded substitute.
- **Issue #6:** historical comment + close attempts returned 403 and left it OPEN. The 7 October
  live audit found the exact secondary target/access still unverified and Actions variables/secrets
  blocked (403); issue #6 remains OPEN/P0 and is not ready for comment or closure. Do not run
  `ops/dr/post_issue_closeout.py --post`.
- **Recovered/absent:** the previous session's `3ed47b3` and its
  `ask_server.py`, `test_ask_server.py` and handover note were verified absent
  from every ref, from the GitHub API (422) and from the checked-in archives.
  The ask slice was therefore **rebuilt** as new work (not recovered), tested
  and shipped on this branch.
- **Product:** `ask_server.py` on port 4190 answers from the 128 positions and
  197 content references with citations and refuses to invent; see section 6 of
  the session update for the honest scope (retrieval, not generation — the
  model key is an owner action).
