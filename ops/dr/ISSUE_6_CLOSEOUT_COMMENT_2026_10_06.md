Issue #6 close-out — evidence re-read live through the PR #34 merge (2026-10-06)

The DR verification record now holds 32 MATCH checkpoints and 22 replication
writes through PR #34 (main d97122f, tree 70b69f8e...). The latest checkpoint is
check-run 112287316035 (workflow run 37468965584, scheduled reconciliation),
completed 2026-10-06T13:13:06Z; the merge itself was verified by check-run
112279322282 (workflow run 37466613010), completed 2026-10-06T12:54:50Z:

- status=MATCH
- primary tree = secondary tree = 70b69f8e03317c64ecb379014843f026795fad69
- rollback commit retained: 490880630a5a73e895982814da8d4f9a886bc493
- traffic_switched=NONE

Checkpoints #21-#32 cover the #28, #27, #30, #31, #32, #33 and #34 main tips
(plus schedule confirmations); every annotation tree was re-read from the GitHub
API and cross-checked against `git rev-parse <sha>^{tree}`. One write is
attributed by annotation tree rather than by head filing: schedule run 37465859915
(check-run 112276811314, rollback b6656066) wrote the e7b65c59 tree for tip
e9bfba0 while filed under the older head 1c13650, so checkpoint #30 is recorded
there as a no-op (check-run 112277370308) and the write is not double-counted.
One tip was never verified and is recorded as a gap, not a match: 95b2133
(PR #29 squash, tree b457b3d1...) — its only workflow run (37455387004) failed
at offline-tests (stale BUILD_AND_CONFIGURATION, check-run 112241605747) so
verify-or-sync was skipped, and no schedule run covered it before #27 merged.
The secondary moved from the #28 tree directly to the #27 tree on the next
verified write; exact-snapshot replication does not need the intermediate tip,
but the chain documents the hole.

Evidence: ops/dr/DEPLOYED_MATCH_2026_10_04.json (observations #21-#32, window C)
and the generated ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md.
Any row re-verifies without log access:
`gh api repos/Vyomaraj1356/Vyomarajai/check-runs/<id>/annotations`
-> the DR SNAPSHOT RESULT annotation carries the row verbatim.

Status note (2026-10-06, session arena/05152d2a-vyomarajai): this text was ready
to post, and four write attempts were made from the Arena connection in this
session (comment and close, CLI and REST). All returned HTTP 403 "Resource not
accessible by integration" — the connection is issues=read only. The issue
therefore stays OPEN until an owner posts this comment and closes it; the
attempts are recorded verbatim in ops/dr/ISSUE_6_ACCESS_RECHECK_2026_10_06.json
and the write is repeatable with `python3 ops/dr/post_issue_closeout.py --post`
using a credential that has issues=write.

This closes the tracked Git main-snapshot verification criteria through PR #34.
It does NOT claim independent-site disaster recovery, runtime backup/restore,
production RPO/RTO, or switched production traffic.
