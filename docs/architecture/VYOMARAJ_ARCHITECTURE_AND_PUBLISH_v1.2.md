# Vyomaraj AI Agent OS — architecture and publish alignment v1.2

**Date:** 7 October 2026
**Status:** Target architecture plus repository implementation assessment. This is not a claim of connected or deployed production services.

## 1. Authority and peer model

```text
Owner (ultimate authority; step-up for privileged changes)
  └─ ShriYantra private control plane (identity, policy, secret references, approvals, audit)
       ├─ Bharath / Vyomaraj — peer core
       ├─ Laxman / Jarvis — peer core
       └─ Hermes — integrity, audit, recovery witness
            └─ authorized agent and sub-agent mesh
                 └─ approved content/data workflows
                      └─ owner-approved publication and financial reconciliation
```

Bharath/Vyomaraj and Laxman/Jarvis have equal **authorized** capabilities under the same control-plane policy. Neither is the root authority. Peer parity does not create self-approval, permission inheritance, root access, or permission to override the owner. Hermes may attest to integrity and state transitions but cannot approve privileged actions. Arena and all external content remain untrusted task/execution surfaces.

## 2. Shared policy and knowledge fabric

- ShriYantra's Universal Knowledge Fabric owns the canonical Universal Knowledge Evolution policy. Current and future categories, agents, sub-agents, topics, content, chapters, and products inherit by a single reference; individual agent records do not duplicate it.
- The nine temporal layers, evidence classes, uncertainty, source lineage, as-of times, and correction history remain visible at claim level. Forecasts, scenarios, and speculation are never reported as facts.
- The Panch-Brother model exposes five shared behavioral domains (Matiman, Shrutiman, Ketuman, Gatiman, Dhritiman) through a local read-only metadata resolver. These labels are not tools, privileges, provider access, or runtime claims.
- Access filters apply before retrieval. Retrieved external content is data, not authority. Context assembly preserves source conflicts and missing evidence; memory promotion requires validation and provenance.
- The shared policy and local resolver are a reference contract. Production enforcement remains `NOT_VERIFIED` until a trusted Harness/CAG loads it on every applicable request and passes end-to-end tests.

Relevant artifacts: `config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json`, `config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml`, `ops/shriyantra/knowledge_evolution.py`, and `ops/vyomaraj/capability_fabric.py`.

## 3. Agent structure and financial control

The checked-in current registry remains **13 categories / 128 counted sub-agents / 421 historical reported products**. The owner-provided target is **14 / 153 / 421** with +6 FOOD, +5 EDU, and a Real Estate category containing 14 sub-agents. Do not update the canonical counts until all exact IDs/names and provenance are reconciled across the source, rules, builders, tests, viewers, gates, and current docs. Preserve the historical registry and archives. The 421 figure remains a historical aggregate, not a current deduplicated product inventory.

KUBER is the financial controller for both peer cores, not a technical root authority. The target trace is:

```text
source/content version → authorized agent/task → owner-approved release → publication ID
 → gross receipts/fees/refunds/costs → net ledger event → reconciliation → append-only audit
```

No live payment/accounting connection or end-to-end revenue trace is verified. The local finance/planning features do not establish a KUBER production controller.

## 4. Owner-authorized change and release lifecycle

1. Authenticate the owner through the trusted control plane; bind a fresh step-up approval to the exact action, object, scope, and target hash.
2. Validate least-privilege grant, policy version, security epoch, freshness, replay protection, idempotency key, and dependency preconditions.
3. Build a transaction plan with before/after state, affected routing/content/knowledge/process/financial references, peer impact, recovery point, and immutable audit event.
4. Stage the change and validate all dependent artifacts. No self-elevation or root-owner authority is possible.
5. Apply atomically only when the runtime store and all required update adapters are present. Coordinate peer state with fencing and conflict preservation; no timestamp-only last-writer-wins or blind overwrite.
6. Verify post-state, hash chain, peer replication/read-after-write, health and business probes. Roll back to a verified point on any mismatch.
7. Require a separate owner decision for production publishing, spending, deployment, failover/failback, or destructive actions.

Current code supports a signed owner-approval validator and plan-only local change validation. The repository does **not** contain an authenticated transactional registry API, dependency updater, peer mutation protocol, production audit store, or rollback/recovery service. `agent-change.sh apply` and process/recovery mutations are blocked; this is intentional.

## 5. Product and publication path

The intended content workflow is research → claim/provenance validation → creation → rights/privacy/cultural review → owner approval → controlled publication → permissioned analytics → settled revenue and reconciliation → learning/correction. A preview gate verifies local repository checks only; it never deploys. No social provider, publishing account, payment gateway, audience analytics, or production AI model is verified as connected.

Web, Android, and macOS are separate release targets. A static PWA is not a native Android/macOS app. Android signing-block presence is not cryptographic validation or signer provenance; native source projects and real-device install evidence are absent/unverified. Every public output must remain owner-approved and privacy-safe.

Location is off by default. No arbitrary phone tracking, covert monitoring, consent bypass, or legal/security bypass is part of this architecture.

## 6. Resilience and DR

Bharath/Laxman synchronization, heartbeat, fencing, immutable audit, verified backups, restore, failover/failback, rollback, and recovery are target capabilities. Current resilience configuration has runtime activation and automatic failover/failback disabled. No authenticated production peer heartbeat, application/database replication, traffic switch, measured RPO/RTO, or production restore is verified.

The latest scheduled DR run reported matching tracked Git trees at one point in time, with no traffic switch. This is not runtime DR. Issue #6 remains OPEN/P0 pending effective target identity, authorized target-only data review, owner/admin approval, authorized verification, and read-after-write evidence.

## 7. Publish decision

- **Repository/local preview:** the public shell and bounded deterministic sandbox planner may be tested locally; the planner returns ephemeral results only and is not deployed on static GitHub Pages.
- **Public production:** **BLOCKED / NOT VERIFIED** until identity and authorization, runtime dependencies, content/permission gates, peer/DR evidence, app release provenance, owner approval, rollback, and production end-to-end evidence pass.
- Do not treat version labels as a gate for this task. Do not claim a product, agent, provider, heartbeat, publication, revenue event, or DR capability is live from metadata/configuration alone.

See [`VYOMARAJ_FINAL_INTEGRATION_GAP_MATRIX_v1.0.md`](VYOMARAJ_FINAL_INTEGRATION_GAP_MATRIX_v1.0.md), [`docs/vyomaraj/context/VERIFICATION_RULES.md`](../vyomaraj/context/VERIFICATION_RULES.md), and [`docs/vyomaraj/state/CURRENT_STATE.md`](../vyomaraj/state/CURRENT_STATE.md).
