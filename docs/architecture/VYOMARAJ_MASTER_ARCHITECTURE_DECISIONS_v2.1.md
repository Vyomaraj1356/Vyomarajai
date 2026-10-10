# Vyomaraj AI Agent OS — Master Architecture and Decision Brief v2.1

**Brand:** Vyomaraj — The King of the Sky  
**System ID:** `VYOMARAJ-AI-STUDIO`  
**Status:** target design for review; not a production deployment attestation.

## Executive decision
Adopt a private, owner-controlled, provider-neutral AI federation. One owner root governs the ShriYantra private foundation; Vyomaraj/Bharath orchestrates and Jarvis/Laxman executes bounded, authorized work. Kuber governs finance; Hermes coordinates integrity/recovery but is not a third root. Keep the original Vyom portrait in a separate brand panel so the technical architecture and ShriYantra Bindu remain unobstructed.

## Control chain
`OWNER ROOT → SHRIYANTRA → VYOMARAJ/BHARATH ↔ JARVIS/LAXMAN → POLICY + HARNESS → AUTHORIZED EXECUTION → VERIFICATION → AUDIT → RECOVERY`

- Owner remains ultimate root. Voice is optional, never the only authorization factor.
- Public surfaces get approved outputs only; private prompts, secrets, databases, and audit logs remain internal.
- Peers share one authorization contract; neither peer may self-grant root authority.
- External providers and partners are replaceable capabilities, not owners of identity, policy, memory, knowledge, or recovery authority.

## Functions and feature scope
### ShriYantra private foundation
Identity/authentication/authorization, owner roles, policy, consent, privacy, prompt/context registry, LLM + harness, model routing, evaluations, RAG/CAG/MAG, short/long-term memory, vector and graph knowledge, provenance, KMDB, version history, MCP allowlist, signed A2A, sandboxed execution, durable jobs, event/task engines, queues, audit, observability, and resilience.

### Vyomaraj/Bharath — orchestration
Intent parsing, task decomposition, research, source triangulation, MECE/SCQA/Socratic/falsification/second-order/OODA/red-team strategy, context assembly, provider/agent selection, risk/cost checks, QA, owner decision support, measurement, and controlled improvement.

### Jarvis/Laxman — execution and recovery
Bounded approved actions, idempotent durable jobs, tool coordination, heartbeat/health monitoring, incident reports, rollback, backup/restore playbooks, recovery rehearsals, and integrity evidence.

### Domain knowledge and agents
Education/civilization, Hindu knowledge/history/languages, Bhakti/Shakti, literature/music/culture/podcasts, food, agriculture/living world, travel, sports, entertainment, research, coding, browser/search, data/analytics, SEO/marketing/sales, business/real estate, collaboration, life/health, finance, and media creation. Knowledge sequence: Origin → Oldest Sources → Historical Evolution → History → Present/Current State → Trends → Future Scenarios. Label evidence as verified fact, historical record, current verified state, trend, forecast, scenario, speculation, or traditional belief.

### Media and monetization
Research → fact-check → rights/safety → edit → captions/metadata → owner approval → publish → analytics/attribution → Kuber reconciliation → learn. Potential revenue surfaces: YouTube and eligible social channels; music/audio/podcasts; books/literature; courses/research/digital products; licensing/syndication; sponsorship/brand deals; affiliate; creator and AI partnerships. Monetization and account permissions must be proven, never assumed.

### Kuber finance
Double-entry ledger, revenue events, payout reconciliation, invoices/costs/taxes, budget/runway, ROI, campaign/product profitability, forecast-vs-actual, and anomaly alerts. Financial writes require explicit authorization, idempotency, and audit records.

### Security and resilience
Zero Trust, least privilege, server-side secrets, prompt-injection defenses, untrusted content treated as data, provider isolation, signed artifacts, deny-by-default MCP, append-only audit target, metrics/logs/traces, canary and rollback, encrypted backups, replica fencing/epochs, checksums, read-after-write, restore drills, incident response, and measured RPO/RTO. No automatic failover/failback or destructive synchronization until repository identity, parity, fencing, and recovery tests pass.

## Architecture decisions — pros, cons, guardrails
| Decision | Pros | Cons / risks | Guardrail |
|---|---|---|---|
| Provider-neutral AI fabric | Less lock-in; optimize quality, cost, privacy, latency | More adapters, evaluation, prompt variance | Standard provider contract; eval every model/provider |
| Two peer cores | Separates planning from execution; clearer recovery roles | Split-brain, duplicated jobs, state divergence | Signed peer contract, fencing/epochs, idempotency, owner-only root |
| ShriYantra foundation | Central policy, memory, identity, knowledge, audit | Foundation can become critical dependency | Isolation, least privilege, fail-closed tests, versioned policy |
| MCP + signed A2A + sandbox | Extensible tools and collaboration | Tool abuse, prompt injection, confused deputy | Allowlist, scoped tokens, sandbox limits, signed delegation |
| Owner approval gates | Lower legal, financial, reputational, destructive-action risk | Slower throughput; approval bottlenecks | Mandatory for public publishing, finance, destructive changes, DR |
| RAG/CAG/MAG + KMDB | Grounding, provenance, continuity | Stale/poisoned retrieval, access leakage, storage cost | ACL filtering, source trust labels, freshness, poisoning tests |
| Kuber finance | ROI visibility and payout reconciliation | Depends on trustworthy platform and payout data | Auditable events; no fabricated revenue or auto-spend |
| Self-improvement loop | Controlled upgrades and measured learning | Regressions and supply-chain risk | Sandbox → evaluation → approval → canary → monitor → rollback |
| Separate portrait panel | Preserves original brand artwork without hiding technical core | More than one visual artifact to maintain | Keep technical and brand editions version-aligned |
| Auditable recovery | Helps prove restore and investigate failures | Cost, retention and privacy overhead | Retention/access policy; measure RPO/RTO rather than assume |

## Operating strategy
1. Truth first: separate verified state, target design, inference, and blocked dependencies.
2. One command contract: declare role, inputs, permissions, side effects, expected outputs, validation, rollback, and audit event.
3. Least privilege: scope provider credentials and tool tokens; keep private data out of public content lanes.
4. Quality gates: facts, safety, rights, privacy, cost, and policy before publication or external action.
5. Economic discipline: Kuber checks budgets and measures ROI; no unapproved spend.
6. Recoverability: restore proof and replica integrity before declaring DR ready; matching Git trees do not prove runtime/database recovery.
7. Controlled learning: observe → sandbox → evaluate → threat/cost test → owner approve → canary → monitor → rollback.
8. Portfolio monetization: small compliant experiments; no fake engagement, spam, or rights-infringing content.

## Production gates
- **G0 Inventory:** primary/DR repositories, branches, data stores, media, providers, domains, runtimes reconciled.
- **G1 Security:** secret/history review, least privilege, threat model, dependencies, owner approval.
- **G2 Quality:** required CI and offline tests green for the exact release commit.
- **G3 Provider:** approved model/provider, secret manager, limits, timeout/retry/redaction, non-sensitive smoke test.
- **G4 Tools:** allowlists, sandbox, signed delegation, idempotency, side-effect ledger, high-risk approvals.
- **G5 Data:** backup restore, checksums, read-after-write, replica parity, fencing/conflict tests.
- **G6 DR:** measured recovery exercise and approved runbook; no automatic failover until proven.
- **G7 Content/revenue:** rights, platform policy, attribution, payout reconciliation, owner approval tested.
- **G8 Release:** reviewed PR, merge/deployment commit, smoke test, monitoring, rollback, handover.

## Known evidence boundaries
PR #61 was last known to be a draft, with provider/model/credential configuration and production smoke testing outstanding. The latest known DR evidence showed unresolved access/parity differences. A green engineering check alone does not prove every test, provider, production runtime, social integration, or recovery path is connected. This diagram is a target design, not proof of implementation.

## Reference images
Six saved historical references were recovered and included in the reference bundle. The original standalone Vyomaraj portrait was reused as-is, resized/compressed only for embedding. The detailed brand edition is delivered as SVG and PNG; this repository diagram is the portrait-free technical edition so the architecture remains legible.

## Release decision
Approve this as the target architecture for review, **not** as production readiness. Keep provider actions, public publishing, financial writes, destructive changes, DR sync, failover, and failback disabled until their authorization and verification gates pass.
