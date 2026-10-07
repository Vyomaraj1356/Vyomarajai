# OWNER-CONTROLLED AGENT CHANGE PROTOCOL v1.0

An owner instruction may add, remove, rename, merge, split, or reorganize agents, sub-agents and content.

## Required transaction

OWNER COMMAND
→ AUTHENTICATE OWNER
→ AUTHORIZE CHANGE
→ SNAPSHOT CURRENT REGISTRY
→ VALIDATE IDENTITY/DEPENDENCIES
→ APPLY CHANGE
→ UPDATE ROUTING/CAPABILITIES/KNOWLEDGE/CONTENT/PROCESS/FINANCE LINKS
→ UPDATE BOTH PEER-CORE STATE
→ REPLICATE TO DR
→ RUN INTEGRITY/REGRESSION CHECKS
→ AUDIT + HASH
→ REPORT BEFORE/AFTER
→ COMPLETE

## Rules

- Owner is the only authority allowed to change the hierarchy.
- Vyomaraj/Bharath and Jarvis/Laxman must both receive the same committed state.
- Every authorized agent/sub-agent inherits the common capability fabric unless policy explicitly restricts a capability.
- Removing an agent normally means ARCHIVED/DEACTIVATED, preserving history, content, IDs, provenance and recovery data.
- Destructive deletion requires explicit owner confirmation and must pass recovery/audit policy.
- A renamed/reorganized agent retains stable identity unless the owner explicitly requests a new identity.
- Content must never become orphaned: mappings are re-pointed, archived, or explicitly marked unresolved.
- Financial mappings and revenue attribution must be recalculated when an affected agent/content path changes.
- Changes must be idempotent and concurrency-safe.
- A partial transaction must roll back or remain visibly RECOVERING; never silently report success.
- External providers are never allowed to mutate the hierarchy directly.

## Voice failure

Voice is only an interface. The same owner command may arrive through authenticated web, Android, macOS or secure recovery. Authority and state remain synchronized.

## Verification

A change is VERIFIED only after registry integrity, capability inheritance, routing, content ownership, peer-state synchronization and DR replication evidence are available.
