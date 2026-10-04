# Deep Primary / Secondary / DR, contents and configuration scan

**Scan date:** 2026-10-04 (Asia/Calcutta)
**Primary main commit inspected:** `d9147fffc5884702d7fcbc38fd666d62622f3b8c`
**Primary main root tree:** `e8c66bd451484071d03afc68ac1aeeb010e8fa96`
**Secondary main commit reported by the read-only GitHub Actions probe:** `307d0383e2b46c064332e35025e25d97614c709d`
**Secondary main root tree:** `e8c66bd451484071d03afc68ac1aeeb010e8fa96`
**Candidate PR:** [#25](https://github.com/Vyomaraj1356/Vyomarajai/pull/25), captured head `fdedf5d39f676dce7a8ddf52e656b2295cee2132` (the reconstruction PR; open, not merged).

## Executive result — what matches, and what does not

| Snapshot | Git tree comparison | Evidence / interpretation |
|---|---|---|
| Primary `main` at `d9147fffc5884702d7fcbc38fd666d62622f3b8c` | **MATCH** | Root tree `e8c66bd451484071d03afc68ac1aeeb010e8fa96`. |
| Secondary `main` at commit `307d0383e2b46c064332e35025e25d97614c709d` | **MATCH** | GitHub Actions read-only annotation says `tree=MATCH`, root tree `e8c66bd451484071d03afc68ac1aeeb010e8fa96`. A matching root tree means all tracked Git paths, modes and blob identities are the same at those two refs. It is a Git snapshot check, not runtime or service DR. |
| PR #25 candidate head `fdedf5d39f676dce7a8ddf52e656b2295cee2132` vs secondary `main` | **NOT MATCHED** | The sanitized read-only annotation (check-run `111423631719`, run `37197962775`, completed 2026-10-04T11:13:06Z) reports `candidate_files=314`, `candidate_missing=16`, `candidate_secondary_only=0`, `candidate_changed=21`. These are counts, not a path-level diff. The report/artifact did not expose file paths. |
| Write permission / synchronization | **UNVERIFIED / NOT RUN** | The annotation explicitly says `write_permission=UNVERIFIED; writes=NONE`; `verify-or-sync` skipped on the PR. No DR write was attempted. |

The local read-only `dr_sync.py`/`dr_diagnostics.py` commands, using the sandbox's `gh` credentials, received HTTP 404 for the secondary. The scripts treat 404 as “missing or hidden by permissions” and do **not** infer nonexistence. The trusted same-repository PR's GET-only Actions probe could read both repositories and compare trees; that probe does not prove write permission.

**No sync was attempted.** The repository policy is `writer=primary_main_only`; the sync workflow is restricted to primary `main`. `automatic_target_only_file_removal=false`, and the pinned one-snapshot removal approval is false. The current primary `main` and secondary `main` already match, so there is nothing to sync at those refs. PR #25 is a different candidate snapshot and is not on `main`; it must not be pushed directly to the secondary. After owner review/merge to primary `main`, the existing main workflow is the allowed path to attempt replication. Do not bypass its guards.

## Scope and confidence

- The base inventory below is from the primary `main` Git tree at `d9147fffc5884702d7fcbc38fd666d62622f3b8c`; the live GitHub branch read during this scan still pointed to that commit.
- The secondary full recursive tree was not locally readable through this sandbox credential. Exact root-tree equality was confirmed by the trusted Actions read-only diagnostic; its public annotation returned counts only for the PR candidate.
- No credentials, environment-file values, phone numbers, email addresses, payout values or device identifiers are reproduced here. `ops/jarvis/jarvis.env` is tracked in Git; its values are intentionally withheld.
- This scan inventories repository records and declared configuration. It does not establish any AI/social provider connection, contract, payout, heartbeat, device reachability, production deployment, runtime readiness or 24x7 operation.
- Binary ZIP/APK/image files are included in the tree comparison and path/size manifest, but their internal contents were not unpacked or semantically audited in this scan. Their Git blobs match between the two main refs because the root tree matches.

## Primary repository contents — main snapshot

At the inspected primary `main` ref: **298 tracked paths; 493,302,815 blob bytes; 232 paths under `ops/`; 64 top-level entries.**

### Top-level path counts

| Top-level path | Tracked files |
|---|---:|
| `ops` | 232 |
| `.github` | 3 |
| `images` | 2 |
| `.gitignore` | 1 |
| `.vyomaraj-dr-heartbeat.log` | 1 |
| `Fix` | 1 |
| `GITHUB_TRIAGE_2026_10_04.md` | 1 |
| `Index.html` | 1 |
| `PRIMARY_SECONDARY_CONFIRMATION_V9.md` | 1 |
| `README.md` | 1 |
| `README_MARKET_READY.md` | 1 |
| `REAL_VYOMARAJ_INVESTIGATION.md` | 1 |
| `VYOMARAJ_REPOSITORY_MAP.md` | 1 |
| `Vyomaraj-All-Chats-Database-One-Month.md` | 1 |
| `Vyomaraj-All-Chats-From-Arena-Database-Till-V16.7.22.zip` | 1 |
| `Vyomaraj-App.apk` | 1 |
| `Vyomaraj-Complete-All-Sessions-All-Handover-Zips-V16.7.22.zip` | 1 |
| `Vyomaraj-Handover-V16.5.3-v167.tar.gz` | 1 |
| `Vyomaraj-Handover-V16.5.3-v167.zip` | 1 |
| `Vyomaraj-Handover-V16.6-v168.zip` | 1 |
| `Vyomaraj-Handover-V16.7-v169.zip` | 1 |
| `Vyomaraj-Handover-V16.7.1-v170.zip` | 1 |
| `Vyomaraj-Handover-V16.7.10-v180.zip` | 1 |
| `Vyomaraj-Handover-V16.7.11-v181.zip` | 1 |
| `Vyomaraj-Handover-V16.7.12-v182.zip` | 1 |
| `Vyomaraj-Handover-V16.7.13-v183.zip` | 1 |
| `Vyomaraj-Handover-V16.7.14-v184.zip` | 1 |
| `Vyomaraj-Handover-V16.7.15-v185.zip` | 1 |
| `Vyomaraj-Handover-V16.7.16-v186.zip` | 1 |
| `Vyomaraj-Handover-V16.7.17-v187.zip` | 1 |
| `Vyomaraj-Handover-V16.7.18-v188.zip` | 1 |
| `Vyomaraj-Handover-V16.7.19-v189.zip` | 1 |
| `Vyomaraj-Handover-V16.7.2-v171.zip` | 1 |
| `Vyomaraj-Handover-V16.7.20-v190.zip` | 1 |
| `Vyomaraj-Handover-V16.7.21-v191.zip` | 1 |
| `Vyomaraj-Handover-V16.7.22-v192.zip` | 1 |
| `Vyomaraj-Handover-V16.7.3-v172.zip` | 1 |
| `Vyomaraj-Handover-V16.7.4-v173.zip` | 1 |
| `Vyomaraj-Handover-V16.7.5-v174.zip` | 1 |
| `Vyomaraj-Handover-V16.7.6-v176.zip` | 1 |
| `Vyomaraj-Handover-V16.7.7-v177.zip` | 1 |
| `Vyomaraj-Handover-V16.7.8-v178.zip` | 1 |
| `Vyomaraj-Handover-V16.7.9-v179.zip` | 1 |
| `Vyomaraj-V10.0-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V11.0-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V12.0-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V12.1-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V13.0-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V14.0-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V15.0-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V15.1-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V6.6-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V6.7-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V6.8-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V6.9-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V7.0-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V8.0-Final-Market-Ready.zip` | 1 |
| `Vyomaraj-V9.0-Final-Market-Ready.zip` | 1 |
| `flow-diagram.html` | 1 |
| `index.html` | 1 |
| `landing.html` | 1 |
| `patch_v16_5_3_law_compliance.py` | 1 |
| `patch_v16_6_food_healing.py` | 1 |
| `patch_v16_7_law_entertainment.py` | 1 |

### Main `ops/` areas

| Area | Tracked files |
|---|---:|
| `ops/vyomaraj-core` | 164 |
| `ops/dr` | 32 |
| `ops/bhakti-shakti` | 22 |
| `ops/availability` | 5 |
| `ops/hanuman` | 4 |
| `ops/jarvis` | 4 |
| `ops/ci` | 1 |

The exhaustive tracked-path/mode/size manifest for this primary-main tree is in Appendix A. All paths below are also on the secondary `main` tree at the matching scan checkpoint; it is not a report of the unmerged PR branch.

## Agents, sub-agents and ownership

The current owner-approved registry is `ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json`:

- **13 main-agent categories, 128 counted sub-agent slots, six uncounted headings**.
- Historical source totals remain **13 / 133 / 421**, preserved in `AGENT_CONTENT_REGISTRY_V16_7_24.json`; those are not live runtime counts.
- Current product total is explicitly **UNRECONCILED**. The reconciliation rule says not to invent unverified sub-sub-agents. All current registry records carry `runtime_status=NOT_VERIFIED`; names/slots marked `UNKNOWN` stay unknown.
- The 173-row `CONTENT_INDEX_CURRENT.json` is a reference index (21 education-topic references plus editorial references); it is not a full 421-product inventory. The historical catalog has 32 files/unique paths. `CONTENT_CATALOG.json` says full 421-product title completeness was not supplied.

### Current category allocation

| Category ID | Category | Counted sub-agent slots | Uncounted headings |
|---|---|---:|---:|
| `FOOD` | Food & Social Connect | 3 | 0 |
| `EDU` | Education | 16 | 0 |
| `ASTRO` | Astro-Celestial & Universal | 3 | 0 |
| `FINANCE` | Finance & Wealth | 7 | 0 |
| `LIFE` | Life Coach & Wellness | 10 | 0 |
| `BHAKTI` | Bhakti Mandir — Ritual, Festival & Grantha | 3 | 0 |
| `SPORTS` | Sports & Legends | 14 | 0 |
| `AGRI` | Agriculture & Environment | 6 | 0 |
| `ENTERTAINMENT` | Entertainment — Comedy, Movies, Hollywood, Bollywood | 32 | 6 |
| `PLATFORM` | Platform & Social Hub + Earn — All Platforms + Monetization | 20 | 0 |
| `TOUR` | Tour and Travel | 4 | 0 |
| `WAR` | War Room — Warriors | 5 | 0 |
| `PODCAST` | Podcast & Entertainment Studio | 5 | 0 |

### Editorial ownership routes

`film` → `ENTERTAINMENT`, `music` → `ENTERTAINMENT`, `bhakti` → `BHAKTI`, `pairings` → `ENTERTAINMENT`, `aghor` → `BHAKTI`

### All 128 current registry entries

| ID | Category | Name / display | Name provenance | Runtime |
|---|---|---|---|---|
| `FOOD-REF-01` | `FOOD` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FOOD-REF-02` | `FOOD` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FOOD-REF-03` | `FOOD` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `EDU-S1` | `EDU` | Veda Rishi | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-S2` | `EDU` | Upanishad Guru | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-S3` | `EDU` | Gita Acharya | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-S4` | `EDU` | Mythology & Mystery Rishi | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-S5` | `EDU` | Vyomaraj Picker | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-S6` | `EDU` | Lectures Hub | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-S7` | `EDU` | Short Notes | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-S8` | `EDU` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `EDU-S9` | `EDU` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `EDU-S10` | `EDU` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `EDU-S11` | `EDU` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `EDU-S12` | `EDU` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `EDU-S13` | `EDU` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `EDU-S14` | `EDU` | Care & Bikes — Bicycles & Two-Wheelers | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-S15` | `EDU` | Social Thinkers, Visionaries & Legends | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `EDU-GOV-S1` | `EDU` | Government Schemes | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `ASTRO-REF-01` | `ASTRO` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ASTRO-REF-02` | `ASTRO` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ASTRO-REF-03` | `ASTRO` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FINANCE-REF-01` | `FINANCE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FINANCE-REF-02` | `FINANCE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FINANCE-REF-03` | `FINANCE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FINANCE-REF-04` | `FINANCE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FINANCE-REF-05` | `FINANCE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FINANCE-REF-06` | `FINANCE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `FINANCE-REF-07` | `FINANCE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-01` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-02` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-03` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-04` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-05` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-06` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-07` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-08` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-09` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `LIFE-REF-10` | `LIFE` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `BHAKTI-REF-01` | `BHAKTI` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `BHAKTI-REF-02` | `BHAKTI` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `BHAKTI-AGHOR-S1` | `BHAKTI` | Aghor & Aghori | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `SPORTS-REF-01` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-02` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-03` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-04` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-05` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-06` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-07` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-08` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-09` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-10` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-11` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-12` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-13` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `SPORTS-REF-14` | `SPORTS` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `AGRI-REF-01` | `AGRI` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `AGRI-REF-02` | `AGRI` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `AGRI-REF-03` | `AGRI` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `AGRI-REF-04` | `AGRI` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `AGRI-REF-05` | `AGRI` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `AGRI-REF-06` | `AGRI` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-INDICOM` | `ENTERTAINMENT` | INDICOM | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `ENT-CRITICISM` | `ENTERTAINMENT` | Criticism gate | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `ENT-AI-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-AI-S2` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-CARTOON-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-CARTOON-S2` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-CARTOON-S3` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-COM-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-COM-S2` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-COM-S3` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-COM-S4` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-COM-S5` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-COM-S6` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-COM-S7` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-COM-S8` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MOVIE-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MOVIE-S2` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MOVIE-S3` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MOVIE-S4` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MOVIE-S5` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MOVIE-S6` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MUS-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MUS-S2` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MUS-S3` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MUS-S4` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MUS-S5` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-MUS-S6` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-SHAYARI-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-WIT-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-HASYA-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-LIQUOR-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `ENT-BAR-S1` | `ENTERTAINMENT` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `PLATFORM-REF-01` | `PLATFORM` | YouTube | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-02` | `PLATFORM` | Instagram | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-03` | `PLATFORM` | Facebook | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-04` | `PLATFORM` | TikTok | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-05` | `PLATFORM` | X | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-06` | `PLATFORM` | LinkedIn | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-07` | `PLATFORM` | Telegram | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-08` | `PLATFORM` | WhatsApp | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-09` | `PLATFORM` | Discord | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-10` | `PLATFORM` | Pinterest | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-11` | `PLATFORM` | Threads | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-12` | `PLATFORM` | Snapchat | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-13` | `PLATFORM` | Reddit | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-14` | `PLATFORM` | Twitch | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-15` | `PLATFORM` | Vimeo | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-16` | `PLATFORM` | Tumblr | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-17` | `PLATFORM` | Mastodon | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-18` | `PLATFORM` | EARN | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-REF-19` | `PLATFORM` | AI | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PLATFORM-UNMAPPED` | `PLATFORM` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `TOUR-REF-01` | `TOUR` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `TOUR-REF-02` | `TOUR` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `TOUR-REF-03` | `TOUR` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `TOUR-REF-04` | `TOUR` | UNKNOWN | UNKNOWN | `NOT_VERIFIED` |
| `WAR-REF-01` | `WAR` | PAST | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `WAR-REF-02` | `WAR` | HISTORY | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `WAR-REF-03` | `WAR` | PRESENT | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `WAR-REF-04` | `WAR` | FUTURE | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `WAR-REF-05` | `WAR` | CROSS-CUTTING | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PODCAST-REF-01` | `PODCAST` | RESEARCH | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PODCAST-REF-02` | `PODCAST` | SCRIPT | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PODCAST-REF-03` | `PODCAST` | PRODUCE | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PODCAST-REF-04` | `PODCAST` | ANALYSIS | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |
| `PODCAST-REF-05` | `PODCAST` | PUBLISH | SUPPLIED_OR_OWNER_APPROVED | `NOT_VERIFIED` |

### Six structural headings (not counted as agents)

| ID | Category | Heading | Counted |
|---|---|---|---|
| `ENT-HUB-COM` | `ENTERTAINMENT` | Comedy hub | False |
| `ENT-HUB-CARTOON` | `ENTERTAINMENT` | Cartoon | False |
| `ENT-HUB-MUS` | `ENTERTAINMENT` | Music | False |
| `ENT-HUB-MOVIE` | `ENTERTAINMENT` | Movie | False |
| `ENT-HUB-WIT` | `ENTERTAINMENT` | Wit | False |
| `ENT-HUB-SHAYARI` | `ENTERTAINMENT` | Shayari | False |

### All 173 content-index references

The last column is the source record's `full_content_imported` flag; `false` means this is only an indexed reference, not complete imported content.

| ID | Title | Owner category | Record kind | Full content imported |
|---|---|---|---|---|
| `EDU-TOPIC-government-schemes` | Government Schemes | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-vedas` | Vedas | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-upanishads` | Upanishads | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-gita` | Gita | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-mythology-mystery` | Mythology and mystery | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-picker` | Vyomaraj Picker | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-lectures` | Lectures | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-notes` | Short notes | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-granthas` | Bharat Grantha, Chanakya and the Granthas | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-bicycles` | Bicycles and two-wheelers | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-thinkers` | Social thinkers, visionaries and legends | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-flora-fauna` | Flora and fauna | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-perfumes` | Perfumes and itras | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-oceans` | Oceans and underwater life | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-dinosaurs` | Dinosaurs and prehistoric life | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-sanatana-texts` | Saptarishi, Smriti, Puranas and Sanatana literature | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-arms-history` | Arms history, law and safety literacy | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-philately` | World stamps and philately | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-scripts` | Ancient scripts and epigraphy | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-architecture` | Architecture | `EDU` | `education_topic_reference` | false |
| `EDU-TOPIC-space` | Space and astronomy | `EDU` | `education_topic_reference` | false |
| `aghor:chapters:meaning` | Aghor, Aghori and Aughar: words and meanings | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:origins` | Sacred origins are not a dated beginning of the universe | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:history` | History, hagiography and the limits of the record | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:kinaram` | Kina Ram / Kinaram / Keenaram and Krim Kund | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:bhagwan-reform` | Bhagwan Ram and twentieth-century service | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:living` | Contemporary communities and diaspora | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:types` | Ways of describing practice—not fixed universal types | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:sadhana` | Sadhana: ordinary discipline and personal boundaries | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:seva` | Seva: service without stigma | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:ritual-context` | Cremation-ground imagery and antinomian traditions | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:medicine` | Ethnography is not a clinical treatment trial | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:leprosy` | Hansen disease: treatment and dignity | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:upayas` | Upayas as optional support, not promised cures | `BHAKTI` | `editorial_chapters` | false |
| `aghor:chapters:research-ethics` | Study respectfully and verify claims | `BHAKTI` | `editorial_chapters` | false |
| `aghor:people:shiva` | Shiva / Aghora aspect | `BHAKTI` | `editorial_people` | false |
| `aghor:people:dattatreya` | Dattatreya | `BHAKTI` | `editorial_people` | false |
| `aghor:people:kaluram` | Baba Kaluram | `BHAKTI` | `editorial_people` | false |
| `aghor:people:kina-ram` | Baba Kina Ram / Kinaram / Keenaram | `BHAKTI` | `editorial_people` | false |
| `aghor:people:bhagwan-ram` | Aghoreshwar Bhagwan Ram | `BHAKTI` | `editorial_people` | false |
| `aghor:people:harihar-ram` | Baba Harihar Ram | `BHAKTI` | `editorial_people` | false |
| `aghor:people:siddharth` | Baba Siddharth Gautam Ram | `BHAKTI` | `editorial_people` | false |
| `aghor:practices:reflection` | Reflection in public accounts | `BHAKTI` | `editorial_practices` | false |
| `aghor:practices:prayer` | Prayer and japa: cultural context | `BHAKTI` | `editorial_practices` | false |
| `aghor:practices:service` | Seva: community-service context | `BHAKTI` | `editorial_practices` | false |
| `aghor:practices:study` | Reading different kinds of evidence | `BHAKTI` | `editorial_practices` | false |
| `aghor:practices:visit` | Community visits: context only | `BHAKTI` | `editorial_practices` | false |
| `aghor:practices:historical-rites` | Historical ritual practices: context only | `BHAKTI` | `editorial_practices` | false |
| `aghor:care:care-skin` | Skin patches, numbness or suspected leprosy | `BHAKTI` | `editorial_care` | false |
| `aghor:care:care-claims` | Pain, infertility and other cure claims | `BHAKTI` | `editorial_care` | false |
| `aghor:care:care-products` | Ashes, unknown herbs and mineral preparations | `BHAKTI` | `editorial_care` | false |
| `aghor:care:care-fear` | Fear of curses or supernatural harm | `BHAKTI` | `editorial_care` | false |
| `aghor:care:care-emergency` | Serious symptoms or immediate danger | `BHAKTI` | `editorial_care` | false |
| `aghor:care:care-upaya` | A non-medical upaya checklist | `BHAKTI` | `editorial_care` | false |
| `film:items:shyam` | Shyamchi Aai · 1953 version | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:jaane` | Jaane Bhi Do Yaaro | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:salaam` | Salaam Bombay! | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:sairat` | Sairat | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:disciple` | The Disciple | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:laapataa` | Laapataa Ladies | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:natsamrat-check` | Natsamrat · edition check required | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:chaitra` | Chaitra | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:aaba` | Aaba Aiktaay Naa? | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:juice` | Juice | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:sintel` | Sintel · open animated short | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:ekzunj` | Ek Zunj Varyashi | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:ghashiram` | Ghashiram Kotwal | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:devbabhali` | Sangeet Devbabhali | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:andhayug` | Andha Yug · festival production | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:adhe` | Adhe Adhure · 2026 programme record | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:dhumrapaan` | Dhumrapaan · 2019 programme record | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:lalitaji` | Surf / Lalitaji · advertising memory | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:liril` | Liril · advertising memory | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:cadbury-old` | Cadbury cricket · original-era case study | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:cadbury-new` | Cadbury cricket · 2021 reimagining | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:ariel` | Ariel ShareTheLoad · 2024 campaign | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:loc` | National Screening Room · archive discovery | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:citizendj` | Citizen DJ · selected reuse collection | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:clip` | Clips, trailers & critical excerpts | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:mr-oneact` | Original Marathi one-act workshop | `ENTERTAINMENT` | `editorial_items` | false |
| `film:items:hi-oneact` | Original Hindi one-act workshop | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:binaca` | Binaca Geetmala | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:bhoole` | Bhoole Bisre Geet | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:chhaya` | Chhayageet | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:sarita` | Sangeet Sarita | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:jaimala` | Jaimala | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:hawamahal` | Hawamahal | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:uk-radio` | The UK Top 40 / BBC Radio 1 context | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:lata` | Lata Mangeshkar · classic catalogue | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:asha` | Asha Bhosle · classic catalogue | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:rafi` | Mohammed Rafi · classic catalogue | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:kishore` | Kishore Kumar · classic catalogue | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:jagjit` | The Unforgettables | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:rahman` | Vande Mataram | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:aashiqui2` | Aashiqui 2 | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:coldmess` | cold/mess | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:goat` | G.O.A.T. | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:katchisera` | Katchi Sera (From Think Indie) | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:radical` | Radical Optimism | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:golden` | GOLDEN | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:burna` | I Told Them... | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:marathi` | Marathi songs · Arnold Bake Collection | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:goa` | Music of Goa | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:bengal` | Bengal · folk and classical connections | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:indian-folk` | Folk Music of India · regional archive | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:world` | World traditions · open discovery map | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:hot100` | Billboard Hot 100 | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:bb200` | Billboard 200 | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:global200` | Billboard Global 200 | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:india-chart` | Billboard India Songs | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:uk-charts` | Official UK singles & albums | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:spotify` | Spotify charts & Local Pulse | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:youtube` | YouTube songs, videos & Shorts | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:ifpi2025` | IFPI Global Single Chart · 2025 | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:audio` | Audio · radio, interviews & listening notes | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:video` | Video · performance, visualiser & documentary | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:hateyou-video` | Hate You · music video | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:big7-video` | Big 7 · music video | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:katchi-video` | Katchi Sera · music video | `ENTERTAINMENT` | `editorial_items` | false |
| `music:items:tumhiho` | Tum Hi Ho · soundtrack recording | `ENTERTAINMENT` | `editorial_items` | false |
| `bhakti:stories:shiv-shakti` | Shiv–Shakti: relationship and meaning | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:ardhanarishvara` | Ardhanarishvara: a shared form | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:shiva-origins` | Names, texts and early worship | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:sati-daksha` | Sati, Daksha and sacred geography | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:parvati` | Parvati, devotion and union | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:family` | Ganesha, Skanda and family stories | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:neelakantha` | Neelakantha and the ocean-churning story | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:ganga` | Gangadhara and the descent of Ganga | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:moon` | The crescent moon and sacred symbols | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:nataraja` | Nataraja: dance, change and renewal | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:forms` | Bhairava, Tripurari and the lingam | `BHAKTI` | `editorial_stories` | false |
| `bhakti:stories:living-traditions` | Temples, festivals and living traditions | `BHAKTI` | `editorial_stories` | false |
| `bhakti:avatars:avatar-01` | Matsya | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-02` | Kurma | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-03` | Varaha | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-04` | Narasimha | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-05` | Vamana | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-06` | Parashurama | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-07` | Rama | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-08` | Krishna | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-09` | Buddha | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:avatars:avatar-10` | Kalki | `BHAKTI` | `editorial_avatars` | false |
| `bhakti:peethas:kamakhya` | Kamakhya | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:peethas:kalighat` | Kalighat | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:peethas:tripura` | Tripura Sundari / Matabari | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:peethas:ambaji` | Ambaji | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:peethas:jwala` | Jwalamukhi / Jawala Mata | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:peethas:kolhapur` | Mahalakshmi / Ambabai | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:peethas:tulja` | Tulja Bhavani | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:peethas:renuka` | Renuka Devi | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:peethas:saptashrungi` | Saptashrungi | `BHAKTI` | `editorial_peethas` | false |
| `bhakti:recipes:fruit` | Seasonal fruit plate | `BHAKTI` | `editorial_recipes` | false |
| `bhakti:recipes:coconut` | Coconut & roasted chana plate | `BHAKTI` | `editorial_recipes` | false |
| `bhakti:recipes:yogurt` | Plain yogurt & fruit bowl | `BHAKTI` | `editorial_recipes` | false |
| `pairings:traditions:tadi-local` | Local tadi / toddy | `ENTERTAINMENT` | `editorial_traditions` | false |
| `pairings:traditions:kallu` | Kallu / Kerala toddy | `ENTERTAINMENT` | `editorial_traditions` | false |
| `pairings:traditions:goa` | Feni & urak heritage | `ENTERTAINMENT` | `editorial_traditions` | false |
| `pairings:traditions:apong` | Apong | `ENTERTAINMENT` | `editorial_traditions` | false |
| `pairings:traditions:chhang` | Chhang | `ENTERTAINMENT` | `editorial_traditions` | false |
| `pairings:traditions:sake` | Sake-making traditions | `ENTERTAINMENT` | `editorial_traditions` | false |
| `pairings:traditions:agave` | Agave & Tequila heritage | `ENTERTAINMENT` | `editorial_traditions` | false |
| `pairings:traditions:bavaria` | Bavarian festival culture | `ENTERTAINMENT` | `editorial_traditions` | false |
| `pairings:snacks:chana` | Lemon & cumin chana | `ENTERTAINMENT` | `editorial_snacks` | false |
| `pairings:snacks:peanuts` | Roasted peanut koshimbir | `ENTERTAINMENT` | `editorial_snacks` | false |
| `pairings:snacks:moong` | Cooked moong chaat | `ENTERTAINMENT` | `editorial_snacks` | false |
| `pairings:snacks:sundal` | Chickpea sundal bowl | `ENTERTAINMENT` | `editorial_snacks` | false |
| `pairings:snacks:tofu` | Pepper & lime tofu bites | `ENTERTAINMENT` | `editorial_snacks` | false |
| `pairings:snacks:paneer` | Herbed paneer & peppers | `ENTERTAINMENT` | `editorial_snacks` | false |
| `pairings:snacks:fish` | Banana-leaf fish plate | `ENTERTAINMENT` | `editorial_snacks` | false |
| `pairings:snacks:veg` | Roasted vegetable crunch | `ENTERTAINMENT` | `editorial_snacks` | false |
| `pairings:events:spirit-goa` | Spirit of Goa | `ENTERTAINMENT` | `editorial_events` | false |
| `pairings:events:oktoberfest` | Oktoberfest | `ENTERTAINMENT` | `editorial_events` | false |
| `pairings:events:local-calendar` | Local tadi, harvest and community heritage events | `ENTERTAINMENT` | `editorial_events` | false |

## Editorial content packages

The canonical content remains in the listed JSON packs; counts below are source records, not a claim of publication or complete world coverage.

| Pack | Source | Counted collections |
|---|---|---|
| Aghor/view-only study | `ops/vyomaraj-core/aghor-experience/content.json` | chapters=14, people=7, practices=6, care=6 |
| Bhakti-Shakti | `ops/vyomaraj-core/bhakti-experience/content.json` | stories=12, avatars=10, peethas=9, recipes=3, research_backlog=6 |
| Comics | `ops/vyomaraj-core/comics-experience/content.json` | agents=3, items=12, formats=4 |
| Film/stage | `ops/vyomaraj-core/film-experience/content.json` | agents=6, items=27, formats=7 |
| Music | `ops/vyomaraj-core/music-experience/content.json` | agents=6, items=39 |
| Roots/pairings | `ops/vyomaraj-core/liquor-bar/content.json` | specification_fields=17, traditions=8, research_backlog=8, snacks=8, events=3 |

Additional catalog/index files: `ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json` (173 references), `CONTENT_OWNERSHIP_CURRENT.json` (single-owner routing), `RECONCILIATION_RULES.json`, `ops/vyomaraj-core/experience/CONTENT_CATALOG.json`, `CONTENT_EXTENSIONS.json`, and generated `EXPERIENCE_CONTENTS_2026_10_03.md`. Per-experience source files are individually listed in Appendix A.

## Architecture, Vyomaraj and Jarvis configuration

- The documented control flow is **Owner → ShriYantra → Vyomaraj/Bharath → Jarvis/Laxman → agents/content → explicit owner review gate → any future approved external action**. This is the architecture/authority model, not a claim that all roles are deployed as running AI services.
- `ops/vyomaraj-core/experience/LOCAL_INTEGRATION.json` declares `status=local_preview_planning_only`, `provider=null`, `automatic_ai_calls=false`, `automatic_publishing=false`, `legacy_jarvis_env_loaded=false`, `production_deployed=false`; governance reports contracts and payments not connected.
- `ops/vyomaraj-core/governance/PUBLIC_POLICY.json` says participation is voluntary, earning is an opportunity not a guarantee, payment/payout services are not connected, and legal contracts are draft/not executed (acceptance and legal certification false).
- The `3d`/`4d`/`5d` values are planner modes. Research adapters are metadata-only (`musicbrainz`, Library of Congress and Open Library); network runtime check is recorded unavailable; SearXNG/Ollama are not configured; schedule is opt-in and inactive.
- `ops/jarvis/jarvis.env` and `.example` contain 24 configuration keys each. This report lists only the key names, not values. The app integration explicitly says the legacy env is **not loaded** by the local planner. `ops/jarvis/devices.json` has three device records and three future-home records; ACTIVE/STANDBY strings are declarations, not observed device health.

### Jarvis environment key names (values withheld)

- `JARVIS_PRIMARY_DEVICE` = value withheld
- `JARVIS_PRIMARY_NUMBER` = value withheld
- `JARVIS_PRIMARY_STATUS` = value withheld
- `JARVIS_PRIMARY_ROLE` = value withheld
- `JARVIS_SECONDARY_DEVICE` = value withheld
- `JARVIS_SECONDARY_NUMBER` = value withheld
- `JARVIS_SECONDARY_STATUS` = value withheld
- `JARVIS_FUTURE_HOME` = value withheld
- `JARVIS_FUTURE_HOME_STATUS` = value withheld
- `JARVIS_FUTURE_HOME_DESC` = value withheld
- `JARVIS_CLOUD_HOME` = value withheld
- `JARVIS_EDGE_HOME` = value withheld
- `SHRI_RAM_JI` = value withheld
- `BHARAT` = value withheld
- `HANUMAN_QUALITY` = value withheld
- `LAXMAN` = value withheld
- `RELATIONSHIP` = value withheld
- `JARVIS_HEARTBEAT_INTERVAL` = value withheld
- `JARVIS_HEARTBEAT_URL` = value withheld
- `JARVIS_STATE_FILE` = value withheld
- `JARVIS_LOCK_FILE` = value withheld
- `TRENDS` = value withheld
- `SCALABLE_TECH` = value withheld
- `JARVIS_TEST` = value withheld

### Declared device inventory (identifiers and numbers withheld)

- Device records: 3; `futureHomes`: 3.
- The file describes mobile and desktop/cloud/edge concepts. Its ACTIVE/STANDBY fields are unverified records, not live heartbeats or authenticated device checks.
- The `JARVIS_HEARTBEAT_URL`, state and lock keys are names only; this scan did not invoke the controller or load the environment.

## AI platform catalogue — names are not connections

### Metadata-only coordination surface

`ops/vyomaraj-core/multi-ai-coordination.js` lists Arena.ai, GitHub primary, GitHub recovery repository, Local preview, ChatGPT, Claude and Gemini with `status=UNVERIFIED`; `operational=false`, no measured load, and platform switching/sharing returns `BLOCKED` because no provider/session-transfer executor is configured.

### Food-content prompt catalogue (10 records)

- Vheer AI Food Generator
- TopMediai AI Video Generator
- Dreamina CapCut AI Food Generator
- Recraft
- MagicShot
- ChatGPT-4o + DALL·E + Runway + Kling
- FlexClip
- Renderforest
- BigMotion
- Leonardo.ai + Kling AI + ImagineArt + Flow AI + CapCut

These entries are prompt/tool suggestions, not configured API clients. `LOCAL_INTEGRATION.json` has no provider, and automatic AI calls are false.

### Other recorded tool names

The historical Jarvis device metadata mentions Meta AI/Llama, Whisper, ElevenLabs, MediaPipe, mapping APIs, Web Speech, Web Audio and MediaRecorder. This is a trend/capability list only; it is not proof of SDK credentials, integrations, subscriptions or running services.

## Social platforms — declared catalogs vs verified integrations

- `ops/hanuman/social-platforms.json` lists 19 platform entries: YouTube, Instagram, Facebook, TikTok, X (Twitter), LinkedIn, Telegram, WhatsApp, Discord, Pinterest, Threads, Snapchat, Reddit, Twitch, Vimeo, Tumblr, Mastodon, GitHub Pages, APK. Its status/heartbeat/revenue wording is a legacy declaration, not verified API or account state.
- `ops/vyomaraj-core/handover/SOCIAL_PLATFORMS_CONTRACTS.json` lists 9 records: YouTube, Instagram, Facebook, TikTok, X Twitter, LinkedIn, Telegram, WhatsApp, Discord. The file is not evidence that contracts were executed or that APIs are connected.
- Current ownership/integration rules do not prove accounts are inherited as working credentials by each agent. No credential sharing is exposed. External social publishing remains manual/owner-gated; automatic publishing is false. The policy reports payment services disconnected and legal contracts not executed.

## What “matching” means here

- **Yes:** primary `main` and secondary `main` have the same root Git tree (`e8c66bd451484071d03afc68ac1aeeb010e8fa96`), so their tracked Git snapshot—including tracked package blobs—is identical at the cited refs/checkpoint.
- **No:** PR #25's branch is not part of that match; the probe reports 16 candidate paths absent on secondary and 21 changed paths, with zero secondary-only paths at the captured head.
- **Not checked/claimed:** actual platform API health, social-account ownership, Jarvis devices/heartbeats, deploy/runtime, database/media/session state, legal agreements, and service-level DR/RPO/RTO.

## Appendix A — exhaustive primary-main file manifest (298 entries)

Path and Git mode are listed for every tracked file; sizes are blob-byte counts. The `ops/jarvis/jarvis.env` size is withheld with its values. Binary files are inventoried but not expanded.

| Path | Mode | Blob bytes |
|---|---|---:|
| `.github/workflows/vyomaraj-ci-diagnostics.yml` | `100644` | 2,294 |
| `.github/workflows/vyomaraj-research.yml` | `100644` | 2,311 |
| `.github/workflows/vyomaraj-sync-both.yml` | `100644` | 7,076 |
| `.gitignore` | `100644` | 605 |
| `.vyomaraj-dr-heartbeat.log` | `100644` | 516 |
| `Fix` | `100644` | 3,423 |
| `GITHUB_TRIAGE_2026_10_04.md` | `100644` | 2,747 |
| `Index.html` | `100644` | 12,761 |
| `PRIMARY_SECONDARY_CONFIRMATION_V9.md` | `100644` | 9,154 |
| `README.md` | `100644` | 8,477 |
| `README_MARKET_READY.md` | `100644` | 65,961 |
| `REAL_VYOMARAJ_INVESTIGATION.md` | `100644` | 12,790 |
| `VYOMARAJ_REPOSITORY_MAP.md` | `100644` | 1,723 |
| `Vyomaraj-All-Chats-Database-One-Month.md` | `100644` | 16,871 |
| `Vyomaraj-All-Chats-From-Arena-Database-Till-V16.7.22.zip` | `100644` | 5,314 |
| `Vyomaraj-App.apk` | `100644` | 24,567,022 |
| `Vyomaraj-Complete-All-Sessions-All-Handover-Zips-V16.7.22.zip` | `100644` | 13,048,185 |
| `Vyomaraj-Handover-V16.5.3-v167.tar.gz` | `100644` | 360,649 |
| `Vyomaraj-Handover-V16.5.3-v167.zip` | `100644` | 407,729 |
| `Vyomaraj-Handover-V16.6-v168.zip` | `100644` | 472,710 |
| `Vyomaraj-Handover-V16.7-v169.zip` | `100644` | 546,712 |
| `Vyomaraj-Handover-V16.7.1-v170.zip` | `100644` | 546,712 |
| `Vyomaraj-Handover-V16.7.10-v180.zip` | `100644` | 577,569 |
| `Vyomaraj-Handover-V16.7.11-v181.zip` | `100644` | 578,874 |
| `Vyomaraj-Handover-V16.7.12-v182.zip` | `100644` | 577,007 |
| `Vyomaraj-Handover-V16.7.13-v183.zip` | `100644` | 577,727 |
| `Vyomaraj-Handover-V16.7.14-v184.zip` | `100644` | 577,754 |
| `Vyomaraj-Handover-V16.7.15-v185.zip` | `100644` | 436,645 |
| `Vyomaraj-Handover-V16.7.16-v186.zip` | `100644` | 578,890 |
| `Vyomaraj-Handover-V16.7.17-v187.zip` | `100644` | 579,032 |
| `Vyomaraj-Handover-V16.7.18-v188.zip` | `100644` | 579,125 |
| `Vyomaraj-Handover-V16.7.19-v189.zip` | `100644` | 579,109 |
| `Vyomaraj-Handover-V16.7.2-v171.zip` | `100644` | 546,712 |
| `Vyomaraj-Handover-V16.7.20-v190.zip` | `100644` | 579,411 |
| `Vyomaraj-Handover-V16.7.21-v191.zip` | `100644` | 579,333 |
| `Vyomaraj-Handover-V16.7.22-v192.zip` | `100644` | 311,660 |
| `Vyomaraj-Handover-V16.7.3-v172.zip` | `100644` | 552,522 |
| `Vyomaraj-Handover-V16.7.4-v173.zip` | `100644` | 552,522 |
| `Vyomaraj-Handover-V16.7.5-v174.zip` | `100644` | 552,580 |
| `Vyomaraj-Handover-V16.7.6-v176.zip` | `100644` | 559,194 |
| `Vyomaraj-Handover-V16.7.7-v177.zip` | `100644` | 559,421 |
| `Vyomaraj-Handover-V16.7.8-v178.zip` | `100644` | 575,383 |
| `Vyomaraj-Handover-V16.7.9-v179.zip` | `100644` | 577,794 |
| `Vyomaraj-V10.0-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V11.0-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V12.0-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V12.1-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V13.0-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V14.0-Final-Market-Ready.zip` | `100644` | 28,963,815 |
| `Vyomaraj-V15.0-Final-Market-Ready.zip` | `100644` | 29,088,017 |
| `Vyomaraj-V15.1-Final-Market-Ready.zip` | `100644` | 29,092,780 |
| `Vyomaraj-V6.6-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V6.7-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V6.8-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V6.9-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V7.0-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V8.0-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `Vyomaraj-V9.0-Final-Market-Ready.zip` | `100644` | 28,907,765 |
| `flow-diagram.html` | `100644` | 61,964 |
| `images/vyomaraj-best-process-flow.png` | `100644` | 2,353,215 |
| `images/vyomaraj-flow-diagram.png` | `100644` | 2,476,295 |
| `index.html` | `100644` | 2,738 |
| `landing.html` | `100644` | 22,846 |
| `ops/availability/LOCAL_FAILOVER_DRILL_2026_10_03.json` | `100644` | 2,480 |
| `ops/availability/LOCAL_FAILOVER_DRILL_2026_10_04.json` | `100644` | 4,035 |
| `ops/availability/README.md` | `100644` | 3,787 |
| `ops/availability/gateway.py` | `100644` | 5,910 |
| `ops/availability/test_gateway.py` | `100644` | 2,433 |
| `ops/bhakti-shakti/additional-sathi-detailed.json` | `100644` | 31,206 |
| `ops/bhakti-shakti/additional-sathi.json` | `100644` | 860 |
| `ops/bhakti-shakti/all-indian-gods-controller.sh` | `100755` | 18,395 |
| `ops/bhakti-shakti/all-indian-gods.json` | `100644` | 17,150 |
| `ops/bhakti-shakti/bhakti-shakti-controller.sh` | `100755` | 8,990 |
| `ops/bhakti-shakti/damru.json` | `100644` | 17,889 |
| `ops/bhakti-shakti/dashavatar.json` | `100644` | 34,828 |
| `ops/bhakti-shakti/jyotirlinga-12.json` | `100644` | 8,605 |
| `ops/bhakti-shakti/major-gods.json` | `100644` | 23,265 |
| `ops/bhakti-shakti/nandi.json` | `100644` | 10,850 |
| `ops/bhakti-shakti/navagraha.json` | `100644` | 23,665 |
| `ops/bhakti-shakti/regional-gods.json` | `100644` | 30,475 |
| `ops/bhakti-shakti/revenue-reel-system.json` | `100644` | 18,151 |
| `ops/bhakti-shakti/rudraksh.json` | `100644` | 19,886 |
| `ops/bhakti-shakti/shakti-forms.json` | `100644` | 17,593 |
| `ops/bhakti-shakti/shankh.json` | `100644` | 41,165 |
| `ops/bhakti-shakti/shiv-bhakts.json` | `100644` | 4,040 |
| `ops/bhakti-shakti/shiv-ke-sathi.json` | `100644` | 132,181 |
| `ops/bhakti-shakti/trimurti-tridevi.json` | `100644` | 21,174 |
| `ops/bhakti-shakti/trishul.json` | `100644` | 12,936 |
| `ops/bhakti-shakti/vasuki.json` | `100644` | 11,959 |
| `ops/bhakti-shakti/village-gram-devta.json` | `100644` | 26,533 |
| `ops/ci/ci_diagnostics.py` | `100644` | 3,812 |
| `ops/dr/.sync-proof-trigger` | `100644` | 59 |
| `ops/dr/ACTIONS_PROBE_EVIDENCE_2026_10_03.json` | `100644` | 1,475 |
| `ops/dr/DEPLOYED_MATCH_2026_10_03.json` | `100644` | 1,976 |
| `ops/dr/DEPLOYED_MATCH_2026_10_04.json` | `100644` | 24,265 |
| `ops/dr/DR_ACTIVATION_REPORT_V15_1.md` | `100644` | 10,756 |
| `ops/dr/DR_ACTIVATION_REPORT_V9.md` | `100644` | 8,492 |
| `ops/dr/DR_CHECK_2026_10_03.json` | `100644` | 386 |
| `ops/dr/DR_FOLLOWUP_2026_10_03.json` | `100644` | 1,258 |
| `ops/dr/DR_POLICY.json` | `100644` | 2,600 |
| `ops/dr/ISSUE_6_RESOLUTION_2026_10_04.md` | `100644` | 6,119 |
| `ops/dr/LIVE_AUDIT_2026_10_03.json` | `100644` | 2,868 |
| `ops/dr/LIVE_AUDIT_VIEW_ONLY_2026_10_03.json` | `100644` | 2,868 |
| `ops/dr/README.md` | `100644` | 15,416 |
| `ops/dr/RECOVERY_REVIEW_2026_10_03.json` | `100644` | 112 |
| `ops/dr/SYNC_VERIFICATION_TRIGGER.md` | `100644` | 309 |
| `ops/dr/actions_read_probe.py` | `100644` | 6,645 |
| `ops/dr/dr.env` | `100644` | 4,162 |
| `ops/dr/dr.env.example` | `100644` | 1,845 |
| `ops/dr/dr_diagnostics.py` | `100644` | 3,751 |
| `ops/dr/dr_live_audit.py` | `100644` | 3,370 |
| `ops/dr/dr_sync.py` | `100644` | 16,696 |
| `ops/dr/failover-controller.sh` | `100755` | 8,491 |
| `ops/dr/recovery_plan.py` | `100644` | 2,322 |
| `ops/dr/run-dr.sh` | `100755` | 904 |
| `ops/dr/secondary_read_probe.py` | `100644` | 2,141 |
| `ops/dr/test_actions_read_probe.py` | `100644` | 3,277 |
| `ops/dr/test_dr_diagnostics.py` | `100644` | 2,823 |
| `ops/dr/test_dr_sync.py` | `100644` | 8,228 |
| `ops/dr/test_http_retry.py` | `100644` | 1,718 |
| `ops/dr/test_pinned_approval.py` | `100644` | 1,948 |
| `ops/dr/test_recovery_plan.py` | `100644` | 893 |
| `ops/dr/test_target_only_gate.py` | `100644` | 2,151 |
| `ops/hanuman/hanuman-controller.sh` | `100755` | 7,649 |
| `ops/hanuman/hanuman-panch-shakti.json` | `100644` | 9,957 |
| `ops/hanuman/ports.json` | `100644` | 4,538 |
| `ops/hanuman/social-platforms.json` | `100644` | 12,853 |
| `ops/jarvis/devices.json` | `100644` | 51,428 |
| `ops/jarvis/jarvis-24x7-controller.sh` | `100755` | 12,752 |
| `ops/jarvis/jarvis.env` | `100644` | withheld |
| `ops/jarvis/jarvis.env.example` | `100644` | 3,762 |
| `ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json` | `100644` | 61,050 |
| `ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json` | `100644` | 63,846 |
| `ops/vyomaraj-core/agents/CONTENT_OWNERSHIP_CURRENT.json` | `100644` | 12,659 |
| `ops/vyomaraj-core/agents/README.md` | `100644` | 6,563 |
| `ops/vyomaraj-core/agents/RECONCILIATION_RULES.json` | `100644` | 1,835 |
| `ops/vyomaraj-core/agents/app.js` | `100644` | 5,181 |
| `ops/vyomaraj-core/agents/index.html` | `100644` | 4,317 |
| `ops/vyomaraj-core/agents/inheritance_audit.py` | `100644` | 11,013 |
| `ops/vyomaraj-core/agents/rebuild_registry.py` | `100644` | 25,532 |
| `ops/vyomaraj-core/agents/styles.css` | `100644` | 4,877 |
| `ops/vyomaraj-core/agents/test_browser.cjs` | `100644` | 5,220 |
| `ops/vyomaraj-core/agents/test_inheritance_audit.py` | `100644` | 1,828 |
| `ops/vyomaraj-core/agents/test_registry.py` | `100644` | 8,593 |
| `ops/vyomaraj-core/aghor-experience/README.md` | `100644` | 2,806 |
| `ops/vyomaraj-core/aghor-experience/app.js` | `100644` | 2,405 |
| `ops/vyomaraj-core/aghor-experience/content.json` | `100644` | 26,257 |
| `ops/vyomaraj-core/aghor-experience/index.html` | `100644` | 5,203 |
| `ops/vyomaraj-core/aghor-experience/styles.css` | `100644` | 2,504 |
| `ops/vyomaraj-core/aghor-experience/test_browser.cjs` | `100644` | 3,946 |
| `ops/vyomaraj-core/approvals/app.js` | `100644` | 3,764 |
| `ops/vyomaraj-core/approvals/approval_queue.py` | `100644` | 5,087 |
| `ops/vyomaraj-core/approvals/content.json` | `100644` | 5,433 |
| `ops/vyomaraj-core/approvals/index.html` | `100644` | 5,699 |
| `ops/vyomaraj-core/approvals/styles.css` | `100644` | 3,660 |
| `ops/vyomaraj-core/approvals/test_approvals.py` | `100644` | 5,480 |
| `ops/vyomaraj-core/bhakti-experience/README.md` | `100644` | 5,438 |
| `ops/vyomaraj-core/bhakti-experience/app.js` | `100644` | 9,321 |
| `ops/vyomaraj-core/bhakti-experience/content.json` | `100644` | 28,426 |
| `ops/vyomaraj-core/bhakti-experience/index.html` | `100644` | 9,967 |
| `ops/vyomaraj-core/bhakti-experience/styles.css` | `100644` | 4,271 |
| `ops/vyomaraj-core/comics-experience/README.md` | `100644` | 1,024 |
| `ops/vyomaraj-core/comics-experience/app.js` | `100644` | 8,219 |
| `ops/vyomaraj-core/comics-experience/content.json` | `100644` | 23,368 |
| `ops/vyomaraj-core/comics-experience/index.html` | `100644` | 7,917 |
| `ops/vyomaraj-core/comics-experience/styles.css` | `100644` | 3,017 |
| `ops/vyomaraj-core/experience/CONTENT_CATALOG.json` | `100644` | 2,851 |
| `ops/vyomaraj-core/experience/CONTENT_EXTENSIONS.json` | `100644` | 3,997 |
| `ops/vyomaraj-core/experience/LOCAL_INTEGRATION.json` | `100644` | 3,013 |
| `ops/vyomaraj-core/experience/aghor_planner.py` | `100644` | 285 |
| `ops/vyomaraj-core/experience/assets/DEVANAGARI-LICENSE.txt` | `100644` | 4,384 |
| `ops/vyomaraj-core/experience/assets/devanagari.woff2` | `100644` | 50,416 |
| `ops/vyomaraj-core/experience/assets/fonts.css` | `100644` | 314 |
| `ops/vyomaraj-core/experience/comics_planner.py` | `100644` | 7,313 |
| `ops/vyomaraj-core/experience/film_planner.py` | `100644` | 5,968 |
| `ops/vyomaraj-core/experience/local_planner.py` | `100644` | 7,339 |
| `ops/vyomaraj-core/experience/music_planner.py` | `100644` | 5,798 |
| `ops/vyomaraj-core/experience/rebuild_contents.py` | `100644` | 7,326 |
| `ops/vyomaraj-core/experience/studio_server.py` | `100644` | 17,001 |
| `ops/vyomaraj-core/experience/test_aghor.py` | `100644` | 3,051 |
| `ops/vyomaraj-core/experience/test_browser.cjs` | `100644` | 3,321 |
| `ops/vyomaraj-core/experience/test_comics.py` | `100644` | 7,986 |
| `ops/vyomaraj-core/experience/test_comics_browser.cjs` | `100644` | 4,445 |
| `ops/vyomaraj-core/experience/test_current_registry.py` | `100644` | 2,526 |
| `ops/vyomaraj-core/experience/test_film.py` | `100644` | 8,247 |
| `ops/vyomaraj-core/experience/test_film_browser.cjs` | `100644` | 6,245 |
| `ops/vyomaraj-core/experience/test_governance.py` | `100644` | 1,824 |
| `ops/vyomaraj-core/experience/test_local_integration.py` | `100644` | 9,822 |
| `ops/vyomaraj-core/experience/test_music.py` | `100644` | 7,739 |
| `ops/vyomaraj-core/experience/test_music_browser.cjs` | `100644` | 6,041 |
| `ops/vyomaraj-core/experience/test_research_http.py` | `100644` | 3,996 |
| `ops/vyomaraj-core/film-experience/README.md` | `100644` | 4,344 |
| `ops/vyomaraj-core/film-experience/app.js` | `100644` | 12,846 |
| `ops/vyomaraj-core/film-experience/content.json` | `100644` | 35,738 |
| `ops/vyomaraj-core/film-experience/index.html` | `100644` | 9,177 |
| `ops/vyomaraj-core/film-experience/styles.css` | `100644` | 3,739 |
| `ops/vyomaraj-core/finance/app.js` | `100644` | 3,199 |
| `ops/vyomaraj-core/finance/content.json` | `100644` | 3,458 |
| `ops/vyomaraj-core/finance/finance_followup.py` | `100644` | 9,013 |
| `ops/vyomaraj-core/finance/index.html` | `100644` | 4,616 |
| `ops/vyomaraj-core/finance/styles.css` | `100644` | 2,302 |
| `ops/vyomaraj-core/finance/test_finance.py` | `100644` | 4,337 |
| `ops/vyomaraj-core/food-agent/ai_platforms_prompts.json` | `100644` | 14,542 |
| `ops/vyomaraj-core/food-agent/bloggers.json` | `100644` | 4,947 |
| `ops/vyomaraj-core/food-agent/books_history.json` | `100644` | 6,395 |
| `ops/vyomaraj-core/food-agent/chefs.json` | `100644` | 5,979 |
| `ops/vyomaraj-core/food-agent/cuisines.json` | `100644` | 4,129 |
| `ops/vyomaraj-core/food-agent/dishes.json` | `100644` | 6,591 |
| `ops/vyomaraj-core/food-agent/food_science_art.json` | `100644` | 20,191 |
| `ops/vyomaraj-core/food-agent/herbs_flavours.json` | `100644` | 3,115 |
| `ops/vyomaraj-core/food-agent/lost_recipes.json` | `100644` | 10,891 |
| `ops/vyomaraj-core/governance/PUBLIC_POLICY.json` | `100644` | 1,499 |
| `ops/vyomaraj-core/handover/AGENT_CONTENT_REGISTRY_V16_7_24.json` | `100644` | 8,425 |
| `ops/vyomaraj-core/handover/AGENT_RECONCILIATION_2026_10_03.md` | `100644` | 14,748 |
| `ops/vyomaraj-core/handover/AGHOR_RESEARCH_2026_10_03.md` | `100644` | 22,428 |
| `ops/vyomaraj-core/handover/ALL_UPDATES_V16_CHANGELOG.md` | `100644` | 11,060 |
| `ops/vyomaraj-core/handover/ARCHITECTURE_V16_8_2026_10_04.md` | `100644` | 10,931 |
| `ops/vyomaraj-core/handover/BHAKTI_FEATURE_UPDATE_2026_10_03.md` | `100644` | 15,884 |
| `ops/vyomaraj-core/handover/BUILD_AND_CONFIGURATION_2026_10_04.md` | `100644` | 10,708 |
| `ops/vyomaraj-core/handover/CONTENT_CREATOR_COLLABS.json` | `100644` | 2,535 |
| `ops/vyomaraj-core/handover/DR_AGHOR_INTEGRATION_2026_10_03.md` | `100644` | 22,594 |
| `ops/vyomaraj-core/handover/DR_RESOLUTION_2026_10_03.md` | `100644` | 10,858 |
| `ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md` | `100644` | 14,399 |
| `ops/vyomaraj-core/handover/ENTERTAINMENT_CONTRACTS_2026_10_03.md` | `100644` | 3,752 |
| `ops/vyomaraj-core/handover/EXPERIENCE_CONTENTS_2026_10_03.md` | `100644` | 36,929 |
| `ops/vyomaraj-core/handover/FILM_THEATRE_ADS_UPDATE_2026_10_03.md` | `100644` | 21,374 |
| `ops/vyomaraj-core/handover/FULL_SYSTEM_INVENTORY_2026_10_03.md` | `100644` | 15,895 |
| `ops/vyomaraj-core/handover/HANDOVER_ALL_UPDATES_2026_10_03.txt` | `100644` | 9,433 |
| `ops/vyomaraj-core/handover/HANDOVER_CHECKLIST.md` | `100644` | 7,024 |
| `ops/vyomaraj-core/handover/HISTORICAL_SYSTEM_INVENTORY_2026_10_03.md` | `100644` | 63,428 |
| `ops/vyomaraj-core/handover/INHERITANCE_AUDIT_2026_10_04.md` | `100644` | 4,564 |
| `ops/vyomaraj-core/handover/LAW_AND_ORDER_STATUTORY_COMPLIANCE.json` | `100644` | 8,240 |
| `ops/vyomaraj-core/handover/LAW_FULL_RESEARCH_V16_7.json` | `100644` | 47,677 |
| `ops/vyomaraj-core/handover/MUSIC_AUDIO_VIDEO_UPDATE_2026_10_03.md` | `100644` | 16,152 |
| `ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_2026_10_04.txt` | `100644` | 24,594 |
| `ops/vyomaraj-core/handover/PREVIEW_VERIFICATION_2026_10_04.json` | `100644` | 12,748 |
| `ops/vyomaraj-core/handover/PRIMARY_SECONDARY_FILE_SIZE_MATCH_V16_7_3.json` | `100644` | 11,114 |
| `ops/vyomaraj-core/handover/PRIMARY_SECONDARY_FILE_SIZE_MATCH_V16_7_5.json` | `100644` | 4,226 |
| `ops/vyomaraj-core/handover/PRIMARY_SECONDARY_SYNC.json` | `100644` | 3,365 |
| `ops/vyomaraj-core/handover/PRIORITY_RECOVERY_AUDIT_2026_10_03.md` | `100644` | 9,468 |
| `ops/vyomaraj-core/handover/README_HANDOVER_V16_5_3.md` | `100644` | 12,107 |
| `ops/vyomaraj-core/handover/README_HANDOVER_V16_7.md` | `100644` | 65,665 |
| `ops/vyomaraj-core/handover/RECOVERY_AND_HANDOVER_PACKAGE_2026_10_04.md` | `100644` | 5,111 |
| `ops/vyomaraj-core/handover/RESEARCH_INTEGRATION_2026_10_03.md` | `100644` | 17,063 |
| `ops/vyomaraj-core/handover/SOCIAL_PLATFORMS_CONTRACTS.json` | `100644` | 2,324 |
| `ops/vyomaraj-core/handover/SOVEREIGN_POLICY_2026_10_03.md` | `100644` | 3,471 |
| `ops/vyomaraj-core/handover/TEST_EVIDENCE_2026_10_04.json` | `100644` | 3,281 |
| `ops/vyomaraj-core/handover/TRANSFER_MANIFEST_2026_10_04.json` | `100644` | 6,240 |
| `ops/vyomaraj-core/handover/VIEW_ONLY_UPDATE_2026_10_03.md` | `100644` | 5,314 |
| `ops/vyomaraj-core/handover/build_configuration_report.py` | `100644` | 14,514 |
| `ops/vyomaraj-core/handover/build_dr_sync_report.py` | `100644` | 14,768 |
| `ops/vyomaraj-core/handover/build_transfer_package.py` | `100644` | 6,165 |
| `ops/vyomaraj-core/handover/preview_reports.py` | `100644` | 12,053 |
| `ops/vyomaraj-core/handover/rebuild_handover.py` | `100644` | 11,349 |
| `ops/vyomaraj-core/handover/test_build_configuration_report.py` | `100644` | 2,295 |
| `ops/vyomaraj-core/handover/test_dr_sync_report.py` | `100644` | 4,872 |
| `ops/vyomaraj-core/handover/test_preview_reports.py` | `100644` | 7,333 |
| `ops/vyomaraj-core/handover/test_rebuild_handover.py` | `100644` | 3,989 |
| `ops/vyomaraj-core/handover/test_transfer_package.py` | `100644` | 2,203 |
| `ops/vyomaraj-core/handover/transfer/NEXT_SESSION_TRANSFER_2026_10_04.zip` | `100644` | 75,684 |
| `ops/vyomaraj-core/handover/verify_preview.py` | `100644` | 8,452 |
| `ops/vyomaraj-core/healing-cache-clean.sh` | `100755` | 3,476 |
| `ops/vyomaraj-core/liquor-bar/README.md` | `100644` | 8,334 |
| `ops/vyomaraj-core/liquor-bar/app.js` | `100644` | 9,071 |
| `ops/vyomaraj-core/liquor-bar/content.json` | `100644` | 29,224 |
| `ops/vyomaraj-core/liquor-bar/index.html` | `100644` | 9,265 |
| `ops/vyomaraj-core/liquor-bar/server.py` | `100644` | 1,730 |
| `ops/vyomaraj-core/liquor-bar/styles.css` | `100644` | 10,590 |
| `ops/vyomaraj-core/liquor-bar/test_content.py` | `100644` | 5,262 |
| `ops/vyomaraj-core/multi-ai-coordination.js` | `100644` | 1,317 |
| `ops/vyomaraj-core/music-experience/README.md` | `100644` | 4,833 |
| `ops/vyomaraj-core/music-experience/app.js` | `100644` | 9,141 |
| `ops/vyomaraj-core/music-experience/content.json` | `100644` | 40,249 |
| `ops/vyomaraj-core/music-experience/index.html` | `100644` | 8,916 |
| `ops/vyomaraj-core/music-experience/styles.css` | `100644` | 8,666 |
| `ops/vyomaraj-core/preview-stable-fix.js` | `100644` | 1,506 |
| `ops/vyomaraj-core/research/CONNECTION_CHECK_2026_10_03.json` | `100644` | 3,800 |
| `ops/vyomaraj-core/research/README.md` | `100644` | 10,852 |
| `ops/vyomaraj-core/research/app.js` | `100644` | 6,217 |
| `ops/vyomaraj-core/research/compose.example.yml` | `100644` | 722 |
| `ops/vyomaraj-core/research/discovery.py` | `100644` | 21,729 |
| `ops/vyomaraj-core/research/index.html` | `100644` | 5,276 |
| `ops/vyomaraj-core/research/searxng-settings.example.yml` | `100644` | 233 |
| `ops/vyomaraj-core/research/styles.css` | `100644` | 5,707 |
| `ops/vyomaraj-core/research/test_browser.cjs` | `100644` | 4,618 |
| `ops/vyomaraj-core/research/test_discovery.py` | `100644` | 13,089 |
| `ops/vyomaraj-core/shriyantra-protection.js` | `100644` | 657 |
| `ops/vyomaraj-core/test_safe_metadata.cjs` | `100644` | 1,441 |
| `ops/vyomaraj-core/upgrades/app.js` | `100644` | 5,564 |
| `ops/vyomaraj-core/upgrades/change_manager.py` | `100644` | 7,097 |
| `ops/vyomaraj-core/upgrades/content.json` | `100644` | 3,828 |
| `ops/vyomaraj-core/upgrades/index.html` | `100644` | 5,534 |
| `ops/vyomaraj-core/upgrades/styles.css` | `100644` | 2,975 |
| `ops/vyomaraj-core/upgrades/test_upgrades.py` | `100644` | 5,485 |
| `ops/vyomaraj-core/upgrades/upgrade-controller.sh` | `100644` | 3,963 |
| `patch_v16_5_3_law_compliance.py` | `100644` | 12,161 |
| `patch_v16_6_food_healing.py` | `100644` | 41,885 |
| `patch_v16_7_law_entertainment.py` | `100644` | 65,440 |
