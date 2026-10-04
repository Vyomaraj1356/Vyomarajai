# ShriYantra + Arena Integration Package

## Included
- `docs/architecture/shriyantra-rag-cag-mag-arena.md`: shared architecture and safety contract.
- `config/intelligence/shriyantra-rag-cag-mag.yaml`: cascading RAG/CAG/MAG and resilience configuration.
- `config/agents/shriyantra-agent-registry.json`: shared services, peer heads, agent families and domain mesh.
- `ops/shriyantra/shriyantra-arena.py`: runnable safe reference CLI for health, checkpoints and task-envelope generation.

## Run locally

Dry-run and health checks:
```bash
python -m pip install -r ops/shriyantra/requirements.txt
python ops/shriyantra/shriyantra-arena.py init
python ops/shriyantra/shriyantra-arena.py health
python ops/shriyantra/shriyantra-arena.py task --task "Audit repository health" --head BHARATH
python -m unittest tests.test_owner_guard -v
```

Windows launcher:
```bat
ops\shriyantra\run-arena-safe.bat init
ops\shriyantra\run-arena-safe.bat health
ops\shriyantra\run-arena-safe.bat task --task "Audit repository health" --head BHARATH
```

Task-envelope generation is dry-run by default. **Actual execution remains blocked unless all controls below are configured.** The reference runner does not claim RAG/vector storage, persistent memory, model providers or Arena are already connected.

### Owner-gated execution setup

The trusted ShriYantra control plane must issue a short-lived EdDSA-signed JWT approval. The signing private key stays in the control plane and must never be copied to Arena, an agent, a developer machine, or this repository. Configure these environment variables in the secured execution environment (never commit their values):
- `VYOMARAJ_AUTH_PUBLIC_KEY`: path to the trusted Ed25519 public key PEM.
- `VYOMARAJ_OWNER_SUBJECT`: immutable owner identity from the identity provider.
- `VYOMARAJ_AUTH_ISSUER` and `VYOMARAJ_AUTH_AUDIENCE`: exact trusted issuer and audience.
- `VYOMARAJ_SECURITY_EPOCH`: current revocation/security epoch; increment it when invalidating outstanding approvals.
- `VYOMARAJ_AUTHZ_REPLAY_DIR`: persistent shared directory with atomic create semantics to prevent approval reuse across workers.
- `VYOMARAJ_AUTHZ_TOKEN`: short-lived, exact-action approval token injected securely by the control plane; never print or log it.
- `VYOMARAJ_ARENA_ADAPTER` and `VYOMARAJ_ARENA_ADAPTER_SHA256`: reviewed adapter path and its pinned SHA-256 digest.

Approval claims must include `sub`, `iss`, `aud`, `iat`, `exp`, unique `jti`, exact `action=arena.execute`, the SHA-256 target hash for the exact task/head/risk tuple, `scope` containing `arena.execute`, current `security_epoch`, `authn=webauthn` or `passkey`, and `step_up=true` for HIGH risk. The runner consumes the `jti` once. A per-machine replay directory is not sufficient for a multi-worker deployment; use shared atomic storage or a central consume-once API.

The reviewed adapter receives one JSON envelope on stdin via `--envelope-stdin`, without a shell. It must return one JSON object on stdout containing an allowed `status`, the matching `task_id`, and matching `checkpoint_id`. Non-zero exit, timeout, invalid schema, mismatched IDs or adapter digest mismatch fail closed. Review and test the adapter in a sandbox before pinning it. These controls are a reference enforcement layer, not a substitute for production identity-provider integration, protected branch rules, least-privilege runtime isolation, monitoring, and recovery testing.

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
