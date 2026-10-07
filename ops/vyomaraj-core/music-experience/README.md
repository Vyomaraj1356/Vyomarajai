# Memory & Melody — music, radio, audio and video

## Audit first: no duplicate music agents

The pinned registry already names **Music** under ENTERTAINMENT and reserves **ENT-MUS-S1–S6**. Individual names/duties are not supplied. This extension proposes functional bindings to those existing slots; it does not allocate six new agents or alter the canonical 13 categories / 133 sub-agents / 421 product counts.

This audit covers the current tracked checkout and reviewed registry, not every historical archive, private conversation or external repository. No dedicated music/audio/video experience files were found before this addition.

## What is implemented

- A 63-card starter catalogue: seven radio references, fourteen artist/recording entries,
  seventeen folk/regional/tradition routes, eight chart formats/references, five audio
  programmes and twelve video/show formats.
- A Sufi, ghazal and studio-show FORMAT layer (24 cards, added 6 October 2026): six Sufi cards
  (qawwali, kafi, Amir Khusrau, mehfil/sama, sufi rock, Baul), six ghazal cards (form,
  gharanas and the thumri tie, the poets, Begum Akhtar, Mehdi Hassan, the form today), eight
  studio/show formats (Coke Studio Pakistan and its franchise editions, the 2011 Indian
  edition, the 2022 Bangla edition, MTV Unplugged, The Dewarists, Tiny Desk Concerts, and one
  card stating the rights rule) and four ORIGINAL programme formats that are ours: Mehfil
  Sessions, the nine-night Sufi Cycle, the Ghazal Cycle and the Navaratri 2026 launch cycle.
  Inherited cards are context, credits and programme structure only and each says so in its own
  words; no episode, recording, lyric, artwork or brand asset is imported, copied or rehosted,
  and every card carries a source link with its check date. The four original programmes carry
  `owned_original_not_yet_recorded`, claim no performer or writer credit yet, and state their
  own rights basis.
- Search plus collection, era and region filters. Modern examples are not automatically the latest releases.
- Ordered selection of up to eight entries, with move/remove controls.
- Same-origin `/api/plan` music dispatch, deterministic role assignment and 15/30/60-minute radio/audio/video programme budgets.
- Source-linked JSON handoffs with catalogue credits, edition context, rights gates and explicit non-live/provider flags.
- A real browser-local audio/video preview for user-authorized files, without upload or autoplay. Supported codecs depend on the browser; maximum file size is 100 MB.
- A five-entry **2025 annual IFPI snapshot**, published in February 2026, clearly distinguished from live weekly rankings.
- Source links for catalogue and chart providers, not unlicensed streams, copied video, artwork or lyrics.

Binaca Geetmala is the provisional interpretation of “Bianaca”. Prasar Bharati radio references include Bhoole Bisre Geet, Chhayageet, Sangeet Sarita, Jaimala and Hawamahal. The latter is a spoken-audio reference, not a song chart. The interface uses an original CSS radio illustration; no presenter voice is synthesized or impersonated.

## Proposed bindings

| Existing slot | Proposed function |
|---|---|
| ENT-MUS-S1 | Radio memory and archives |
| ENT-MUS-S2 | Artists, albums and recordings |
| ENT-MUS-S3 | Folk, regional and world discovery |
| ENT-MUS-S4 | Charts and dated top lists |
| ENT-MUS-S5 | Audio programming and playlists |
| ENT-MUS-S6 | Music video and visual programmes |

Canonical names remain **UNKNOWN**. These are new functional proposals, not recovered historical names/chapters. Local routing works, but autonomous model-backed agents, provider connections and publishing are not implemented.

## Run / test

```sh
python ops/vyomaraj-core/experience/studio_server.py --port 4176 --home music
# Open http://127.0.0.1:4176/music/ on the same machine; reports are at /reports/music.
```

The studio is loopback-only by default and rejects non-loopback bind addresses. Research/approval writers additionally require action-bound owner tokens; do not proxy the local control routes to public ingress.

```sh
python -m unittest discover -s ops/vyomaraj-core/experience -p 'test_*.py' -v
node --check ops/vyomaraj-core/music-experience/app.js
# Optional, with Playwright/Chromium installed and the preview running:
node ops/vyomaraj-core/experience/test_music_browser.cjs
```

Browser smoke tests accept `VYOMARAJ_PREVIEW_URL` and `TEST_CHROMIUM_EXECUTABLE`; `NODE_PATH` can reference an external Playwright installation. Test binaries/caches must not be committed.

Example local API payload:

```json
{"experience":"music","item_ids":["binaca","marathi","tumhiho","ifpi2025"],"mode":"radio","duration_minutes":30}
```

Only catalogue IDs, mode and planning budget go to the server. Selected local media files and file names are never included. There is no upload endpoint. Plans are not actual recordings, playlists on a third-party account, or broadcast-ready timing logs.

## Scope / release gates

`content.json` records source citations, review basis and backlog. This is not every album, singer, folk tradition or chart. Live charts need permitted access, dated snapshots and explicit stale/error states. Discographies need edition and track-credit reconciliation. Historical and folk recordings are not automatically public domain. Review recording/composition/video/sync/broadcast/artwork/lyrics rights, performer consent, clean/explicit editions, captions and translations before publication. Devotional music expansion should cross-reference existing BHAKTI content, not invent duplicate agents.

No secrets, runtime/device configuration, legacy controllers, external models, production deployment or DR operations are used by this extension.

## Validation for this update

77 automated tests and both real Chromium smoke suites passed. Music checks cover desktop/mobile discovery, queue/rundown/download behavior, actual local audio/video playback, no autoplay or media upload, permission revocation and report rendering. Canonical registry/catalog hashes remain unchanged. This is a preview deployment only, not a production or DR release.
