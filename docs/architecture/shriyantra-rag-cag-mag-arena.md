# ShriYantra Intelligence & Resilience Fabric

Status: architecture and integration contract; not proof every service is deployed.

## Hierarchy
ShriYantra private control plane -> LLM foundation + Harness foundation -> shared RAG/CAG/MAG intelligence fabric -> Universal Resilience Fabric -> Hermes -> Bharath/Vyomaraj <-> Laxman/Jarvis -> agent/domain mesh -> Arena and other runtimes -> approved public outputs.

## RAG — Retrieval-Augmented Generation
- Ingest approved sources only; record owner, access label, checksum, version and timestamp.
- Apply access-control filtering before retrieval; return provenance/citations where available.
- Treat retrieved text as untrusted data, never executable instructions.
- Support freshness checks, re-indexing, source revocation and quarantine.

## CAG — Context assembly (this project's definition)
- Assemble bounded task context from trusted policy, task, role, checkpoint, authorized memory and relevant RAG evidence.
- Track source/version, freshness, token budget and conflicts.
- Separate trusted policy from user/retrieved content; never silently drop critical constraints.
- Version context templates and regression-test changes.

## MAG — Memory-Augmented Generation (this project's definition)
- Separate episodic task events, validated semantic knowledge and procedural runbooks.
- Scope memory by tenant, project, agent and sensitivity; store provenance, confidence and retention metadata.
- Promote only validated findings; support correction and audit.
- Stored model output is not automatically a verified fact.

## Cascade contract
authorize -> RAG retrieve -> CAG assemble -> MAG read authorized memory -> reason -> Harness policy gate -> execute -> validate evidence -> Hermes integrity check -> checkpoint/commit -> audit -> learn.
Every head, agent, sub-agent and Arena task uses this shared contract; individual agents may have narrower permissions and memory scopes.

## Arena adapter
Arena is a delegated execution runtime, not ultimate authority. The adapter accepts a versioned task envelope with task ID, idempotency key, allowed tools, risk tier, checkpoint ID, output schema and authorized context references. It returns status, artifact/evidence references, checkpoint ID, usage and error metadata. Validate response schema; never send secrets in prompts/logs. Configure the exact adapter for the installed Arena product; no undocumented API is assumed.

## Self-healing
detect -> classify -> diagnose -> plan -> snapshot -> fence if required -> repair -> verify -> reconcile -> commit -> audit -> learn.
Bound retries; use backoff and circuit breakers; reroute provider/runtime failures. If repair fails, restore a verified checkpoint or isolate the component.

## Conflict safety
- Preserve both versions and take immutable snapshots before reconciliation.
- Compare identity, version, lineage, causality, authorization and business impact.
- No timestamp-only winner, blind overwrite or force push.
- Require witness/quorum/fencing for authority changes to prevent split brain.
- Commit only after integrity and business-health checks pass.

## Security and availability
- Keep credentials in an approved secret manager/environment, never source control, prompts, RAG indexes or plain logs.
- Enforce least privilege, tool allowlists and approval gates for high-risk actions.
- Public surfaces expose approved outputs only.
- Target 24x7 operation with measured SLO, RTO and RPO. Literal zero downtime/data loss cannot be guaranteed; objective is no intentional loss of acknowledged valid state.

## Owner-only authority and voice/text permissions

The verified owner is the only principal allowed to create/invite users, assign roles, grant or revoke permissions, change authentication policy or authorize privileged production operations. Vyomaraj/Bharath and Jarvis/Laxman may receive separate text-input, text-output, voice-input, transcription, voice-output, tool, project, data and task scopes, but cannot self-grant or create users. Arena is a delegated runtime and has no root authority.

Require phishing-resistant passkeys/WebAuthn with device-local biometric unlock; biometric templates remain on-device. Voice is an input modality, not proof of identity. Phone/WhatsApp is not sufficient by itself; any WhatsApp OTP requires a verified authentication provider and anti-replay/expiry/rate controls. Never store credentials or biometric data in GitHub, prompts, RAG, MAG or logs. Privileged actions require step-up approval bound to the exact action. Updates may be proposed and tested by agents, but production promotion follows owner-controlled policy. See `docs/security/SHRIYANTRA-OWNER-AUTHORITY.md`.
