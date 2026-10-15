# Vyomaraj Trend Intelligence and Original Media Factory
Version: 1.0
Status: Proposed implementation specification; not evidence of live integrations

## Mission
Vyomaraj and Jarvis/Laxman continuously discover public market signals, assess emerging trends, develop original multi-format media, verify rights and factual claims, publish through approved official connectors, and learn from measured audience and revenue outcomes. The aim is unusually fast, consistent, high-quality execution—not a guarantee of virality or market domination.

## Operating responsibilities
- **Vyomaraj:** orchestrates the pipeline, ranks opportunities, assigns specialist agents, routes tasks to suitable AI/media providers, enforces policies, and maintains the durable task ledger.
- **Jarvis/Laxman:** runs scheduled discovery jobs, queues, health checks, retries, monitoring, failure alerts, and recovery runbooks.
- **Kuber:** applies per-experiment budgets, tracks provider and production costs, reconciles channel revenue, calculates contribution margin, and recommends scale/pause decisions.
- **Owner/root:** controls credentials, spending caps, account access, publishing permissions, legal commitments, and high-impact production actions. Owner can pause all outbound publishing.

## Market signal intake
Collect only signals permitted by source terms and configured access:
- official platform trend/search/analytics APIs and creator analytics available to the account;
- public search trend data and news feeds with provenance;
- audience comments, watch-time/retention, click-through, saves/shares, search queries, subscriber changes and conversions from authorized analytics;
- partner briefs, customer questions, seasonal/cultural calendars, product/commerce signals and competitor public metadata where terms allow.
Do not bypass authentication, scrape prohibited pages, evade rate limits, or collect private/personal data without a valid basis and permission. Record source, collection time, region, language, query/topic, metric definition, API/version, usage restrictions, and freshness.

## Trend scoring
Score each candidate using an explicit, explainable rubric:
1. Momentum: rate of change over a comparable time window, not raw views alone.
2. Audience fit: match to target region, language, age suitability and existing audience.
3. Original value: ability to contribute verified insight, storytelling, utility, commentary or distinctive production.
4. Shelf life: short-lived spike versus evergreen interest.
5. Competition/saturation: whether the topic is already over-supplied.
6. Monetization fit: relevant offer, eligible channel and realistic conversion path.
7. Cost/time: research, media generation, human review, localization and distribution effort.
8. Risk: misinformation, health/finance/legal sensitivity, tragedy exploitation, harassment, minors, privacy, copyright and brand safety.
9. Confidence: signal quality, sample size, source diversity and freshness.
The system must keep score components and source evidence; no unexplained “viral prediction” claims. High-risk or weak-evidence topics are held for review or rejected.

## Original media production pipeline
DISCOVER → DEDUPLICATE → SCORE → BRIEF → SOURCE RESEARCH → SCRIPT/OUTLINE → FACT-CHECK → RIGHTS/SAFETY REVIEW → GENERATE/EDIT → QA → LOCALIZE → OWNER/POLICY APPROVAL → SCHEDULE/PUBLISH → MEASURE → LEARN.

For each approved topic, create a campaign package:
- long-form video or documentary where justified;
- short-form vertical reels/shorts with platform-specific pacing;
- audio-only narration/podcast version;
- captioned clips and quote cards;
- thumbnail/title/description variants;
- subtitles, transcripts, source notes and accessibility captions;
- localized versions only where translation and cultural review are sound;
- companion article, newsletter, guide, or digital product where useful.
Not every topic should become every format. Each output needs a distinct purpose, suitable edit, native aspect ratio, caption treatment, rights record, and platform requirements.

## AI and media provider fabric
Use a provider-neutral adapter interface for language models, research/search, transcription, speech, image, video, music/audio, editing/rendering, translation, analytics and publishing. Provider names such as ChatGPT/OpenAI, Arena AI, Claude, Gemini, local/open models and media tools are candidates until each exact product/API, access scope, terms, price and connection are verified.
- Route each job based on quality evaluation, modality, latency, availability, licensing, privacy and total cost.
- Keep provider-specific prompts and parameters versioned behind common task contracts.
- Support graceful fallback only when the alternate provider is approved and tested.
- Store durable source assets, project files, prompts, model/version metadata, edit decisions, approvals, outputs and checksums in controlled storage.
- Do not imply that ChatGPT, Arena AI or any external platform is connected merely because it appears in the architecture. An integration is active only after credentials are configured securely and a real test passes.
- Use only assets with clear ownership/licensing or a documented legal basis. Never clone voices, likenesses, or identities without authorization. Clearly disclose synthetic or materially altered content when required by platform policy or law.

## Quality gates
Before release, check:
- factual claims against cited sources and current dates;
- originality and substantive editorial contribution;
- rights for footage, music, images, fonts, clips, voice, likeness and translations;
- platform-specific disclosure, synthetic media, monetization, community and advertising rules;
- sound levels, loudness, visual quality, spelling, subtitles, safe areas, aspect ratio, duration and encoding;
- child safety, medical/financial/legal claims, cultural sensitivity and privacy;
- metadata and thumbnail truthfulness; no misleading title/thumbnail or artificial engagement;
- duplicate/cross-post policy and music rights for each target platform.
Sensitive topics require appropriate human review. Do not automatically publish urgent health, finance, legal, crisis, election, tragedy or allegations content based only on a trend score.

## Publishing and experimentation
- Begin in draft/sandbox mode. Enable scheduled publishing only after connector scopes and account ownership are verified and owner approves channel policy.
- Use official APIs or approved platform integrations; honor quotas, rate limits, content policies, disclosure and monetization eligibility.
- Maintain per-channel queues, idempotency keys, publication receipts, retry limits, cancellation and takedown workflows.
- Test one or two content niches and one or two channels first. Run controlled experiments with a clear hypothesis and pre-defined success metric.
- Never buy views, followers or engagement; never coordinate spam, misleading mass posting, or unauthorized reposting.
- Keep a human-approval switch and emergency stop for all outbound publishing.

## Measurement and learning
Track per topic, format, language, region, provider, campaign and channel:
- production cost and elapsed time;
- views/reach with source-specific definitions, click-through, retention/watch time, completion, saves, shares, meaningful comments and returning audience;
- qualified leads, conversions, affiliate attribution, memberships/sales, refunds and net revenue;
- rights/safety incidents, corrections, takedowns and review time.
Use cohort comparisons and controlled experiments. Do not optimize only for views: rank campaigns by audience value, trust, conversion, retention and contribution margin. Feed lessons back into trend scores and production briefs while retaining version history.

## Resilience and security
- Queue tasks durably; use idempotent writes, bounded retries, backoff, dead-letter queues, circuit breakers and provider quotas.
- Store secrets in an approved secrets manager; never in repository files, prompts, logs or generated media.
- Restrict connectors to minimum required scopes and isolate publishing tokens by channel/environment.
- Audit who/what approved and published each asset; keep source references and output checksums.
- Back up source projects, content metadata and publication receipts; test restoration. Provider redundancy does not replace storage/DR testing.
- Alert on unusual costs, sudden engagement anomalies, publishing failures, API policy changes and suspected credential compromise.

## Pilot launch and acceptance criteria
Pilot only after the owner chooses a niche, audience, language, budget ceiling and authorized channels.
- [ ] Trend signals have provenance, timestamps, freshness and terms-compliant collection.
- [ ] Trend scoring is explainable and rejects or escalates high-risk candidates.
- [ ] One original campaign is produced in at least two useful formats from a shared verified research package.
- [ ] Rights, factual, quality and platform policy checks are recorded.
- [ ] All external integrations have verified official docs, secure credentials, least-privilege scopes and a successful test.
- [ ] Publishing requires the configured owner/policy approval; stop switch is tested.
- [ ] Analytics and costs are attributable to each asset and campaign.
- [ ] One end-to-end failure drill covers provider outage, duplicate retry, revoked token and rollback/takedown.
- [ ] Scale decisions use observed retention, conversion, cost and margin—not a promise of virality.

## Important status statement
This is an implementation blueprint. It does not assert that trend feeds, Arena AI, ChatGPT, media generation tools, publishing accounts, or analytics connectors are installed or active. Each connection must be configured and verified separately.


## Implementation status update — 2026-10-15

The companion contract is `docs/strategy/VYOMARAJ_TREND_INTELLIGENCE_RUNTIME_CONTRACT_v1.1.md`.
A safe, offline-first intake/scoring utility now exists at
`ops/vyomaraj-core/trends/trend_intake.py`, with unit tests at
`ops/vyomaraj-core/trends/test_trend_intake.py`; the offline suite runner includes that test directory.
This is a first executable foundation, not a live trend connector: it consumes JSONL from an authorized
adapter, defaults to dry-run, appends only when explicitly passed `--write`, and never calls external
services or publishes. Provider adapters, scheduler, durable production queue, alerting, scheduled prompt discovery/vault ingestion, analytics ingestion, publishing and DR acceptance remain separate integration gates until
authenticated end-to-end evidence exists.
