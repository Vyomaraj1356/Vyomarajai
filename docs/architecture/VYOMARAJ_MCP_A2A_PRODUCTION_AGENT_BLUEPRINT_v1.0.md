# VYOMARAJ / JARVIS — MCP + A2A + PRODUCTION AGENT BLUEPRINT

## Decision

MCP is the standard integration layer for agent-to-tool/resource/prompt connections. A2A is the agent-to-agent collaboration layer. The official A2A documentation explicitly describes them as complementary. 

## Repository finding

The repository already declares MCP and A2A dependencies and has an MCP registry/security-perimeter concept. However, the existing experience orchestrator is plan-only: media adapters have no provider and execution is disabled. Therefore MCP/A2A were NOT yet production-deployed.

## Autonomous creative director

Vyomaraj/Jarvis now have a defined autonomous decision contract:

BRIEF -> KNOWLEDGE/PROVENANCE -> CLASSIFY -> SELECT AGENT -> SELECT CHARACTER/VOICE/STYLE -> SELECT TOOLCHAIN -> BUILD PROMPT -> SCRIPT -> STORYBOARD -> GENERATE -> EDIT -> VOICEOVER -> AUDIO MIX -> CAPTIONS -> FACT/QUALITY/SAFETY/RIGHTS QA -> KUBER COST -> OWNER PUBLISH POLICY -> PUBLISH -> ANALYZE -> LEARN

Within approved policy they can independently choose:
- specialist agent and sub-agent
- model/provider
- MCP tools
- A2A delegation
- format and platform version
- character
- voice
- tone
- language
- animation level
- editing style
- presentation structure
- thumbnail
- captions/subtitles
- retries and non-destructive revisions

## Character and voice rules

Characters are versioned synthetic creative identities with character/visual/voice bibles. The system selects an existing approved identity first; if none fits, it may propose/create a new synthetic identity subject to uniqueness, rights and policy checks.

Voice selection considers language, tone, domain, audience and platform. Voice cloning or real-person likeness requires owner approval. The system must never silently imitate an unapproved real person.

## MCP production lifecycle

DISCOVER -> REGISTER -> SECURITY REVIEW -> SCHEMA VALIDATE -> SANDBOX -> COST/RISK CHECK -> OWNER APPROVAL -> CANARY -> OBSERVE -> PROMOTE

MCP servers cannot receive root, owner, memory, registry or Kuber authority merely because a tool is exposed.

## A2A production lifecycle

DISCOVER AGENT CARD -> AUTHENTICATE -> AUTHORIZE -> SIGN TASK -> DELEGATE -> EXECUTE -> VERIFY ARTIFACT -> RECONCILE -> AUDIT

A2A results remain untrusted until Harness validation.

## Production-ready agent

An agent is not production-ready because a Python class, prompt or registry entry exists. It needs identity, role, capability contract, prompt contract, memory policy, MCP/A2A contracts, authentication, authorization, sandbox, timeout, retry, idempotency, durable execution, observability, audit, evaluation, cost control, failure recovery, deployment manifest, rollback and owner gate.

## Provider-neutral media

Image, video, audio, TTS/voice, editing, compositing, 3D, animation, rendering and interactive/AR capabilities remain adapter-based. The router chooses by capability, quality, latency, cost, rights, availability, language and policy.

External credentials, running servers and production infrastructure are runtime prerequisites and cannot be honestly marked deployed from repository metadata alone.
