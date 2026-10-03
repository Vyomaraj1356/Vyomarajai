# Frame & Stage — Film, Theatre, Clips and Advertising

A local extension under the **existing** ENTERTAINMENT / `ENT-MOVIE-S1–S6` group. Original slot names remain UNKNOWN. Six proposed functional bindings cover features, shorts, clips/archives, Marathi theatre, Hindi/multilingual theatre and advertising. No additional agents or canonical products are counted.

## Implemented

- 27 source-attributed starter records/formats across full-length film references, short films, Marathi/Hindi stage works, old/new ad case studies, archives and original one-act formats.
- Search plus format/language/era filters and up to eight research references.
- Seven deterministic planning formats: feature, short, clip, long play, one-act, advert and mix. Two original seeds include Marathi/Hindi/English dialogue samples. **These are outlines, not full scripts or rendered films.**
- Existing-slot routing and Vyomaraj/Jarvis source/review handoff through `/api/plan`.
- Browser-only video cut room: up to six files, trim in/out, reorder/remove, sequential hard-cut preview and local edit-decision JSON export.
- No upload, remote URL import, automatic playback, multitrack audio mix, transitions, frame-accurate editing or encoded MP4 export.

Full commercial films/plays/adverts are not bundled. Provider, archive and open-film links remain references; availability and rights vary. The Sintel record includes its CC BY 3.0 attribution/credit requirements and exclusions. Natsamrat edition ambiguity, a disputed Cadbury campaign year and a conflicting theatre cast listing remain explicit rather than guessed.

## Run

```sh
python ops/vyomaraj-core/experience/studio_server.py --port 4176 --home film
```

Routes: `/film/`, `/reports/film`, `/reports/contents`, `/reports/`, plus the existing `/music/`, `/bhakti/` and `/pairings/` experiences.

Local planner example:

```json
{"experience":"film","format":"one-act","language":"Marathi","seed":"shelf","duration_seconds":600,"item_ids":["ekzunj"]}
```

References provide research context only: they are not adapted into the original seed or authorized as footage. All freeform file paths, URLs and upload fields are rejected. Plans explicitly declare no model call, rendering, publication, production deployment or verified DR.

The cut room accepts browser-recognised video files up to 100 MB each / 300 MB combined and finite readable duration. Unsupported files receive a visible error. Files remain in browser memory and are discarded on clearing/unchecking permission/page exit. Exports contain filenames/times, not media. Rights acknowledgement is not automated legal clearance. Local playback is approximate and depends on codec/browser support.

## Verify

```sh
python -m unittest discover -s ops/vyomaraj-core/experience -p 'test_*.py' -v
node --check ops/vyomaraj-core/film-experience/app.js
# Optional with Playwright/Chromium installed and the shared preview running:
node ops/vyomaraj-core/experience/test_film_browser.cjs
```

The browser smoke accepts `VYOMARAJ_PREVIEW_URL` and `TEST_CHROMIUM_EXECUTABLE`; `NODE_PATH` can refer to external Playwright dependencies. Keep browser binaries/test media outside Git.

## Research and release gates

Source references and their review basis are in `content.json`. The companion report distinguishes fully fetched licensing text from search excerpts and partial reads. This is not a complete catalogue, a current theatre booking service or proof that an OTT subscription can play every title. Performance/adaptation/translation, recording/distribution, music, artwork, trademarks, performer consent, captions and advertising claim/disclosure requirements need use-specific review. No universal short-clip exception or blanket public-domain claim is assumed. Local templates are not certified production scripts or legal advice.

Devanagari UI/dialogue uses a locally served Noto Sans Devanagari WOFF2 subset (via Fontsource). Its SIL Open Font License is retained in `experience/assets/DEVANAGARI-LICENSE.txt`; no Google Fonts runtime request is made.

## Validation

93 automated tests and all three real Chromium smoke suites passed for this update. Film checks include actual two-file local sequence playback and edit-decision export, alongside desktop/mobile rendering and Devanagari font loading. Production and DR are unchanged.
