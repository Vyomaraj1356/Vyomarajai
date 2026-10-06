# IMPLEMENTATION GATES

A green architecture file is not a production claim.

## Gate 1 — Core
- Shared API exists.
- Vyomaraj core owns orchestration.
- Jarvis owns workflow coordination.
- ShriYantra owns retrieval/context/memory/harness controls.

## Gate 2 — AI
- At least two independent provider adapters work.
- Provider health checks work.
- Context survives provider fallback.
- No provider key reaches a client.

## Gate 3 — Data
- Primary + replica verified.
- Vector memory backup/restore verified.
- Object storage backup/restore verified.
- Audit logs recoverable.

## Gate 4 — Clients
- Web, Android and macOS authenticate against the same API.
- Same task produces equivalent core behavior across clients.
- No client contains an independent agent registry.

## Gate 5 — DR
- Backup test passes.
- Restore test passes.
- Read-after-write test passes.
- Failover test passes.
- Failback test passes.
- Runtime state, queues, jobs, memory and audit state are included.

## Gate 6 — Security
- Secrets server-side only.
- Owner authorization enforced.
- Public boundary verified.
- Audit trail verified.

## Gate 7 — Final authentication
Only after Gates 1–6:
- voice
- biometric
- owner passcode

## Production status rule

Production-ready = all gates green + actual deployment verification.

Architecture presence alone is not production readiness.
