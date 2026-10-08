#!/usr/bin/env python3
"""Guard the two ways a gate in this repository silently stopped gating.

Both defects below shipped to main on 7 October, survived review, and were invisible to
`bash -n`, to `py_compile` and to the offline suite. Each is cheap to detect statically.

1. INVISIBLE TESTS. `tests/` is executed by `unittest discover`, which only collects
   `unittest.TestCase` subclasses. PR #47 rewrote `tests/test_agent_capability_inheritance.py`
   as bare pytest functions, so discover stopped collecting the module entirely and the
   offline suite lost eight tests without any failure being reported. The only job that
   still ran them used pytest, and it had been failing on every branch.

2. LITERAL `\\$` IN SHELL. Five scripts were written with `\\${BASH_SOURCE[0]}` instead of
   `${BASH_SOURCE[0]}`. `$ROOT` then resolved to the wrong directory, every required
   contract reported MISSING, and the gate still exited 0 — a gate that always passed.
   `bash -n` accepts `\\$` as a valid escape, so syntax checking could never catch it.

Exit 0 when clean, 1 when a finding is present. Read-only; no network.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEST_DIRS = ('tests',)
# A guard that inspects nothing reports PASS, which is the failure mode this file exists to
# prevent — the first draft used parents[2], silently scanned an empty ops/tests, and passed.
# These floors make a mis-resolved ROOT or a moved directory an error instead of a green tick.
MIN_TEST_FILES = 8
MIN_SHELL_FILES = 20
# Scripts whose whole purpose is to refuse unless a contract is met. A silently
# mis-resolved path in one of these turns a deny-by-default gate into an allow-all.
SHELL_GLOBS = ('ops/**/*.sh',)
# `\$` is legitimate inside a single-quoted string, a heredoc body or a regex, so the
# guard targets the specific construct that broke: an escaped expansion of a variable.
BAD_ESCAPE = re.compile(r'\\\$(?=[A-Za-z_{(])')


def _is_test_case(node: ast.ClassDef) -> bool:
    for base in node.bases:
        name = base.attr if isinstance(base, ast.Attribute) else getattr(base, 'id', '')
        if name in ('TestCase', 'IsolatedAsyncioTestCase', 'FunctionTestCase'):
            return True
        # Subclasses of a local base class that itself extends TestCase are resolved by
        # the discover run itself; treat any explicit base as sufficient here.
    return bool(node.bases)


def check_discoverable_tests() -> list[str]:
    findings = []
    inspected = 0
    for directory in TEST_DIRS:
        base = ROOT / directory
        if not base.is_dir():
            continue
        for path in sorted(base.rglob('test_*.py')):
            rel = path.relative_to(ROOT).as_posix()
            inspected += 1
            try:
                tree = ast.parse(path.read_text(encoding='utf-8'), filename=rel)
            except SyntaxError as exc:
                findings.append(f'{rel}: does not parse ({exc.msg})')
                continue
            classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and _is_test_case(n)]
            functions = [n for n in tree.body
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and n.name.startswith('test_')]
            if classes:
                continue
            if functions:
                findings.append(
                    f'{rel}: defines {len(functions)} module-level test function(s) and no '
                    'unittest.TestCase subclass, so "unittest discover" collects nothing from '
                    'it. Wrap them in a TestCase.')
            else:
                findings.append(f'{rel}: contains no collectable tests.')
    if inspected < MIN_TEST_FILES:
        findings.append(
            f'inspected only {inspected} test file(s) under {TEST_DIRS} relative to {ROOT}, '
            f'expected at least {MIN_TEST_FILES}. The root is mis-resolved or tests moved; '
            'refusing to report PASS without having read anything.')
    return findings


def check_shell_escapes() -> list[str]:
    findings = []
    seen: set[str] = set()
    for pattern in SHELL_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            if rel in seen or not path.is_file():
                continue
            seen.add(rel)
            for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                if BAD_ESCAPE.search(line):
                    findings.append(
                        rf'{rel}:{number}: literal \$ before a variable expansion — the '
                        'expansion will not happen. Remove the backslash.')
    if len(seen) < MIN_SHELL_FILES:
        findings.append(
            f'inspected only {len(seen)} shell script(s) matching {SHELL_GLOBS} relative to '
            f'{ROOT}, expected at least {MIN_SHELL_FILES}. The root is mis-resolved; refusing '
            'to report PASS without having read anything.')
    return findings


CHECKS = (('unittest-discoverable tests', check_discoverable_tests),
          ('shell variable expansion', check_shell_escapes))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                        help='exit non-zero on any finding (default behaviour)')
    parser.parse_args()

    total = 0
    for title, check in CHECKS:
        findings = check()
        total += len(findings)
        status = 'PASS' if not findings else f'FAIL ({len(findings)})'
        print(f'{status}: {title}')
        for finding in findings:
            print(f'  - {finding}')
    if total:
        print(f'\nSUITE INTEGRITY: FAIL ({total} finding(s))')
        return 1
    print('\nSUITE INTEGRITY: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
