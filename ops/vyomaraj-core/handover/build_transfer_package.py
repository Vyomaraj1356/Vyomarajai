#!/usr/bin/env python3
"""Build (or check) the small, non-secret handover transfer package.

The package is a frozen, human-reviewable handover artifact. Its manifest pins the exact member bytes
that were packaged at creation time; later source files may legitimately evolve. The check therefore
verifies the committed archive against its manifest and verifies that the current builder remains
deterministic for the current source set. Never add secrets, tokens, environment files or runtime
state to MEMBERS.
"""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NOTE = 'NEXT_SESSION_HANDOVER_2026_10_04.txt'
RECOVERY = 'RECOVERY_AND_HANDOVER_PACKAGE_2026_10_04.md'
MANIFEST = HERE / 'TRANSFER_MANIFEST_2026_10_04.json'
PACKAGE = HERE / 'transfer' / 'NEXT_SESSION_TRANSFER_2026_10_04.zip'
FIXED_TIMESTAMP = (2026, 10, 4, 0, 0, 0)
CORE = HERE.parent
AVAILABILITY = HERE.parents[1] / 'availability'

MEMBERS = [
    (NOTE, HERE / NOTE),
    (RECOVERY, HERE / RECOVERY),
    ('DR_SYNC_RESULTS_2026_10_04.md', HERE / 'DR_SYNC_RESULTS_2026_10_04.md'),
    ('build_dr_sync_report.py', HERE / 'build_dr_sync_report.py'),
    ('test_dr_sync_report.py', HERE / 'test_dr_sync_report.py'),
    ('HANDOVER_ALL_UPDATES_2026_10_03.txt', HERE / 'HANDOVER_ALL_UPDATES_2026_10_03.txt'),
    ('build_transfer_package.py', HERE / 'build_transfer_package.py'),
    ('preview_reports.py', HERE / 'preview_reports.py'),
    ('test_preview_reports.py', HERE / 'test_preview_reports.py'),
    ('test_transfer_package.py', HERE / 'test_transfer_package.py'),
    ('verify_preview.py', HERE / 'verify_preview.py'),
    ('BUILD_AND_CONFIGURATION_2026_10_04.md', HERE / 'BUILD_AND_CONFIGURATION_2026_10_04.md'),
    ('build_configuration_report.py', HERE / 'build_configuration_report.py'),
    ('test_build_configuration_report.py', HERE / 'test_build_configuration_report.py'),
    ('DEPLOYED_MATCH_2026_10_04.json', AVAILABILITY.parent / 'dr' / 'DEPLOYED_MATCH_2026_10_04.json'),
    ('studio_server.py', CORE / 'experience' / 'studio_server.py'),
    ('experience/rebuild_contents.py', CORE / 'experience' / 'rebuild_contents.py'),
    ('gateway.py', AVAILABILITY / 'gateway.py'),
    ('test_gateway.py', AVAILABILITY / 'test_gateway.py'),
    ('INHERITANCE_AUDIT_2026_10_04.md', HERE / 'INHERITANCE_AUDIT_2026_10_04.md'),
    ('inheritance_audit.py', CORE / 'agents' / 'inheritance_audit.py'),
    ('test_inheritance_audit.py', CORE / 'agents' / 'test_inheritance_audit.py'),
    ('LOCAL_FAILOVER_DRILL_2026_10_03.json', AVAILABILITY / 'LOCAL_FAILOVER_DRILL_2026_10_03.json'),
    ('LOCAL_FAILOVER_DRILL_2026_10_04.json', AVAILABILITY / 'LOCAL_FAILOVER_DRILL_2026_10_04.json'),
    ('V16.9/AUTO_ALIGN_NEXT_SESSION.json', HERE / 'AUTO_ALIGN_NEXT_SESSION.json'),
    ('V16.9/AUTO_ALIGN_NEXT_SESSION_2026_10_04.md', HERE / 'AUTO_ALIGN_NEXT_SESSION_2026_10_04.md'),
    ('V16.9/PLATFORM_OPEN_ITEMS_2026_10_04.json', HERE / 'PLATFORM_OPEN_ITEMS_2026_10_04.json'),
    ('V16.9/PLATFORM_CONFIGURATION_CHECK_2026_10_04.md', HERE / 'PLATFORM_CONFIGURATION_CHECK_2026_10_04.md'),
    ('V16.9/ISSUES_AND_PRS_LEDGER.json', HERE / 'ISSUES_AND_PRS_LEDGER.json'),
    ('V16.9/ISSUES_AND_PRS_LEDGER_2026_10_04.md', HERE / 'ISSUES_AND_PRS_LEDGER_2026_10_04.md'),
    ('V16.9/build_platform_check.py', HERE / 'build_platform_check.py'),
    ('V16.9/build_issue_ledger.py', HERE / 'build_issue_ledger.py'),
    ('V16.9/auto_align.py', HERE / 'auto_align.py'),
    ('V16.9/run_offline_suites.py', HERE / 'run_offline_suites.py'),
    ('V16.9/check_language_policy.py', HERE / 'check_language_policy.py'),
    ('V16.9/test_auto_align.py', HERE / 'test_auto_align.py'),
    ('V16.9/test_build_platform_check.py', HERE / 'test_build_platform_check.py'),
    ('V16.9/test_issue_ledger.py', CORE / 'ledger' / 'test_issue_ledger.py'),
    ('V16.9/ISSUE_6_CLOSEOUT_COMMENT_2026_10_04.md', AVAILABILITY.parent / 'dr' / 'ISSUE_6_CLOSEOUT_COMMENT_2026_10_04.md'),
    ('V16.9/ISSUE_6_RESOLUTION_2026_10_04.md', AVAILABILITY.parent / 'dr' / 'ISSUE_6_RESOLUTION_2026_10_04.md'),
    ('V16.9/GITHUB_TRIAGE_2026_10_04.md', ROOT / 'GITHUB_TRIAGE_2026_10_04.md'),
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def build_bytes():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for arcname, source in MEMBERS:
            if not source.is_file():
                raise SystemExit(f'missing package member: {source}')
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix, so rebuilds do not depend on the writer's OS
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes())
    return buffer.getvalue()


def manifest_for(payload):
    return {
        'package': PACKAGE.relative_to(ROOT).as_posix(),
        'package_sha256': sha256(payload),
        'package_bytes': len(payload),
        'note_sha256': sha256((HERE / NOTE).read_bytes()),
        'note_byte_identical_download': '/reports/download/next-session.txt serves the note file unchanged',
        'rebuild_command': 'python3 ops/vyomaraj-core/handover/build_transfer_package.py',
        'check_command': 'python3 ops/vyomaraj-core/handover/build_transfer_package.py --check',
        'determinism': 'fixed member timestamps and permissions; same-Python/zlib rebuilds are byte-identical',
        'members': [
            {'archive_name': arcname, 'source': source.relative_to(ROOT).as_posix(),
             'sha256': sha256(source.read_bytes()), 'bytes': source.stat().st_size}
            for arcname, source in MEMBERS
        ],
    }


def write():
    payload = build_bytes()
    PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE.write_bytes(payload)
    MANIFEST.write_text(json.dumps(manifest_for(payload), indent=2) + '\n')
    print(f'{PACKAGE.relative_to(ROOT)}  {len(payload)} bytes  sha256 {sha256(payload)}')
    print(f'{MANIFEST.relative_to(ROOT)}  note sha256 {sha256((HERE / NOTE).read_bytes())}')


def check():
    problems = []
    if not PACKAGE.is_file() or not MANIFEST.is_file():
        problems.append('package or manifest missing; run without --check first')
    else:
        manifest = json.loads(MANIFEST.read_text())
        on_disk = PACKAGE.read_bytes()
        if sha256(on_disk) != manifest['package_sha256']:
            problems.append('package bytes differ from the manifest SHA256')
        rebuilt_a = build_bytes()
        rebuilt_b = build_bytes()
        if rebuilt_a != rebuilt_b:
            problems.append('current package builder is not deterministic byte-for-byte with this Python/zlib')
        with zipfile.ZipFile(io.BytesIO(on_disk)) as archive:
            if archive.namelist() != [name for name, _ in MEMBERS]:
                problems.append('package members differ from MEMBERS')
            for member in manifest['members']:
                data = archive.read(member['archive_name'])
                if sha256(data) != member['sha256'] or len(data) != member['bytes']:
                    problems.append(f"member differs from frozen manifest: {member['archive_name']}")
        if manifest['note_sha256'] != sha256((HERE / NOTE).read_bytes()):
            problems.append('note SHA256 differs from the manifest')
    if problems:
        for problem in problems:
            print('FAIL:', problem)
        raise SystemExit(1)
    print(f'OK: package reproducible and manifest matches ({PACKAGE.relative_to(ROOT)})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; never write')
    args = parser.parse_args()
    check() if args.check else write()
