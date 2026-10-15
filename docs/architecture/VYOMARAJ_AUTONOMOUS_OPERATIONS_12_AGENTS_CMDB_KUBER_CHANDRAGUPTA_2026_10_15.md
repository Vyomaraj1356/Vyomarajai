# Vyomaraj + Jarvis — Autonomous Operations, Governance, 12-Agent Model and Continuous Evolution

**Revision:** 2026-10-15  
**Status:** Proposed architecture and acceptance contract. This document defines required behavior; it does not assert that all integrations or autonomous operations are currently deployed.

## 1. Architecture decisions

1. **Vyomaraj / Bharath** is the coordinating orchestrator and system planner.
2. **Jarvis / Laxman** is the execution, verification, heartbeat and recovery coordinator.
3. Vyomaraj and Jarvis operate as reciprocal peers for health, task continuity and disaster recovery. They must use leases/fencing, a clear authoritative-writer rule and split-brain prevention; two peers must never independently write the same authoritative data without a consistency protocol.
4. **Hermes** is the security/integrity witness and policy enforcement function.
5. **Kuber** owns finance controls, audit coordination, compliance tracking, spend governance, reconciliation and escalation visibility.
6. **Chandragupta** is the legal and regulatory intelligence sub-agent under Kuber. It tracks obligations and evidence; it is not a substitute for qualified legal counsel and cannot provide a definitive legal opinion without qualified review.
7. **Podcast moves under Entertainment & Media**. Keep podcast workflows, prompts, tools and metrics as a specialist sub-agent/lane rather than a separate top-level agent.
8. The taxonomy uses **12 main agent families**, symbolically aligned with the 12 Jyotirlingas. This is a naming/organizational convention, not a technical dependency.
9. **CMDB is the authoritative configuration/change inventory**, linked to source control, prompt/tool/agent registries, deployments, runtime observations, approvals, audit records and rollback artifacts.
10. Every new feature, technology, regulation, trend or material change must enter a governed intake-and-impact process before adoption.

## 2. Twelve main agent families

| # | Main agent family | Core responsibilities | Representative sub-agents |
|---|---|---|---|
| 1 | Education & Knowledge | Teaching, research literacy, structured learning and assessment | Tutor, curriculum planner, quiz/exam builder, languages, dictionary, vocabulary, civics, Constitution, history, Indian knowledge, culture, metals/coins/stamps |
| 2 | Bhakti Shakti | Devotional and sacred-culture content with source/context discipline | Scripture research, mantra/prayer explainer, festival and ritual information, pilgrimage, devotional narration |
| 3 | Astro-Numerology-Vigyan | Traditional systems and scientific explanation, clearly distinguishing evidence from belief | Astrology, numerology, calendar, astronomy/science explainer, comparative-source reviewer |
| 4 | Food & Culinary | Recipes, culinary education, menus, food safety and product workflows | Regional cuisine, baking, cakes, desserts, beverages, nutrition information, kitchen costing |
| 5 | Finance & Kuber | Finance, accounting evidence, audits, compliance coordination and commercial controls | Chandragupta legal/regulatory intelligence, invoice/reconciliation, budget, tax research, risk, ROI, procurement and spend controls |
| 6 | Life & Culture | Practical life skills, cultural knowledge and personal-development content | Communication, productivity, local culture, practical guides, accessibility/localization |
| 7 | Agriculture & Living World | Agricultural and ecological knowledge | Crops, soil/water, horticulture, livestock, pests, sustainable practices, biodiversity |
| 8 | Sports | Sports information, analysis, education and media | Rules, statistics, player/team research, training education, events and highlights |
| 9 | Entertainment & Media | Creative production, media pipelines and podcast | Writing, stories, screenplay, music, animation briefs, podcast research/script/editing/show notes, video/audio, thumbnails, repurposing |
| 10 | Platform & Collaboration | Internal platform operations, partner workflows and integrations | Workspace operations, connector registry, support coordination, customer service, collaboration |
| 11 | Tourism | Destination and travel information/content | Destination research, itineraries, attractions, local culture, travel guides, approved booking handoffs |
| 12 | War & Strategy | Historical/educational strategy and fictional strategy content within safety boundaries | Military history, strategic studies, leadership, scenario analysis, fictional world-building |

**Shared cross-agent services (not separate top-level domain agents):** Research & trend intelligence; Fact-check/provenance; Translation/localization; Rights/copyright; Safety review; Prompt engineering; Content QA; Publishing operations; Analytics; Sales/customer journey; Software engineering; SRE/operations; Security; Backup/DR; Accessibility.

Each sub-agent must have an ID, purpose, scope, prohibited actions, owner, prompt version, input/output schema, approved tools, permissions, data classification, model policy, tests, quality threshold, budget, timeout/retry policy, approval gates, audit events, health status and disable/rollback procedure.

## 3. Kuber audit, compliance and escalation operating model

Kuber is the control and reporting owner for financial assurance and compliance workflow. It must coordinate with Vyomaraj, Jarvis, Hermes and the relevant domain agent.

### Kuber functions
- Revenue, expense, invoice, refund, fee and settlement reconciliation against authoritative records.
- Budget and cost caps by model, tool, agent, product, channel, campaign and environment.
- Financial anomaly detection, duplicate-payment detection and variance reporting.
- Audit evidence index, evidence freshness, control owner, test result, finding, severity and remediation due date.
- Compliance register with jurisdiction, topic, authoritative source, publication/effective dates, applicability, obligation, owner, evidence and review deadline.
- Supplier/vendor, licensing, contract, privacy, retention, security and platform-policy review tracking.
- Findings and corrective-action register with risk, impact, due date, owner, escalation level and closure evidence.
- Monthly management report: control health, open findings, spend, actual revenue, refunds, margin, overdue actions and unverified claims.

### Escalation severity
- **P0 Critical:** suspected compromise, unlawful disclosure, destructive/unauthorized action, data integrity loss, split-brain, failed critical recovery or uncontrolled financial exposure. Stop the affected action, preserve evidence, alert the owner through configured channels and follow the incident runbook.
- **P1 High:** missed regulatory deadline, significant reconciliation mismatch, critical integration outage, failed backup/restore, repeated authentication failures or high-impact policy issue. Notify owner promptly and track until verified closure.
- **P2 Medium:** degraded service, approaching deadline, moderate variance, repeated job failure or stale data. Create an assigned ticket and notify through configured preferences.
- **P3 Routine:** optimization, low-risk recommendations, scheduled reviews and trend opportunities. Include in the daily/weekly digest.

Thresholds, deadlines, recipients and contact channels must be configurable and tested. Do not invent thresholds or claim that an alert was delivered unless delivery evidence exists.

### Email/call/support policy
Vyomaraj/Jarvis may autonomously gather diagnostics, draft a support request, open an authorized support ticket, check its status and follow up within approved account scopes. Sending email, making a phone call, submitting a contractual/legal representation, disclosing sensitive information, incurring cost, or changing production settings requires an explicit pre-approved policy or action-specific owner approval. Use official verified contact channels, minimal redacted diagnostics, ticket IDs and a complete audit record. Never impersonate the owner, fabricate evidence, share secrets, or claim a support request was made when it was only drafted.

## 4. Chandragupta — legal and regulatory intelligence sub-agent

Chandragupta sits under Kuber for control ownership, with a dotted-line advisory relationship to every domain agent. Legal/regulatory requirements affect the entire system, so it must not be isolated from engineering, content, HR/people workflows, finance, privacy, security, sales or publishing.

### Scope
- International/global obligations and treaties where applicable.
- India central laws, rules, regulations, regulator notifications, official guidance and court/tribunal developments.
- State/UT laws, rules, notifications and regulator requirements.
- Local/municipal/region-specific permits, tax, labor, consumer, business, content and operating requirements.
- Sector-specific requirements: privacy/data protection, cybersecurity, consumer protection, advertising, intellectual property, tax/accounting, payments, employment, education, food, agriculture, media, platform terms and cross-border data transfers as applicable.
- Contract, license, terms-of-service, content rights and retention review tracking.
- Effective date, transition period, applicability, jurisdiction and official-source lineage.
- Impact assessment for system, product, agent, prompt, tool, data store, content, client and business process.
- Remediation tickets, deadlines, owner approval and evidence of closure.

### Legal-intelligence workflow
1. Monitor authoritative official gazettes, statutes, regulator websites, court publications and trusted secondary alerts.
2. Capture source URL, jurisdiction, issuing authority, published/effective dates, retrieval time, version and content hash.
3. Distinguish binding law, regulator guidance, court decision, proposed bill, consultation, industry standard, platform policy and commentary.
4. Verify source and applicability; flag uncertainty and conflicting interpretations.
5. Map the change to impacted agents, data, features, prompts, tools, deployments, contracts and business lanes.
6. Assign impact/severity, legal review need, control owner and due date.
7. Notify Kuber, Vyomaraj, Jarvis, Hermes and each affected agent; create tracked remediation items.
8. Require qualified counsel or authorized owner review for material/ambiguous/high-risk conclusions.
9. Apply approved changes through change management, tests and deployment gates.
10. Verify the change and preserve closure evidence; continue monitoring for amendments.

Do not present generated summaries as legal advice, assume one jurisdiction applies globally, or automatically change production behavior solely from a detected headline.

## 5. CMDB — authoritative change and configuration lifecycle

CMDB must be more than a static list. It should join desired configuration, actual runtime state, version control and change history.

### Managed configuration items
- Services, environments, hosts, deployment targets, domains, networks and dependencies.
- Agents, sub-agents, prompts, prompt templates, models and provider adapters.
- MCP servers, A2A endpoints, plugins, APIs, credentials references and permission scopes (never secret values).
- Databases, KMDB, vector indexes, queues, object stores, backups and retention policies.
- Workflows, CI/CD pipelines, feature flags, schedules, alert rules and runbooks.
- Client builds, APKs, signing identities references, releases and compatibility ranges.
- Legal/compliance controls, owners, evidence references and review deadlines.
- Business products, publishing channels, billing integrations and finance data sources.

### Required change record
- Unique change ID; requestor; owner; date/time; affected configuration-item IDs.
- Change type: new feature, upgrade, patch, configuration, prompt/model change, dependency, security fix, rollback, migration or emergency.
- Before/after version and redacted configuration diff.
- Source branch, commit SHA, pull request, artifact/build ID and deployment ID.
- Reason, expected benefit, impact/risk assessment, dependencies and compatibility.
- Tests run, test result links, security/compliance review and approval record.
- Deployment start/end, actual outcome, observed runtime state and drift result.
- Backup/checkpoint and rollback instructions; rollback trigger and outcome if used.
- Related incidents, findings, costs, provider/model changes and impacted agents.
- Final status, verifier, evidence links and next review date.

### Change procedure
1. Detect a proposed or observed change.
2. Create or update a change record before mutation (emergency exceptions still require retrospective evidence).
3. Resolve the complete dependency graph and impacted agents.
4. Assess security, legal/compliance, privacy, reliability, cost and customer impact.
5. Create a versioned patch/configuration change on an isolated branch.
6. Test in isolated environments and validate rollback.
7. Obtain approvals according to risk.
8. Deploy through controlled CI/CD.
9. Compare desired versus actual state; record drift and read-after-write evidence.
10. Notify affected agents and Kuber with the change ID, impact, required actions and status.
11. Close only after independent verification; otherwise leave blocked/open with owner and deadline.

## 6. Cross-system trend and capability intelligence

### Sources to monitor
- Official model/provider release notes, APIs, deprecations, SDKs, rate/pricing changes and service incidents.
- Security advisories, CVEs, dependency releases and infrastructure/runtime updates.
- Official laws, regulator notices, standards and platform policies.
- Social/search trends and creator-platform analytics where permitted.
- User requests, support tickets, customer feedback, product analytics and competitor/market signals.
- New tools, agent frameworks, protocols, benchmarks and relevant research.

### Intake-to-adoption pipeline
1. Discover and record source/provenance/time.
2. Deduplicate and score freshness, reliability, relevance and confidence.
3. Classify as trend, feature request, security issue, deprecation, regulation, opportunity or incident.
4. Estimate impact, urgency, implementation cost, risk, revenue/customer value and confidence.
5. Map to affected main agents, sub-agents, prompts, models, tools, datasets, clients and controls.
6. Create a proposal/change record; assign an accountable owner.
7. Run sandbox/benchmark/security/compliance tests and compare with the current baseline.
8. Present a decision brief: adopt, pilot, defer, reject or monitor.
9. Obtain owner approval when scope, permissions, external exposure, spending or legal posture changes.
10. Deploy gradually with a feature flag, canary, budget cap and rollback path.
11. Notify all affected agents and Kuber; require acknowledgement for critical changes.
12. Measure real impact and either standardize, roll back or retire the feature.

Social virality alone is not a reason to adopt a feature. Source credibility, customer value, legal eligibility, cost, security and measurable benefit must all be considered.

## 7. Prompt and AI-platform registry

The system must distinguish the platform's product-level features from APIs and runtime integrations. A ChatGPT subscription or Claude/Gemini web UI does not automatically grant programmatic API access.

### Registry record required for every prompt/instruction
- Platform and capability family.
- Prompt/skill/agent ID, purpose, owner, version and status.
- System/developer/task instructions and variables, with secrets excluded.
- Model/provider, supported modalities and context/limit assumptions.
- Input/output schema, examples, refusal/safety boundaries and data class.
- Tool/action/connector scopes and approval requirements.
- Evaluation dataset, expected behavior, regression results and score threshold.
- Cost/latency limits, fallback behavior and known failure modes.
- Source provenance, created/updated date, changelog, approver and rollback version.
- Cross-platform portability mapping and platform-specific overrides.

### Platform capability families to inventory
- **ChatGPT/OpenAI products:** model and API catalog; system/developer/task prompt templates; Projects/project instructions; custom GPT instructions and knowledge; Actions/API schemas; connectors; tool calling; structured outputs; file/image/audio/video capabilities where supported; Codex/repository instructions and coding workflows; evaluations, usage/budget and model deprecation monitoring.
- **Claude/Anthropic:** model/API catalog; system and task prompts; Projects/project knowledge; Skills; tool use; MCP connectors; structured output where supported; code/repository workflows; usage limits, pricing, deprecation and evaluation.
- **Google Gemini:** model/API catalog; system instructions; Gems/custom assistants; files/context; function calling; extensions/connectors where available; structured output; multimodal workflows; usage limits, release changes and evaluation.
- **Other AI/workflow platforms:** Arena AI, local/open models and any approved provider, each with its own capability, terms, permissions, API, data policy, cost, evaluation and deprecation records.
- **Creation tools:** Runway, OpenArt, Canva, Adobe and Descript—prompt templates, brand assets, licensing, input/output formats, job state, generation cost, review and version history.
- **Growth/analytics tools:** Metricool and vidIQ—channel permissions, analytics scope, content workflows, rate limits, publishing approval and performance evidence.

These are capability families to audit against the actual current platform offering. Product names and capabilities change; each integration must be confirmed from current official documentation and tested. Do not scrape or attempt to copy hidden internal system prompts from third-party services. Store user-owned prompts and permitted platform settings; use official APIs and interfaces.

### Prompt lifecycle
Draft → source/owner review → schema and safety tests → offline evaluation → approved version → controlled deployment → monitoring → drift/regression detection → rollback or retirement. Prompt/model updates are CMDB change events and must notify impacted agents and Kuber.

## 8. Continuous scaling and self-improvement

Vyomaraj/Jarvis can continuously identify, test and propose improvements. They must not grant themselves additional permissions or silently move untested code/configuration into production.

### Improvement loop
1. Observe reliability, task outcomes, user feedback, costs, model/provider releases, security advisories and domain trends.
2. Detect a gap or opportunity and create an evidence-linked improvement ticket.
3. Rank by customer/business value, risk reduction, urgency, confidence, cost and dependencies.
4. Identify affected agents, prompts, integrations, CMDB items and compliance controls.
5. Design the smallest reversible change with acceptance criteria.
6. Test in a sandbox: unit/regression, quality, security, privacy, legal applicability, load, cost and failure recovery as relevant.
7. Compare against the baseline and reject regressions.
8. Require approval for production, new permissions, external communications, spending, legal commitments or material policy changes.
9. Deploy progressively with feature flags, health gates, cost caps and rollback.
10. Observe real outcomes and verify independent evidence.
11. Update docs, CMDB, prompt registry, agent registry and runbooks.
12. Notify affected agents; obtain acknowledgement or mark the task blocked.
13. Kuber audits cost, ROI, compliance impact and outstanding findings.
14. Retire obsolete tools/prompts/models only after dependency and rollback checks.

### Scale dimensions
- **Horizontal:** more workers/agent instances behind queues and concurrency limits.
- **Vertical:** appropriate compute/resources based on measured bottlenecks.
- **Model routing:** select task-appropriate approved models; do not assume the largest model is always best.
- **Caching/retrieval:** reduce repeated work while controlling freshness and access.
- **Queue/back-pressure:** protect dependencies from overload.
- **Provider diversity:** validated adapters, quotas and tested fallbacks.
- **Agent specialization:** split roles only when it improves measured outcomes and has a clear owner.
- **Cost governance:** budget per task/agent/channel and stop conditions.
- **Quality scaling:** evaluations and regression suites must grow with capability.
- **Operational scaling:** alerts, runbooks, on-call/escalation routes and DR capacity.

## 9. 24×7×365 autonomy contract

### Autonomous without routine human intervention
- Health checks, heartbeat, queue processing, retry of safe/idempotent tasks.
- Read-only research and trend monitoring within approved sources.
- Routine diagnostics, evidence collection, reconciliation and status reports.
- Drafting tickets, emails and support requests; authorized ticket submission/follow-up.
- Low-risk approved deployments or configuration changes only if pre-authorized and gated.
- Backup freshness checks, integrity verification and alerts.
- Routine content drafts and analytics reports without unapproved publication.

### Owner approval or qualified human review required
- New permissions, providers, data sharing or high-risk connectors.
- External publishing, mass messaging, financial transactions or material spend.
- Legal commitments, regulatory filings or authoritative legal interpretations.
- Destructive data changes, migrations, production failover/failback and key rotation with availability impact.
- Changes to owner/root access, safety policy, audit retention or protected recovery gates.
- Any action whose scope, cost, destination or consequence is uncertain.

### Runtime requirements
- Durable task queue and persisted state; safe restart and checkpoint recovery.
- Separate primary and secondary environments with writer fencing and split-brain prevention.
- Independent backups and regular isolated restore drills.
- Monitored uptime, queue lag, task failures, costs, provider availability and data freshness.
- Circuit breakers, rate limits, dead-letter queues and bounded retries.
- Tested escalation recipients and multiple authorized notification routes.
- Defined RPO/RTO, service objectives and documented maintenance/degradation modes.
- No claim of 24×7 operation until monitoring and recovery evidence support it.

## 10. Notification and change-propagation protocol

For each approved material change, publish a signed/versioned change event containing: change ID, summary, source, affected CMDB items, impacted agents, urgency, effective time, required action, owner, approval, tests, rollback, evidence links and acknowledgement deadline.

Vyomaraj routes the event. Jarvis checks that affected agents reload the approved version and pass health tests. Hermes checks policy/integrity. Kuber assesses cost, financial-control and compliance impact. Each affected agent reports acknowledged, applied-and-verified, not-applicable or blocked. Unacknowledged critical changes escalate; no silent assumed synchronization.

## 11. Minimum system-wide acceptance gates

- [ ] Every main agent and sub-agent is in one canonical registry with a named owner.
- [ ] Podcast is represented under Entertainment & Media without losing its workflow inventory.
- [ ] Chandragupta's legal/regulatory scope and qualified-review gates are explicit.
- [ ] Kuber tracks actual financial evidence, audit findings, deadlines and escalations.
- [ ] CMDB captures before/after state, source/version, tests, approvals, deployment and rollback.
- [ ] Prompt registry covers user-owned prompts and each approved platform integration.
- [ ] One provider works end-to-end through the protected harness.
- [ ] One safe tool call passes authorization, execution and independent read-back.
- [ ] Trend intake maps changes to affected agents and records their acknowledgements.
- [ ] Autonomous email/support behavior uses verified channels, permitted scopes and audit records.
- [ ] Primary/secondary runtime and application data recovery are independently tested.
- [ ] Restore, failover and failback have measured outcomes and explicit gates.
- [ ] The 24×7 operating objective is supported by real infrastructure, monitoring and escalation tests.
- [ ] Production changes remain reversible and fail closed when evidence is missing.

## 12. Implementation sequence

1. Reconcile this specification with repository code, prompts, workflows and current deployment.
2. Complete and verify the prompt-runtime path.
3. Build the canonical agent/sub-agent, prompt, tool and CMDB registries.
4. Establish Kuber findings/escalation and Chandragupta legal-intelligence records.
5. Prove one provider and one authorized tool path.
6. Add durable task/event state and change-notification acknowledgements.
7. Prove application-data backup, read-after-write, isolated restore and reciprocal DR fencing.
8. Implement trend intake, sandbox evaluation and controlled rollout.
9. Add support-ticket/email automation within approved scopes.
10. Expand platform/domain integrations based on measured business value and verified controls.

**Truth statement:** This specification is a target and acceptance contract. A requirement is complete only when implementation, configuration, tests, runtime behavior and independent evidence agree.