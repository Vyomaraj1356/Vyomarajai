# Configuration and Session Recovery Audit — 2026-10-18

## Purpose and scope

Read-only inspection of the current Primary repository and historical Arena branch to identify preserved project records, configuration gaps, and candidate assets for safe recovery. This report does not certify the user's complete ChatGPT account history, private provider sessions, or the current DR repository.

## Findings and evidence

### Present on current `main`

- `config/ai/PROMPT_REGISTRY_V1.json` — versioned prompt registry; its current content indicates provider configuration is still required. Registry presence is not evidence that every preset is connected to a live provider.
- `config/ai/PRODUCTION_AGENT_TOOL_REGISTRY_v1.0.yaml` — canonical tool registry.
- `ops/vyomaraj-core/handover/ARENA_SESSION_RECOVERY_INDEX_2026_10_06.md` and `ARENA_SESSION_RECOVERY_MANIFEST_2026_10_06.json` — recovery records describing 12 historical Arena branches and 42 archives at the time of the inventory.
- `Vyomaraj-All-Chats-Database-One-Month.md` — consolidated chat index/record. The recovery index notes a heading/body count discrepancy (28 vs. 34 entries); preserve it unchanged until reconciled.
- `ops/vyomaraj-core/handover/HANDOVER_ARCHIVE_INDEX_V16_7_24.json`, `AGENT_CONTENT_REGISTRY_V16_7_24.json`, `ops/vyomaraj-core/experience/CONTENT_CATALOG.json`, `ops/vyomaraj-core/experience/orchestrator.py`, and `ops/integration/vyomaraj-jarvis-arena-recovery.py`.
- Selected copies of the experience orchestrator, content catalog, V16.7.24 agent registry, archive index, recovery script, and setup script were byte-identical by Git blob SHA on `main` and `arena/01a0f634-vyomarajai`.

### Known gaps or differences

- Raw per-chat transcripts were not recovered by the repository's documented export attempt. This is a repository evidence gap, not proof that ChatGPT account history was deleted.
- `ops/jarvis/jarvis.env` is absent from current Primary `main`. Commit `702f9b0015a29ca9a9ddc2acbd303a697852ba53` deliberately removed the tracked legacy environment file and added it to `.gitignore`. Do not restore historical secret-bearing contents blindly.
- The intended DR repository's protected copy of `ops/jarvis/jarvis.env` could not be verified through the available GitHub connection. No DR write was attempted by this audit.
- `ops/jarvis/llm_harness.py` and `ops/jarvis/test_llm_harness.py` differ between `main` and `arena/01a0f634-vyomarajai`. Keep current `main` authoritative pending code-level review; do not replace it wholesale.
- `experience-studio.html` exists on `arena/01a0f634-vyomarajai` but not at that path on `main`. It is a candidate for review, not an automatic restore.
- The recovery index lists the V16.7.23 and V16.7.24 handover ZIPs in historical material, but the current-main content lookup did not find those root-level paths. The available text-file reader cannot decode the binary ZIP contents. Archive integrity and contents therefore remain unverified.
- The Arena branch `arena/01a0f634-vyomarajai` is substantially diverged from current `main` (44 commits ahead, 245 behind at comparison time). Do not merge the branch wholesale; inspect unique artifacts individually.
- This audit does not establish current live-provider acceptance, runtime persistence, DR write/read-back, recovery/failover, or production readiness.

## Follow-up verification — read-only DR probe

A subsequent read-only CI probe completed successfully on 2026-10-18 (workflow run #285; job `dr-read-only-diagnostic`). This supersedes the earlier access limitation above for repository readability only:

- Primary and secondary repository refs were readable; secondary `main` commit: `81057ea4d86f079e5e4662d0874a4d4e12dc4c92`; secondary tree: `5e7465c2a7319a8baf48f8ec9b163de7bb3010c8`.
- Inventory: 621 primary files vs. 622 secondary files; 0 primary files missing on secondary; 1 secondary-only path; 0 changed content/mode paths.
- The 54-file package comparison matched exactly (54/54).
- Probe flags: `writes=NONE`, `write_permission=UNVERIFIED`, `installed_environment_verified=false`. The probe did not verify the protected environment file's contents or installed runtime, and it did not authorize a write.
- Candidate-set comparison reports 1 candidate missing and 1 secondary-only path; inspect that path before deciding whether it is an approved exception or drift. Exact tree equality is not established and must not be claimed.

This read-only evidence improves repository access confidence but does not satisfy Policy B's protected-path validation, write authorization, read-after-write, or recovery-drill gates.

## Safe recovery rules

1. Preserve current `main` as the working baseline; do not force-merge a stale/diverged branch.
2. Compare candidate files individually, with provenance and tests; use canonical IDs and avoid duplicate entries.
3. Never print, commit, or copy secret values from historical `jarvis.env` into portable files or this report. Reconfigure credentials through an approved secret manager/environment instead.
4. Respect Policy B for DR: preserve the protected DR-only `ops/jarvis/jarvis.env`; do not write to DR until the exception, target identity, and explicit write authorization are validated. Do not claim exact tree equality while the protected path differs.
5. Treat missing original chat transcripts as unrecovered unless obtained from an authorized original source. Do not fabricate chat content from summaries.
6. Make future recovery changes in a dedicated branch/PR with tests and explicit acceptance evidence. No merge, production deploy, traffic switch, or DR write is authorized by this report.

## Recommended next sequence

1. Independently verify the intended DR repository identity and read access.
2. Locate and checksum the historical ZIPs through a binary-capable, authorized path; list archive members without extracting secrets.
3. Review the historical `experience-studio.html` and the harness/test diffs; selectively port only confirmed missing functionality.
4. Reconcile the consolidated chat record's 28/34 discrepancy and label summary-derived records separately from raw transcripts.
5. Validate the protected-path exception and explicit DR write authorization before any DR write; then require read-after-write, integrity, and a documented recovery rehearsal.
6. Run CI and live provider/runtime checks before making any production-readiness claim.

## Change record

- This audit is documentation only.
- No existing file was overwritten.
- No secrets were exposed or restored.
- No DR write, merge to `main`, deployment, or traffic switch was performed.
