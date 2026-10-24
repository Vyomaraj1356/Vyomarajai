# GitHub Tooling and AI Integration Catalog — Initial Research

**Status:** DISCOVERY ONLY — no third-party repository is installed, trusted, integrated, or approved for production by this document.
**Owner:** Vyomaraj platform engineering; Jarvis runtime/continuity; Hermes security; Kuber cost and license review.
**Review date:** 2026-10-24
**Policy:** Prefer official upstream repositories, pinned versions/commits, least privilege, isolated evaluation, reproducible builds, and reviewed pull requests. Never execute third-party code directly on a privileged runner.

## Why this catalog exists

GitHub is a discovery source, not an installation or security guarantee. Public source availability does not prove that a project is maintained, safe, compatible, licensed for our use, or appropriate for production. This catalog identifies candidate building blocks to evaluate against the existing Vyomaraj/Jarvis repository before any dependency is introduced.

## Candidate upstream repositories

| Capability | Upstream repository | Potential fit | Initial disposition |
|---|---|---|---|
| Agent orchestration | https://github.com/microsoft/agent-framework | Evaluate for typed agent workflows and multi-agent orchestration; compare with the current orchestrator before adoption. | Evaluate in an isolated branch; no runtime integration claimed. |
| Agent orchestration patterns | https://github.com/langchain-ai/langgraph | Evaluate stateful, checkpointed workflows and human-in-the-loop boundaries. | Compare against existing plan/approval model; do not replace architecture by default. |
| Self-hostable workflow automation | https://github.com/n8n-io/n8n | Potential connector/workflow layer for approved business processes. | Separate deployment and license/security review required; never expose privileged control plane publicly. |
| Retrieval / search pipeline | https://github.com/deepset-ai/haystack | Evaluate source-grounded retrieval and pipeline composition for research workflows. | Benchmark against existing RAG/CAG/MAG design and data provenance requirements. |
| AI workflow/application platform | https://github.com/langgenius/dify | Candidate for bounded internal prototyping of provider workflows and knowledge apps. | Do not treat as the trusted control plane; evaluate isolation, secrets, permissions, licensing and operational cost. |
| Observability | https://github.com/open-telemetry/opentelemetry-collector | Potential vendor-neutral telemetry collection and export. | Evaluate data minimization and India-region destination configuration before use. |
| Container vulnerability scanning | https://github.com/aquasecurity/trivy | Candidate scanner for images, filesystem dependencies and misconfiguration. | Run in CI on test fixtures first; pin action/image versions and inspect permissions. |
| Secret scanning | https://github.com/gitleaks/gitleaks | Candidate scanner to prevent accidental credential commits. | Test against synthetic fixtures; never print matched secret values in logs. |
| Software supply-chain signing | https://github.com/sigstore/cosign | Candidate for verifying/signing container artifacts where applicable. | Adopt only with a documented keyless/key-management policy and verified identity boundary. |
| LLM proxy / routing | https://github.com/BerriAI/litellm | Candidate provider abstraction, routing and budget controls. | High-impact integration: evaluate secret handling, model allowlists, egress controls, logging, fallback semantics and current license before deployment. |
| LLM / RAG evaluation | https://github.com/explodinggradients/ragas | Candidate for measuring retrieval and answer quality with curated test sets. | Use non-sensitive synthetic/approved data; do not let an evaluator self-certify production readiness. |

## Required evaluation gates (all candidates)

1. **Identity and provenance:** Confirm the canonical upstream, maintainers, recent releases, release artifacts, commit history, advisories and ownership changes.
2. **License:** Read the exact license at the selected commit and review transitive dependencies; Kuber records direct/indirect cost and license obligations.
3. **Supply chain:** Pin an immutable commit or verified release; generate an SBOM where feasible; inspect install scripts, actions, containers and dependency lockfiles.
4. **Security:** Scan in a disposable sandbox with no production secrets, no privileged host mounts, no Docker socket, no production network, and no broad GitHub token. Use read-only tokens by default.
5. **Compatibility:** Test the target OS/runtime, Python/Node versions, dependency conflicts, CPU/RAM/storage, India-region and data-residency requirements, and rollback path.
6. **Behavior:** Add unit/contract tests, failure/timeout/rate-limit tests, idempotency and duplicate-prevention tests, and bounded integration tests.
7. **Approval:** Produce a PR containing the pinned dependency, threat model, permissions, configuration schema, tests, costs, operational owner and uninstall/rollback procedure. Do not auto-merge.
8. **Production proof:** Report separate statuses: DISCOVERED, REVIEWED, SANDBOX_TESTED, APPROVED, INSTALLED, INTEGRATED, DEPLOYED, PRODUCTION_VERIFIED. Never infer a later status from an earlier one.

## Non-negotiable boundaries

- No secrets, access tokens, private environment files, customer data, or personal media in prompts, issue text, artifacts or logs.
- Do not execute code from untrusted pull requests on a privileged self-hosted runner. Use GitHub-hosted or disposable isolated runners for untrusted checks.
- A self-hosted runner must be dedicated, least-privileged, patched, monitored, and restricted to trusted branches/workflows. No public PR-triggered jobs on that runner.
- No production deployment, public publishing, financial action, account/permission change, destructive sync, failover, or DR write without the corresponding verified authorization gate.
- Preserve ops/jarvis/jarvis.env: never fetch, print, copy into artifacts, or log its contents. The DR protected-path exception remains in force.
- Zero RPO and zero RTO are objectives, not established facts. Record measured recovery-point and recovery-time results from controlled drills.
- Do not claim a repository is installed or operational merely because it is listed here or a CI job is green.

## Current integration blockers to resolve

1. The connected GitHub integration lists the primary repository Vyomaraj1356/Vyomarajai; the configured DR repository deepakGoyal1356/Vyomaraj-Agent-6d64e is not readable through the current connection. A 404 is not proof that it does not exist.
2. The repository's LLM harness is documented as provider-neutral and no-tools; provider configuration, agent tool permissions, and production orchestration must be separately verified.
3. Local Windows runner installation/registration and machine-level dependency installation require authorized local execution; this catalog cannot perform those actions by itself.
4. Render/public-preview health and deployed commit need live verification; a deployment record is not an end-to-end readiness proof.
5. Vyomaraj↔Jarvis authenticated heartbeat, real-time DR write/read-back, and recovery/failover drills remain separate acceptance gates.

## Suggested implementation sequence

- **Stage A — inventory:** Reconcile repository manifests, current dependencies, workflows, provider configuration, deploy targets and open P0/P1 issues.
- **Stage B — baseline security:** Add/verify secret scanning, dependency review, pinned CI actions, least-privilege permissions and safe artifact handling.
- **Stage C — evaluation sandbox:** Compare agent frameworks and workflow engines without production credentials; select only after tests and threat-model review.
- **Stage D — observability:** Add structured redacted health/queue/job/DR signals and actionable alerts, without collecting prompts or secrets by default.
- **Stage E — integration:** Add one approved adapter at a time behind feature flags and dry-run mode; verify idempotency, rollback and audit events.
- **Stage F — release/recovery:** Verify deployed commit, runtime smoke tests, read-after-write evidence and controlled recovery. Keep DR writes blocked until the current authorization/evidence gate is satisfied.

## Research links

These are direct upstream repository links, not endorsements or proof of security:
- Microsoft Agent Framework: https://github.com/microsoft/agent-framework
- LangGraph: https://github.com/langchain-ai/langgraph
- n8n: https://github.com/n8n-io/n8n
- Haystack: https://github.com/deepset-ai/haystack
- Dify: https://github.com/langgenius/dify
- OpenTelemetry Collector: https://github.com/open-telemetry/opentelemetry-collector
- Trivy: https://github.com/aquasecurity/trivy
- Gitleaks: https://github.com/gitleaks/gitleaks
- Cosign: https://github.com/sigstore/cosign
- LiteLLM: https://github.com/BerriAI/litellm
- Ragas: https://github.com/explodinggradients/ragas