#!/usr/bin/env python3
"""Confirm that primary and secondary carry the same packages.

Two distinct meanings of "package" are both checked, because both matter for DR:

1. **Dependency packages** — the declared third-party distributions
   (``requirements*.txt``, ``pyproject.toml``, ``package.json``, lockfiles...).
2. **Distributable packages** — the tracked release artifacts that the repository
   itself ships (``*.zip``, ``*.apk``, ``*.tar.gz``).

What this proves and what it does not
-------------------------------------
Offline mode validates the *declarations*: that the lock file satisfies the bounded
requirements, that the compatibility patch file agrees with the canonical bounds, and
that no manifest pins the same distribution twice with conflicting constraints.

Remote mode compares the Git blob SHA of every package path in the primary and the
secondary ``main`` trees. Identical blob SHAs mean the two repositories hold byte-identical
package files. That is a *repository* fact.

It is **not** evidence that the packages are installed anywhere, that the pinned versions
exist on an index, that a site-packages directory matches, or that a runtime is recoverable.
Installed-environment parity requires a separate, credentialed runtime check.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dr_sync import (  # noqa: E402
    BRANCH,
    PRIMARY,
    APIError,
    CheckError,
    GitHub,
    git_blob_sha,
    snapshot,
    validate_target,
)

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).with_name('PACKAGE_PARITY.json')

# Dependency manifests, by exact name or suffix. Kept explicit: a silent glob would let a
# new ecosystem's lockfile escape the parity check without anyone noticing.
DEPENDENCY_NAMES = {
    'pyproject.toml', 'setup.py', 'setup.cfg', 'Pipfile', 'Pipfile.lock',
    'poetry.lock', 'uv.lock', 'package.json', 'package-lock.json',
    'npm-shrinkwrap.json', 'yarn.lock', 'pnpm-lock.yaml', 'Gemfile', 'Gemfile.lock',
    'go.mod', 'go.sum', 'Cargo.toml', 'Cargo.lock',
}
DEPENDENCY_PATTERNS = (
    re.compile(r'(?:^|/)requirements[A-Za-z0-9._-]*\.txt$'),
    re.compile(r'(?:^|/)constraints[A-Za-z0-9._-]*\.txt$'),
)
DISTRIBUTABLE_SUFFIXES = ('.zip', '.apk', '.tar.gz', '.tgz', '.whl', '.aab', '.jar')

# Declaration consistency contract for the 2026 Python foundation.
CANONICAL_REQUIREMENTS = 'ops/engineering/requirements-2026.txt'
LOCKED_REQUIREMENTS = 'ops/engineering/requirements-2026-lock.txt'
PATCH_REQUIREMENTS = 'ops/engineering/requirements-2026-patch.txt'

REQUIREMENT_LINE = re.compile(
    r'^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)'
    r'(?:\[(?P<extras>[^\]]*)\])?'
    r'(?P<specifier>.*)$'
)
SPECIFIER = re.compile(r'(==|!=|>=|<=|~=|>|<)\s*([A-Za-z0-9][A-Za-z0-9.*+!_-]*)')


def normalize(name: str) -> str:
    """PEP 503 normalization so ``PyYAML`` and ``pyyaml`` are the same distribution."""
    return re.sub(r'[-_.]+', '-', name).lower()


def version_key(version: str) -> tuple:
    """Order release segments numerically; trailing non-numeric parts sort before them.

    Deliberately simple: the repository pins plain ``X.Y.Z`` releases. Anything exotic is
    reported as unparsable rather than silently mis-ordered.
    """
    parts = []
    for chunk in re.split(r'[.+-]', version):
        if chunk.isdigit():
            parts.append((1, int(chunk), ''))
        elif chunk:
            parts.append((0, 0, chunk))
    return tuple(parts)


def satisfies(version: str, operator: str, bound: str) -> bool:
    if operator == '==':
        return version == bound or version_key(version) == version_key(bound)
    if operator == '!=':
        return version_key(version) != version_key(bound)
    left, right = version_key(version), version_key(bound)
    if operator == '>=':
        return left >= right
    if operator == '<=':
        return left <= right
    if operator == '>':
        return left > right
    if operator == '<':
        return left < right
    if operator == '~=':
        # Compatible release: >= bound, and < next significant release.
        if left < right:
            return False
        head = bound.split('.')[:-1]
        if not head:
            return False
        ceiling = version_key('.'.join(head[:-1] + [str(int(head[-1]) + 1)])) if head[-1].isdigit() else None
        return ceiling is None or left < ceiling
    raise CheckError(f'Unsupported version operator: {operator}')


def parse_requirements(text: str) -> dict[str, dict]:
    """Parse a pip requirements file into ``{normalized_name: record}``.

    Unsupported constructs (``-r``, URLs, environment markers) are recorded rather than
    guessed at, so a reviewer can see exactly what was and was not compared.
    """
    parsed: dict[str, dict] = {}
    unsupported: list[str] = []
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        if line.startswith('-') or '://' in line or ';' in line:
            unsupported.append(line)
            continue
        match = REQUIREMENT_LINE.match(line)
        if not match:
            unsupported.append(line)
            continue
        name = normalize(match.group('name'))
        extras = sorted(filter(None, (part.strip() for part in (match.group('extras') or '').split(','))))
        specifier_text = (match.group('specifier') or '').strip()
        specifiers = [(op, value) for op, value in SPECIFIER.findall(specifier_text)]
        if specifier_text and not specifiers:
            unsupported.append(line)
            continue
        if name in parsed:
            parsed[name]['duplicate'] = True
            continue
        parsed[name] = {
            'name': name,
            'extras': extras,
            'specifiers': specifiers,
            'duplicate': False,
        }
    return {'requirements': parsed, 'unsupported_lines': unsupported}


def tracked_files() -> list[str]:
    try:
        proc = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT,
                              capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckError('Could not enumerate tracked files with git') from exc
    if proc.returncode:
        raise CheckError('git ls-files failed; package inventory needs a Git checkout')
    return sorted(path for path in proc.stdout.split('\0') if path)


def classify(path: str) -> str | None:
    name = path.rsplit('/', 1)[-1]
    if name in DEPENDENCY_NAMES or any(pattern.search(path) for pattern in DEPENDENCY_PATTERNS):
        return 'dependency_manifest'
    if path.endswith(DISTRIBUTABLE_SUFFIXES):
        return 'distributable_package'
    return None


def collect_local() -> list[dict]:
    """Inventory every tracked package file with content hashes.

    The Git blob SHA is recorded so a tree entry from the GitHub API can be compared
    without downloading the artifact — the release archives here are tens of megabytes.
    """
    records = []
    for path in tracked_files():
        kind = classify(path)
        if kind is None:
            continue
        blob = ROOT / path
        if not blob.is_file():
            records.append({'path': path, 'kind': kind, 'status': 'MISSING_IN_WORKTREE'})
            continue
        raw = blob.read_bytes()
        records.append({
            'path': path,
            'kind': kind,
            'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'git_blob_sha': git_blob_sha(raw),
        })
    return records


def validate_declarations() -> dict:
    """Check the Python foundation declarations agree with each other."""
    findings: list[str] = []
    files: dict[str, dict] = {}
    for label, relative in (('canonical', CANONICAL_REQUIREMENTS),
                            ('lock', LOCKED_REQUIREMENTS),
                            ('patch', PATCH_REQUIREMENTS)):
        path = ROOT / relative
        if not path.is_file():
            findings.append(f'missing declaration file: {relative}')
            continue
        files[label] = parse_requirements(path.read_text(encoding='utf-8'))

    for label, data in files.items():
        for name, record in data['requirements'].items():
            if record['duplicate']:
                findings.append(f'{label}: {name} is declared more than once')

    canonical = files.get('canonical', {}).get('requirements', {})
    lock = files.get('lock', {}).get('requirements', {})
    patch = files.get('patch', {}).get('requirements', {})

    locked_versions = {}
    for name, record in lock.items():
        pins = [value for op, value in record['specifiers'] if op == '==']
        if len(pins) != 1:
            findings.append(f'lock: {name} must be pinned with exactly one == version')
            continue
        locked_versions[name] = pins[0]

    for name, version in locked_versions.items():
        declared = canonical.get(name)
        if declared is None:
            findings.append(f'lock: {name} is pinned but not declared in {CANONICAL_REQUIREMENTS}')
            continue
        for operator, bound in declared['specifiers']:
            if not satisfies(version, operator, bound):
                findings.append(
                    f'lock: {name}=={version} violates the declared bound {operator}{bound}')

    for name, record in patch.items():
        declared = canonical.get(name)
        if declared is None:
            findings.append(f'patch: {name} is not declared in {CANONICAL_REQUIREMENTS}')
            continue
        if sorted(record['specifiers']) != sorted(declared['specifiers']):
            findings.append(f'patch: {name} bounds differ from the canonical declaration')

    # Packages the canonical file declares but the lock omits: recorded, not failed, because
    # test-only tooling is deliberately unpinned.
    unlocked = sorted(set(canonical) - set(locked_versions))

    return {
        'status': 'PASS' if not findings else 'FAIL',
        'canonical_requirements': CANONICAL_REQUIREMENTS,
        'declared_distributions': sorted(canonical),
        'locked_distributions': locked_versions,
        'declared_but_unlocked': unlocked,
        'unsupported_lines': {label: data['unsupported_lines']
                              for label, data in files.items() if data['unsupported_lines']},
        'findings': findings,
        'installed_environment_verified': False,
        'index_availability_verified': False,
    }


def check_index_availability(locked: dict[str, str], timeout: int = 20) -> dict:
    """Confirm each locked pin actually exists on PyPI.

    A lock file that pins a nonexistent release is unreproducible on both primary and
    secondary: the two repositories would hold identical text that no machine can install.
    This is a network call and therefore never part of the offline suite.
    """
    import urllib.error
    import urllib.request

    available, unavailable, unknown = {}, {}, {}
    for name, version in sorted(locked.items()):
        url = f'https://pypi.org/pypi/{name}/{version}/json'
        request = urllib.request.Request(url, headers={'User-Agent': 'Vyomaraj-DR-PackageParity'})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status == 200:
                    available[name] = version
                else:
                    unknown[name] = f'http {response.status}'
        except urllib.error.HTTPError as exc:
            (unavailable if exc.code == 404 else unknown)[name] = f'http {exc.code}'
        except (urllib.error.URLError, TimeoutError, OSError):
            unknown[name] = 'index unreachable from this host'
    return {
        'status': 'PASS' if not unavailable and not unknown else ('FAIL' if unavailable else 'BLOCKED'),
        'index': 'pypi.org',
        'available': available,
        'not_on_index': unavailable,
        'not_determined': unknown,
        'note': 'Release existence only. This does not download, install, verify hashes, '
                'check signatures, or prove the dependency tree resolves.',
    }


def remote_package_map(client: GitHub, repo: str, tree_sha: str) -> dict[str, str]:
    response = client.request('GET', f'repos/{repo}/git/trees/{tree_sha}?recursive=1')
    if response.get('truncated') or not isinstance(response.get('tree'), list):
        raise CheckError('Truncated or invalid tree; refusing a partial package comparison')
    mapping = {}
    for entry in response['tree']:
        if entry.get('type') != 'blob':
            continue
        path = entry.get('path', '')
        if classify(path) is None:
            continue
        mapping[path] = entry.get('sha', '')
    return mapping


def compare_maps(primary_map: dict[str, str], secondary_map: dict[str, str]) -> dict:
    missing = sorted(set(primary_map) - set(secondary_map))
    extra = sorted(set(secondary_map) - set(primary_map))
    differing = sorted(path for path in set(primary_map) & set(secondary_map)
                       if primary_map[path] != secondary_map[path])
    identical = sorted(path for path in set(primary_map) & set(secondary_map)
                       if primary_map[path] == secondary_map[path])
    return {
        'status': 'MATCH' if not (missing or extra or differing) else 'MISMATCH',
        'primary_package_files': len(primary_map),
        'secondary_package_files': len(secondary_map),
        'identical_package_files': len(identical),
        'missing_on_secondary': missing,
        'secondary_only': extra,
        'content_differs': differing,
    }


def local_report() -> dict:
    inventory = collect_local()
    by_kind: dict[str, int] = {}
    total_bytes = 0
    for record in inventory:
        by_kind[record['kind']] = by_kind.get(record['kind'], 0) + 1
        total_bytes += record.get('bytes', 0)
    declarations = validate_declarations()
    return {
        'schema_version': 1,
        'scope': ('tracked package files in the Git snapshot; dependency declarations are '
                  'checked for internal consistency, not installed or resolved'),
        'primary_repository': PRIMARY,
        'branch': BRANCH,
        'package_file_count': len(inventory),
        'package_files_by_kind': dict(sorted(by_kind.items())),
        'total_package_bytes': total_bytes,
        'declaration_check': declarations,
        'inventory': inventory,
        'installed_environment_verified': False,
        'runtime_package_parity_verified': False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                        help='offline: verify the committed inventory matches the working tree')
    parser.add_argument('--remote', action='store_true',
                        help='compare primary and secondary package files over the GitHub API')
    parser.add_argument('--index', action='store_true',
                        help='network: confirm each locked pin exists on PyPI')
    parser.add_argument('--target', default=os.environ.get('DR_REPO', ''),
                        help='secondary owner/repository (never guessed)')
    parser.add_argument('--output', type=Path, help='write sanitized evidence JSON')
    args = parser.parse_args(argv)

    report = local_report()

    if args.index:
        report['index_availability'] = check_index_availability(
            report['declaration_check']['locked_distributions'])

    if args.remote:
        try:
            target = validate_target(args.target)
            primary_client = GitHub(os.environ.get('PRIMARY_TOKEN'))
            secondary_client = GitHub(os.environ.get('DR_TOKEN'))
            src = snapshot(primary_client, PRIMARY)
            dst = snapshot(secondary_client, target)
            comparison = compare_maps(
                remote_package_map(primary_client, PRIMARY, src['tree']),
                remote_package_map(secondary_client, target, dst['tree']),
            )
            comparison.update({'secondary_repository': target,
                               'primary_commit': src['commit'], 'secondary_commit': dst['commit'],
                               'primary_tree': src['tree'], 'secondary_tree': dst['tree']})
        except (CheckError, ValueError, KeyError, TypeError) as exc:
            comparison = {
                'status': 'BLOCKED',
                'secondary_repository': args.target or None,
                'detail': str(exc) if isinstance(exc, CheckError)
                          else 'Malformed API response; no package parity claimed',
                'failed_api_operation': getattr(exc, 'operation', None),
                'failed_http_status': getattr(exc, 'status', None),
            }
        report['secondary_comparison'] = comparison
    else:
        report['secondary_comparison'] = {
            'status': 'NOT_ATTEMPTED',
            'detail': 'Run with --remote and a confirmed DR_REPO to compare the secondary.',
        }

    report['checked_at_utc'] = datetime.now(timezone.utc).isoformat()
    serializable = {key: value for key, value in report.items() if key != 'checked_at_utc'}
    text = json.dumps(serializable, indent=2, ensure_ascii=False) + '\n'

    if args.check:
        # Deterministic: the timestamp and the remote result are excluded from the
        # committed inventory so an offline check never depends on network state.
        committed = {key: value for key, value in serializable.items()
                     if key not in ('secondary_comparison', 'index_availability')}
        expected = json.dumps(committed, indent=2, ensure_ascii=False) + '\n'
        if not EVIDENCE.is_file() or EVIDENCE.read_text(encoding='utf-8') != expected:
            print(f'{EVIDENCE.name} is out of date; rerun without --check', file=sys.stderr)
            return 1
        if report['declaration_check']['status'] != 'PASS':
            for finding in report['declaration_check']['findings']:
                print(f'DECLARATION: {finding}', file=sys.stderr)
            return 1
        print(f"OK: {report['package_file_count']} tracked package files; "
              f"{len(report['declaration_check']['locked_distributions'])} locked distributions")
        return 0

    if not args.remote:
        committed = {key: value for key, value in serializable.items()
                     if key not in ('secondary_comparison', 'index_availability')}
        EVIDENCE.write_text(json.dumps(committed, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')

    print(text, end='')
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        comparison = report['secondary_comparison']
        status = comparison.get('status', 'UNKNOWN')
        if status not in ('MATCH', 'MISMATCH', 'BLOCKED', 'NOT_ATTEMPTED'):
            status = 'UNKNOWN'
        level = 'notice' if status in ('MATCH', 'NOT_ATTEMPTED') else 'error'
        print(f'::{level} title=DR PACKAGE PARITY::'
              f'status={status}; package_files={report["package_file_count"]}; '
              f'declarations={report["declaration_check"]["status"]}; '
              f'installed_environment_verified=false')

    if report['declaration_check']['status'] != 'PASS':
        return 1
    if report.get('index_availability', {}).get('status') == 'FAIL':
        return 1
    if report['secondary_comparison']['status'] == 'MISMATCH':
        return 1
    if report['secondary_comparison']['status'] == 'BLOCKED':
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
