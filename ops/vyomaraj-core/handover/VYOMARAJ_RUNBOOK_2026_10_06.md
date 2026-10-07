# VYOMARAJ — RUNBOOK: CONFIGURE · INTEGRATE · INHERIT · VERIFY

Generated 2026-10-07 14:10 UTC. The procedure for running this project, in the order it should be done. Copy-pasteable. Every command is run from the repository root.

---

## A · Safe preview posture

At generation, the allowlisted sandbox preview on :5310 is listening in this sandbox; it exposes exact public assets and a bounded deterministic POST /api/plan for Bhakti-Shakti and Roots & Pairings only. The plan is ephemeral; there are no provider calls, storage, or privileged writer services. Legacy product/viewer/gateway/studio listeners at generation: none. A sandbox preview is not deployment or production telemetry.
Latest scheduled Actions run `37605789908` at `2026-10-07T10:13:11Z` reports equal tracked Git trees only (`data_match=True`). Effective secondary identity, installed/deployed artifact equality and runtime DR remain unverified.

The studio and availability gateway now reject non-loopback bind addresses and default to `127.0.0.1`. Privileged HTTP actions require short-lived request-scoped Ed25519 owner tokens bound to the exact action and canonical request payload; the approval decision path also requires step-up and persists its JTI, queue update and local hash-chain event transactionally. The trusted owner issuer/key/security epoch are not configured in this checkout, so privileged actions fail closed. Do not weaken the bind policy or proxy writer routes to public ingress. The allowlisted sandbox preview on :5310 is separate: it offers only the bounded ephemeral local planner, with no privileged writer or persistence route.

The research worker does not start unless `--enable-research-worker` is explicitly supplied. These are local single-host controls, not a production identity provider, multi-host replay service, independent audit witness, or deployment. Stop any isolated test process after verification.

---

## B · Verify (run this before trusting anything)

The offline gate is safe to run now. No studio/gateway process is currently assumed running. The code enforces loopback binds and owner-token checks, but the trusted token issuer is absent; live route verifiers still require a deliberately configured, isolated test stack. Do not restart or proxy these services on the public preview.

```bash
python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci   # tests, node checks, builders
# Optional only in a secured, isolated test environment:
python3 ops/vyomaraj-core/handover/verify_live_wiring.py       # explicit test ports only
python3 ops/vyomaraj-core/handover/verify_preview.py           # page contracts + packages
python3 ops/vyomaraj-core/handover/realtime_status.py          # local port probe as JSON
python3 ops/vyomaraj-core/handover/probes.py --once             # manual, fixed-loopback snapshot
python3 ops/jarvis/heartbeat_monitor.py status                  # last local read-only snapshot
python3 ops/jarvis/heartbeat_monitor.py check                   # blank example endpoints return not_configured
python3 ops/jarvis/heartbeat_monitor.py shift                   # intentionally BLOCKED; never use as failover
# Optional sandbox-only loop, default endpoints stay blank:
python3 ops/jarvis/heartbeat_monitor.py run
```

`probes.py --once` appends to `/tmp/vyomaraj-probes.jsonl` and atomically writes `/tmp/vyomaraj-probes.latest.json`; `/reports/monitor` reads that file only when its viewer is deliberately running. The Jarvis monitor's example URLs are blank; its `run` loop writes private local snapshots but cannot authenticate peers, alert an owner, measure replication lag, verify backups, or perform independent-site DR. A reachable HTTP endpoint remains `reachable_unverified`.

A missing live listener means that local service is unavailable, not production failure or success. Do not weaken loopback/owner-token enforcement or restart a service just to make a verifier green; configure an isolated test environment out of band, then record the exact ports and scope.

---

## C · Regenerate the evidence after any change

Order matters. Refresh only generated status reports; preserve frozen transfer archives and historical packages unless the owner explicitly approves a new archive.

```bash
python3 ops/vyomaraj-core/handover/build_issue_ledger.py
python3 ops/vyomaraj-core/handover/build_stack_record.py
python3 ops/vyomaraj-core/handover/architecture_diagram.py
python3 ops/vyomaraj-core/handover/build_market_readiness.py
python3 ops/vyomaraj-core/handover/build_go_live_brief.py
python3 ops/vyomaraj-core/handover/build_full_handover.py
python3 ops/vyomaraj-core/handover/build_ai_handoff.py
python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci
```

Each report builder also supports `--check`, which fails if its checked-in copy has drifted. Do not rebuild frozen archives as part of a status refresh.

---

## D · Configure a real thing (procedure that has worked here)

1. **Measure first.** Probe the current state; never assume.
2. **Write the smallest checkable artifact** — JSON or Markdown — that states the new fact.
3. **Add a `--check`** so the artifact cannot silently drift.
4. **Gate it** by adding the command to `run_offline_suites.py`.
5. **Wire it** to a read-only surface by default; any writer needs owner-approved authentication, authorization, CSRF protection, audit logging and a restricted network boundary first.
6. **Add it to the verifier's required files** so a missing file is a failure.
7. Run offline gates. Use live verifiers only in an explicitly isolated test environment; keep the studio/gateway loopback-only and do not expose writer routes through public ingress.

This is why the project can be trusted: every claim has a command that fails when the claim stops being true.

---

## E · Integrate with a platform (the honest sequence)

| Step | Do this | Cost |
|---|---|---|
| 1 | Publish by hand from the owner's own account | ₹0 |
| 2 | Add a contact address to the page so a viewer can reach the owner | ₹0 |
| 3 | Add a free analytics counter and confirm it records a visit | ₹0 |
| 4 | Grow the audience until the platform's own threshold is met | ₹0 |
| 5 | Only then request API access for automation | ₹0, needs review |
| 6 | Only after earnings: host, domain, payments, vendors | paid |

Do not build a publisher before there is published content — and do not promise a platform integration in any document until an API call exists in code with a credential behind it.

---

## F · Inherit content correctly

| Take | Leave |
|---|---|
| The format: how a Sufi/qawwali or ghazal performance is structured and credited | The recording, the lyrics, the melody |
| The studio-show shape: house band, guest pairing, one episode one story | The show's name, branding or episode content |
| The documentation habit: name every creator, record every source | Any claim of endorsement by a named artist |

The test that enforces this in the repository fails the build if inherited titles, lyrics or artwork are copied in.

---

## G · Recover, hand over, and protect

- **Hand over:** `build_full_handover.py` and `build_ai_handoff.py` produce the documents and the downloadable archives. Both are safe to share: no token, no credential, no environment file, and the owner's email is redacted in the AI-facing one.
- **Back up / DR:** scheduled run `37605789908` at `2026-10-07T10:13:11Z` records an equal tracked Git tree for its workflow-selected target (`data_match=True`). The effective target name is not independently confirmed; Actions settings access is 403. This is a repository snapshot, not runtime/database replication, deployed-app equality, failover, RPO or RTO. Keep issue #6 OPEN/P0; owner/admin must confirm target identity and review target-only data before further sync. No new workflow run is triggered by this handover.
- **Protect:** the reports viewer serves an allowlist only and sends a hardened `Content-Security-Policy`. Same-origin images are permitted (`img-src 'self'`); scripts and external hosts are not.

---

## H · Owner-gated steps before any release or earning claim

1. **Resolve issue #6 safely:** owner/admin privately confirms the effective Actions-selected existing secondary; review current target-only data before authorizing any further sync, then obtain independent read-after-write evidence. The latest Git-tree match does not close the runtime/identity criteria. Keep issue #6 OPEN/P0 until every live acceptance criterion is evidenced.
2. **Verify the existing APK** with `apksigner verify`, review signer provenance and install it on a real Android device. If verification fails or provenance is unknown, recover the original source, rebuild and sign with an owner-held key; otherwise leave it off the release page.
3. **Review branch scope and deployment:** obtain explicit owner approval before any PR merge or Pages deployment; this branch is not currently deployed.
4. **Build native clients from approved source:** Android source/build project and macOS/Xcode project are absent here; obtain owner-approved source, signing/notarization access and real-device test plans before calling either a release.
5. **Connect peers safely:** implement the common Vyomaraj/Jarvis identity and capability contract, authenticated heartbeat in shadow mode, replay protection, immutable audit and single-writer fencing; owner approval remains required for privileged actions.
6. **Publish a contact address** on the public page and **switch on analytics** only after owner account decisions; confirm one real visit is recorded.

Then hand-publish the first episodes and apply to the YouTube Partner Program **before 1 February 2027** — the threshold for new applicants rises to 8,000 watch hours that day, from 4,000 today. The 500-subscriber tier opens fan funding earlier at 3,000 hours.

---

## I · Known limits, stated so nobody is surprised

| Limit | Consequence |
|---|---|
| Preview links are session-scoped | allowlisted static :5310 is open in this sandbox; legacy ports listening now: none; Pages is durable but serves `main` only |
| `flow-diagram.html` loads Mermaid from a CDN | on a network that blocks that CDN, the diagrams do not render |
| No analytics | nobody can see visits |
| No login | no returning audience |
| No payments | nothing can be sold |
| DR covers files, not runtime | a live database would not be covered; tree match is not failover/RPO/RTO evidence |
| Native Android/macOS | no Android/macOS source project here; APK signing and device installation unverified |
| Peer heartbeat | local example endpoints are blank; no authenticated production peer or failover |

