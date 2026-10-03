# Roots & Pairings — Liquor and Bar expansion

**Added 3 October 2026 · editorial proposal + interactive browser prototype.**

Requested experience: **Liquor → local tadi / regional and global traditions → Bar chakhna and snack pairings → illustrative 3D/4D/5D views.** This is content and a local preview, not a live alcohol, AI-generation, event-booking or publishing service.

## Agent mapping

- Liquor: `ENT-LIQUOR-S1`, under ENTERTAINMENT.
- Bar: `ENT-BAR-S1`, under ENTERTAINMENT.
- The experience links Bar beneath the Liquor journey. The canonical registry still treats the agents as **siblings**; it has not been silently reparented.
- `content.json` proposes **12 Liquor chapters and 10 Bar chapters**, matching the reported chapter counts without pretending to recover the missing original titles.
- The 13 / 133 / 421 totals are unchanged. The historical 32-file catalog remains unchanged. This new content pack is registered separately in `../experience/CONTENT_EXTENSIONS.json`.

## Liquor coverage

| Area | Content added | Evidence status |
|---|---|---|
| Local tadi / toddy | Maharashtra and neighbouring traditions; local names, palm source, community stories, traceability | Research candidate; no local origin date, ABV, licence or specific producer invented |
| Kerala kallu | Coconut-palm sap, changing character with fermentation, Kumarakom food and toddy-shop culture | Kerala Tourism overview [1](https://www.keralatourism.org/kumarakom/toddy-shops-kumarakom.php) |
| Goa feni / urak | Regional heritage, cashew/coconut traditions, festival food and craft | Historical Spirit of Goa listing [1](https://utsav.gov.in/view-event/spirit-of-goa-festival) |
| Apong | Rice-beverage tradition and community context in Arunachal Pradesh | Incredible India [1](https://www.incredibleindia.gov.in/en/arunachal-pradesh/itanagar/a-culinary-journey-through-itanagar-and-arunachal-pradesh) |
| Chhang | Ladakhi barley-based beverage and celebration context | Incredible India [2](https://www.incredibleindia.gov.in/en/ladakh/kargil/kargil-travel-and-food-guide) |
| Sake-making | Grain/water, koji knowledge, craft transmission and social occasions | UNESCO [1](https://ich.unesco.org/en/decisions/19.COM/7.B.44) |
| Agave / Tequila | Landscape, cultivation, production history and cultural heritage | UNESCO [1](https://whc.unesco.org/en/decisions/1015/) |
| Bavaria | Oktoberfest cultural history, originating in the 1810 royal-wedding celebrations | Official organiser history [1](https://www.oktoberfest.de/en/magazine/tradition/the-history-of-oktoberfest) |

Additional **research topics**, not established product records: mahua, Sri Lankan/South-East Asian palm traditions, African palm wines, Korean makgeolli, Andean chicha, Mexican pulque, regional cider/perry and whisky traditions. Each needs local/community sources, accurate naming, legal review and appropriate cultural consent.

### History, specifications, style, process and procedure

Every tradition card has region, ingredient base, style, history/context, conceptual process stages, source references and review status. The content schema reserves fields for language/community, exact ingredient specification, fermented-versus-distilled type, ABV, provenance, licensed producer, batch/label, storage, service, allergens and local law.

**Unknown specifications stay unknown.** Fresh sap, a fermented drink and a distilled spirit must not be equated merely because a local word is shared. The production section is an educational overview, not a home-distillation recipe, equipment guide or claim that homemade alcohol is safe.

The Bar side has actual short food-preparation sequences. They remain recipe concepts: quantities, measured nutrition, catering validation and individual dietary suitability need further work before commercial or medical use.

## Bar: eight chakhna / snack concepts

These are original, region-inspired editorial recipes—not a verified universal “best” ranking or claims of traditional authenticity.

| Snack | Dietary category | Listed recipe allergens | Design intention |
|---|---|---|---|
| Lemon & cumin chana | Plant-based | None listed* | Pulses with cucumber/tomato and citrus |
| Roasted peanut koshimbir | Plant-based | Peanut | Small nut portion with fresh vegetables |
| Cooked moong chaat | Plant-based | None listed* | Thoroughly cooked beans rather than raw sprouts |
| Chickpea sundal bowl | Plant-based | None listed* | Modest oil/coconut and aromatic curry leaves |
| Pepper & lime tofu bites | Plant-based | Soy | Baked/pan-cooked option with peppers |
| Herbed paneer & peppers | Vegetarian | Milk | Portion-aware dairy plus vegetables |
| Banana-leaf fish plate | Pescatarian | Fish | Cooked fish and vegetables, not a deep-fried default |
| Roasted vegetable crunch | Plant-based | None listed* | Vegetable-forward snack; combine with suitable protein if desired |

*“None listed” is **not allergen-free certification**. Check the exact ingredients, every individual's allergies, local allergen guidance and kitchen cross-contact. No calories/protein values or medical dietary prescriptions were fabricated. Every recipe includes ingredients, a four-step procedure, flavour/texture notes and a non-alcoholic pairing.

Food cannot make drinking safe. WHO describes health risks from alcohol and states that there is no risk-free level of alcohol consumption. This experience does not call alcohol healthy, sell it as a treatment, or claim that chakhna prevents intoxication/hangovers. [1](https://www.who.int/europe/news/item/04-01-2023-no-level-of-alcohol-consumption-is-safe-for-our-health)

## Events, without fake freshness

- **Spirit of Goa:** the cited listing is for **17–19 May 2024**. Marked historical; no later edition inferred. [1](https://utsav.gov.in/view-event/spirit-of-goa-festival)
- **Oktoberfest:** the organiser FAQ publishes **19 September–4 October 2026**. Stored as a date snapshot checked 3 October 2026, not a live availability feed. Recheck organiser changes before travel. [2](https://www.oktoberfest.de/en/information/service-for-visitors/faqs-for-wiesn-visitors)
- **Local tadi / harvest / community events:** research placeholder with **no dates or venues invented**. Add only organiser-confirmed/community-authorised records.

## What the views actually do

- **3D-style:** an original CSS-perspective stylised food plate with a rotation slider. It is not a photorealistic render, AI-generated image or full 3D mesh.
- **4D:** a user-stepped preparation sequence, with previous/next controls, captions and no autoplay. “4D” is a project convention for adding time.
- **5D:** diet, listed-allergen and spice-preference controls plus contextual pairing notes. “5D” is a project convention, not five physical dimensions or connected sensory hardware.
- **AI:** a provider-neutral art brief is stored as a proposal. Provider remains null, execution disabled. No API key, external model invocation, synthetic voice, publishing or purchase action is present.

Food content is available by default. Alcohol-related atlas and event cards require an explicit local-legal-age acknowledgement in this prototype. That checkbox is **not legal age verification or production compliance enforcement**. No claims of licensing, medical safety, guaranteed popularity or legal approval are made.

## Preview and tests

```sh
python ops/vyomaraj-core/liquor-bar/server.py --port 4175
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s ops/vyomaraj-core/liquor-bar -p 'test_*.py' -v
node --check ops/vyomaraj-core/liquor-bar/app.js
```

The server binds to `0.0.0.0`. Only index.html, app.js, styles.css and content.json are available. It cannot serve `.git`, environment files, device configuration, archives or arbitrary repository paths. Browser requests remain same-origin; outbound links are source references opened explicitly by the reader. No analytics, credentials or persistent preference storage are used.

## Release gates

Community/local research and consent → factual and legal review → recipe/food-safety and allergy review → real renderer/provider selection if wanted → licensed imagery/rights checks → production access controls and human approval. No dependence on unavailable DR or automatic publication is introduced.
