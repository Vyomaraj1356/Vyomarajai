# Current Vyomaraj hierarchy / Education reconciliation

**Later Aghor addition:** `BHAKTI-AGHOR-S1` is a new user-requested slot. Active total is now 128 (BHAKTI 3, named 42, unnamed 86); the earlier 127-slot reconciliation and 180-test results below describe the preceding baseline. Current evidence: `/reports/resilience`. The active index now contains 197 references across Education and the five editorial packs (21 Education + 109 Entertainment + 67 Bhakti, including the 33 Aghor chapter/profile/practice/care records) — the 173 quoted in the 2026-10-03/04 documents is that date's earlier count, kept there as a dated snapshot.

The user explicitly approved **all Government Schemes under Education** and **Comedy, Cartoon, Music, Movie, Wit and Shayari as parent headings, not extra counted agents**.

## Current source of truth

- `AGENT_REGISTRY_CURRENT.json`: 13 categories, **128 counted positions**, six uncounted headings; **Education 16, Finance 7, Entertainment 32**. Bhakti-Shakti now has 3 after the newly requested Aghor addition; other category counts are unchanged.
- `RECONCILIATION_RULES.json`: owner-approved transformation from the pinned historical registry. The active builder is deterministic and refuses conflicting duplicate identities.
- `CONTENT_OWNERSHIP_CURRENT.json`: 21 Education topic references, including all Government Schemes. Source-backed single-slot mappings are retained; shared Grantha positions remain unmapped.
- `CONTENT_INDEX_CURRENT.json`: 197 indexed references (21 Education + 176 selected references from the five editorial packs and the Aghor addition). **Not** all 421 products or an exhaustive archive-content inventory.
- The V16.7.24 historical registry still reports 133. It is preserved byte-for-byte, not the current hierarchy. The previous full report is preserved byte-for-byte as `handover/HISTORICAL_SYSTEM_INVENTORY_2026_10_03.md`.

Unnamed agents have `name: null`, `name_status: UNKNOWN`. The viewer displays only their serial unless audit IDs are explicitly enabled. Serials are **new display positions**, not recovered source slot mappings. The PLATFORM unnamed position is not falsely assigned a historical S20. Existing Music/Movie/Liquor/Bar IDs remain stable; the local planner and discovery enqueue validate them against the active registry. Named creative functions in the earlier editorial packs remain **proposals**, not assigned agent names.

All government schemes move as a single existing Finance position into Education. The old canonical Finance roster had only a count; the historical diagram supplied the Govt Schemes label. The new transfer is explicitly owner-approved rather than a recovered complete Finance slot map. No financial scheme database was found or claimed moved. No benefits, eligibility, dates or application advice were invented.

The current editorial packs did not contain a misplaced Education pack. The Education page gives the supplied roster and available historical topic references an explicit current owner. It does not claim to recover missing full courses, lectures, texts or chapter lists. Existing content stays available through its original source references.

## Duplicate policy

- Categories, source roster entries, groups, lanes and named lists: an identical record with the same identity is included once. A conflicting identity fails rather than deleting either meaning.
- Six overlapping counted hub positions were reclassified by user approval; their names/child edges remain as headings. This is not a claim that six source records were byte-identical.
- Every active node ID is globally unique, every counted slot has one valid parent and one category, and display serials are unique/contiguous within each category.
- Active content references are de-duplicated by scoped stable identity **and full source-record equality**, not fuzzy title matching. Different works, editions, record types and contexts are retained. Source pack records are not destructively rewritten.
- All 32 historical catalogue paths are already unique. Multiple files referring to one agent do not create multiple agents. Historical archives, snapshots and versions are not deleted as “duplicates.”
- Historical sovereign roles remain separate cross-cutting references, not extra children in the current total. No unverified third-level roster has been invented.

There are 42 supplied/approved individual names and 86 unnamed positions. Source-reported product numbers remain historical metadata; **current product ownership/counts are unreconciled**, particularly after the Government Schemes transfer. The complete 421-title list is unavailable, so no fabricated “all products deduplicated” claim is made.

## Ask the catalog (retrieval over these two files)

`ask_catalog.py` selects rows from `AGENT_REGISTRY_CURRENT.json` and
`CONTENT_INDEX_CURRENT.json` and cites them; `ask_server.py` serves it with `ask.html`.

```bash
python3 ops/vyomaraj-core/agents/ask_server.py --port 4190   # open http://localhost:4190
python3 -m unittest discover -s ops/vyomaraj-core/agents -p 'test_*.py'
```

- `GET /api/ask?q=gita&limit=10` → ranked records with `citation` (`file#/record-id`), matched terms and score.
- `GET /api/stats` → counts read from the files (128 positions, 197 references, 13 categories, 6 headings).
- Unnamed positions are returned as serial-only slots; nothing is named on their behalf.
- A query whose words do not all match returns **no results and says so** — no nearest guess.
- **Retrieval, not generation.** There is no model call and no model key; a generated answer would sit behind the same `ask()` seam once a key is configured. Do not describe this as AI answering.

## Viewer and commands

```bash
python ops/vyomaraj-core/agents/rebuild_registry.py
python ops/vyomaraj-core/agents/rebuild_registry.py --check
python -m unittest discover -s ops/vyomaraj-core/agents -p 'test_*.py' -v
python ops/vyomaraj-core/experience/studio_server.py --home agents --port 4176
```

- `/agents/`: complete serial-first active roster and reference index.
- `/education/`: Education default filter, all 16 positions and 21 topic references.
- `/reports/agents`, `/reports/`: current reconciliation and full inventory.
- `/reports/history`: historical audit with an explicit supersession banner.
- Existing Film, Music, Bhakti, Pairings and Research views all link to the current directory/Education.

The builder reads only the pinned metadata registry, explicit rules/ownership, the five reviewed editorial packs and the historical filename catalogue. Source topic paths are checked for existence, not ingested as arbitrary HTML/code. Runtime, device, Hanuman and environment bodies are not imported. The server allows only explicit public metadata/assets/reports; builder/rule/private paths are not served. No source controllers, archive members, external AI, media downloads, publication or DR operations run during reconciliation.

**Earlier baseline validation: 180 automated checks PASS** (DR 29, handover 13, Pairings 9, integrated experience/HTTP 62, research 36, active registry 28, Node 3). All **five real Chromium suites PASS**, including serial-only display, unique hierarchy identities, Education ownership, current versus historical reports and existing media/planner flows. Both rebuild checks, six app-script syntax checks, YAML syntax and diff checks pass. Previous inventory preserved byte-for-byte; canonical source hashes unchanged. No external AI/production/DR success is claimed.

Directory serials run within each category; the Music/Movie experience widgets number their six local positions. These are presentation numbers, not different agent identities; the internal IDs are unchanged.

## Shared capability reference (7 October 2026)

The shared Panch-Brother behavior model is centralized at `config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml`, referenced through ShriYantra / Universal Knowledge Fabric, and resolved locally by `ops/vyomaraj/capability_fabric.py`. It adds no per-agent copies and grants no permissions or root authority. `python3 ops/vyomaraj/capability_fabric.py check` validates metadata only; runtime execution and production enforcement remain unimplemented/unverified.

The requested 14-category / 153-slot target (six FOOD additions, five EDU additions, and fourteen Real Estate slots) is recorded in `docs/vyomaraj/context/00_MASTER_CONTEXT.md`. The current registry remains 13 / 128 / 421 until the exact supplied IDs/names are reconciled across the source, builder, tests, viewers, gates, and current documents. Historical snapshots and archives remain intact.
