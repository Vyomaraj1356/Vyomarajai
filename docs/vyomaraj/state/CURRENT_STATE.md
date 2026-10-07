# Vyomaraj — current state

**Updated:** 7 October 2026 · **Branch:** `arena/a83291a3-vyomarajai`

## Repository and scope

The session worktree already contained extensive staged/unstaged historical work and untracked files before this alignment pass. Changes have been kept additive and scoped; no reset, clean, broad staging, commit, push, or branch change was performed. GitHub Pages is served from `main`; this working branch is not deployed.

## Canonical counts

| Measure | Current checked-in canonical structure | Master-script target | Status |
|---|---:|---:|---|
| Main categories | 13 | 14 | `BLOCKED`: exact new category/roster mapping must be reconciled before changing canonical data. |
| Counted sub-agents | 128 | 153 | `BLOCKED`: target implies +25 additions (6 FOOD + 5 EDU + 14 Real Estate); preserve current and historical values until the named source rows are reconciled. |
| Historical reported products | 421 | 421 | Historical aggregate only; active product identity/ownership is unreconciled. |

No taxonomy changes have been made. The pinned historical source remains unmodified.

## Implemented in this alignment pass (local scope only)

- Added one shared Panch-Brother behavioral capability reference and a read-only local resolver at `ops/vyomaraj/capability_fabric.py`.
- Added registry/index metadata that points to the shared policy once; individual agent entries do not receive duplicated capability lists or permissions.
- Added static architecture inspection, plan-only agent-change validation, read-only process controls, and a final readiness gate. Registry `apply`, process restart, failover, and failback remain blocked.
- Disabled resilience runtime activation, automatic failover, and automatic failback in the unconfigured target YAML.
- Added context/state/process and integration-gap documents. The supplied 34-section script itself has not been copied verbatim into the repository; `00_MASTER_CONTEXT.md` is clearly labeled as an additive summary, not a replacement.
- Implemented a session-scoped sandbox planner page and exact-route HTTP endpoint: only Bhakti-Shakti and Roots & Pairings packs are accepted; requests/responses are bounded; the deterministic plan is ephemeral with no model/provider/external-network call, visitor-data persistence, owner queue, or privileged writer. Added HTTP/security/non-mutation regression tests and a home-page link. This demo is not GitHub Pages or a production deployment.

## Runtime status

- Agent registry is metadata, not running agents.
- `capability_fabric.py` is a local metadata resolver; production policy enforcement is `NOT_VERIFIED`.
- **Local security remediation implemented:** `studio_server.py` now binds to `127.0.0.1` only, rejects network bind addresses, and does not start its research worker unless explicitly enabled. Privileged HTTP writes use a request-scoped, exact-action/payload-bound Ed25519 owner token; process-wide environment tokens are not used by web handlers.
- The owner-approval desk now has a private local SQLite queue, atomic one-time JTI consumption + decision update + hash-chained audit event, concurrency/replay/tamper tests, and no publish/notification side effects. Upgrades no longer imply a real schedule or rollback; the shell `--execute` path is blocked before changes.
- **Still not configured:** no trusted owner issuer, Ed25519 public key, owner subject, security epoch, shared research replay directory or production identity configuration is available in this checkout. Real signed owner actions therefore fail closed; mocked auth tests prove handler wiring, not issuer connection.
- The approval workflow is local metadata only: no agent handoff, message, external audit witness, publication or runtime upgrade.
- Authenticated peer heartbeat, production peer connection, application/database DR, provider/social/payment integration, and end-to-end publishing are not verified.
- Latest scheduled DR evidence is a tracked Git-tree comparison with no traffic switch. Effective target identity, owner/admin target-only data review, authorized verification, and read-after-write proof remain unresolved. Issue #6 is OPEN/P0.
- Native Android/macOS source and device/signature provenance remain unverified.
- Previous Reel Sprint work is retained; no prospect contact, owner-approved price, or revenue was recorded.

## Validation state

**Local offline regression: PASS** — `python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci` completed with 569 Python tests across 15 suites, 15 Node checks, 30 builders, and 0 failures. The suite includes the sandbox demo HTTP tests and `demo.js` syntax check. The deterministic registry rebuild, capability-fabric static check, architecture inspector, agent-change validation, JSON/YAML-syntax check, Python compilation, and shell syntax checks passed.

**Release readiness remains BLOCKED.** `ops/vyomaraj/final-readiness-gate.sh` exits non-zero because the requested 14-category / 153-slot taxonomy target is not yet reconciled and production runtime evidence is absent. Passing local checks do not establish a runtime connection, live capability enforcement, peer heartbeat, DR, production release, or revenue.

## Deployment and open-PR audit — 7 October 2026

- GitHub Pages is a public HTTPS site built from `main:/`; this worktree is not deployed. The sandbox preview at `0.0.0.0:5310` now serves the exact public asset allowlist and bounded deterministic `/api/plan` route. Local HTTP checks returned `200` for `/`, `/demo.html`, its CSS/JS, and a valid Bhakti plan; private repository, `.git`, and approval paths returned `404`. This is a session-scoped demo, not a production deployment.
- PR #39 is `OPEN/DRAFT` and `UNSTABLE`; diagnostics and offline tests failed. It has no review decision.
- PR #41 is `OPEN`/non-draft and `CLEAN`; its listed diagnostics/offline checks passed, but PR-event `verify-or-sync` was skipped and no review decision is recorded. It combines DR evidence with public-preview changes; a main-branch update may activate the conditional DR workflow, whose effective target remains unconfirmed. Issue #6 is still `OPEN/P0`.
- PR #42 is `OPEN/DRAFT` and `DIRTY`; its engineering-foundation check passed, but it has no review decision. Its remote proposal contains the 14-category / 153-agent roster, while its `historical_totals` field says 13 / 133 / 421 rather than preserving the checked-in 13 / 128 / 421 baseline. Treat it as an unmerged proposal until that historical-count discrepancy, full tests, and merge conflicts are resolved.
- No PR was merged, dispatched, or pushed in this pass. The obsolete static-only sandbox listener was replaced by the bounded local planner preview; no privileged writer or production service was installed or changed. The offline suite passed at 569 Python tests / 15 suites / 15 Node checks / 30 builders / 0 failures.
