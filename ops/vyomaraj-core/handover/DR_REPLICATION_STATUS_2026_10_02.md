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

## Remaining scope — PRIMARY `main` is not resolved

- PRIMARY `main` was last checked at `15aa2fd8a12b8c95e3b3b1f2ae99052ef5c4a23c`. Workflow runs #308 and #309 on `main` failed. No SECONDARY `main` SHA equality was verified in this work.
- The merge conflict was resolved by integrating that fetched `main` history **into the fixed Arena branch only**. PR #1 remains open and unmerged; no push or merge to `main` was made. A fresh Arena workflow run must verify the merge-head SHA after publication.
- Therefore the **Arena ref** can be described as synchronized only at a SHA for which the scoped read-after-write check succeeded. Do not describe PRIMARY/SECONDARY `main` or overall production DR as fully synchronized. Only an authorized maintainer may merge [PR #1](https://github.com/Vyomaraj1356/Vyomarajai/pull/1); after that, require a separate exact read-after-write check on `main` before closing main-to-main scope.

## Follow-up verification

The initial addendum commit `1d8858413cfa724fc3c6835ad548f9685a9e4511` was checked by workflow run #312 ([36978103779](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/36978103779)). The pre-merge Arena tip `0b5d82a36ebf648cbbb151a97c16d7e5c275e7db` then passed the same exact read-after-write check in run #313 ([36978208191](https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/36978208191)). These were documentation-only follow-ups to the code fix, not changes to the replication logic.

Any later commit to the Arena branch requires a fresh successful workflow run for its new SHA. Use the branch's latest Actions run and ref as the authority; do not assume an earlier verified SHA remains the current tip.
