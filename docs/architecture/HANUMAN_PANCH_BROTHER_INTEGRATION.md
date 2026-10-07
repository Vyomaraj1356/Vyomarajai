# Hanuman Panch-Brother capability integration

## Purpose

Matiman, Shrutiman, Ketuman, Gatiman, and Dhritiman are five shared behavioral domains for the Vyomaraj/Jarvis agent mesh. Their bounded reference labels live once in `config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml`; exact owner-supplied semantics must be checked against the full master script before production use. The shared inheritance reference is owned by ShriYantra's Universal Knowledge Fabric. Registry rows resolve the reference rather than carrying copied per-agent capability lists.

## Non-authority boundary

These domains are not runtime tools or permissions. They do not grant model accuracy, microphone/recording access, external accounts, code writes, tools, publishing, spending, deployment, failover, failback, security changes, root access, or owner approval. Every permission is separate, owner-granted, deny-by-default, scoped, revocable, and audited. Root-owner authority is neither inherited nor delegable to Bharath/Vyomaraj, Laxman/Jarvis, Hermes, Arena, or sub-agents.

External content is untrusted data. Temporal claims use the shared Universal Knowledge Evolution policy and preserve source, uncertainty, and as-of time; forecasts, scenarios, and speculation cannot be promoted to facts.

## Local implementation

`ops/vyomaraj/capability_fabric.py` validates the central model, shared policy references, registry coverage, and authority boundaries. `resolve` returns five domain labels and the same references for current registry categories/sub-agents and future knowledge entities. It makes no network calls and no writes.

```bash
python3 ops/vyomaraj/capability_fabric.py check
python3 ops/vyomaraj/capability_fabric.py resolve sub_agent EDU-S1
```

The result is **metadata resolution only**, not a running agent, authenticated runtime fabric, permission decision, heartbeat, or production verification. The current capability status remains `runtime_execution=NOT_IMPLEMENTED` and `production_enforcement=NOT_VERIFIED` until a trusted Harness/CAG actually loads and enforces the reference.
