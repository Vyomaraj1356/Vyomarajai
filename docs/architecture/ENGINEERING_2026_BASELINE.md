# Vyomaraj AI Agent OS — 2026 Engineering Baseline

Status: **FOUNDATION_INTEGRATION**

This baseline adds scalable engineering interfaces without replacing the existing Vyomaraj/Bharath ↔ Jarvis/Laxman architecture.

## Installed dependency foundation

The repository now declares bounded Python dependencies for:

- Temporal durable execution
- Model Context Protocol (MCP)
- Agent2Agent (A2A)
- OpenTelemetry
- JSON Schema validation
- YAML configuration
- existing cryptographic owner-authorization support

MCP is the standardized agent-to-tool/data boundary; A2A is the agent-to-agent boundary. Temporal supplies durable workflow execution, while OpenTelemetry supplies vendor-neutral traces, metrics and logs. These are integrated as replaceable implementations behind Vyomaraj interfaces.

## Architecture lock

**Vyomaraj/Bharath ↔ Jarvis/Laxman remain peer cores.**

Both retain full authorized capability. Neither becomes a subordinate backup process. ShriYantra remains the common foundation.

RAG/CAG/MAG remain inside ShriYantra and are shared by both cores.

## Engineering layers added

1. Durable execution — Temporal adapter boundary.
2. MCP — narrow, allowlisted tool/data access.
3. A2A — authenticated peer-agent communication.
4. Workload identity — short-lived credentials and mTLS-ready boundaries.
5. Policy-as-code — deny-by-default decision boundary.
6. OpenTelemetry — end-to-end agent/workflow observability.
7. Agent supply-chain controls — registry, version pinning, hashes and ABOM/SBOM.
8. Sandboxed execution — untrusted tools cannot receive unrestricted host access.
9. Hybrid RAG — semantic + lexical + metadata/ACL retrieval with reranking.
10. Governed memory — working/episodic/long-term tiers with provenance.
11. Event-driven scaling — queues, back-pressure and autoscaling interfaces.
12. DR fencing — epoch/fencing required before core recovery to prevent split-brain.

## Integration rule

No provider, protocol or framework becomes the owner of Vyomaraj.

OpenAI, Anthropic, Gemini, Arena, local models, MCP servers, A2A agents, workflow engines and other runtimes are replaceable capabilities.

## Verification boundary

The CI check proves only:

- dependency manifest is present;
- modules are installable in the CI environment;
- required architecture invariants are present.

It does **not** falsely claim:

- production Temporal is deployed;
- external MCP servers are trusted;
- A2A peers are connected;
- OpenTelemetry collector is deployed;
- SPIFFE/SPIRE is running;
- Kubernetes/KEDA is running;
- provider credentials are configured;
- application DR is complete.

Those require environment-specific integration and runtime evidence.
