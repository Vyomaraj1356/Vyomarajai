# VYOMARAJ — FINAL SHARED-CORE ARCHITECTURE

**System:** VYOMARAJ-AI-STUDIO  
**Role:** Central AI Orchestrator + Autonomous Resilience Core  
**Status:** Target architecture / implementation baseline  
**Primary:** Vyomaraj1356/Vyomarajai  
**DR:** deepakGoyal1356/Vyomaraj-Agent-6d64e

## Non-negotiable architecture

Vyomaraj is a **private orchestration and production engine**. Public users receive published creations/output, not the private control plane.

Web, Android and macOS are authenticated owner/operator clients of one shared backend. They do not contain separate Vyomaraj brains.

```
WEB ───────┐
ANDROID ───┼──> SHARED VYOMARAJ API ──> VYOMARAJ CORE
macOS ─────┘                              │
                                         ├── SHRIYANTRA
                                         │   RAG / CAG / MAG / LLM / HARNESS
                                         │
                                         ├── JARVIS / LAXMAN
                                         │   workflow + routing + execution
                                         │
                                         ├── PROVIDER-NEUTRAL AI FABRIC
                                         │   OpenAI / Claude / Gemini / Arena
                                         │   Local / Open Source / Future
                                         │
                                         ├── AGENT FABRIC
                                         │   research / coding / GitHub / content
                                         │   media / social / analytics / automation
                                         │
                                         └── DATA + MEMORY FABRIC
                                             relational / vector / object / cache
```

## Resilience

Every critical state class must have a recoverable path:

- AI provider: primary → alternate provider → local/open model
- relational data: primary → replica → verified backup
- vector memory: primary → replica → verified archive
- object storage: primary → secondary → offline/archive backup
- application: active → standby/recovery
- source: primary GitHub → DR GitHub
- workflow state, queues, jobs, memory and audit data must be included in application DR; Git replication alone is not application DR.

**No force-push, blind overwrite, or target-only destructive replication.**

## Clients

All three clients must consume the same API contract and expose the same core capabilities:

- owner authentication/authorization
- conversations and task execution
- agent registry and routing
- memory/knowledge
- content pipeline
- reports and audit
- DR/health status
- settings

The final authentication layer is deliberately deferred:

- Voice: pending integration
- Biometric: pending integration
- Owner passcode: pending configuration

## Public boundary

Public web pages may expose published creations, landing/portfolio material and approved outputs.

They must not expose:

- provider credentials
- internal agent controls
- private memory
- owner permissions
- DR controls
- internal orchestration endpoints
- private audit records

## Existing-repository truth

The 2026-10-06 market-readiness audit states that the current checkout has real static Pages delivery and a working local rehearsal stack, but **does not yet have live external AI-provider calls, production database service, social publishing, payments or analytics**. This architecture therefore defines the implementation target; it must not be represented as already deployed.

## Build order

1. Preserve existing content, reports, DR evidence and handover history.
2. Introduce the shared API contract/core boundary.
3. Move existing deterministic capabilities behind that contract.
4. Add provider adapters without provider lock-in.
5. Add persistent data/memory services and tested backups.
6. Build Web, Android and macOS clients against the same contract.
7. Wire owner authentication.
8. Add voice + biometric + passcode last.
9. Run integration, security, backup/restore, failover/failback and read-after-write tests.
10. Only then mark production readiness.
