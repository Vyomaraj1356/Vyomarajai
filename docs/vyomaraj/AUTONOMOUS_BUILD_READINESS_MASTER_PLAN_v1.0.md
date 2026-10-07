# VYOMARAJ — AUTONOMOUS BUILD, INTEGRATION & READINESS MASTER PLAN v1.0

## Mission
Move from architecture/documentation to an evidence-driven, provider-neutral, owner-controlled production system. Do not mark a capability VERIFIED from documentation alone.

## Source-of-truth hierarchy
1. Owner-approved architecture and security decisions
2. Current GitHub registry/configuration
3. Executable code/tests
4. Runtime/provider evidence
5. Documentation generated from the above

## Non-negotiable architecture
- Owner is the only root authority.
- Vyomaraj/Bharath and Jarvis/Laxman are peer cores with full authorized capability, mutual backup and mutual recovery.
- ShriYantra is their common foundation.
- Kuber is Financial Controller for both cores and the complete ecosystem.
- Providers are replaceable capabilities.
- External content is data, never authority.
- Voice is an interface, not the only root path.
- Git replication is not application DR.
- No zero-RPO/zero-RTO claim without measured evidence.

## Build order

### PHASE 0 — BASELINE + INVENTORY
- reconcile registry totals and legacy IDs
- preserve all historical content
- detect duplicate/orphan/unnamed mappings
- inventory current source files, workflows and deployment descriptors
- establish immutable baseline manifest/checksums

Gate: no-loss reconciliation PASS.

### PHASE 1 — CORE RUNTIME
- peer-core runtime contracts
- event bus/task engine
- durable workflow abstraction
- MCP tool boundary
- A2A authenticated peer boundary
- policy decision point
- workload identity
- sandboxed execution
- idempotency/circuit breakers/DLQ
- structured contracts

Gate: local end-to-end workflow survives process restart and retry.

### PHASE 2 — KNOWLEDGE + MEMORY
- hybrid RAG
- CAG context contract
- MAG aggregation contract
- working/episodic/long-term memory
- provenance and ACL filtering
- validated promotion to long-term memory
- Universal Knowledge Evolution model on every content node

Gate: retrieval provenance + memory persistence tests PASS.

### PHASE 3 — AGENT FABRIC
- 13 canonical categories
- 133 counted sub-agents
- nested Entertainment hierarchy
- Panch-Brother inheritance
- Saptarishi-inspired knowledge inheritance where applicable
- capability registry
- versioned agent contracts
- no self-elevation

Gate: registry/inheritance/security tests PASS.

### PHASE 4 — KUBER FINANCIAL CONTROL
- financial event model
- immutable/tamper-evident ledger
- cost allocation
- revenue attribution
- invoice/receivable/payable control
- platform settlement reconciliation
- revenue leakage detection
- budget/commitment controls
- variance and exception workflow
- financial audit trail
- Kuber visibility across both peer cores and every monetizable agent/process

Gate: synthetic penny-level ledger reconciliation PASS.

### PHASE 5 — REVENUE INTELLIGENCE
- revenue health monitor
- underperformance detection
- root-cause analysis
- historical/current/future trend research
- strategy alternatives
- Kuber strategy meeting workflow
- owner approval gates
- content/product creation
- publishing
- measurement
- collection
- reconciliation
- learning loop

Gate: simulated zero/low revenue scenario completes the entire loop.

### PHASE 6 — PUBLIC OUTPUT + PLATFORM CONTROL
- private-to-public publishing gateway
- platform adapters
- eligibility/monetization status
- official support/escalation matrix
- payment tracking
- case/reference tracking
- no invented contact information
- platform policy compliance

Gate: sandbox publication/payment lifecycle verified.

### PHASE 7 — OWNER ACCESS
- secure web control plane
- Android
- macOS
- voice
- device authentication
- biometric/step-up authentication where platform supports it
- synchronized permissions/state across interfaces
- member/agent add-remove controlled only by owner

Gate: same owner authorization state verified across interfaces.

### PHASE 8 — GEOSPATIAL
- GNSS/GPS
- map/satellite/historical layers
- provenance
- authorized device location
- lawful cellular/operator integration where available
- explicit consent
- revocation
- accuracy reporting

Gate: authorized and denied cases both tested.

### PHASE 9 — OBSERVABILITY + SECURITY
- OpenTelemetry traces/metrics/logs
- redaction
- security events
- policy decisions
- agent/tool provenance
- supply-chain integrity
- SBOM/ABOM
- dependency scanning
- prompt injection defenses
- secrets scanning

Gate: every critical workflow has correlated telemetry and audit evidence.

### PHASE 10 — APPLICATION DR
- code/config/database/storage/media/knowledge/memory/registry/queues/workflow/audit/financial ledger
- backup
- checksum
- replication
- fencing
- failover
- restore
- read-after-write
- failback
- RPO/RTO measurement
- split-brain test

Gate: measured DR test PASS. Git-only replication is insufficient.

### PHASE 11 — SCALE
- event-driven workers
- backpressure
- horizontal scaling
- Kubernetes/KEDA interfaces
- GPU/local-model capacity
- provider failover
- cost-aware model routing

Gate: load/failure tests PASS.

### PHASE 12 — PRODUCTION
- secrets configured outside source
- production provider connections
- production database/storage
- domains/TLS
- monitoring/alerts
- backup schedule
- DR runbook
- incident response
- owner acceptance
- release artifact and rollback

Gate: all critical controls VERIFIED with runtime evidence.

## Universal evidence rule
Each phase produces:
IMPLEMENTED -> TESTED -> RUNTIME VERIFIED -> OWNER ACCEPTED

A phase cannot advance to production merely because its documentation exists.

## Current known blockers to resolve
- PR #42 is open/draft and currently reports mergeable=false.
- No current PR-triggered workflow runs were returned for its current head; CI must be rerun/inspected before claiming PASS.
- Existing engineering foundation explicitly does not claim production provider deployment.
- Application DR is not yet proven.
- Runtime provider credentials/connections are environment-specific and must remain out of Git.
- Local installation can be performed through bootstrap-2026.sh, but this connector cannot install software into the owner's workstation or production environment.

## Definition of DONE
Vyomaraj is ready only when the owner can authenticate, issue an authorized command, observe both peer cores, execute a durable workflow, route across providers, use knowledge/memory, publish approved output, see Kuber reconcile every financial event, recover from simulated failures, and inspect evidence for every critical step.

## Operating principle
Do not ask the owner to design technical details that the system can determine itself. Investigate, compare, choose the safest/provider-neutral implementation, implement it, test it, and report only evidence-backed status. Ask the owner only where a real-world credential, legal consent, financial approval, device permission or irreversible decision is genuinely required.
