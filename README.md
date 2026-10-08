# Vyomaraj — The King of Sky

Vyomaraj is a private AI-agent orchestration and creation system.

> **Current evidence (8 October 2026).** **The scheduled DR verification had stopped running and has not yet resumed on `main`.** `verify-or-sync` depends on `offline-tests`; that gate began failing on main at `ae92895` (2026-10-07 15:53 UTC) and stayed broken through PRs #45–#49, so the primary↔secondary comparison was **skipped** 37 consecutive times — roughly sixteen hours with no verification. The last comparison that actually executed is check-run `112880681037`, completed `2026-10-07T15:50:01Z` on main `04b7ae60`: `status=MATCH`, `data_match=true`, equal tracked Git trees `986288ee…`, `traffic_switched=NONE`. Main has since advanced to `5935588` **without** DR verification, so no current primary/secondary equality is claimed. The cause was five canonical files overwritten by the 7 October consolidation merges plus a shell-escaping defect that made several deny-by-default gates exit 0 without checking anything; those are repaired on this branch and the offline suite is back to **61/61** (585 Python tests, 15 Node checks, 31 builders), but the repair must reach `main` before the 30-minute schedule can verify again. Package parity — both dependency manifests and release archives — is now checked on every DR run and recorded in [PACKAGE_PARITY.json](ops/dr/PACKAGE_PARITY.json); all 8 locked pins were confirmed to exist on PyPI. From Arena the read-only DR test still returns `BLOCKED`/HTTP 404 on the secondary and 403 on Actions settings, so the effective target remains owner-unconfirmed; **a 404 is not proof of absence**. No sync was performed, no traffic was switched, no installed environment was compared, and issue #6 remains OPEN/P0. The tracked APK blob's v2 signing-block entry is still not proof of signature validity, signer provenance or real-device installation. See the [sync, DR test and package parity record](ops/dr/DR_SYNC_AND_PACKAGE_PARITY_2026_10_08.md), [timestamped issue/PR/Pages ledger](ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md), [latest DR evidence](ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md), [shared peer architecture and heartbeat status](ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md), [integration/release audit](ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md), and [safe runbook](ops/vyomaraj-core/handover/VYOMARAJ_RUNBOOK_2026_10_06.md).
>
> <details><summary>Preserved 7 October evidence block</summary>
>
> **Current evidence (7 October 2026; full access audit at 08:28 UTC, scoped issue/PR/main/Pages metadata re-read at 10:06 UTC, and latest scheduled DR annotation separately re-read):** GitHub Pages is built from `main:/` at `04b7ae60`; this Arena branch is not deployed and main is two commits ahead of PR #41's base. Issue #6 remains OPEN/P0. PR #41 is OPEN/non-draft; PRs #39 and #42 are OPEN/DRAFT; PR #39 was left untouched. The scoped 10:06 UTC metadata read confirmed those states, main at `04b7ae60`, and Pages source `main:/`; candidate-path 404s and Actions-settings 403s remain from the 08:28 full access audit. The latest scheduled `verify-or-sync` run (`37605789908`, check-run `112741170924`, completed `10:13:11Z`) reported `MATCH`, `data_match=true`, identical primary/secondary **tracked Git trees** (`986288ee…`), `traffic_switched=NONE`, and annotation `http=UNAVAILABLE`. This latest addendum checked only the new annotation; the preceding 40 annotations were not re-read. The last full historical annotation audit remains separately recorded through 08:28 UTC. Two automatic main-push runs recorded replication writes. This is a point-in-time repository snapshot match—not an installed/deployed app, live service, authoritative-target identity, authenticated heartbeat, or DR failover; the Arena credential still gets 404 on candidate paths and 403 for Actions settings, so issue #6's owner-confirmation and target-only-data gates remain open. The tracked APK blob is present in the matched tree, but its v2 signing-block entry is not proof of signature validity; signer provenance and real-device installation remain unverified. No Android/macOS source project or production heartbeat service is present. A local read-only heartbeat monitor exists but its peer URLs default to unconfigured. See the [timestamped issue/PR/Pages ledger](ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md), [latest DR evidence](ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md), [shared peer architecture and heartbeat status](ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md), [integration/release audit](ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md), and [safe runbook](ops/vyomaraj-core/handover/VYOMARAJ_RUNBOOK_2026_10_06.md).
>
> </details>

## Current handover artifacts

- [Integration alignment and release audit](ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md)
- [Shared peer architecture and heartbeat plan](ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md)
- [Universal Knowledge Evolution inheritance contract](docs/architecture/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE.md) · [machine-readable policy](config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json)
- [Current 7 October full-handover archive](ops/vyomaraj-core/handover/transfer/VYOMARAJ_FULL_HANDOVER_2026_10_07.zip)
- [Current 7 October AI handoff archive](ops/vyomaraj-core/handover/transfer/AI_PLATFORM_HANDOFF_2026_10_07.zip)

The 6 October archives are preserved alongside these additive current snapshots.

## Public experience

The public surface is intentionally limited to approved creations and published experiences:

- AI-generated and human-approved content
- Knowledge, education and research experiences
- Culture, food, travel, sports and entertainment content
- Social-platform publishing outputs
- Approved public web experiences

## Private control plane

Internal orchestration, credentials, agent routing, infrastructure, recovery controls, private data, operational logs and other sensitive implementation details are kept out of the public-facing experience.

The repository contains operational material for authorized development and recovery. Secrets must remain in GitHub Actions secrets or another secure secret store and must never be committed to source files.

## Repository roles

- **Primary:** `Vyomaraj1356/Vyomarajai`
- **DR / secondary — latest point-in-time snapshot:** scheduled run `37605789908` / check-run `112741170924` on main `04b7ae60` reported equal primary/secondary tracked Git trees (`986288ee…`) at 10:13:11 UTC, with `traffic_switched=NONE` and annotation `http=UNAVAILABLE`; it was a no-write confirmation. Two automatic main-push sync writes were observed since the preceding recorded baseline. The Actions variable may override the in-repo fallback, and the Arena credential cannot read Actions settings or the target repo, so the owner-confirmed canonical target and target-only-data review remain unresolved. This is Git-tree equality, not runtime/site/app failover evidence; issue #6 remains OPEN/P0. See the [timestamped ledger](ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md), [DR results](ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md), [DR runbook](ops/dr/README.md) and [repository map](VYOMARAJ_REPOSITORY_MAP.md).
- The reviewed workflow replicates only primary `main`; pull-request sync is skipped, automatic main-push/schedule writes are gated by its policy/Actions configuration, and the current Pages build is at main `04b7ae60`. The current branch is not deployed. A 404 is not proof that a private repository does not exist.
- DR-to-primary promotion is a controlled recovery operation; no blind two-way overwrite or force-push is used.

## Verification policy

A commit message, screenshot, archive name, old preview URL, or previous "synced" statement is not proof of a current state.

Current claims should be backed by:

1. source commit/ref verification,
2. authenticated DR access verification,
3. replication evidence containing source and target state,
4. preview verification,
5. explicit separation of recovered, missing, reconciled and verified information.

## Development

Use review branches and pull requests for changes. Do not push experimental Arena changes directly over `main`.

> **Preview safety:** the sandbox landing server on :5310 serves an exact public-asset allowlist and a bounded deterministic `POST /api/plan` for Bhakti-Shakti and Roots & Pairings only. The plan is returned in memory; no AI/provider or external-network call, visitor-data persistence, approval queue, privileged writer, or private repository path is exposed. Start it with `python3 ops/vyomaraj-core/experience/public_landing_server.py --host 0.0.0.0 --port 5310`, then open `/demo.html` (or the home page). This session-scoped preview is not GitHub Pages, production, or an autonomous agent. Other studio/gateway services on 3000/4174/4176/4181/4182 are separate; never expose their writers on public ingress. Use an isolated test stack with disposable data and owner-approved controls.

## Architecture V16.8 (2026-10-04)

This is the intended authority chain, not a claim that each service is currently live: You (Owner) → ShriYantra (authority) → Vyomaraj/Bharath + Jarvis/Laxman → agents and sub-agents → content creation and verification → **owner approval (central nostalgic camera)** → approved publishing → social platforms → analytics and monetization → learning — with Hermes guarding integrity end to end and Arena executing approved tasks only. Full document:
[ARCHITECTURE_V16_8_2026_10_04.md](ops/vyomaraj-core/handover/ARCHITECTURE_V16_8_2026_10_04.md),
interactive diagram: [flow-diagram.html](flow-diagram.html).

Local lanes and desks (deterministic planners + tests + browser prototypes, nothing publishes
automatically): `/comics/` (Chitra Katha — every title and edition in Hindi, English and
Hinglish, past versions preserved, future versions plannable), `/approvals/` (the wooden
nostalgic-camera owner approval queue), `/finance/` (finance and audit follow-up plus the
every-morning briefing drafts), `/upgrades/` (post-deployment change management with
backup-first rollback).

## Reconstructed handover — 3 October 2026

The [handover notepad](ops/vyomaraj-core/handover/HANDOVER_ALL_UPDATES_2026_10_03.txt) was reconstructed from the verified roster and content catalog on the reconciled Arena branch. It is **not the recovered original 365-line file**. It preserves `UNKNOWN` names and `UNMAPPED` slots, lists only the 32 cataloged JSON filenames (not all 421 product titles), and excludes populated runtime/device values.

Validate it locally with `python ops/vyomaraj-core/handover/rebuild_handover.py --check`.

For the expanded agent roster, historical candidates, content-label index, platform/technology configuration, and unresolved work, see the [full system inventory](ops/vyomaraj-core/handover/FULL_SYSTEM_INVENTORY_2026_10_03.md). It distinguishes local files, remote-only implementations and unverified historical claims; private configuration values are excluded.

The [DR resolution report](ops/vyomaraj-core/handover/DR_RESOLUTION_2026_10_03.md) records historical 404/403 access blockers, local fixes and GitHub PR/CI evidence; the current status is in the timestamped ledger above. The read-only report viewer was stopped at the 08:15 UTC probe. If it is needed for local review, run `python ops/vyomaraj-core/handover/preview_reports.py --port 4174`; this is a session-scoped viewer, not a deployment. It serves only an exact-route allowlist of sanitized reports. Do not replace it with unrestricted repository-root file serving, or start the unauthenticated gateway/studio writers on a publicly reachable preview.

## Films, theatre, clips and advertising

[Frame & Stage](ops/vyomaraj-core/film-experience/README.md) extends the six existing Movie slots with proposed functions for films, shorts, clips, Marathi/Hindi theatre and advertising. It adds source-linked discovery, original outline planning, and browser-local trim/reorder previews with edit-decision JSON—not rehosted commercial films or encoded movie exports. Run the shared server with `--home film`; open `/film/`, `/reports/film` and `/reports/contents`. [All experience contents](ops/vyomaraj-core/handover/EXPERIENCE_CONTENTS_2026_10_03.md) · [Film update](ops/vyomaraj-core/handover/FILM_THEATRE_ADS_UPDATE_2026_10_03.md).

## Music, radio, audio and video

[Memory & Melody](ops/vyomaraj-core/music-experience/README.md) fills the dedicated music experience gap without duplicating the six existing ENT-MUS slots. It adds researched nostalgia/album/folk/world/chart/video discovery, a browser-local authorized-file player, and source-linked Vyomaraj/Jarvis programme plans. Run the shared studio on port 4176 and open `/music/`. [Updated audit and feature report](ops/vyomaraj-core/handover/MUSIC_AUDIO_VIDEO_UPDATE_2026_10_03.md). Slot functions are proposals; streaming, live charts and external AI are not connected.

## Bhakti-Shakti and the integrated local studio

The [Bhakti-Shakti feature report](ops/vyomaraj-core/handover/BHAKTI_FEATURE_UPDATE_2026_10_03.md) covers Shiv–Shakti, a 12-chapter proposed Shiva story guide, a Dashavatara overview, nine Shakti Peetha/regional starter profiles and Mahadev television context. The [content guide](ops/vyomaraj-core/bhakti-experience/README.md) explains sources and limitations.

The integrated studio now defaults to **127.0.0.1**, refuses non-loopback binds and does not start the research worker unless `--enable-research-worker` is explicitly requested. `/api/plan` performs deterministic local topic routing and Jarvis review handoffs. Research writes and privileged approval/change decisions require request-scoped, action-bound Ed25519 owner tokens; approval decisions persist to a private local SQLite database with a hash-chained audit event. This checkout has no configured owner token issuer/key, so privileged calls fail closed. This is a single-host local service, not a production deployment; keep it off public ingress. Prasad-style food rotation, preparation sequences and preference controls remain illustrative. External AI and production publishing are unconnected. The latest scheduled DR run reported a matching tracked Git tree, but the effective secondary identity, runtime DR, failover, RPO and RTO remain unverified; issue #6 is OPEN/P0. No canonical agent totals or old content files were overwritten.

## Liquor + Bar: Roots & Pairings

The [Liquor/Bar content expansion](ops/vyomaraj-core/liquor-bar/README.md) adds local tadi/toddy, regional/global cultural research, event-source records, and eight chakhna/snack concepts with preparation, allergen preferences and non-alcoholic pairings. Run `python ops/vyomaraj-core/liquor-bar/server.py --port 4175` for the interactive browser prototype. Its 3D-style plate, 4D sequence and 5D preference controls are illustrative; no AI renderer or alcohol service is connected. Proposed chapters live in a separate extension catalog without changing the original 133/421 counts or 32-file snapshot.

## V16.9 auto-align and open-item ledger

The [auto-align plan](ops/vyomaraj-core/handover/AUTO_ALIGN_NEXT_SESSION_2026_10_04.md) gives every open platform-check item a concrete completion step; the [platform check](ops/vyomaraj-core/handover/PLATFORM_CONFIGURATION_CHECK_2026_10_04.md) lists those mappings, and the [issues/PRs ledger](ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md) is the new-session runbook. Validate with `python3 ops/vyomaraj-core/handover/auto_align.py --check` and `python3 ops/vyomaraj-core/handover/build_issue_ledger.py --check`. The runner is local-only: it does not install, purchase, connect providers, publish content or change GitHub state. A historical issue #6 close-out draft is preserved for provenance only; issue #6 remains OPEN/P0, and that text must not be posted or used to close it.

## Priority recovery / cleanup status

The [non-destructive recovery audit](ops/vyomaraj-core/handover/PRIORITY_RECOVERY_AUDIT_2026_10_03.md) records the historical primary fetch, duplicate archive candidates and reconciliation plan. The latest scheduled run on 7 October at 10:13:11Z reports equal tracked Git trees, but the effective secondary target identity and target-only review remain unconfirmed; runtime/failover/RPO/RTO are not proven. See [priority issue #6](https://github.com/Vyomaraj1356/Vyomarajai/issues/6), which remains OPEN/P0. Do not delete historical archives or authorize another exact-snapshot DR write before the owner confirms the target and secondary-only work is inspected and preserved.

## Security

Never commit:

- personal financial/account information,
- access tokens or API keys,
- private contact information,
- internal authentication material,
- private operational URLs,
- database credentials,
- recovery secrets.

If sensitive information is discovered in a public file, remove it and rotate the affected credential where applicable.

© 2026 Vyomaraj

## AI Agent OS alignment — 7 October 2026

The additive execution context, verification rules, live status, decisions, blockers and next actions are indexed under [`docs/vyomaraj/context/`](docs/vyomaraj/context/README.md) and [`docs/vyomaraj/state/`](docs/vyomaraj/state/CURRENT_STATE.md). The current target architecture and final integration gap matrix are in [`docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md`](docs/architecture/VYOMARAJ_ARCHITECTURE_AND_PUBLISH_v1.2.md) and [`docs/architecture/VYOMARAJ_FINAL_INTEGRATION_GAP_MATRIX_v1.0.md`](docs/architecture/VYOMARAJ_FINAL_INTEGRATION_GAP_MATRIX_v1.0.md). These are alignment records, not production verification or a replacement for the owner-supplied master script.

The current checked-in registry remains 13 categories / 128 counted sub-agents / 421 historically reported products. The requested 14 / 153 / 421 target is not applied until every supplied addition is reconciled. Production peer, provider, transactional mutation, application DR, publishing, financial, Android signer/device, and macOS release evidence remains unverified.
