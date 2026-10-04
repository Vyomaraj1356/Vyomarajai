#!/usr/bin/env python3
"""Check repository text files for UTF-8 validity and embedded NUL bytes.

This gate prints paths and counts only; it never emits source text or reads known environment
files. Binary and generated archive formats are excluded.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEXT_SUFFIXES = {'.py', '.md', '.txt', '.json', '.html', '.js', '.css', '.yml', '.yaml', '.sh', '.cjs', '.mjs', '.toml'}
SKIP_NAMES = {'dr.env', 'jarvis.env', '.env', 'local.env'}


def candidates():
    proc = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                          cwd=ROOT, capture_output=True, check=True)
    for raw in proc.stdout.split(b'\0'):
        if not raw:
            continue
        path = Path(raw.decode('utf-8', errors='strict'))
        if path.name.lower() in SKIP_NAMES or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if '.git' in path.parts or any(part.startswith('.') and part in {'.venv', '.cache', 'node_modules'}
                                        for part in path.parts):
            continue
        yield path


def check():
    problems = []
    count = 0
    for relative in candidates():
        path = ROOT / relative
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b'\x00' in data:
            problems.append(f'{relative.as_posix()}: embedded NUL byte')
            continue
        try:
            data.decode('utf-8')
        except UnicodeDecodeError:
            problems.append(f'{relative.as_posix()}: not valid UTF-8')
            continue
        count += 1
    return count, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='check only; never rewrite')
    args = parser.parse_args()
    try:
        count, problems = check()
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        parser.exit(2, f'ERROR: language gate could not enumerate repository files: {exc}\n')
    for problem in problems:
        print('FAIL:', problem)
    if problems:
        return 1
    print(f'OK: {count} repository text files are valid UTF-8 with no NUL bytes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
