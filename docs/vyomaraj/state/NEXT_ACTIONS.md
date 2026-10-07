# Next actions — ordered, owner-gated

## Live deployment/PR gate — 7 October 2026

The allowlisted sandbox planner preview is running on port 5310 with an exact public-asset allowlist and bounded deterministic `/api/plan` for two local experiences; responses are ephemeral, with no AI/provider, visitor-data persistence, or privileged writer. This is not GitHub Pages or production. Pages remains public and built from `main:/`.

- **PR #39:** OPEN/DRAFT, UNSTABLE; diagnostics and offline checks failed.
- **PR #41:** OPEN/non-draft, CLEAN; listed checks passed, but PR-event `verify-or-sync` was skipped and no review decision is recorded. It combines DR and preview scope; main updates may trigger the conditional DR workflow. Issue #6 remains OPEN/P0 because the effective secondary and target-only data are unconfirmed.
- **PR #42:** OPEN/DRAFT, DIRTY; engineering-foundation check passed, but it has no review decision. It proposes 14/153/421, yet its remote `historical_totals` field is 13/133/421, so it must not be merged until the frozen 13/128/421 baseline is preserved and the difference is explained.

**Safe sequence:** keep all three open; validate/fix #39 and #42 on their owners' branches, preserve the original source snapshots, run the complete suite on the reconciled target, and review #41's DR side effects separately from public Pages publication. No merge, workflow dispatch, or production installation is authorized by a generic request to integrate; require an exact owner-approved release step after its blockers clear.

## Local security/code update — 7 October 2026

A concrete local vertical slice now addresses the previously confirmed unsafe studio writer:

- `studio_server.py` and the availability gateway default to IPv4 loopback and reject non-loopback binds. The research worker is opt-in.
- Research enqueue/review and privileged approval/change routes call the fail-closed owner guard using request-scoped Bearer tokens bound to a canonical action + payload; no process-wide token fallback is used by the web handler.
- Approval decisions update a private SQLite queue, consume one JTI, store the record, and append a locally verified hash-chained event in one transaction. Tampered history halts future decisions. No notification, agent handoff or publishing occurs.
- Upgrade planning/rollback output is explicitly plan-only; `upgrade-controller.sh --execute` exits blocked before snapshot/test/process/repository mutation.
- The real token issuer/key/owner subject/security epoch/replay directory is not configured here. Valid privileged requests therefore remain unavailable; unit tests use a mock verifier for handler wiring, and optional real Ed25519 tests use disposable test keys only.

This is a secured **local code slice**, not a production deployment or a live AI/provider-backed agent.

1. **DONE — 7 October 2026:** the bounded local sandbox planner UI/API is implemented and live on the session preview; valid requests were HTTP-checked, private paths denied, and no AI/provider, persistence, or writer side effect observed. Full offline verification passed: 569 Python tests / 15 suites, 15 Node checks, 30 builders, 0 failures. This does not change production deployment or owner-gated release status.
2. Obtain/verify the complete owner-supplied FOOD-S04…S09, EDU-S16…S20, and Real Estate category/sub-agent list. Compare against historical sources, then reconcile 14/153/421 in the builder and every current dependent test, gate, viewer, and doc. Preserve historical snapshots.
3. Add the full 34-section master script verbatim as a separate immutable file; retain the context summary and existing architecture docs.
4. Keep `agent-change apply`, service restart, failover, failback, publish, spending, and production deployment blocked. The approval desk has local transactional persistence, but agent registry transactions, production identity/revocation, peer fencing, DR replication, external audit anchoring, executable rollback and recovery remain unimplemented or unverified.
5. Resolve Issue #6 through authorized GitHub access: confirm effective secondary identity, review target-only data, obtain owner approval, perform only authorized verification, and require read-after-write evidence. Do not use a private 404 as proof of absence.
6. After peer identity and owner authorization are confirmed, implement heartbeat in read-only/shadow mode first; prove replay protection, freshness, fencing, alerting, conflict preservation, and split-brain safety before any failover.
7. Define and implement KUBER's owner-approved event/accounting contract, then validate content → agent → publication → settled revenue → reconciliation without representing a forecast as cash.
8. **Local approval slice built; runtime configuration still blocked.** The studio now has request-scoped owner-token enforcement and a single-host persistent approval/audit path. Next, only after the owner provisions a trusted issuer/key/replay configuration out of band, run a real signed-token end-to-end rehearsal. Require separate owner approval before external providers, payments, location, publishing, or production deployment.
9. Build/verify web, Android, and macOS surfaces from reviewed source. Keep Android signer provenance, device installation, and native macOS evidence separate from PWA/site evidence.
10. Re-run full offline and regression suites after taxonomy/runtime changes; update this state file from observed output and preserve dated evidence/history.
