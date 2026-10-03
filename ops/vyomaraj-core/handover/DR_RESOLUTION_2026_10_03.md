# GitHub, report-link and DR resolution — 3 October 2026

> **Latest DR / Aghor follow-up:** `/reports/resilience` supersedes earlier live-status statements below. Primary main advanced to `9be6d39`; the corrected secondary ends `6d64e`. Main Actions run `37123060948` passed authentication but failed replication; integrity reporting was skipped. Arena access still differs (404/403). A same-host failover rehearsal is tested separately, not production DR. The newly requested Aghor sub-agent makes the active total 128 (BHAKTI 3); see `/aghor/` and `/reports/aghor`.

## Latest follow-up — discovery integration pass

Read-only preflight: local `gh` identity, primary repository and primary main are readable. The old workflow secondary candidate still returns 404 (missing or hidden); Actions-variable listing still returns 403. This tests the local GitHub connection, **not the Actions PAT secret**. Primary main remains `e69af4d6155aca87eb87f3da5c4c90e1b8b681a1`. Run [37120524834](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/37120524834) is successful only for `offline-tests`; `verify-or-sync` was **skipped**. PR #5 remains open. No secondary write or merge was attempted.

The linked `e69af4d` commit only repairs multiline curl syntax. The review branch uses tested Python diagnostics now: `ops/dr/dr_diagnostics.py` performs GET-only identity, exact repository-name and main-ref checks, reports redacted status codes, refuses guessed/malformed targets and never logs credentials or identity response bodies. `/user` success is not repository authorization; read access is not write permission or verified replication. The workflow saves diagnostic evidence even when preflight blocks. See `/reports/research` for the integrated update and `ops/dr/DR_FOLLOWUP_2026_10_03.json` for the sanitized local result.

## Current result

**Report access fixed locally. Repair code tested. Live Primary → Secondary sync remains BLOCKED by unverified private-repository access. No DR success or traffic failover is claimed.**

The broken `http://03.md` link is not a project report URL. Use the Arena file viewer or the allowlisted report preview. Its root renders the full inventory with readable tables; `/download/inventory.md` downloads the original Markdown. It does not serve the repository root, environment files, device records or `.git`.

## GitHub investigation

- Primary repository is reachable through `gh`: `Vyomaraj1356/Vyomarajai`.
- Observed primary main: `e69af4d6155aca87eb87f3da5c4c90e1b8b681a1`.
- Latest sync run inspected: `37115458618`, https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/37115458618.
- Run result: **failure at Authenticate DR**; replication and final integrity steps **skipped**. This is not a partial sync success.
- Earlier recent sync runs inspected also failed. GitHub Pages build `37110446300` succeeded; Pages API says built from main at `/`. Pages success is not DR success.
- Full run-log retrieval failed with EOF; the exact Actions PAT failure (invalid token versus scope/path/other authentication condition) could not be established from logs.
- Authenticated GET checks returned **404** for all four secondary names actually referenced in the code/history: `deepakGoyal1356/Vyomaraj-Agent`, `deepakGoyal1356/Vyomaraj-Agent-6d64`, `deepakGoyal1356/Vyomaraj-Agent-6d64e`, `deepakGoyal1356/Vyomraj-Agent-6d64`.
- A private-repository 404 can be missing/renamed repository OR insufficient visibility. It does not establish nonexistence and is not a reason to create a replacement or force-overwrite a branch.
- Listing primary Actions variables returned **403 Resource not accessible by integration**. No secret values were requested or retrieved.
- No open GitHub issues were returned by the initial issue-list check. Existing PRs #2/#4 concern security and #3 concerns reconciled preview/recovery; they were not merged or overwritten.

## Fixes prepared on this session branch

1. **Readable report viewer:** safe HTML rendering of the inventory table and sections, with an exact three-report allowlist, downloadable Markdown and no repository-directory serving. HTML input is escaped.
2. **Two broken JavaScript files repaired:** `multi-ai-coordination.js` and `shriyantra-protection.js` now parse and expose explicit metadata-only compatibility interfaces. They do not fabricate LIVE status, random load, session transfer or security protection. Historical valid prototypes were inspected, but their simulated-health/protection claims were not restored.
3. **One DR workflow:** consolidate tests/verification/approved replication in `vyomaraj-sync-both.yml`; remove duplicate readiness/verification workflows that disagreed on targets, including the one printing environment contents.
4. **No guessed target:** require the approved Actions variable `VYOMARAJ_DR_REPO`; explicit `VYOMARAJ_DR_SYNC_ENABLED=true` is required for writes. A read-only diagnostic target cannot be used to select a write destination.
5. **Read-only local DR test:** new `ops/dr/dr_sync.py`; `run-dr.sh` no longer sources legacy `dr.env`, silently selects a secondary or runs a production failover. Production traffic-changing commands are blocked through this entry point.
6. **Replication integrity:** complete source-tree validation; blob-hash checks; preserve executable/symlink modes; refuse submodules/truncated trees; exact snapshot without retaining stale target-only files; validate new tree before ref update; retain old target commit as parent; non-force publication; stable-ref and read-after-write checks. No initial branch creation on a 404.
7. **Documentation:** explicit unconfirmed-secondary repository map, safe runbook, inventory follow-up notice and corrected README instructions.

## Tests actually performed

- **20 offline DR tests passed:** read-only behavior, branch/repository/approval gates, ambiguous 404 refusal, blob/tree mismatches, truncated trees, unsupported entries, concurrent target change, no-op equal snapshots, non-force writes and read-after-write failure.
- **9 existing handover regression tests passed.** Reconstruction validation still confirms 13 categories / 133 sub-agents / 421 product counts / 32 cataloged files.
- **4 report-viewer tests passed:** readable table, download, HTML escaping and private/path-traversal URL rejection.
- **3 JavaScript tests passed:** explicit unverified health, blocked operations, immutable metadata and no claimed security implementation.
- Bash syntax passed for the runner and legacy controller; JavaScript syntax passed for both repaired files.
- Live read-only check against the target used by the old main sync workflow (`deepakGoyal1356/Vyomaraj-Agent-6d64`) returned **BLOCKED, HTTP 404**. Sanitized evidence is in `ops/dr/DR_CHECK_2026_10_03.json`.
- **36 automated tests passed in total.** These are not a production restore/failover drill or proof that external providers/devices are connected.

## What must happen before a real sync can pass

1. **Reconnect GitHub in Arena** with access to the intended private secondary and appropriate primary Actions permissions. This connection cannot currently inspect that secondary or the repository variables.
2. An authorized owner confirms the exact secondary full name, rather than choosing among the conflicting suffixes by guesswork.
3. Separately review the Actions secret `VYOMARAJ_PAT` securely in repository settings. Arena authentication and this Actions secret are different credentials. Do not paste tokens into chat.
4. Review/merge the repair branch into primary main through a PR. This session does not push to main. The old main workflow is unchanged until review/merge.
5. Configure `VYOMARAJ_DR_REPO`; run manual **verify** first. Confirm branch existence, permissions and intended exact-snapshot semantics.
6. Only then approve `VYOMARAJ_DR_SYNC_ENABLED=true` and run the main-only **sync** path. Review sanitized evidence and independently compare source/target Git tree SHAs.

## Still unresolved; not hidden by the fixes

- Full 421-title product catalog, 87 unknown canonical individual names, missing sub-sub-agent hierarchy and disputed historical candidate mappings.
- Real device migration, live AI/media/social publishing adapters, deployed backend/database health and product readiness.
- Legacy tracked sensitive material and potentially destructive healing/controller behavior: documented for separate cleanup/review, not executed or globally rewritten here.
- Legal/commercial rights, native-app provenance and production RPO/RTO.
- Primary/secondary data equality and successful DR restore remain unverified until access is repaired.

## Publication status

- Repair commit `922feee857968d2e8132a88da4bee53e968164a3` was pushed to `arena/01a10140-vyomarajai`; the origin ref was verified. This document is a follow-up evidence update.
- Review PR **#5** is OPEN: https://github.com/Vyomaraj1356/Vyomarajai/pull/5. It was MERGEABLE at the check; it has not been merged.
- GitHub CI run **37116901675** passed the offline-tests job. The verify-or-sync job was **SKIPPED by the feature-branch safety gate**. A green workflow here is not evidence of DR synchronization.
- An explicit READ-ONLY workflow dispatch on this session branch was attempted, with the old main workflow's target as a diagnostic candidate. GitHub rejected dispatch with **403 Resource not accessible by integration**. No secondary write was attempted by that request.
- Published inventory URL returned **HTTP 200**: https://github.com/Vyomaraj1356/Vyomarajai/blob/arena/01a10140-vyomarajai/ops/vyomaraj-core/handover/FULL_SYSTEM_INVENTORY_2026_10_03.md.
- Local report-preview routes `/`, `/dr-status`, `/handover` and `/download/inventory.md` all returned HTTP 200. Private-file/traversal routes are rejected in tests.

Primary main remains unchanged by this session. No secondary write or traffic switch occurred. Reconnection/permissions, target confirmation and PR review are required before the live sync can be completed.
