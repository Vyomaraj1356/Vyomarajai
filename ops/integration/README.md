# Vyomaraj + Jarvis + Arena Recovery Integration

Run ops/integration/run-arena-recovery.bat on Windows or the Python importer directly.

Set ARENA_EXPORT_DIRS to the directory where Arena exposes exported sessions. Multiple directories are separated by semicolons.

The importer discovers repository chat/session/handover evidence, discovers Arena exports only when a directory is explicitly mounted, hashes sources, and safely extracts ZIP/TAR without executing members. It writes local staging data under `.arena-recovery/` (git-ignored) and never pushes, merges, deletes or force-updates anything. The GitHub workflow uploads reports only, not staged session text.

Uploaded reports use repository-relative names or opaque `ARENA_EXPORT/item-NNNN` labels. They do not include absolute home/runner paths, raw session IDs, chat numbers, credentials, or staged chat contents. SHA-256 values are available to correlate a local export without publishing its filename.

GitHub repository access does not equal access to Arena's private session database. If Arena does not export a session, it is marked UNRECOVERED — SOURCE NOT AVAILABLE. A workflow run without `ARENA_EXPORT_DIRS` can only scan repository evidence; it is not proof that private Arena sessions were recovered.

This is intentionally separate from PR #1. Review the updated PR and reconcile any actually recovered Arena work against current PRIMARY main before an authorized merge.

## Separate LLM harness

The standalone Vyomaraj/Jarvis LLM harness is documented in [`ops/jarvis/LLM_HARNESS.md`](../jarvis/LLM_HARNESS.md). It is not connected to this recovery importer, has no tools or automatic repository actions, and remains disabled until an owner chooses a trusted provider/model and configures local environment variables.
