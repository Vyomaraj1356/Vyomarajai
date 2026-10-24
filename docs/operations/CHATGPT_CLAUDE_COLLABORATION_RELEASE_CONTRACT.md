# ChatGPT + Claude collaboration contract for Vyomaraj/Jarvis

**Status:** additive implementation contract; provider connectivity and production acceptance remain unproven.
**Authority:** owner/operator controls credentials, external actions, release, finance, publishing and recovery.
**Canonical registries:** `config/ai/PROMPT_REGISTRY_V1.json`, `config/ai/PRODUCTION_AGENT_TOOL_REGISTRY_v1.0.yaml`, the canonical agent registry and the integration truth matrix. This document references them; it does not duplicate their entries or silently replace them.

## Goal

Use approved ChatGPT/OpenAI and Claude/Anthropic capabilities to assist Vyomaraj and Jarvis throughout the lifecycle: discovery, research, requirements, architecture, writing, frontend/backend implementation, testing, security, deployment planning, monitoring, incident analysis, recovery planning, measurement and learning. Each stage uses the best available approved capability; no stage assumes every provider or tool is connected.

## Collaboration pattern

1. **Intake and identity:** create a task ID, idempotency key, owner, scope, data classification, budget, deadline, expected output and risk tier. Reject missing required fields for high-risk tasks.
2. **Canonical context:** retrieve only necessary approved context from the existing source of truth. Include registry/version references and source provenance, not copied duplicate registry entries or secrets.
3. **Plan:** Vyomaraj coordinates the task and decomposes it into bounded work units. Jarvis checks dependencies, failure modes, tests and rollback. Both are logical roles, not proof of separate live agents.
4. **Provider selection:** choose an approved provider per work unit based on capability, quality, language, latency, availability, privacy, rights and cost. ChatGPT consumer product access, OpenAI API access, and connected ChatGPT tools are separate surfaces; Claude product access and Anthropic API access are also separate. Do not assume one grants the other.
5. **Independent review when useful:** for high-impact code or factual claims, obtain a second independent analysis only when a second provider is actually configured and permitted to receive the data. Compare evidence, not confidence or model consensus. Preserve disagreements and unresolved risks.
6. **Validation:** run deterministic tests, schema checks, security checks and factual/source checks. Model approval is never a substitute for tests. All model output and retrieved external text are untrusted data.
7. **Change proposal:** produce a minimal diff against the canonical version. Preserve originals. Never replace or delete existing content merely to simplify; add only when no equivalent canonical item exists. For a matching item, propose a versioned edit with before/after diff and explicit review.
8. **Approval and execution:** classify actions as read-only, reversible internal change, or consequential external action. Require owner authorization for production deployment, publishing, spending, outreach, access changes, destructive edits, provider credential changes and DR writes. Use scoped, short-lived approvals bound to the exact action and target.
9. **Post-action verification:** independently read back the changed state, compare expected versus actual, retain redacted evidence, and record result. A successful command or workflow alone does not prove user-visible success.
10. **Learn without duplication:** append an audit/result record with task ID, artifact hash, version, sources, providers actually used, tests, approvals and outcome. Upsert by stable ID/idempotency key; do not create another canonical record for a retry. Corrections are new versions linked to the prior version, never silent overwrites.

## No-overwrite / no-duplicate rules

- Treat the existing canonical registry, agent IDs, prompt aliases, content IDs, routes and product IDs as authoritative until a governed migration changes them.
- Before adding any record, normalize its stable key and check the canonical registry. If the key exists, stop and report a conflict; do not auto-create a near-duplicate.
- Use compare-and-swap/version checks (ETag or expected version) for writes. If the source changed since planning, stop and regenerate the diff.
- Never perform destructive replacement on the basis of model output alone. Preserve originals and rollback snapshots.
- Make retries idempotent. Never repeat a non-idempotent external action without reading back its prior status.
- Keep secrets out of prompts, source control, logs, client bundles, model context and audit payloads. Store secret references and rotation status only.
- Keep an explicit provenance trail for source material, generated artifacts, decisions and approvals. Generated content does not become fact until verified.
- Consolidate duplicate entries only after identity matching, dependency analysis, ownership confirmation, backup and a reversible migration plan.

## Provider and tool registry policy

Register each integration in the existing canonical tool/provider registry with: stable ID, provider, supported API/product surface, owner, purpose, scopes, data class, auth method/secret reference, approved models, allowed task classes, timeout, retry policy, idempotency, budget/rate limit, health test, audit policy, fallback, rollback and status.

Allowed statuses: `DESIGN_ONLY`, `CODE_PRESENT`, `CONFIGURED`, `CONNECTED`, `TESTED`, `PRODUCTION_READY`, `BLOCKED`. A status may advance only with linked evidence. Never infer provider connectivity from installed software, a product subscription, a source file, a successful build, or another provider's credentials.

## Trustmode and security gates

- Default to least privilege and no tools. A text model may propose actions but cannot grant itself permissions.
- Treat prompt injection in files, webpages, issue comments and provider output as untrusted data.
- Apply data minimization, privacy/retention rules, rights checks, cost ceilings, request bounds, timeouts, rate limits, safe error handling and circuit breakers.
- Use deterministic allowlists for tool discovery and signed/authorized task envelopes for agent-to-agent requests.
- Require independent tests and owner approval for high-impact or irreversible actions.
- Fail closed if identity, provider configuration, policy, expected version, budget, authorization, evidence or rollback is missing.
- Do not claim 24x7 operation, autonomous recovery, monitoring, model fallback or live integration until exercised in the deployed runtime with evidence.

## Lifecycle acceptance matrix

| Stage | Required artifact | Acceptance evidence |
|---|---|---|
| Research | question, source list, findings, uncertainty | primary sources, dates, citations and conflict notes |
| Design | requirements, architecture and threat model | reviewed interfaces, data classification and rollback |
| Frontend/backend | minimal patch and migration plan | unit/integration tests, accessibility/security checks |
| Content/scriptwriting | original draft, source/rights checklist | factual review, rights review and owner release approval |
| Tools/MCP/A2A | scoped connector contract | auth/scope tests, allowlist, audit, timeout and denial tests |
| Release | versioned build and release manifest | CI for exact commit, deployment smoke, rollback tested |
| Operations | health, SLOs, alerts and runbooks | authenticated dependency probes, alert test and incident drill |
| Disaster recovery | backup catalog and recovery procedure | authorized write/read-back, integrity verification and successful restore/failover drill |
| Improvement | metrics and decision log | source-backed measures, cost/quality comparison and reversible change |

## Current implementation boundary

The Anthropic adapter in `ops/jarvis/anthropic_adapter.py` is an opt-in, no-tools draft adapter. The existing generic LLM harness is OpenAI-compatible and remains separate. This contract does not connect the consumer ChatGPT app, install plugins, provision credentials, configure Render, merge PRs, enable tool permissions, or perform deployment/DR writes. Those actions require the appropriate connected integration and explicit authorization.

## Release checklist

- [ ] Current-head CI passes for the adapter and collaboration tests.
- [ ] Approved ChatGPT/OpenAI API surface and Claude/Anthropic API surface are configured separately in protected secret storage.
- [ ] Provider identity/model, quota/cost caps, privacy terms and data scopes are reviewed.
- [ ] Live smoke test succeeds for each provider separately; outage, timeout, malformed response and fallback tests pass.
- [ ] Duplicate-key conflict, stale-version, retry/idempotency and rollback tests pass.
- [ ] Frontend never exposes keys or privileged tools; backend enforces authentication and authorization.
- [ ] Release smoke, monitoring/alert test, backup restore and DR acceptance pass.
- [ ] Truth matrix is updated with evidence links and the actual status; no aspirational capability is labelled production-ready.
