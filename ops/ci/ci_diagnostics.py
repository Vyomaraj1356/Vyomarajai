#!/usr/bin/env python3
"""Run the offline suite set and surface failures as readable workflow annotations.

Some sandboxes cannot download Actions logs (the log endpoints return EOF), so this job prints
a compact, sanitized result as check-run annotations, which stay readable through the API.
Credential-free by construction: it never reads environment secrets, only the repository.
"""
import re
import subprocess
import sys
from pathlib import Path

COMMANDS = [
    ['python3', '-m', 'unittest', 'discover', '-s', 'ops/dr', '-p', 'test_*.py', '-v'],
    ['python3', 'ops/vyomaraj-core/handover/rebuild_handover.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_configuration_report.py', '--check'],
    ['python3', 'ops/vyomaraj-core/handover/build_transfer_package.py', '--check'],
    ['python3', '-m', 'unittest', 'discover', '-s', 'ops/vyomaraj-core/handover', '-p', 'test_*.py', '-v'],
    ['node', '--test', 'ops/vyomaraj-core/test_safe_metadata.cjs'],
    ['python3', '-m', 'unittest', 'discover', '-s', 'ops/vyomaraj-core/liquor-bar', '-p', 'test_*.py', '-v'],
    ['node', '--check', 'ops/vyomaraj-core/liquor-bar/app.js'],
    ['python3', '-m', 'unittest', 'discover', '-s', 'ops/vyomaraj-core/experience', '-p', 'test_*.py', '-v'],
    ['node', '--check', 'ops/vyomaraj-core/bhakti-experience/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/music-experience/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/film-experience/app.js'],
    ['python3', '-m', 'unittest', 'discover', '-s', 'ops/vyomaraj-core/research', '-p', 'test_*.py', '-v'],
    ['node', '--check', 'ops/vyomaraj-core/research/app.js'],
    ['python3', 'ops/vyomaraj-core/agents/rebuild_registry.py', '--check'],
    ['python3', '-m', 'unittest', 'discover', '-s', 'ops/vyomaraj-core/agents', '-p', 'test_*.py', '-v'],
    ['node', '--check', 'ops/vyomaraj-core/agents/app.js'],
    ['node', '--check', 'ops/vyomaraj-core/aghor-experience/app.js'],
    ['python3', '-m', 'unittest', 'discover', '-s', 'ops/availability', '-p', 'test_*.py', '-v'],
    ['bash', '-n', 'ops/dr/run-dr.sh', 'ops/dr/failover-controller.sh'],
]
SECRET = re.compile(r'(ghp_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|x-access-token:[^@\s]+@|'
                    r'(?i)(token|secret|password|pat)[=:\s]+[A-Za-z0-9_\-\.]{12,})')


def redact(text):
    return SECRET.sub('REDACTED', text)


def emit(kind, title, message):
    """GitHub workflow command; newlines and percent signs must be escaped."""
    safe = message.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print(f'::{kind} title={title}::{safe}', flush=True)


def tail(text, limit=1200):
    lines = [line for line in text.splitlines() if line.strip()]
    return '\n'.join(lines[-12:])[:limit]


def main():
    failures, results, log = [], [], []
    for command in COMMANDS:
        proc = subprocess.run(command, capture_output=True, text=True)
        output = redact((proc.stdout or '') + (proc.stderr or ''))
        status = 'OK' if proc.returncode == 0 else f'FAILED({proc.returncode})'
        results.append((status, ' '.join(command)))
        log.append(f'$ {" ".join(command)}\n{output}\n--- exit {proc.returncode} ---\n')
        if proc.returncode != 0:
            failures.append((' '.join(command), output, proc.returncode))
    Path('ci-diagnostics.log').write_text(''.join(log))
    summary = '; '.join(f'{status}: {cmd}' for status, cmd in results)
    emit('notice', 'offline suites summary', summary[:6000])
    for command, output, code in failures[:3]:
        emit('error', f'failed: {command[:120]}', f'exit={code}\n{tail(output)}')
    print(f'{len(COMMANDS) - len(failures)}/{len(COMMANDS)} commands passed', flush=True)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
