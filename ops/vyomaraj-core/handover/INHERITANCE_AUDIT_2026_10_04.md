# Vyomaraj — inheritance audit — 2026-10-04

**Generated file — do not edit by hand.** Rebuild with `python3 ops/vyomaraj-core/agents/inheritance_audit.py` from the repository root; `--check` verifies this checked-in copy still matches its sources.

Scope: what the repository's own current metadata records about **inheritance** — the current structure, content-ownership routing and the shared page theme. This is **not** a runtime audit: no agent, provider, device, account or service is asserted operational.

## 1. Structural inheritance — agent registry

Status: `CURRENT_OWNER_APPROVED_STRUCTURE_not_runtime_inventory` (updated 2026-10-03). Source snapshot: `handover/AGENT_CONTENT_REGISTRY_V16_7_24.json`.

| Category | Counted sub-agents | Named | Name UNKNOWN | Source-reported (historical) | Products (historical) |
|---|---|---|---|---|---|
| FOOD — Food & Social Connect | 3 | 0 | 3 | 3 | 6 |
| EDU — Education | 16 | 10 | 6 | 15 | 68 |
| ASTRO — Astro-Celestial & Universal | 3 | 0 | 3 | 3 | 9 |
| FINANCE — Finance & Wealth | 7 | 0 | 7 | 8 | 15 |
| LIFE — Life Coach & Wellness | 10 | 0 | 10 | 10 | 34 |
| BHAKTI — Bhakti Mandir — Ritual, Festival & Grantha | 3 | 1 | 2 | 2 | 8 |
| SPORTS — Sports & Legends | 14 | 0 | 14 | 14 | 29 |
| AGRI — Agriculture & Environment | 6 | 0 | 6 | 6 | 14 |
| ENTERTAINMENT — Entertainment — Comedy, Movies, Hollywood, Bollywood | 32 | 2 | 30 | 38 | 168 |
| PLATFORM — Platform & Social Hub + Earn — All Platforms + Monetization | 20 | 19 | 1 | 20 | 39 |
| TOUR — Tour and Travel | 4 | 0 | 4 | 4 | 9 |
| WAR — War Room — Warriors | 5 | 5 | 0 | 5 | 13 |
| PODCAST — Podcast & Entertainment Studio | 5 | 5 | 0 | 5 | 9 |
| **Total (counted)** | **128** | **42** | **86** | 133 | 421 |

- Every one of the 128 counted rows resolves to one of the 13 category ids; the category sum equals the total.
- 86 rows carry `name_status: UNKNOWN` and no name — nothing is invented to fill a slot; serial-only entries are display placeholders, not recovered identities.
- 6 parent headings are uncounted after reclassification (reclassified, not deleted).
- Product policy: 421 is a historical aggregate, not a verified deduplicated/current owner-assigned product inventory.
- Hierarchy policy: Only the six explicitly approved hubs acquire child edges. Other missing sub-sub-agent mappings remain UNMAPPED; do not invent a third tier.

## 2. Content-ownership routing

- 173 indexed references — **BHAKTI** 67, **EDU** 21, **ENTERTAINMENT** 85 — every owner resolves to a registry category.
- All 21 education topics are owned by EDU; the ownership map keeps `Government Schemes` there after the approved transfer from FINANCE.
- Editorial pack owners: `aghor` → BHAKTI, `bhakti` → BHAKTI, `film` → ENTERTAINMENT, `music` → ENTERTAINMENT, `pairings` → ENTERTAINMENT.
- No indexed reference claims imported full content: every record carries `full_content_imported: false` (metadata references only).

## 3. Applied ownership rules

- Government Schemes: FINANCE → EDU, 1 slot (`EDU-GOV-S1`), owner approved.
- Six Entertainment hubs remain parent headings (6 listed); the surplus source-reported slots were reclassified, not deleted.
- New sub-agent from the rules: `BHAKTI-AGHOR-S1` (Aghor & Aghori) in BHAKTI.
- Distinct named entries (INDICOM, Criticism gate) and historical archives are preserved.

## 4. Theme and page inheritance

- Both report servers render from ONE shared theme constant (`preview_reports.STYLE`: Shani Blue #0a1628, Kuber Gold #f59e0b); the lane server imports it as `reports.STYLE` instead of defining its own.
- Every allowlisted report page on both servers carries that shared style, the same fixed navigation block and the three reference pages (`/reports/chats`, `/reports/issue-6`, `/reports/test-evidence`); both test suites assert this.
- This section verifies the source relationship and the palette tokens only; the audit itself renders no page.

## 5. What this audit does not assert

- Runtime inheritance: every registry row carries `runtime_status: NOT_VERIFIED`; counts describe recorded structure, not running agents.
- Product ownership at item level stays UNRECONCILED — `active_products` is `null`, not zero; the historical 421 is an aggregate, not a verified inventory.
- No provider account, revenue channel, device, contract or external AI service was contacted, and none is reported operational here.
- Sovereign roles: 11 historical cross-cutting roles remain historical records, not additional category children.
