#!/usr/bin/env python3
"""Validate, render, or execute the repository-local part of the V16.9 completion plan.

The runner only starts argv lists from the checked-in allowlist. It never uses a shell, installs
packages, calls providers, publishes content, pushes/merges Git, or changes live infrastructure.
Preview probes use loopback only and are recorded as expected skips if the server is down.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN_PATH = HERE / 'AUTO_ALIGN_NEXT_SESSION.json'
ITEMS_PATH = HERE / 'PLATFORM_OPEN_ITEMS_2026_10_04.json'
REPORT_PATH = HERE / 'AUTO_ALIGN_NEXT_SESSION_2026_10_04.md'
STATE_PATH = HERE / 'AUTO_ALIGN_STATE_2026_10_04.json'
EVIDENCE_PATH = HERE / 'TEST_EVIDENCE_2026_10_04.json'
REQUIRED_STEP_COUNT = 21
REQUIRED_PHASE_COUNT = 5
REQUIRED_OPEN_ITEM_COUNT = 41
REQUIRED_LOCAL_STEP_COUNT = 14
FORBIDDEN_COMMAND = re.compile(
    r'(^|[\s/])(?:pip\s+install|npm\s+install|yarn\s+add|pnpm\s+add|'
    r'gh\s+(?:issue\s+(?:close|comment)|pr\s+(?:merge|create))|git\s+(?:push|merge)|'
    r'curl|wget|purchase|publish)(?=$|[\s/])|https?://', re.IGNORECASE)
MARKERS = {
    '/reports/auto-align': 'AUTO-ALIGN EXECUTION PLAN',
    '/reports/platform-check': 'How it gets configured (auto-align plan)',
    '/reports/issues': 'New-session runbook (in order)',
}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(plan=None, items_doc=None):
    plan = plan or load(PLAN_PATH)
    items_doc = items_doc or load(ITEMS_PATH)
    problems = []
    steps = plan.get('steps', [])
    phases = plan.get('phases', [])
    sequence = plan.get('local_sequence', [])
    items = items_doc.get('items', [])
    step_ids = [step.get('id') for step in steps]
    phase_ids = [phase.get('id') for phase in phases]
    item_ids = [item.get('id') for item in items]

    if len(steps) != REQUIRED_STEP_COUNT:
        problems.append(f'expected {REQUIRED_STEP_COUNT} plan steps, found {len(steps)}')
    if len(phases) != REQUIRED_PHASE_COUNT:
        problems.append(f'expected {REQUIRED_PHASE_COUNT} phases, found {len(phases)}')
    if len(sequence) != REQUIRED_LOCAL_STEP_COUNT:
        problems.append(f'expected {REQUIRED_LOCAL_STEP_COUNT} local steps, found {len(sequence)}')
    if len(items) != REQUIRED_OPEN_ITEM_COUNT:
        problems.append(f'expected {REQUIRED_OPEN_ITEM_COUNT} open platform items, found {len(items)}')
    for label, values in (('step', step_ids), ('phase', phase_ids), ('platform item', item_ids)):
        if None in values or len(values) != len(set(values)):
            problems.append(f'{label} ids must be present and unique')

    step_by_id = {step.get('id'): step for step in steps}
    if set(phase_ids) != {f'phase-{i}' for i in range(REQUIRED_PHASE_COUNT)}:
        problems.append('phase ids must be phase-0 through phase-4')
    phase_members = []
    for phase in phases:
        declared = phase.get('step_ids', [])
        phase_members.extend(declared)
        for step_id in declared:
            if step_id not in step_by_id:
                problems.append(f"phase {phase.get('id')} references missing step {step_id}")
            elif step_by_id[step_id].get('phase') != phase.get('number'):
                problems.append(f"step {step_id} has a phase number inconsistent with its phase list")
    if sorted(phase_members) != sorted(step_ids):
        problems.append('every plan step must appear in exactly one phase')

    for step in steps:
        for field in ('title', 'actor', 'status', 'action', 'verify', 'done_when', 'evidence_path'):
            if not isinstance(step.get(field), str) or not step[field].strip():
                problems.append(f"step {step.get('id')} is missing {field}")
        if not isinstance(step.get('covers'), list):
            problems.append(f"step {step.get('id')} covers must be a list")

    covered = []
    for step in steps:
        for item_id in step.get('covers', []):
            covered.append(item_id)
            if item_id not in item_ids:
                problems.append(f"step {step.get('id')} references unknown platform item {item_id}")
    for item_id in item_ids:
        if item_id not in covered:
            problems.append(f'open platform item {item_id} has no completion step')
    for item_id in set(covered):
        if covered.count(item_id) > 1:
            problems.append(f'open platform item {item_id} is mapped more than once')

    local_ids = [entry.get('id') for entry in sequence]
    if len(local_ids) != len(set(local_ids)) or None in local_ids:
        problems.append('local sequence ids must be present and unique')
    for entry in sequence:
        if entry.get('kind') == 'command':
            argv = entry.get('argv')
            if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
                problems.append(f"{entry.get('id')} must use a non-empty argv list")
                continue
            command = ' '.join(argv)
            # l03 is a deliberate, read-only self-check exception: the runner must validate its own
            # command even though that command names auto_align.py.
            if FORBIDDEN_COMMAND.search(command):
                problems.append(f"{entry.get('id')} contains a forbidden external or live command")
            if '--run' in argv:
                problems.append(f"{entry.get('id')} may not recursively launch the runner")
            if entry.get('allow_runner_check'):
                expected = ['python3', 'ops/vyomaraj-core/handover/auto_align.py', '--check']
                if entry.get('id') != 'l03-align-self-check' or argv != expected:
                    problems.append('only l03-align-self-check may carry the self-check exemption')
        elif entry.get('kind') == 'preview':
            if not isinstance(entry.get('port'), int) or not 1024 <= entry['port'] <= 65535:
                problems.append(f"{entry.get('id')} has an invalid localhost preview port")
            if not entry.get('skip_if_unavailable'):
                problems.append(f"{entry.get('id')} must skip explicitly when its preview is down")
            if not all(str(route).startswith('/') for route in entry.get('routes', [])):
                problems.append(f"{entry.get('id')} contains a non-local route")
        else:
            problems.append(f"{entry.get('id')} has unsupported local step kind")

    if plan.get('platform_items_source') != ITEMS_PATH.name:
        problems.append('plan platform_items_source must name the checked-in open-items file')
    # This relation, not exact equality, avoids a deadlock when evidence is written after the suites.
    if STATE_PATH.is_file():
        state = load(STATE_PATH)
        recorded = {row.get('id') for row in state.get('local_steps', [])}
        if not recorded.issubset(set(local_ids)):
            problems.append('state file records local steps absent from the plan')
        state_evidence = state.get('evidence', {})
        if state_evidence.get('source_script') and state_evidence['source_script'] != 'run_offline_suites.py':
            problems.append('state evidence scope does not name the offline-suite runner')
    return plan, items_doc, problems


def render(plan=None, items_doc=None):
    plan, items_doc, problems = validate(plan, items_doc)
    if problems:
        raise ValueError('; '.join(problems))
    items_by_id = {item['id']: item for item in items_doc['items']}
    paths_by_item = {}
    for step in plan['steps']:
        for item_id in step['covers']:
            paths_by_item[item_id] = step['id']

    lines = [
        '# AUTO-ALIGN EXECUTION PLAN — V16.9',
        '',
        f"As of: {plan['as_of']}",
        '',
        plan['scope'],
        '',
        '**This is a completion path, not a claim that an account, provider, service or control is configured.** '
        'The runner is local-only. Owner decisions stay with the owner; no installation, purchase, provider connection, '
        'content publishing, GitHub comment/close, push or merge is performed automatically.',
        '',
        f"Plan: **{len(plan['steps'])} steps · {len(plan['phases'])} phases · "
        f"{len(items_by_id)} open platform items mapped · {len(plan['local_sequence'])} local checks**.",
        '',
        '## Phase 0 — automatic readiness and publication',
        '',
        'The two local/preview checks are runnable without owner credentials. Publishing is a separate agent action '
        'after review and is not triggered by `--run`.',
        '',
    ]
    phase_map = {phase['number']: phase for phase in plan['phases']}
    for phase_number in range(5):
        phase = phase_map[phase_number]
        if phase_number:
            lines.extend([f"## Phase {phase_number} — {phase['name']}", ''])
        for step_id in phase['step_ids']:
            step = next(value for value in plan['steps'] if value['id'] == step_id)
            lines.extend([
                f"### {step['id']} — {step['title']}",
                '',
                f"- **Owner:** {step['actor']} · **Initial state:** `{step['status']}`",
                f"- **Action:** {step['action']}",
                f"- **Verify:** {step['verify']}",
                f"- **Done when:** {step['done_when']}",
                f"- **Evidence:** `{step['evidence_path']}`",
            ])
            if step['covers']:
                names = ', '.join(f"`{item_id}`" for item_id in step['covers'])
                lines.append(f'- **Open-item coverage:** {names}')
            lines.append('')
    lines += [
        '## Fourteen-step local sequence',
        '',
        'Run from the repository root with `python3 ops/vyomaraj-core/handover/auto_align.py --run`. '
        'Commands are fixed argv lists (no shell); preview checks are loopback-only and record an explicit skip '
        'if the service is not already running.',
        '',
        '| Step | Check | Mode |', '|---|---|---|',
    ]
    for entry in plan['local_sequence']:
        detail = ' '.join(entry.get('argv', [])) if entry['kind'] == 'command' else f"localhost:{entry['port']} routes"
        lines.append(f"| `{entry['id']}` | {entry['purpose']} | `{detail}` |")
    lines += [
        '',
        '## Safety and evidence rules',
        '',
    ]
    lines.extend(f"- {rule}." for rule in plan['safety']['automatic_actions'])
    lines.extend(f"- Never automatic: {rule}." for rule in plan['safety']['never_automatic'])
    lines += [
        '',
        'Every open item has exactly one step id in the generated platform-check report. A step moves to DONE only '
        'after its `done_when` evidence is reviewed and stored; the initial status in this plan is not a completion claim.',
        '',
        '## Source map for open items',
        '',
        '| Item | Area | Open check | Completion step |', '|---|---|---|---|',
    ]
    for item in items_doc['items']:
        lines.append(f"| `{item['id']}` | {item['area']} | {item['item']} | `{paths_by_item[item['id']]}` |")
    return '\n'.join(lines) + '\n'


def port_is_open(port):
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=0.35):
            return True
    except OSError:
        return False


def run_preview(entry):
    port = entry['port']
    if not port_is_open(port):
        return {'id': entry['id'], 'status': 'SKIPPED_PREVIEW_UNAVAILABLE', 'ok': True,
                'detail': f'localhost:{port} is not listening; expected optional-preview skip.'}
    details = []
    for route in entry['routes']:
        url = f'http://127.0.0.1:{port}{route}'
        try:
            with urllib.request.urlopen(url, timeout=4) as response:
                body = response.read()
                if response.status != 200:
                    raise RuntimeError(f'{route}: HTTP {response.status}')
                marker = MARKERS.get(route)
                if marker and marker.encode('utf-8') not in body:
                    raise RuntimeError(f'{route}: expected content marker missing')
                details.append(f'{route}=200')
        except (OSError, urllib.error.HTTPError, RuntimeError) as exc:
            return {'id': entry['id'], 'status': 'FAIL', 'ok': False, 'detail': str(exc)}
    return {'id': entry['id'], 'status': 'OK', 'ok': True, 'detail': ', '.join(details)}


def run_command(entry):
    argv = entry['argv']
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        return {'id': entry['id'], 'status': 'FAIL', 'ok': False, 'exit_code': 124,
                'duration_seconds': round(time.monotonic() - started, 3), 'detail': 'command timed out'}
    output = (proc.stdout or '') + (proc.stderr or '')
    return {'id': entry['id'], 'status': 'OK' if proc.returncode == 0 else 'FAIL',
            'ok': proc.returncode == 0, 'exit_code': proc.returncode,
            'duration_seconds': round(time.monotonic() - started, 3),
            'detail': '\n'.join(output.strip().splitlines()[-18:])[:5000]}


def write_state(results):
    try:
        evidence = load(EVIDENCE_PATH)
        summary = {
            'source_script': 'run_offline_suites.py',
            'python_tests_total': evidence.get('python_tests_total'),
            'python_suite_count': len(evidence.get('python_suites', [])),
            'python_suites': evidence.get('python_suites', []),
            'node_check_count': len(evidence.get('node_checks', [])),
            'builder_count': len(evidence.get('builders', [])),
            'failures': evidence.get('failures', []),
            'sha256': sha256(EVIDENCE_PATH),
        }
    except (OSError, ValueError):
        summary = {'source_script': 'run_offline_suites.py', 'unavailable': True}
    ok = all(row.get('ok') for row in results)
    state = {
        'schema_version': 1,
        'recorded_at_utc': dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        'scope': 'LOCAL_AUTO_ALIGN_RUN_ONLY; no provider, install, purchase, publishing or GitHub mutation',
        'branch': subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=ROOT,
                                 capture_output=True, text=True).stdout.strip(),
        'plan_sha256': sha256(PLAN_PATH),
        'open_items_source_sha256': sha256(ITEMS_PATH),
        'counts': {
            'plan_steps': REQUIRED_STEP_COUNT,
            'phases': REQUIRED_PHASE_COUNT,
            'open_items_covered': REQUIRED_OPEN_ITEM_COUNT,
            'local_steps': len(results),
            'local_steps_ok_or_expected_skip': sum(bool(row.get('ok')) for row in results),
            'failed': sum(not bool(row.get('ok')) for row in results),
            'owner_steps_awaiting_action': sum(1 for step in load(PLAN_PATH)['steps'] if step['status'] == 'OWNER_ACTION_REQUIRED'),
            'agent_steps_awaiting_action': sum(1 for step in load(PLAN_PATH)['steps'] if step['status'] == 'AWAITING_AGENT'),
        },
        'local_steps': results,
        'evidence': summary,
        'limits': ['Skipped preview checks are not live verification.',
                   'This local run does not close any owner step or publish/merge a change.'],
        'result': 'OK' if ok else 'FAILED',
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    print(f"wrote {STATE_PATH.relative_to(ROOT)} ({STATE_PATH.stat().st_size} bytes)")
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--run', action='store_true', help='run the allowlisted local sequence and write state evidence')
    group.add_argument('--plan', action='store_true', help='print the human-readable plan')
    group.add_argument('--render', action='store_true', help='write the generated plan page')
    group.add_argument('--check', action='store_true', help='validate the plan, coverage and rendered page; never write')
    args = parser.parse_args()
    plan, items_doc, problems = validate()
    if problems:
        for problem in problems:
            print('FAIL:', problem)
        return 1
    if args.plan:
        print(render(plan, items_doc), end='')
        return 0
    rendered = render(plan, items_doc)
    if args.render:
        REPORT_PATH.write_text(rendered, encoding='utf-8')
        print(f'Wrote {REPORT_PATH.relative_to(ROOT)} ({REPORT_PATH.stat().st_size} bytes)')
        return 0
    if args.check or not args.run:
        current = REPORT_PATH.read_text(encoding='utf-8') if REPORT_PATH.is_file() else ''
        if current != rendered:
            print(f'FAIL: {REPORT_PATH.name} is out of date; run auto_align.py --render')
            return 1
        print(f'OK: {len(plan["steps"])} steps, {len(plan["phases"])} phases, '
              f'{len(items_doc["items"])} open items covered, {len(plan["local_sequence"])} local checks')
        return 0

    results = []
    for entry in plan['local_sequence']:
        result = run_preview(entry) if entry['kind'] == 'preview' else run_command(entry)
        results.append(result)
        print(f"{result['status']:>30}  {entry['id']} — {entry['purpose']}")
        if result.get('detail'):
            for line in result['detail'].splitlines()[-4:]:
                print('    ' + line)
    state = write_state(results)
    good = state['counts']['local_steps_ok_or_expected_skip']
    total = state['counts']['local_steps']
    print(f"{good}/{total} local steps OK; {state['counts']['failed']} failed")
    evidence = state['evidence']
    if not evidence.get('unavailable'):
        print(f"Evidence: {evidence.get('python_tests_total')} tests / {evidence.get('python_suite_count')} suites / "
              f"{evidence.get('node_check_count')} node checks / {evidence.get('builder_count')} builders; "
              f"failures {len(evidence.get('failures', []))}")
    return 0 if state['result'] == 'OK' else 1


if __name__ == '__main__':
    raise SystemExit(main())
