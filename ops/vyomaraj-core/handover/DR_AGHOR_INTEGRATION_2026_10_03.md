# Primary / Secondary — Exact File Match Verified

**3 October 2026 · deployed on main · real sync and repeat verification succeeded.**

## Verified result

PR #5 was merged through GitHub at primary commit `37930203be6de10efb9587cf1434d860f9a6c294`. The main sync run **37126108656** completed successfully. A separate scheduled run **37126121716** then confirmed the same match.

| Checkpoint measurement | Verified result |
|---|---|
| Primary | Vyomaraj1356/Vyomarajai — main |
| Secondary | deepakGoyal1356/Vyomaraj-Agent-6d64e — main |
| Tracked files at this checkpoint | **244 on each matching tree** |
| Primary tree | `e69e5c90f2ddec237a307b45830cff712649ed92` |
| Secondary tree | `e69e5c90f2ddec237a307b45830cff712649ed92` |
| GitHub result | **status=MATCH; data_match=true** |
| Previous secondary commit preserved | `7107980ce0bb1fc788da9e1f7a87f3d6cd9bf1d3` |
| Production traffic switching | None |

Matching Git tree hashes cover the tracked paths, file bytes and file modes of these main snapshots. Commit hashes/history can differ because the secondary keeps its own previous commit as parent for rollback. No force push or Git-history deletion was used.

Evidence: `ops/dr/DEPLOYED_MATCH_2026_10_03.json`.

Sync: `https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/37126108656`

Repeat check: `https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/37126121716`

## Authorized correction and retained rollback

The owner explicitly requested completing the exact match after the extra-file issue was explained. A new preflight compared the release—not just the old primary main—to secondary: 150 secondary-only paths, 120 missing paths and 6 changed shared paths. Approval was bound to the exact preflight secondary commit/tree and a UTC expiry; any target advance would invalidate it.

The correction built the exact new tree without `base_tree`, validated it before publication, preserved the old secondary commit as parent, updated the ref without force, and performed read-after-write and stable-source checks. The owner-approved snapshot-only removal gate was consumed successfully and is now disabled. Future target-only removals still need explicit approval; no permanent blanket deletion permission was added.

The old secondary's files remain recoverable through its retained parent commit. That is a Git rollback checkpoint, not an independent-site backup. Restoration still needs review and fencing; no automatic reverse overwrite is enabled.

## What this does not claim

This is a **verified Git main snapshot match**, not proof of identical unrelated branches, repository settings, secrets, ignored runtime files, databases, browser-local media, or production traffic. Independent-site/runtime recovery and zero RPO/RTO are not verified. Spiritual content remains entertainment/view-only, with Sovereign policy and draft Contracts unchanged.

This report records a specific verified checkpoint **before this evidence/report update**. Publishing the update changes the source tree and adds an evidence file; its rollout requires another sync and will produce a newer tree hash/file count. The dated hashes above are not presented as a permanent live-HEAD guarantee. Current workflow results remain the authority for each later snapshot.

## Validation

**227 automated checks passed in release CI**, including 53 DR tests, and the real main sync and scheduled repeat both passed. No secret values or file bodies were placed into public diagnostic annotations. Local-planner flags describe actions performed by each plan; they do not independently verify GitHub. `/api/status` carries this explicitly scoped external Git snapshot observation.

## Earlier investigation and integration history

The previous mismatch reports below are preserved as dated history. Their statements that PR #5 is open or production Git sync is unexecuted are superseded by this verified result. Runtime/site DR limitations remain in effect.

# DR Script Investigation — Confirmed Tree Mismatch

**3 October 2026 · real GitHub Actions credential probes executed, not just local tests.**

## Confirmed current problem

Actions run **37125323786**, job **111209399552**, successfully read primary and secondary repository metadata, both main refs, both commit/tree snapshots and full non-truncated tree metadata. Stable refs were rechecked. It reported:

| Measurement | Observed count |
|---|---:|
| Files on primary main | 125 |
| Files on secondary main | 274 |
| Primary files missing on secondary | 0 |
| Shared files with different content or mode | 0 |
| Secondary-only files | **149** |

**All 125 primary files match, but the entire trees differ because secondary contains 149 extra files.** This is a confirmed explanation of the current integrity mismatch, not speculation that the repository is missing or its credential is invalid. Counts describe primary main `9be6d39` at the audit; they must be recalculated after the proposed changes reach main.

Evidence: `ops/dr/ACTIONS_PROBE_EVIDENCE_2026_10_03.json`. GitHub run: `https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/37125323786` . The earlier probe `37125232441` independently confirmed read access and tree mismatch. The evidence was retrieved from check-run annotations, so it did not depend on the broken log-download path. No file bodies, private filenames or credentials were emitted; neither probe wrote data or refs.

## Actual script defect and correction

The old main workflow sets `tree_payload["base_tree"] = base_tree`, overlays primary entries, publishes the resulting commit, and only afterward checks whole-tree equality. That construction retains secondary-only paths while its validation requires them not to exist. It can publish a non-matching snapshot before reporting failure.

The replacement script in this review branch:

- Builds an exact tree **without base_tree** and verifies its SHA **before publishing a ref**.
- Preserves the old secondary commit as the new commit's parent; no force push or automatic history deletion.
- Rechecks source and destination refs and verifies the published result.
- Reuses blobs already on secondary instead of uploading matching content again.
- Emits a sanitized **DR SNAPSHOT RESULT** annotation with HTTP status and failed API operation, so future errors remain visible when log downloads fail.
- **Refuses target-only file removal by default, before any write.** The newly measured extra files are not assumed to be disposable.

Local regression tests verify both paths: unapproved removal is blocked without any writes; explicit approval produces the exact tree without `base_tree`, while retaining the previous commit as parent. The DR suite now has **48 passing tests**.

## What is, and is not, proved

The existing Actions credential can read both main branches and their trees. The failure of Arena's separate connection to read the private secondary is not the same failure. Replacing the Actions PAT blindly is not justified by these results. Its permission to perform future writes remains unverified.

The old main replication run `37123060948` and separate verifier `37123060897` are failed. Both log-download methods (`gh api` job logs and `gh run view --log-failed`) returned EOF with zero log bytes; the exact historical exception is still unavailable. The 149-file mismatch and the conflicting old-script logic are independently confirmed, but we do not invent a historical HTTP error or claim this excludes another error in that run.

## Deployment and approval gates

The corrected code is on `arena/01a10140-vyomarajai`, in **open PR #5**, not on main. Thus main still runs the old script. PR: `https://github.com/Vyomaraj1356/Vyomarajai/pull/5` . No merge to main, secondary ref update or production traffic switch was performed in this investigation.

1. Review/merge the correction through the authorized GitHub process. Automatic main sync will still refuse any unapproved target-only removals.
2. Run **verify** against the then-current primary main and secondary. Do not assume today's 149-file count still applies after the merge.
3. Review secondary-only content and preserve an independent backup/known-good recovery checkpoint. If secondary has its own necessary application files, do not authorize an exact-root mirror until storage/layout requirements are resolved.
4. Only when an exact-root mirror and the specific removals are intended: manually run the main workflow with `mode=sync` and **allow_target_only_removal=true**. The checkbox defaults false; scheduled and push-triggered runs do not implicitly grant this approval. The script also requires the existing main/repository/credential gates.
5. Require final `MATCH` / `data_match=true` and readback evidence. If GitHub rejects a write, the new annotation identifies the failing operation/HTTP status; then address the actual permission or branch-rule issue.

**Implemented solution: exact-tree construction, pre-publication integrity, actionable error reporting and a removal-review gate. Production correction is not yet executed.** Git mirroring is still separate from runtime/database recovery, independent-site failover, and any zero-RPO/RTO claim.

## Current validation

**222 automated checks PASS locally:** DR 48; local availability 8; handover 13; Pairings 9; experience/governance 77; research 36; registry 28; Node metadata safety 3. Registry and historical-handover rebuild checks also pass. Real Actions read probes passed in runs 37125232441 and 37125323786; these are read evidence, not production sync.

## Earlier integration snapshot

The following report retains earlier local drill results and Aghor research history. The latest owner-directed entertainment/view-only policy still applies; Aghor practice planning remains disabled. See `/reports/policy`, `/sovereign/` and `/contracts/`.

# Vyomaraj / Jarvis — DR and Aghor Integration Update

**Latest owner correction:** Entertainment and view-only spiritual content; participation is voluntary. No hazardous rituals or cure claims. Aghor practice-plan UI/API and all practice steps have been removed. Previous planner descriptions below are historical. See `/reports/policy`, `/sovereign/` and `/contracts/` for the current non-harm policy and draft earning terms.

**3 October 2026 · implemented and locally tested · production DR remains unverified.**

## Executive status

| Requirement | Observed result |
|---|---|
| Correct secondary | `deepakGoyal1356/Vyomaraj-Agent-6d64e`, confirmed by primary main's target corrections |
| Main Actions authentication | PASS in run `37123060948` |
| Main Actions replication | FAIL at `Replicate PRIMARY main to DR main`; subsequent integrity reporting skipped |
| Exact failure cause | Not established: retrieved annotation says exit code 1; full failed log unavailable through this connection |
| Arena connection | Primary readable; secondary 404; Actions settings/secret-name metadata 403; earlier dispatch attempt 403 |
| Code/workflow improvements | Prepared on review branch; do not activate until authorized merge to main |
| Application process failover | Locally deployed and actually drilled; either replica can serve this shared application |
| Independent-site/data disaster recovery | NOT deployed or verified; shared sandbox/storage and one gateway remain common failure points |
| Zero RPO / zero RTO | NOT demonstrated or promised |
| Aghor & Aghori | New requested Bhakti-Shakti sub-agent, live local viewer and safe deterministic planner |
| Current hierarchy | 13 categories, 128 counted slots, six uncounted headings; 42 named / 86 unnamed |
| Validation | 206 automated checks and six real Chromium suites PASS |

The reports distinguish **Git snapshot replication**, **application process availability** and **runtime/data disaster recovery**. Success in one is not proof of the others. “Vyomaraj replica” and “Jarvis replica” are labels for two copies of this application, not evidence of independent autonomous AI agents backing up their memories or credentials.

## 1. GitHub investigation and implemented changes

Primary main advanced to `9be6d3950cb65dcdd5dba36e548f48c599361d57`. Its corrected secondary differs from the older failing target. The main workflow's Actions PAT can authenticate while Arena's separate connection cannot read the private secondary. A local 404 is therefore not proof that the repository is absent or that the Actions PAT is invalid. Primary metadata reports repository admin/push capabilities, but Actions endpoint access still returns 403; role metadata and token endpoint permissions are different.

Evidence: `ops/dr/LIVE_AUDIT_2026_10_03.json`. Main run: `https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/37123060948` . The observation is a timestamped audit, not a live success indicator.

### Review-branch implementation

- Reconcile primary main's corrected target and retain one consolidated workflow with explicit policy in `ops/dr/DR_POLICY.json`; retire the redundant verifier.
- Reviewed file defaults select the confirmed target and the owner-requested primary-main writer policy when repository variables are unset. Explicit repository variables override these defaults. This avoids an unnecessary settings-write dependency but does not grant new token permissions.
- Reuse existing authenticated target blob SHAs and upload repeated new content once; avoid needless archive retransfers.
- Retry only bounded transient GET failures, respecting numeric Retry-After within the budget. Never retry ambiguous writes; do not retry authentication/permission failures.
- Keep exact no-base-tree construction, path/hash/mode checks, source and target race guards, non-force ref update and final readback comparison. The deployed old workflow's base-tree approach can retain target-only files; that is a concrete code risk, not the established cause of this run's failure.
- Add sanitized API-operation classification and a GET-only live audit. No credentials or raw provider error bodies are put into reports.
- Add secondary-to-primary **read-only recovery planning**, not automatic reverse overwrite. Fencing, a known-good snapshot, backups, security/diff review and fresh-ref checks remain mandatory before a separately authorized restore.

The live recovery-review CLI was attempted against the corrected target and exited **BLOCKED**, with `writes_performed: false`; see `ops/dr/RECOVERY_REVIEW_2026_10_03.json`. No secondary ref, repository settings, PAT value or production traffic was changed by this session.

### What must still happen for verified Git replication

1. Reconnect/reauthorize the Arena GitHub integration for the intended private repository and relevant Actions endpoints. Never send PATs in chat.
2. Review and merge the review-branch workflow/policy through the authorized GitHub process. Review-branch CI does not execute production replication.
3. Privately verify `VYOMARAJ_PAT` in GitHub Actions secrets: selected target access, Contents read/write, Workflows write for workflow-file changes, applicable organization approval/SSO and compatible branch rules. Metadata-read success alone proves none of those write permissions.
4. Run read-only verification first, then approved primary-main sync. Require complete-tree `MATCH`, `data_match=true` and final read-after-write evidence, not just a green authentication step.
5. Maintain independent versioned backups: a mirror propagates deletions/corruption too. Test recovery of runtime databases, secrets, uploads and other non-Git state separately.

Detailed operator steps: `ops/dr/README.md`. GitHub review: `https://github.com/Vyomaraj1356/Vyomarajai/pull/5` . No merge to main or production DR completion is asserted here.

## 2. Real local Vyomaraj / Jarvis failover rehearsal

The local preview gateway on port 4176 routes to two studio processes on ports 4181 and 4182. Browsers use relative URLs; loopback addresses are only gateway-side. Both replicas share the same checkout and SQLite queue. This is intentionally an application-process rehearsal, not two independent GitHub-backed deployments.

| Controlled state | Actual HTTP result | Served by | Single request after fault |
|---|---:|---|---:|
| Both replicas ready | 200 | Primary | 3.572 ms |
| Primary stopped | 200 | Secondary | 5.396 ms |
| Secondary stopped, primary restored | 200 | Primary | 5.152 ms |
| Both stopped | 503 | None | 2.609 ms |
| Both restored | 200 | Primary; both checks ready | 3.678 ms |

Evidence: `ops/availability/LOCAL_FAILOVER_DRILL_2026_10_03.json`, recorded 12:43–12:44 UTC. **These are individual request latencies after the fault, not measured disaster-onset-to-recovery time, guaranteed detection time, production RTO or replication lag.** Both replicas were restored after the drill.

- GET falls back on connection failures/server errors; a legitimate 404 remains a 404.
- POST chooses a ready replica and is sent once. Ambiguous transport failure returns 503 with `write_outcome_unknown_not_retried`; callers must inspect state before retrying. Eight tests include the no-replay safety case.
- `/api/availability` exposes current rehearsal readiness and explicitly reports `production_dr_verified: false`. Replica `/healthz` validates current application metadata only, not all dependencies or data durability.
- The shared discovery lease is not instantaneous worker-job migration: existing lease-expiry recovery still applies.
- A machine/storage failure or gateway failure can take out the whole rehearsal. Authentication, redundant ingress, separate hosts, durable replicated state, encrypted backup/restore and workload-based RPO/RTO measurement remain production requirements.

Implementation/runbook: `ops/availability/README.md`. No automatic bidirectional-main overwrite or split-brain writer promotion is configured.

## 3. Aghor & Aghori under Bhakti-Shakti

**New agent:** `BHAKTI-AGHOR-S1`, display name **Aghor & Aghori**. The two preceding unnamed Bhakti positions remain; BHAKTI now has three. No names were invented for the other unnamed positions.

| Content | Implemented |
|---|---:|
| Proposed study chapters | 14 |
| Selected, unranked profiles | 7 |
| Practice/context cards | 6 |
| Care-boundary cards | 6 |
| Timeline entries | 6 |
| Attributed sources | 11 |

The guide covers vocabulary; theological origins versus dated history; limits of the pre-1950 record; lineage self-descriptions; Shaiva-Shakta associations; sadhana/seva; editorial study lenses rather than universal sect ranks; ethical preparation and respectful visits; optional gentle public prayer/reflection/service; healing narratives versus clinical evidence; leprosy care and stigma; product safety and protection from coercion.

Profiles: Shiva and Dattatreya as sacred associations; Kaluram and Kina Ram in attributed lineage narratives; Bhagwan Ram, Harihar Ram and Siddharth Gautam Ram in sourced historical/institutional contexts. These are not a “most powerful” ranking. Sacred origins are not archaeological dates for the beginning of the universe or India. Current appointments are not independently certified; Siddharth's appointment claim is explicitly dated and unverified for 2026.

The research ledger distinguishes an academic excerpt from institutional accounts and clinical authorities. The entire Barrett book was not reviewed. Traditional healing accounts do not establish clinical efficacy. WHO guidance, NCCIH product-safety warnings and India's 112 service support the care boundaries. No medicinal doses, human-remains procedures, hazardous ingestion, coercive exorcism, self-harm or secret initiation instructions are supplied. Spiritual upayas do not replace clinical care.

### Viewer, planner and mapping

- `/aghor/`: chapter and profile filters, six practice cards, care boundaries, timeline, source ledger and downloadable local study/reflection/service plans.
- `/bhakti/`: retained original experience plus the new Aghor entry.
- `/reports/aghor`: research depth, evidence distinctions, proposed chapter scope and source limitations.
- `/agents/` / `/reports/agents`: additive current mapping; serial-only unnamed display retained.
- `/reports/contents`: all five editorial packs, including 33 Aghor chapter/profile/practice/care references.
- `/reports/resilience`: this current DR/integration report.

The deterministic planner reads only the selected Aghor pack plus active registry. It accepts a known topic and `study`, `reflection` or `service`; symptoms, treatment/ritual modes and arbitrary fields are refused. No provider, autonomous guru, prescription, media upload or publication service is connected by this addition.

The active content index has **173 actual references**, including 21 Education topics and 33 Aghor records. References are not 173 new agents or a complete 421-product reconciliation. Education ownership and the six non-counted Entertainment headings remain unchanged. Historical registry/catalogue/inventory snapshots are preserved.

## 4. Validation actually executed

| Suite | Passing checks |
|---|---:|
| DR integrity, permissions, retry and recovery planning | 38 |
| Local availability gateway | 8 |
| Historical handover/report safety | 13 |
| Roots & Pairings | 9 |
| Integrated experience/planner/HTTP | 71 |
| Research/discovery | 36 |
| Current hierarchy/ownership/privacy | 28 |
| Node metadata safety | 3 |
| **Total** | **206** |

**Six real Chromium suites PASS:** Aghor, current agents/Education, Research Desk, Film, Music and the general Bhakti/Pairings experience. They ran against the actual gateway. Aghor coverage checks chapter/profile/practice/care counts, filtering, sourced plan download, stale-plan invalidation, treatment-field rejection, three Bhakti slots with two unnamed, both replicas ready, report access, mobile overflow and absence of JavaScript errors. Existing media playback/local-file rights and report flows remain tested.

Registry and historical-handover rebuild checks pass. Seven app scripts pass Node syntax checks. Workflow YAML parses with the existing validation dependency; shell syntax and Git whitespace checks pass. Historical registry SHA-256 remains `9e301bfcb1c6e8b23c1bea4fbdcf0d9d12d4c457fe62d7ef60e3161ac3a908a9`; historical inventory remains `c2c64cad82afdbc3dc0f498a412b2228d1059f99d3e6f566ef7aabfae1b274d2`.

Local code, viewer integration and the controlled process drill are validated. **Production private-repository replication, independent-site recovery, zero data loss and zero downtime are not validated.**
