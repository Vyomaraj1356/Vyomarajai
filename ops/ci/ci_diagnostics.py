#!/usr/bin/env python3
"""CI wrapper for the shared local auto-align and offline-suite runners.

The offline harness lives in run_offline_suites.py so local and CI evidence use the same command
list. This wrapper keeps readable, redacted GitHub annotations and the short-lived log artifact.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMANDS = [
    ['python3', 'ops/vyomaraj-core/handover/auto_align.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_issue_ledger.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/run_offline_suites.py', '--ci'],
]
SECRET = re.compile(r'(ghp_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|x-access-token:[^@\s]+@'
                    r'|(?:token|secret|password|pat)[=:\s]+[A-Za-z0-9_\-\.]{12,})', re.IGNORECASE)


def redact(text):
    return SECRET.sub('REDACTED', text)


def emit(kind, title, message):
    safe = message.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print(f'::{kind} title={title}::{safe}', flush=True)


def main():
    failures, results, log = [], [], []
    for command in COMMANDS:
        try:
            proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=1800)
            output = redact((proc.stdout or '') + (proc.stderr or ''))
            code = proc.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            output, code = f'{type(exc).__name__}: command could not complete', 1
        status = 'OK' if code == 0 else f'FAILED({code})'
        results.append((status, ' '.join(command)))
        log.append(f'$ {" ".join(command)}\n{output}\n--- exit {code} ---\n')
        if code:
            failures.append((' '.join(command), output, code))
    (ROOT / 'ci-diagnostics.log').write_text(''.join(log), encoding='utf-8')
    emit('notice' if not failures else 'error', 'offline suites summary',
         '; '.join(f'{status}: {command}' for status, command in results))
    for command, output, code in failures[:3]:
        tail = '\n'.join(output.splitlines()[-12:])[:1600]
        emit('error', f'failed: {command[:120]}', f'exit={code}\n{tail}')
    print(f'{len(COMMANDS) - len(failures)}/{len(COMMANDS)} shared checks passed', flush=True)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
