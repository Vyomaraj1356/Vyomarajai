# Production verification and release process

## Claim rule

A production capability is `VERIFIED` only after an authenticated end-to-end test demonstrates the exact behavior in the intended environment, with the relevant identity, authorization decision, target, as-of time, before/after state, audit record, failure path, and owner approval. Local config, documentation, a Git commit, CI, a preview, or a matching Git tree is not sufficient.

## Gates

1. **Source:** verify the exact reviewed commit, provenance, change set, and frozen-history boundaries.
2. **Identity/security:** confirm owner/peer identities, key lifecycle, least-privilege scopes, step-up, replay protection, revocation, secret handling, and audit.
3. **Runtime:** exercise the real API/provider/store path, all permission boundaries, denial paths, rate limits, idempotency, and safe failure handling.
4. **Data/knowledge:** verify pre-retrieval access filtering, provenance, evidence labels, future-claim guard, memory correction/deletion, and shared-policy inheritance.
5. **Change transaction:** verify atomic dependency updates, two-peer fencing/synchronization, conflict preservation, integrity hashes, rollback, recovery, and read-after-write.
6. **DR:** verify the exact secondary identity, target-only data, authorized replication, application/runtime parity, independent restore, traffic/failback process, and measured RPO/RTO. Git replication alone is not DR.
7. **Clients:** build web/Android/macOS from reviewed source; prove signing provenance, device install, platform-specific controls, privacy, accessibility, and rollback.
8. **Business:** validate owner-approved offer, customer delivery, platform/payment scopes, settled receipts, fees/refunds/costs, and KUBER reconciliation. Forecasts are not revenue.
9. **Release:** obtain separate owner approval; canary, monitor, retain an immutable pre-release checkpoint, and preserve an immediate rollback route.

## Current release status

Repository/static validation can pass independently. Production remains `BLOCKED / NOT VERIFIED` until every applicable gate passes. The current preview gate is verification-only and performs no deployment; process restart and DR mutation commands remain blocked. Version reconciliation is not an acceptance gate for this alignment task.
