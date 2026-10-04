# Vyomaraj AI Agent OS — Final Target Architecture and Immediate Remediation

Status: target architecture and staged implementation plan. This document is not proof that external services are already connected or deployed.

## 1. Mission and privacy boundary

Vyomaraj is a private control plane. Internal prompts, memories, credentials, model-routing decisions, agent topology, recovery controls, operational logs, and private repositories must remain private. Only explicitly approved outputs may be published to social platforms or external destinations.

Design goals: scalable technology adoption; provider neutrality; secure configuration; modular build and inheritance; observable integration; self-healing; tested forward/reverse backup and restore; safe disaster recovery; measurable availability, RTO, and RPO.

## 2. Logical architecture

Private control plane: ShriYantra
- Identity, tenant/workspace boundaries, RBAC/ABAC, consent, policy and approval gates.
- Configuration registry, secrets references, model/provider registry, capability registry and versioned agent contracts.
- Audit events, telemetry, cost/rate limits, quotas, health and feature flags.

Intelligence foundation
- LLM gateway/router: OpenAI API and ChatGPT-connected workflows where supported, Anthropic/Claude, Google/Gemini, local and open-weight models, and future providers through adapters.
- ChatGPT integration must distinguish the ChatGPT user product, custom GPTs/Actions/connectors where available, OpenAI API, and MCP/tool integrations. These are separate integration surfaces; access to one does not imply access to another.
- Harness: execution boundary around every model/tool call; validates identity, permissions, schemas, policy, budget, risk, human approval and allowed side effects.
- RAG: source connectors, ingestion, parsing/OCR, chunking, embeddings, hybrid/vector + keyword retrieval, reranking, ACL filtering, provenance, freshness, deletion propagation and source quarantine.
- CAG (project definition: context-augmented generation): assemble bounded task context from policy, agent role, user intent, checkpoint, approved memory and RAG evidence; keep trusted policy separate from untrusted retrieved content.
- MAG (project definition: memory-augmented generation): governed episodic, semantic and procedural memory with scope, provenance, expiry, consent, validation, versioning and deletion/retention rules.
- Knowledge and context controls: token budgets, redaction, prompt-injection isolation, citation/evidence requirements and context-window fallback.

Orchestration and execution
- Bharath / Vyomaraj and Laxman / Jarvis are peer-capable heads with explicit authority boundaries and reconciled shared state; do not assume one is automatically safe to promote over the other.
- Hermes is the integrity witness/guardian: heartbeat, health, quorum/fencing decisions, reconciliation, checkpoint verification and recovery audit.
- Universal agent mesh: research, fact-check, coding, architecture, security, data, creative/media, social publishing, business, finance, knowledge, automation, SRE and disaster-recovery agents.
- Arena is a delegated execution runtime behind a versioned adapter. Its tasks receive a signed/validated envelope with task ID, requesting principal, head/agent, policy version, approved tools, data classification, risk, timeout, budget, idempotency key, checkpoint reference and output schema. Arena results return as untrusted data until validated by Harness and Hermes.
- Additional runtimes: provider APIs, MCP servers, approved browser/tool agents, local model workers, queues, scheduled jobs and external APIs. Each is optional and replaceable.

Data and platform foundation
- API gateway; stateless services; durable queue/event bus; relational metadata store; object/blob storage; vector/search index; governed memory store; cache; workflow/job state; secrets manager; identity provider; observability stack.
- Containerized deployments and CI/CD; infrastructure as code; environment separation (dev/test/staging/prod); migrations; schema/version compatibility; dependency and container scanning; signed artifacts and SBOM where practical.
- Scale horizontally using queues, bounded concurrency, back-pressure, autoscaling, per-provider rate limits, circuit breakers, timeouts, retries with jitter and dead-letter queues. Never retry non-idempotent side effects without idempotency protection.

## 3. Required execution contract

authorize -> retrieve RAG evidence -> assemble CAG -> read authorized MAG -> reason through LLM router -> Harness preflight -> execute least-privilege tool/runtime -> validate schema and evidence -> Hermes integrity checks -> checkpoint/commit -> audit -> approved learning/memory update.

Fail closed for unknown identity, missing policy, invalid signatures, unapproved high-impact actions, unavailable mandatory audit, and untrusted tool output. Dry-run is the default. External publication, financial transactions, destructive changes, production deployment, and authority changes require explicit policy and appropriate approval.

## 4. Configuration, build and inheritance

- All environment-specific values live in versioned non-secret configuration; credentials are secret-manager references or protected CI secrets, never committed in source or copied into logs.
- Validate configuration schema at startup and in CI. Reject unknown provider IDs, missing required endpoints, unsafe permissions, duplicate agent IDs and incompatible versions.
- Inheritance is contract-based, not blind prompt copying. Every agent inherits the baseline policy, identity context, RAG/CAG/MAG interfaces, audit/checkpoint hooks and safety defaults; each agent can only narrow permissions unless an authorized policy explicitly grants more.
- Use capability interfaces/adapters for providers and storage backends. Pin dependency versions; support staged rollout, feature flags, canary, rollback and configuration version history.
- Maintain a capability matrix showing each provider/runtime's supported operations, authentication method, data handling, region, rate limits, cost, timeout, and tested status.

## 5. Self-healing and operational repair

Universal recovery lifecycle:
detect -> classify -> diagnose -> capture evidence -> snapshot -> fence if needed -> repair -> verify -> reconcile -> commit -> audit -> learn.

Self-healing may restart unhealthy workers, recycle expired connections, retry transient failures, open/close circuit breakers, reroute to approved fallback models, requeue idempotent jobs, quarantine bad documents, restore known-good configuration and raise an incident. It must not silently modify access policy, rotate identity ownership, delete user data, force-push Git, promote a split-brain node, or perform destructive recovery without authorization.

Health dimensions: API and business probes, queue lag, job age, model/provider latency and error rate, retrieval quality, memory-store availability, database/object-store health, CPU/RAM/disk/network, certificates, secrets expiry, replication lag, backup freshness, integrity verification, and actual end-to-end task success.

## 6. Forward/reverse backup, replication, restore and DR

- Forward backup: production -> immutable/versioned backup and approved DR target, with encryption, retention, integrity hashes, access isolation and scheduled restore tests.
- Reverse backup: DR/secondary -> primary or independent vault only after identity, provenance, generation/version, policy and integrity checks. Never treat “reverse” as an unconditional mirror overwrite.
- Preserve code, configuration, schema/migrations, database snapshots/logs, object/file data, knowledge sources and indexes (or reproducible index manifests), memory, queue/workflow state where supported, agent/provider registry, audit records, backup catalog and deployment metadata.
- Git replication alone is not application disaster recovery. Do not replicate plaintext secrets; replicate references and securely provision secrets independently.
- For the known GitHub topology: Primary `Vyomaraj1356/Vyomarajai`, branch `main`; DR mirror `deepakGoyal1356/Vyomaraj-Agent-6d64e`, branch `main`. The old `deepakGoyal1356/Vyomaraj-Agent` is not the designated DR target.
- Preserve the current Primary -> DR replication as the default until a conflict-safe promotion/reconciliation procedure is tested. Bidirectional *state exchange* is possible, but do not implement blind bidirectional Git writes or two active writers on the same branch. Use immutable snapshots, change manifests, explicit authority epochs, conflict reports and reviewed fast-forward/reconciliation.
- Failover gates: primary health failure confirmed; secondary health and data freshness verified; integrity and business probes pass; fencing/quorum prevents split brain; authorized traffic switch; post-switch business probe and audit. Failback requires the repaired primary to be reconciled before promotion.
- Measure RPO, RTO, restore duration, data-loss window, recovery verification and service impact. Never promise literal zero downtime or zero data loss.

## 7. Security, privacy and compliance

Least privilege; separate service identities; short-lived credentials where supported; secret rotation; encryption in transit and at rest; redaction; data classification; retention/deletion enforcement; tenant isolation; signed task envelopes; anti-replay/idempotency; prompt-injection defenses; tool allowlists; egress restrictions; audit integrity; dependency scanning; backup isolation; incident response and access review.

Treat model output, retrieved documents, web pages, Arena results and tool responses as untrusted data. They cannot rewrite system policy, reveal secrets or grant themselves permissions.

## 8. Immediate remediation sequence

1. Preserve the current Primary branch and inspect open PR #9 before merging. Do not force-push or overwrite either repository.
2. Run the existing reference runner in dry-run mode; verify Python version, syntax, configuration schema, filesystem permissions and audit/checkpoint output.
3. Configure the real Arena adapter from the deployed Arena API/CLI documentation. Use a dedicated least-privilege service identity and a test workspace; never guess endpoint paths or token formats.
4. Connect RAG to one approved source and a real retrieval backend; test citations, ACL filtering, prompt injection, stale/deleted documents and source failure.
5. Connect MAG to a durable governed store; test scope isolation, provenance, retention, deletion and recovery. Until connected, report NOT_CONFIGURED rather than inventing memory.
6. Add provider adapters one at a time, starting with a non-production health/model probe. Configure OpenAI API separately from ChatGPT product/connector access; add Claude, Gemini and local models through the same router contract.
7. Run contract tests, security tests, failure injection, backup/restore drill, replication verification and rollback test in staging.
8. Enable controlled production execution only after human approval, logs, alerts, idempotency, rate/cost limits and rollback are verified.
9. Keep PR #9 unmerged until required checks and deployment-specific adapter configuration are reviewed and passing.

## 9. Minimum acceptance checklist

- [ ] No secret in repository, logs, task envelope or model context.
- [ ] RAG returns permission-filtered evidence with provenance.
- [ ] CAG respects policy/context budgets and labels untrusted inputs.
- [ ] MAG enforces scopes, provenance, expiry/deletion and tested restore.
- [ ] Provider fallback is bounded, observable and policy-compatible.
- [ ] Arena adapter passes authentication, timeout, cancellation, idempotency and output-validation tests.
- [ ] Every tool call is policy-gated and audited.
- [ ] Checkpoints are written before risky mutations; failed verification never commits.
- [ ] Forward backup and reverse/reconciliation workflows are tested without blind overwrite.
- [ ] DR fencing, failover, failback and rollback are exercised in staging.
- [ ] CI verifies schemas, unit/contract/security tests and configuration.
- [ ] Public publishing requires approval and excludes private internals.
- [ ] SLOs, RTO/RPO and actual recovery evidence are recorded.

## 10. Current implementation truth

The ShriYantra RAG/CAG/MAG + Arena foundation on PR #9 is a reference architecture and runner. RAG and MAG adapters are placeholders until a real backend is configured. The runner intentionally does not execute Arena tasks without a reviewed deployment-specific adapter. This document defines the complete target and safe path to operational integration; it does not claim that external systems have already been connected.
