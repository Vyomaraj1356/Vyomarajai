# Vyomaraj + Jarvis — Master System Inventory, Operating Procedures, Agents and Content

**Document class:** Owner/operator handover and readiness inventory  
**As-of:** 2026-10-24  
**Repository baseline:** `Vyomaraj1356/Vyomarajai` (`main`)  
**Evidence rule:** This is a descriptive baseline assembled from repository documentation and tool-access evidence. It is not proof that every listed component is installed, connected, deployed, licensed, running, or production-ready.

## 1. Executive summary

Vyomaraj AI Agent OS is intended to be a private, owner-controlled multi-agent operating system for research, creation, operations, publishing, financial control, and resilience. The public experience must remain a narrow allowlisted surface. The private control plane contains orchestration, identities, provider routing, permissions, secrets, job execution, recovery controls, and operational records.

The intended operating loop is:

`RESEARCH → REASON → PLAN → AUTHORIZE → CREATE/EXECUTE → VERIFY → MEASURE → RECONCILE → LEARN → IMPROVE → PROTECT → RECOVER`

**Current reality:** the repository contains substantial architecture, registries, deterministic local prototypes, CI and DR workflows, a provider-neutral LLM harness, and a public-preview server. These artifacts do not establish complete autonomous business operation. Production peer heartbeats, external provider/account connections, local runner installation, publishing, transactional financial integrations, installed device features, and end-to-end DR recovery need separate evidence.

## 2. Authority, roles and boundaries

| Role | Intended responsibility | Authority boundary / current evidence |
|---|---|---|
| Owner / Root | Final authority for identity, access, sensitive actions, public release, spending and recovery decisions. | Owner approval is required for high-impact actions; never infer approval from model output. |
| ShriYantra | Policy and knowledge foundation: identity, model routing, retrieval, capability registry, audit, security and resilience contracts. | The architecture is documented; shared policy references do not prove runtime enforcement. |
| Vyomaraj / Bharath | Platform/control-plane coordination, task decomposition, workflow orchestration, cross-agent routing and operational dashboards. | Core role prompts exist in the harness; live independent production orchestration is not proven. |
| Jarvis / Laxman | Intelligence, operational execution coordination, continuity, monitoring and reciprocal recovery. | Role prompt and LLM harness exist; the harness exposes no tools, and authenticated peer heartbeat/failover is unverified. |
| Hermes | Security, policy enforcement, threat review, privacy, secrets hygiene and incident protection. | Architectural role; do not assume a production security agent is actively enforcing controls. |
| Kuber FC | Finance controller across the system: budgets, provider costs, invoices, receivables/payables, attribution, ROI, reconciliation and audit. | Finance architecture is documented; bank/payment/account connections and live ledger reconciliation are not proven. |
| Chandragupta (proposed Kuber compliance sub-agent) | Legal/regulatory research across applicable jurisdictions, with dated authoritative sources and escalation. | Desired design; no claim of a live legal-monitoring integration. |
| 12 main agents / 12 ShivJyoti Lingas concept | Domain-level orchestration and content stewardship. | This is a user-requested design target; the active checked-in roster currently documents 13 categories, 128 counted sub-agent slots and 6 uncounted entertainment headings. Do not silently force the roster to 12 without an owner-approved migration. |

### Capability inheritance is not permission inheritance

The Panch-Brother behavior domains in the architecture are Matiman (intelligence/strategy), Shrutiman (knowledge/learning), Ketuman (signals/guidance), Gatiman (execution/mobility), and Dhritiman (resilience/constancy). These are descriptive capability mappings, not security grants. No agent may self-grant root access, production secrets, provider credentials, publishing, financial authority, deployment rights, or failover rights.

## 3. Agent taxonomy and content registry

The latest inventory documentation reconciles the active hierarchy as **13 categories, 128 counted sub-agent slots, 6 uncounted entertainment headings, 42 individually approved names and 86 unnamed numbered positions**. The older V16.7.24 snapshot had 133 counted slots; that historical count is retained, not silently overwritten. The product aggregate of 421 is historical and is not yet a reconciled/deduplicated current item-level total.

| Category | Display name | Counted slots | Historical reported products |
|---|---|---:|---:|
| FOOD | Food & Social Connect | 3 | 6 |
| EDU | Education | 16 | 68 |
| ASTRO | Astro-Celestial & Universal | 3 | 9 |
| FINANCE | Finance & Wealth | 7 | 15 |
| LIFE | Life Coach & Wellness | 10 | 34 |
| BHAKTI | Bhakti Mandir — Ritual, Festival & Grantha | 3 | 8 |
| SPORTS | Sports & Legends | 14 | 29 |
| AGRI | Agriculture & Environment | 6 | 14 |
| ENTERTAINMENT | Entertainment — Comedy, Movies, Hollywood, Bollywood | 32 | 168 |
| PLATFORM | Platform & Social Hub + Earn — All Platforms + Monetization | 20 | 39 |
| TOUR | Tour and Travel | 4 | 9 |
| WAR | War Room — Warriors | 5 | 13 |
| PODCAST | Podcast & Entertainment Studio | 5 | 9 |

Historical product figures above are not current reallocated totals. They must not be summed as a verified unique catalog without the underlying item-level manifests. The earlier snapshot reported 394 products, 12 placeholder videos, 52 pending and 5 planned items needing chapters; those workflow figures have not been reconciled against 421 and must remain separately labeled until item-level evidence resolves the difference.

### Content ownership and cross-links

- **Education** is the universal civilization and knowledge spine, not a closed school-subject silo. Government Schemes are assigned to Education rather than Finance or Entertainment.
- Podcast is conceptually part of Education + Entertainment; the historical PODCAST category remains in the current registry until an approved migration updates routing and counts.
- The user requested PLATFORM be renamed **Social Platform**. Apply only through an additive, validated registry migration so IDs and existing content links remain stable.
- The Universal Knowledge Evolution contract defines: `ORIGIN → OLD → HISTORICAL EVOLUTION → HISTORY → PRESENT → CURRENT STATE → TRENDS → FUTURE → POSSIBLE FUTURES`.
- Every claim should carry an evidence class, source provenance, temporal scope, uncertainty, and as-of time where relevant. Trends need at least two dated observations. Forecasts and scenarios must never be presented as facts.
- The policy file currently says `implementation_status: reference_contract_not_deployed`; this is a contract, not proof that production agents enforce it.
- Content IDs, agent IDs, topic IDs, product/media IDs, publishing IDs and financial events should remain linked end to end to prevent duplicates and support Kuber reconciliation.

### Content families and editorial experiences documented

The repository handover documents Food & Social Connect; Education/Government Schemes; astronomy and universal knowledge; Finance & Wealth; Life Coach & Wellness; Bhakti-Shakti including Shiv–Shakti, Shiva story guide, Dashavatara and regional Shakti Peetha starter profiles; Sports & Legends; Agriculture & Environment; Entertainment including comedy/cartoon/music/movie/wit/shayari parent headings; Platform/Social Hub + Earn; Tour & Travel; War Room; Podcast & Entertainment Studio; Film/Stage/Ads; Music/Radio/Audio/Video; Roots & Pairings; Research Desk; comics; approvals; finance briefing; upgrades; and historical/source audits.

These are documented content areas or prototypes, not proof that each content item is complete or that external streaming, charts, AI rendering, publishing or monetization is live. Content rights, provenance, age-safety, regional law and owner approval must be checked per output.

## 4. Architecture and software technologies

| Layer | Technologies / contracts referenced in repository | Status interpretation |
|---|---|---|
| Agent orchestration | Vyomaraj/Jarvis peer-core design, deterministic planners, role prompts, agent/sub-agent registry | Design and some local deterministic code exist; autonomous production execution is not proven. |
| LLM harness | `ops/jarvis/llm_harness.py`; OpenAI-compatible chat-completions; `JARVIS_LLM_ENDPOINT`, `JARVIS_LLM_MODEL`, `JARVIS_LLM_API_KEY`; timeout and token limits | Code exists. The harness has no tools; configured endpoint/key/model and provider response must be independently tested without exposing secrets. |
| Prompt registry | `config/ai/PROMPT_REGISTRY_V1.json` referenced by harness | Versioned presets are validated by code; count/current contents require inventory verification. |
| RAG/CAG/MAG | Retrieval, context assembly and memory architecture | Design contracts; production vector store, memory backend, ACL filters and runtime enforcement are not established by architecture text alone. |
| MCP/A2A | Model Context Protocol and agent-to-agent communication in target architecture | Desired integration layer; do not claim all agents or providers are connected. |
| Durable workflows / queues | Event engine, queue, checkpoints, retries, idempotency and approval gates in architecture | Production scheduler/queue/checkpoint/alert coverage is not fully evidenced. |
| Policy and identity | Owner-bound action tokens, fail-closed gates, least privilege, audit trail; local studio docs describe action-bound Ed25519 approval tokens | Local implementation/config exists in documented prototypes; production issuer/key and distributed enforcement are not verified. |
| State / audit | Local SQLite and hash-chained audit events described for integrated local studio | Local prototype evidence only; not proof of replicated production database or immutable remote audit. |
| Observability | Grafana Cloud / Prometheus; OpenTelemetry architecture; Render health endpoint | Grafana stack/Prometheus instance were previously provisioned but had zero series at the recorded check. Current live metrics and alerts need verification. |
| Deployment | GitHub Actions; Render public-preview service | Service configuration/history exists; live health, deployed SHA and end-to-end behavior require fresh runtime checks. |
| Security scanning | Gitleaks, Trivy, Cosign listed as candidates in PR #114 catalog | Research candidates only; not declared installed or enforced. |
| Provider routing | LiteLLM listed as candidate; OpenRouter-compatible harness reported in prior session | Candidate router is not integrated by the catalog. Previous OpenRouter live test was reported successful, but current runtime and production reliability need a fresh evidence record. |
| AI frameworks | Microsoft Agent Framework, LangGraph, n8n, Haystack, Dify, Ragas listed in research catalog | Discovery only. No third-party package installation or production adoption is claimed. |
| Client surfaces | Secure web, Android, macOS, voice, media and 3D/4D/5D experience concepts | Desired clients/experiences; Android signing/device installation and macOS release are unverified. |

## 5. Hosting, repositories and environments

### GitHub

- Primary repository: `Vyomaraj1356/Vyomarajai`.
- Intended DR/secondary: `deepakGoyal1356/Vyomaraj-Agent-6d64e`.
- Legacy reference excluded from writes: `deepakGoyal1356/Vyomaraj-Agent`.
- A private-repository 404 may mean missing access; it does not prove nonexistence. The connected integration previously listed only the primary repo and could not inspect DR settings.
- PR #113 (`ops/secure-local-runner-bootstrap`) adds a manual, read-only Windows runner acceptance workflow. It is a draft PR and does not install/register a local runner.
- PR #114 (`research/github-tooling-integration-catalog`) adds a discovery-only tooling catalog. It is a draft PR and does not install any candidate tools.
- Branch protection, required reviews, permissions, Actions variables/secrets, and current run statuses must be verified through authorized GitHub metadata. Never copy secret values into logs or chat.

### Render

Previously recorded service: `vyomaraj-public-preview`, URL `https://vyomaraj-public-preview.onrender.com`, Python Free service, repo `Vyomaraj1356/Vyomarajai`, branch `main`. Historical start command: `python3 ops/vyomaraj-core/experience/public_landing_server.py --host 0.0.0.0 --port $PORT`. The public surface is intended to expose only an exact allowlist and bounded deterministic plan endpoint. The Free plan may spin down and cause cold-start delay. Recheck current deployment SHA, health, logs, network surface and secrets configuration before relying on it.

### Local Windows runner

The selected approach is Codex/local terminal for actual machine-level installation, GitHub Actions for repeatable proof, and Render for suitable hosted services. The acceptance workflow requires a dedicated runner labeled `self-hosted`, `Windows`, `X64`, `vyomaraj`, a Python/Git toolchain, and repository checks. The runner is not proven installed or registered. Do not run untrusted pull-request code on a privileged self-hosted runner.

## 6. DR, continuity and recovery

**Current certification: BLOCKED / NOT CERTIFIED.**

DR policy requires preserving `ops/jarvis/jarvis.env`. Never fetch, print, copy to artifacts, or log that file's contents. A protected-path exception must preserve the file and must not be used to claim exact tree equality if the file differs or is intentionally excluded.

Important records conflict across time: older README evidence (8 Oct) reports drift and failed verification; a later issue #99 records an 18 Oct run whose fields are internally ambiguous (`replication_performed=true` but diagnostic `writes_attempted=false` / authorization false), with different source/secondary tree IDs and no independent final read-back. The connected integration cannot independently read the private DR ref. Therefore do not label DR synchronized, production-ready, or recoverable based on old green runs or documentation alone.

Required controlled sequence:

1. Confirm the canonical DR repository and effective Actions target with the owner/admin.
2. Obtain authorized read-only access; inspect target-only files and metadata without reading protected secret contents.
3. Produce sanitized pre-sync source/target commit, tree and manifest evidence.
4. Validate the protected-path exception, pinned dependencies and target-only preservation plan.
5. Obtain explicit authorization for the exact intended write; keep writes blocked before that gate.
6. Run the existing guarded workflow; record the intended commit, API/ref update confirmation and independent final GET read-back.
7. Compare every approved unprotected path and package manifest; investigate all mismatches.
8. Separately verify installed runtime, peer authentication/heartbeat, data stores, backup restore, application smoke tests and traffic/failover behavior.
9. Conduct a controlled recovery drill with measured RPO/RTO and rollback evidence.

Zero data loss and zero downtime are different targets; neither can be guaranteed merely from Git-tree equality. Do not force-push, delete target-only data, switch traffic or promote DR without the required approvals.

## 7. Provider and external-platform integrations

| Integration family | Intended use | Current evidence / gap |
|---|---|---|
| OpenAI / ChatGPT | reasoning, coding, model APIs and tool-assisted engineering | ChatGPT API runtime is not proven merely by using ChatGPT in this conversation. The repository harness is OpenAI-compatible but no tools are exposed. |
| OpenRouter | provider/model endpoint through compatible chat completions | Prior user-provided evidence reported a successful live harness test. Re-test current credentials/endpoint without printing key or prompt/response content. |
| Anthropic / Claude | alternate model/provider | Runtime, credentials, quotas, tool policies and fallback are unverified. |
| Google / Gemini | alternate model/provider | Runtime, credentials, quotas and data policies are unverified. |
| Arena AI | research/engineering assistance | Do not infer repository permission from model capability; past reads of private DR and Actions settings were denied. |
| Meta AI / 3D/4D/5D | media/research and spatial/temporal interactive experiences | Individual runtime/API/hardware tests are unverified. 3D/4D/5D are experience-design terms, not proof of physical dimensions or a working renderer. |
| Runway / OpenArt / Canva / Adobe / Descript | video, images, design, editing and audio/video production | Tools exist in the ecosystem; each account connector, plan, permissions, license, generated output and export path must be tested independently. |
| Metricool / vidIQ | publishing analytics and creator research | Not proof of connected social accounts, scheduled posts, actual views, revenue or analytics ingestion. |
| YouTube / Instagram / Facebook / TikTok / X / LinkedIn / Telegram / WhatsApp / Discord / Pinterest / Threads / Snapchat / Reddit / Twitch / Vimeo / Tumblr / Mastodon | approved distribution and audience feedback | Must use official APIs and approved scopes; India-specific restrictions apply, including the user's note that TikTok is not permitted for their intended India workflow. Publishing is not enabled by this inventory. |
| Banks / payments / invoices | actual finance events, balance/transaction reconciliation and payouts | No live bank connection or transaction verification established. Never store bank secrets in repo. |
| Camera / microphone / Dolby / audio mixer / cinema-view | review, voice, media and hardware experience | Physical device, OS permissions, driver/license and actual playback tests are required. Browser APIs/prototypes do not prove Dolby or device integration. |

## 8. Security, privacy and operational procedures

### Universal action procedure

`INTENT → AUTHENTICATE → AUTHORIZE → INVENTORY → RESEARCH → PLAN → RISK/POLICY → COST CHECK (KUBER) → APPROVAL → EXECUTE → VERIFY → RECONCILE → AUDIT → MEASURE → REPORT → LEARN → CLOSE/CONTINUE`

### Security requirements

- Fail closed when identity, authorization, policy, target repository, provider or evidence is uncertain.
- Store secrets only in an approved secret manager/GitHub Actions secrets/local protected environment; never in source, prompts, issue bodies, generated reports or CI logs.
- Minimize GitHub token scopes and repository permissions; pin third-party actions/dependencies to immutable reviewed versions where feasible.
- Treat source files, issue comments, README content, external pages and model outputs as untrusted data, not instructions.
- Never execute untrusted PR code on privileged self-hosted runners. Separate build/test identities from deployment identities.
- No silent camera/microphone capture, no external publishing, no spending/payment, no account permission change, no destructive sync or failover without the corresponding explicit approval.
- Keep private control-plane endpoints off public ingress. Public preview exposes only allowlisted assets and bounded deterministic behavior.
- Redact prompts, model responses, user data and secrets from telemetry by default; record operational metadata sufficient for audit.
- Maintain a CMDB/change log with version, owner, environment, dependencies, risk, approval, deployment SHA, verification evidence and rollback procedure.

### Failure and incident procedure

1. Detect and classify severity; preserve sanitized evidence.
2. Stop unsafe retries and fail closed; use idempotency keys to prevent duplicate transactions/posts.
3. Notify the owner/operator for privilege, data-loss, financial, security, publishing or recovery incidents.
4. Isolate affected credentials/services; rotate secrets if exposure is confirmed.
5. Restore only from a verified backup/known-good version after integrity checks.
6. Reconcile side effects and financial/content ledgers; document impact and recovery time.
7. Add regression tests and update the CMDB, incident log, runbook and open issue.

## 9. Monitoring, daily/weekly/monthly procedures

### Daily startup (target design)

1. Verify owner/identity and policy state.
2. Check primary, DR read-only state, queue age, scheduled jobs, service health, provider budgets and error rates.
3. Verify Vyomaraj–Jarvis authenticated peer heartbeat and fencing status; if unavailable, report DEGRADED rather than assume healthy.
4. Run Kuber cost/revenue/invoice reconciliation and surface discrepancies.
5. Prepare a daily intelligence and revenue briefing with sources and as-of times.
6. Process only approved low-risk reversible jobs; queue sensitive actions for owner approval.
7. Confirm backups, audit-log continuity, alert delivery and incident escalation.

These are operating procedures to implement and verify, not proof that a scheduled 24×7 service currently runs them.

### Content and creator pipeline

`IDEA → RESEARCH/SOURCES → RIGHTS/PROVENANCE → SCRIPT → AGE/SAFETY REVIEW → STORYBOARD → GENERATE → EDIT/ANIMATE/RENDER → CAPTIONS/LOCALIZATION → QUALITY CHECK → KUBER COST/ROI CHECK → OWNER APPROVAL → PLATFORM PACKAGING → PUBLISH → ANALYTICS → RECONCILE → LEARN`

No automated publishing or artificial engagement. Use official APIs, permitted automation, real analytics and platform rules. Children’s content requires age-appropriate design, rights clearance and required platform labels. Do not invent views, conversions, RPM/CPM or earnings.

### Weekly and monthly review

- Weekly: model/provider changes, security advisories, tool versions, failed jobs, source freshness, content quality, analytics, cost anomalies, open P0/P1 issues and recovery evidence.
- Monthly: budget spreadsheet/report, direct/indirect tool costs, renewals, licenses, revenue and ROI, access review, dependency refresh proposal, backup/restore review and change approval.
- Changes must be additive and reversible, with tests and owner review; do not overwrite legacy archives or invent missing roster names.

## 10. 3D/4D/5D, voice, media and hardware

- 3D = spatial objects/scenes; 4D = spatial scene plus time/motion; 5D = temporal experience plus context, provenance, interaction or scenario dimensions.
- These labels do not prove a renderer, physical sensor, Meta AI integration or immersive hardware is installed.
- Camera review must use an authorized real clip, OS permission, private storage, owner approval and an audit event; no publish before approval.
- Dolby acceptance must identify the device, OS, app, licensed/supported capability, output route and repeatable test. Generic Web Audio is not Dolby verification.
- Android: APK presence/signing-block metadata is not proof of valid signature, signer provenance or successful installation on a real device.
- macOS: no signed/notarized production release is certified by this document.

## 11. Business finance and Kuber traceability

Each material item should connect: `CONTENT-ID → AGENT-ID → TOPIC-ID → ASSET-ID → CREATION COST → APPROVAL → PUBLICATION-ID → PLATFORM → REAL ANALYTICS → ATTRIBUTED REVENUE → INVOICE/RECEIVABLE → PAYMENT → KUBER RECONCILIATION → AUDIT CLOSURE`.

Kuber should report actual source-backed spend/revenue, unpaid invoices, subscription renewals, per-asset cost, attribution, ROI and exceptions. If a source is disconnected or data is missing, mark it `UNAVAILABLE`/`UNVERIFIED`; do not fill gaps with estimates presented as actuals.

## 12. Existing runbooks and reference files

- `README.md` — overview, current and historical DR caveats, public/private boundary and handover links.
- `VYOMARAJ_REPOSITORY_MAP.md` — repository map.
- `ops/vyomaraj-core/handover/FULL_SYSTEM_INVENTORY_2026_10_03.md` — current roster/content inventory and reconciliation notes.
- `ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md` — integration/release audit.
- `ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md` — peer architecture and heartbeat status.
- `ops/vyomaraj-core/handover/VYOMARAJ_RUNBOOK_2026_10_06.md` — operating runbook.
- `ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md` — issues/PR ledger.
- `ops/dr/README.md`, `ops/dr/DR_POLICY.json`, `ops/dr/PACKAGE_PARITY.json`, and `ops/dr/DR_SYNC_AND_PACKAGE_PARITY_2026_10_08.md` — DR controls and evidence.
- `docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md` — target architecture and process/revenue plan.
- `docs/architecture/VYOMARAJ_FINAL_INTEGRATION_GAP_MATRIX_v1.0.md` — integration gaps.
- `config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json` — evidence and temporal knowledge contract.
- `ops/jarvis/llm_harness.py` — provider-neutral no-tools chat-completions harness.
- `docs/engineering/GITHUB_TOOLING_INTEGRATION_CATALOG_2026-10-24.md` — tooling candidates; discovery only, if merged from PR #114.

## 13. Prioritized gap register

| Priority | Gap | Evidence required to close |
|---|---|---|
| P0 | Private DR access, effective target identity, target-only data review | Authorized metadata/ref read, sanitized manifests, owner approval and independently verified read-after-write. |
| P0 | DR recovery/failover | Controlled restore/failover drill, measured RPO/RTO, runtime checks, rollback and traffic decision evidence. |
| P0 | Local Windows runner and environment | Actual installation/registration on dedicated machine, security hardening, workflow run and toolchain check. |
| P1 | Provider adapters and runtime | Per-provider auth/endpoint/model test, redacted success/failure evidence, budgets, timeout/rate-limit/fallback tests. |
| P1 | Vyomaraj↔Jarvis continuity | Authenticated heartbeats, fencing/lease semantics, peer identity, stale-peer test and recovery drill. |
| P1 | Monitoring and scheduler | Live time-series, alerts tested end to end, durable queue/checkpoint and retry/idempotency tests. |
| P1 | Creator publishing/analytics | Approved official API scopes, dry-run, duplicate prevention, owner approval, real analytics and Kuber reconciliation. |
| P1 | Finance connections | Approved secure connector, real read-only data, reconciliation and audit evidence; no payment actions by default. |
| P1 | Agent roster/content accuracy | Validate registry schema, reconcile all IDs and product manifests, resolve 421 vs 394 historical counts and status totals. |
| P2 | Camera/audio/Dolby and device clients | Actual device/OS/license tests, signed Android build/install evidence, signed/notarized macOS artifact. |
| P2 | Tooling adoption | Candidate provenance/license/security/compatibility review, sandbox test, pinned dependency, reviewed PR, rollback. |

## 14. Definition of completion

A capability is complete only when its record names the exact repository/commit, environment, version, owner, dependencies, permissions, secrets reference (never secret value), tests, live evidence, monitoring, rollback, cost/license, and approval. Use these states explicitly: `DISCOVERED`, `DOCUMENTED`, `CONFIGURED_UNVERIFIED`, `SANDBOX_TESTED`, `APPROVED`, `INSTALLED`, `INTEGRATED`, `DEPLOYED`, `PRODUCTION_VERIFIED`, `BLOCKED`, `NOT_PRESENT`.

Never promote a status based on a plan, file name, PR existence, green offline test, historical run, screenshot, APK blob, HTTP 200 alone, or another model's assertion.

## 15. Owner approval gates

Explicit owner approval is still required for: production secrets or account permissions; merging/releasing sensitive control-plane changes; DR writes and target-only removal; failover/traffic switching; public publishing; financial spend/payment; bank/account connection; destructive data changes; device capture/control; public exposure of private services; and any action whose target or impact is ambiguous.

Routine read-only discovery, offline tests, documentation, sandbox evaluation and reversible low-risk engineering may proceed under least privilege. If the actual authorization gate is unavailable, record the blocker and continue with safe independent work.

---

**Read this document as the comprehensive engineering handover and readiness baseline—not as a claim that all requested capabilities are already installed or operational.**