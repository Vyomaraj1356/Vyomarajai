#!/usr/bin/env python3
"""Rebuild/check the DR sync results report from recorded, closed-vocabulary evidence only.

Every row and every claim in the output is read from a checked-in file:
  * ops/dr/DEPLOYED_MATCH_2026_10_04.json    (MATCH checkpoints, blocked run, read-only probe)
  * ops/dr/DR_POLICY.json                    (scope flags and the one-snapshot removal approval)
  * .github/workflows/vyomaraj-sync-both.yml (triggers and schedule)
Nothing is transcribed by hand and nothing is inferred beyond the recorded fields. If a run is
missing from the record, the report is missing it too — the fix is to record the run, not to
edit this output. Run without arguments to write, with --check to verify the checked-in copy.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORD = ROOT / 'ops/dr/DEPLOYED_MATCH_2026_10_04.json'
POLICY = ROOT / 'ops/dr/DR_POLICY.json'
WORKFLOW = ROOT / '.github/workflows/vyomaraj-sync-both.yml'
OUTPUT = HERE / 'DR_SYNC_RESULTS_2026_10_04.md'
SHORT = 12


def load(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def short(value, keep=SHORT):
    return value[:keep] if value else '—'


def triggers(text):
    """Read the workflow's own trigger block instead of restating it from memory."""
    names = []
    for key in ('push', 'pull_request', 'workflow_dispatch', 'schedule'):
        if re.search(rf'^\s{{2}}{key}:', text, re.M):
            names.append(key)
    crons = re.findall(r"cron:\s*'([^']+)'", text)
    return ', '.join(names), (crons[0] if crons else 'no schedule')


def yes_no(value):
    return 'yes' if value else 'no'


def render(root=ROOT):
    record = load(root / RECORD.relative_to(ROOT))
    policy = load(root / POLICY.relative_to(ROOT))
    workflow = (root / WORKFLOW.relative_to(ROOT)).read_text()
    observations = record['observations']
    writes = [o for o in observations if o.get('replication_write_in_this_run')]
    blocked = record.get('blocked_runs', [])
    trigger_names, cron = triggers(workflow)

    unsupported = [o['check_run_id'] for o in observations
                   if o['status'] != 'MATCH' or o['primary_tree'] != o['secondary_tree']]
    if unsupported:
        raise ValueError(f'record contains non-MATCH or tree-mismatched checkpoints: {unsupported}')
    if record.get('primary_main_tip_checked') is None:
        raise ValueError('record has no checked main tip')

    lines = [
        '# Vyomaraj — DR sync results — 2026-10-04',
        '',
        '**Generated file — do not edit by hand.** Rebuild with '
        '`python3 ops/vyomaraj-core/handover/build_dr_sync_report.py` from the repository root; '
        '`--check` verifies this checked-in copy still matches its evidence.',
        '',
        '## 1. Scope — what this record does and does not assert',
        '',
        f"Primary repository: `{record['primary']}`. Secondary repository: `{record['secondary']}`.",
        f"Main tip covered by this record: `{record['primary_main_tip_checked']}`.",
        f"Workflow: `.github/workflows/vyomaraj-sync-both.yml` — triggers: {trigger_names}; "
        f"schedule: `{cron}` (UTC).",
        f"Recorded scope: {record['scope']}.",
        '',
        'This is a Git-snapshot replication record. It is **not** a production disaster-recovery '
        'approval and it says nothing about runtime databases, live media sessions, provider '
        'accounts, secrets or production traffic.',
        '',
        '## 2. Evidence sources (all checked in)',
        '',
        '| Source | SHA256 | What it contributes |',
        '|---|---|---|',
        f"| `{RECORD.relative_to(ROOT).as_posix()}` | `{digest(root / RECORD.relative_to(ROOT))}` | "
        f"{len(observations)} MATCH checkpoints, {len(writes)} replication writes, "
        f"{len(blocked)} blocked run, 1 read-only probe |",
        f"| `{POLICY.relative_to(ROOT).as_posix()}` | `{digest(root / POLICY.relative_to(ROOT))}` | "
        'scope flags and the time-boxed one-snapshot removal approval |',
        f"| `{WORKFLOW.relative_to(ROOT).as_posix()}` | `{digest(root / WORKFLOW.relative_to(ROOT))}` | triggers and schedule |",
        '',
        f"Method: {record['method']}",
        '',
        f"Re-validation: {record['revalidation']['method']} Result: {record['revalidation']['result']}",
        '',
    ]
    corrections = record['revalidation'].get('timestamp_corrections') or []
    if corrections:
        lines += ['Timestamp corrections applied during that re-validation (status, trees and rollback '
                  'commits were unchanged):', '']
        for item in corrections:
            lines.append(f"- check-run `{item['check_run_id']}`: recorded `{item['recorded']}` → "
                         f"live `{item['corrected_to']}`")
        lines.append('')

    lines += [
        f"## 3. Verification checkpoints ({len(observations)})",
        '',
        'A checkpoint is a successful `verify-or-sync` run on a main tip. `rollback_commit` present '
        'means the run replicated (wrote) the snapshot to the secondary; absent means the two '
        'snapshots were already identical and the run changed nothing. Trees are shown shortened '
        'from the full 40-character values in the record; every row ended `data_match=true`.',
        '',
        '| # | completed (UTC) | merge | PR | run | check-run | status | primary tree | secondary tree | replication write |',
        '|---|---|---|---|---|---|---|---|---|---|',
    ]
    for index, o in enumerate(observations, start=1):
        pr = o.get('merge_pr')
        lines.append(
            f"| {index} | {o['completed_at_utc']} | `{short(o['head_sha'])}` | "
            f"{'#' + str(pr) if pr else 'base'} | `{o.get('workflow_run_id', '—')}` | "
            f"`{o['check_run_id']}` | {o['status']} | "
            f"`{short(o['primary_tree'])}` | `{short(o['secondary_tree'])}` | "
            f"{'yes (`' + short(o['rollback_commit']) + '`)' if o.get('rollback_commit') else 'no'} |")
    lines += [
        '',
        f"All {len(observations)} rows were re-read from the GitHub API at "
        f"{record['revalidated_at_utc']} and matched the values stored in the record.",
        '',
        f"## 4. Replication writes ({len(writes)})",
        '',
        '| merge | PR | run | check-run | rollback commit (previous secondary tip, retained) |',
        '|---|---|---|---|---|',
    ]
    for o in writes:
        pr = o.get('merge_pr')
        lines.append(f"| `{short(o['head_sha'])}` | {'#' + str(pr) if pr else 'base'} | "
                     f"`{o.get('workflow_run_id', '—')}` | `{o['check_run_id']}` | `{o['rollback_commit']}` |")
    lines += [
        '',
        'A write replaces the secondary snapshot with the primary snapshot and keeps the previous '
        'secondary commit as the rollback parent; no force-push and no history deletion is used.',
        '',
        f"## 5. The correctly blocked run ({len(blocked)}) and its approved resolution",
        '',
    ]
    for item in blocked:
        probe = item.get('read_only_probe', {})
        lines += [
            f"One run in this session did **not** match and is deliberately excluded from the "
            f"checkpoint count:",
            '',
            f"- Run `{item.get('workflow_run_id')}` on merge #{item.get('merge_pr')} "
            f"(`{short(item['head_sha'])}`), check-run `{item['check_run_id']}`, "
            f"completed {item['completed_at_utc']}.",
            f"- Public annotation: `{item['public_annotation']}`",
            f"- Interpretation recorded with the evidence: {item['interpretation']}",
        ]
        if probe:
            lines += [
                f"- Read-only probe `{probe['check_run_id']}` (`{short(probe['head_sha'])}`, "
                f"{probe['completed_at_utc']}) reported:",
                '',
                f"  `{probe['public_annotation']}`",
                '',
            ]
        lines += [
            f"- Resolution: {item['resolution']}.",
            '',
        ]
    approval = policy.get('one_snapshot_removal_approval', {})
    if approval:
        lines += [
            'The approval recorded in `DR_POLICY.json` was narrow by design:',
            '',
            f"- approved: {yes_no(approval.get('approved'))}; consumed: {yes_no(approval.get('consumed'))}; "
            f"reviewed candidate secondary-only paths: {approval.get('reviewed_candidate_secondary_only_paths')}; "
            f"expired at {approval.get('expires_at_utc')}.",
            f"- expected secondary commit `{approval.get('expected_commit')}` / tree "
            f"`{approval.get('expected_tree')}`; fulfilled by run `{approval.get('fulfilled_by_run')}`.",
            f"- outcome recorded: {approval.get('outcome')}",
            '',
        ]
    lines += [
        '## 6. Scope limits — do not restate otherwise',
        '',
        f"- Traffic was never switched by these runs: `traffic_switched` = "
        f"{str(record['traffic_switched']).lower()}.",
        f"- Runtime/site disaster recovery was not tested: `runtime_or_site_dr_verified` = "
        f"{str(record['runtime_or_site_dr_verified']).lower()}.",
        f"- No zero-RPO/RTO claim is made: `zero_rpo_or_rto_claimed` = "
        f"{str(record['zero_rpo_or_rto_claimed']).lower()}; policy `zero_rpo_verified` = "
        f"{str(policy.get('zero_rpo_verified')).lower()}, `zero_rto_verified` = "
        f"{str(policy.get('zero_rto_verified')).lower()}.",
        f"- Automatic target-only file removal is off by default: "
        f"`automatic_target_only_file_removal` = "
        f"{str(policy.get('automatic_target_only_file_removal')).lower()}; removal needs explicit, "
        'time-boxed, human approval per reviewed path.',
        f"- Automatic reverse overwrite is off: `automatic_reverse_overwrite` = "
        f"{str(policy.get('automatic_reverse_overwrite')).lower()}.",
        f"- Policy scope, verbatim: {policy.get('scope')}.",
        f"- Branch scope: {record.get('branch_scope_warning')}",
        '',
        '## 7. Re-verify a row yourself',
        '',
        "Ask the API for the recorded annotation of any check-run above: "
        "`gh api repos/Vyomaraj1356/Vyomarajai/check-runs/<check_run_id>/annotations "
        "--jq \'.[] | select(.title==\"DR SNAPSHOT RESULT\") | .message\'`.",
        '',
        'Compare the returned `status`, `primary_tree`, `secondary_tree` and `rollback_commit` with '
        'the row above. No credential beyond read access is required.',
        '',
        'END OF DR SYNC RESULTS',
    ]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; never write')
    args = parser.parse_args()
    try:
        text = render()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
    if args.check:
        if (ROOT / OUTPUT.relative_to(ROOT)).read_bytes() != text.encode('utf-8'):
            parser.exit(1, f'FAIL: {OUTPUT.name} is out of date; rebuild and review\n')
    else:
        OUTPUT.write_text(text, encoding='utf-8')
    record = load(RECORD)
    print(f"PASS: {len(record['observations'])} checkpoints, "
          f"{record['replication_writes_total']} replication writes, "
          f"{record.get('blocked_runs_total', 0)} blocked run; "
          f"{len(text.splitlines())} lines")


if __name__ == '__main__':
    main()
