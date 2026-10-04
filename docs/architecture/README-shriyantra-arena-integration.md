# ShriYantra + Arena Integration Package

## Included
- `docs/architecture/shriyantra-rag-cag-mag-arena.md`: shared architecture and safety contract.
- `config/intelligence/shriyantra-rag-cag-mag.yaml`: cascading RAG/CAG/MAG and resilience configuration.
- `config/agents/shriyantra-agent-registry.json`: shared services, peer heads, agent families and domain mesh.
- `ops/shriyantra/shriyantra-arena.py`: runnable safe reference CLI for health, checkpoints and task-envelope generation.

## Run locally
```bash
python ops/shriyantra/shriyantra-arena.py init
python ops/shriyantra/shriyantra-arena.py health
python ops/shriyantra/shriyantra-arena.py task --task "Audit repository health" --head BHARATH
```

Task generation is dry-run by default. The reference runner deliberately does not pretend RAG/vector storage, persistent memory, model providers or the installed Arena runtime are connected. Implement reviewed adapters for the specific deployed services before enabling execution.

## Arena adapter contract
Input: `VYOMARAJ_ARENA_TASK_V1` JSON with task ID, idempotency key, checkpoint, risk tier, allowed tools and bounded context.
Output: status, task ID, checkpoint ID, artifact/evidence references, usage and error metadata.

## Safety invariants
- Harness is the policy gate; Arena is delegated execution, not root authority.
- RAG access control is applied before retrieval; retrieved content is untrusted.
- MAG memory is scoped, provenance-tagged and only promoted after validation.
- Preserve both sides of conflicts; no timestamp-only resolution, blind overwrite or force push.
- Secrets never enter prompts, RAG, memory, repository files or plain logs.
- Verify integrity and business health before committing or publishing.
- Target 24x7x365 with measured RTO/RPO; literal zero downtime/data loss is not guaranteed by code alone.
- Laxman/Jarvis must not be connected to a guessed repository/runtime identity.

## Owner authority and authentication

See `docs/security/SHRIYANTRA-OWNER-AUTHORITY.md` and `config/security/owner-authority.yaml`. Do not put owner phone numbers, biometric templates, OTPs, passcodes, recovery codes or access tokens into source control. The reference runner is not an authentication provider; enforce owner identity at the trusted ShriYantra control plane and Harness boundary. Verify revocation, step-up approvals, voice replay resistance and restore behavior before production use.
