# Vyomaraj Backend Agent, Content & Configuration Inventory
**Audit date:** 2026-10-15  
**Scope:** Read-only inventory of Primary `main`, current registry/configuration documents, and the connected Render workspace. This document records evidence and gaps; it does not certify production readiness.

## Executive status
- Primary repository: `Vyomaraj1356/Vyomarajai`, branch `main`.
- Secondary Git snapshot target recorded by policy: `deepakGoyal1356/Vyomaraj-Agent-6d64e`. This is code-repository snapshot scope only, not application data/runtime DR.
- Render service observed: `vyomaraj-public-preview`, branch `main`, URL https://vyomaraj-public-preview.onrender.com, health path `/healthz`, start command `python3 ops/vyomaraj-core/experience/public_landing_server.py --host 0.0.0.0 --port $PORT`.
- Render build command is currently `python3 --version`; review and replace with a meaningful dependency/build validation step after confirming repository requirements. Public service IP allowlist is `0.0.0.0/0`; expected for a public preview only, not evidence of private control-plane protection.
- No secret values are reproduced. This audit does not change environment variables, deployments, access policy, DR targets, or publishing state.

## Agent and content categories
Historical owner-supplied snapshot `AGENT_CONTENT_REGISTRY_V16_7_24.json` reports **13 categories, 133 sub-agent slots, 421 product counts**. These are source-reported counts, not runtime availability. Current structural registry reflects **128 counted sub-agent entries and 6 uncounted parent headings**; differences are intentional/recorded in its build report and should not be silently overwritten. Active item-level product totals remain unreconciled.

| ID | Category | Historical sub-agents | Historical products | Registry note |
|---|---|---:|---:|---|
| FOOD | Food & Social Connect | 3 | 6 | Individual names incomplete |
| EDU | Education & World Wisdom | 15 | 68 | Partial named roster; includes approved Government Schemes transfer in current structure |
| ASTRO | Astro-Celestial & Universal | 3 | 9 | Individual names incomplete |
| FINANCE | Finance & Wealth | 8 | 15 | Current structural count differs after approved transfer |
| LIFE | Life Coach & Wellness | 10 | 34 | Individual names incomplete |
| BHAKTI | Bhakti Mandir — Ritual, Festival & Grantha | 2 | 8 | Current structure includes view-only Aghor route |
| SPORTS | Sports & Legends | 14 | 29 | Individual names incomplete |
| AGRI | Agriculture & Environment | 6 | 14 | Individual names incomplete |
| ENTERTAINMENT | Comedy, Movies, Hollywood, Bollywood | 38 | 168 | Six parent headings are uncounted in current structural registry |
| PLATFORM | Social Hub, platforms & earning | 20 | 39 | 19 lanes named; one slot remains unmapped |
| TOUR | Tour & Travel | 4 | 9 | Individual names incomplete |
| WAR | War Room — Warriors | 5 | 13 | Five high-level lanes recorded |
| PODCAST | Podcast & Entertainment Studio | 5 | 9 | Research, Script, Produce, Analysis, Publish |

### Named / structural roster highlights
- EDU: Veda Rishi, Upanishad Guru, Gita Acharya, Mythology & Mystery Rishi, Vyomaraj Picker, Lectures Hub, Short Notes, Care & Bikes, Social Thinkers/Visionaries/Legends, Government Schemes; some source group slots remain unresolved.
- BHAKTI: Aghor & Aghori is recorded as an editorial/view-only route, not a deployed autonomous teacher.
- ENTERTAINMENT: INDICOM and Criticism gate are named; six hubs are represented as parent headings rather than counted agents.
- PLATFORM: YouTube, Instagram, Facebook, TikTok, X, LinkedIn, Telegram, WhatsApp, Discord, Pinterest, Threads, Snapchat, Reddit, Twitch, Vimeo, Tumblr, Mastodon, EARN, AI; one of 20 slots remains unmapped.
- WAR: PAST, HISTORY, PRESENT, FUTURE, CROSS-CUTTING.
- PODCAST: RESEARCH, SCRIPT, PRODUCE, ANALYSIS, PUBLISH.
- All registry entries must be treated as `NOT_VERIFIED` for runtime unless there is separate successful live evidence.

## Configuration and control files
| File / area | What it controls | Evidence-based status / next action |
|---|---|---|
| `ops/vyomaraj-core/handover/AGENT_CONTENT_REGISTRY_V16_7_24.json` | Owner-supplied historical categories, partial names, product counts | Source snapshot; preserve; don't invent missing names |
| `ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json` | Current structural agent identities and parent links | Structural inventory only; runtime not proven; reconcile source-count differences deliberately |
| `ops/vyomaraj-core/experience/CONTENT_CATALOG.json` | Metadata-only content packs and routes | Indexed references, not exhaustive 421-product title inventory |
| `ops/vyomaraj-core/experience/EXPERIENCE_ORCHESTRATOR.json` | Planner routes, supported modes and release gates | Planning architecture; safety policy explicitly not a deployed filter |
| `ops/vyomaraj-core/experience/LOCAL_INTEGRATION.json` | Local preview endpoint, role handoff, experience modes, feature flags | `local_preview_planning_only`; automatic AI and publishing disabled; provider null; owner-token issuer not configured in checkout |
| `ops/vyomaraj-core/handover/CONTENT_SAFETY_POLICY_V16_7_24.json` | Proposed safety/review workflow | Policy specification only; not a production moderation pipeline |
| `ops/vyomaraj-core/governance/PUBLIC_POLICY.json` | View-only spiritual content, voluntary participation, monetization constraints | Policy present; not legal-compliance certification; payment/payout not connected |
| `config/ai/PROMPT_REGISTRY_V1.json` | Versioned user-owned task presets for Vyomaraj/Jarvis | Presets present; does not enable provider, tools or external actions |
| `ops/jarvis/llm_harness.py`, `ops/jarvis/LLM_HARNESS.md` | Provider-neutral OpenAI-compatible text completion boundary and role profiles | No-tools harness; live provider/model completion not proven |
| Runtime-only provider settings | `JARVIS_LLM_ENDPOINT`, `JARVIS_LLM_MODEL`, `JARVIS_LLM_API_KEY` (names only) | Configure in approved secret/runtime store; never commit or paste values; run harmless live smoke and budget/privacy tests |
| `ops/dr/DR_POLICY.json` | Primary/secondary Git snapshot policy and guarded writer scope | Primary-main writer, no automatic reverse overwrite or target-only removal; no zero-RPO/RTO or runtime/data DR claim |
| `ops/jarvis/devices.json` | Device-number/configuration metadata | Sensitive operational configuration; values deliberately omitted from this report; review access and minimize exposure |
| GitHub Actions workflows | CI, preview smoke, DR sync, evidence refresh and research scheduling | Workflow presence is not proof each integration is connected; inspect latest run artifacts before claiming success |
| Render service configuration | Public preview build/start/health/network settings | Preview only; build command quality and public exposure should be reviewed before broader release |

## Integrations and capability truth
- **Present / offline-tested:** named prompt presets, deterministic content planner, agent/content structure, provider-neutral harness code.
- **Not proven connected:** OpenAI API, Claude/Anthropic, Gemini, local inference, multi-model fallback, MCP/A2A tool mesh, Meta AI, 3D/4D/5D media-generation tools, authorized trend feeds, publishing APIs, account analytics, CRM/payment and revenue reconciliation.
- **Not proven production-ready:** owner/operator authentication, live tool execution, durable KMDB/CMDB, production monitoring/alert delivery, Android/macOS releases, application-state replication, independent restore and controlled production recovery.
- Product-specific verification is required for each named service/capability; a prompt alias, package, architecture label, or preset is not proof of a connection.
- Publishing, artificial engagement, financial actions, production traffic switching and destructive recovery remain gated.

## Immediate safe next steps
1. Review and replace Render's `python3 --version` build command with repository-appropriate dependency/build checks after identifying the service's actual dependency manifest.
2. Select one owner-approved LLM endpoint/model and configure secrets only in protected runtime settings; execute a non-sensitive live smoke test with timeout, cost cap and redacted evidence.
3. Add a machine-readable connector/config inventory with owner, endpoint, scopes, secret reference (never value), data classification, budget, health check, last-tested timestamp, evidence URL and rollback.
4. Verify Meta AI and 3D/4D/5D individually with product-specific live tests before changing any status to CONNECTED.
5. Keep publication and production failover disabled until owner authentication, permission tests, audit, data recovery and independent verification pass.

## Safety and evidence limits
This is an inventory, not a penetration test or live provider certification. No secrets were read into this report; no deployment, environment-variable change, external publication, destructive DR operation, or traffic switch was performed. Any real credential discovered in tracked history should be rotated through its owner/provider workflow, without copying the value into issues, logs or reports.
