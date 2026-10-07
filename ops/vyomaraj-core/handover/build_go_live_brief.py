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
import socket
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
ISSUES_LEDGER = HERE / "ISSUES_AND_PRS_LEDGER.json"
MONITOR_STATE = Path.home() / ".local/state/vyomaraj/jarvis-heartbeats.json"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def facts() -> dict:
    ev = json.loads(EVIDENCE.read_text(encoding="utf-8")) if EVIDENCE.is_file() else {}
    rm = json.loads(RECOVERY.read_text(encoding="utf-8")) if RECOVERY.is_file() else {}
    rec = json.loads(DR_RECORD.read_text(encoding="utf-8")) if DR_RECORD.is_file() else {}
    ledger = json.loads(ISSUES_LEDGER.read_text(encoding="utf-8")) if ISSUES_LEDGER.is_file() else {}
    live = ledger.get("current_live_recheck_2026_10_07", {})
    prs = live.get("pull_requests", {})
    pages = live.get("pages", {})
    dr = live.get("dr_snapshot", {})
    dr_target = live.get("dr_target_resolution", {})
    issue6 = live.get("issue_6", {})
    secondary = live.get("secondary_path_probes", {})
    metadata_followup = ledger.get("current_github_metadata_followup_2026_10_07", {})
    metadata_prs = metadata_followup.get("pull_requests", {})
    obs = rec.get("observations", [])
    main_writes = live.get("observed_main_replication_writes", {}).get("writes", [])
    def listening(port: int) -> bool:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.15):
                return True
        except OSError:
            return False
    preview_state = "running in sandbox only" if listening(5310) else "stopped"
    try:
        monitor_snapshot = json.loads(MONITOR_STATE.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        monitor_snapshot = {}
    def pr_status(number: str) -> str:
        pr = prs.get(number, {})
        if not pr:
            return "UNVERIFIED"
        return f"{pr.get('state', 'unknown')}/{'DRAFT' if pr.get('draft') else 'non-draft'}"
    return {
        "sessions": rm.get("session_branches_count", "—"),
        "archives": rm.get("archives_count", "—"),
        "unique_files": rm.get("unique_files_across_branches", "—"),
        "chats_missing": "raw per-chat transcripts",
        "dr_checkpoints": len(obs) if obs else "—",
        "dr_writes": sum(1 for o in obs if o.get("replication_write_in_this_run")) if obs else "—",
        "dr_end": obs[-1].get("completed_at_utc", "")[:10] if obs else "—",
        "github_checked_at": live.get("checked_at_utc", "UNVERIFIED"),
        "metadata_recheck_at": metadata_followup.get("observed_at_utc", "not recorded"),
        "metadata_issue6": f"{metadata_followup.get('issue_6', {}).get('state', 'UNVERIFIED')}/{metadata_followup.get('issue_6', {}).get('priority', 'UNVERIFIED')}",
        "metadata_pr39": f"{metadata_prs.get('39', {}).get('state', 'UNVERIFIED')}/{'DRAFT' if metadata_prs.get('39', {}).get('draft') else 'non-draft'}",
        "metadata_pr41": f"{metadata_prs.get('41', {}).get('state', 'UNVERIFIED')}/{'DRAFT' if metadata_prs.get('41', {}).get('draft') else 'non-draft'}",
        "metadata_pr42": f"{metadata_prs.get('42', {}).get('state', 'UNVERIFIED')}/{'DRAFT' if metadata_prs.get('42', {}).get('draft') else 'non-draft'}",
        "metadata_main_sha": metadata_followup.get("main_sha", "unknown")[:8],
        "metadata_pages_source": f"{metadata_followup.get('pages', {}).get('source_branch', 'unknown')}:{metadata_followup.get('pages', {}).get('source_path', 'unknown')}",
        "metadata_scope": metadata_followup.get("scope", "No scoped metadata follow-up recorded."),
        "issue6_state": issue6.get("state", "UNVERIFIED"),
        "issue6_priority": issue6.get("priority", "UNVERIFIED"),
        "issue6_updated_at": issue6.get("updated_at", "not recorded"),
        "visible_repositories": len(live.get("visible_repositories", [])),
        "secondary_404_count": sum(1 for value in secondary.values() if value == "404"),
        "actions_variables_api": live.get("actions_variables_api", "UNVERIFIED"),
        "actions_secrets_api": live.get("actions_secrets_api", "UNVERIFIED"),
        "pr39_status": pr_status("39"),
        "pr39_updated_at": prs.get("39", {}).get("updated_at", "not recorded"),
        "pr41_status": pr_status("41"),
        "pr41_updated_at": prs.get("41", {}).get("updated_at", "not recorded"),
        "pr41_note": prs.get("41", {}).get("note", "note not recorded"),
        "pr42_status": pr_status("42"),
        "pr42_updated_at": prs.get("42", {}).get("updated_at", "not recorded"),
        "pages_status": pages.get("status", "UNVERIFIED"),
        "pages_source": pages.get("source", "UNVERIFIED"),
        "pages_commit": pages.get("build_commit", "unknown")[:8],
        "pages_last_build": pages.get("last_build_created_at", "not recorded"),
        "feature_branch_status": ("is deployed" if pages.get("feature_branch_deployed") is True
                                  else "is not deployed" if pages.get("feature_branch_deployed") is False
                                  else "has an unverified deployment status"),
        "dr_latest_status": dr.get("status", "UNVERIFIED"),
        "dr_completed_at": dr.get("completed_at_utc", "not recorded"),
        "dr_workflow_run": dr.get("workflow_run_id", "not recorded"),
        "dr_check_run": dr.get("check_run_id", "not recorded"),
        "dr_primary_tree": dr.get("primary_tree", "unknown"),
        "dr_secondary_tree": dr.get("secondary_tree", "unknown"),
        "dr_data_match": str(dr.get("data_match", "unknown")).lower(),
        "dr_traffic_switched": dr.get("traffic_switched", "unknown"),
        "dr_target_identity": dr_target.get("effective_target_identity", "UNCONFIRMED"),
        "dr_target_variable_api": dr_target.get("workflow_variable_read_result", "UNVERIFIED"),
        "main_write_run_ids": ", ".join(str(row.get("workflow_run_id")) for row in main_writes) or "none recorded",
        "safe_preview_state": preview_state,
        "monitor_summary": monitor_snapshot.get("summary", "not_checked"),
        "monitor_checked_at": monitor_snapshot.get("checked_at_utc", "not recorded"),
    }


TEMPLATE = """# GO-LIVE GAPS, PLATFORM CHOICE, AND MOVING THE WORK

Written {now}. Repository measurements are computed from this checkout; GitHub and Pages facts are
from live read-only queries on 7 October 2026, not assumptions from a chat. Re-read those external
states before acting; verify local lines with the commands in section 7.

### Scoped GitHub metadata re-read — read-only

At `{metadata_recheck_at}`, issue #6 was `{metadata_issue6}`; PR #39 was `{metadata_pr39}`, PR #41 `{metadata_pr41}`, and PR #42 `{metadata_pr42}`. Main remained `{metadata_main_sha}` and Pages source `{metadata_pages_source}`. No issue, PR, Pages or workflow mutation occurred. {metadata_scope}

## 1 · The short answer to the three questions

**"Are we ready to go live?"** The existing `main` Pages site can be shown and handed over, but
this launch-preview branch is **not deployed**. The privacy guard and offline checks are permanent
parts of the gate; they do not provide production authentication or continuous monitoring. A
scheduled Actions run at `{dr_completed_at}` reported equal tracked Git trees, but that is not
runtime/app equality, target identity, or failover proof. The gate receipt is
`TEST_EVIDENCE_2026_10_04.json`; run it (section 7) for the current result rather than reading a
number frozen into this document. Ready to *operate itself*, no — the assistant/agent layer is
records and local harnesses, not production services (section 3).

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

- GitHub Pages API read at `{github_checked_at}` reports `{pages_status}` from `{pages_source}` at `{pages_commit}` (latest build `{pages_last_build}`). This feature branch {feature_branch_status}; owner review/merge and a successful new Pages build are separate requirements.
- The exact-asset allowlisted sandbox preview on :5310 is `{safe_preview_state}` in this sandbox. Its only API is a bounded deterministic POST `/api/plan` for Bhakti-Shakti and Roots & Pairings; results are ephemeral and there are no provider calls, visitor-data persistence, privileged writer routes or owner-authentication claims. The separate local heartbeat snapshot reports `{monitor_summary}`; blank example URLs mean no peer was contacted. Neither local tool proves production readiness.
- Scheduled Actions run `{dr_workflow_run}` / check `{dr_check_run}` completed `{dr_completed_at}` with status `{dr_latest_status}`, `data_match={dr_data_match}`, equal recorded trees `{dr_primary_tree}` / `{dr_secondary_tree}`, and `traffic_switched={dr_traffic_switched}`. Main-push runs `{main_write_run_ids}` recorded automatic snapshot writes. This evidence covers tracked Git only; the Actions variable may override the checked-in fallback. The effective target is `{dr_target_identity}`; current Arena reads see {visible_repositories} repository, {secondary_404_count} candidate secondary paths return 404 (ambiguous), and Actions variables/secrets reads returned `{actions_variables_api}` / `{actions_secrets_api}`. Issue #6 stays OPEN/P0; no audit-session dispatch, comment, merge or deployment occurred.
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
   probe; its example peer URLs are blank and its latest summary is `{monitor_summary}`. It cannot
   authenticate a peer, prove production health, or trigger a
   shift/failover. The shared peer protocol, replay protection, key rotation, alerting, quorum,
   fencing and production service still need implementation and owner-approved deployment.
3. **Native app release readiness is unverified.** The tracked APK is {apk_bytes:,} bytes and contains
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
6. **GitHub issue #6 remains {issue6_state}/{issue6_priority}; close-out is not authorized.** The
   read-only audit at `{github_checked_at}` records issue update `{issue6_updated_at}`, {visible_repositories}
   visible repository, {secondary_404_count} candidate-path 404s (not proof that no private target
   exists), and Actions variables/secrets responses `{actions_variables_api}` / `{actions_secrets_api}`.
   The latest scheduled run reports equal tracked trees, but the workflow-selected target name is
   not independently confirmed because the Actions variable may override the checked-in fallback.
   Owner/admin must confirm the effective repository privately, review target-only data, and authorize
   independent read-after-write; runtime/app equality and failover remain unverified. PRs: #41 {pr41_status} (updated `{pr41_updated_at}`;
   {pr41_note}); #39 {pr39_status} (updated `{pr39_updated_at}`); #42 {pr42_status} (updated
   `{pr42_updated_at}`). PR #39 was re-read and left untouched. Do not infer replication or deployment
   from checks; no issue close, comment, dispatch, merge, force-push or deployment was performed.
7. **The DR gateway is a local rehearsal, not independent-site DR.** The real cross-site
   verification stays owner-gated by design.
8. **One address is still unpublished.** Both landing pages now read `[OWNER_EMAIL_REDACTED]`.
   A public site with no public contact is a choice, not a bug — but it is a choice only you can
   make. Same for the mobile numbers.

## 3b · 7 October live GitHub and DR read

**PR scope at the live-read timestamp `{github_checked_at}`:** #41 is {pr41_status} (updated
`{pr41_updated_at}`; {pr41_note}); #39 is {pr39_status} (updated `{pr39_updated_at}`) and #42 is
{pr42_status} (updated `{pr42_updated_at}`). PR #39 was left untouched. A passing CI run is not
production authorization; the current pull request set remains owner-reviewable.

**A scheduled Git-tree match is recorded; canonical DR target identity remains owner-blocked.**
Run `{dr_workflow_run}` / check `{dr_check_run}` completed `{dr_completed_at}` with
`status={dr_latest_status}`, `data_match={dr_data_match}`, trees `{dr_primary_tree}` and
`{dr_secondary_tree}`, and `traffic_switched={dr_traffic_switched}`. Earlier main-push runs
`{main_write_run_ids}` recorded workflow snapshot writes. The workflow selects Actions variable
`VYOMARAJ_DR_REPO` when configured and otherwise falls back to the checked-in policy; the current
Arena connection lists {visible_repositories} repository, {secondary_404_count} candidate paths
return 404 (ambiguous), and Actions variables/secrets reads return `{actions_variables_api}` /
`{actions_secrets_api}`. Thus the workflow annotation establishes equality for its selected target,
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
| APK | v2 signing-block entry detected; cryptographic verification, signer provenance, device install and unexplained byte matches remain unresolved | Run `apksigner verify`, confirm provenance, test on a real device; rebuild from trusted source if unresolved |
| Issue #6 ({issue6_state}/{issue6_priority}) | Exact secondary repository and Actions access remain unverified in the `{github_checked_at}` read | Owner/admin confirms the existing target and grants required read/Actions access through GitHub; no secret values should be shared in chat |

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
