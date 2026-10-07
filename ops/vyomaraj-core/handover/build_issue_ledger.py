#!/usr/bin/env python3
"""Render and validate the historical issue/PR ledger plus the current blocked issue #6 state.

The JSON is the source of truth. This builder does not call GitHub and never posts comments,
closes issues or changes pull requests. Live status must be re-read before any action.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / 'ISSUES_AND_PRS_LEDGER.json'
OUTPUT = HERE / 'ISSUES_AND_PRS_LEDGER_2026_10_04.md'
ALLOWED_STATUS = {
    'READY_TO_CLOSE', 'OWNER_DECISION_REQUIRED', 'WATCH', 'RESOLVED_DOCUMENTED',
    'FIX_APPLIED_OFFLINE', 'OWNER_ACTION_REQUIRED'
}


def load(path=SOURCE):
    return json.loads(path.read_text(encoding='utf-8'))


def validate(data=None):
    data = data or load()
    problems = []
    entries = data.get('entries', [])
    if len(entries) != 14:
        problems.append(f'expected 14 ledger entries, found {len(entries)}')
    ids = [entry.get('id') for entry in entries]
    if len(ids) != len(set(ids)) or None in ids:
        problems.append('ledger entry ids must be present and unique')
    for entry in entries:
        if entry.get('status') not in ALLOWED_STATUS:
            problems.append(f"{entry.get('id')} has unsupported status {entry.get('status')}")
        for field in ('reference', 'title', 'summary', 'next_action'):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                problems.append(f"{entry.get('id')} is missing {field}")
    required = {
        'issue-6': 'OWNER_ACTION_REQUIRED', 'pr-2': 'OWNER_DECISION_REQUIRED',
        'pr-3': 'OWNER_DECISION_REQUIRED', 'pr-4': 'OWNER_DECISION_REQUIRED',
        'pr-7': 'OWNER_DECISION_REQUIRED', 'pr-9': 'WATCH',
        'merge-chain-10-24': 'RESOLVED_DOCUMENTED',
        'chats-count-conflict': 'FIX_APPLIED_OFFLINE',
        'contract-status-conflict': 'OWNER_DECISION_REQUIRED',
    }
    by_id = {entry.get('id'): entry for entry in entries}
    for entry_id, status in required.items():
        if entry_id not in by_id:
            problems.append(f'missing required ledger item {entry_id}')
        elif by_id[entry_id].get('status') != status:
            problems.append(f'{entry_id} must have status {status}')
    issue = data.get('issue_6_closeout', {})
    snapshot = data.get('snapshot', {})
    checkpoint = snapshot.get('merge_checkpoint', {})
    if issue.get('state_at_snapshot') != 'OPEN' or not issue.get('prepared_but_not_sent'):
        problems.append('issue #6 historical comment state must remain preserved, not sent')
    if issue.get('historical_snapshot_only') is not True or issue.get('do_not_post_or_close') is not True:
        problems.append('issue #6 historical close-out must be explicitly marked stale/do-not-post')
    if issue.get('current_live_state') != 'OPEN/P0' or not issue.get('current_blocker'):
        problems.append('issue #6 current owner blocker must remain explicit')
    live = data.get('current_live_recheck_2026_10_07', {})
    if live.get('issue_6', {}).get('closeout_authorized') is not False:
        problems.append('issue #6 close-out must not be authorized by the current snapshot')
    if not live.get('checked_at_utc'):
        problems.append('current GitHub/Pages recheck must carry its read timestamp')
    if live.get('issue_6', {}).get('state') != 'OPEN' or live.get('issue_6', {}).get('priority') != 'P0':
        problems.append('issue #6 must remain OPEN/P0 until owner-approved acceptance evidence is complete')
    dr = live.get('dr_snapshot', {})
    if (dr.get('status') != 'MATCH' or not dr.get('data_match')
            or dr.get('primary_tree') != dr.get('secondary_tree')
            or dr.get('traffic_switched') != 'NONE'):
        problems.append('latest scheduled DR evidence must preserve the exact same-tree/no-traffic-switch result')
    if live.get('observed_main_replication_writes', {}).get('count_since_previous_recorded_checkpoint') != 2:
        problems.append('current snapshot must preserve the two observed automatic main-push replication writes')
    if live.get('pages', {}).get('feature_branch_deployed') is not False:
        problems.append('current Pages snapshot must state that this feature branch is not deployed')
    if issue.get('checkpoint') != '#19' or issue.get('replication_writes') != 15:
        problems.append('issue #6 close-out must cite checkpoint #19 and 15 writes')
    if checkpoint.get('check_run_id') != issue.get('check_run_id'):
        problems.append('issue #6 close-out check-run id does not match the snapshot')
    if checkpoint.get('status') != 'MATCH' or checkpoint.get('primary_tree') != checkpoint.get('secondary_tree'):
        problems.append('latest issue #6 checkpoint is not a matching tree')
    if len(issue.get('runbook', [])) != 5:
        problems.append('issue #6 runbook must contain five ordered steps')
    return problems


def render(root=ROOT, data=None):
    data = data or load(root / SOURCE.relative_to(ROOT))
    problems = validate(data)
    if problems:
        raise ValueError('; '.join(problems))
    snapshot = data['snapshot']
    issue = data['issue_6_closeout']
    checkpoint = snapshot['merge_checkpoint']
    live = data['current_live_recheck_2026_10_07']
    current_issue = live['issue_6']
    current_pages = live['pages']
    dr = live['dr_snapshot']
    auto_writes = live['observed_main_replication_writes']
    main = live['main']
    followup = data.get('current_github_metadata_followup_2026_10_07', {})
    dr_followup = data.get('current_dr_annotation_followup_2026_10_07', {})
    lines = [
        '# Issues and pull requests ledger — 2026-10-04',
        '',
        '**New-session runbook (in order)**',
        '',
        'This ledger accounts for the known open issue/PR decisions and the repository conflicts. '
        'It is a checked-in snapshot, not a claim that every external state is unchanged. Re-read GitHub before acting.',
        '',
        f"Snapshot commit: `{snapshot['main_commit']}` · recorded `{data['recorded_at_utc']}` · "
        f"source: {data['source_note']}",
        '',
        '| # | Reference | State | Summary | Next action |',
        '|---:|---|---|---|---|',
    ]
    for index, entry in enumerate(data['entries'], start=1):
        summary = entry['summary'].replace('|', '\\|')
        action = entry['next_action'].replace('|', '\\|')
        lines.append(f"| {index} | {entry['reference']} — {entry['title']} | **{entry['status']}** | {summary} | {action} |")
    lines += [
        '',
        '## Decision rules for open pull requests (2026-10-04 snapshot)',
        '',
        '- PRs #2, #3, #4 and #7 are **not to be merged** from their current branches: the recorded blocker is no merge base with `main`. If selected, re-apply the desired content as a fresh reviewed change.',
        '- PR #9 is another session\'s draft and stays untouched unless the owner explicitly directs otherwise.',
        '- The #10–#24 merge chain is already recorded as merged; do not duplicate it as pending work.',
        '',
        '## Offline conflict notices',
        '',
        '- **All-chats file:** its heading says 28 chats while it contains 34 numbered entries. The viewer states both values; the historical source remains unchanged until the owner confirms the canonical count.',
        '- **Contract status:** conflicting records are preserved. The ledger does not choose an authority; follow auto-align step `o02-contract-authority` and keep a superseded-by pointer after the owner decides.',
        '',
        '## Current GitHub / Pages / DR read — 7 October 2026 (read-only audit)',
        '',
        f"Checked at `{live['checked_at_utc']}`. Issue #6 remains **{current_issue['state']}/{current_issue['priority']}** "
        f"(GitHub updated `{current_issue.get('updated_at', 'not recorded')}`); close-out is not authorized. "
        f"The connection can list only the primary repository. Four candidate secondary paths returned 404 "
        f"(not proof that a private repository does not exist); Actions variables/secrets APIs returned "
        f"{live.get('actions_variables_api', 'unread')!r} and {live.get('actions_secrets_api', 'unread')!r}. "
        f"The workflow's `VYOMARAJ_DR_REPO` variable can override the in-repo fallback; it is unreadable here, so the effective target identity remains unconfirmed. "
        f"The latest scheduled check-run `{dr['check_run_id']}` / workflow run `{dr['workflow_run_id']}` "
        f"completed `{dr['completed_at_utc']}` with `status=MATCH`, `data_match=true`, and identical tracked "
        f"Git trees `{dr['primary_tree']}` on main `{dr['head_sha']}`; `traffic_switched={dr['traffic_switched']}`. "
        "This is repository-tree equality only. The two main-push writes shown below were executed by the "
        "existing Actions workflow, not initiated by this read-only session. Target identity/access and "
        "target-only-data review remain owner-blocked, so issue #6 stays open.",
        f"Main `{main['sha'][:8]}` is {main['session_base_compare']['ahead_by']} commits ahead of the session/PR #41 base; "
        "this branch is not deployed on Pages.",
        '',
        '| PR | Live state | GitHub updated | Note |',
        '|---|---|---|---|',
        *[f"| #{number} | {item['state']}, {'draft' if item['draft'] else 'non-draft'} | "
          f"{item.get('updated_at', 'not recorded')} | {item.get('note', 'Left unchanged')} |"
          for number in ('41', '39', '42')
          for item in (live['pull_requests'][number],)],
        '',
        f"Pages is `{current_pages.get('status', 'status unknown')}` from `{current_pages.get('source', 'source unknown')}` "
        f"at `{current_pages.get('build_commit', 'unknown')[:8]}` (latest build "
        f"`{current_pages.get('last_build_created_at', 'time unknown')}`); this feature branch is not deployed there. "
        'Re-read current GitHub/Pages state before any action.',
        '',
        '### Automatic main-push replication writes observed after the previous DR checkpoint',
        '',
        '| Workflow run | Check-run | Main tip | Rollback parent | Completed (UTC) |',
        '|---|---|---|---|---|',
        *[f"| `{row['workflow_run_id']}` | `{row['check_run_id']}` | `{row['head_sha'][:12]}` | "
          f"`{row['rollback_commit']}` | {row['completed_at_utc']} |"
          for row in auto_writes['writes']],
        '',
        f"The latest tracked APK in the matched main tree is `{live['tracked_apk_in_main_tree']['path']}` "
        f"(Git blob `{live['tracked_apk_in_main_tree']['git_blob_sha']}`, {live['tracked_apk_in_main_tree']['size_bytes']} bytes). "
        "Equal Git trees imply matching repository bytes at the secondary; APK signature validity, signer provenance "
        "and real-device installation remain UNVERIFIED.",
        '',
        '## Issue #6 — historical close-out draft; blocked; DO NOT POST OR CLOSE',
        '',
        f"The 2026-10-04 snapshot recorded checkpoint **{issue['checkpoint']}** and **{issue['replication_writes']} replication writes** through PR #{issue['pr']}. It is historical evidence only and does not meet the current owner/admin access gate.",
        f"Historical check-run `{checkpoint['check_run_id']}` / workflow run `{checkpoint['workflow_run_id']}` completed `{checkpoint['completed_at_utc']}` with `status={checkpoint['status']}`; then-recorded primary and secondary trees matched; rollback `{checkpoint['rollback_commit']}` was retained. That older row did not establish current state; the later scheduled 7 October tree-match checkpoint is reported above.",
        '',
        f"Historical draft retained for provenance at `{issue['closeout_file']}`. It is stale and **must not be posted**. No GitHub comment or close has been performed by this builder.",
        '',
        'Owner/admin runbook (no writes; do not run automatically):',
        '',
    ]
    for index, command in enumerate(issue['runbook'], start=1):
        lines.append(f'{index}. {command}')
    lines += [
        '',
        'If GitHub returns 403 or 404, stop. Do not change credentials, dispatch a workflow, post the stale comment, or close the issue. Preserve the historical artifact and ask the owner/admin to resolve the access gate.',
        '',
        '## Auto-align paths',
        '',
        'The provider, studio, service and operations items have finite completion paths in `AUTO_ALIGN_NEXT_SESSION_2026_10_04.md`; the corresponding JSON source is `AUTO_ALIGN_NEXT_SESSION.json`. Every open platform item is mapped to a step id in `PLATFORM_CONFIGURATION_CHECK_2026_10_04.md`.',
        '',
        '## Scope',
        '',
        'This ledger does not assert that a provider is connected, a contract executed, production traffic switched, or independent runtime disaster recovery tested. Owner decisions remain pending until evidence is recorded and reviewed.',
        'No prices, plan limits or earnings projections are stated here.',
        '',
    ]
    if followup:
        pr = followup.get('pull_requests', {})
        pages = followup.get('pages', {})
        latest = followup.get('latest_scheduled_workflow_run', {})
        run_url = f"https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/{latest.get('workflow_run_id')}"
        lines += [
            '## Scoped GitHub metadata follow-up — 7 October 2026 (read-only)',
            '',
            f"Read started at `{followup.get('observed_at_utc')}`. Issue #6 is `{followup.get('issue_6', {}).get('state')}/{followup.get('issue_6', {}).get('priority')}`; "
            f"PR #39 is `{pr.get('39', {}).get('state')}/DRAFT`, PR #41 is `{pr.get('41', {}).get('state')}/non-draft`, "
            f"and PR #42 is `{pr.get('42', {}).get('state')}/DRAFT`. Main remains `{followup.get('main_sha')}`; "
            f"Pages source remains `{pages.get('source_branch')}:{pages.get('source_path')}`.",
            f"The latest scheduled run in the read list was [{latest.get('workflow_run_id')}]({run_url}) "
            f"({latest.get('status')}/{latest.get('conclusion')}) with check-run `{latest.get('check_run_id')}`; "
            "the current check-run annotation is separately recorded above in the DR report.",
            followup.get('scope', ''),
            '',
        ]
    if dr_followup:
        run_url = f"https://github.com/Vyomaraj1356/Vyomarajai/actions/runs/{dr_followup.get('workflow_run_id')}"
        check_url = f"{run_url}/job/{dr_followup.get('check_run_id')}"
        lines += [
            '## Latest scheduled DR annotation follow-up — 7 October 2026 (read-only)',
            '',
            f"Run [{dr_followup.get('workflow_run_id')}]({run_url}) / check-run "
            f"[{dr_followup.get('check_run_id')}]({check_url}) completed "
            f"`{dr_followup.get('run_completed_at_utc')}` with `status={dr_followup.get('status')}`, "
            f"`data_match={str(dr_followup.get('data_match')).lower()}`, equal tracked trees "
            f"`{dr_followup.get('primary_tree')}`, `traffic_switched={dr_followup.get('traffic_switched')}`, "
            f"no write, annotation `http={dr_followup.get('http')}`.",
            f"This follow-up checked the new annotation only; previous checkpoint annotations reread: "
            f"{dr_followup.get('previous_checkpoints_reread')}. {dr_followup.get('scope')}",
            '',
        ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; never write')
    args = parser.parse_args()
    try:
        problems = validate()
        if problems:
            raise ValueError('; '.join(problems))
        output = render()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
    if args.check:
        current = OUTPUT.read_text(encoding='utf-8') if OUTPUT.is_file() else ''
        if current != output:
            parser.exit(1, f'FAIL: {OUTPUT.name} is out of date; rebuild and review\n')
    else:
        OUTPUT.write_text(output, encoding='utf-8')
    print(f'OK: {len(load()["entries"])} ledger entries; issue #6 remains OPEN/P0; historical draft not for posting')


if __name__ == '__main__':
    main()
