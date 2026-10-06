# GO-LIVE GAPS, PLATFORM CHOICE, AND MOVING THE WORK

Written 2026-10-06 13:44 UTC. Every number below was computed from this repository at that moment; nothing is
recalled from a chat. Verify any line with the commands in section 7.

## 1 · The short answer to the three questions

**"Are we ready to go live?"** Ready to be *shown* and *handed over*, yes: the site is live, the
privacy guard and recovery checks are permanent parts of the gate, and the work of every session is
on GitHub. The gate's receipt is `TEST_EVIDENCE_2026_10_04.json`; run it (section 7) for the current
result rather than reading a number frozen into this document. Ready to *operate
itself*, no — the assistant/agent layer is records and documentation, not running services (section
3). That is the honest line between "the shell is finished" and "the machine runs".

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

- The public site, served by GitHub Pages from this branch root: product, lanes, reports, studios.
- Four local servers (viewer, two lane studios, availability gateway) plus the product page, in the
  sandbox, each serving the reports and downloads byte-identical to their source files.
- The DR path: file replication driven by GitHub Actions, with the replication gate enforcing it.
- The report chain: gate receipt, configuration report, platform check, issue ledger, DR sync
  report, AI handoff pack, runbook, and the Arena session recovery index.
- A privacy guard that fails the build if a personal email or phone number returns to any tracked
  file. Since the repository root is a public web page, that guard is a go-live requirement, not a
  nicety.

## 3 · What is still missing before go-live — measured, in priority order

1. **Nobody has to log in.** There is no owner authentication in front of the studios, the agent
   records or the lane endpoints. Anything exposed publicly right now is reachable by anyone with
   the URL. Go-live of interactive surfaces needs auth first. *Owner decision + implementation.*
2. **The agent layer does not run.** Agent network = registry records (13 primary, 128 sub-agents,
   6 listening, 421 inherited); 0 running. Jarvis voice/heartbeat = records plus browser voice.
   Intelligence adapters are `metadata_only`; `switchPlatform` is BLOCKED. RAG, CAG and MAG are
   NOT_IMPLEMENTED. Arena execution has no adapter, and the heartbeat is the repository pipeline
   only — no runtime monitor. The independent probes the audit asks for (last successful check,
   latency, consecutive failures, replication lag, last verified backup) are not built;
   `/reports/realtime` measures per request, which is weaker than a monitor. *This is the real
   remaining build, and it is deliberately not faked.*
3. **The APK is unsigned** (24,567,022 bytes). It cannot be distributed through a store without
   signing, and store distribution needs a developer account. Separately, 12 phone-shaped byte
   matches inside the binary remain unexplained; an exact search for the known numbers found none.
   Rebuild the APK from clean source and re-scan before it is shipped anywhere.
4. **No social publishing and no revenue gateway is connected.** 0 of each. The earn-capable
   actions in the runbook are the honest starting point: they need accounts, not code.
5. **Personal data is out of the files but still in git history.** The guard protects every future
   commit; history still contains the earlier state. Fixing that means a history rewrite or a
   public/private split, and both are owner decisions with consequences (section 6).
6. **The pull-request backlog is cleared; one issue is not.** #27 and #9 were merged into `main`;
   #2, #4, #7 and #3 were closed as superseded, each after its unique files were recovered into
   `main` first (35 files: the Jarvis LLM harness, the Experience orchestrator, the Hermes health
   probe, the security protocol, and the V16.7.23/V16.7.24 handover archives). Issue #6's
   verification is complete and its closing comment is prepared; the issue record itself lives on
   GitHub, re-read it there rather than trusting this snapshot. Nothing was deleted from any branch.
7. **The DR gateway is a local rehearsal, not independent-site DR.** The real cross-site
   verification stays owner-gated by design.
8. **One address is still unpublished.** Both landing pages now read `[OWNER_EMAIL_REDACTED]`.
   A public site with no public contact is a choice, not a bug — but it is a choice only you can
   make. Same for the mobile numbers.

## 3b · Two questions the audit raised, answered by measurement

**PR #9 (ShriYantra RAG/CAG/MAG and Arena foundation) is safe to integrate, with one extra step.**
Rehearsed on a scratch copy without merging anything: it merges into `main` with no conflicts, its
own 7 tests pass, and the only gate impact is that `build_configuration_report.py` must be
regenerated because a new workflow file appears in its list — after that the gate is green. What it
does *not* do yet is written in its own code: `shriyantra-arena.py` carries TODOs for the retrieval
store (ACLs before returning chunks) and the governed memory store. It is a foundation, not a
running intelligence, and it should be merged as a foundation.

**The DR endpoint is unreachable from the primary's own connection, but the replication is live.**
The recorded target is `deepakGoyal1356/Vyomaraj-Agent-6d64e` — private and under another account, so
an API call from here returns 404. That is expected and is not evidence of breakage. The evidence
that matters: the most recent push to `main` ran the replication job and it succeeded, and the DR
record carries 32 MATCH observations (22 replication writes) ending 2026-10-06. Independent verification still requires the
owner's credentials — the one step no outside audit can perform.

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
| APK | Unsigned and unexplained byte matches | Rebuild from clean source, sign it, then distribute |
| Issue #6 | Only the comment is missing, not the verification | Paste the prepared comment (this connection has no issues write access) or grant it |

## 7 · Verify every claim above

```bash
python3 ops/vyomaraj-core/handover/run_offline_suites.py          # the gate - prints its own totals
python3 ops/vyomaraj-core/handover/sanitize_personal_data.py --check   # privacy guard
python3 ops/vyomaraj-core/handover/build_recovery_index.py --check     # sessions still recoverable
python3 ops/vyomaraj-core/handover/build_go_live_brief.py --check      # this document
gh run list --branch <branch> --limit 5                           # CI state, live
```

If any command disagrees with this document, the command is right and this document is stale.
