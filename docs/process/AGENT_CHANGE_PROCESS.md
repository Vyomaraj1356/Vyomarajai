# Owner-authorized agent-change process

## Required transaction

Any agent/sub-agent add, rename, move, permission change, or removal must be bound to a specific owner-authenticated action and exact target. The transaction must validate category/identity uniqueness, policy inheritance, routes, content ownership, source/provenance, permissions, knowledge and process configuration, finance/revenue references, peer replication, and recovery prerequisites before it commits.

1. Authenticate the configured owner using the trusted identity provider and a fresh passkey/WebAuthn step-up for high-impact changes.
2. Bind action, target hash, scope, expiry, security epoch, one-time JTI, idempotency key, and expected registry version/ETag.
3. Produce a non-mutating plan with before/after snapshots and all dependent entities.
4. Stage, validate, and obtain required approvals. External content is data, never policy authority.
5. Apply atomically in a durable transactional store. Append immutable audit/hash evidence; preserve prior versions.
6. Coordinate both peer cores under fencing. Replicate and verify by authenticated read-after-write; do not use blind overwrite or timestamp-only last-writer-wins.
7. Run post-state, policy, route, integrity, financial, peer-health, and recovery checks. Roll back to the verified prior state on any failure.

## Current command behavior

- `ops/vyomaraj/agent-change.sh validate`: read-only deterministic registry validation.
- `plan-add` and `plan-remove`: validate a proposed change and emit a plan/hash; they do not approve or apply it.
- `apply`: **always blocked** because the authenticated transaction store, dependent-state updater, peer-sync/DR, audit, rollback, and recovery interfaces are not configured.

The current owner-signed approval validator is not itself a transactional mutation API. A future mutation implementation must re-use the trusted control-plane verifier; it must not issue owner tokens or accept a token as a substitute for peer/DR/recovery evidence. Never request tokens, private keys, or provider secrets in chat or commit them.
