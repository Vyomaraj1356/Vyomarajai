# Shared peer architecture and heartbeat plan — 7 October 2026

**Status: architecture target and local probe code exist; production peers are not connected.** This document separates the intended Vyomaraj/Jarvis design from what was measured in the repository and on GitHub. It does not authorize a production deployment, key creation, repository write, failover, or device tracking.

Diagram: [`ARCHITECTURE_DIAGRAM_2026_10_06.svg`](ARCHITECTURE_DIAGRAM_2026_10_06.svg) · Current integration evidence: [`INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md`](INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md).

## 1. Peer model: one contract, two peers, no inherited root authority

```text
                         OWNER / HUMAN APPROVAL
                                  │
                    ShriYantra policy & identity boundary
                                  │
              ┌───────────────────┴───────────────────┐
              │                                       │
      Vyomaraj / Bharath  ◄── authenticated link ──►  Jarvis / Laxman
      research · planning                              continuity · proposals
      owner-facing coordination                        scoped execution · monitoring
              │                                       │
              └──────────── same versioned capability contract ────────────┘
                                  │
                  least-privilege tools · durable audit · recovery
```

The two peers share a contract for identity, policy evaluation, capability names, task envelopes, evidence and audit records. Their roles may differ; neither peer is a parent/root principal for the other. A capability description can be inherited as metadata, but **identity, owner authority, credentials, secrets, consent, location, and approval grants never inherit**. Root-owner authority cannot be delegated to an agent. Server-side authorization is mandatory; a UI, local config, model response or heartbeat is not an authorization decision.

High-risk actions require deny-by-default policy, a fresh owner step-up approval, an idempotency/replay guard, scoped execution and immutable audit. Provider keys remain in a server-side secret manager. No keys or contact data belong in this repository or in chat.

## 2. Heartbeat protocol — target behavior, not current capability

A periodic HTTP `GET /healthz` can show only that a reachable endpoint answered. It cannot authenticate a peer, prove process readiness, verify durable state, or authorize failover. A response field such as `ready: true` is an untrusted claim unless it is bound to an authenticated identity and current challenge.

Before a production heartbeat is described as verified, implement and test all of these:

1. **Unique peer identity:** provision one owner-controlled service identity per installation; pin/rotate trust material. Prefer mutual TLS or an equivalently reviewed signed challenge protocol. Do not share one API key between peers.
2. **Freshness and replay defense:** signed peer ID, monotonic sequence, nonce/challenge, issued/expiry times and a request ID. Reject replay, stale messages and excessive clock skew. Store replay/sequence state durably.
3. **Bounded health semantics:** report liveness, readiness and dependency state separately; a failed dependency is not hidden behind a green process check. Return only safe metadata—no tokens, user content, device identifiers, location or secrets.
4. **Explicit peer allowlist:** operator-configured hostnames/certificates only, HTTPS for remote endpoints, strict timeouts and size limits, redirect refusal, and auditable configuration changes.
5. **Alerting and retention:** authenticated success/failure history, last-success age, consecutive misses and owner-visible alerts. Keep local probe status separate from production telemetry.
6. **Failover fence:** a heartbeat cannot switch the writer. Use a durable lease/quorum or a monotonic fencing token, prove the old writer is stopped, preserve a known-good backup, then require owner approval for promotion. No split-brain or dual-writer mode.

### What exists now

- `ops/jarvis/heartbeat_monitor.py` is a fail-closed, read-only, standard-library probe. Example peer URLs are blank. A reachable configured URL is reported as `reachable_unverified`; a partial pair is `partially_configured`; the shipped example is `not_configured`.
- The monitor stores a private local snapshot atomically and can loop at a configured interval. Its `shift` command returns `BLOCKED` and it never performs failover, state transfer, location tracking or remote mutation.
- A fresh local read-only check at `2026-10-07T10:15:32Z` was `not_configured`; both peer URLs remain blank, so zero remote endpoints were contacted. Authenticated heartbeat, production peer/DR verification and failover were all `false`. Capability status was separately re-read at `10:15:36Z` and still reports runtime fabric `not_implemented` and `root_authority_inherited=false`.
- `ops/jarvis/jarvis-24x7-controller.sh` is a compatibility wrapper. It does not source the legacy `jarvis.env` file. Its `test` command runs the real offline test module.
- The final offline gate passed at `2026-10-07T10:19:50Z`: 507 Python tests across 15 suites, 14 Node checks and 26 builders; 0 failures. The test set includes 9 Jarvis heartbeat-monitor unit tests and is local software-test evidence only, not an authenticated heartbeat or production-health check. The receipt is `ops/vyomaraj-core/handover/TEST_EVIDENCE_2026_10_04.json` (viewer: [`/reports/test-evidence`](/reports/test-evidence)).
- `ops/hanuman/capability_status.py` reports capability mappings as metadata only and blocks heartbeat/shift claims. It explicitly reports `root_authority_inherited=false`.
- The current local example config intentionally has no endpoint URLs, trust roots, peer tokens or signing keys. No authenticated Vyomaraj↔Jarvis heartbeat service, alerting service or production multi-agent runtime is deployed.

Do not put phone numbers, arbitrary phone URLs, personal location endpoints or third-party URLs into the example config. Location stays off unless a lawful, consented use is separately authorized. No covert tracking or access bypass is implemented.

## 3. Current package / deployment boundary

At the 09:45:42Z scheduled checkpoint (#40), run `37602725866` / check-run `112730920825` on primary main commit `04b7ae60ce2855b1d48043d80f790488e894ee79` reported `status=MATCH`, `data_match=true`, `traffic_switched=NONE`, `http=UNAVAILABLE`, and identical tracked Git trees `986288ee2cc4ec4d89400320150ea893f7a7a2de`; it was a no-write confirmation. That checkpoint was checked as a tracked-tree result only, not runtime/app availability, independent site DR, authenticated heartbeat, failover, RPO or RTO evidence. Its addendum did not re-read the prior 39 annotations; the last full historical annotation audit remains separately recorded at 08:28 UTC. Two earlier main-push workflow runs recorded actual snapshot writes.

The latest scheduled checkpoint (#41), run `37605789908` / check-run `112741170924`, completed at `2026-10-07T10:13:11Z` on the same main tip. Its freshly re-read annotation again reports `MATCH`, `data_match=true`, identical tracked trees `986288ee2cc4ec4d89400320150ea893f7a7a2de`, `traffic_switched=NONE`, no write and `http=UNAVAILABLE`. This addendum checked only the new annotation, not the previous 40; it is not runtime/app availability, authenticated heartbeat, failover, RPO or RTO evidence.

The primary tree contains `Vyomaraj-App.apk` (Git blob `9c95df15c8cb1787bf85b7d44f9445ff9376f1f2`, 24,567,022 bytes). Equal tree hashes imply the same tracked APK blob in the workflow's compared secondary tree. They do **not** validate the v2 signing-block signature, signer provenance, device installation or deployment of that APK.

GitHub Pages is built from `main:/` at `04b7ae60`; this session's branch is not deployed and PR #41 remains open on a base two commits behind main. The workflow variable `VYOMARAJ_DR_REPO` can override the in-repository fallback, but the Arena credential cannot read Actions settings (403), so the effective target name is not independently confirmed. Candidate-path 404s are ambiguous. Issue #6 remains OPEN/P0 pending owner/admin confirmation of the authoritative target and review of target-only data.

## 4. Release and integration status

| Surface | Verified now | Not verified / next gate |
|---|---|---|
| Web | Static HTML/CSS/JS PWA shell; GitHub Pages main build exists; safe allowlisted local preview server is available | This branch has not been deployed; no public publishing approval is implied |
| Android | A 24,567,022-byte APK is tracked in the same Git tree | No Android source/build project or SDK tools found here; signature, signer, device install and release provenance unverified |
| macOS | Browser-based web preview can be used on a Mac | No macOS/Xcode source project, build, signing or notarization artifact |
| Vyomaraj/Jarvis peer roles | Shared architecture and capability metadata are documented | No common authenticated peer runtime or production interlink |
| Heartbeats | Local bounded read-only monitor and tests exist | No production endpoints, identity, authentication, scheduler, alerts, quorum or failover |
| Providers | Local no-tools harness/prototypes can be exercised with explicit local config | No social, payment, analytics, email/SMS or external AI provider connection is evidenced |
| DR | Latest scheduled Actions result reports equal tracked Git trees | Effective secondary identity, runtime/data equality, backup restore, failover, RPO/RTO remain unproven |

## 5. Safe implementation sequence

1. Owner/admin confirms the authoritative secondary repository and whether the Actions variable overrides the repository fallback. Review target-only data before any additional snapshot write; do not share secret values.
2. Keep issue #6 open until authorized source/target metadata, target-only review, a controlled non-force sync, and independent read-after-write evidence satisfy its acceptance criteria.
3. Review PR #41's combined scope against current main, now two commits ahead of its base. Merge/deploy only after owner approval. PR #39 remains untouched; no PR state is changed by this report.
4. Build the authenticated peer identity and scoped authorization layer before connecting the two peers. Keep root authority, secrets and consent non-inheritable.
5. Add the authenticated heartbeat protocol above in shadow/read-only mode first. Exercise expired challenges, replay, skew, missing peer, partial config, dependency failures and certificate/key rotation.
6. Define durable state/backup boundaries and a manual failover runbook with fencing. Test restore and failover on disposable infrastructure; record measured RPO/RTO before making claims.
7. Build native Android/macOS clients only from owner-approved source. Verify signing provenance with platform tools and install/test on real devices before advertising either as a release.

## 6. Go/no-go wording

**Accurate:** “At the 10:13:11Z scheduled checkpoint (#41), the primary and workflow-selected secondary reported equal tracked Git trees (`status=MATCH`, `data_match=true`, `traffic_switched=NONE`; annotation `http=UNAVAILABLE`). This is not runtime, deployed-app, authenticated-heartbeat, target-identity, signing-validity, failover, RPO or RTO verification.”

**Not accurate:** “Everything is connected,” “Jarvis is live 24×7,” “the APK is a verified release,” or “DR failover is ready.”

For current status and the detailed evidence table, see [`INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md`](INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md).