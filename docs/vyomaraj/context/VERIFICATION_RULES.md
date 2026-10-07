# Verification rules

These rules classify evidence; a status applies only to the exact scope and time stated.

## Status vocabulary

| Status | Meaning | Minimum evidence |
|---|---|---|
| `PRESENT` | A file, configuration entry, or artifact exists. | Read-only repository inspection. |
| `CONFIGURED` | Configuration expresses a target setting. | Parse/validate the configuration; this is not a runtime claim. |
| `IMPLEMENTED_LOCAL` | Local code performs a bounded operation. | Code inspection plus tests for its actual behavior and negative cases. |
| `TESTED_LOCAL` | A local suite passed for a stated revision and scope. | Captured command, exit code, and test results. |
| `CONNECTED` | An authenticated integration successfully exchanged data with the named service. | Live authenticated request/response evidence, permissions, time, and target identity; no secret values in the report. |
| `VERIFIED_RUNTIME` | The relevant end-to-end behavior ran in the intended runtime. | Reproducible runtime trace, actor/authorization decision, state before/after, audit record, and failure-path evidence. |
| `PRODUCTION_APPROVED` | The owner explicitly authorized production use after required gates passed. | Separate owner approval plus production deployment and rollback evidence. |
| `BLOCKED` | A required dependency, permission, identity, test, or approval is unavailable. | Name the missing prerequisite; do not infer success from absence of an error. |
| `NOT_VERIFIED` | Evidence is missing, stale, inaccessible, or outside the inspection scope. | State exactly what was and was not checked. |

## Hard rules

- Documentation, configuration, provider names, keys, commits, CI, or a green preview do **not** prove a runtime connection or production capability.
- A Git replication match does not prove database/application replication, runtime equality, failover, RPO, RTO, or restoration.
- A local resolver or test proves only its local scope. Do not label capability inheritance as live unless the trusted runtime loads and enforces the shared reference for all applicable entities.
- Every runtime claim must name its identity, target, time, authorization, operation, evidence, and limitations. Never print secret values or request them in chat.
- Forecast, scenario, and speculation must be visibly distinguished from facts and current verified state.
- Future-layer claims must never use `FACT`, `HISTORICAL_RECORD`, `CURRENT_VERIFIED_STATE`, or `TREND` as their evidence class.
- Missing evidence is `UNKNOWN_UNVERIFIED` or `BLOCKED`, not a presumed pass.
- Version reconciliation is not a gate for this task. Preserve source and history; never force a destructive alignment.
- No restart, failover, failback, publish, spend, deploy, destructive operation, or registry mutation without the exact owner-authenticated transaction and required step-up approval.
