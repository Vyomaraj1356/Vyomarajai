# VYOMARAJ — FULL HANDOVER, ALL DETAILS

Generated 2026-10-06 10:37 UTC from this repository and from live probes of the running services. Everything here is checkable: each section says where it came from, and the archive beside this file carries the sources themselves.

**One command rebuilds this document and its archive:** `python3 ops/vyomaraj-core/handover/build_full_handover.py` — `--check` verifies the checked-in copy still matches the repository and the probes.

---

## 1 · Real-time state at generation

| Port | Service | Live now |
|---|---|---|
| 3000 | product page (static http.server) | **open** |
| 4174 | reports viewer | **open** |
| 4176 | availability gateway | **open** |
| 4181 | lane studio A | **open** |
| 4182 | lane studio B | **open** |

The live view of this table is served at `/reports/realtime` on the viewer, both lane studios and the gateway — it re-probes on every load and refreshes itself every 10 seconds, so what you read there is the state at that moment, not a recording.

---

## 2 · Chats — every session since the first Arena session

- `Vyomaraj-All-Chats-Database-One-Month.md` — 16,879 bytes. Its heading says **28 chats**; the body carries **34 numbered entries**. That discrepancy is pre-existing and is served unmodified at `/reports/chats` rather than smoothed over.
- `Vyomaraj-All-Chats-From-Arena-Database-Till-V16.7.22.zip` — the archive copy.
- `Vyomaraj-Complete-All-Sessions-All-Handover-Zips-V16.7.22.zip` — all sessions, all handover zips.

---

## 3 · All agents, sub-agents and hubs

| Tier | Count | Source |
|---|---|---|
| Main agents | **13** | owner-approved registry, categories below |
| Sub-agents | **128** (42 named, 86 unnamed) | `AGENT_REGISTRY_CURRENT.json` |
| Third tier (hubs) | **6** | only the six explicitly approved hubs acquire child edges |
| Products | **421** historical | *not a verified current inventory* |

### The 13 main agents and their sub-agents

| # | Main agent | Sub-agents | Historical products reported |
|---|---|---|---|
| 1 | **Food & Social Connect** (`FOOD`) | 3 | 6 |
| 2 | **Education** (`EDU`) | 16 | 68 |
| 3 | **Astro-Celestial & Universal** (`ASTRO`) | 3 | 9 |
| 4 | **Finance & Wealth** (`FINANCE`) | 7 | 15 |
| 5 | **Life Coach & Wellness** (`LIFE`) | 10 | 34 |
| 6 | **Bhakti Mandir — Ritual, Festival & Grantha** (`BHAKTI`) | 3 | 8 |
| 7 | **Sports & Legends** (`SPORTS`) | 14 | 29 |
| 8 | **Agriculture & Environment** (`AGRI`) | 6 | 14 |
| 9 | **Entertainment — Comedy, Movies, Hollywood, Bollywood** (`ENTERTAINMENT`) | 32 | 168 |
| 10 | **Platform & Social Hub + Earn — All Platforms + Monetization** (`PLATFORM`) | 20 | 39 |
| 11 | **Tour and Travel** (`TOUR`) | 4 | 9 |
| 12 | **War Room — Warriors** (`WAR`) | 5 | 13 |
| 13 | **Podcast & Entertainment Studio** (`PODCAST`) | 5 | 9 |

### The six approved hubs (the only third tier)

| From | Hub | Registry id |
|---|---|---|
| ENTERTAINMENT | Comedy hub | `ENT-HUB-COM` |
| ENTERTAINMENT | Cartoon | `ENT-HUB-CARTOON` |
| ENTERTAINMENT | Music | `ENT-HUB-MUS` |
| ENTERTAINMENT | Movie | `ENT-HUB-MOVIE` |
| ENTERTAINMENT | Wit | `ENT-HUB-WIT` |
| ENTERTAINMENT | Shayari | `ENT-HUB-SHAYARI` |

Hierarchy policy, verbatim from the registry: *Only the six explicitly approved hubs acquire child edges. Other missing sub-sub-agent mappings remain UNMAPPED; do not invent a third tier.*

Display policy, verbatim: *Show unnamed entries by serial only; null names remain unassigned. Display serials are not recovered slot identities.*

### The 42 named sub-agents

| id | Name | Category | Kind |
|---|---|---|---|
| `EDU-S1` | Veda Rishi | EDU | sub_agent |
| `EDU-S2` | Upanishad Guru | EDU | sub_agent |
| `EDU-S3` | Gita Acharya | EDU | sub_agent |
| `EDU-S4` | Mythology & Mystery Rishi | EDU | sub_agent |
| `EDU-S5` | Vyomaraj Picker | EDU | sub_agent |
| `EDU-S6` | Lectures Hub | EDU | sub_agent |
| `EDU-S7` | Short Notes | EDU | sub_agent |
| `EDU-S14` | Care & Bikes — Bicycles & Two-Wheelers | EDU | sub_agent |
| `EDU-S15` | Social Thinkers, Visionaries & Legends | EDU | sub_agent |
| `EDU-GOV-S1` | Government Schemes | EDU | sub_agent |
| `BHAKTI-AGHOR-S1` | Aghor & Aghori | BHAKTI | sub_agent |
| `ENT-INDICOM` | INDICOM | ENTERTAINMENT | sub_agent |
| `ENT-CRITICISM` | Criticism gate | ENTERTAINMENT | sub_agent |
| `PLATFORM-REF-01` | YouTube | PLATFORM | sub_agent |
| `PLATFORM-REF-02` | Instagram | PLATFORM | sub_agent |
| `PLATFORM-REF-03` | Facebook | PLATFORM | sub_agent |
| `PLATFORM-REF-04` | TikTok | PLATFORM | sub_agent |
| `PLATFORM-REF-05` | X | PLATFORM | sub_agent |
| `PLATFORM-REF-06` | LinkedIn | PLATFORM | sub_agent |
| `PLATFORM-REF-07` | Telegram | PLATFORM | sub_agent |
| `PLATFORM-REF-08` | WhatsApp | PLATFORM | sub_agent |
| `PLATFORM-REF-09` | Discord | PLATFORM | sub_agent |
| `PLATFORM-REF-10` | Pinterest | PLATFORM | sub_agent |
| `PLATFORM-REF-11` | Threads | PLATFORM | sub_agent |
| `PLATFORM-REF-12` | Snapchat | PLATFORM | sub_agent |
| `PLATFORM-REF-13` | Reddit | PLATFORM | sub_agent |
| `PLATFORM-REF-14` | Twitch | PLATFORM | sub_agent |
| `PLATFORM-REF-15` | Vimeo | PLATFORM | sub_agent |
| `PLATFORM-REF-16` | Tumblr | PLATFORM | sub_agent |
| `PLATFORM-REF-17` | Mastodon | PLATFORM | sub_agent |
| `PLATFORM-REF-18` | EARN | PLATFORM | sub_agent |
| `PLATFORM-REF-19` | AI | PLATFORM | sub_agent |
| `WAR-REF-01` | PAST | WAR | sub_agent |
| `WAR-REF-02` | HISTORY | WAR | sub_agent |
| `WAR-REF-03` | PRESENT | WAR | sub_agent |
| `WAR-REF-04` | FUTURE | WAR | sub_agent |
| `WAR-REF-05` | CROSS-CUTTING | WAR | sub_agent |
| `PODCAST-REF-01` | RESEARCH | PODCAST | sub_agent |
| `PODCAST-REF-02` | SCRIPT | PODCAST | sub_agent |
| `PODCAST-REF-03` | PRODUCE | PODCAST | sub_agent |
| `PODCAST-REF-04` | ANALYSIS | PODCAST | sub_agent |
| `PODCAST-REF-05` | PUBLISH | PODCAST | sub_agent |

The remaining 86 sub-agents are numbered slots with names not yet assigned. The registry keeps them as serials rather than inventing names.

---

## 4 · AI platforms, context and connections

What the coordination module itself declares (its own header: *"Metadata-only compatibility surface, not a provider or device-control client"*):

| Platform id | Declared name | Declared status | Actually connected? |
|---|---|---|---|
| `arena` | Arena.ai | `UNVERIFIED` | **no** — no client, no credential, no call |
| `primary` | GitHub primary | `UNVERIFIED` | **yes** — repository/host this project runs on |
| `secondary` | GitHub recovery repository | `UNVERIFIED` | **yes** — repository/host this project runs on |
| `local` | Local preview | `UNVERIFIED` | **yes** — repository/host this project runs on |
| `chatgpt` | ChatGPT | `UNVERIFIED` | **no** — no client, no credential, no call |
| `claude` | Claude | `UNVERIFIED` | **no** — no client, no credential, no call |
| `gemini` | Gemini | `UNVERIFIED` | **no** — no client, no credential, no call |

The module's own health function returns `mode: metadata_only`, `operational: false`, `currentLoad: null`, `confidence: UNVERIFIED`, and its `switchPlatform` / `shareLoadWith` functions return `BLOCKED` with the reason *"No provider/session-transfer executor is configured."* Nothing here transfers work between AI platforms.

### The V15.1 port file — claim vs live probe

`ops/hanuman/ports.json` declares `allPortsEnabled: True`, `allPortsActive: True`, `allPortsLive: True`. Probed on this host at generation time:

| Port | Claimed service | Declared status | Live now |
|---|---|---|---|
| 3000 | Website V15.1 Preview http.server | ENABLED ACTIVE LIVE | **open** |
| 443 | HTTPS — All Social Platforms YouTube Instagram Facebook Ti | ENABLED ACTIVE LIVE | **closed** |
| 80 | HTTP Redirect to HTTPS | ENABLED ACTIVE LIVE | **closed** |
| 5432 | PostgreSQL — jarvis_phones platforms tables — CRUD API POS | ENABLED ACTIVE LIVE | **closed** |
| 6379 | Redis Cache — Session Transfer State Sync Heartbeat | ENABLED ACTIVE LIVE | **closed** |
| 8000 | FastAPI Backend — Jarvis 24x7 Bharat-Laxman Hanuman Qualit | ENABLED ACTIVE LIVE | **closed** |
| 5000 | Flask API — Social Platforms All Enabled | ENABLED ACTIVE LIVE | **closed** |

Ports 80 and 443 are claimed live for *"All Social Platforms"*. Nothing in this repository binds them, and unprivileged processes cannot. Treat that file as intent, not as telemetry.

### The V15.1 social file — 23 platforms, all figures unverified

`ops/hanuman/social-platforms.json` records handles and figures. Not one of them is verified by this repository, and no code connects to any platform:

| Platform | Recorded handle string (verbatim, unverified) |
|---|---|
| youtube | @Vyomaraj — 18.9K members — Channel ID UC... — MRR ₹3.0L — Best Scene Shorts 30 sec fair use 9:1 |
| instagram | @Vyomaraj — 56.2K followers — Reels 90 sec 9:16 Remix Reels Best Scene Affiliate links bio linkt |
| facebook | @Vyomaraj — 38.4K followers — FB Reels Bonus Reels Play FB/IG Bonus ₹1,29,000 +12% — API Faceboo |
| tiktok | @Vyomaraj — TikTok Short video 15-60 sec trending audio — API TikTok API |
| x | @Vyomaraj — X API v2 Tweets threads 280 chars Brand pitch analytics 5.42M views |
| linkedin | @Vyomaraj — B2B brand collab 12 leads ₹8.4L — API LinkedIn API |
| telegram | @VyomarajBot — 28.5K MRR ₹5.67L Subscription funnel Free Reel best scene 30 sec → Link → Telegra |
| whatsapp | Vyomaraj WhatsApp Business API — 2B UPI + Razorpay Nurture Day1 Veda fact Day3 Gold tip Day5 bes |
| discord | Vyomaraj Discord — Community 94.6K FB+IG — API Discord API |
| pinterest | Vyomaraj Pinterest — Pins boards affiliate — API Pinterest API |
| threads | Vyomaraj Threads — Text posts 500 chars — API Threads API |
| snapchat | Vyomaraj Snapchat — Snap Kit API Spotlight 60 sec — API Snapchat Snap Kit |

The follower counts, view counts and revenue figures in that row set — and in `README_MARKET_READY.md` — are the same class of claim this project already removed from its JavaScript. Do not repeat them to a partner, a bank or a platform reviewer until a platform dashboard shows them.

### What connects to a platform today

| Route | State |
|---|---|
| GitHub (primary repo, Pages, Actions) | **connected** — authenticated in this sandbox |
| Landing page → lane studios / gateway | **connected** — same host |
| YouTube / Instagram / Facebook / X / LinkedIn / TikTok / Telegram… | **not connected** — 0 API clients, 0 tokens, 0 upload calls |
| Payment gateways | **not connected** — 0 integrations |
| Analytics | **not connected** — 0 counters |
| AI providers (OpenAI, Anthropic, Google) | **not connected** — 0 calls; planners state `ai_calls_made=false` |

---

## 5 · Configuration — Vyomaraj and Jarvis

### Configuration — Vyomaraj (the product and its servers)

| Component | Setting |
|---|---|
| Public address | `https://vyomaraj1356.github.io/Vyomarajai/` — GitHub Pages from `main`, free |
| Palette | Shani Blue `#0a1628`, Kuber Gold `#f59e0b` |
| Product pages | `index.html`, `landing.html`, `flow-diagram.html` — static, no framework |
| Port 3000 | product page (static http.server) — **up** |
| Port 4174 | reports viewer — **up** |
| Port 4176 | availability gateway — **up** |
| Port 4181 | lane studio A — **up** |
| Port 4182 | lane studio B — **up** |
| Server runtime | Python 3 standard library only (`http.server` / `ThreadingHTTPServer`), binds `0.0.0.0` |
| Storage | JSON + SQLite files on disk; **no database server** |
| Content packs | music 107 · film 59 · bhakti 47 · comics 22 · pairings 28 · aghor 44 records |
| Agents surface | `/agents/` and `CONTENT_INDEX_CURRENT.json` — 13 categories, 128 slots |
| Reports surface | 30+ viewer routes, all checked by `verify_live_wiring.py` |
| Security headers | `Content-Security-Policy` with `default-src 'none'`, `img-src 'self'` on the viewer |
| APK | `Vyomaraj-App.apk`, 24,567,022 B, **unsigned** — Android refuses it until signed |

### Configuration — Jarvis (the device/presence layer)

`ops/jarvis/devices.json` (version V15.1) carries keys: `version`, `owner`, `shriRamJi`, `hanumanJi`, `panchShakti`, `bharat`, `hanumanQuality`, `laxman`, `relationship`, `currentHome`.

| Jarvis item | State |
|---|---|
| `ops/jarvis/jarvis-24x7-controller.sh` | present — a shell controller, **not running in this sandbox** |
| `ops/jarvis/jarvis.env.example` | present — template only; the real `jarvis.env` is **never** included in any handover |
| Jarvis voice | Web Speech API on the visitor's device (browser), permission-gated |
| Jarvis enrollment | on-device only, `uploads_enabled: false`, delete-my-voice supported |
| Jarvis as a running service | **not running** — no process, no port, no scheduler in this repository |

So: Vyomaraj is configured and live as pages and local servers. Jarvis is configured as **records, policy and browser features** — there is no always-on Jarvis process yet, and an always-on process is exactly what the "buy when Vyomaraj earns" list is for.

---

## 6 · Research: issues found, resolved and fixed

| Item | State found | Action taken |
|---|---|---|
| Issue #6 — Unblock private DR access | OPEN, ledger verdict **READY_TO_CLOSE** | close-out comment prepared and held for owner confirmation; nothing sent |
| PR #27 — replication gate + companion | OPEN, this session's branch | ready to merge; merging fires `verify-or-sync` |

Found and fixed while researching this handover:

| Issue | Fix |
|---|---|
| `landing.html` polled `/api/sync/status` every 4s and POSTed `/api/sync/trigger` every 2 min against routes no server implements → the status box hung on "Loading sync status…" forever and every visitor produced a 404 storm | the servers now answer a real `/api/sync/status` built from checked-in DR evidence, the page states one true line, the fake "Master Sync Now" button is gone, and the polling loop is removed |
| the same box displayed "6 sub-agents syncing together" — a value nothing produces | replaced with the repository's own evidence date and the plain statement that replication is a GitHub Actions job |
| `flow-diagram.html` depends on a CDN for Mermaid | recorded: on a network that blocks the CDN, all 6 diagrams render 0 SVGs and the visitor sees raw source text |
| the capture gallery's images were blocked by the hardened CSP | fixed with `img-src 'self'` — same-origin only |

---

## 7 · What is in the downloadable archive

`transfer/VYOMARAJ_FULL_HANDOVER_2026_10_06.zip` carries 29 files:

| File | Bytes |
|---|---|
| `ops/vyomaraj-core/handover/VYOMARAJ_FULL_HANDOVER_2026_10_06.md` | 17,637 |
| `Vyomaraj-All-Chats-Database-One-Month.md` | 16,879 |
| `VYOMARAJ_REPOSITORY_MAP.md` | 1,723 |
| `REAL_VYOMARAJ_INVESTIGATION.md` | 12,822 |
| `ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json` | 61,050 |
| `ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json` | 73,517 |
| `ops/vyomaraj-core/handover/INHERITANCE_AUDIT_2026_10_04.md` | 4,565 |
| `ops/vyomaraj-core/handover/STACK_AND_PLATFORM_RECORD_2026_10_06.md` | 13,312 |
| `ops/vyomaraj-core/handover/LINK_AND_ARCHIVE_LEDGER_2026_10_06.json` | 16,963 |
| `ops/vyomaraj-core/handover/MARKET_READINESS_AND_WIRING_2026_10_06.md` | 12,176 |
| `ops/vyomaraj-core/handover/NAVARATRI_GO_LIVE_PLAN_2026_10_11.md` | 13,508 |
| `ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.png` | 589,897 |
| `ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg` | 19,995 |
| `ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md` | 8,321 |
| `ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json` | 11,255 |
| `ops/vyomaraj-core/handover/LIVE_WIRING_STATE_2026_10_06.json` | 36,280 |
| `ops/vyomaraj-core/handover/PREVIEW_VERIFICATION_2026_10_04.json` | 35,574 |
| `ops/vyomaraj-core/handover/TEST_EVIDENCE_2026_10_04.json` | 29,010 |
| `ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md` | 20,763 |
| `ops/vyomaraj-core/governance/VOICE_ENROLLMENT_POLICY.json` | 893 |
| `ops/vyomaraj-core/experience/CONTENT_EXTENSIONS.json` | 4,188 |
| `ops/jarvis/devices.json` | 51,494 |
| `ops/jarvis/jarvis.env.example` | 3,800 |
| `ops/hanuman/ports.json` | 4,540 |
| `ops/hanuman/social-platforms.json` | 12,887 |
| `ops/vyomaraj-core/handover/screenshots/SCREENSHOT_CAPTURE_RAW.json` | 5,643 |
| `ops/vyomaraj-core/handover/screenshots/product-page.jpg` | 83,747 |
| `ops/vyomaraj-core/handover/screenshots/lane-music.jpg` | 112,856 |
| `ops/vyomaraj-core/handover/screenshots/report-network-diagram.jpg` | 1,040,321 |

`ops/jarvis/jarvis.env` is deliberately **not** in the archive: it is the one file that may hold credentials, and handover artifacts in this project stay reviewable and non-secret.

---

## 8 · Verdict and the next three actions

| Question | Answer |
|---|---|
| Is Vyomaraj equipped to go live on 11 October? | **Yes** on the free route — Pages is built, the lanes are real, the gates are green |
| Is everything in the vision connected? | **No** — the 22 platforms, payments, analytics and AI providers are records, not connections |
| Is Jarvis running 24×7? | **No** — records, policy and browser voice; no process |
| Will it earn on day one? | **No** — see the three wirings below |

**Next three actions, all free, all owner decisions:** sign the APK with your own `keytool` key · put a contact address on the page · switch on a free analytics counter. Then hand-publish the first episodes and apply to the YouTube Partner Program before 1 February 2027, when new applicants need 8,000 watch hours instead of 4,000.

