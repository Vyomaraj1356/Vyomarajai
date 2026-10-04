# Open pull-request triage — 2026-10-04

Purpose: account for every open pull request after this session's merges (#10–#14) without
silently closing anyone's unmerged work. The GitHub connection available in this sandbox has
`issues=read` only, so PR conversations cannot be commented from here (403 on
`/issues/<n>/comments`); dispositions are recorded here instead, and every PR is left open.

SUPERSEDED FOR CURRENT NAVIGATION: see `ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md`
(the generated ledger is the new-session runbook and includes the later #15–#24 merge chain).
This triage note is retained as historical context; its original scope and wording are not silently
rewritten.

## The shared blocker on #2, #3, #4, #7

These four branches have **no merge base with `main`**: `git merge-base origin/main pr<N>` fails
with *"no merge base"*. They were built from a different lineage (an earlier, divergent history),
so GitHub reports `mergeable=UNKNOWN` and merging them would import a parallel history rather
than a patch. Their trees differ from main in 150+ paths, of which **zero are byte-identical on
main** — so they are neither merged nor duplicate; they are an unmergeable separate lineage.

| PR | Head branch | Commits | Paths differing vs main | Distinctive files absent from main |
|----|-------------|---------|--------------------------|-------------------------------------|
| #2 | `security/vyomaraj-security-guard-20261002` | 5 | 155 | 7 — `VYOMARAJ_SECURITY_PROTOCOL.md`, `ops/security/*` (4), `.github/workflows/dr-readiness.yml`, `dr-replication.yml` |
| #3 | `arena/live-preview-reconciled-20261002` | 7 | 171 | 28 — integration/recovery scripts (`ops/integration/*`), chat/commit transcripts, plus the same security and workflow files |
| #4 | `security/active-reconciled-20261002` | 1 | 152 | 7 — same security set as #2 |
| #7 | `feat/bharath-laxman-hermes-ha` | 4 | 151 | 6 — `config/resilience/bharath-laxman-hermes.yaml`, `docs/architecture/bharath-laxman-hermes.md`, `ops/hermes/*` |

Disposition: **left open, unmodified.** If any of that content is wanted on current main (the
security guard from #2/#4 and the Hermes resilience files from #7 are the plausible candidates),
it needs to be re-applied as a fresh commit/PR on top of current main — not merged from these
branches, and not closed before that decision. That decision is the owner's; no file was copied
from them into this session's commits.

## PR #9 — active draft (not this session's)

`feat/shriyantra-rag-cag-mag-arena`, 24 commits, DRAFT, does have merge base `3936bad` (the commit
this session started from), CI currently running under its own workflow. This is another
session's live work: **not touched, not reviewed, not closed.**

## This session's PRs

#10, #11, #12, #13, #14 — all merged after green `diagnostics` + `offline-tests` (+ the
`dr-read-only-diagnostic` job from #12 on), and every resulting main-push sync was verified
(MATCH with identical trees; see `ops/dr/DEPLOYED_MATCH_2026_10_04.json`).
