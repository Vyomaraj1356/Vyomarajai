# GO-LIVE GAPS, PLATFORM CHOICE, AND MOVING THE WORK

Written 2026-10-07 15:04 UTC. Repository measurements are computed from this checkout; GitHub and Pages facts are
from live read-only queries on 7 October 2026, not assumptions from a chat. Re-read those external
states before acting; verify local lines with the commands in section 7.

### Scoped GitHub metadata re-read — read-only

At `2026-10-07T10:06:21Z`, issue #6 was `OPEN/P0`; PR #39 was `OPEN/DRAFT`, PR #41 `OPEN/non-draft`, and PR #42 `OPEN/DRAFT`. Main remained `04b7ae60` and Pages source `main:/`. No issue, PR, Pages or workflow mutation occurred. Read-only metadata recheck of issue #6, PRs #39/#41/#42, main ref, Pages source metadata, and the latest scheduled workflow run list. No issue/PR/Pages/workflow mutation. Candidate secondary 404s and Actions settings 403s were not re-queried in this narrower follow-up; the full access audit remains timestamped 08:28 UTC.

## 1 · The short answer to the three questions

**"Are we ready to go live?"** The existing `main` Pages site can be shown and handed over, but
this launch-preview branch is **not deployed**. The privacy guard and offline checks are permanent
parts of the gate; they do not provide production authentication or continuous monitoring. A
scheduled Actions run at `2026-10-07T10:13:11Z` reported equal tracked Git trees, but that is not
runtime/app equality, target identity, or failover proof. The gate receipt is
`TEST_EVIDENCE_2026_10_04.json`; run it (section 7) for the current result rather than reading a
number frozen into this document. Ready to *operate itself*, no — the assistant/agent layer is
records and local harnesses, not production services (section 3).

**"Which AI platform should I use?"** Claude Code on a Claude Pro plan ($20/mo (about $17 billed annually)) as the
primary, because Vyomaraj's continuity lives in a repository and that is the tool built for
repository-shaped, many-file work. Codex is the sensible second ($8–$20/mo) for long unattended
runs. Details and alternatives in section 4. The important part is that **the platform is now
interchangeable** — whichever one you pick reads the same repo.

**"Did I lose the 12 sessions?"** No. All 12 session branches are still on GitHub and
42 archives are in the repository; 13 files exist on session branches that main
does not carry. The one thing that is genuinely not recoverable from here is the raw per-chat transcripts —
that lives in Arena's own session history, not in the repo (section 5).

## 2 · What is genuinely live today

- GitHub Pages API read at `2026-10-07T08:28:20Z` reports `built` from `main:/` at `04b7ae60` (latest build `2026-10-07T03:45:29Z`). This feature branch is not deployed; owner review/merge and a successful new Pages build are separate requirements.
- The public web preview remains on `main` until a reviewed merge. Its static demo bundle includes curated local content and a deterministic in-browser planner for Bhakti-Shakti and Roots & Pairings; the session sandbox additionally serves read-only GET `/api/catalog` and ephemeral POST `/api/plan` routes. There are no provider calls, visitor-data persistence, privileged writer routes or owner-authentication claims. The separate local heartbeat snapshot reports `not_checked`; blank example URLs mean no peer was contacted. None proves production AI peers or DR.
- Scheduled Actions run `37605789908` / check `112741170924` completed `2026-10-07T10:13:11Z` with status `MATCH`, `data_match=true`, equal recorded trees `986288ee2cc4ec4d89400320150ea893f7a7a2de` / `986288ee2cc4ec4d89400320150ea893f7a7a2de`, and `traffic_switched=NONE`. Main-push runs `37567565649, 37568236297` recorded automatic snapshot writes. This evidence covers tracked Git only; the Actions variable may override the checked-in fallback. The effective target is `UNCONFIRMED: an Actions variable may override the in-repo fallback and is unreadable here`; current Arena reads see 1 repository, 4 candidate secondary paths return 404 (ambiguous), and Actions variables/secrets reads returned `403 Resource not accessible by integration` / `403 Resource not accessible by integration`. Issue #6 stays OPEN/P0; no audit-session dispatch, comment, merge or deployment occurred.
- The report chain includes the gate receipt, configuration/platform checks, issue ledger, DR sync report, integration-alignment audit, peer architecture/heartbeat plan, AI handoff, runbook and Arena session recovery index.
- A privacy guard that fails the build if a personal email or phone number returns to any tracked
  file. Since the repository root is a public web page, that guard is a go-live requirement, not a
  nicety.

## 3 · What is still missing before go-live — measured, in priority order

1. **Local owner gate is implemented; trusted identity is not configured.** The integrated studio and
   availability gateway now enforce loopback-only binds; privileged writer routes require request-scoped,
   action-bound Ed25519 tokens and the approvals desk persists accepted decisions atomically. No issuer,
   public key, owner subject or security epoch is provisioned, so privileged requests fail closed. The
   sandbox preview exposes only the bounded deterministic read-only planner; it has no privileged API/writer routes. Production still needs owner-provisioned identity,
   key/revocation operations, shared replay protection and a real signed-token rehearsal.
2. **The agent layer does not run as a production service.** The registry records 13 primary, 128
   sub-agent, 6 listening and 421 inherited entries; these are metadata, not live processes.
   Intelligence adapters remain `metadata_only`; `switchPlatform` is BLOCKED and RAG/CAG/MAG are
   NOT_IMPLEMENTED. `ops/jarvis/heartbeat_monitor.py` is a fail-closed, read-only local reachability
   probe; its example peer URLs are blank and its latest summary is `not_checked`. It cannot
   authenticate a peer, prove production health, or trigger a
   shift/failover. The shared peer protocol, replay protection, key rotation, alerting, quorum,
   fencing and production service still need implementation and owner-approved deployment.
3. **Native app release readiness is unverified.** The tracked APK is 24,567,022 bytes and contains
   a v2 signing-block entry (ID `0x7109871a`), but signature validity, signer provenance and real-device
   installation remain unverified. No Android source/build project or macOS/Xcode source/build
   project was found in this checkout. The Android binary also has 12 unexplained phone-shaped byte
   matches (none matches the known exact numbers); verify provenance and re-scan from trusted source
   before distribution. A static web/PWA shell is not a native Android/macOS release.
4. **No social publishing and no revenue gateway is connected.** 0 of each. The earn-capable
   actions in the runbook are the honest starting point: they need accounts, not code.
5. **Personal data is out of the files but still in git history.** The guard protects every future
   commit; history still contains the earlier state. Fixing that means a history rewrite or a
   public/private split, and both are owner decisions with consequences (section 6).
6. **GitHub issue #6 remains OPEN/P0; close-out is not authorized.** The
   read-only audit at `2026-10-07T08:28:20Z` records issue update `2026-10-03T10:38:24Z`, 1
   visible repository, 4 candidate-path 404s (not proof that no private target
   exists), and Actions variables/secrets responses `403 Resource not accessible by integration` / `403 Resource not accessible by integration`.
   The latest scheduled run reports equal tracked trees, but the workflow-selected target name is
   not independently confirmed because the Actions variable may override the checked-in fallback.
   Owner/admin must confirm the effective repository privately, review target-only data, and authorize
   independent read-after-write; runtime/app equality and failover remain unverified. PRs: #41 OPEN/non-draft (updated `2026-10-07T05:15:38Z`;
   Combines DR checkpoint and launch-preview scope; verify-or-sync is skipped for pull requests. Head is based on 8e9a67a while current main is two commits ahead at 04b7ae60; owner review required. No merge or deployment performed.); #39 OPEN/DRAFT (updated `2026-10-06T16:06:13Z`); #42 OPEN/DRAFT (updated
   `2026-10-07T05:14:56Z`). PR #39 was re-read and left untouched. Do not infer replication or deployment
   from checks; no issue close, comment, dispatch, merge, force-push or deployment was performed.
7. **The DR gateway is a local rehearsal, not independent-site DR.** The real cross-site
   verification stays owner-gated by design.
8. **One address is still unpublished.** Both landing pages now read `[OWNER_EMAIL_REDACTED]`.
   A public site with no public contact is a choice, not a bug — but it is a choice only you can
   make. Same for the mobile numbers.

## 3b · 7 October live GitHub and DR read

**PR scope at the live-read timestamp `2026-10-07T08:28:20Z`:** #41 is OPEN/non-draft (updated
`2026-10-07T05:15:38Z`; Combines DR checkpoint and launch-preview scope; verify-or-sync is skipped for pull requests. Head is based on 8e9a67a while current main is two commits ahead at 04b7ae60; owner review required. No merge or deployment performed.); #39 is OPEN/DRAFT (updated `2026-10-06T16:06:13Z`) and #42 is
OPEN/DRAFT (updated `2026-10-07T05:14:56Z`). PR #39 was left untouched. A passing CI run is not
production authorization; the current pull request set remains owner-reviewable.

**A scheduled Git-tree match is recorded; canonical DR target identity remains owner-blocked.**
Run `37605789908` / check `112741170924` completed `2026-10-07T10:13:11Z` with
`status=MATCH`, `data_match=true`, trees `986288ee2cc4ec4d89400320150ea893f7a7a2de` and
`986288ee2cc4ec4d89400320150ea893f7a7a2de`, and `traffic_switched=NONE`. Earlier main-push runs
`37567565649, 37568236297` recorded workflow snapshot writes. The workflow selects Actions variable
`VYOMARAJ_DR_REPO` when configured and otherwise falls back to the checked-in policy; the current
Arena connection lists 1 repository, 4 candidate paths
return 404 (ambiguous), and Actions variables/secrets reads return `403 Resource not accessible by integration` /
`403 Resource not accessible by integration`. Thus the workflow annotation establishes equality for its selected target,
not that target's canonical identity, runtime/app equality, failover, RPO or RTO. No workflow dispatch,
secret change, issue mutation, merge or deployment was performed by this audit. Owner/admin must
confirm the effective target and review target-only data before any further sync, then arrange an
authorized independent read-after-write check; keep issue #6 OPEN/P0 meanwhile.

## 4 · The platform recommendation, and why

The landscape changed in 2026: Google ended free consumer access to Gemini CLI on 18 June 2026 and
replaced it with the closed-source Antigravity CLI; Cursor changed hands; OpenAI's Codex CLI and
Claude Code are the two practical head-to-head options for individual work.

| | Claude Code (recommended primary) | Codex CLI (recommended second) | Antigravity CLI / OpenCode (free paths) |
|---|---|---|---|
| Fits Vyomaraj because | Repository-shaped, many-file work with long sessions — exactly the shape of this project | Long unattended terminal/cloud runs; cheaper per task; publishes its limits | Antigravity has a real free tier; OpenCode is open-source and model-agnostic (BYO key or local) |
| Entry price | Claude Pro $20/mo (about $17 billed annually) | ChatGPT Go $8/mo / Plus $20/mo | Free tier; Google AI Pro $19.99/mo for higher limits |
| Ceiling | Max 5x $100/mo / 20x $200/mo | Pro $100/mo / $200/mo | AI Ultra from $99.99/mo |
| Watch out | Limits are 5-hour + weekly and unpublished; heavy multi-agent runs multiply consumption | Repository reasoning trails on some repo-level benchmarks | Gemini CLI itself is now enterprise/API only |

Practical setup for you: **Claude Pro at $20/mo (about $17 billed annually) is enough to start**, keep Codex on a
$8/mo–$20/mo plan as the overflow/parallel option, and treat the free tiers as
experiments. Whichever you choose, point it at the repository and paste
`AI_PLATFORM_HANDOFF_2026_10_06.md` — it already tells the receiving assistant the nine binding
constraints, the verified-state table, and the rule that it must never emit a status the system
cannot prove.

## 5 · Moving the 12 sessions — recovery, not redoing

The work is not in the chat, it is in Git. Each Arena session pushed its branch, so the sessions
survive as `origin/arena/*`.

```bash
git fetch origin '+refs/heads/arena/*:refs/remotes/origin/arena/*'   # bring every session down
git switch -c recovery/all-sessions                                  # never touch main directly

git diff --name-status main origin/arena/<session-branch>            # what that session has
git checkout origin/arena/<session-branch> -- path/to/file           # bring one file across
```

Then consolidate on the recovery branch: one manifest, one hash per artifact, a review before any
merge. `ARENA_SESSION_RECOVERY_INDEX_2026_10_06.md` lists every session branch with the files that
are unique to it, and `ARENA_SESSION_RECOVERY_MANIFEST_2026_10_06.json` carries the machine-readable
version. The single unrecoverable item — raw per-chat transcripts — can only come from Arena's own session
list; the relational record of every session (what was decided, in order) is in the repository's
chats database and the two chat archives.

## 6 · Decisions that are yours alone

| Decision | Why it matters | Options |
|---|---|---|
| Repository visibility | The repo root is the public website; every tracked file is a page | Keep public + history rewrite to purge old identifiers · split (public showcase repo, private operations repo) · paid plan + private repo (note: Pages from a private repo needs GitHub Pro/Team, and the site stays publicly readable unless Enterprise Cloud, so a private repo alone does not hide the site) |
| Git history | Identifiers removed from files remain in past commits | Rewrite history (recovery branch, force-push rules permitting) or accept that the old snapshot stays readable |
| Public contact | The site currently shows no address | Publish a contact address (a dedicated one, not a personal mailbox) or keep the redaction |
| APK | v2 signing-block entry detected; cryptographic verification, signer provenance, device install and unexplained byte matches remain unresolved | Run `apksigner verify`, confirm provenance, test on a real device; rebuild from trusted source if unresolved |
| Issue #6 (OPEN/P0) | Exact secondary repository and Actions access remain unverified in the `2026-10-07T08:28:20Z` read | Owner/admin confirms the existing target and grants required read/Actions access through GitHub; no secret values should be shared in chat |

## 7 · Verify every claim above

```bash
python3 ops/vyomaraj-core/handover/run_offline_suites.py          # the gate - prints its own totals
python3 ops/vyomaraj-core/handover/sanitize_personal_data.py --check   # privacy guard
python3 ops/vyomaraj-core/handover/build_recovery_index.py --check     # sessions still recoverable
python3 ops/vyomaraj-core/handover/build_go_live_brief.py --check      # this document
gh run list --branch <branch> --limit 5                           # CI state, live
```

If any command disagrees with this document, the command is right and this document is stale.
