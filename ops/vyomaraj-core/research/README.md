# Vyomaraj / Jarvis Research Desk

Metadata discovery and local human review, **not media downloading, autonomous publishing or a production AI service**. Standard-library Python; no pip dependencies. Uses existing Music/Movie slots as **proposed** functions, canonical names **UNKNOWN**. No canonical registry or editorial-pack writes.

## Run

From the repository root:

```bash
python ops/vyomaraj-core/experience/studio_server.py --port 4176 --home research
# Open the preview's /research/ route. Relative browser API URLs only.
python ops/vyomaraj-core/research/discovery.py run --profile marathi-theatre
python ops/vyomaraj-core/research/discovery.py status
python ops/vyomaraj-core/research/discovery.py export --output research-candidates.json
python -m unittest discover -s ops/vyomaraj-core/research -p 'test_*.py' -v
```

The preview's daemon worker consumes queued jobs while that process is running. It does **not** enqueue daily searches itself. CLI `run` enqueues and drains pending jobs; status/export do not call external providers. Exit code **2** means a requested/processed job is partial, blocked, failed or still queued/running elsewhere, not an all-provider success. Reusing an earlier blocked job never becomes a false zero-work success. Local database: ignored `.state/discovery.sqlite3`. Export is metadata-only JSON; neither an encoded video nor licensed media. Do not serve the repository directory with a generic file server.

## Configured adapters and actual observations, 3 October 2026

| Adapter | Implemented path | Observed here |
|---|---|---|
| Existing catalogue | Explicitly allowlisted Music/Film packs | Working: 12 attributed existing leads across four profiles; not fresh online research |
| MusicBrainz | Release-group metadata search, descriptive User-Agent, JSON | Runtime `network_unavailable`; mock-response tests pass |
| Library of Congress | Film/video or audio JSON metadata | Runtime `network_unavailable`; mock-response tests pass |
| Open Library | Work search, selected fields | Runtime `network_unavailable`; bibliographic/script leads, not performances |
| SearXNG | Optional local `/search?format=json` | Not configured/deployed; mocked integration tested |
| Ollama | Optional local `/api/chat`, JSON schema | No model/service installed or selected; mocked integration tested |

MusicBrainz requires a meaningful User-Agent and no more than one call/second; reservations use 1.1 seconds per provider in the shared local SQLite database. [1](https://musicbrainz.org/doc/MusicBrainz_API)

Other implementation references: [Open Library search API](https://openlibrary.org/dev/docs/api/search), [LOC JSON API](https://www.loc.gov/apis/json-and-yaml/), [SearXNG search API](https://docs.searxng.org/dev/search_api.html), [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs). Documentation access is not runtime-connection verification.

## Query profiles

- Classic Hindi music: existing Lata-related editorial lead, MusicBrainz artist query, LOC audio, optional SearXNG; proposed `ENT-MUS-S1`.
- 2025–2026 music: MusicBrainz first-release-date search and optional SearXNG; proposed `ENT-MUS-S2`. Provider-claimed dates are unverified; includes possible future or incorrect records, not a live chart.
- Indian film/archive (classic and modern existing references): existing film references, LOC and optional SearXNG; proposed `ENT-MOVIE-S3`.
- Recent Marathi/Hindi films: optional SearXNG only; proposed `ENT-MOVIE-S1`. **Currently blocked without that service.** No substitute list is fabricated.
- Marathi theatre: existing references, Open Library author search, optional SearXNG; proposed `ENT-MOVIE-S4`.
- Hindi theatre: existing references, Open Library author search, optional SearXNG; proposed `ENT-MOVIE-S5`.

Profiles are editable operator-owned Python configuration, not arbitrary browser prompts/URLs. Search matching is imperfect; all leads require relevance, edition, language and date checks. Historic vs new is a discovery query, not a verified classification. A theatre text, revival, production recording and film adaptation remain different things.

## Optional local open-source services

`compose.example.yml` and `searxng-settings.example.yml` are **unexecuted deployment templates**, not a running integration. Neither Docker nor Ollama was available in this sandbox. Review project/model licences, engine terms, image digests, model size, resources and network policy first. Floating image tags are examples, not reproducibly pinned production dependencies. SearXNG forwards search queries to external engines; it is not private/offline search.

On an approved Docker host, from this directory:

```bash
# Generate locally; never echo, paste in chat or commit this value.
export SEARXNG_SECRET="$(python -c 'import secrets; print(secrets.token_hex(32))')"
# After replacing example image tags with reviewed digests:
docker compose -f compose.example.yml up -d searxng
# Optional, starts an empty runtime; DOES NOT install a model:
docker compose -f compose.example.yml --profile ai up -d ollama
```

Approve/install a model separately according to its licence and resource needs. No model pull command is run by Vyomaraj. Start the Python preview process with only the required explicit process variables (legacy env files are never loaded):

```bash
export VYOMARAJ_SEARXNG_URL=http://127.0.0.1:8080
# Set only after a reviewed model has actually been installed:
export VYOMARAJ_OLLAMA_URL=http://127.0.0.1:11434
export VYOMARAJ_OLLAMA_MODEL='<operator-approved-installed-model>'
```

Use the real model tag in place of the placeholder. Restart the studio after changing its process environment. Local endpoints are allowlisted to loopback or the corresponding Compose service hostname, on ports 8080/11434; arbitrary remote endpoints, credentials in URLs and redirects are refused. Browser requests remain same-origin `/api/research/...`; these loopback addresses are **server-side only**. No cloud-provider keys are requested or configured. Never expose these unauthenticated services directly through public ingress.

Ollama can produce **one** capped advisory note per job, from title/date/source URL, with structured JSON and no tools. Metadata is untrusted prompt content. Parsing is strict, extra action fields are rejected, displayed text is escaped, and a note cannot approve rights, change a canonical agent, publish or execute code. This reduces consequences of prompt injection; it does not make AI output factually trustworthy. A configured model or URL is not a successful connection.

## Recurrence, durability and honest scale limits

`.github/workflows/vyomaraj-research.yml` defines daily **03:15 UTC / 08:45 India time**, plus manual profile selection. It only runs on approved `main` with repository variable `VYOMARAJ_RESEARCH_ENABLED=true`. **Not active now:** the workflow is review-branch code and Actions-variable access is blocked. The job has read-only repository permission, a ten-minute timeout, fixed profiles and artifact outputs; no PAT, site write, PR or publication is performed. Partial/blocked sources cause nonzero exit and evidence is still uploaded. Until optional SearXNG is configured, `all` includes an explicitly blocked recent-film profile.

GitHub-hosted runners do not inherit this preview's local services/database. The Actions queue is a **separate** best-effort cache restored by concurrency-serialized runs, with review artifacts retained 30 days. Cache eviction loses that queue; artifacts are not a durable production database. Local viewer reviews do not magically synchronize to Actions. No automatic artifact ingestion is implemented. To use the very same reviewed queue repeatedly, schedule the CLI on the approved host using the same `--db` path and service environment. Keep its backups outside Git.

One active job across SQLite-connected workers; 10 pending jobs maximum, five normalized leads per source, 2 MB JSON response ceiling, 20-second socket timeout, 24-hour successful-response cache (including legitimate empty results), 60-second per-profile queue de-duplication. No automatic rapid retries on 403/429/503 or transport failures. A later deliberate pass/daily schedule may retry. Requests that fail are **not** converted into empty successful results. Socket timeout is not a total wall-clock bound; workflow-level timeout is the outer guard. Do not run multiple independent stores behind one egress IP without a shared provider limiter.

Provider + stable-record-ID de-duplication preserves different editions and sources rather than guessing cross-provider identity. Re-seen records retain review state; changed title/date/source/description resets it to pending. Profile/slot proposals merge. Caps: 5,000 records (fail explicitly at capacity), ~200 recent completed job records, 10,000 local review events. Interrupted work gets an explicit lease-expired state, not an automatic retry. No accepted/rejected record is silently evicted; export/archive and operator review are required at capacity. SQLite supports a modest single-host queue, **not distributed or unlimited scale**. Production would need authenticated RBAC, PostgreSQL/managed queue, global quota coordination, source-specific contracts and monitoring; not installed or claimed here.

## Trust and rights gates

`pending_review → accepted_metadata_only / rejected` affects only this queue. Every record retains `rights_status=UNKNOWN`, `availability=NOT_VERIFIED`, `media_url=null`. Acceptance never adds a record to published editorial packs. Sources and dates are claims; reviewers must confirm originals, editions, countries, item licences, third-party rights and provider metadata-use terms. No whole movie, recording, play text or paywall bypass exists.

Same-origin JSON POSTs, closed fields, server-owned profiles, bounded requests and SQLite placeholders protect the local API. Review events are timestamped but **not authenticated/signed decisions**; do not treat the public preview as a multi-user production approval system. API responses and exports are plaintext-safe metadata; no legacy environment, device, Hanuman/runtime or `.git` files are read/served. Queue DB, operator `.env` and result exports stay out of Git.

## Validation on 3 October 2026

35 offline discovery tests, 8 new HTTP integration tests (within 56 experience tests), 29 DR tests, retained handover/Pairings/Node suites: **145 automated checks PASS** overall. All four real Chromium suites pass, including the Research Desk actual queue/terminal-source outcome, metadata accept/filter/reset, export, mobile layout and integrated report navigation. Mocked source/model success tests are not real-provider/model connection tests. All YAML files parse; optional containers and production scheduling were not run.
