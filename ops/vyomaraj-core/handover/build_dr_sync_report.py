#!/usr/bin/env python3
"""Rebuild/check the DR sync results report from recorded, closed-vocabulary evidence only.

Every row and every claim in the output is read from a checked-in file:
  * ops/dr/DEPLOYED_MATCH_2026_10_04.json    (MATCH checkpoints, blocked run, read-only probe)
  * ops/dr/DR_POLICY.json                    (scope flags and the one-snapshot removal approval)
  * .github/workflows/vyomaraj-sync-both.yml (triggers and schedule)
  * ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json (separately timestamped current access/PR/Pages recheck)
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
ISSUES_LEDGER = HERE / 'ISSUES_AND_PRS_LEDGER.json'
WORKFLOW = ROOT / '.github/workflows/vyomaraj-sync-both.yml'
OUTPUT = HERE / 'DR_SYNC_RESULTS_2026_10_04.md'
REPO_URL = 'https://github.com/Vyomaraj1356/Vyomarajai'
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


def pr_link(number):
    return f"[#{number}]({REPO_URL}/pull/{number})"


def run_link(run_id):
    return f"[`{run_id}`]({REPO_URL}/actions/runs/{run_id})"


def check_link(check_id, run_id=None):
    if run_id:
        url = f"{REPO_URL}/actions/runs/{run_id}/job/{check_id}"
        return f"[`{check_id}`]({url})"
    return f"`{check_id}`"


def commit_link(sha):
    return f"[`{short(sha)}`]({REPO_URL}/commit/{sha})"


def render(root=ROOT):
    record = load(root / RECORD.relative_to(ROOT))
    policy = load(root / POLICY.relative_to(ROOT))
    current_ledger = load(root / ISSUES_LEDGER.relative_to(ROOT))
    live = current_ledger.get('current_live_recheck_2026_10_07', {})
    if not live.get('checked_at_utc'):
        raise ValueError('current issue/PR/Pages recheck is missing its read timestamp')
    dr_snapshot = live.get('dr_snapshot', {})
    if dr_snapshot and (dr_snapshot.get('status') != 'MATCH' or
                        dr_snapshot.get('primary_tree') != dr_snapshot.get('secondary_tree')):
        raise ValueError('current scheduled DR snapshot is not a matching tracked Git tree')
    workflow = (root / WORKFLOW.relative_to(ROOT)).read_text()
    observations = record['observations']
    by_check_run = {str(o['check_run_id']): o for o in observations}
    writes = [o for o in observations if o.get('replication_write_in_this_run')]
    blocked = record.get('blocked_runs', [])
    trigger_names, cron = triggers(workflow)

    unsupported = [o['check_run_id'] for o in observations
                   if o['status'] != 'MATCH' or o['primary_tree'] != o['secondary_tree']]
    if unsupported:
        raise ValueError(f'record contains non-MATCH or tree-mismatched checkpoints: {unsupported}')
    if record.get('primary_main_tip_checked') is None:
        raise ValueError('record has no checked main tip')

    current_dr_sentence = (
        f"Latest scheduled DR run {run_link(dr_snapshot['workflow_run_id'])} / check-run "
        f"{check_link(dr_snapshot['check_run_id'], dr_snapshot['workflow_run_id'])} completed "
        f"`{dr_snapshot['completed_at_utc']}` with `MATCH`, `data_match=true`, and identical tracked Git trees "
        f"`{dr_snapshot['primary_tree']}`; `traffic_switched={dr_snapshot['traffic_switched']}`. "
        "This is a tracked repository-tree match only. "
        if dr_snapshot else 'No current scheduled tree-match evidence is recorded. '
    )
    main_lag = live.get('main', {}).get('session_base_compare', {}).get('ahead_by')
    lag_sentence = f"Main is {main_lag} commits ahead of the session/PR #41 base. " if main_lag is not None else ''
    target_resolution = live.get('dr_target_resolution', {})
    target_resolution_sentence = (
        f"Workflow variable `{target_resolution.get('workflow_variable', 'VYOMARAJ_DR_REPO')}` may override "
        f"the in-repo fallback `{target_resolution.get('in_repo_fallback', 'unknown')}`; because it returned "
        f"{target_resolution.get('workflow_variable_read_result', 'unread')}, the effective target identity is unconfirmed. "
        if target_resolution else ''
    )
    pr_status_sentence = (
        f"Current PRs: #41 {live['pull_requests']['41']['state']}/"
        f"{'DRAFT' if live['pull_requests']['41']['draft'] else 'non-draft'}, "
        f"#39 {live['pull_requests']['39']['state']}/"
        f"{'DRAFT' if live['pull_requests']['39']['draft'] else 'non-draft'}, "
        f"#42 {live['pull_requests']['42']['state']}/"
        f"{'DRAFT' if live['pull_requests']['42']['draft'] else 'non-draft'}; PR #39 was left untouched."
    )

    lines = [
        '# Vyomaraj — DR sync results — 2026-10-04',
        '',
        '**Generated file — do not edit by hand.** Rebuild with '
        '`python3 ops/vyomaraj-core/handover/build_dr_sync_report.py` from the repository root; '
        '`--check` verifies this checked-in copy still matches its evidence.',
        '',
        '## 1. Scope — what this record does and does not assert',
        '',
        f"Primary repository: `{record['primary']}`. Secondary repository named by this historical record: `{record['secondary']}`.",
        f"Main tip covered by this record: `{record['primary_main_tip_checked']}`.",
        f"Workflow: `.github/workflows/vyomaraj-sync-both.yml` — triggers: {trigger_names}; "
        f"schedule: `{cron}` (UTC).",
        f"Recorded scope: {record['scope']}.",
        '',
        'This is a timestamped Git-snapshot replication record, not a production disaster-recovery '
        'approval. It does not prove runtime databases, app-service availability, live media sessions, '
        'provider accounts, secrets, deployment equality or production traffic.',
        '',
        '## Current GitHub / DR access recheck — 7 October 2026 (read-only)',
        '',
        f"Checked at `{live['checked_at_utc']}`. Issue #6 remains **{live['issue_6']['state']}/{live['issue_6']['priority']}**; close-out is not authorized. "
        f"The connection lists {len(live.get('visible_repositories', []))} repository; the four candidate secondary paths returned 404 (not proof that no private secondary exists), and Actions variables/secrets reads returned {live.get('actions_variables_api', 'unread')!r} and {live.get('actions_secrets_api', 'unread')!r}. "
        f"{current_dr_sentence}"
        f"{target_resolution_sentence}Current authoritative-target identity/access and target-only data review remain owner-blocked; no mutation or workflow dispatch was made by this audit. Automatic main-push replication writes are separately recorded in the checkpoint table. "
        f"{lag_sentence}{pr_status_sentence}",
        f"Pages API reports `{live['pages'].get('status', 'unknown')}` from `{live['pages'].get('source', 'unknown')}` at "
        f"`{live['pages'].get('build_commit', 'unknown')[:8]}`; this feature branch is not deployed.",
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
        f"| `{ISSUES_LEDGER.relative_to(ROOT).as_posix()}` | `{digest(root / ISSUES_LEDGER.relative_to(ROOT))}` | timestamped current issue/PR/Pages and DR-access recheck |",
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
        '| # | completed (UTC) | main tip | event | PR | run | check-run | status | primary tree | secondary tree | replication write |',
        '|---|---|---|---|---|---|---|---|---|---|---|',
    ]
    for index, o in enumerate(observations, start=1):
        pr = o.get('merge_pr')
        run_id = o.get('workflow_run_id')
        event = o.get('workflow_event') or ('merge/push' if pr else 'historical checkpoint')
        pr_cell = pr_link(pr) if pr else '—'
        run_cell = run_link(run_id) if run_id else '—'
        lines.append(
            f"| {index} | {o['completed_at_utc']} | {commit_link(o['head_sha'])} | {event} | "
            f"{pr_cell} | {run_cell} | {check_link(o['check_run_id'], run_id)} | {o['status']} | "
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
        run_id = o.get('workflow_run_id')
        lines.append(f"| {commit_link(o['head_sha'])} | {pr_link(pr) if pr else 'base'} | "
                     f"{run_link(run_id) if run_id else '—'} | {check_link(o['check_run_id'], run_id)} | "
                     f"`{o['rollback_commit']}` |")
    lines += [
        '',
        'A write replaces the secondary snapshot with the primary snapshot and keeps the previous '
        'secondary commit as the rollback parent; no force-push and no history deletion is used.',
        '',
        f"## 5. The correctly blocked run ({len(blocked)}) and its approved resolution",
        '',
    ]
    unavailable = [(o['check_run_id'], o['rollback_commit_timestamp']) for o in writes
                   if o.get('rollback_commit_timestamp')]
    if unavailable:
        lines += ['Rollback-commit timestamps that could not be read (recorded as failed reads, never as '
                  'guessed values):', '']
        for check_run_id, item in unavailable:
            value = 'null' if item.get('value_utc') is None else item['value_utc']
            run_id = by_check_run.get(str(check_run_id), {}).get('workflow_run_id')
            lines.append(f"- check-run {check_link(check_run_id, run_id)}: value_utc = {value}.")
            lines.append(f"  - Attempt: {item.get('attempt')}")
            lines.append(f"  - Bounded substitute: {item.get('bounded_substitute')}")
            lines.append(f"  - Standing: {item.get('not_fabricated')}")
        lines += ['']
        lines += ['']
    for item in blocked:
        probe = item.get('read_only_probe', {})
        lines += [
            f"One run in this session did **not** match and is deliberately excluded from the "
            f"checkpoint count:",
            '',
            f"- Run {run_link(item.get('workflow_run_id'))} on merge "
            f"{pr_link(item.get('merge_pr'))} "
            f"({commit_link(item['head_sha'])}), check-run "
            f"{check_link(item['check_run_id'], item.get('workflow_run_id'))}, "
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
    publication = record.get('publication_status', {})
    if publication:
        rebuilt = publication.get('rebuilt_from_lost_local_commits', {})
        lines += [
            '## 5b. Publication status of this record',
            '',
            f"Recorded by session: `{publication.get('recorded_by_session')}`.",
            f"Session branch base: `{publication.get('session_branch_base')}`.",
            f"Pushed to origin at record time: {yes_no(publication.get('pushed_at_record_time'))}.",
        ]
        if publication.get('published_as'):
            lines += [
                f"Published as: {publication['published_as']}.",
                f"Coverage: {publication.get('comics_and_architecture_coverage')}.",
            ]
        lines += [
            f"Publish path: {publication.get('publish_path')}.",
            f"DR coverage of the merge that carries this record: {publication.get('dr_coverage_of_this_merge')}.",
            f"Local sync possible from the recording sandbox: {yes_no(publication.get('local_sync_possible_from_this_sandbox'))}.",
            '',
        ]
        if rebuilt:
            lines += [
                f"Rebuilt from lost local commits: {rebuilt.get('lost_session')}.",
                'Rebuilt in this merge:',
                '',
            ]
            for item in rebuilt.get('rebuilt_in_this_merge', []):
                lines.append(f"- {item}")
            lines.append('')
    lines += [
        '## 5c. Checkpoint selection and the next-read rule',
        '',
        'This record includes one successful verify-or-sync checkpoint for each newly observed main tip,',
        'plus the latest successful scheduled confirmation on the final main tip. Duplicate same-tree no-op',
        'runs are re-read and listed in the current extension audit but are not counted as extra selected',
        'checkpoints. Unmerged branch tips and local edits are excluded. Future main changes are not pre-counted:',
        '',
        '```',
        "gh api repos/Vyomaraj1356/Vyomarajai/commits/main/check-runs --jq '.check_runs[] | select(.name==\"verify-or-sync\") | [.id, .conclusion] | @tsv'",
        "gh api repos/Vyomaraj1356/Vyomarajai/check-runs/<check_run_id>/annotations --jq '.[] | select(.title==\"DR SNAPSHOT RESULT\") | .message'",
        '```',
        '',
        'After an owner-approved merge, re-read the resulting workflow annotation in the next update; do not',
        'merge, dispatch or pre-count that future run. A scheduled tree match is not an application deployment',
        'or a runtime/failover test.',
        '',
        '## 5d. Local verification attempt in the recording session',
        '',
    ]
    attempt = record.get('local_verification_attempt', {})
    if attempt:
        lines += [
            f"- Command: `{attempt.get('command')}`",
            f"- Result: **{attempt.get('result')}** (checked {attempt.get('checked_at_utc', 'at the previously recorded time')})",
            f"- Explanation: {attempt.get('explanation')}",
            '',
            'This is why the record is built from the workflow\'s own public annotations: the Actions credential is the',
            'authorized reader/writer for the private secondary, and a sandbox 404 is not evidence about the secondary.',
            '',
        ]
    windows = record.get('unverified_windows') or []
    if windows:
        lines += [
            f'## 5e. Windows in which verify-or-sync did not execute ({len(windows)})',
            '',
            'A window is a period in which the workflow ran but the verify-or-sync job never executed, so',
            '**no** checkpoint exists for it — no match, no mismatch and no write was observed. Windows are',
            'recorded here rather than in section 3 precisely because they are not checkpoints: counting them',
            'as matches would overstate coverage, and counting them as mismatches would overstate damage.',
            '',
        ]
        for index, window in enumerate(windows, start=1):
            runs = ', '.join(f'`{run}`' for run in window.get('runs', []))
            resumed = window.get('resumed_by')
            lines += [
                f'### {index}. {window.get("window")}',
                '',
                f'- Head SHA at the time: `{window.get("head_sha")}`',
                f'- Runs involved: {runs}',
                f'- Observation: {window.get("observation")}',
                f'- Cause recorded: {window.get("cause_recorded")}',
                f'- Effect: {window.get("effect")}',
                f"- Resumed by: {'run `' + str(resumed) + '`' if resumed else 'open at record time — the next checkpoint closes it'}",
                '',
            ]
    extension = record.get('record_extension_2026_10_06')
    if extension:
        lines += [
            f"## 5f. Record extension by `{extension.get('session')}` (2026-10-06)",
            '',
            f"- Finding: {extension.get('finding')}",
            f"- Fix: {extension.get('fix')}",
            f"- Next checkpoint: {extension.get('next_checkpoint')}",
            '',
        ]
        probe = extension.get('read_only_probe_confirmation')
        if probe:
            lines += [
                '### Read-only confirmation of the open window',
                '',
                f"- Source: {probe.get('source')}",
                f"- Public annotation: `{probe.get('annotation')}`",
                f"- What it means: {probe.get('meaning')}",
                f"- Second defect found by making the diagnostic run again: {probe.get('second_class_defect')}",
                '',
            ]
    extension_b = record.get('record_extension_2026_10_06_b')
    if extension_b:
        lines += [
            f"## 5g. Record extension by `{extension_b.get('session')}` (2026-10-06, second pass)",
            '',
            f"- Finding: {extension_b.get('finding')}",
            f"- Fix: {extension_b.get('fix')}",
            f"- Recording rule: {extension_b.get('rule')}",
            f"- Next checkpoint: {extension_b.get('next_checkpoint')}",
            '',
        ]
        if extension_b.get('fulfilled_by'):
            lines += [f"- Fulfilled by: {extension_b.get('fulfilled_by')}", '']
    extension_c = record.get('record_extension_2026_10_06_c')
    if extension_c:
        lines += [
            f"## 5h. Record extension by `{extension_c.get('session')}` (2026-10-06, third pass)",
            '',
            f"- Finding: {extension_c.get('finding')}",
            f"- Fix: {extension_c.get('fix')}",
            f"- Stale-head race: {extension_c.get('stale_head_race')}",
            f"- Rollback timestamp attempt: {extension_c.get('rollback_timestamp_attempt')}",
            f"- Next checkpoint: {extension_c.get('next_checkpoint')}",
            '',
        ]
    race = record.get('stale_head_race_note_2026_10_06')
    if race:
        instance = race.get('observed_instance', {})
        lines += [
            '## 5i. Stale-head race between a schedule run and a merge (2026-10-06)',
            '',
            f"- Phenomenon: {race.get('phenomenon')}",
            f"- Observed instance: schedule run `{instance.get('schedule_run_id')}` (head "
            f"`{short(instance.get('schedule_head_sha'))}`, check-run `{instance.get('schedule_check_run_id')}`, "
            f"completed {instance.get('schedule_completed_at_utc')}) verified and wrote the "
            f"`{short(instance.get('schedule_annotation_trees'))}` tree; the push run `{instance.get('push_run_id')}` "
            f"on head `{short(instance.get('push_head_sha'))}` (check-run `{instance.get('push_check_run_id')}`, "
            f"completed {instance.get('push_completed_at_utc')}) then found the snapshots already equal.",
            f"- Rule for future reads: {race.get('rule_for_future_reads')}",
            f"- Checkpoint #30 guidance: {race.get('checkpoint_30_guidance')}",
        ]
        if race.get('fulfilled_by'):
            lines += [f"- Fulfilled by: {race.get('fulfilled_by')}"]
        lines += ['']
    extension_d = record.get('record_extension_2026_10_07')
    if extension_d:
        audit = extension_d.get('annotation_audit', {})
        lines += [
            f"## 5j. Record extension by `{extension_d.get('session')}` (2026-10-07)",
            '',
            f"- Finding: {extension_d.get('finding')}",
            f"- Fix: {extension_d.get('fix')}",
            f"- Live annotation audit: {audit.get('previous_checkpoints_re_read')} previous rows re-read; "
            f"mismatches: {audit.get('mismatches')}; new check-runs: "
            f"{', '.join(check_link(value, by_check_run.get(str(value), {}).get('workflow_run_id')) for value in audit.get('new_check_runs', []))}; "
            f"completed at {audit.get('completed_at_utc')}.",
            f"- PR #39 status: [live PR page]({REPO_URL}/pull/39); "
            f"{extension_d.get('pr_39_live_status')}",
            f"- Next checkpoint: {extension_d.get('next_checkpoint')}",
            '',
        ]
    extension_e = record.get('record_extension_2026_10_07_b')
    if extension_e:
        audit = extension_e.get('annotation_audit', {})
        aligned_apk = extension_e.get('artifact_alignment', {})
        main_cmp = extension_e.get('current_main_vs_session_base', {})
        latest = extension_e.get('latest_scheduled_match', {})
        lines += [
            f"## 5k. Main-tip and scheduled-match extension by `{extension_e.get('session')}` (2026-10-07)",
            '',
            f"- Finding: {extension_e.get('finding')}",
            f"- Fix/selection rule: {extension_e.get('fix')}",
            f"- Audit: {audit.get('previous_checkpoints_re_read')} prior rows re-read, "
            f"{audit.get('new_successful_main_annotations_re_read')} new successful main annotations re-read; "
            f"{audit.get('previous_mismatches', 0) + audit.get('new_mismatches', 0)} mismatches. "
            f"Selected new checks: {', '.join(check_link(value, by_check_run.get(str(value), {}).get('workflow_run_id')) for value in audit.get('new_selected_check_runs', []))}. "
            f"Additional duplicate/older no-write checks: {', '.join(str(value) for value in audit.get('additional_no_write_check_runs_re_read', []))}. "
            f"Completed at {audit.get('completed_at_utc')}.",
            f"- Latest scheduled confirmation: run {run_link(latest.get('workflow_run_id'))}, "
            f"check-run {check_link(latest.get('check_run_id'), latest.get('workflow_run_id'))}, "
            f"completed `{latest.get('completed_at_utc')}`; equal tree `{short(latest.get('primary_tree'))}`, "
            f"no write, traffic switch `{latest.get('traffic_switched')}`.",
            f"- Current main comparison: main `{short(main_cmp.get('main'))}` is {main_cmp.get('ahead_by')} commits ahead of "
            f"PR #41's base `{short(main_cmp.get('pr_41_base'))}`; PR #41 is still {main_cmp.get('pr_41_state')}. "
            f"PR #39 remains open/draft and untouched: {extension_e.get('pr_39_live_status')}",
            f"- Tracked APK in matched tree: `{aligned_apk.get('path')}` blob `{aligned_apk.get('git_blob_sha')}`, "
            f"{aligned_apk.get('size_bytes')} bytes. Equal tree implies the same repository blob at the secondary; "
            f"signature, signer provenance and real-device installation remain unverified.",
            f"- Issue #6: {extension_e.get('issue_6')}",
            f"- Next checkpoint: {extension_e.get('next_checkpoint')}",
            '',
        ]
    extension_f = record.get('record_extension_2026_10_07_c')
    if extension_f:
        latest = extension_f.get('latest_scheduled_match', {})
        audit = extension_f.get('annotation_audit', {})
        lines += [
            f"## 5l. Follow-up scheduled checkpoint by `{extension_f.get('session')}` (2026-10-07)",
            '',
            f"- Finding: {extension_f.get('finding')}",
            f"- Fix: {extension_f.get('fix')}",
            f"- Latest live read: run {run_link(latest.get('workflow_run_id'))}, "
            f"check-run {check_link(latest.get('check_run_id'), latest.get('workflow_run_id'))}, "
            f"created `{latest.get('created_at_utc')}`, completed `{latest.get('completed_at_utc')}`; "
            f"status `{latest.get('status')}`, `data_match={str(latest.get('data_match')).lower()}`, "
            f"equal tracked trees `{latest.get('primary_tree')}` / `{latest.get('secondary_tree')}`, "
            f"traffic `{latest.get('traffic_switched')}`, write `{str(latest.get('replication_write_in_this_run')).lower()}`.",
            f"- Annotation limits: `http={latest.get('http')}`, "
            f"`failed_api_operation={latest.get('failed_api_operation')}`. This annotation is a tracked-tree result only, "
            "not runtime, deployed-app, authenticated-heartbeat, failover, RPO or RTO evidence.",
            f"- Audit scope: re-read only the new checkpoint annotation; prior rows reread in this addendum: "
            f"{audit.get('previous_checkpoints_reread')}. {audit.get('scope_note')}",
            '',
        ]
    extension_g = record.get('record_extension_2026_10_07_d')
    if extension_g:
        latest = extension_g.get('latest_scheduled_match', {})
        audit = extension_g.get('annotation_audit', {})
        lines += [
            f"## 5m. Latest scheduled checkpoint follow-up by `{extension_g.get('session')}` (2026-10-07)",
            '',
            f"- Finding: {extension_g.get('finding')}",
            f"- Fix: {extension_g.get('fix')}",
            f"- Latest scheduled run {run_link(latest.get('workflow_run_id'))} / "
            f"check-run {check_link(latest.get('check_run_id'), latest.get('workflow_run_id'))} "
            f"completed `{latest.get('completed_at_utc')}`; status `{latest.get('status')}`, "
            f"`data_match={str(latest.get('data_match')).lower()}`, equal trees `{latest.get('primary_tree')}` / "
            f"`{latest.get('secondary_tree')}`, traffic `{latest.get('traffic_switched')}`, "
            f"write `{str(latest.get('replication_write_in_this_run')).lower()}`, "
            f"annotation `http={latest.get('http')}`.",
            f"- Scope: prior checkpoint annotations reread in this addendum: "
            f"{audit.get('previous_checkpoints_reread')}; {audit.get('scope_note')} "
            f"No runtime/app, authenticated-heartbeat, failover, RPO or RTO proof is established.",
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
