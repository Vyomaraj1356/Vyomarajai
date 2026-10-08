# Safe Primary → DR verification and replication

> **Current status — 8 October 2026.** **DR verification had stopped running.** `verify-or-sync`
> declares `needs: offline-tests`; `offline-tests` began failing on main at `ae92895`
> (2026-10-07 15:53 UTC) and stayed broken through PRs #45–#49, so the comparison job was
> **skipped** 37 consecutive times and nothing compared primary to secondary for about sixteen
> hours. The last run that actually executed is check-run `112880681037`, completed
> `2026-10-07T15:50:01Z` on main `04b7ae60`: `status=MATCH`, `data_match=true`, equal trees
> `986288ee2cc4ec4d89400320150ea893f7a7a2de`, `traffic_switched=NONE`. That remains the most
> recent verified state; **main has since advanced to `5935588` with no DR verification.**
>
> Root cause: the 7 October consolidation merges overwrote five files that were already the
> source of truth for other code (the Universal Knowledge policy, the Panch-Brother capability
> model, `capability_fabric.py`, `verify_2026_stack.py`, and three deny-by-default gate scripts),
> and introduced a literal `\${BASH_SOURCE[0]}` defect that made several gates pass without
> checking anything. Those files are restored, the superseded content is preserved additively,
> and the offline suite is back to 61/61. Full account:
> [DR_SYNC_AND_PACKAGE_PARITY_2026_10_08.md](DR_SYNC_AND_PACKAGE_PARITY_2026_10_08.md).
>
> Package parity is now part of every DR run — see `package_parity.py` below. From Arena the
> read-only DR test still returns `BLOCKED` / HTTP 404 on the secondary, as it has throughout;
> that is a credential scope limit, not proof of absence. No sync was performed, and issue #6
> remains OPEN/P0.

## Package parity — "the same packages"

`ops/dr/package_parity.py` confirms primary and secondary carry the same packages in both
senses: dependency manifests (`requirements*.txt`, `package.json`, lockfiles…) and
distributable packages (`*.zip`, `*.apk`, `*.tar.gz`). It records each file's size, SHA-256
and Git blob SHA, so a tree entry is compared without downloading a 24 MB artifact.

```sh
python3 ops/dr/package_parity.py                 # inventory + declaration report
python3 ops/dr/package_parity.py --check         # offline: committed inventory still current
python3 ops/dr/package_parity.py --index         # network: every locked pin exists on PyPI
DR_REPO=confirmed-owner/repo python3 ops/dr/package_parity.py --remote
```

`--check` runs in the offline suite; `--remote` runs in `verify-or-sync` for both verify and
sync modes. A package `MISMATCH` or an inconsistent declaration fails the job; an access
failure is recorded as a warning and never reported as parity. None of this inspects an
installed environment: `installed_environment_verified` is always `false`.

> **Earlier status override — full access audit captured 7 October 2026 08:28 UTC; issue/PR/main/Pages metadata re-read at 10:06 UTC; latest scheduled DR annotation separately re-read.** Issue #6 remains OPEN/P0; do not post its historical close-out or close it. The latest successful scheduled workflow run `37605789908` / check-run `112741170924` completed at `10:13:11Z` on main `04b7ae60` and reported `MATCH`, `data_match=true`, equal primary/secondary tracked Git trees `986288ee2cc4ec4d89400320150ea893f7a7a2de`, `traffic_switched=NONE`, and annotation `http=UNAVAILABLE`; it was a no-write confirmation. This is a point-in-time tracked Git-tree match only, not deployed-app/runtime equality, service availability, authenticated heartbeat, failover, RPO or RTO. The matched tree includes the tracked APK blob `9c95df15c8cb1787bf85b7d44f9445ff9376f1f2` (24,567,022 bytes); signature validity, signer provenance and real-device installation remain unverified. Two earlier main-push runs performed automatic snapshot writes, recorded in the DR report; this session did not dispatch or initiate them. The later addendum checked only the new annotation; the previous 40 were not re-read. The earlier full annotation audit remains preserved separately. The 08:28 access audit found candidate secondary paths returning 404 and Actions variables/secrets returning 403; these do not negate the Actions evidence, but owner-confirmed target identity/access and target-only-data review remain open. PR #41 is OPEN/non-draft and based on `8e9a67a`, two commits behind current main; PRs #39/#42 are OPEN/DRAFT, and #39 was left untouched. Pages is built from `main:/` at `04b7ae60`; this working branch is not deployed. Existing gateway/report/lane preview ports were closed at the 08:22 UTC probe; a separate allowlisted sandbox web preview is not production. This status block supersedes older present-tense wording below.

## Historical MATCH checkpoint — 3 October 2026 (not current DR evidence)

PR #5 merged at `3793020`; main sync `37126108656` and scheduled repeat `37126121716` succeeded with tree `e69e5c90f2ddec237a307b45830cff712649ed92` on both repositories (244 tracked files at that checkpoint). Rollback parent: `7107980ce0bb1fc788da9e1f7a87f3d6cd9bf1d3`. Evidence: `DEPLOYED_MATCH_2026_10_03.json`; report `/reports/resilience`. The one-snapshot approval is consumed/disabled; future target-only removal remains guarded. This is not runtime/site DR or a permanent live-HEAD guarantee. Earlier pending statements below are historical.

## Historical mismatch snapshot — 3 October 2026 (superseded as current status): 125 primary files + 149 secondary-only files

At that historical snapshot, Actions probe run `37125323786` succeeded using the existing Actions credential. Primary main had 125 files, secondary 274; missing 0, changed shared content/mode 0, secondary-only 149. `ACTIONS_PROBE_EVIDENCE_2026_10_03.json` retains the sanitized check-run annotation. This records the then-current tree mismatch and demonstrates that Actions read access worked, separately from Arena's restricted credential.

Old main overlays entries onto `base_tree` and checks equality only after publishing. The replacement uses no base tree and verifies before ref publication. **New safety gate:** `DR_ALLOW_TARGET_ONLY_REMOVAL` must be literal `true` before any target-only removal; workflow input `allow_target_only_removal` defaults false and is only explicitly approved in manual dispatch. Main still owns writes; the guard is checked before blob/tree/commit writes. Review and independently back up extra files first. Counts are recalculated and may change after main receives PR #5.

The trusted same-repository review-branch **push** now runs a separate GET-only Actions probe, after offline tests. It never runs on pull requests/forks, never copies blobs and never changes refs. Green probe = readable, not synchronized or write-authorized. The main-only verify/sync guard is unchanged. `DR SNAPSHOT RESULT` annotations now expose only closed-vocabulary result, failed API operation, HTTP status and removal-review count, never raw provider bodies or credentials.

At that 3 October snapshot, PR #5 was the deployment gate. Do not treat that old gate/status as current: the 7 October scheduled run now provides a same-tree Git snapshot match, but issue #6 remains OPEN/P0 because its owner-confirmed target/access and target-only-data acceptance is still incomplete. Never claim production success without owner-authorized target review and independent readback. The previous failed-log download returned EOF, so the historical exception remains unfilled. Viewer report: `/reports/resilience`.


## One configuration authority, no guessed private repository

Primary is `Vyomaraj1356/Vyomarajai:main`. In the deployed workflow, the Actions variable `VYOMARAJ_DR_REPO` (`owner/repository`, not a URL) overrides the reviewed in-repository fallback `DR_POLICY.json` value `deepakGoyal1356/Vyomaraj-Agent-6d64e`. The Arena credential receives 403 for the Actions settings endpoints, so we cannot tell whether a variable override is set; the public workflow annotations prove only that the workflow's selected target was reachable for the recorded comparisons/writes, not which repository name it selected. Candidate-path 404s are ambiguous. The owner/admin must still confirm the intended authoritative target and review current target-only data before issue #6 can close.

A private repository 404 is ambiguous: wrong name, renamed/deleted repository, or lack of access. Reconnect GitHub in Arena with the intended repositories selected. Separately review the existing Actions secret `VYOMARAJ_PAT` with an authorized repository administrator. Arena's GitHub integration and an Actions PAT are different credentials; fixing one does not prove the other works. Never send token values in chat.

## Read-only test

```sh
DR_REPO=confirmed-owner/confirmed-repository bash ops/dr/run-dr.sh test
```

This reads repository identity, main refs and commit trees through `gh` (GET only) or supplied process credentials. It **does not source legacy dr.env**, print private values, run controllers, switch traffic or write repository refs.

- `MATCH` / exit 0: the two observed Git trees match and the refs remained stable during verification. Commit SHAs may differ for snapshot mirrors.
- `MISMATCH` / exit 1: readable repos, different trees; not success.
- `BLOCKED` / exit 2: missing target, authentication/permissions, missing ref or invalid data. A 404 never creates a repository or initial branch.

This is a repository-integrity test, not a running-application, backup-restore, RPO/RTO or disaster-failover drill.

## Controlled replication after review/merge

The single workflow is `.github/workflows/vyomaraj-sync-both.yml`. Feature pushes and PRs run offline tests only. Main pushes and the schedule are verification-only; a snapshot write now requires an explicit `workflow_dispatch` with `mode=sync`, a confirmed target, and `VYOMARAJ_DR_SYNC_ENABLED=true`. Manual `mode=verify` supports a `diagnostic_target` for read-only checks. No untrusted input is interpolated directly into shell code.

The checked-in policy sets `sync_approved_on_main=false` while issue #6 remains OPEN/P0. This branch change prevents an ordinary web-release merge or scheduled run from silently writing to an unconfirmed secondary. It does not confirm the target, close issue #6, or perform a sync.

For actual replication, an authorized maintainer must:

1. Review and merge the repair PR into primary main. Changes on the Arena branch do not repair the currently deployed main workflow.
2. Confirm the intended secondary exists, already has a `main` ref, and is a dedicated snapshot mirror. Review target-only files: an exact snapshot removes them from the new tree, while preserving prior DR commit history.
3. Set `VYOMARAJ_DR_REPO` to that confirmed destination. Configure `VYOMARAJ_PAT` securely with the necessary repository permissions (including workflow-file permissions if the mirrored tree requires them); ensure branch protections allow the approved update.
4. Complete a read-only verification first. `diagnostic_target` is never accepted for writes.
5. Keep repository variable `VYOMARAJ_DR_SYNC_ENABLED=false` until the owner/admin resolves issue #6 and approves the reviewed target/data diff. Main pushes and the 30-minute schedule remain read-only regardless of the variable. Only then may an authorized maintainer use explicit workflow dispatch with `mode=sync`; the confirmed target, approval variable and primary-main guard are all required.
6. Verify the uploaded sanitized evidence artifact and independently compare tree SHAs. A green job is not application failover readiness.

Replication validates complete source trees and blob hashes, refuses unsupported submodules, creates an exact new tree **without base_tree** (so source deletions are reflected), checks tree equality **before** publication, preserves the existing target commit as parent, rechecks both refs and uses `force:false`. It is idempotent when trees match. Source/target movement causes a failure rather than a stale success; a target force-reset to an ancestor is outside the ordinary non-force concurrency assumption. Protect both branches against force updates. GitHub offers no cross-repository atomic transaction, so a source advance after publication can require the next approved run.

Remote failures can leave unreachable Git objects created before publication; no success is claimed and no rollback force-update is attempted. API rate limits/large archives may block a full snapshot. No automatic initial target creation, reverse sync or traffic switching is implemented.

## Legacy files

Tracked `dr.env`, examples, old activation reports and `failover-controller.sh` remain historical inputs; their target names/status/zero-loss claims are not authoritative. `run-dr.sh` no longer sources them. Failover/failback through that entry point are blocked pending a separately reviewed production runbook. Do not invoke the old controller directly as an unattended service without reviewing endpoints, fencing, authorization, rollback and secret handling.

The two duplicate verification/readiness workflows have been removed on the repair branch; their useful syntax/verification checks are consolidated in the single workflow. The former readiness job printed environment content; no replacement does that.

## Offline tests

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s ops/dr -p 'test_*.py' -v
```

No external requests, tokens or production writes are used by these tests.

## PAT identity diagnostic follow-up (3 October 2026)

`python ops/dr/dr_diagnostics.py --output dr-diagnostic-evidence.json` performs GET-only identity/repository/main-ref checks using the same explicit process-token or local read-only `gh` client. `DR_REPO` must be a confirmed owner/repository for normal use; no target is guessed. Missing/malformed target returns a redacted blocked result. GET `/user` is narrowly allowed; user writes and arbitrary external URLs are not. No identity response body, login, token or scopes are logged.

Identity access is not repository access; repository read access is not verified write permission or exact-tree DR equality. A local gh diagnostic does not test the Actions PAT. Workflow preflight runs before compare/sync and preserves redacted evidence on a failed check. **Historical 3 October diagnostic status** was blocked (secondary 404; Actions-variable access 403); current 7 October scheduled tree-match evidence is recorded in `DEPLOYED_MATCH_2026_10_04.json` and `../vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md`. The Arena connection still cannot independently establish the exact override/target. The linked e69af4d curl formatting change cannot itself repair permissions.

## Historical technical follow-up — 3 October 2026: corrected target, authenticated Actions, failed replication

Primary `main` advanced independently to `9be6d3950cb65dcdd5dba36e548f48c599361d57`. Its preceding commit corrects the actual secondary to `deepakGoyal1356/Vyomaraj-Agent-6d64e`; the next fixes the verification workflow's target. Main run **37123060948 passed Authenticate DR but failed Replicate PRIMARY main to DR main**. Integrity reporting was skipped. Full failed-log retrieval was unavailable; exit-code annotation alone does not establish the exact cause. This supersedes earlier blanket statements that the Actions PAT could not authenticate.

Arena's separate GitHub connection still returns secondary 404 and Actions settings/secret-name metadata/dispatch 403, even though primary repository metadata reports admin/push capabilities. Repository role flags do not grant absent token endpoint permissions. No PAT value was retrieved or requested.

`DR_POLICY.json` records the target proven by those main commits and the owner-requested single-writer backup policy. The consolidated workflow uses reviewed file defaults when repository variables are unset; explicit `VYOMARAJ_DR_REPO` / `VYOMARAJ_DR_SYNC_ENABLED` values still override them. This removes the need to *write variables through Arena* just to select the already-confirmed target. It does **not** grant API access, repair a PAT, or activate review-branch code on main. Default primary→secondary sync is approved in that policy based on the owner's request and the already-operating main workflow; writes still require primary/main, the real Actions PAT and all integrity guards. Set the repository variable to `false` to disable scheduled/push-triggered writes, or keep the default branch change unmerged.

### Exact technical changes

- Keep one workflow; retire the redundant verification workflow rather than run competing target definitions. Preserve the owner's corrected target in policy. Reconcile main's two target changes into this session branch, not onto main.
- Reuse blob SHAs already present in the authenticated target tree, and upload repeated new blob content once. This reduces needless transfer of retained archives.
- Bounded GET retries for transient transport failures / 429 / 502 / 503 / 504; respect numeric Retry-After up to 60 seconds, otherwise stop. Do not retry 401/403 or ambiguous writes.
- Redacted failed API operation classification (e.g. POST:git/blobs), not credential values or raw response bodies.
- Existing exact-tree construction **without base_tree**, source/target race checks, hash checks, non-force publication, no auto-initialization on 404 and final read-after-write comparison remain. The deployed old main workflow's `base_tree` approach can retain target-only files; that is an observed code risk, **not a proven cause of the latest failure**.
- Workflow timeout: 25 minutes. Timeout/failure is not converted to success.
- `dr_live_audit.py`: reproducible GET-only redacted audit of the connection and latest main workflow.
- `recovery_plan.py`: GET-only secondary→primary recovery-review metadata and stable-ref checks. It cannot write a ref. It requires fencing, a known-good snapshot, diff/security review, backups and independent application recovery tests before a separately authorized restore.

### Operator activation / verification

1. Reconnect/reauthorize the Arena GitHub connection for the intended private secondary and required Actions endpoints. Do not paste credentials into chat. A successful Actions PAT read does not make Arena's token interchangeable with it.
2. Review this branch/PR and the in-repository policy; merge through the authorized GitHub process. No main merge was performed by this session. Review-branch CI only proves offline tests, not replication.
3. In GitHub Settings → Secrets and variables → Actions, privately verify the `VYOMARAJ_PAT` secret. The target token needs access to the corrected private repository, Contents read/write and Workflows write if `.github/workflows` files are changed, plus any required organization approval/SSO. A fine-grained token is scoped to its selected owner/repositories; primary reads use the primary `GITHUB_TOKEN` separately. Branch rules can still block writes. Repo metadata read success is not proof of any write permission.
4. Run **verify** first. Both exact repository identities and main refs must be readable. A 404 must not auto-create or erase a branch. Review any tree mismatch. Inspect sanitized diagnostic evidence if blocked.
5. After confirming the intended mirror/diff and policy, run **sync** on primary main. Require `status=MATCH`, `data_match=true`, complete-tree verification and final read-after-write evidence. A job merely starting, authenticating or staying green elsewhere is not proof.
6. Protect independent versioned backups and a known-good recovery checkpoint. A mirror alone also propagates deletions/corruption. Git snapshots do not capture ignored SQLite state, process memory, browser-local media, credentials, settings, protections, issues/releases or every ref/history.
7. Failback is deliberate single-writer recovery, not simultaneous bidirectional overwrites. This tool does not implement automated failback or production traffic switching.

The same-host application rehearsal lives in `../availability/`. It demonstrates process availability only; it is not the private Git mirror or an independent disaster-recovery deployment.

## Owner-authorized deployment, 3 October 2026

The owner explicitly requested merging the correction and obtaining a perfect file match. A real Actions preflight (`37125967048`) pinned secondary commit `7107980ce0bb1fc788da9e1f7a87f3d6cd9bf1d3`, tree `bd628db084433e9cc885fdc6e4c99c6ab2fe44d7`. The then-proposed release had 150 secondary-only paths (including the retired verification workflow), 119 missing paths and 6 changed shared paths. These counts may change as release files are added; the destination approval remains pinned.

`one_snapshot_removal_approval` in DR_POLICY records the owner's confirmation, exact destination and expiry. It only applies inside primary-main Actions, with both destination commit and tree unchanged and before its UTC expiry. Any destination advance invalidates it. It is not a standing approval for future destructive mirroring; the ordinary manual-checkbox gate remains available. The previous secondary commit is retained as parent for rollback—no force push or history deletion. This is not an independent backup or runtime/data DR certification.

Mutating API requests are serialized with a minimum 1.1-second interval to reduce content-generation rate-limit pressure. They are still never automatically replayed. Public annotations include validated tree hashes and rollback commit identifiers, not credentials or file contents.
