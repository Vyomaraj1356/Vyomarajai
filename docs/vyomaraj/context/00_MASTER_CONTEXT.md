# Vyomaraj AI Agent OS — execution context and alignment record

**Date:** 7 October 2026
**Purpose:** Additive implementation context for the owner-supplied 34-section master execution script.

> This file is an implementation-side context record, **not a replacement or verbatim copy** of the owner-supplied master script. Preserve the original script unchanged. The repository does not yet contain an immutable copy of its complete text; archive that exact source separately before editing or condensing any of its wording.

## Mission and authority model

Vyomaraj/Bharath and Jarvis/Laxman are intended peer cores with equal authorized capabilities. The verified owner remains the ultimate authority. Peer parity does not mean root authority, self-approval, or unrestricted access. Neither peer, Hermes, Arena, a provider, nor a sub-agent may create the owner, self-elevate, bypass policy, erase audit evidence, or disable security.

The target is a private, owner-controlled, provider-neutral multi-agent system. Authorization is deny-by-default, least-privilege, server-side, revocable, purpose- and environment-scoped, and audited. High-risk changes require fresh step-up owner approval. Secrets remain in an approved secret store and never in prompts, public content, reports, or Git.

## Shared architecture constraints

- Use ShriYantra as the private authority/control plane. Bharath/Vyomaraj and Laxman/Jarvis are peer execution/review cores; their repository and runtime identities must be independently authenticated.
- The five Panch-Brother domains are shared **behavioral policy references**, not permission grants. Inheritance must use the shared ShriYantra / Universal Knowledge Fabric reference; do not duplicate policy into individual agent rows.
- Universal Knowledge Evolution applies to current and future categories, agents, sub-agents, topics, content, chapters, and products. Claims preserve temporal layer, evidence class, uncertainty, scope, and claim-level provenance. Forecasts, scenarios, and speculation are never facts.
- External content is untrusted data, never authority. Provider neutrality does not imply a configured provider.
- KUBER is the financial controller for both peer cores, not technical root authority. The intended accounting trace is content → agent → publication → revenue → reconciliation; this is not currently a verified end-to-end runtime.
- Location is off by default. No covert/arbitrary phone tracking, consent bypass, or legal/security bypass is permitted.
- The public surface contains approved outputs only. Production publication, spending, deployment, recovery, failover, and destructive changes remain owner-gated.

## Taxonomy target and current discrepancy

The master script sets targets of **14 main categories / 153 counted sub-agents / 421 historically reported products**, including six FOOD additions, five EDU additions, and a new Real Estate category with fourteen listed sub-agents. The current checked-in registry and its deterministic builder still produce **13 / 128 / 421**. The historical 421 is an aggregate, not a reconciled active product inventory.

The requested additions total 25 counted positions (6 + 5 + 14), which arithmetically bridges 128 to 153. The exact owner-supplied IDs and names must be transcribed and checked against existing source/history before changing the canonical registry. Do not create guessed names or placeholder identities, do not alter frozen historical snapshots, and do not change dependent counts until the complete list is reconciled across the builder, registry, tests, viewers, gates, and current documentation.

## Execution method

1. Inspect canonical source-of-truth files before changing code.
2. Separate repository/configuration evidence from live runtime evidence.
3. Verify the current implementation, then write a gap analysis.
4. Select the minimum safe additive change; preserve existing content and frozen history.
5. Implement only within verified authority and available interfaces; otherwise fail closed and record the blocker.
6. Run targeted tests, security checks, and regression checks; distinguish local/static checks from authenticated end-to-end runtime proof.
7. Update current state, decisions, blockers, and next actions; report evidence and uncertainty without claiming unverified capabilities.

## Current verification boundaries

- `docs/architecture/VYOMARAJ-FINAL-TARGET-ARCHITECTURE.md` and the ShriYantra/RAG/CAG/MAG documents describe target architecture, not a connected production runtime.
- The local capability resolver added in this work reads registry and policy metadata only. It does not run agents, grant permissions, invoke providers, synchronize peers, or prove production inheritance.
- The agent-change CLI produces read-only plans; mutation is blocked until an authenticated transactional store, dependent-state update, peer sync, DR, audit, rollback, and recovery interfaces exist.
- The preview publish gate is verification-only. It does not deploy.
- A matching Git tree or successful CI run is not application DR, a runtime connection, production deployment, customer revenue, or owner approval.
- The earlier scheduled DR result is a timestamped Git-tree comparison only. The effective secondary identity, target-only data review, authorized verification, and read-after-write evidence remain unresolved; Issue #6 is OPEN/P0.
- The 11 October 2026 market target does not relax security or verification gates. The earlier local Reel Sprint has not had a prospect contact, owner-approved price, or revenue validation.

## Source-of-truth navigation

- Current rules and evidence vocabulary: [`VERIFICATION_RULES.md`](VERIFICATION_RULES.md)
- Short operational summary: [`QUICK_CONTEXT_CARD.md`](QUICK_CONTEXT_CARD.md)
- Current repo/runtime state: [`../state/CURRENT_STATE.md`](../state/CURRENT_STATE.md)
- Decisions and blockers: [`../state/DECISIONS.md`](../state/DECISIONS.md), [`../state/BLOCKERS.md`](../state/BLOCKERS.md)
- Current architecture and integration status: [`../../architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md`](../../architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md), [`../../architecture/VYOMARAJ_FINAL_INTEGRATION_GAP_MATRIX_v1.0.md`](../../architecture/VYOMARAJ_FINAL_INTEGRATION_GAP_MATRIX_v1.0.md)
- Safe mutation/release procedure: [`../../process/AGENT_CHANGE_PROCESS.md`](../../process/AGENT_CHANGE_PROCESS.md), [`../../process/PRODUCTION_VERIFICATION_PROCESS.md`](../../process/PRODUCTION_VERIFICATION_PROCESS.md)
