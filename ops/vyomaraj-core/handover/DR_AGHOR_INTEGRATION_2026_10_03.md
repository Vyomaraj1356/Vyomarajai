# Vyomaraj / Jarvis — DR and Aghor Integration Update

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

Evidence: `ops/dr/LIVE_AUDIT_2026_10_03.json`. Main run: https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/37123060948 . The observation is a timestamped audit, not a live success indicator.

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

Detailed operator steps: `ops/dr/README.md`. GitHub review: https://github.com/Vyomaraj1356/Vyomarajai/pull/5 . No merge to main or production DR completion is asserted here.

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
