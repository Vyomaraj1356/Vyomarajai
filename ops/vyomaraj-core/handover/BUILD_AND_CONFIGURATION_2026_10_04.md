# Vyomaraj — build, configuration and inventory — 2026-10-04

Generated from the checked-in registry, content and configuration files by `build_configuration_report.py`; every number below is read from those files, not transcribed. This is a structural inventory, **not** runtime readiness: no sub-agent, provider or revenue channel is claimed operational.

## 1. Agents — current owner-approved structure

- Registry status: `CURRENT_OWNER_APPROVED_STRUCTURE_not_runtime_inventory` (updated 2026-10-03)
- Main agents: **13** · counted sub-agent slots: **128** · named: **42** · serial-only (name UNKNOWN): **86**
- Uncounted parent headings: **6** · historical reported products: **421** (active product count: None — not reconciled, deliberately not zero)
- Source snapshot: `handover/AGENT_CONTENT_REGISTRY_V16_7_24.json` (sha256 `9e301bfcb1c6e8b23c1bea4fbdcf0d9d12d4c457fe62d7ef60e3161ac3a908a9`); historical arithmetic validated: True

| Main agent | Current sub-agents | Historical snapshot | Change | Named | Serial-only |
|---|---:|---:|---|---:|---:|
| FOOD — Food & Social Connect | 3 | 3 | unchanged | 0 | 3 |
| EDU — Education | 16 | 15 | +1 | 10 | 6 |
| ASTRO — Astro-Celestial & Universal | 3 | 3 | unchanged | 0 | 3 |
| FINANCE — Finance & Wealth | 7 | 8 | -1 | 0 | 7 |
| LIFE — Life Coach & Wellness | 10 | 10 | unchanged | 0 | 10 |
| BHAKTI — Bhakti Mandir — Ritual, Festival & Grantha | 3 | 2 | +1 | 1 | 2 |
| SPORTS — Sports & Legends | 14 | 14 | unchanged | 0 | 14 |
| AGRI — Agriculture & Environment | 6 | 6 | unchanged | 0 | 6 |
| ENTERTAINMENT — Entertainment — Comedy, Movies, Hollywood, Bollywood | 32 | 38 | -6 | 2 | 30 |
| PLATFORM — Platform & Social Hub + Earn — All Platforms + Monetization | 20 | 20 | unchanged | 19 | 1 |
| TOUR — Tour and Travel | 4 | 4 | unchanged | 0 | 4 |
| WAR — War Room — Warriors | 5 | 5 | unchanged | 5 | 0 |
| PODCAST — Podcast & Entertainment Studio | 5 | 5 | unchanged | 5 | 0 |

### Approved structural changes carried in this registry

- **ENTERTAINMENT 38 → 32**: six hubs (Comedy, Cartoon, Music, Movie, Wit, Shayari) were reclassified from counted sub-agents to uncounted parent headings — kept, not deleted.
- **FINANCE 8 → 7 and EDU 15 → 16**: the Government Schemes position moved from FINANCE to EDU as one owner-approved transfer (`EDU-GOV-S1`).
- **BHAKTI 2 → 3**: `BHAKTI-AGHOR-S1` (Aghor & Aghori) added as an explicitly requested, view-only editorial route — not a deployed autonomous teacher.

### Named sub-agents (current)

- **EDU**: EDU-S1 Veda Rishi; EDU-S2 Upanishad Guru; EDU-S3 Gita Acharya; EDU-S4 Mythology & Mystery Rishi; EDU-S5 Vyomaraj Picker; EDU-S6 Lectures Hub; EDU-S7 Short Notes; EDU-S14 Care & Bikes — Bicycles & Two-Wheelers; EDU-S15 Social Thinkers, Visionaries & Legends; EDU-GOV-S1 Government Schemes
- **BHAKTI**: BHAKTI-AGHOR-S1 Aghor & Aghori
- **ENTERTAINMENT**: ENT-INDICOM INDICOM; ENT-CRITICISM Criticism gate
- **PLATFORM**: PLATFORM-REF-01 YouTube; PLATFORM-REF-02 Instagram; PLATFORM-REF-03 Facebook; PLATFORM-REF-04 TikTok; PLATFORM-REF-05 X; PLATFORM-REF-06 LinkedIn; PLATFORM-REF-07 Telegram; PLATFORM-REF-08 WhatsApp; PLATFORM-REF-09 Discord; PLATFORM-REF-10 Pinterest; PLATFORM-REF-11 Threads; PLATFORM-REF-12 Snapchat; PLATFORM-REF-13 Reddit; PLATFORM-REF-14 Twitch; PLATFORM-REF-15 Vimeo; PLATFORM-REF-16 Tumblr; PLATFORM-REF-17 Mastodon; PLATFORM-REF-18 EARN; PLATFORM-REF-19 AI
- **WAR**: WAR-REF-01 PAST; WAR-REF-02 HISTORY; WAR-REF-03 PRESENT; WAR-REF-04 FUTURE; WAR-REF-05 CROSS-CUTTING
- **PODCAST**: PODCAST-REF-01 RESEARCH; PODCAST-REF-02 SCRIPT; PODCAST-REF-03 PRODUCE; PODCAST-REF-04 ANALYSIS; PODCAST-REF-05 PUBLISH

Serial-only entries are shown in the viewer as `REF`/serial identifiers (`display_policy`: Show unnamed entries by serial only; null names remain unassigned. Display serials are not recovered slot identities.). Hierarchy: Only the six explicitly approved hubs acquire child edges. Other missing sub-sub-agent mappings remain UNMAPPED; do not invent a third tier.

## 2. Contents

- Indexed references: **173** (Current indexed references, not the complete historical 421 products or an exhaustive archive-content audit.)
- Education topics: **21** · historical catalog files: **32** unique paths (32)
- Deduplication: Exact identity + equal source record only. Conflicts stop rebuild; similar titles, different editions or source contexts are not silently merged.
- Ownership: education = EDU, government schemes = EDU

| Experience route | Content counts |
|---|---|
| Aghor & Aghori (`/aghor/`) | chapters 14, people 7, practices 6, care 6, sources 11, timeline 6 |
| Bhakti-Shakti (`/bhakti/`) | stories 12, avatars 10, peethas 9, recipes 3, sources 13 |
| Roots & Pairings (no-alcohol by default) (`/pairings/`) | traditions 8, research_backlog 8, snacks 8, events 3, sources 9 |
| Music & media (`/music/`) | agents 6, items 39, sources 27 |
| Film & stage (`/film/`) | agents 6, items 27, sources 25, formats 7 |

- Ingested content packs: ops/vyomaraj-core/food-agent (9 files), ops/bhakti-shakti (20 files), ops/hanuman (3 files) — Repository file/module inventory only. This is not an item-level catalog of the 421 registry products, and it does not import source-file contents into the planner.
- Readiness note: Registry-reported readiness figures are preserved separately and are not reconciled to the 421 product total without owner clarification.

## 3. Vyomaraj configuration

- `LOCAL_INTEGRATION.json`: status `local_preview_planning_only`, roles — Vyomaraj: Validate experience/topic/preferences and assemble the local content route. Jarvis: Prepare a deterministic handoff with source references, unresolved mappings and review gates.
- Planning endpoint `/api/plan`; experiences bhakti, liquor-bar, music, film, aghor; modes 3d, 4d, 5d
- Flags: automatic AI calls False, automatic publishing False, legacy Jarvis env loaded False, production deployed False
- `PUBLIC_POLICY.json` (updated 2026-10-03): spiritual content mode `view_only_not_practice_instruction`, participation `voluntary_no_pressure_no_required_belief_or_practice`
- `DR_POLICY.json`: secondary `deepakGoyal1356/Vyomaraj-Agent-6d64e`, writer `primary_main_only`, sync approved on main `True`, automatic target-only removal `False`, reverse overwrite `False`, zero-RPO/RTO verified False/False
- Scope guard: Git main snapshot only; not runtime databases, secret stores, live media sessions or production traffic

### Workflows

| File | Name | Schedule |
|---|---|---|
| `vyomaraj-ci-diagnostics.yml` | Vyomaraj CI diagnostics (readable annotations) | `no schedule` |
| `vyomaraj-research.yml` | Vyomaraj Metadata Discovery | `15 3 * * *` |
| `vyomaraj-sync-both.yml` | Vyomaraj PRIMARY to DR Sync | `*/30 * * * *` |

## 4. Jarvis configuration

- `ops/jarvis/jarvis.env` — configuration **key names only, no values are printed or copied**: BHARAT, HANUMAN_QUALITY, JARVIS_CLOUD_HOME, JARVIS_EDGE_HOME, JARVIS_FUTURE_HOME, JARVIS_FUTURE_HOME_DESC, JARVIS_FUTURE_HOME_STATUS, JARVIS_HEARTBEAT_INTERVAL, JARVIS_HEARTBEAT_URL, JARVIS_LOCK_FILE, JARVIS_PRIMARY_DEVICE, JARVIS_PRIMARY_NUMBER, JARVIS_PRIMARY_ROLE, JARVIS_PRIMARY_STATUS, JARVIS_SECONDARY_DEVICE, JARVIS_SECONDARY_NUMBER, JARVIS_SECONDARY_STATUS, JARVIS_STATE_FILE, JARVIS_TEST, LAXMAN, RELATIONSHIP, SCALABLE_TECH, SHRI_RAM_JI, TRENDS
- `ops/jarvis/devices.json` — 51428 bytes, primary/secondary device-number configuration. Values stay in the repository; they are not reproduced here.
- `ops/jarvis/jarvis-24x7-controller.sh` — controller script; not started as an unattended service in this session, and no switch/fencing URL in it was called.
- Local roles: the two preview replicas act as the Vyomaraj and Jarvis sides of the availability rehearsal (`ops/availability/README.md`); both share one host and one queue.

## 5. Recorded verification evidence

- **Preview verification** (`ops/vyomaraj-core/handover/PREVIEW_VERIFICATION_2026_10_04.json`): 13 viewer route checks, 11 gateway route checks, problems: none
- **Primary-secondary verification** (`ops/dr/DEPLOYED_MATCH_2026_10_04.json`): 14 checkpoints; current state: This file covers the 2026-10-03 and 2026-10-04 runs through merge #19 — the merge that delivered this rebuild — and is closed there on purpose: every later merge is verified by the same workflow and its result is visible in the live check-run annotations. Every checkpoint recorded here is status=MATCH with identical primary and secondary trees; 10 of the 14 carried a replication write (rollback_commit present). A run that finds the snapshots already equal carries no rollback_commit and is an idempotent no-op, not a failure. The one BLOCKED run (#11) is documented separately and is deliberately not counted as a MATCH checkpoint.; replication writes observed: [111212722666, 111375777820, 111377398899, 111377861073, 111378391997, 111379204732, 111379714913, 111380439332, 111380998467, 111385960390]
- **Failover drill 2026-10-03** (`ops/availability/LOCAL_FAILOVER_DRILL_2026_10_03.json`): 5 phases (baseline, primary_stopped, secondary_stopped, both_stopped, both_restored)
- **Failover drill 2026-10-04** (`ops/availability/LOCAL_FAILOVER_DRILL_2026_10_04.json`): 5 phases (baseline, primary_stopped, secondary_stopped, both_stopped, both_restored)
- **Test evidence** (`ops/vyomaraj-core/handover/TEST_EVIDENCE_2026_10_04.json`): recorded separately; see the file for per-suite counts and results

## 6. What this report does not claim

- No sub-agent, provider account, revenue channel or device is asserted operational; every registry entry carries `runtime_status`: NOT_VERIFIED.
- No production deployment, traffic switch, RPO/RTO or independent-site DR is claimed; the DR evidence covers the Git main snapshot only.
- Product counts remain historical (421 reported) until the title list is reconciled; active products are `null`, not zero.
- The preview stack is unauthenticated and is a local sandbox, not a production service.
