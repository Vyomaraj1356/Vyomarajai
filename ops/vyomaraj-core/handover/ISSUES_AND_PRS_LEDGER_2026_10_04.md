# Issues and pull requests ledger — 2026-10-04

**New-session runbook (in order)**

This ledger accounts for the known open issue/PR decisions and the repository conflicts. It is a checked-in snapshot, not a claim that every external state is unchanged. Re-read GitHub before acting.

Snapshot commit: `d9147fffc5884702d7fcbc38fd666d62622f3b8c` · recorded `2026-10-04T10:56:22Z` · source: Read-only GitHub state was re-read in this session for issue #6, PRs #2/#3/#4/#7/#9, the merged PR list and the #24 verify-or-sync check-run. Text conflicts and owner decisions are not inferred from GitHub state.

| # | Reference | State | Summary | Next action |
|---:|---|---|---|---|
| 1 | #6 — Unblock private DR access and confirm the authoritative secondary before synchronization | **READY_TO_CLOSE** | Issue acceptance evidence is current through the PR #24 merge. The issue is still OPEN; no comment or close action has been performed. | Re-read the recorded checkpoint rows live, then use the prepared comment and close-out command only after owner confirmation. |
| 2 | #2 — Security guard from a divergent branch | **OWNER_DECISION_REQUIRED** | OPEN; reported no merge base with main. Do not merge this branch. Re-apply selected content as a fresh reviewed change if the owner wants it. | Owner selects whether any specific file or behavior should be freshly re-applied. |
| 3 | #3 — Live preview and reconciled recovery from a divergent branch | **OWNER_DECISION_REQUIRED** | OPEN; reported no merge base with main. Do not merge this branch. Re-apply only owner-selected changes on a fresh branch. | Owner identifies any specific change to re-apply; leave the PR open and untouched meanwhile. |
| 4 | #4 — Active integrity guard from a divergent branch | **OWNER_DECISION_REQUIRED** | OPEN; reported no merge base with main. Do not merge this branch. Re-apply selected content as a fresh reviewed change if the owner wants it. | Owner selects whether any specific file or behavior should be freshly re-applied. |
| 5 | #7 — Bharath-Laxman-Hermes resilience foundation | **OWNER_DECISION_REQUIRED** | OPEN; reported no merge base with main. Do not merge this branch. Re-apply owner-selected content as a new change if desired. | Owner selects whether any specific resilience behavior should be freshly re-applied. |
| 6 | #9 — ShriYantra RAG CAG MAG and Arena foundation | **WATCH** | OPEN draft from another session. It was not reviewed, edited or closed as part of this recovery. | Continue read-only watch; do not merge, close or modify without an explicit owner decision. |
| 7 | #10–#24 — Published merge chain | **RESOLVED_DOCUMENTED** | The PR #10–#24 merge chain is recorded in main and the DR verification record; PR #24 is the current main tip in this checkout. | Keep the merge/checkpoint mapping in the generated DR report; no action required on these merged PRs. |
| 8 | All-chats database — Heading says 28 chats; the file contains 34 numbered entries | **FIX_APPLIED_OFFLINE** | The source file is preserved unchanged. The viewer notice states both counts and asks the owner to confirm; neither count is silently rewritten. | Owner confirms the canonical count; then update the source with a dated correction while preserving its history. |
| 9 | Contract status — Conflicting contract-status records | **OWNER_DECISION_REQUIRED** | The conflict is documented; this ledger does not guess which record governs or erase historical text. | Owner identifies the governing record; retain a superseded-by pointer on the other record. |
| 10 | Owner decision O-01 — Secret manager and access policy | **OWNER_DECISION_REQUIRED** | No secret manager is configured by this plan and no secret value belongs in the repository. | Follow auto-align step o01-secret-manager. |
| 11 | Owner decision O-03 — Tool accounts and plans | **OWNER_DECISION_REQUIRED** | Required accounts and owner-selected plans have not been inferred or activated here. | Follow auto-align step o03-tool-accounts. |
| 12 | Owner decision O-04 — Meaning of the recorded term "posilki" | **OWNER_DECISION_REQUIRED** | The term remains unidentified; no tool or service was inferred from it. | Follow auto-align step o04-posilki. |
| 13 | Provider items P-01–P-15 — Research, media, publishing, scheduling and analytics providers | **OWNER_ACTION_REQUIRED** | Provider setup paths are mapped; connection and operational readiness remain unverified. | Follow auto-align steps p01-research-drafting through p04-review-gates after owner decisions. |
| 14 | Studio/services S-01–S-14; DR/ops D-01–D-08 — Studio, services, independent DR and operations | **OWNER_ACTION_REQUIRED** | Local preview and Git snapshot evidence do not establish an installed studio, independent DR, runtime restore or 24x7 operations. | Follow auto-align steps s01-studio-install through d04-intelligence-learning in order. |

## Decision rules for open pull requests

- PRs #2, #3, #4 and #7 are **not to be merged** from their current branches: the recorded blocker is no merge base with `main`. If selected, re-apply the desired content as a fresh reviewed change.
- PR #9 is another session's draft and stays untouched unless the owner explicitly directs otherwise.
- The #10–#24 merge chain is already recorded as merged; do not duplicate it as pending work.

## Offline conflict notices

- **All-chats file:** its heading says 28 chats while it contains 34 numbered entries. The viewer states both values; the historical source remains unchanged until the owner confirms the canonical count.
- **Contract status:** conflicting records are preserved. The ledger does not choose an authority; follow auto-align step `o02-contract-authority` and keep a superseded-by pointer after the owner decides.

## Issue #6 close-out — prepared, not sent

Issue #6 is still `OPEN`. The latest recorded point is checkpoint **#19**: **15 replication writes** through PR #24.
Check-run `111404791435` / workflow run `37191596397` completed `2026-10-04T09:17:04Z` with `status=MATCH`; primary and secondary trees are both `e8c66bd451484071d03afc68ac1aeeb010e8fa96`; rollback `be715362ca394464844e5058745fb10914e40a1e` is retained.

Prepared comment: `ops/dr/ISSUE_6_CLOSEOUT_COMMENT_2026_10_04.md`. No GitHub comment or issue close has been performed by this builder.

Runbook (re-read first; do not run automatically):

1. Before any GitHub write, use the 19 check_run_id values in DEPLOYED_MATCH_2026_10_04.json to re-read every check-run annotation via gh api repos/Vyomaraj1356/Vyomarajai/check-runs/{id}/annotations; compare status, primary_tree, secondary_tree, data_match and rollback_commit row by row. Specifically confirm check-run 111404791435 (PR #24) is MATCH with equal e8c66bd4 trees. Stop if any row is missing or differs.
2. Run python3 ops/vyomaraj-core/handover/build_dr_sync_report.py --check and inspect checkpoint #19 in ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md.
3. After owner approval, post the prepared statement with gh issue comment 6 --repo Vyomaraj1356/Vyomarajai --body-file ops/dr/ISSUE_6_CLOSEOUT_COMMENT_2026_10_04.md.
4. After the comment succeeds and issue #6 is still OPEN, close with gh issue close 6 --repo Vyomaraj1356/Vyomarajai --reason completed --comment "19 MATCH checkpoints (15 replication writes) through merge #24".
5. If the integration returns 403, do not retry with another credential; preserve the prepared file and report that owner-side permission is required.

If GitHub returns 403, stop. Do not switch credentials or retry a write through another identity; retain the prepared comment and ask the owner to perform the action with the correct permission.

## Auto-align paths

The provider, studio, service and operations items have finite completion paths in `AUTO_ALIGN_NEXT_SESSION_2026_10_04.md`; the corresponding JSON source is `AUTO_ALIGN_NEXT_SESSION.json`. Every open platform item is mapped to a step id in `PLATFORM_CONFIGURATION_CHECK_2026_10_04.md`.

## Scope

This ledger does not assert that a provider is connected, a contract executed, production traffic switched, or independent runtime disaster recovery tested. Owner decisions remain pending until evidence is recorded and reviewed.
No prices, plan limits or earnings projections are stated here.
