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
