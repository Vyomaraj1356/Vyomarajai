# Vyomaraj + Jarvis + Arena Recovery Integration

Run ops/integration/run-arena-recovery.bat on Windows or the Python importer directly.

Set ARENA_EXPORT_DIRS to the directory where Arena exposes exported sessions. Multiple directories are separated by semicolons.

The importer discovers repository chat/session/handover evidence, discovers Arena exports when mounted, hashes sources, safely extracts ZIP/TAR without executing members, creates a recovery manifest and canonical handoff, redacts obvious credentials from generated text, and never pushes, merges, deletes or force-updates anything.

GitHub repository access does not equal access to Arena's private session database. If Arena does not export a session, it is marked UNRECOVERED — SOURCE NOT AVAILABLE.

This is intentionally separate from PR #1. Reconcile recovered Arena work against current PRIMARY main before merging.
