# Vyomaraj + Jarvis — Technology, AI-Agent & Revenue Flow

**Status:** strategy and architecture proposal, based on the repository inspected on 7 October 2026. This is not a claim that the AI agents, integrations, payment system, or revenue are live. The solid/current section describes repository artifacts and configured hosting; dashed paths are proposed or unverified.

## Single-view flow chart

```mermaid
flowchart TB
  subgraph NOW["A · WHAT EXISTS IN THE REPOSITORY / CURRENT DELIVERY BOUNDARY"]
    GIT["GitHub repository<br/>source, static assets, configuration and tests"]
    PAGES["GitHub Pages<br/>configured source main:/<br/>Arena working branch is not deployed"]
    WEB["Static web/PWA shell<br/>HTML · CSS · JavaScript<br/>manifest · service worker · offline page"]
    LOCAL["Python local prototypes<br/>deterministic planners · preview/studio/report tools<br/>not a production API"]
    HARNESS["Optional local LLM harness<br/>provider unconfigured · explicit CLI only<br/>no tools · no automatic calls"]
    CI["GitHub Actions / local checks<br/>software and tracked-tree checks<br/>not application runtime or failover"]
    DATA["Current data boundary<br/>repo files + public static assets<br/>no confirmed production DB, vector store, queue or memory service"]
    GIT -.->|"configured Pages source"| PAGES
    PAGES --> WEB
    GIT --> CI
    LOCAL --> DATA
    HARNESS -.->|"only when explicitly configured and run"| LOCAL
  end

  subgraph CONTRACT["B · SHARED KNOWLEDGE + AGENT CONTRACT — PRESENT AS METADATA, NOT A LIVE FABRIC"]
    POLICY["Universal Knowledge Evolution policy<br/>9 ordered time layers · 8 evidence classes<br/>provenance required · forecasts/scenarios are never facts"]
    REG["Current registry/index references<br/>13 main-agent categories · 128 sub-agent slots (42 named)<br/>197 content references · metadata is not live processes"]
    POLICY --> REG
  end

  subgraph TARGET["C · INTENDED SHRIYANTRA / AI-AGENT STACK — RUNTIME NOT DEPLOYED"]
    OWNER["Owner is the authority<br/>step-up for publishing, spending, deployment and other high-risk actions"]
    SHRI["ShriYantra Harness<br/>identity · least privilege · policy · budget · approval · audit"]
    RAG["RAG<br/>approved sources · access filters · citations/provenance"]
    CAG["CAG<br/>bounded task context: policy + brief + evidence"]
    MAG["MAG<br/>scoped, validated and deletable memory"]
    ROUTER["LLM/provider router<br/>provider-neutral adapters; provider must be chosen and connected"]
    MESH["Agent registry roles<br/>research · fact-check · creative · engineering · business · social · finance · SRE"]
    VYO["Vyomaraj / Bharath<br/>orchestration and product head — intended role"]
    JAR["Jarvis / Laxman<br/>peer review and operations head — intended role"]
    HERMES["Hermes<br/>integrity witness / checkpoints — production service unverified"]
    ARENA["Arena task adapter / workers<br/>planned delegated execution; not a verified production runtime"]
    STORES["Target platform, to be selected<br/>API · SQL metadata · object store · vector/search · queue · secrets · observability"]
    OWNER --> SHRI --> RAG --> CAG --> MAG --> ROUTER --> MESH
    MESH --> VYO
    MESH --> JAR
    VYO -.->|"authenticated peer / heartbeat not configured"| JAR
    MESH -.-> ARENA
    HERMES -.->|"integrity checks when implemented"| MESH
    STORES -.-> RAG
    STORES -.-> MAG
  end

  POLICY -.->|"shared reference; production loading/enforcement still required"| SHRI

  subgraph SELL["D · RECOMMENDED FIRST BUSINESS FLOW — MANUAL, OWNER-SUPERVISED VALIDATION"]
    NICHE["Test one niche first<br/>Pune independent cafés / small hospitality venues<br/>hypothesis, not validated market research"]
    LEAD["Owner-led outreach<br/>10 buyer conversations"]
    BRIEF["Agree a brief, audience, scope,<br/>delivery date and rights"]
    PILOT["Sell a paid pilot<br/>invoice/payment handled outside this app"]
    RESEARCH["Research & claim checks<br/>sources and uncertainty labelled"]
    DRAFT["Content pack<br/>4 original short-video concepts/scripts<br/>hooks · captions · shot list · 7-day calendar"]
    RIGHTS["Rights, privacy and cultural review<br/>original or licensed assets only"]
    GATE["Human review<br/>owner approves; client approves their materials"]
    DELIVER["Deliver the pack<br/>filming, editing and posting excluded initially"]
    RENEW["Ask for feedback and renewal<br/>continue only if customer value and margin are real"]
    NICHE --> LEAD --> BRIEF --> PILOT --> RESEARCH --> DRAFT --> RIGHTS --> GATE --> DELIVER --> RENEW
  end

  subgraph LATER["E · REVENUE LATER — ONLY AFTER PROOF, ELIGIBILITY AND OWNER APPROVAL"]
    SERVICE["Near-term cash path<br/>paid content-planning service → recurring retainer"]
    PRODUCTS["Later product path<br/>templates, workshops or a focused paid knowledge pack<br/>only after repeat demand"]
    CHANNEL["Client/owner social channel<br/>manual publishing after explicit approval<br/>platform connectors are not connected"]
    METRICS["Permissioned platform analytics<br/>use real dashboard exports; views alone are not revenue"]
    PLATFORM["Possible audience revenue<br/>ads · sponsorships · disclosed affiliate links · membership<br/>only when accounts are eligible and terms are met"]
    LEDGER["Revenue ledger<br/>record settled payments, fees, refunds and costs<br/>no forecast counted as cash"]
    SERVICE --> LEDGER
    PRODUCTS -.-> LEDGER
    CHANNEL --> METRICS --> PLATFORM --> LEDGER
  end

  LOCAL -.->|"can support planning/rehearsal; human performs the service today"| DRAFT
  HARNESS -.->|"not a live autonomous agent"| DRAFT
  VYO -.-> RESEARCH
  JAR -.->|"independent review role; not currently connected"| RIGHTS
  GATE --> CHANNEL
  DELIVER --> SERVICE
  RENEW -.->|"only after customer value is demonstrated"| PRODUCTS

  classDef current fill:#dcfce7,stroke:#15803d,color:#10251a,stroke-width:2px;
  classDef prototype fill:#dbeafe,stroke:#2563eb,color:#10223d,stroke-width:2px;
  classDef contract fill:#fef3c7,stroke:#d97706,color:#3c2b08,stroke-width:2px;
  classDef future fill:#f1f5f9,stroke:#64748b,color:#1e293b,stroke-width:2px,stroke-dasharray:5 5;
  classDef revenue fill:#ecfccb,stroke:#4d7c0f,color:#1e2b08,stroke-width:2px;
  classDef caution fill:#fee2e2,stroke:#b91c1c,color:#3f1111,stroke-width:2px;
  class GIT,PAGES,WEB,CI current;
  class LOCAL,HARNESS prototype;
  class POLICY,REG contract;
  class OWNER,SHRI,RAG,CAG,MAG,ROUTER,MESH,VYO,JAR,HERMES,ARENA,STORES future;
  class NICHE,LEAD,BRIEF,PILOT,RESEARCH,DRAFT,RIGHTS,GATE,DELIVER,RENEW,SERVICE,PRODUCTS,CHANNEL,METRICS,PLATFORM,LEDGER revenue;
  class DATA caution;
```

**Reading the chart:** The revenue workflow is an operating recommendation, not an automated feature. Today the viable path is the owner using existing local planning/research tools and delivering work manually. Do not represent the registry, local LLM harness, RAG/CAG/MAG configuration, peer link, or publishing/payment adapters as live agents or connected services.

## Technology and agent map

| Layer | Technology / roles in the repository | Honest status |
|---|---|---|
| Web surface | HTML, CSS, JavaScript, Web App Manifest, service worker, offline page; GitHub Pages | Static preview/site artifacts exist. Pages metadata points at `main:/`; this Arena branch is not deployed. It is not the private AI control plane or a customer checkout. |
| Local product prototypes | Python planners, local preview/studio/report tools, browser prototypes | Useful for rehearsals and deterministic planning. Not a hardened public service; no automatic publishing or customer intake/payment flow. |
| Build and assurance | Git, GitHub Actions, Python test suites, browser checks, read-only probes | Can verify source/config and tests. A matching Git tree is not production DR, a running app, or revenue evidence. |
| Optional model call | Provider-neutral OpenAI-compatible HTTP harness with `vyomaraj` and `jarvis` role profiles | Provider is unconfigured; use is explicit/local; no tools or automatic execution. Review a provider's privacy terms before sending customer briefs. |
| Shared policy | ShriYantra policy reference; Universal Knowledge Evolution inheritance; provenance and future-claim guard | Policy/config and offline validation exist. `reference_contract_not_deployed`: no proof of production enforcement. |
| Retrieval and memory | RAG, CAG, MAG, model routing, Harness, Hermes and Arena adapter | Target/configuration contracts only; not a verified deployed runtime, shared memory service, or peer mesh. |
| Native/mobile | PWA assets; a tracked APK artifact | APK signing, source provenance and device installation are unverified. No native Android build source or macOS/Xcode project was found. |
| Commercial integrations | Model vendors, social APIs, analytics, payment, affiliate and sponsor connections | Not connected/verified in this repository. The platform registry is not account authorization. |

### Agent family responsibilities

These are registry roles, not a report of processes currently running. Bharath/Vyomaraj is the intended orchestration head; Laxman/Jarvis is a peer head for review/operations. They do not have a verified authenticated production peer connection.

| Registry family | Example roles in the registry | Use in the proposed earning workflow |
|---|---|---|
| Core | Orchestrator, research, web research, fact-check, architecture, project manager, final review | Convert an approved customer brief into a scoped plan; check claims and deliverables. |
| AI | OpenAI, Claude, Gemini, local model, model router, prompt governance | Optional drafting/routing only after an owner selects and configures a provider; currently no provider is configured. |
| Engineering | Coding, GitHub, debug, DevOps, QA, security | Build and test product plumbing after demand is proven; do not expose internal credentials or auto-deploy. |
| Creative | Content, creative, script, image, audio, video, media | Draft original concepts and scripts now; image/video/audio generation adapters are not configured. |
| Social | YouTube strategy/research/script/SEO, thumbnail, shorts, analytics, monetization, publisher | Prepare channel-specific drafts and analyze permissioned metrics; platform publishing/analytics connections remain unconfigured. |
| Knowledge | Data, memory, knowledge, analytics, RAG, CAG, MAG | Maintain source notes and evidence labels; retrieval and shared memory services are not deployed. |
| Business | Marketing, sales, product, business, automation | Qualify leads, define the offer, follow up and measure renewal; owner-led/manual first. |
| Resilience | Health monitor, SRE, self-healing, DR, failover, backup, restore, conflict resolution | Protect internal service reliability; do not market a configured recovery plan as proven production resilience. |

## Recommended earning strategy

### Start with a service, not ad forecasts

**First offer to test:** a small, clearly scoped short-form content pack for independent cafés or small hospitality businesses in Pune. The repository has FOOD/Tourism planning material, but no customer demand has yet been validated.

A pilot could include **four original content concepts/scripts**, hook, caption/CTA, shot list, one-week calendar, sources/claim notes, a rights checklist and one revision. Exclude filming, video generation, paid media, posting, and promises of reach or sales until those capabilities and permissions actually exist.

The price bands below are **experiments, not researched market rates or earnings promises**: test a one-week pilot around **₹2,500–₹5,000**, then consider a **₹8,000–₹18,000/month** planning retainer only if customers renew and the time/cost math works. Interview potential buyers before fixing prices; change scope or price if they will not pay.

### Revenue ladder

1. **Paid pilot service:** collect for a defined deliverable using an owner-selected, lawful invoicing/payment method outside this application. No payment gateway is connected here.
2. **Recurring service:** turn successful pilots into a monthly planning/review retainer; report actual deliverables, revisions, hours and customer feedback.
3. **Digital products/workshops:** only after repeated requests reveal a specific reusable need; validate with preorders or a small paid cohort.
4. **Audience revenue:** later, and separately: platform ads, memberships, sponsorships or affiliate commissions. Require verified account ownership, eligibility, written terms where needed, clear disclosures and actual settlement reports. Reposting a clip does not automatically multiply revenue.

### Four-day validation sprint: 7–11 October 2026

- **7 Oct:** choose the café/hospitality hypothesis; create three original sample packs, labelled as samples—not client results. Finalize exclusions, rights checklist and owner review.
- **8–9 Oct:** speak with ten potential buyers. Ask what content work they already pay for, the outcome they need, approval workflow and budget. Seek three paid pilot commitments; do not build integrations first.
- **10 Oct:** deliver the first pilot manually. Track time, revisions, client approval and any attributable enquiry/coupon result, with the client's permission.
- **11 Oct:** continue, re-scope or stop based on actual conversion, renewal interest and contribution margin. A target date is not proof of launch, deployment or market fit.

### Measure money honestly

`Net contribution = cash actually collected − refunds − payment/platform fees − direct production/tool/contractor costs − tax reserve.`

Track qualified conversations, paid-pilot conversion, delivery hours, revision count, renewals and customer-attributed outcomes. Keep views, likes and forecasts in a separate engagement report. **Do not use the legacy `₹340 CPM` or “triple revenue on three platforms” calculations as actual or promised income**: they are unsupported assumptions, not verified payouts. Views × an assumed CPM is not a revenue ledger.

## Required guardrails

- Owner approval remains mandatory before public posting, spending, deploying, changing account access or connecting customer data. Agents cannot inherit root-owner authority.
- Use only original or properly licensed media. A “fair use” label by itself does not grant reuse rights. Keep source and licence records.
- For cultural, devotional or educational material, distinguish tradition/belief from sourced historical fact; do not promise cures, blessings, investment gains or guaranteed outcomes. Label forecasts and scenarios as uncertain.
- Collect only the customer information needed to deliver the agreed work; get permission before using customer metrics or examples in a portfolio.
- Never place provider keys, payment credentials, bank data or customer personal data in the repository, prompts, or chat.

## Repository evidence to consult

- `config/agents/shriyantra-agent-registry.json` — shared service and agent-family role metadata.
- `config/intelligence/shriyantra-rag-cag-mag.yaml` and `config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json` — shared knowledge/control contracts and deployment status.
- `ops/jarvis/LLM_HARNESS.md` — provider-unconfigured, explicit no-tools harness.
- `ops/vyomaraj-core/experience/EXPERIENCE_ORCHESTRATOR.json` — plan-only routes, local adapters and owner-review gates.
- `ops/bhakti-shakti/revenue-reel-system.json` — preserved historical concepts; its account, CPM, audience and revenue claims are not verified and must not be repeated as facts.
- `ops/vyomaraj-core/handover/GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md` — current release and integration gaps.
