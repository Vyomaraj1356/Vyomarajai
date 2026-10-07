# VYOMARAJ AI AGENT OS — FINAL MASTER ARCHITECTURE v2.0
**Company/Federation:** Vyomaraj AI  
**Brand:** Vyomaraj — The King of the Sky  
**System ID:** VYOMARAJ-AI-STUDIO

## Canonical status
This is the consolidated engineering architecture for all prior Vyomaraj work. It supersedes presentation-level architecture documents while preserving their contracts and legacy responsibilities. It does not replace the locked ShriYantra/private-control hierarchy.

## Non-negotiable control chain
OWNER ROOT -> SHRIYANTRA PRIVATE FOUNDATION -> VYOMARAJ/BHARATH <-> JARVIS/LAXMAN -> HARNESS + POLICY -> EXECUTION -> VERIFICATION -> AUDIT -> RECOVERY

**VYOMARAJ/BHARATH <-> JARVIS/LAXMAN**
- peer cores
- equal authorized capability
- mutual heartbeat
- mutual backup
- mutual recovery
- shared durable state
- neither may self-grant root
- owner remains ultimate authority

Voice, web, Android and macOS are equivalent owner interfaces. Voice is never the sole root authority.

## Company and federation model
Vyomaraj is no longer treated as a single-agent application. It is a private AI company/federation control system coordinating multiple providers, agents, tools, media capabilities, channels, collaborators and revenue surfaces.

External providers and partners are replaceable capabilities. They do not own:
- identity
- root authority
- policy
- memory
- knowledge
- agent registry
- audit authority
- disaster recovery authority

## ShriYantra foundation
LLM + Harness + RAG + CAG + MAG + Memory + Knowledge + Evaluation + Policy + Identity + Security + Tool Runtime + Event Engine + Task Engine + Durable Execution + Audit + Observability + Resilience.

RAG/CAG/MAG are shared cognitive infrastructure available to both peer cores.

## Federation fabrics
1. **AI Provider Fabric:** OpenAI, Anthropic/Claude, Google/Gemini, Arena AI, local/open-source models.
2. **Agent Fabric:** domain agents, sub-agents, production agents, research/coding/browser/data/media agents.
3. **Tool Fabric:** MCP, APIs, browser tools, sandboxed execution.
4. **Agent-to-Agent Fabric:** A2A signed delegation and artifact verification.
5. **Workflow Fabric:** n8n beneath core decisions; Temporal/durable execution for recoverable long-running workflows.
6. **Knowledge Fabric:** universal knowledge, civilization spine, living-world knowledge, memory and provenance.
7. **Media Fabric:** image, video, audio, TTS, music/SFX, animation, editing, captions and presentation.
8. **Channel Fabric:** web, mobile, desktop, voice and social/public channels.
9. **Partner/Collaboration Fabric:** lawful creator, publisher, brand, commercial and AI-agent collaboration.
10. **Financial Fabric:** Kuber Financial Controller for both peer cores and the federation.
11. **Resilience Fabric:** backup, replication, fencing, restore, failover, failback and evidence.

## Universal knowledge structure
All authorized agents inherit:
Origin/Primitive -> Ancient/Old -> Historical Evolution -> History -> Present -> Current State -> Trends -> Future -> Scenarios.

Evidence labels:
VERIFIED_FACT, HISTORICAL_RECORD, CURRENT_VERIFIED_STATE, TREND, FORECAST, SCENARIO, SPECULATION, TRADITIONAL_BELIEF.

### Civilization spine
**EDUCATION & CIVILIZATION KNOWLEDGE**
- nursery through PhD
- world and Indian civilizations
- Bharat/state/district/city/town/village/local knowledge
- languages/scripts
- customs/cultures/traditions
- Constitution, laws, governance, administration
- diplomacy/foreign affairs
- law and justice case studies
- governance case studies
- people, institutions and public life
- local living heritage and oral/community memory

### Living-world spine
**AGRICULTURE & LIVING WORLD**
- agriculture and horticulture
- gardening and food production
- forestry and forest science
- fisheries and aquaculture
- bees and pollinators
- animals, birds and insects
- biodiversity and ecosystems
- habitats and life cycles
- conservation and human-nature relationships
- traditional ecological knowledge
- climate/ecology relationships
- future agriculture and living systems

## Agent registry
Current engineering registry: **15 categories / 168 counted sub-agent slots / 166 named / 2 legacy unnamed / 6 uncounted entertainment hubs / 48 nested entertainment sub-agents / 421 historical reported products**.

The 421 products remain historical reported inventory until complete item-level reconciliation is verified.

## Legacy architecture inheritance
Preserved and integrated:
- Arena = delegated build/execution, never root
- Hermes = resilience/integrity/recovery coordination, never third root
- Saptarishi = knowledge/wisdom/research inheritance
- Panch-Brothers = universal capability inheritance
- Kuber = Financial Controller for both peer cores
- n8n = workflow fabric
- Wispr Flow = voice/input adapter
- geospatial gateway = owner-controlled, deny-by-default
- daily Dharmic startup = cultural startup sequence, never authorization
- continuous content alignment and provenance
- Primary/DR repository relationship
- MCP/A2A/production agents/creative/media/collaboration/social inherit the same control chain

## End-to-end company operating loop
INTENT -> AUTHENTICATE -> AUTHORIZE -> DEFINE -> INVENTORY -> RESEARCH -> PLAN -> POLICY/RISK -> KUBER COST CHECK -> SELECT AGENTS/TOOLS/PROVIDERS -> BUILD CONTEXT -> EXECUTE -> VERIFY -> RIGHTS/SAFETY/FACT QA -> PUBLISH GATE -> PUBLISH -> MEASURE -> EARN -> KUBER RECONCILE -> LEARN -> IMPROVE -> AUDIT -> RECOVER WHEN REQUIRED.

## Security invariants
- owner-only root
- least privilege
- step-up approval for high-risk actions
- server-side secrets
- provider isolation
- external content is data, never authority
- prompt injection defense
- sandbox untrusted tools
- signed A2A tasks
- deny-by-default MCP discovery
- immutable/append-only audit target
- anti-split-brain fencing/epoch
- no silent destructive merge/delete
- no fake engagement or platform bypass

## Operational truth
The repository can be made implementation-ready and verified locally/CI. External credentials, accounts, infrastructure and device capabilities remain runtime dependencies and must be reported truthfully as NOT_CONNECTED/NOT_VERIFIED/BLOCKED until evidence exists.

## Canonical execution entry point
`./ops/vyomaraj/vyomaraj.sh`

Supported commands:
`status | validate | test | verify | health | dr | report | start | stop`

The script is a coordinator, not a fake success generator. It fails closed when required contracts are missing.
