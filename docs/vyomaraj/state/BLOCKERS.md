# Current blockers

| Area | Status | Evidence needed to unblock |
|---|---|---|
| Owner-supplied taxonomy additions | `BLOCKED` | Reconcile exact category, IDs, names, ownership, provenance, and count basis for 6 FOOD + 5 EDU + 14 Real Estate entries against historical and current sources. Then update builder, registry, dependent tests, UI, gates, and current docs in one reviewed change. |
| Verbatim master script archive | `BLOCKED` | Add the complete owner-supplied 34-section text as a separate immutable file; do not replace it with this context summary. |
| Owner identity / authorization runtime | `NOT_CONFIGURED` | Trusted issuer, key management, owner role source, security epoch, persistent shared JTI replay store, and an authenticated runtime API. Never place secrets in Git or chat. |
| Transactional agent/sub-agent changes | `NOT_IMPLEMENTED` | Atomic change store, exact owner-action binding, dependent route/content/knowledge/process/financial updates, idempotency, peer coordination, immutable audit/hash, rollback and recovery tests. The current `apply` command intentionally blocks. |
| Bharath–Laxman peer connection | `NOT_CONFIGURED` | Confirm exact peer repository/service identity, authenticated bidirectional protocol, heartbeat freshness/replay protection, fencing, conflict handling, and owner-approved activation. |
| DR and Issue #6 | `OPEN/P0` | Authorized secondary metadata/main-ref read, target-only data review, current target confirmation, authorized verification, and read-after-write evidence. Git-tree equality alone is insufficient. |
| Automatic failover/failback | `DISABLED` | Runtime peer proof, fencing, integrity/freshness/business probes, owner step-up, traffic control, measured rollback/recovery and DR test evidence. |
| Providers and social platforms | `NOT_CONNECTED` | Owner-selected provider, approved terms/data region, server-side credentials, least-privilege scopes, authenticated end-to-end test, revocation and audit. |
| KUBER revenue controller | `NOT_VERIFIED` | Shared owner-approved financial event ledger, idempotent event capture, gross/fees/refunds/net treatment, reconciliation and audit across both peers. No payment gateway or settled revenue is proven by repo metadata. |
| Web/Android/macOS release | `NOT_VERIFIED` | Owner-approved production build, Android signer provenance and real-device installation, native macOS source/build/signing, release review, rollback, and production runtime evidence. |
| Production knowledge enforcement | `NOT_VERIFIED` | Trusted Harness/CAG loads the shared versioned policy for every applicable entity; claim-level provenance/future guard tests, correction/recovery behavior, and runtime evidence. |
| Public market/revenue validation | `NOT_VALIDATED` | Owner-approved prospect contact and offer, permitted delivery, customer feedback, settled payment, costs/refunds, and reconciliation. No forecast counts as revenue. |
