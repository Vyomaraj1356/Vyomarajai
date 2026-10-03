# Safe Primary → DR verification and replication

## One configuration authority, no guessed private repository

Primary is `Vyomaraj1356/Vyomarajai:main`. The secondary must be explicitly confirmed in the primary repository's GitHub Actions **variable** `VYOMARAJ_DR_REPO` (`owner/repository`, not a URL). There is deliberately no default: legacy files disagree between several names and all inspected candidates returned 404 to the Arena integration on 3 October 2026.

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

The single workflow is `.github/workflows/vyomaraj-sync-both.yml`. Feature pushes and PRs run offline tests only. Manual `mode=verify` supports a `diagnostic_target` for read-only checks. No untrusted input is interpolated directly into shell code.

For actual replication, an authorized maintainer must:

1. Review and merge the repair PR into primary main. Changes on the Arena branch do not repair the currently deployed main workflow.
2. Confirm the intended secondary exists, already has a `main` ref, and is a dedicated snapshot mirror. Review target-only files: an exact snapshot removes them from the new tree, while preserving prior DR commit history.
3. Set `VYOMARAJ_DR_REPO` to that confirmed destination. Configure `VYOMARAJ_PAT` securely with the necessary repository permissions (including workflow-file permissions if the mirrored tree requires them); ensure branch protections allow the approved update.
4. Complete a read-only verification first. `diagnostic_target` is never accepted for writes.
5. Set repository variable `VYOMARAJ_DR_SYNC_ENABLED=true` only when mirror writes are approved. With this value, primary-main pushes and the 30-minute schedule may replicate; manual `mode=sync` is also gated on this value and primary main. A manual default `mode=verify` stays read-only.
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

Identity access is not repository access; repository read access is not verified write permission or exact-tree DR equality. A local gh diagnostic does not test the Actions PAT. Workflow preflight runs before compare/sync and preserves redacted evidence on a failed check. Current evidence remains blocked (secondary 404; Actions-variable access 403); see `DR_FOLLOWUP_2026_10_03.json` and the integrated `/reports/research` report. The linked e69af4d curl formatting change cannot itself repair permissions.
