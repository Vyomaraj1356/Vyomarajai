# Vyomaraj / Jarvis — Integrated Research & System Update

> **Latest DR / Aghor follow-up:** `/reports/resilience` supersedes earlier live-status statements below. Primary main advanced to `9be6d39`; the corrected secondary ends `6d64e`. Main Actions run `37123060948` passed authentication but failed replication; integrity reporting was skipped. Arena access still differs (404/403). A same-host failover rehearsal is tested separately, not production DR. The newly requested Aghor sub-agent makes the active total 128 (BHAKTI 3); see `/aghor/` and `/reports/aghor`.

> **Later owner-approved reconciliation:** Current directory `/agents/`; Education and all Government Schemes `/education/`; report `/reports/agents`. Current counts are 13 categories / 127 counted slots / 6 uncounted headings (Education 16, Finance 7, Entertainment 32). Earlier 133/38/15/8 figures below describe the historical snapshot, not current counts. Existing feature slot IDs and earlier validation evidence are preserved.

**3 October 2026 · review branch · metadata-only discovery · no production or DR-success claim**

## Executive result

A working local **Research Desk** is integrated with the four existing experiences and report viewer. It supplies a durable local queue, six repeatable research profiles, source-aware adapters, de-duplication, caching, per-provider outcomes, metadata-only review and JSON export. Optional SearXNG/Ollama connectors and an opt-in daily Actions workflow are implemented, but their services/schedule are **not active**.

The actual six-profile run re-indexed **12 existing editorial leads**: 1 music, 5 film/archive, 3 Marathi-theatre and 3 Hindi-theatre. **Zero fresh internet leads** were retrieved. MusicBrainz, Open Library and Library of Congress calls failed at the network layer in this sandbox. No failure was presented as a successful empty search. No film, song, script or theatre recording was downloaded.

**DR remains BLOCKED.** The linked PAT diagnostic commit corrected curl formatting, not credentials, scope or secondary visibility. The new Python preflight is tested and integrated, but cannot grant missing GitHub permissions or inspect the Actions secret.

## Open the integrated viewer

| Area | Route | Current capability |
|---|---|---|
| Research Desk | `/research/` | Queue, source outcomes, review, metadata export |
| This consolidated update | `/reports/research` | Configuration, actual evidence, limitations |
| All four content extensions | `/reports/contents` | Every current editorial record and source index, not all 421 historical titles |
| Film, theatre & ads | `/film/`, `/reports/film` | References, original outlines, local authorized-file cut preview |
| Music, radio & video | `/music/`, `/reports/music` | Catalogue, local queue/playback, deterministic plans |
| Bhakti-Shakti | `/bhakti/`, `/reports/bhakti` | Proposed story/food chapters, local personalization |
| Roots & Pairings | `/pairings/` | Traditions, chakhna, browser food demonstration |
| Historical inventory | `/reports/` | Preserved canonical agent/content counts |
| DR evidence | `/reports/dr` | Redacted status, safe replication runbook, remaining block |

All four experiences link to the Research Desk and this report. Asset/report routes are explicitly allowlisted. Database, environment, device/runtime records and `.git` are not served. Browser calls use same-origin relative APIs suitable for the Arena preview.

## Platforms: implemented versus connected

| Component | Integration | Real status here |
|---|---|---|
| Existing Music/Film catalogue | Allowlisted attributed editorial metadata | **WORKING locally**; 12 leads, not a new online search |
| MusicBrainz | JSON release-group adapter; artist/date queries | **BLOCKED: network_unavailable** |
| Library of Congress | Audio and film/video JSON adapters | **BLOCKED: network_unavailable** |
| Open Library | Selected-field work search for author/script leads | **BLOCKED: network_unavailable**; not a performance licence |
| SearXNG | Local JSON search connector and example configuration | **NOT CONFIGURED / NOT DEPLOYED** |
| Ollama | Local structured advisory-note connector | **NOT CONFIGURED**; no model selected, installed or tested |
| Daily/manual research | Read-only Actions workflow, main + approval-variable gate | **NOT ACTIVE**; review branch unmerged, variable access denied |
| Primary → DR | Redacted preflight plus existing explicit replication gates | **BLOCKED**; secondary unreadable, no write attempted |

MusicBrainz documents a meaningful application User-Agent and at most one call per second; this implementation reserves 1.1 seconds per provider in its shared local database. [1](https://musicbrainz.org/doc/MusicBrainz_API)

Technical reference links for the other adapters: [Open Library search](https://openlibrary.org/dev/docs/api/search), [LOC JSON API](https://www.loc.gov/apis/json-and-yaml/), [SearXNG search API](https://docs.searxng.org/dev/search_api.html), [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs). These are implementation references, not proof of live connections. Deployment/model/provider metadata licences and service terms still need operator review.

No paid AI subscription or provider key is required for the implemented public-metadata adapters. No external AI platform was consulted on the user's private repository. The optional model sees only bounded title/date/source metadata, not repository files, secrets or private conversations.

## Six repeatable profiles and proposed existing-slot routes

| Profile | Proposed slot | Evidence / scope |
|---|---|---|
| Classic Hindi music | `ENT-MUS-S1` | Lata-related editorial lead, artist query, LOC audio, optional web search |
| 2025–2026 music | `ENT-MUS-S2` | Provider first-release-date query; not live charts or verified release dates |
| Indian film & archives | `ENT-MOVIE-S3` | Existing film references and archive metadata |
| Recent Marathi/Hindi films | `ENT-MOVIE-S1` | Optional SearXNG query only; currently blocked, no fabricated replacement |
| Marathi theatre/script leads | `ENT-MOVIE-S4` | Existing references + Vijay Tendulkar bibliographic query |
| Hindi theatre/script leads | `ENT-MOVIE-S5` | Existing references + Mohan Rakesh bibliographic query |

These are proposed routing functions, **not recovered names or new agents**. All canonical Music/Movie names remain **UNKNOWN**. BHAKTI child mappings remain **UNMAPPED**. Results can be irrelevant, differently dated, translated or edition-specific; a book record is not a licensed recording. Keep original play, revival, adaptation and film version separate.

## What a research pass does

1. Browser selects a fixed operator-owned profile; arbitrary URLs, shell commands and free-form automation instructions are rejected.
2. A SQLite queue de-duplicates pending/recent requests. One active worker consumes jobs while the preview runs; CLI can drain the same queue.
3. Source adapters read **metadata only**. Successful responses cache for 24 hours; legitimate zero results differ from transport/API failure. No automatic tight retry loop.
4. At most five leads per source retain provider IDs, source links, provider-claimed dates and first/last-seen timestamps. Stable provider + record IDs prevent duplicate re-import; cross-provider identities/editions are not guessed.
5. Re-seen metadata preserves review state; changed title/date/source/description resets review to pending. Changed slot/profile proposals are retained together.
6. Human reviewer can accept **metadata only**, reject, or reset. Rights remain `UNKNOWN`, availability `NOT_VERIFIED`, media URL null. Neither editorial pack nor canonical registry is altered.
7. Optional Ollama may supply one bounded **unverified advisory note** per job. Strict JSON parsing, no tools and no rights/publication authority; model output is never a trusted approval.
8. JSON export contains metadata and local review state, **not media files or legal clearance**.

Limits: 10 pending jobs, one active job, five normalized leads/source, 2 MB response ceiling, 20-second socket timeout, 5,000 stored records, ~200 recent completed jobs and 10,000 retained local review events. Explicit capacity errors; accepted/rejected records are not silently evicted. Lease-expired work is marked interrupted, not secretly retried. A socket timeout is not a total operation deadline; Actions supplies a ten-minute outer limit.

Local review is an unauthenticated prototype decision, not an identity-verified editorial signature. Same-origin JSON enforcement is not a substitute for production authentication. Restrict this preview to trusted reviewers.

## Recurrence and scale: configured, not overstated

- Workflow: `.github/workflows/vyomaraj-research.yml`.
- Daily schedule: **03:15 UTC / 08:45 India time**, subject to GitHub scheduler delays; manual profile selection also defined.
- Activation requires reviewed merge to `main` and `VYOMARAJ_RESEARCH_ENABLED=true`. Neither was done. Existing PR [#5](https://github.com/Vyomaraj1356/Vyomarajai/pull/5) remains open on this session branch.
- Contents-read-only permissions, no PAT, no source-branch push, no PR creation and no site publication. Partial/blocked results exit nonzero; evidence artifacts still upload.
- Actions queue/cache and this viewer's local queue are **separate**. Cache restore is best-effort, not durable production storage; artifacts retain 30 days. No automatic artifact ingestion or synchronization of local reviews is claimed.
- For repeated work on the same approved host, schedule the CLI against the same `--db` file and service environment. The viewer's worker processes queued jobs, but does not itself enqueue daily jobs.
- Scaling now means bounded, repeatable single-host work. Distributed infrastructure, authenticated reviewer roles, shared PostgreSQL/queue, global egress quotas, monitoring and backup services are **not installed**. Independent stores behind one egress IP need a shared provider limiter.

Optional local deployment templates are in `research/compose.example.yml` and `research/searxng-settings.example.yml`. They were not executed: Docker and Ollama executables were absent. Review/pin container digests, engine terms, local resource requirements and model licences before use. No model download occurs automatically; example floating tags are not production pins. Service endpoints stay private/server-side, never browser `localhost` calls.

## Fresh DR / PAT evidence and applicable fix

The user-linked main commit is [e69af4d](https://github.com/Vyomaraj1356/Vyomarajai/commit/e69af4d6155aca87eb87f3da5c4c90e1b8b681a1). Inspection shows it repaired two malformed multiline curl commands, for identity and target-repository diagnostics. It does not fix expired credentials, permissions, repository selection or hidden private targets. Reapplying those old shell lines to the current Python workflow would not solve the block.

New `ops/dr/dr_diagnostics.py`:

- GET-only identity, primary repository/main and explicitly supplied secondary repository/main checks.
- Narrow client allowance for GET `/user`; no user writes or arbitrary external URL.
- Exact repository-name matching; malformed/primary-as-secondary targets rejected.
- Redacted 401/403/404 reasons; no raw response, login, token, scopes or credential values printed.
- Identity success cannot authorize repository access. Main-ref readability cannot prove write scope or matching content trees. Installation-token identity failure does not automatically invalidate successful repository GETs.
- Workflow writes a diagnostic artifact before existing verification/sync; failure stops replication. Existing main-only, approval-variable, stable-reference, non-force and exact-tree guards remain.

Observed local result:

| Check | Outcome |
|---|---|
| Credential source | Local `gh` fallback; **not the Actions secret** |
| Identity endpoint | Readable; identity body withheld |
| Primary repository / main | Readable; main still `e69af4d6155aca87eb87f3da5c4c90e1b8b681a1` |
| Old-main secondary candidate | HTTP 404 — missing/renamed OR hidden by permissions |
| Primary Actions variables | HTTP 403 |
| Secondary main | Not attempted after repository access failed |
| Secondary writes / traffic changes | None |
| DR synchronization / write authorization | Not verified |

Inspected run [37120524834](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/37120524834), review-branch head `bb6c1dd`: `offline-tests` succeeded, `verify-or-sync` **skipped**. A green feature-branch run is not DR success. Sanitized results are saved in `ops/dr/DR_FOLLOWUP_2026_10_03.json`; existing earlier recovery evidence is preserved separately. No repeated target-name guessing, secondary creation, force push or merge was performed.

**Still required for DR:** the GitHub connection needs appropriate repository/Actions access; the owner must confirm the approved secondary and configure the Actions PAT/variables privately in GitHub. Then run the read-only preflight/compare before authorizing replication. Secrets must never be pasted in chat. We cannot modify permissions through a formatting fix.

## All earlier content work remains integrated

| Delivered area | Retained content / capability | Important boundary |
|---|---|---|
| Roots & Pairings | Regional/global traditions, eight chakhna concepts, 12/10 proposed Liquor/Bar chapters | Adult/legal safeguards, food/allergen guidance; no unsafe distillation or health claims |
| Bhakti-Shakti | 12 proposed story chapters, ten-avatar overview, nine starter Peetha profiles, three prasad-style concepts | Not a complete Peetha list or connected AI renderer; local 3D/4D/5D demonstration means rotation, steps and preferences |
| Music & media | 39 cards, 27 sources, six existing-slot proposals, local queue/playback/planning | No licensed streaming or autonomous broadcaster; IFPI 2025 annual chart snapshot is not live 2026 ranking |
| Film, theatre & ads | 27 references/formats, 25 sources, six existing Movie-slot proposals, seven outline formats, Marathi/Hindi/English original dialogue samples | Outlines are not full scripts; hard-cut browser preview/EDL is not rendered MP4 or commercial-footage licensing |
| Historical recovery | 43 archives preserved; inventory and historical catalogue retained | No invented missing names or private-chat/session recovery |

Canonical totals unchanged: **13 categories / 133 sub-agents / 421 products; 46 known and 87 UNKNOWN names; sub-sub mappings UNMAPPED; exactly 32 historical JSON filenames cataloged.** The 293 selected labels include duplicates and are not 421 recovered titles. Research leads and editorial extensions do not increment those historical totals. No populated private device/runtime values are added to the report.

## Validation

**145 automated checks PASS:** DR 29, handover 13, Roots & Pairings 9, integrated experience/API 56, discovery 35, Node metadata-safety 3.

**All four real Chromium suites PASS:** Research Desk; Film/Stage/Ads; Music; Bhakti/Pairings. Research coverage includes an actual queued job reaching a terminal source outcome, desktop/mobile layout, six profiles, acknowledgement-gated accept/filter/reset, JSON download retaining UNKNOWN rights/null media, source-link safety, navigation from all four experiences, report rendering, and no external browser requests, JS errors or horizontal overflow. Review test changes were reset; they do not approve any media.

All five app scripts pass Node syntax checks. The two workflows and optional service templates parse as YAML; this is syntax validation, **not container or Actions execution**. Shell syntax, pinned inventory rebuild and `git diff --check` pass. Canonical hashes unchanged:

- Registry: `9e301bfcb1c6e8b23c1bea4fbdcf0d9d12d4c457fe62d7ef60e3161ac3a908a9`.
- Catalogue: `86f2fc0a5b5c9adb606b5f72aa5047fa8ed0bf5bc6c7d9bcd9c82dbcf5b95f70`.

Live public-provider failures are actual CLI results, distinct from passing mock-adapter/Ollama tests. No real model was used. Snapshot evidence: `research/CONNECTION_CHECK_2026_10_03.json`; deployment/runbook: `research/README.md`.

## Activation checklist, not a claim of completion

1. Review the current branch/PR; no merge was performed.
2. Restore appropriate GitHub repository/Actions access and confirm the secondary privately; re-run read-only DR checks.
3. Provide an approved network environment for public APIs; verify each source outcome before calling it connected.
4. Optionally deploy SearXNG and/or a licence-reviewed installed Ollama model; run the profile against the real service. No provider key is requested in chat.
5. After review, activate recurrence on the approved host or opt-in main workflow. Establish backups, authenticated review and global quotas before production scale.
6. Obtain item-specific lawful permissions before any future media acquisition, adaptation, streaming, remix or publication. This pipeline does not perform those actions.
