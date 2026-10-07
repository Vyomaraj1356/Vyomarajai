#!/usr/bin/env python3
"""Verify the frozen POST-PR25 companion transfer package.

The companion is a strict superset of the frozen canonical 41-member transfer package:
every canonical member is present with identical bytes, plus the eight post-PR25 documents
and diagnostics scripts (49 members total). Its SHA256 has been published, so this checker
validates the archive against its checked-in manifest and the frozen canonical archive, not
against live source files that have since evolved. New work belongs in a new, versioned archive.
"""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import build_transfer_package as canonical

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = HERE.parent
NOTE = 'NEXT_SESSION_HANDOVER_POST_PR25_2026_10_04.txt'
MANIFEST = HERE / 'POST_PR25_MANIFEST_2026_10_04.json'
PACKAGE = HERE / 'transfer' / 'NEXT_SESSION_UPDATE_POST_PR25_2026_10_04.zip'
# Eight historical additions in the immutable 49-member snapshot.
ADDITIONS = [
    (NOTE, HERE / NOTE),
    ('post-pr25/DEEP_PRIMARY_SECONDARY_CONFIGURATION_SCAN_2026_10_04.md',
     HERE / 'DEEP_PRIMARY_SECONDARY_CONFIGURATION_SCAN_2026_10_04.md'),
    ('post-pr25/AUTO_ALIGN_STATE_2026_10_04.json', HERE / 'AUTO_ALIGN_STATE_2026_10_04.json'),
    ('post-pr25/DR_POLICY.json', CORE.parent / 'dr' / 'DR_POLICY.json'),
    ('post-pr25/DR_FOLLOWUP_2026_10_03.json', CORE.parent / 'dr' / 'DR_FOLLOWUP_2026_10_03.json'),
    ('post-pr25/ACTIONS_PROBE_EVIDENCE_2026_10_03.json',
     CORE.parent / 'dr' / 'ACTIONS_PROBE_EVIDENCE_2026_10_03.json'),
    ('post-pr25/dr_diagnostics.py', CORE.parent / 'dr' / 'dr_diagnostics.py'),
    ('post-pr25/ci_diagnostics.py', CORE.parent / 'ci' / 'ci_diagnostics.py'),
]
MEMBERS = list(canonical.MEMBERS) + ADDITIONS


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def write():
    raise SystemExit('POST-PR25 companion is frozen; create a separately versioned archive instead')


def check():
    problems = []
    if not PACKAGE.is_file() or not MANIFEST.is_file():
        problems.append('frozen package or manifest is missing')
    elif not canonical.PACKAGE.is_file() or not canonical.MANIFEST.is_file():
        problems.append('frozen canonical package or manifest is missing')
    else:
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        canonical_manifest = json.loads(canonical.MANIFEST.read_text(encoding='utf-8'))
        on_disk = PACKAGE.read_bytes()
        canonical_disk = canonical.PACKAGE.read_bytes()
        if sha256(on_disk) != manifest.get('package_sha256'):
            problems.append('frozen package bytes differ from the manifest SHA256')
        if manifest.get('package_bytes') != len(on_disk):
            problems.append('manifest byte count differs from the frozen package')
        if manifest.get('members_total') != len(manifest.get('members', [])):
            problems.append('manifest member count differs from its recorded member list')
        if manifest.get('canonical_package_sha256_rebuilt_from_source') != canonical_manifest.get('package_sha256'):
            problems.append('manifest does not identify the frozen canonical package')
        with zipfile.ZipFile(io.BytesIO(on_disk)) as archive, zipfile.ZipFile(io.BytesIO(canonical_disk)) as canonical_archive:
            names = archive.namelist()
            member_rows = manifest.get('members', [])
            expected_names = [row.get('archive_name') for row in member_rows]
            canonical_names = canonical_archive.namelist()
            if names != expected_names:
                problems.append('package members differ from the frozen manifest order')
            if names[:len(canonical_names)] != canonical_names:
                problems.append('canonical members are not the leading block of the package')
            for member in member_rows:
                name = member.get('archive_name')
                if name not in names:
                    problems.append(f'frozen manifest member is missing: {name}')
                    continue
                data = archive.read(name)
                if sha256(data) != member.get('sha256') or len(data) != member.get('bytes'):
                    problems.append(f'frozen member differs from its manifest: {name}')
            for name in canonical_names:
                if archive.read(name) != canonical_archive.read(name):
                    problems.append(f'canonical snapshot member differs: {name}')
        if manifest.get('note_sha256') != sha256((HERE / NOTE).read_bytes()):
            problems.append('companion note SHA256 differs from its frozen source')
        if manifest.get('note_bytes') != (HERE / NOTE).stat().st_size:
            problems.append('companion note byte count differs from its frozen source')
    if problems:
        for problem in problems:
            print('FAIL:', problem)
        raise SystemExit(1)
    print(f'OK: frozen companion matches its manifest and canonical snapshot '
          f'({manifest["members_total"]} members, {PACKAGE.relative_to(ROOT)})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; never write')
    args = parser.parse_args()
    check() if args.check else write()
