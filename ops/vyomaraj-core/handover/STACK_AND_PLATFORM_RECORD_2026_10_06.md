# Vyomaraj — stack and platform record — 7 October 2026

**Generated file — do not edit by hand.** Rebuild with `python3 ops/vyomaraj-core/handover/build_stack_record.py`; `--check` verifies this copy.

This is the answer to "what technologies and platforms did we use and configure?" written from evidence in this checkout, not from memory. It separates what is **implemented by code here** from what a historical document **claimed**; a local listener or probe does not prove production readiness. Read section 3 before repeating any figure from the earlier market-ready README.

## 1. What the product is actually made of

| Area | Technology | Evidence | Note |
|---|---|---|---|
| Public launch page and planner demo | Static HTML + CSS + vanilla JavaScript; no bundler or framework | `index.html, launch.css, launch.js, demo.html/demo.css/demo.js; landing.html redirects to the evidence-based page` | GitHub Pages serves static files; the sandbox root opens demo.html and /index.html keeps the brand shell; GET /api/catalog and POST /api/plan exist only on the sandbox server and are not deployed to Pages |
| Installable web shell | Web App Manifest + service worker + local PNG/SVG icons | `manifest.webmanifest, sw.js, offline.html, assets/vyomaraj-icon-*` | offline cache includes only the public landing shell; not a native Android or macOS client |
| Product palette | Launch shell: #091323 + gold; experience previews retain Shani Blue #0a1628 + Kuber Gold #f59e0b | `launch.css, preview_reports.STYLE, styles.css` | two documented surfaces; no external font/CDN dependency on the launch page |
| Local servers | Python 3 standard library http.server / ThreadingHTTPServer | `ops/vyomaraj-core/experience/studio_server.py, ops/availability/gateway.py, ops/vyomaraj-core/handover/preview_reports.py, public_landing_server.py` | studio/gateway enforce loopback-only binds; public preview serves an exact asset allowlist, read-only GET /api/catalog over curated Bhakti-Shakti and Roots & Pairings content, and bounded ephemeral POST /api/plan; no privileged writers, provider calls or persistence; no Flask/FastAPI/Django |
| One-shot local service monitor | Manual loopback probes with a read-only latest-snapshot page | `ops/vyomaraj-core/handover/probes.py and /reports/monitor` | JSONL + latest local snapshot; no scheduler, alerting or production/DR claim |
| Jarvis reachability monitor | Python standard-library bounded GET probe with private local state | `ops/jarvis/heartbeat_monitor.py, heartbeat-config.example.json` | reports reachability only; no authenticated mutual heartbeat, failover or production health |
| Shared peer architecture and heartbeat target | Vyomaraj/Jarvis common identity, policy and capability contract; fail-closed heartbeat plan | `PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md, ops/jarvis/heartbeat_monitor.py` | design + local read-only probe only; no production interlink, inherited root authority, quorum or failover |
| LLM draft harness | Optional no-tools OpenAI-compatible chat client with explicit invocation | `ops/jarvis/llm_harness.py, ops/jarvis/LLM_HARNESS.md` | no provider is configured by the repository; no tool execution or autonomous actions |
| Panch capability metadata | Five-name mapping validator with no runtime/heartbeat claim | `ops/hanuman/capability_status.py, ops/hanuman/test_capability_status.py` | checks metadata only; capability execution and platform connections remain unimplemented |
| Local owner-approval slice | Ed25519 exact-action verification + private transactional SQLite queue and local hash chain | `ops/shriyantra/owner_guard.py, ops/vyomaraj-core/approvals/approval_store.py, experience/studio_server.py` | issuer/key/owner/security epoch are not configured; local single-host control slice only; no agent handoff or publishing |
| Bindings | Server-specific: studio and availability gateway enforce IPv4 loopback; public sandbox preview binds for session access | `studio_server.py and gateway.py validate_loopback_host; public_landing_server.py serves exact assets, GET /api/catalog, and POST /api/plan` | catalog is curated/read-only for two fixed packs; the planner accepts only two fixed experiences, performs no persistence/provider calls, and is not a privileged writer; never network-bind the local studio/gateway |
| Public hosting | GitHub Pages from main (static) | `Live read 2026-10-07: Pages API build 04b7ae60, source main` | the current feature branch is not deployed there; the URL serves main only |
| Automation | GitHub Actions workflow definitions, Python 3.12 and Node 20/24 runners | `vyomaraj-sync-both.yml, vyomaraj-ci-diagnostics.yml, vyomaraj-research.yml` | scheduled run 37605789908 reports a tracked-tree match; Actions variable may override fallback and settings API access is 403 |
| DR mechanism | Git-snapshot replication workflow with scheduled tracked-tree match evidence | `ops/dr/dr_sync.py, ops/dr/DR_POLICY.json, live read-only annotations recorded in ISSUES_AND_PRS_LEDGER.json` | scheduled check 2026-10-07T10:13:11Z reports equal tracked Git trees (986288ee2cc4ec4d89400320150ea893f7a7a2de); canonical target identity and runtime DR are unverified |
| Tests and preview release gate | Python unittest + node syntax/tests + builder checks; verification only | `ops/vyomaraj-core/handover/run_offline_suites.py, ops/vyomaraj/publish-gate.sh` | a preview PASS does not change the separate production status; the gate never deploys |
| State stores | SQLite and JSON files on disk (no database server) | `ops/vyomaraj-core/research/discovery.py, approvals/approval_store.py, ops/vyomaraj-core/ledger` | research/approval state is single-host and outside Git-snapshot replication; approval DB is owner-only, but both need independent backup/restore evidence |
| Browser voice | Web Speech API (speechSynthesis) where the page uses it | `product HTML/JS voice controls` | microphone capture needs device permission |
| Browser media | WebRTC getUserMedia + MediaRecorder + Web Audio API | `camera/video/audio mixer lanes in the product page` | no upload; files stay in the tab |
| Maps | Leaflet 1.9.4 with OpenStreetMap tiles | `map lane in the product page` | tiles load from the OSM service at view time |
| Plans and content | Deterministic local planners by default; optional explicit no-tools LLM draft stage | `local_planner.py, music_planner.py, film_planner.py, comics_planner.py, aghor_planner.py, ops/jarvis/llm_harness.py` | provider calls require explicit local configuration and invocation; plans do not publish |
| Registry | JSON registry + content index + ownership map, pinned and test-guarded | `ops/vyomaraj-core/agents/*.json, test_registry.py` | 13 categories / 128 counted slots / 6 headings |
| Android app | APK binary committed (24,567,022 bytes); v2 signing-block entry detected, but cryptographic validity, signer provenance and device installation are UNVERIFIED; no project source in repo | `Vyomaraj-App.apk: 222 entries, 8 dex files; verify_live_wiring.py parses ZIP signing-block structure (scheme ID 0x7109871a)` | not a verified release; keep off downloads until apksigner verification, signer review and a real-device install pass |
| macOS native app | No macOS source project or signed application archive in this checkout | `repository file inventory` | not available as a native release |

## 2. The month's archive (all of it, in this repository)

- Handover zip packages: **25** (V16.5.3-v167 through V16.7.22-v192), plus 1 duplicate tarball of the first one
- Market-ready releases: **15** (V6.6 through V15.1)
- Archives counted in total: **44**

| Archive | Bytes | SHA256 | Zip members |
|---|---|---|---|
| `Vyomaraj-Handover-V16.5.3-v167.tar.gz` | 360,649 | `32cda4391cd8e618…` | — |
| `Vyomaraj-Handover-V16.5.3-v167.zip` | 407,729 | `465f56e8ef9f99c1…` | 58 |
| `Vyomaraj-Handover-V16.6-v168.zip` | 472,710 | `9de7362323078c7d…` | 70 |
| `Vyomaraj-Handover-V16.7-v169.zip` | 546,712 | `7fad96ecce832be9…` | 74 |
| `Vyomaraj-Handover-V16.7.1-v170.zip` | 546,712 | `c6d3dd389e957add…` | 74 |
| `Vyomaraj-Handover-V16.7.10-v180.zip` | 577,569 | `70de9dca3c87fb20…` | 83 |
| `Vyomaraj-Handover-V16.7.11-v181.zip` | 578,874 | `617b54535443dac9…` | 84 |
| `Vyomaraj-Handover-V16.7.12-v182.zip` | 577,007 | `c7efb4e91db0ec3c…` | 84 |
| `Vyomaraj-Handover-V16.7.13-v183.zip` | 577,727 | `758ecf7ff6d7ae77…` | 85 |
| `Vyomaraj-Handover-V16.7.14-v184.zip` | 577,754 | `243440032fbc6a16…` | 85 |
| `Vyomaraj-Handover-V16.7.15-v185.zip` | 436,645 | `a10c03b77ffa88d5…` | 37 |
| `Vyomaraj-Handover-V16.7.16-v186.zip` | 578,890 | `f5f3a784ace56240…` | 74 |
| `Vyomaraj-Handover-V16.7.17-v187.zip` | 579,032 | `9b20c0e2cedbce3b…` | 74 |
| `Vyomaraj-Handover-V16.7.18-v188.zip` | 579,125 | `cbf686c55c30571e…` | 74 |
| `Vyomaraj-Handover-V16.7.19-v189.zip` | 579,109 | `e3676dcce3f62cbf…` | 74 |
| `Vyomaraj-Handover-V16.7.2-v171.zip` | 546,712 | `c6d3dd389e957add…` | 74 |
| `Vyomaraj-Handover-V16.7.20-v190.zip` | 579,411 | `b97348d8a8eba209…` | 74 |
| `Vyomaraj-Handover-V16.7.21-v191.zip` | 579,333 | `ec7c0cf2cd4e854a…` | 74 |
| `Vyomaraj-Handover-V16.7.22-v192.zip` | 311,660 | `6f5c4297074e0d84…` | 92 |
| `Vyomaraj-Handover-V16.7.3-v172.zip` | 552,522 | `c3753c1174dd9612…` | 75 |
| `Vyomaraj-Handover-V16.7.4-v173.zip` | 552,522 | `300de0418e4e1dd0…` | 75 |
| `Vyomaraj-Handover-V16.7.5-v174.zip` | 552,580 | `ad1b70ed9c4feb0a…` | 75 |
| `Vyomaraj-Handover-V16.7.6-v176.zip` | 559,194 | `555b9fa641a2a5be…` | 76 |
| `Vyomaraj-Handover-V16.7.7-v177.zip` | 559,421 | `ff2c5697dd3def58…` | 76 |
| `Vyomaraj-Handover-V16.7.8-v178.zip` | 575,383 | `ccb052d73da329a7…` | 82 |
| `Vyomaraj-Handover-V16.7.9-v179.zip` | 577,794 | `fbc983103126efef…` | 83 |
| `Vyomaraj-All-Chats-From-Arena-Database-Till-V16.7.22.zip` | 5,314 | `d7018a01b394f897…` | 3 |
| `Vyomaraj-App.apk` | 24,567,022 | `948e60b03ed62b8b…` | — |
| `Vyomaraj-Complete-All-Sessions-All-Handover-Zips-V16.7.22.zip` | 13,048,185 | `05e38de17a3481cf…` | 31 |
| `Vyomaraj-V10.0-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V11.0-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V12.0-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V12.1-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V13.0-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V14.0-Final-Market-Ready.zip` | 28,963,815 | `c0b12507910381ba…` | 38 |
| `Vyomaraj-V15.0-Final-Market-Ready.zip` | 29,088,017 | `cb3cba59b376e46b…` | 48 |
| `Vyomaraj-V15.1-Final-Market-Ready.zip` | 29,092,780 | `24d206172bac4a93…` | 53 |
| `Vyomaraj-V6.6-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V6.7-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V6.8-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V6.9-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V7.0-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V8.0-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |
| `Vyomaraj-V9.0-Final-Market-Ready.zip` | 28,907,765 | `6d2aa682a2e4fb6f…` | 34 |

### Product surface on disk

| File | Bytes |
|---|---|
| `index.html` | 12,906 |
| `Index.html` | 12,761 |
| `landing.html` | 691 |
| `flow-diagram.html` | 61,992 |
| `demo.html` | 6,354 |
| `launch.css` | 11,337 |
| `launch.js` | 1,841 |
| `demo.css` | 7,077 |
| `demo.js` | 11,660 |
| `manifest.webmanifest` | 740 |
| `sw.js` | 1,708 |
| `offline.html` | 1,107 |

### The one-month chat record

- File: `Vyomaraj-All-Chats-Database-One-Month.md` (16,879 bytes)
- Discrepancy already recorded and served at `/reports/chats`: heading says 28 chats, file contains 34 numbered entries
- All-Chats-Extraction-Error.txt inside the chats zip records that `git show origin/main~4:index.html` failed (exit 128): the raw chat transcripts were never exported. What exists is the consolidated one-month notes, plus the Git commit list and the 25 handover and 15 market-ready archives.

**Nothing is missing, and nothing more exists than this.** The consolidated notes, the commit list, and all 25 handover plus 15 market-ready archives are in the repository and served. Raw per-chat transcripts are the one thing that was never exported — the extraction error above is why — so no future session should promise to "recover" them from this repository.

## 3. Verified here vs claimed in a document

**Claimed in `README_MARKET_READY.md` (V15.1) or the V10.0 investigation note, with nothing running behind it in this checkout.** Do not repeat these as live:

| Claim | Where it is claimed |
|---|---|
| PostgreSQL on 5432 | README_MARKET_READY.md V15.1 ports registry |
| Redis on 6379 | README_MARKET_READY.md V15.1 ports registry |
| FastAPI backend on 8000 | README_MARKET_READY.md V15.1 ports registry |
| Flask API on 5000 | README_MARKET_READY.md V15.1 ports registry |
| HTTPS 443 / HTTP 80 listeners | README_MARKET_READY.md V15.1 ports registry |
| Social platform APIs configured (YouTube, Instagram, Facebook, X, Telegram, WhatsApp, Discord, Pinterest, Threads, Snapchat, Reddit, Twitch, Vimeo, Tumblr, Mastodon) | README_MARKET_READY.md V15.1 social registry |
| Panch-Shakti metadata labels/rosters stating ACTIVE or all agents LIVE | ops/hanuman/hanuman-panch-shakti.json, devices.json, and ports.json; these are declarations, not runtime probes |
| Revenue, follower and MRR figures (₹3.0L, 56.2K, ₹1,29,000, 5.42M views, ₹8.4L, ₹5.67L, 2B UPI, 94.6K) | README_MARKET_READY.md V15.1 social registry |
| ElevenLabs voice cloning, Twilio calling, Whisper captions, 4K60 video synthesis | REAL_VYOMARAJ_INVESTIGATION.md V10.0 plan and README_MARKET_READY.md |
| MediaPipe Face Mesh / face generation | REAL_VYOMARAJ_INVESTIGATION.md V9-V10 notes |
| Multi-AI provider coordination as a live bus | ops/vyomaraj-core/multi-ai-coordination.js states in its own header that it is metadata-only and that historical versions fabricated LIVE values |
| SearXNG + Ollama research runtime | ops/vyomaraj-core/research/ — discovery is local; the provider runtime is not active |

Everything in section 1 is the implemented repository stack: static pages, Python standard-library servers, GitHub Pages, GitHub Actions workflow definitions, a Git-snapshot replication mechanism, local planners, and browser APIs. The scheduled Actions check at `2026-10-07T10:13:11Z` (run `37605789908` / check `112741170924`) reports `status=MATCH`, `data_match=True`, equal tracked trees `986288ee2cc4ec4d89400320150ea893f7a7a2de` / `986288ee2cc4ec4d89400320150ea893f7a7a2de`, and traffic `NONE`. The workflow-selected target identity `UNCONFIRMED: an Actions variable may override the in-repo fallback and is unreadable here` is not independently confirmed (Actions settings API 403; candidate paths 404 are ambiguous). This does not prove runtime/app equality, site failover, RPO or RTO; issue #6 stays OPEN/P0.

## 4. Links: what lasts and what dies

| Class | Example | Status | Note |
|---|---|---|---|
| GitHub repository | `https://github.com/Vyomaraj1356/Vyomarajai` | **WORKING** | Durable; every artifact in this record lives here. |
| GitHub Pages | `https://vyomaraj1356.github.io/Vyomarajai/` | **WORKING (main only)** | Live read 2026-10-07: Pages source is `main:/` at 04b7ae60; the current feature branch is not deployed there. |
| Raw file URLs | `https://raw.githubusercontent.com/Vyomaraj1356/Vyomarajai/main/<path>` | **WORKING** | Serve any committed file on main. A file is only reachable after its pull request is merged. |
| Arena session links | `https://arena.ai/agent/<session-id>` | **SESSION-SCOPED / DIES** | REAL_VYOMARAJ_INVESTIGATION.md records earlier session links returning "Something went wrong". They are not storage; the repository is. |
| Sandbox preview links | `https://<port>-<sandbox>.e2b.app` | **SESSION-SCOPED / DIES** | Every preview host from every session so far has died with its sandbox (4190, 4174-...). Never announce one as the launch address. |
| Local studio/gateway rehearsal ports | `127.0.0.1:4176 / 4181 / 4182 (defaults; loopback policy enforced)` | **LOCAL-ONLY / NOT RUNNING** | Studio/gateway refuse non-loopback binds; privileged writer actions require request-scoped owner tokens; do not expose through public ingress. |
| Allowlisted sandbox landing + planner demo | `0.0.0.0:5310` | **SESSION-SCOPED / READ-ONLY CATALOG + PLANNER** | Exact asset allowlist plus GET /api/catalog for curated entries from two local packs and ephemeral POST /api/plan; no provider calls, visitor-data persistence, privileged writers or private paths. This is not a public deployment or production health signal. |

## 5. The zero-cost launch path (no money spent)

| Need | Free route | Cost | Limit to state honestly |
|---|---|---|---|
| Public address | GitHub Pages from `main:/` at `04b7ae60` | ₹0 | This feature branch is not deployed; static files only, no server-side runtime |
| Automation + DR | Scheduled run `37605789908` reports equal tracked Git trees | ₹0 | Effective target identity `UNCONFIRMED: an Actions variable may override the in-repo fallback and is unreadable here` remains unconfirmed; runtime/failover/RPO/RTO are not proven |
| App distribution | Existing APK v2 signing-block entry; signature validity not established | ₹0 tooling | Run `apksigner verify`, confirm signer provenance, then test installation on a real device before distributing; never treat block presence alone as proof |
| Local dry runs | Five legacy Python preview services plus the allowlisted :5310 demo are defined | ₹0 | Port 5310 is a session-scoped preview; listener state is transient and deliberately not persisted in this generated record.; session-only rehearsal, not production |
| Voice enrollment | On-device only, consent screen + delete control | ₹0 | No cloud vendor, no cloning, no identity-document capture in the app |
| Payments | None until revenue exists | ₹0 | No gateway, no UPI integration; do not advertise payments |

**When Vyomaraj earns, this is the order to buy in** (cheapest first, each one unlocking something the free stack cannot do):

1. **A domain** — the launch address stops depending on `github.io`.
2. **A small always-on host** — the Python services run outside a sandbox, with a supervisor and a health check the owner can read from a phone.
3. **Runtime database backup or object storage** — Git-snapshot replication does not cover the SQLite/JSON state.
4. **Payments/KYC** — only with a real gateway account and a legal read.
5. **A voice/video vendor** — only with a signed data-processing agreement, replacing the on-device enrollment.
6. **Play Console (one-time)** — signed release builds and store listing.
7. **CDN / media hosting** — only when there is licensed or owned media to serve.

Every step above is a purchase decision for the owner and is not assumed here. The 11 October 2026 date remains a target; owner-approved DR access, branch review/deployment and release checks are separate gates.

END OF STACK AND PLATFORM RECORD
