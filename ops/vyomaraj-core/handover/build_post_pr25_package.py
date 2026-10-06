#!/usr/bin/env python3
"""Build (or check) the POST-PR25 companion transfer package.

The companion is a strict superset of the canonical 41-member transfer package:
every canonical member is present with identical bytes, plus the eight post-PR25
documents and diagnostics scripts listed in ADDITIONS (49 members in total). It exists
because the canonical package records the pre-PR25 state and must stay byte-stable for the
SHA256 already published and quoted.

Like the canonical package this is a deterministic zip: fixed member timestamps and
permission bits, so rebuilding with the same Python/zlib is byte-identical. Never add
secrets, tokens, environment files or runtime state to MEMBERS: this artifact is meant to
be human-reviewable.
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
FIXED_TIMESTAMP = (2026, 10, 4, 0, 0, 0)

# Eight post-PR25 members. Chosen so that every file is stable between suite runs: the
# generated evidence that changes on each run (TEST_EVIDENCE, PREVIEW_VERIFICATION) is
# deliberately absent, exactly as it is absent from the canonical package.
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


def validate_members():
    """Reject a misconfigured member list before it can be packaged or trusted."""
    problems = []
    names = [arcname for arcname, _ in MEMBERS]
    if len(names) != len(set(names)):
        problems.append('duplicate archive names in MEMBERS')
    sources = [source.relative_to(ROOT).as_posix() for _, source in MEMBERS]
    if len(sources) != len(set(sources)):
        problems.append('duplicate source paths in MEMBERS')
    canonical_names = [arcname for arcname, _ in canonical.MEMBERS]
    missing = [name for name in canonical_names if name not in names]
    if missing:
        problems.append(f'canonical members missing from the companion: {missing}')
    for arcname, source in MEMBERS:
        if 'secret' in arcname.lower():
            problems.append(f'secret-like archive name: {arcname}')
        if arcname.endswith(('.env', '.local.env', '.pem', '.key', '.json.state')):
            problems.append(f'secret-like archive suffix: {arcname}')
        if 'dr.local.env' in source.as_posix():
            problems.append(f'local environment file in MEMBERS: {source}')
        if not source.is_file():
            problems.append(f'missing package member: {source}')
    if problems:
        raise SystemExit('; '.join(problems))


def build_bytes():
    validate_members()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for arcname, source in MEMBERS:
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix, so rebuilds do not depend on the writer's OS
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes())
    return buffer.getvalue()


def canonical_bytes():
    """The canonical package as it must appear inside the companion, rebuilt from source."""
    return canonical.build_bytes()


def manifest_for(payload):
    return {
        'package': PACKAGE.relative_to(ROOT).as_posix(),
        'package_sha256': sha256(payload),
        'package_bytes': len(payload),
        'note': NOTE,
        'note_sha256': sha256((HERE / NOTE).read_bytes()),
        'note_bytes': (HERE / NOTE).stat().st_size,
        'note_byte_identical_download': '/reports/download/post-pr25-handover.txt serves the note unchanged',
        'members_total': len(MEMBERS),
        'canonical_members_total': len(canonical.MEMBERS),
        'additions_total': len(ADDITIONS),
        'superset_of_canonical': True,
        'canonical_package': canonical.PACKAGE.relative_to(ROOT).as_posix(),
        'canonical_package_sha256_rebuilt_from_source': sha256(canonical_bytes()),
        'rebuild_command': 'python3 ops/vyomaraj-core/handover/build_post_pr25_package.py',
        'check_command': 'python3 ops/vyomaraj-core/handover/build_post_pr25_package.py --check',
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
    print(f'{MANIFEST.relative_to(ROOT)}  {len(MEMBERS)} members '
          f'({len(canonical.MEMBERS)} canonical + {len(ADDITIONS)} post-PR25)')


def check():
    problems = []
    try:
        validate_members()
    except SystemExit as exc:
        problems.append(str(exc))
    if not PACKAGE.is_file() or not MANIFEST.is_file():
        problems.append('package or manifest missing; run without --check first')
    else:
        manifest = json.loads(MANIFEST.read_text())
        on_disk = PACKAGE.read_bytes()
        rebuilt = build_bytes()
        if sha256(on_disk) != manifest['package_sha256']:
            problems.append('package bytes differ from the manifest SHA256')
        if rebuilt != on_disk:
            problems.append('package is not reproducible byte-for-byte with this Python/zlib')
        with zipfile.ZipFile(io.BytesIO(on_disk)) as archive:
            if archive.namelist() != [name for name, _ in MEMBERS]:
                problems.append('package members differ from MEMBERS')
            else:
                canonical_names = [name for name, _ in canonical.MEMBERS]
                if archive.namelist()[:len(canonical_names)] != canonical_names:
                    problems.append('canonical members are not the leading block of the package')
                if archive.read(NOTE) != (HERE / NOTE).read_bytes():
                    problems.append('companion note in the package differs from its source')
            for member in manifest['members']:
                if archive.read(member['archive_name']) != (ROOT / member['source']).read_bytes():
                    problems.append(f"member differs from source: {member['archive_name']}")
        if manifest['note_sha256'] != sha256((HERE / NOTE).read_bytes()):
            problems.append('note SHA256 differs from the manifest')
        if manifest['members_total'] != len(MEMBERS):
            problems.append('manifest member count differs from MEMBERS')
        if manifest['package_bytes'] != len(on_disk):
            problems.append('manifest byte count differs from the package on disk')
    if problems:
        for problem in problems:
            print('FAIL:', problem)
        raise SystemExit(1)
    print(f'OK: companion package reproducible, superset of the canonical package '
          f'({len(MEMBERS)} members, {PACKAGE.relative_to(ROOT)})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify only; never write')
    args = parser.parse_args()
    check() if args.check else write()
