# Vyomaraj Reel Sprint — one-hour MVP

A focused local-first planner for a **human-reviewed short-video campaign pack**. It turns an owner-entered small-business brief into four editable Reel/Shorts planning templates, a one-week calendar, shot prompts, captions, and claim/rights checks.

## Run locally

From the repository root:

```sh
python3 -m http.server 4178 --bind 0.0.0.0 --directory products/vyomaraj-reel-sprint
```

Open `/` in the local preview. It has no external libraries or network calls. The form is not persisted; clearing or reloading removes the working brief. Use **Load sample** for a clearly marked fictional café demo. Download a `.txt` plan or use the browser's print-to-PDF option. The matching sample output is `fictional-demo-pack.txt`.

## What is real in this MVP

- The browser UI and deterministic template generator work without a model provider.
- Four distinct concept angles are created from the operator's text.
- User-supplied facts/sources are labeled as **not independently verified**.
- Selected absolute, health, certification, and guarantee-style claims receive a review warning.
- Output is built with DOM `textContent`, so entered text is not inserted as HTML.
- Human review, permission checks, manual client delivery and owner approval remain explicit.

## What it is not

No production agent mesh, external LLM, web trend feed, image/video generation, fact-checking API, social OAuth/publishing, analytics connection, account, database, payment gateway, or earnings guarantee is included. The current release is English-template-only. Marathi/Hindi translation and client posting must be handled and reviewed by a person.

## Sellable service hypothesis

Offer Pune independent cafés/small hospitality venues a paid pilot: four original short-video concepts/scripts, captions, shot list, a one-week calendar, and a human-reviewed source/rights checklist. Filming, editing, posting, ad spend and reach/sales promises are excluded.

The suggested pilot/retainer prices in the related architecture strategy document are experiments only—not market research. Validate with buyer interviews and three paid pilots before investing in payment or AI automation. Collect payment only through an owner-selected lawful invoicing/payment method outside this prototype. Get client permission for source material and case-study metrics.

## Local checks

```sh
node --check products/vyomaraj-reel-sprint/app.js
node tests/test_reel_sprint.cjs
```

This MVP is an additive demo; it does not change the main landing page or deploy itself. Any public launch requires owner review and the repository's normal branch/PR process.
