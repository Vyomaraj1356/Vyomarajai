# AUTO-ALIGN EXECUTION PLAN — V16.9

As of: 2026-10-04

A finite completion path for every currently open platform-check item. Status does not become DONE without repository evidence; account access, owner decisions, installations, live connections and publishing are never performed by this runner.

**This is a completion path, not a claim that an account, provider, service or control is configured.** The runner is local-only. Owner decisions stay with the owner; no installation, purchase, provider connection, content publishing, GitHub comment/close, push or merge is performed automatically.

Plan: **21 steps · 5 phases · 41 open platform items mapped · 14 local checks**.

## Phase 0 — automatic readiness and publication

The two local/preview checks are runnable without owner credentials. Publishing is a separate agent action after review and is not triggered by `--run`.

### a01-local-auto-align — Run local verification sequence

- **Owner:** agent · **Initial state:** `READY_AUTOMATIC`
- **Action:** Run the allowlisted local-only sequence below and write timestamped evidence for the commands that ran.
- **Verify:** python3 ops/vyomaraj-core/handover/auto_align.py --run
- **Done when:** All required local checks pass; unavailable preview routes are explicitly recorded as expected skips; the state file lists failures as zero.
- **Evidence:** `AUTO_ALIGN_STATE_2026_10_04.json`

### a02-preview-verify — Verify the live preview when available

- **Owner:** agent · **Initial state:** `READY_AUTOMATIC`
- **Action:** Check the allowlisted viewer and gateway routes on the local preview ports; never start, stop or publish a service as part of this check.
- **Verify:** The l09 and l13 checks in AUTO_ALIGN_STATE_2026_10_04.json.
- **Done when:** Each available route has its expected status and content marker, or a down preview port is recorded as SKIPPED_PREVIEW_UNAVAILABLE.
- **Evidence:** `AUTO_ALIGN_STATE_2026_10_04.json`

### a03-publish — Publish the reviewed branch

- **Owner:** agent · **Initial state:** `AWAITING_AGENT`
- **Action:** After local checks and owner review, publish only arena/01a10655-vyomarajai and open a pull request. Do not merge automatically.
- **Verify:** Read the branch head and pull-request checks from GitHub after the owner-approved publish action.
- **Done when:** The change is visible in a pull request from the required session branch and the PR records its checks; merge remains an owner decision.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/a03-publish.json`

## Phase 1 — Owner decisions

### o01-secret-manager — Select the secret manager

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Choose the approved secret manager, access owners and rotation procedure; record names and policy only.
- **Verify:** Review the secret-manager configuration and access policy without copying secret values into the repository.
- **Done when:** The owner-approved manager, access policy and rotation evidence are recorded in the repository with no secret values.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/o01-secret-manager.json`
- **Open-item coverage:** `O-01`

### o02-contract-authority — Resolve the governing contract record

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Identify which conflicting contract-status record governs and document the decision without deleting historical records.
- **Verify:** Compare the candidate records, owner decision and their scope; retain a superseded-by pointer for the non-governing record.
- **Done when:** One governing record and its authority are owner-approved, with the conflict and retained history documented.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/o02-contract-authority.json`
- **Open-item coverage:** `O-02`

### o03-tool-accounts — Confirm accounts and plans

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Inventory the tool accounts, owners and selected plans needed for the approved work; leave unknowns explicit.
- **Verify:** Review the account inventory and access boundaries; do not infer a price, plan limit or connected status.
- **Done when:** The owner has approved an account and plan inventory and each item has an evidence pointer or an explicit not-selected status.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/o03-tool-accounts.json`
- **Open-item coverage:** `O-03`

### o04-posilki — Clarify the recorded term

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Confirm what "posilki" means in the source note and whether it names a tool, person, workflow or typo.
- **Verify:** Record the owner's exact interpretation and point to the source context.
- **Done when:** The term has an owner-confirmed meaning or is explicitly marked unresolved and removed from active setup assumptions.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/o04-posilki.json`
- **Open-item coverage:** `O-04`

## Phase 2 — Provider connections

### p01-research-drafting — Configure research and drafting providers

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Review Perplexity, ChatGPT, custom GPTs, Claude and Gemini as separate owner-approved workflows with scoped access.
- **Verify:** For each selected provider, record the account owner, allowed data, test result, failure behavior and reviewer without storing credentials.
- **Done when:** Every provider is either owner-approved and tested with repo evidence, or explicitly declined with a reason and no connection made.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/p01-research-drafting.json`
- **Open-item coverage:** `P-01`, `P-02`, `P-03`, `P-04`, `P-05`

### p02-media-pipeline — Configure media tools and rights evidence

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Review Canva, ElevenLabs, Animaker and CapCut; document approved stock and music sources with item-level rights evidence.
- **Verify:** Test each selected tool using owner-approved sample media, consent records and export review gates.
- **Done when:** Selected tools and media sources have owner approval, documented rights/consent and a reviewed export path; unselected tools stay disabled.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/p02-media-pipeline.json`
- **Open-item coverage:** `P-06`, `P-07`, `P-08`, `P-09`, `P-10`, `P-11`

### p03-publishing-stack — Configure publishing, scheduling and analytics

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Select destinations, account owners, scheduling rules, analytics scope and rollback behavior.
- **Verify:** Review platform permissions and conduct a non-publishing dry run with an owner-approved test asset.
- **Done when:** Each destination has explicit approval, least-privilege access, a schedule policy and analytics evidence; no item is published by this plan.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/p03-publishing-stack.json`
- **Open-item coverage:** `P-12`, `P-13`, `P-14`

### p04-review-gates — Exercise review gates with real media

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Exercise the approval path using real media selected and approved by the owner before enabling any publishing connection.
- **Verify:** Record consent, rights, moderation, owner approval, rejection and rollback test outcomes.
- **Done when:** The owner signs off on the end-to-end review evidence and publishing remains disabled until that sign-off.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/p04-review-gates.json`
- **Open-item coverage:** `P-15`

## Phase 3 — Studio and services

### s01-studio-install — Install the studio path

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Install and test the camera, voice path, mixer and cut room in the approved space.
- **Verify:** Record device inventory, consent/access controls, signal tests and a reviewed handoff sample.
- **Done when:** Each studio component passes its documented test and the owner approves the handoff workflow.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/s01-studio-install.json`
- **Open-item coverage:** `S-01`, `S-02`, `S-03`, `S-04`

### s02-queue-events — Deploy queue and event path

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Deploy the replicated queue and its event path with explicit ownership, idempotency, retry and recovery rules.
- **Verify:** Run duplicate, delayed, retry, failover and restore tests; preserve their outputs as evidence.
- **Done when:** Queue and event tests pass on the intended failure domains and a documented restore procedure is owner-approved.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/s02-queue-events.json`
- **Open-item coverage:** `S-05`, `S-06`

### s03-rag-cag-mag — Configure retrieval and memory boundaries

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Define RAG sources, CAG context rules and MAG memory boundaries per data class and agent.
- **Verify:** Review provenance, retention, deletion, cross-workspace isolation and output attribution tests.
- **Done when:** All retrieval and memory paths have owner-approved scope, tests and rollback evidence; unapproved sources remain excluded.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/s03-rag-cag-mag.json`
- **Open-item coverage:** `S-07`, `S-08`, `S-09`

### s04-workspaces-contracts — Scope workspaces and agent contracts

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Create least-privilege workspaces and reconcile per-agent contracts against the owner-selected governing record.
- **Verify:** Test isolation and audit logging; compare every assigned agent's permissions to its approved contract.
- **Done when:** Workspace boundaries and contract assignments have owner approval, evidence and a tested revocation path.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/s04-workspaces-contracts.json`
- **Open-item coverage:** `S-10`, `S-11`

### s05-jarvis-channels — Configure Jarvis runtime and channels

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Design the Jarvis 24x7 service window and channels with an owner-controlled escalation route.
- **Verify:** Test service restart, channel delivery, alerting, access revocation and safe shutdown.
- **Done when:** Runtime and channels pass their documented tests under owner-approved supervision and have a verified stop path.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/s05-jarvis-channels.json`
- **Open-item coverage:** `S-12`, `S-13`

### s06-shriyantra — Deploy ShriYantra control services

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Define authority boundaries and deploy the ShriYantra control services with fail-closed behavior.
- **Verify:** Test authorized, unauthorized, unavailable and rollback paths with an owner-approved test fixture.
- **Done when:** The authority matrix and test evidence are approved by the owner; a control failure cannot silently widen access.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/s06-shriyantra.json`
- **Open-item coverage:** `S-14`

## Phase 4 — Disaster recovery and operations

### d01-independent-dr — Establish independent DR and tested restore

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Provision a separate DR failure domain and run a complete restore from an owner-approved backup.
- **Verify:** Record the independent-site identity, backup provenance, restore test, integrity results and limitations.
- **Done when:** The separate site and restore test are independently reviewed and documented; local two-lane evidence is not substituted.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/d01-independent-dr.json`
- **Open-item coverage:** `D-01`, `D-02`

### d02-business-probes — Define business window and real probes

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Set the business maintenance window, escalation ownership and real probe scope.
- **Verify:** Run probes only with explicit owner authorization; record target, timing, safety boundaries and measured results.
- **Done when:** The business window is approved and each real probe has an auditable result with no production claim beyond its scope.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/d02-business-probes.json`
- **Open-item coverage:** `D-03`, `D-04`

### d03-rollout-hermes — Stage rollout and Hermes monitoring

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Define canary, stop and rollback gates; configure Hermes monitors and prove alert delivery.
- **Verify:** Exercise the rollout and alert path on an approved non-production target before any production change.
- **Done when:** The staged rollout and alert evidence are owner-reviewed and the rollback gate has passed a controlled test.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/d03-rollout-hermes.json`
- **Open-item coverage:** `D-05`, `D-06`

### d04-intelligence-learning — Define runtime intelligence and learning loop

- **Owner:** owner · **Initial state:** `OWNER_ACTION_REQUIRED`
- **Action:** Set privacy scope, owner review, versioned evaluations and rollback criteria before activating runtime learning.
- **Verify:** Review a reproducible evaluation set, data lineage, retention policy and rollback exercise.
- **Done when:** The owner approves the runtime-intelligence boundary and the measured learning loop demonstrates a reversible release.
- **Evidence:** `AUTO_ALIGN_EVIDENCE/d04-intelligence-learning.json`
- **Open-item coverage:** `D-07`, `D-08`

## Fourteen-step local sequence

Run from the repository root with `python3 ops/vyomaraj-core/handover/auto_align.py --run`. Commands are fixed argv lists (no shell); preview checks are loopback-only and record an explicit skip if the service is not already running.

| Step | Check | Mode |
|---|---|---|
| `l01-platform-check` | Verify all open platform items still map to a completion step. | `python3 ops/vyomaraj-core/handover/build_platform_check.py --check` |
| `l02-issue-ledger` | Verify the issue and PR ledger is current with its source data. | `python3 ops/vyomaraj-core/handover/build_issue_ledger.py --check` |
| `l03-align-self-check` | Validate the plan structure, safety and rendered page. | `python3 ops/vyomaraj-core/handover/auto_align.py --check` |
| `l04-offline-suites` | Run the complete offline Python, Node and builder suite; write evidence only after execution. | `python3 ops/vyomaraj-core/handover/run_offline_suites.py` |
| `l05-handover-check` | Verify the canonical handover note from its source data. | `python3 ops/vyomaraj-core/handover/rebuild_handover.py --check` |
| `l06-registry-check` | Verify the current registry builder. | `python3 ops/vyomaraj-core/agents/rebuild_registry.py --check` |
| `l07-inheritance-check` | Verify the ownership and inheritance audit. | `python3 ops/vyomaraj-core/agents/inheritance_audit.py --check` |
| `l08-dr-report-check` | Verify the DR report from recorded evidence. | `python3 ops/vyomaraj-core/handover/build_dr_sync_report.py --check` |
| `l09-viewer-preview` | Check report-viewer routes when the local viewer is already running. | `localhost:4174 routes` |
| `l10-language-policy` | Check tracked text files decode as UTF-8 and contain no NUL bytes. | `python3 ops/vyomaraj-core/handover/check_language_policy.py --check` |
| `l11-transfer-package` | Verify the deterministic, non-secret handover package. | `python3 ops/vyomaraj-core/handover/build_transfer_package.py --check` |
| `l12-diff-whitespace` | Check the working diff for whitespace errors. | `git diff --check` |
| `l13-gateway-preview` | Check gateway report routes when the local gateway is already running. | `localhost:4176 routes` |
| `l14-evidence-scope` | Check generated evidence for internally consistent counts without requiring it to predate the suite that wrote it. | `python3 ops/vyomaraj-core/handover/run_offline_suites.py --check` |

## Safety and evidence rules

- read repository files.
- run local test commands.
- render reports.
- write timestamped local evidence.
- Never automatic: install packages.
- Never automatic: purchase services.
- Never automatic: connect provider accounts.
- Never automatic: publish content.
- Never automatic: comment or close GitHub issues.
- Never automatic: push or merge code.
- Never automatic: change live infrastructure.

Every open item has exactly one step id in the generated platform-check report. A step moves to DONE only after its `done_when` evidence is reviewed and stored; the initial status in this plan is not a completion claim.

## Source map for open items

| Item | Area | Open check | Completion step |
|---|---|---|---|
| `O-01` | Owner decision | Select and configure the approved secret manager; record secret names and access policy, never secret values. | `o01-secret-manager` |
| `O-02` | Owner decision | Identify which contract record governs where the repository currently records a conflict. | `o02-contract-authority` |
| `O-03` | Owner decision | Inventory the required tool accounts and owner-selected plans, without guessing plan limits or costs. | `o03-tool-accounts` |
| `O-04` | Owner decision | Confirm the meaning and intended use of the recorded term "posilki". | `o04-posilki` |
| `P-01` | Research and drafting providers | Owner-authorize and configure the Perplexity research workflow. | `p01-research-drafting` |
| `P-02` | Research and drafting providers | Owner-authorize and configure the ChatGPT workspace. | `p01-research-drafting` |
| `P-03` | Research and drafting providers | Identify and review the custom GPTs required for the approved workflow. | `p01-research-drafting` |
| `P-04` | Research and drafting providers | Owner-authorize and configure the Claude workflow. | `p01-research-drafting` |
| `P-05` | Research and drafting providers | Owner-authorize and configure the Gemini workflow. | `p01-research-drafting` |
| `P-06` | Media providers | Configure Canva canvas access and a reviewed asset workflow. | `p02-media-pipeline` |
| `P-07` | Media providers | Configure ElevenLabs voice access with consent and review gates. | `p02-media-pipeline` |
| `P-08` | Media providers | Configure Animaker access and a reviewed export path. | `p02-media-pipeline` |
| `P-09` | Media providers | Configure CapCut access and a reviewed edit/export path. | `p02-media-pipeline` |
| `P-10` | Media providers | Document approved stock image/video sources and item-level rights evidence. | `p02-media-pipeline` |
| `P-11` | Media providers | Document approved music/audio sources and item-level rights evidence. | `p02-media-pipeline` |
| `P-12` | Publishing, scheduling and analytics | Select publishing destinations and authorize accounts per platform. | `p03-publishing-stack` |
| `P-13` | Publishing, scheduling and analytics | Configure a human-approved scheduling workflow and its rollback path. | `p03-publishing-stack` |
| `P-14` | Publishing, scheduling and analytics | Configure analytics access, retention and owner review. | `p03-publishing-stack` |
| `P-15` | Review gates | Exercise review gates with real, owner-approved media before any publishing workflow is enabled. | `p04-review-gates` |
| `S-01` | Studio and services | Install and verify the camera in the owner-approved studio location. | `s01-studio-install` |
| `S-02` | Studio and services | Install and verify the voice/microphone path and consent controls. | `s01-studio-install` |
| `S-03` | Studio and services | Install and verify the audio mixer and monitored signal path. | `s01-studio-install` |
| `S-04` | Studio and services | Prepare the cut room and reviewed media handoff. | `s01-studio-install` |
| `S-05` | Studio and services | Deploy a replicated work queue with documented ownership and recovery. | `s02-queue-events` |
| `S-06` | Studio and services | Deploy and test the queue event path, including duplicate and retry behavior. | `s02-queue-events` |
| `S-07` | Studio and services | Configure RAG sources, access scopes, freshness and deletion behavior. | `s03-rag-cag-mag` |
| `S-08` | Studio and services | Configure CAG context assembly, provenance and review controls. | `s03-rag-cag-mag` |
| `S-09` | Studio and services | Configure MAG memory boundaries, retention and per-agent access. | `s03-rag-cag-mag` |
| `S-10` | Studio and services | Create scoped workspaces with least-privilege access and audit evidence. | `s04-workspaces-contracts` |
| `S-11` | Studio and services | Reconcile and approve per-agent contracts before assigning live work. | `s04-workspaces-contracts` |
| `S-12` | Studio and services | Install and exercise the Jarvis 24x7 runtime under an owner-approved service window. | `s05-jarvis-channels` |
| `S-13` | Studio and services | Configure Jarvis communication channels with delivery and escalation tests. | `s05-jarvis-channels` |
| `S-14` | Studio and services | Deploy ShriYantra control services with explicit authority and fail-closed behavior. | `s06-shriyantra` |
| `D-01` | Disaster recovery and operations | Provision an independent DR failure domain; the local two-lane rehearsal is not independent DR. | `d01-independent-dr` |
| `D-02` | Disaster recovery and operations | Run and record a tested restore from an independent, owner-approved backup. | `d01-independent-dr` |
| `D-03` | Disaster recovery and operations | Define and approve the business maintenance window and escalation owner. | `d02-business-probes` |
| `D-04` | Disaster recovery and operations | Run real, owner-approved probes and record their scope, result and limitations. | `d02-business-probes` |
| `D-05` | Disaster recovery and operations | Define a staged rollout with explicit canary, stop and rollback gates. | `d03-rollout-hermes` |
| `D-06` | Disaster recovery and operations | Configure Hermes monitoring and prove actionable alert delivery. | `d03-rollout-hermes` |
| `D-07` | Disaster recovery and operations | Define runtime intelligence inputs, privacy scope and owner review before activation. | `d04-intelligence-learning` |
| `D-08` | Disaster recovery and operations | Define a measured learning loop with versioned evaluations and rollback criteria. | `d04-intelligence-learning` |
