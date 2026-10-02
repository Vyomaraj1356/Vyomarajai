# DR replication resolution addendum — 2026-10-02

This is a post-archive addendum. It is intentionally **not** added to or substituted for any member of `Vyomaraj-Handover-V16.7.24-v194.zip`; the existing archive and its member set remain unchanged.

## Verified result

- PRIMARY: `Vyomaraj1356/Vyomarajai`
- SECONDARY: `deepakGoyal1356/Vyomaraj-Agent-6d64e` (private)
- Verified ref: `arena/01a0f634-vyomarajai`
- Exact SHA verified by the successful workflow run: `eca273eedce2a91f06a3df324aeafee3e28e1df1`
- Workflow run #311: [36977892814](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/36977892814)
- Commit: `eca273eedce2a91f06a3df324aeafee3e28e1df1` (`fix(dr): archive verified legacy mirror before exact sync`)

The successful run completed **“Verify PRIMARY and push exact commit to SECONDARY.”** That step checks the PRIMARY ref against the triggering commit, writes the triggering branch ref to SECONDARY (plus a preservation archive ref only if guarded reconciliation is needed), reads the triggering ref back, and fails unless its SHA equals the expected PRIMARY SHA. Thus the Arena ref equality above was verified by the workflow, not inferred from a successful push alone.

## What changed and why

1. Run #310 ([36977581318](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/36977581318)) correctly refused the then-existing non-fast-forward SECONDARY ref; it did not force-update the ref.
2. Commit `eca273e` added a guarded recovery for the fixed Arena ref only. For divergent history it requires a synthetic mirror commit whose subject identifies a PRIMARY ancestor, verifies that ancestor is in the source history, and requires the complete Git tree to match that ancestor. It preserves the previous SECONDARY commit on a private archive ref before a lease-protected update. This path is disabled for `main` and all non-`arena/*` refs; any failed precondition refuses the update.
3. The workflow then reads SECONDARY back and verifies exact SHA equality. Its heartbeat is read-only, so later steps do not add a commit or invalidate that check.
4. Local shell syntax and whitespace checks passed before the commit. Only the workflow file was included in `eca273e`; the other pre-existing worktree changes were left untouched.

The Actions log download returned `EOF` through the CLI, so the specific archive ref is not independently recorded in this addendum. The run's success proves the equality check; check the run page's job summary or inspect SECONDARY refs if the precise archive ref must be audited.

## Post-conflict integration — Arena verified; PRIMARY `main` still open

- PRIMARY `main` is currently at `39cda8f38a4f0076f39eac322f4ab070ff3c3dc5`. Runs #308, #309 and latest run #314 ([36978931155](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/36978931155)) failed on `main`; #314 failed in the API workflow's SECONDARY ref-read path before it established equality. No SECONDARY `main` SHA equality was verified.
- Main history through `39cda8f` was merged **into the fixed Arena branch only**. The failed main-side API writer was not selected; Arena's tested exact-Git-ref writer remains. No push or merge to PRIMARY `main` was made.
- The resolved Arena head `d59dbaae5a9d2aee5f2ed227511a944a506348d5` passed the exact read-after-write check in workflow run #315 ([36979617503](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/36979617503)). PR #1 is open, `CLEAN`/`MERGEABLE`, and unmerged. This branch update was a fast-forward from the previously verified Arena SHA; no guarded force recovery was needed.
- Therefore the **Arena ref** is verified only at a SHA with a successful scoped check. Do not describe PRIMARY/SECONDARY `main` or overall production DR as fully synchronized. GitHub Pages still serves `main` at `/`; only an authorized maintainer may merge [PR #1](https://github.com/Vyomaraj1356/Vyomarajai/pull/1), after which `main` needs its own exact read-after-write verification.

## Follow-up verification

The initial addendum commit `1d8858413cfa724fc3c6835ad548f9685a9e4511` was checked by workflow run #312 ([36978103779](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/36978103779)). The pre-merge Arena tip `0b5d82a36ebf648cbbb151a97c16d7e5c275e7db` then passed the same exact read-after-write check in run #313 ([36978208191](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/36978208191)). These were documentation-only follow-ups to the code fix, not changes to the replication logic.

Any later commit to the Arena branch requires a fresh successful workflow run for its new SHA. Use the branch's latest Actions run and ref as the authority; do not assume an earlier verified SHA remains the current tip.
