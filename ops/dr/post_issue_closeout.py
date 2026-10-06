#!/usr/bin/env python3
"""Post (or dry-run) the issue #6 close-out with a credential that has issues=write.

The Arena GitHub connection in this sandbox is issues=read only: every comment and
close attempt returns HTTP 403 'Resource not accessible by integration' (four live
attempts, recorded in ops/dr/ISSUE_6_ACCESS_RECHECK_2026_10_06.json). That write is
therefore an owner action. This tool makes the step explicit and repeatable instead
of a manual retry:

  * ``--check``  — offline. Verifies the close-out comment file cites check-runs that
    actually exist in the DR record, so a credential holder cannot publish a comment
    that points at evidence the repository does not hold.
  * ``--post``   — comments on issue #6 with the file, then closes the issue. Comment
    first, close only if the comment succeeded. Requires `gh` authenticated with a
    credential that has issues=write.
  * default      — prints the plan and exits 3 (blocked: owner credential required).

No token is read, stored or printed by this script; it shells out to `gh`, which uses
its own credential store.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RECORD = HERE / 'DEPLOYED_MATCH_2026_10_04.json'
RECHECK = HERE / 'ISSUE_6_ACCESS_RECHECK_2026_10_06.json'
COMMENT = HERE / 'ISSUE_6_CLOSEOUT_COMMENT_2026_10_06.md'
ISSUE = 6
EXIT_BLOCKED_OWNER = 3

LONG_ID = re.compile(r'\b(\d{9,})\b')


def cited_ids(text):
    """Every long id (check-run or workflow run) the comment points at."""
    return sorted({int(value) for value in LONG_ID.findall(text)})


def known_check_runs(record):
    known = {int(o['check_run_id']) for o in record['observations']}
    known |= {int(o['check_run_id']) for o in record.get('blocked_runs', [])}
    return known


def known_ids(record, extra_paths=(RECHECK,)):
    """Ids the record holds anywhere: rows, blocked runs, windows, notes — plus the
    checked-in access recheck, which holds the read-only probe evidence."""
    blob = json.dumps(record)
    for path in extra_paths:
        if Path(path).is_file():
            blob += Path(path).read_text(encoding='utf-8')
    return {int(value) for value in LONG_ID.findall(blob)}


def validate(comment_text, record, extra_paths=(RECHECK,)):
    """Every id the comment cites must exist in the evidence it summarizes."""
    known = known_ids(record, extra_paths)
    problems = []
    missing = [value for value in cited_ids(comment_text) if value not in known]
    if missing:
        problems.append(f'comment cites check-runs or runs absent from the record: {missing}')
    for required in ('status=MATCH', 'traffic_switched=NONE'):
        if required not in comment_text:
            problems.append(f'comment does not state "{required}"')
    if 'close' not in comment_text.lower():
        problems.append('comment does not read as a close-out')
    return problems


def run(command):
    proc = subprocess.run(command, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def post(comment_path=COMMENT, runner=run):
    """Comment on the issue, then close it. Returns the observed outcome per step."""
    code, output = runner(['gh', 'issue', 'comment', str(ISSUE), '--body-file', str(comment_path)])
    result = {'comment': {'exit_code': code, 'output': output}, 'closed': False}
    if code != 0:
        result['close'] = {'exit_code': None, 'output': 'not attempted: the comment step did not succeed'}
        result['blocked'] = True
        return result
    code, output = runner(['gh', 'issue', 'close', str(ISSUE)])
    result['close'] = {'exit_code': code, 'output': output}
    result['closed'] = code == 0
    result['blocked'] = not result['closed']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='offline validation of the comment against the record')
    modes.add_argument('--post', action='store_true', help='comment and close issue #6 (needs issues=write)')
    parser.add_argument('--comment', default=str(COMMENT))
    parser.add_argument('--record', default=str(RECORD))
    parser.add_argument('--recheck', default=str(RECHECK))
    args = parser.parse_args()

    comment_path = Path(args.comment)
    record = json.loads(Path(args.record).read_text(encoding='utf-8'))
    recheck = Path(args.recheck)
    problems = validate(comment_path.read_text(encoding='utf-8'), record,
                        extra_paths=(recheck,) if recheck else ())
    if problems:
        for problem in problems:
            print(f'FAIL: {problem}')
        return 1
    print(f'OK: {comment_path.name} cites {len(cited_ids(comment_path.read_text(encoding="utf-8")))} '
          f'check-runs/runs, all present in {Path(args.record).name} or '
          f'{Path(args.recheck).name if args.recheck else "(no recheck)"}.')
    if args.check:
        return 0
    if not args.post:
        print(f'Would run: gh issue comment {ISSUE} --body-file {comment_path}')
        print(f'Then:     gh issue close {ISSUE}')
        print('Blocked: this connection has issues=read only (403 verified). Grant issues=write or run '
              'this on a credential that has it, then add --post.')
        return EXIT_BLOCKED_OWNER
    outcome = post(comment_path)
    print(json.dumps(outcome, indent=2))
    if outcome.get('blocked'):
        print('BLOCKED: the write did not succeed; issue #6 stays open and no close is claimed.')
        return EXIT_BLOCKED_OWNER
    print(f'DONE: issue #{ISSUE} commented and closed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
