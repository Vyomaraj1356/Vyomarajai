# Bhakti-Shakti — Sacred Stories & Living Traditions

A researched editorial extension and **local browser/planning prototype**, dated 3 October 2026. It is not a complete sacred-text corpus, production deployment, connected AI renderer or DR synchronization.

## Content and mapping

- **Shiv–Shakti / Shiva:** 12 proposed reading chapters: relationship/meaning, Ardhanarishvara, early worship/texts, Sati–Daksha, Parvati, family stories, Neelakantha, Ganga, crescent/symbols, Nataraja, forms/lingam narratives, and living temple traditions. These are an editorial reading order, not a historical biography or recovered original chapter titles.
- **Narayan/Vishnu:** a ten-entry Dashavatara overview. List variations are explicit; the historical `Buddha_Balarama` record is preserved rather than overwritten.
- **Shakti Peethas:** nine source-attributed starter profiles, with separate tradition labels. This is **not all 51/52/108 sites**. Body-part associations, Bhairava assignments, live timings and coordinates remain unset unless independently reviewed.
- **Mahadev television:** the likely intended title is *Devon Ke Dev… Mahadev*. Its separate screen-adaptation lane contains original commentary prompts and a catalogue reference only—no copied episode footage, dialogue, actor images, music or voice cloning.
- **Prasad-style food:** three editorial food concepts with ingredients, four-step preparation sequences, dietary controls and ingredient/allergy cautions. No universal ritual/fasting prescription is claimed.

Canonical route: `BHAKTI`. Its two registry sub-agent names/slot assignments are still not supplied; the new topics are **not invented agents**. Cross-category references to ENTERTAINMENT and FOOD are editorial context only. The 13/133/421 totals and historical 32-file catalog remain unchanged. `../experience/CONTENT_EXTENSIONS.json` registers this new pack separately.

## What works locally

1. Theme filter for the Shiva reading trail.
2. Region filter for the Peetha atlas; source and tradition distinctions remain visible.
3. Topic selection for a local handoff.
4. Rotatable CSS-perspective food illustration, not a photorealistic or mesh render.
5. User-stepped preparation sequence (project label “4D”).
6. Topic/region/diet/listed-allergen personalization (project label “5D”).
7. `POST /api/plan`: deterministic Vyomaraj topic routing and Jarvis source/review handoff, with downloadable JSON.
8. Shared navigation to the existing Liquor/Bar experience and updated reports.

These labels do not imply physical sensory output, AR, translations, model reasoning, device control, temple booking or automatic publishing. Local role functions read only the chosen reviewed content pack. Legacy device/environment files are never loaded.

## Research discipline

Sources are recorded per item in `content.json`, including original search citation links and date checked. The full source index and current scope appear in `../handover/BHAKTI_FEATURE_UPDATE_2026_10_03.md`.

- Preserve religious traditions respectfully without declaring one sect's interpretation universally binding.
- Distinguish devotional origin stories from dated construction history and archaeology.
- Preserve 51-site, 52-site and Maharashtra regional classifications instead of silently merging them.
- Do not infer miracles, health benefits, guaranteed blessings or live temple information from tourism descriptions.
- Complete-list work requires selecting a named textual/traditional list, reconciling aliases and disputed sites, and checking each record.
- Rights/community/temple review is required before public release. No copied copyrighted artwork or actor likeness is included; hero imagery is an original CSS schematic, not a depiction of a verified shrine.

## Run the integrated preview

```sh
python ops/vyomaraj-core/experience/studio_server.py --port 4176
```

The studio binds to `127.0.0.1` only and uses same-origin URLs; open `http://127.0.0.1:4176/bhakti/` on the same machine. It is not exposed through public ingress.

- `/bhakti/` — new experience.
- `/pairings/` — existing Liquor/Bar prototype with optional local handoff.
- `/reports/bhakti` — feature update.
- `/reports/` — full inventory.
- `/api/status` — explicit local capability flags.
- `/api/plan` — bounded, validated POST; no external effects.

Only allowlisted reviewed files are served. No repository-root file serving, `.env`, `.git`, device records or archive download paths are available through this server. The browser and planner do not call an external AI provider.

## Verify

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s ops/vyomaraj-core/experience -p 'test_*.py' -v
node --check ops/vyomaraj-core/bhakti-experience/app.js
python ops/vyomaraj-core/handover/rebuild_handover.py --check
```

Optional real-browser smoke (with Playwright and Chromium installed and the preview running):

```sh
node ops/vyomaraj-core/experience/test_browser.cjs
```

Use `NODE_PATH` for an external Playwright installation if needed. Optional `TEST_CHROMIUM_EXECUTABLE` and `VYOMARAJ_PREVIEW_URL` override the installed browser and test target. Do not commit browser binaries or npm caches. The desktop/mobile smoke and all 62 automated tests passed for this update.

Production hosting, real AI tool adapters, rigorous age/access controls for the separate alcohol pack, source/rights approval and DR access remain independent release gates. A working preview is not proof of any of those.
