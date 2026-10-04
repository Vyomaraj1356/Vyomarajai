#!/usr/bin/env python3
"""Render and validate the V16.9 issue/PR ledger and its prepared issue #6 close-out.

The JSON is the source of truth. This builder does not call GitHub and never posts comments,
closes issues or changes pull requests. Live status should be re-read before any action.
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
        'issue-6': 'READY_TO_CLOSE', 'pr-2': 'OWNER_DECISION_REQUIRED',
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
        problems.append('issue #6 close-out must remain prepared, not sent')
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
        '## Decision rules for open pull requests',
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
        '## Issue #6 close-out — prepared, not sent',
        '',
        f"Issue #6 is still `{issue['state_at_snapshot']}`. The latest recorded point is checkpoint **{issue['checkpoint']}**: **{issue['replication_writes']} replication writes** through PR #{issue['pr']}.",
        f"Check-run `{checkpoint['check_run_id']}` / workflow run `{checkpoint['workflow_run_id']}` completed `{checkpoint['completed_at_utc']}` with `status={checkpoint['status']}`; primary and secondary trees are both `{checkpoint['primary_tree']}`; rollback `{checkpoint['rollback_commit']}` is retained.",
        '',
        f"Prepared comment: `{issue['closeout_file']}`. No GitHub comment or issue close has been performed by this builder.",
        '',
        'Runbook (re-read first; do not run automatically):',
        '',
    ]
    for index, command in enumerate(issue['runbook'], start=1):
        lines.append(f'{index}. {command}')
    lines += [
        '',
        'If GitHub returns 403, stop. Do not switch credentials or retry a write through another identity; retain the prepared comment and ask the owner to perform the action with the correct permission.',
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
    print(f'OK: {len(load()["entries"])} ledger entries; issue #6 close-out prepared, not sent')


if __name__ == '__main__':
    main()
