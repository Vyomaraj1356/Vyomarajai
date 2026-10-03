# Bharath Laxman Hermes Architecture

Bharath (Vyomaraj) and Laxman (Jarvis) are peer autonomous heads. Hermes is the coordination, integrity, recovery and audit layer. Shriyantra is the private control-plane home.

Operating loop: RESEARCH -> REASON -> CREATE -> VERIFY -> PUBLISH -> MEASURE -> EARN -> LEARN -> PROTECT -> RECOVER

```mermaid
flowchart TB
  S[SHRIYANTRA Private Control Plane]
  H[HERMES Protection Coordination Witness]
  B[BHARATH / VYOMARAJ Autonomous Head]
  L[LAXMAN / JARVIS Peer Autonomous Head]
  A[Agent Mesh]
  P[Publishing and Revenue Plane]
  D[Durable State Audit Recovery]
  S --> H
  H <--> B
  H <--> L
  B <--> L
  B --> A
  L --> A
  A --> P
  A <--> D
  H <--> D

```

Safety contract:
- preserve acknowledged valid state on both heads
- fence a failed head before promotion
- never use blind destructive overwrite
- quarantine conflicting state and reconcile by version/event lineage
- keep secrets outside replicated business state
- audit every state transition
- verify integrity before failover and failback

The existing GitHub DR mirror remains a recovery layer. Repository-level Laxman automation must not be activated until the exact Laxman/Jarvis repository is supplied.
