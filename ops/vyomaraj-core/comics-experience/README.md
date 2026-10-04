# Chitra Katha — Vyomaraj comics lane

Trilingual comics planning lane (Hindi / English / Hinglish) with preserved past versions and
plannable future versions. Local viewer `/comics/`; deterministic planner
`../experience/comics_planner.py`; tests `../experience/test_comics.py`.

- Binds the **existing** `ENT-CARTOON-S1–S3` slots (canonical names remain UNKNOWN; no
  duplicate agents; registry totals unchanged).
- Every title and every edition carries **all three languages** — in past and future versions
  alike. Past editions are preserved in history (read-only); future editions extend the line.
- Heritage publishers (Amar Chitra Katha, Tinkle, Chacha Chaudhary, Raj Comics, Indrajal,
  Chandamama) are context references only — no characters, artwork or stories are copied.
- Every plan ends at the owner gate (`PENDING_OWNER_PERMISSION`) and is routed to the central
  nostalgic camera approval queue (`../approvals/`).
- Nothing renders artwork, hosts media, calls a provider or publishes automatically.
