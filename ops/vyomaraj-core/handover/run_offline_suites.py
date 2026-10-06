#!/usr/bin/env python3
"""Run the repository's offline verification suites and regenerate TEST_EVIDENCE.

This is the single local evidence command used by auto-align and CI. Results are recorded only
after the checks finish; evidence is not used as an exact precondition for the tests that create it.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / 'TEST_EVIDENCE_2026_10_04.json'
SUITES = [
    'ops/dr',
    'ops/vyomaraj-core/handover',
    'ops/vyomaraj-core/liquor-bar',
    'ops/vyomaraj-core/experience',
    'ops/vyomaraj-core/research',
    'ops/vyomaraj-core/agents',
    'ops/availability',
    'ops/vyomaraj-core/approvals',
    'ops/vyomaraj-core/finance',
    'ops/vyomaraj-core/upgrades',
    'ops/vyomaraj-core/ledger',
]
NODE_COMMANDS = [
    ['node', '--test', 'ops/vyomaraj-core/test_safe_metadata.cjs'],
    ['node', '--check', 'ops/vyomaraj-core/liquor-bar/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/bhakti-experience/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/music-experience/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/film-experience/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/comics-experience/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/approvals/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/finance/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/upgrades/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/research/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/agents/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/aghor-experience/app.js'],
]
BUILDER_COMMANDS = [
    ['python3', 'ops/vyomaraj-core/handover/rebuild_handover.py', '--check'],
    ['python3', 'ops/vyomaraj-core/agents/rebuild_registry.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_dr_sync_report.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_transfer_package.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_post_pr25_package.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_stack_record.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/architecture_diagram.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_market_readiness.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_full_handover.py', '--check'],
    ['python3', 'ops/vyomaraj-core/experience/voice_enrollment.py', '--audit'],
    ['python3', 'ops/vyomaraj-core/handover/build_configuration_report.py', '--check'],
    ['python3', 'ops/vyomaraj-core/experience/rebuild_contents.py', '--check'],
    ['python3', 'ops/vyomaraj-core/agents/inheritance_audit.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_platform_check.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_issue_ledger.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/auto_align.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/check_language_policy.py', '--check'],
    ['python3', '-m', 'json.tool', 'ops/vyomaraj-core/handover/AUTO_ALIGN_NEXT_SESSION.json'],
    ['bash', '-n', 'ops/dr/run-dr.sh', 'ops/dr/failover-controller.sh', 'ops/vyomaraj-core/upgrades/upgrade-controller.sh'],
]
SECRET = re.compile(r'(ghp_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|x-access-token:[^@\s]+@'
                    r'|(?:token|secret|password|pat)[=:\s]+[A-Za-z0-9_\-\.]{12,})', re.IGNORECASE)


def redact(text):
    return SECRET.sub('REDACTED', text)


def tail(text, limit=2500):
    return '\n'.join(line for line in text.splitlines()[-20:] if line.strip())[:limit]


def execute(argv):
    try:
        proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=1800)
        output = redact((proc.stdout or '') + (proc.stderr or ''))
        return proc.returncode, output
    except subprocess.TimeoutExpired as exc:
        output = redact((exc.stdout or '') + (exc.stderr or '')) if isinstance(exc.stdout, str) else 'command timed out'
        return 124, output + '\ncommand timed out'
    except OSError as exc:
        return 127, f'could not start command: {exc}'


def check_recorded_evidence():
    if not EVIDENCE.is_file():
        return ['TEST_EVIDENCE is missing; run run_offline_suites.py first']
    try:
        data = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return [f'TEST_EVIDENCE is not valid JSON: {exc}']
    problems = []
    suite_paths = set(SUITES)
    recorded = data.get('python_suites', [])
    if any(row.get('path') not in suite_paths for row in recorded):
        problems.append('recorded Python suite is not in this runner\'s configured suite list')
    total = sum(int(row.get('ran', 0)) for row in recorded)
    if total != data.get('python_tests_total'):
        problems.append('recorded Python total does not equal the sum of the recorded suite counts')
    node_commands = {' '.join(command) for command in NODE_COMMANDS}
    builder_commands = {' '.join(command) for command in BUILDER_COMMANDS}
    if any(row.get('command') not in node_commands for row in data.get('node_checks', [])):
        problems.append('recorded Node check is not in this runner\'s configured command list')
    if any(row.get('command') not in builder_commands for row in data.get('builders', [])):
        problems.append('recorded builder is not in this runner\'s configured command list')
    if len(recorded) > len(SUITES) or len(data.get('node_checks', [])) > len(NODE_COMMANDS) or len(data.get('builders', [])) > len(BUILDER_COMMANDS):
        problems.append('recorded evidence exceeds the scope of this runner')
    for section in ('python_suites', 'node_checks', 'builders'):
        if any(row.get('result') != 'OK' for row in data.get(section, [])):
            problems.append(f'{section} contains a non-OK result')
    if data.get('failures'):
        problems.append('recorded evidence contains failures')
    return problems


def github_emit(kind, title, message):
    safe = message.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print(f'::{kind} title={title}::{safe}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='validate the last evidence file without running tests')
    modes.add_argument('--ci', action='store_true', help='run checks and emit compact GitHub annotations')
    args = parser.parse_args()
    if args.check:
        problems = check_recorded_evidence()
        if problems:
            for problem in problems:
                print('FAIL:', problem)
            return 1
        data = json.loads(EVIDENCE.read_text(encoding='utf-8'))
        print(f"OK: evidence is internally consistent ({data['python_tests_total']} Python tests; "
              f"{len(data['python_suites'])} suites, {len(data['node_checks'])} Node checks, "
              f"{len(data['builders'])} builders)")
        return 0

    failures = []
    suites = []
    total_tests = 0
    for path in SUITES:
        command = ['python3', '-m', 'unittest', 'discover', '-s', path, '-p', 'test_*.py', '-v']
        code, output = execute(command)
        match = re.search(r'Ran (\d+) tests?', output)
        ran = int(match.group(1)) if match else 0
        total_tests += ran
        row = {'path': path, 'command': ' '.join(command), 'ran': ran,
               'result': 'OK' if code == 0 else f'FAILED({code})',
               'tail': tail(output)}
        suites.append(row)
        print(f"{'OK' if code == 0 else 'FAIL'}: {path} — {ran} tests")
        if code:
            failures.append({'kind': 'python_suite', 'command': row['command'], 'exit_code': code, 'tail': row['tail']})

    node_results = []
    for command in NODE_COMMANDS:
        code, output = execute(command)
        row = {'command': ' '.join(command), 'result': 'OK' if code == 0 else f'FAILED({code})',
               'tail': tail(output, 1200)}
        node_results.append(row)
        print(f"{'OK' if code == 0 else 'FAIL'}: {' '.join(command)}")
        if code:
            failures.append({'kind': 'node_check', 'command': row['command'], 'exit_code': code, 'tail': row['tail']})

    builder_results = []
    for command in BUILDER_COMMANDS:
        code, output = execute(command)
        row = {'command': ' '.join(command), 'result': 'OK' if code == 0 else f'FAILED({code})',
               'tail': tail(output, 1200)}
        builder_results.append(row)
        print(f"{'OK' if code == 0 else 'FAIL'}: {' '.join(command)}")
        if code:
            failures.append({'kind': 'builder', 'command': row['command'], 'exit_code': code, 'tail': row['tail']})

    evidence = {
        'recorded_at_utc': dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        'scope': 'Offline local suite set; generated only after the checks below have completed. No external provider, publishing or DR mutation is performed.',
        'source_script': 'ops/vyomaraj-core/handover/run_offline_suites.py',
        'python_suites': suites,
        'python_tests_total': total_tests,
        'node_checks': node_results,
        'builders': builder_results,
        'failures': failures,
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {EVIDENCE.relative_to(ROOT)} ({total_tests} tests; '
          f'{len(suites)} suites; {len(node_results)} Node checks; {len(builder_results)} builders)')
    if args.ci:
        summary = f'{total_tests} Python tests across {len(suites)} suites; {len(node_results)} Node checks; {len(builder_results)} builders; {len(failures)} failures'
        github_emit('notice' if not failures else 'error', 'offline suite summary', summary)
        for failure in failures[:3]:
            github_emit('error', f"failed: {failure['command'][:120]}", failure['tail'])
    print(f'{len(suites) + len(node_results) + len(builder_results) - len(failures)}/'
          f'{len(suites) + len(node_results) + len(builder_results)} suites/checks/builders passed')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
