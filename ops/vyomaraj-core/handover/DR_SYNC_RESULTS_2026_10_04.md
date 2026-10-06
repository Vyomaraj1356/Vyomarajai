# Vyomaraj — DR sync results — 2026-10-04

**Generated file — do not edit by hand.** Rebuild with `python3 ops/vyomaraj-core/handover/build_dr_sync_report.py` from the repository root; `--check` verifies this checked-in copy still matches its evidence.

## 1. Scope — what this record does and does not assert

Primary repository: `Vyomaraj1356/Vyomarajai`. Secondary repository: `deepakGoyal1356/Vyomaraj-Agent-6d64e`.
Main tip covered by this record: `d97122fc340febc587e5c6020e8d1c53d02b4388`.
Workflow: `.github/workflows/vyomaraj-sync-both.yml` — triggers: push, pull_request, workflow_dispatch, schedule; schedule: `*/30 * * * *` (UTC).
Recorded scope: Git main tracked-file snapshot verified by the primary repository Actions workflow; not runtime/site DR.

This is a Git-snapshot replication record. It is **not** a production disaster-recovery approval and it says nothing about runtime databases, live media sessions, provider accounts, secrets or production traffic.

## 2. Evidence sources (all checked in)

| Source | SHA256 | What it contributes |
|---|---|---|
| `ops/dr/DEPLOYED_MATCH_2026_10_04.json` | `a68251a5a0bd035a1eb829e9ece7184dac2c65ea30fb84aef0d2cbc00683faa8` | 32 MATCH checkpoints, 22 replication writes, 1 blocked run, 1 read-only probe |
| `ops/dr/DR_POLICY.json` | `6090042dc9e05fa1273ba0f0345a6821d633e28c755cac6be806712e7ee222df` | scope flags and the time-boxed one-snapshot removal approval |
| `.github/workflows/vyomaraj-sync-both.yml` | `299ff016ebd02919252a56de396c60b63b0c2246f74190923b24eb8216206681` | triggers and schedule |

Method: All successful verify-or-sync check-runs on the main tip were enumerated and their public annotations parsed. A run that replicated carries rollback_commit; an idempotent no-op does not.

Re-validation: All 29 previously recorded annotations re-read live from the GitHub API in one pass (zero mismatches), plus the 3 new verify-or-sync annotations for the PR #33 merge, the PR #34 merge and the following schedule reconciliation. Every annotation tree was cross-checked against git rev-parse of its head SHA in the local clone; the PR #33 merge commit e9bfba0 is not in the shallow clone and was fetched by SHA first, then its tree matched the annotation. The rollback commit of checkpoint #31 lives in the private secondary and is not readable by this credential; that failed read and the bounded public interval are recorded in the row instead of a guessed timestamp. Result: 32 MATCH checkpoints (22 replication writes) through the PR #34 merge and the schedule confirmation on its tip; window B completed and closed by checkpoint #21; window C (PR #29 tip) recorded as a gap; the stale-head race write is documented but not double-counted.

## 3. Verification checkpoints (32)

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
| 14 | 2026-10-04T07:18:10Z | `a47f76602b26` | #19 | `37185319991` | `111385960390` | MATCH | `91597533650f` | `91597533650f` | yes (`0216f1a8e93c`) |
| 15 | 2026-10-04T07:20:56Z | `686c8e0b1c1a` | #20 | `37185458807` | `111386365434` | MATCH | `7fb902cc997d` | `7fb902cc997d` | yes (`f2bfd8a581a3`) |
| 16 | 2026-10-04T08:20:20Z | `ad99c2eaf896` | #21 | `37188502423` | `111395579579` | MATCH | `9b95c7e8465d` | `9b95c7e8465d` | yes (`a3e4e6309e91`) |
| 17 | 2026-10-04T08:26:11Z | `feb720681514` | #22 | `37188867431` | `111396668243` | MATCH | `99c42eb64224` | `99c42eb64224` | yes (`96537d32b58b`) |
| 18 | 2026-10-04T08:30:31Z | `767f87986044` | #23 | `37189095334` | `111397396312` | MATCH | `5d1787acac6f` | `5d1787acac6f` | yes (`096c2ec6e0dc`) |
| 19 | 2026-10-04T09:17:04Z | `d9147fffc588` | #24 | `37191596397` | `111404791435` | MATCH | `e8c66bd45148` | `e8c66bd45148` | yes (`be715362ca39`) |
| 20 | 2026-10-04T11:26:52Z | `0671fc590a87` | #25 | `37198689808` | `111425773341` | MATCH | `88f681aae844` | `88f681aae844` | yes (`307d0383e2b4`) |
| 21 | 2026-10-06T10:31:15Z | `d6f10dde04b4` | #28 | `37450204853` | `112224787168` | MATCH | `aa19889fb375` | `aa19889fb375` | yes (`c0edf483cd78`) |
| 22 | 2026-10-06T10:43:59Z | `d6f10dde04b4` | #28 | `37451637449` | `112229472156` | MATCH | `aa19889fb375` | `aa19889fb375` | no |
| 23 | 2026-10-06T11:11:30Z | `d6f10dde04b4` | #28 | `37454689059` | `112239413563` | MATCH | `aa19889fb375` | `aa19889fb375` | no |
| 24 | 2026-10-06T11:35:40Z | `cbc402fe4e5c` | #27 | `37457034872` | `112247203850` | MATCH | `ec594b22fb49` | `ec594b22fb49` | yes (`6eef7c79bc7b`) |
| 25 | 2026-10-06T11:43:11Z | `cbc402fe4e5c` | #27 | `37458191303` | `112251025871` | MATCH | `ec594b22fb49` | `ec594b22fb49` | no |
| 26 | 2026-10-06T11:46:13Z | `ed21fe71c6b6` | #30 | `37458392452` | `112251697240` | MATCH | `0f4a78550c66` | `0f4a78550c66` | yes (`6d4335caf932`) |
| 27 | 2026-10-06T11:50:21Z | `d46d8b3705a7` | #31 | `37458973059` | `112253587690` | MATCH | `bb8632f62eb9` | `bb8632f62eb9` | yes (`42c401d27070`) |
| 28 | 2026-10-06T12:13:39Z | `d46d8b3705a7` | #31 | `37461681369` | `112262665018` | MATCH | `bb8632f62eb9` | `bb8632f62eb9` | no |
| 29 | 2026-10-06T12:43:24Z | `1c13650ce19e` | #32 | `37465147285` | `112274342282` | MATCH | `c2f20ec8ad7e` | `c2f20ec8ad7e` | yes (`8af782dbe364`) |
| 30 | 2026-10-06T12:49:55Z | `e9bfba0efd36` | #33 | `37465870496` | `112277370308` | MATCH | `e7b65c5952a3` | `e7b65c5952a3` | no |
| 31 | 2026-10-06T12:54:50Z | `d97122fc340f` | #34 | `37466613010` | `112279322282` | MATCH | `70b69f8e0331` | `70b69f8e0331` | yes (`490880630a5a`) |
| 32 | 2026-10-06T13:13:06Z | `d97122fc340f` | #34 | `37468965584` | `112287316035` | MATCH | `70b69f8e0331` | `70b69f8e0331` | no |

All 32 rows were re-read from the GitHub API at 2026-10-06T13:40:38Z and matched the values stored in the record.

## 4. Replication writes (22)

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
| `a47f76602b26` | #19 | `37185319991` | `111385960390` | `0216f1a8e93c0e67a92899348230a0cb9a23d684` |
| `686c8e0b1c1a` | #20 | `37185458807` | `111386365434` | `f2bfd8a581a3064d87a16dc67e7db22c2e8a219a` |
| `ad99c2eaf896` | #21 | `37188502423` | `111395579579` | `a3e4e6309e919f1fbfa6afacba401be59eb64ad5` |
| `feb720681514` | #22 | `37188867431` | `111396668243` | `96537d32b58bc2221608d42a1fba5af9abad02b6` |
| `767f87986044` | #23 | `37189095334` | `111397396312` | `096c2ec6e0dc05762af0c2d22a03507839a22bc6` |
| `d9147fffc588` | #24 | `37191596397` | `111404791435` | `be715362ca394464844e5058745fb10914e40a1e` |
| `0671fc590a87` | #25 | `37198689808` | `111425773341` | `307d0383e2b46c064332e35025e25d97614c709d` |
| `d6f10dde04b4` | #28 | `37450204853` | `112224787168` | `c0edf483cd786b63a149c987bce370ab81404897` |
| `cbc402fe4e5c` | #27 | `37457034872` | `112247203850` | `6eef7c79bc7bb1f159d6501b43867f030e556396` |
| `ed21fe71c6b6` | #30 | `37458392452` | `112251697240` | `6d4335caf932381f8edcba2181d39433b19a1481` |
| `d46d8b3705a7` | #31 | `37458973059` | `112253587690` | `42c401d27070c037b3f3782735af0d144fe4465e` |
| `1c13650ce19e` | #32 | `37465147285` | `112274342282` | `8af782dbe364a5c8bd4528bbc5e761bca69c391a` |
| `d97122fc340f` | #34 | `37466613010` | `112279322282` | `490880630a5a73e895982814da8d4f9a886bc493` |

A write replaces the secondary snapshot with the primary snapshot and keeps the previous secondary commit as the rollback parent; no force-push and no history deletion is used.

## 5. The correctly blocked run (1) and its approved resolution

Rollback-commit timestamps that could not be read (recorded as failed reads, never as guessed values):

- check-run `112279322282`: value_utc = null.
  - Attempt: Requested for this record; GET /repos/deepakGoyal1356/Vyomaraj-Agent-6d64e/commits/490880630a5a73e895982814da8d4f9a886bc493 through the Arena credential on 2026-10-06 returns 404: the private secondary is not readable by this integration (the documented issue #6 limitation). The same SHA is not a commit in the primary (API 422).
  - Bounded substitute: The public workflow evidence for the run that created it: run 37466613010, verify-or-sync job/check-run 112279322282, step 'Verify or replicate exact main snapshot' ran 2026-10-06T12:54:21Z-12:54:47Z; rollback_commit is the previous secondary tip retained by that write and its committer timestamp lies inside that step interval.
  - Standing: No timestamp is asserted; the field records the failed read and the bounded public interval.


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

## 5b. Publication status of this record

Recorded by session: `arena/01a10655-vyomarajai (current recovery session)`.
Session branch base: `d9147fffc5884702d7fcbc38fd666d62622f3b8c (PR #24 merge; checkpoint #19)`.
Pushed to origin at record time: no.
Published as: pending at record time: the V16.9 auto-align and issue-ledger reconstruction is local on arena/01a10655-vyomarajai; no push or PR has been made by this update.
Coverage: the comics lane, the V16.8 architecture and the governance desks remain part of the replicated snapshot verified by checkpoints #16-#18 — they were published by the third session and nothing of them is lost.
Publish path: review changes on arena/01a10655-vyomarajai → push only this branch → pull request → merge to main after owner review → read the verify-or-sync checkpoint; do not merge automatically.
DR coverage of the merge that carries this record: PR #24 is covered by checkpoint #19; a later merge carrying this record will create its own verify-or-sync checkpoint.
Local sync possible from the recording sandbox: no.

Rebuilt from lost local commits: two earlier Arena sandboxes: the second session's local commits 2430a16 (comics lane) and ac2f741 (status + sharing) were rebuilt by the third session; the third session's local commits (theme upgrade + viewer update, reported head 4a5a6d9) never reached GitHub and are rebuilt by this session. Verified live: the remote branch tip is 13f083215306ae7f9cf2c32189f0eb2999ced74c (fully merged via PR #23) and no commit 4a5a6d9 exists in the repository. The reported V16.9 local commits 68baff5/c405eaa and their transfer artifacts were not available in this fresh clone or on advertised GitHub refs; the current session reconstructed the documented plan and ledger from the supplied handover text, not from original patch bytes.
Rebuilt in this merge:

- rebuilt: the third session's unpublished viewer work (theme upgrade, inheritance audit, three reference pages) as a documented re-implementation, not byte-identical to the lost commits
- preserved: the comics lane, the V16.8 architecture and the governance desks merged via PR #21 (checkpoint #16)
- reconstructed from the supplied handover: a 21-step, five-phase auto-align plan with 41 completion paths and a bounded local runner; not byte-identical to the reported unpublished patch
- reconstructed from the supplied handover: a 14-entry issue/PR ledger and prepared issue #6 close-out; no comment or close action performed

## 5c. The trailing-checkpoint rule (why the newest merge is not a row yet)

This record closes at the last checkpoint that was re-read live as a complete set. The merge that
publishes this very record is verified by the same workflow immediately after it lands; that
checkpoint is recorded in the next update and is visible live meanwhile:

```
gh api repos/Vyomaraj1356/Vyomarajai/commits/main/check-runs --jq '.check_runs[] | select(.name=="verify-or-sync") | [.id, .conclusion] | @tsv'
gh api repos/Vyomaraj1356/Vyomarajai/check-runs/<check_run_id>/annotations --jq '.[] | select(.title=="DR SNAPSHOT RESULT") | .message'
```

A checkpoint that is not yet a row here is not an unverified merge; it is a row waiting for the
next full-set re-read. No merge is ever silently skipped.

## 5d. Local verification attempt in the recording session

- Command: `python3 ops/dr/dr_sync.py --target deepakGoyal1356/Vyomaraj-Agent-6d64e`
- Result: **BLOCKED (HTTP 404 hidden by permissions)** (checked 2026-10-04T08:07:38Z)
- Explanation: Re-attempted by the recording session (arena/01a105da-vyomarajai) with the same result: the Arena GitHub integration credential cannot see the private secondary; this is the documented reason the workflow uses a separate Actions credential (VYOMARAJ_PAT). A 404 does not imply the secondary is missing, and no write was attempted.

This is why the record is built from the workflow's own public annotations: the Actions credential is the
authorized reader/writer for the private secondary, and a sandbox 404 is not evidence about the secondary.

## 5e. Windows in which verify-or-sync did not execute (3)

A window is a period in which the workflow ran but the verify-or-sync job never executed, so
**no** checkpoint exists for it — no match, no mismatch and no write was observed. Windows are
recorded here rather than in section 3 precisely because they are not checkpoints: counting them
as matches would overstate coverage, and counting them as mismatches would overstate damage.

### 1. 2026-10-05 19:13Z - 21:25Z (scheduled)

- Head SHA at the time: `0671fc590a8778e5984f89ca66eb65e38d6ec734`
- Runs involved: `37361831782`, `37365244096`, `37368125663`, `37371579909`, `37374236163`
- Observation: Five consecutive scheduled runs concluded failure with the offline-tests job CANCELLED - not failed on a test - after running for 15m02s each; verify-or-sync was skipped in all five, so no checkpoint was produced.
- Cause recorded: Platform-side cancellation: the job was stopped after a uniform 15m02s with no test output, and the same commit's next scheduled run at 21:43Z completed the identical suite in 21 seconds. No repository defect is claimed or ruled out beyond that evidence.
- Effect: The already-verified snapshot for 0671fc59 stayed in place; the secondary was not touched and no drift was created by the window itself.
- Resumed by: run `37377733744`

### 2. 2026-10-06 05:29Z - 10:31Z (push, scheduled, and two pull-request runs) - closed by checkpoint #21

- Head SHA at the time: `f735f92b00be903384c18fdcfa2a7a264ba3e09a`
- Runs involved: `37418230309`, `37418814411`, `37418836991`, `37419872626`, `37422569870`, `37425864571`, `37428197083`, `37431461993`, `37434510525`, `37438051850`, `37441262759`, `37444957085`, `37448075653`
- Observation: Thirteen runs concluded failure; the offline-tests job failed in each, so verify-or-sync never executed (11 skipped check-runs on the main tip f735f92, completed 05:30-10:11Z, plus two pull-request runs on branch heads b636964 and 4935ec8). The main tip f735f92 (tree 4064ba289bd5...) has no verify-or-sync checkpoint.
- Cause recorded: Repository defect introduced by commits 4935ec8d and f735f92: the transfer-package archive and TRANSFER_MANIFEST were restored from an older tree while their five member sources stayed current, so test_transfer_package failed and build_transfer_package.py --check reported five members differing from source.
- Effect: The secondary snapshot remains at the PR #25 snapshot 0671fc59 (tree 88f681aae844...); the two commits after it (4935ec8d, f735f92) were never replicated. This is a real Git-snapshot replication gap, closed only by a successful verify-or-sync run on the fixed main tip. Closed by checkpoint #21 (run 37450204853, 2026-10-06T10:31:15Z), which replicated the PR #28 tree aa19889f with rollback c0edf483 retained.
- Resumed by: run `run 37450204853 (checkpoint #21, 2026-10-06T10:31:15Z)`

### 3. 2026-10-06 11:17Z - tip superseded unverified (single push run)

- Head SHA at the time: `95b21335ad1035c223c4f930dfa15885ebd4b56b`
- Runs involved: `37455387004`
- Observation: One push run concluded failure; the offline-tests job failed after 18s, so verify-or-sync was skipped (check-run 112241732986) and the PR #29 squash tip 95b2133 (tree b457b3d1...) has no verify-or-sync checkpoint. Exactly one verify-or-sync check-run exists for this tip, so no schedule or dispatch run covered it before PR #27 merged.
- Cause recorded: CI annotations on offline-tests check-run 112241605747: build_configuration_report.py --check failed (BUILD_AND_CONFIGURATION_2026_10_04.md out of date) plus a handover-suite failure; 2 failures in that run.
- Effect: The secondary snapshot moved from the PR #28 tree (aa19889f...) directly to the PR #27 tree (ec594b22...) on checkpoint #24. Exact-snapshot replication does not need the intermediate tip, but no observation proves what the secondary held at the #29 tip.
- Resumed by: run `run 37457034872 (checkpoint #24, 2026-10-06T11:35:40Z) - next verified write after the gap`

## 5f. Record extension by `arena/582559e8-vyomarajai` (2026-10-06)

- Finding: The tip published on 2026-10-06 (f735f92, 'Vyomaraj sovereign restore') had no successful verify-or-sync run: the offline gate failed first, so replication never ran and the failure was silent in the DR record until this re-read.
- Fix: The transfer package and its manifest were rebuilt from the current sources with their own builder (package sha256 8125959942d3d293f4971d3f52f46a9047868a3b5f113ee6d2b80efee2240a67, 133941 bytes - byte-identical to the package that PR #25 recorded in PREVIEW_VERIFICATION), and the workflow no longer pins a single expired session branch, so the offline gate and the read-only PAT diagnostic run on every Arena session branch.
- Next checkpoint: The merge of the fix on main is verified by the same workflow immediately after it lands; that run becomes checkpoint #21 and closes the 2026-10-06 window.

### Read-only confirmation of the open window

- Source: Read-only Actions credential probe (ops/dr/actions_read_probe.py), run 37421416568 job diagnose-existing-pat on commit d2bf6d631b73, annotation read live from check-run 112131576824
- Public annotation: `read_access=READ_ACCESS_CONFIRMED; identity=READABLE; primary_repository=READABLE; primary_main=READABLE; secondary_repository=READABLE; secondary_main=READABLE; tree=MISMATCH; writes=NONE; write_permission=UNVERIFIED; primary_files=315; secondary_files=315; missing_on_secondary=0; secondary_only=0; changed_content_or_mode=3; secondary_commit=c0edf483cd786b63a149c987bce370ab81404897; secondary_tree=88f681aae8441eb0bf3b176f8222eeb68d5ba602; candidate_files=320; candidate_secondary_only=0; candidate_missing=5; candidate_changed=14`
- What it means: Independently confirms the gap recorded in window B: the secondary really is at tree 88f681aae844 (the PR #25 snapshot) while main has moved on, and the credential can read it. Writes stayed NONE and write permission stays UNVERIFIED - a green diagnostic means readable, not replicated.
- Second defect found by making the diagnostic run again: The probe script itself was pinned to the same expired branch name (GITHUB_REF == 'refs/heads/arena/01a10140-vyomarajai'), so once the workflow was fixed to run the job on any arena/ branch, the script exited 2 with 'restricted to the trusted review-branch push'. The guard is now a prefix rule ('refs/heads/arena/') covered by TrustedPushTests in ops/dr/test_actions_read_probe.py.

## 5g. Record extension by `arena/6bc12929-vyomarajai` (2026-10-06, second pass)

- Finding: The record stopped at PR #25 while main had moved to PR #31; the #26 tip (f735f92) was an open gap (window B, then listing 4 of its 13 runs) and the #29 tip (95b2133) was never verified at all.
- Fix: Re-read every verify-or-sync annotation live: all 20 old rows match byte-for-byte, and 8 new checkpoints (#21-#28, 4 writes) were recorded from the #28/#27/#30/#31 main tips plus schedule confirmations. Every annotation tree was cross-checked against git rev-parse of its head SHA. Window B is completed (13 runs) and closed by checkpoint #21; window C documents the #29 tip as a gap.
- Recording rule: One checkpoint row per distinct new main tip plus the latest schedule confirmation on the final tip; the complete per-tip check-run sets were enumerated with per_page=100, so no successful verify-or-sync run on these tips is missing.
- Next checkpoint: The merge carrying this extension is verified by the same workflow immediately after it lands; that run becomes checkpoint #29 per the trailing rule (section 5c).

- Fulfilled by: run 37465147285 (checkpoint #29, 2026-10-06T12:43:24Z): the PR #32 merge verified write + MATCH, trees c2f20ec8, rollback 8af782db retained.

## 5h. Record extension by `arena/05152d2a-vyomarajai` (2026-10-06, third pass)

- Finding: The record stopped at checkpoint #29 (PR #32 tip). The PR #33 and PR #34 merges were verified live (no-op MATCH and write + MATCH) and the final tip also received a schedule confirmation; none of the three was recorded.
- Fix: The three live annotations were parsed (not transcribed) into rows #30-#32, the write list and both totals were recomputed from the rows, and the trailing-checkpoint rule of section 5c now closes at the final tip.
- Stale-head race: Checkpoint #30 remains a deliberate no-op row: the write for its tree came from schedule run 37465859915, filed under the older head 1c13650. Attribution follows annotation trees, per stale_head_race_note_2026_10_06, so the write is not double-counted.
- Rollback timestamp attempt: GET of the checkpoint #31 rollback commit 49088063 against the private secondary returned 404 through the Arena credential and 422 against the primary. Recorded as a failed read with the public step interval 12:54:21Z-12:54:47Z as the bounded substitute; this is the same owner-side access limitation tracked by issue #6.
- Next checkpoint: The merge carrying this extension is verified by the same workflow immediately after it lands; that run becomes checkpoint #33 and is recorded in the next update.

## 5i. Stale-head race between a schedule run and a merge (2026-10-06)

- Phenomenon: Schedule runs pin head_sha at creation but read LIVE main via the API at execution. If a merge lands in between, the run verifies (and may replicate) a NEWER snapshot than its head_sha, and its check-run files under the stale head. Attribute replication writes by ANNOTATION TREES, not by head_sha filing.
- Observed instance: schedule run `37465859915` (head `1c13650ce19e`, check-run `112276811314`, completed 2026-10-06T12:49:03Z) verified and wrote the `e7b65c5952a3` tree; the push run `37465870496` on head `e9bfba0efd36` (check-run `112277370308`, completed 2026-10-06T12:49:55Z) then found the snapshots already equal.
- Rule for future reads: When a verify-or-sync annotation trees do not match git rev-parse of its head SHA, list sibling workflow runs before flagging a mismatch: a schedule/push race is the expected cause. The push run filed under the new tip remains the canonical checkpoint row for that tip.
- Checkpoint #30 guidance: Record push-run check 112277370308 (no-op MATCH, trees e7b65c59) as the row for tip e9bfba0 with replication_write_in_this_run=false, and note the snapshot write was performed minutes earlier by schedule run 37465859915 (filed under 1c13650, rollback b6656066 retained).
- Fulfilled by: checkpoint #30 (check-run 112277370308, 2026-10-06T12:49:55Z): recorded as the canonical no-op row for tip e9bfba0 with the schedule write attributed to run 37465859915 in its row note.

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
