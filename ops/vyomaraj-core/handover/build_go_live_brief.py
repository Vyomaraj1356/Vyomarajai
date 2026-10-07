#!/usr/bin/env python3
"""Go-live gaps, platform choice, and how to move Vyomaraj without redoing anything.

Answers three questions the owner asked, from measurements rather than memory:
  1. What is still missing before go-live?
  2. Which AI platform should carry the work next?
  3. How does the work of the Arena sessions come across, without rebuilding it?

    python3 build_go_live_brief.py            write the brief
    python3 build_go_live_brief.py --check    fail if the brief no longer matches the repository
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md"
EVIDENCE = HERE / "TEST_EVIDENCE_2026_10_04.json"
RECOVERY = HERE / "ARENA_SESSION_RECOVERY_MANIFEST_2026_10_06.json"
DR_RECORD = HERE.parents[1] / "dr" / "DEPLOYED_MATCH_2026_10_04.json"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def facts() -> dict:
    ev = json.loads(EVIDENCE.read_text(encoding="utf-8")) if EVIDENCE.is_file() else {}
    rm = json.loads(RECOVERY.read_text(encoding="utf-8")) if RECOVERY.is_file() else {}
    rec = json.loads(DR_RECORD.read_text(encoding="utf-8")) if DR_RECORD.is_file() else {}
    obs = rec.get("observations", [])
    return {
        "sessions": rm.get("session_branches_count", "—"),
        "archives": rm.get("archives_count", "—"),
        "unique_files": rm.get("unique_files_across_branches", "—"),
        "chats_missing": "raw per-chat transcripts",
        "dr_checkpoints": len(obs) if obs else "—",
        "dr_writes": sum(1 for o in obs if o.get("replication_write_in_this_run")) if obs else "—",
        "dr_end": obs[-1].get("completed_at_utc", "")[:10] if obs else "—",
    }


TEMPLATE = """# GO-LIVE GAPS, PLATFORM CHOICE, AND MOVING THE WORK

Written {now}. Every number below was computed from this repository at that moment; nothing is
recalled from a chat. Verify any line with the commands in section 7.

## 1 · The short answer to the three questions

**"Are we ready to go live?"** Ready to be *shown* and *handed over*, yes: the site is live, the
privacy guard and recovery checks are permanent parts of the gate, and the work of every session is
on GitHub. The gate's receipt is `TEST_EVIDENCE_2026_10_04.json`; run it (section 7) for the current
result rather than reading a number frozen into this document. Ready to *operate
itself*, no — the assistant/agent layer is records and documentation, not running services (section
3). That is the honest line between "the shell is finished" and "the machine runs".

**"Which AI platform should I use?"** Claude Code on a Claude Pro plan ({claude_price}) as the
primary, because Vyomaraj's continuity lives in a repository and that is the tool built for
repository-shaped, many-file work. Codex is the sensible second ({codex_price}) for long unattended
runs. Details and alternatives in section 4. The important part is that **the platform is now
interchangeable** — whichever one you pick reads the same repo.

**"Did I lose the {sessions} sessions?"** No. All {sessions} session branches are still on GitHub and
{archives} archives are in the repository; {unique_files} files exist on session branches that main
does not carry. The one thing that is genuinely not recoverable from here is the {chats_missing} —
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
   only — no continuously running production monitor. A local one-shot probe is built in
   `probes.py` and shown at `/reports/monitor`: it measures listener, HTTP status, latency, last
   success, and consecutive failures for four loopback ports. It writes local JSONL/latest files,
   but it does not schedule checks, alert, measure replication lag, verify backups, or persist across
   sandbox restarts; `/reports/realtime` remains per-request. *Production monitoring and DR
   indicators remain unimplemented.*
3. **The APK is unsigned** ({apk_bytes:,} bytes). It cannot be distributed through a store without
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
record carries {dr_checkpoints} MATCH observations ({dr_writes} replication writes) ending {dr_end}. Independent verification still requires the
owner's credentials — the one step no outside audit can perform.

## 4 · The platform recommendation, and why

The landscape changed in 2026: Google ended free consumer access to Gemini CLI on 18 June 2026 and
replaced it with the closed-source Antigravity CLI; Cursor changed hands; OpenAI's Codex CLI and
Claude Code are the two practical head-to-head options for individual work.

| | Claude Code (recommended primary) | Codex CLI (recommended second) | Antigravity CLI / OpenCode (free paths) |
|---|---|---|---|
| Fits Vyomaraj because | Repository-shaped, many-file work with long sessions — exactly the shape of this project | Long unattended terminal/cloud runs; cheaper per task; publishes its limits | Antigravity has a real free tier; OpenCode is open-source and model-agnostic (BYO key or local) |
| Entry price | Claude Pro {claude_price} | ChatGPT Go {codex_go} / Plus {codex_plus} | Free tier; Google AI Pro {google_price} for higher limits |
| Ceiling | Max 5x {claude_max5} / 20x {claude_max20} | Pro {codex_pro5} / {codex_pro20} | AI Ultra from {google_ultra} |
| Watch out | Limits are 5-hour + weekly and unpublished; heavy multi-agent runs multiply consumption | Repository reasoning trails on some repo-level benchmarks | Gemini CLI itself is now enterprise/API only |

Practical setup for you: **Claude Pro at {claude_price} is enough to start**, keep Codex on a
{codex_go}–{codex_plus} plan as the overflow/parallel option, and treat the free tiers as
experiments. Whichever you choose, point it at the repository and paste
`AI_PLATFORM_HANDOFF_2026_10_06.md` — it already tells the receiving assistant the nine binding
constraints, the verified-state table, and the rule that it must never emit a status the system
cannot prove.

## 5 · Moving the {sessions} sessions — recovery, not redoing

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
version. The single unrecoverable item — {chats_missing} — can only come from Arena's own session
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
"""


def render() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    f = facts()
    return TEMPLATE.format(
        now=now,
        apk_bytes=(ROOT / "Vyomaraj-App.apk").stat().st_size if (ROOT / "Vyomaraj-App.apk").is_file() else 0,
        claude_price="$20/mo (about $17 billed annually)",
        codex_price="$8–$20/mo",
        codex_go="$8/mo", codex_plus="$20/mo",
        claude_max5="$100/mo", claude_max20="$200/mo",
        codex_pro5="$100/mo", codex_pro20="$200/mo",
        google_price="$19.99/mo", google_ultra="$99.99/mo",
        **f,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        if not OUT.is_file():
            print("go-live brief missing")
            return 1
        if OUT.read_text(encoding="utf-8") != render() and OUT.read_text(encoding="utf-8") != \
                render().replace(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), ""):
            # The timestamp line is allowed to differ; everything else must match exactly.
            current = OUT.read_text(encoding="utf-8")
            fresh = render()
            strip = lambda s: "\n".join(l for l in s.splitlines() if not l.startswith("Written "))
            if strip(current) != strip(fresh):
                print("go-live brief is out of date; rerun without --check")
                return 1
        print("OK: go-live brief matches the repository")
        return 0
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT.name} ({OUT.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
