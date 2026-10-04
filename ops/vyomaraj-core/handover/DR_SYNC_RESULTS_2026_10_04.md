# Vyomaraj — DR sync results — 2026-10-04

**Generated file — do not edit by hand.** Rebuild with `python3 ops/vyomaraj-core/handover/build_dr_sync_report.py` from the repository root; `--check` verifies this checked-in copy still matches its evidence.

## 1. Scope — what this record does and does not assert

Primary repository: `Vyomaraj1356/Vyomarajai`. Secondary repository: `deepakGoyal1356/Vyomaraj-Agent-6d64e`.
Main tip covered by this record: `244f5a66cee8c80bab1603ea4d9aad0ff942a25a`.
Workflow: `.github/workflows/vyomaraj-sync-both.yml` — triggers: push, pull_request, workflow_dispatch, schedule; schedule: `*/30 * * * *` (UTC).
Recorded scope: Git main tracked-file snapshot verified by the primary repository Actions workflow; not runtime/site DR.

This is a Git-snapshot replication record. It is **not** a production disaster-recovery approval and it says nothing about runtime databases, live media sessions, provider accounts, secrets or production traffic.

## 2. Evidence sources (all checked in)

| Source | SHA256 | What it contributes |
|---|---|---|
| `ops/dr/DEPLOYED_MATCH_2026_10_04.json` | `ecff349186244f0c299a806ac80d862b65484f9e8e4f6ac3ec8b25b5ddb93405` | 13 MATCH checkpoints, 9 replication writes, 1 blocked run, 1 read-only probe |
| `ops/dr/DR_POLICY.json` | `6090042dc9e05fa1273ba0f0345a6821d633e28c755cac6be806712e7ee222df` | scope flags and the time-boxed one-snapshot removal approval |
| `.github/workflows/vyomaraj-sync-both.yml` | `f567ee62daacd1d4aa23aec9d6cc0e142891f5feefd4971f9b8581f6b049f398` | triggers and schedule |

Method: All successful verify-or-sync check-runs on the main tip were enumerated and their public annotations parsed. A run that replicated carries rollback_commit; an idempotent no-op does not.

Re-validation: every check-run id in this record, plus the #18 run, was re-read live from the GitHub API; each DR SNAPSHOT annotation was re-parsed and compared with the values stored here. Result: all 13 checkpoints re-read as status=MATCH with primary_tree == secondary_tree; no mismatch in status, trees or rollback commits

Timestamp corrections applied during that re-validation (status, trees and rollback commits were unchanged):

- check-run `111379204732`: recorded `2026-10-04T06:31:25Z` → live `2026-10-04T06:31:26Z`
- check-run `111380439332`: recorded `2026-10-04T06:46:30Z` → live `2026-10-04T06:40:03Z`

## 3. Verification checkpoints (13)

A checkpoint is a successful `verify-or-sync` run on a main tip. `rollback_commit` present means the run replicated (wrote) the snapshot to the secondary; absent means the two snapshots were already identical and the run changed nothing. Trees are shown shortened from the full 40-character values in the record; every row ended `data_match=true`.

| # | completed (UTC) | merge | PR | run | check-run | status | primary tree | secondary tree | replication write |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-03T13:32:27Z | `3936badc63ce` | base | `37126479491` | `111212722666` | MATCH | `3e3c55bbfca2` | `3e3c55bbfca2` | yes (`9d8678c69092`) |
| 2 | 2026-10-03T18:24:59Z | `3936badc63ce` | base | `37144067397` | `111264329856` | MATCH | `3e3c55bbfca2` | `3e3c55bbfca2` | no |
| 3 | 2026-10-04T00:12:28Z | `3936badc63ce` | base | `37164197259` | `111323711822` | MATCH | `3e3c55bbfca2` | `3e3c55bbfca2` | no |
| 4 | 2026-10-04T03:55:22Z | `3936badc63ce` | base | `37175427270` | `111356987170` | MATCH | `3e3c55bbfca2` | `3e3c55bbfca2` | no |
| 5 | 2026-10-04T05:38:41Z | `3936badc63ce` | base | `37180458704` | `111371856577` | MATCH | `3e3c55bbfca2` | `3e3c55bbfca2` | no |
| 6 | 2026-10-04T06:07:16Z | `8adf9496ab14` | #10 | `37181811020` | `111375777820` | MATCH | `ad4321bfa840` | `ad4321bfa840` | yes (`7a7a539ddca7`) |
| 7 | 2026-10-04T06:18:22Z | `2424e786327d` | #12 | `37182374090` | `111377398899` | MATCH | `434fc389fa45` | `434fc389fa45` | yes (`4363387e94bf`) |
| 8 | 2026-10-04T06:21:30Z | `15cbfea07ea5` | #13 | `37182538000` | `111377861073` | MATCH | `5a9d1418a037` | `5a9d1418a037` | yes (`5203c2223481`) |
| 9 | 2026-10-04T06:25:24Z | `dd341accd7ee` | #14 | `37182720884` | `111378391997` | MATCH | `01197482660b` | `01197482660b` | yes (`11c1de61f21b`) |
| 10 | 2026-10-04T06:31:26Z | `eead435ad0bb` | #15 | `37183003792` | `111379204732` | MATCH | `3604bb15a257` | `3604bb15a257` | yes (`1b374fd94de8`) |
| 11 | 2026-10-04T06:34:56Z | `a128173cbb10` | #16 | `37183181239` | `111379714913` | MATCH | `7b166ac14ac0` | `7b166ac14ac0` | yes (`ced0a0928492`) |
| 12 | 2026-10-04T06:40:03Z | `c1d625047056` | #17 | `37183425727` | `111380439332` | MATCH | `1d13c7ee7a50` | `1d13c7ee7a50` | yes (`a979bac5aab9`) |
| 13 | 2026-10-04T06:44:02Z | `244f5a66cee8` | #18 | `37183619048` | `111380998467` | MATCH | `b6029f977847` | `b6029f977847` | yes (`6a614f7f6706`) |

All 13 rows were re-read from the GitHub API at 2026-10-04T07:11:55Z and matched the values stored in the record.

## 4. Replication writes (9)

| merge | PR | run | check-run | rollback commit (previous secondary tip, retained) |
|---|---|---|---|---|
| `3936badc63ce` | base | `37126479491` | `111212722666` | `9d8678c69092db794fe42d3686093305f9fba7a4` |
| `8adf9496ab14` | #10 | `37181811020` | `111375777820` | `7a7a539ddca7e0ee12f5d216c84edaa2a1d61b74` |
| `2424e786327d` | #12 | `37182374090` | `111377398899` | `4363387e94bfe03d6e9364dee4f36345ddca15d3` |
| `15cbfea07ea5` | #13 | `37182538000` | `111377861073` | `5203c22234810a128f6a1e68c0ffcb3419a36dbc` |
| `dd341accd7ee` | #14 | `37182720884` | `111378391997` | `11c1de61f21b4b2a559eb7eb01adf4f2c4c5a088` |
| `eead435ad0bb` | #15 | `37183003792` | `111379204732` | `1b374fd94de8d2f535785235124c6d087294cc1a` |
| `a128173cbb10` | #16 | `37183181239` | `111379714913` | `ced0a09284924e5fa8e98289dbc507b1ec0d9b1b` |
| `c1d625047056` | #17 | `37183425727` | `111380439332` | `a979bac5aab924f97f79549d7e46fa202d765f2c` |
| `244f5a66cee8` | #18 | `37183619048` | `111380998467` | `6a614f7f6706e2564440ebfcf147930b4e5676d1` |

A write replaces the secondary snapshot with the primary snapshot and keeps the previous secondary commit as the rollback parent; no force-push and no history deletion is used.

## 5. The correctly blocked run (1) and its approved resolution

One run in this session did **not** match and is deliberately excluded from the checkpoint count:

- Run `37182034198` on merge #11 (`f8f948b6077c`), check-run `111376415924`, completed 2026-10-04T06:11:11Z.
- Public annotation: `status=BLOCKED; failed_api_operation=NONE_OR_UNCLASSIFIED; http=UNAVAILABLE; traffic_switched=NONE; target_only_files_awaiting_review=1`
- Interpretation recorded with the evidence: The one reviewed path existed only on the secondary; the gate refused to delete it, so the run concluded failure by design. A blocked run is the safety system working, not a replication defect, and is deliberately not counted as a MATCH checkpoint.
- Read-only probe `111376891786` (`b79197bfa791`, 2026-10-04T06:14:30Z) reported:

  `read_access=READ_ACCESS_CONFIRMED; identity=READABLE; primary_repository=READABLE; primary_main=READABLE; secondary_repository=READABLE; secondary_main=READABLE; tree=MISMATCH; writes=NONE; write_permission=UNVERIFIED; primary_files=261; secondary_files=262; missing_on_secondary=0; secondary_only=1; changed_content_or_mode=6; secondary_commit=4363387e94bfe03d6e9364dee4f36345ddca15d3; secondary_tree=ad4321bfa840f43855c05fd99379ca18b78dd374; candidate_files=262; candidate_secondary_only=1; candidate_missing=1; candidate_changed=7`

- Resolution: see DR_POLICY.json one_snapshot_removal_approval (time-boxed, single reviewed path, history retained).

The approval recorded in `DR_POLICY.json` was narrow by design:

- approved: no; consumed: yes; reviewed candidate secondary-only paths: 1; expired at 2026-10-06T06:15:52+00:00.
- expected secondary commit `4363387e94bfe03d6e9364dee4f36345ddca15d3` / tree `ad4321bfa840f43855c05fd99379ca18b78dd374`; fulfilled by run `37182374090`.
- outcome recorded: MATCH after replication; primary_tree == secondary_tree == 434fc389fa45e80300dac3e7d7bf6387a42bdf0c; rollback_commit 4363387e... retained as parent

## 6. Scope limits — do not restate otherwise

- Traffic was never switched by these runs: `traffic_switched` = false.
- Runtime/site disaster recovery was not tested: `runtime_or_site_dr_verified` = false.
- No zero-RPO/RTO claim is made: `zero_rpo_or_rto_claimed` = false; policy `zero_rpo_verified` = false, `zero_rto_verified` = false.
- Automatic target-only file removal is off by default: `automatic_target_only_file_removal` = false; removal needs explicit, time-boxed, human approval per reviewed path.
- Automatic reverse overwrite is off: `automatic_reverse_overwrite` = false.
- Policy scope, verbatim: Git main snapshot only; not runtime databases, secret stores, live media sessions or production traffic.
- Branch scope: This evidence covers primary main only. Two earlier commits on arena/01a1056f-vyomarajai (6e2cfc6, 0c73706) were not on main at the time they were first reported and therefore were not in the DR snapshot then; the branch was subsequently merged through PRs #10-#18 and is now covered by the checkpoints above. Unmerged branch tips are never part of the DR snapshot.

## 7. Re-verify a row yourself

Ask the API for the recorded annotation of any check-run above: `gh api repos/Vyomaraj1356/Vyomarajai/check-runs/<check_run_id>/annotations --jq '.[] | select(.title=="DR SNAPSHOT RESULT") | .message'`.

Compare the returned `status`, `primary_tree`, `secondary_tree` and `rollback_commit` with the row above. No credential beyond read access is required.

END OF DR SYNC RESULTS
