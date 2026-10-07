#!/usr/bin/env python3
"""Read-only live-wiring check for the launch: routes, downloads, packs, registry, APK, databases.

Answers one question with evidence: "are the pages, the agents, the contents and the artifacts
actually linked right now?" It reads the running preview stack over HTTP and the checked-in
packs on disk, and writes LIVE_WIRING_STATE_2026_10_06.json. It never starts, stops or writes to
a server, never calls an external provider and never sends a message anywhere.

Blocking checks (a missing file, a dead advertised route, an unresolvable pack binding) exit
non-zero. Advisory checks (APK metadata, enrollment absence, runtime database location) are
recorded as findings and never pass silently as if they were verified.

Run it while the stack is up:
    python3 ops/vyomaraj-core/experience/studio_server.py --port 4181 --home aghor
    python3 ops/vyomaraj-core/experience/studio_server.py --port 4182 --home aghor
    python3 ops/availability/gateway.py --port 4176 --primary-port 4181 --secondary-port 4182
    python3 ops/vyomaraj-core/handover/preview_reports.py --port 4174
    python3 ops/vyomaraj-core/handover/verify_live_wiring.py
"""
import argparse
import hashlib
import json
import re
import struct
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = HERE.parent
OUTPUT = HERE / 'LIVE_WIRING_STATE_2026_10_06.json'
APK = ROOT / 'Vyomaraj-App.apk'

LANES = [('music', 'Memory & Melody'), ('film', 'Frame & Stage'), ('bhakti', 'Bhakti-Shakti'),
         ('comics', 'Chitra Katha'), ('liquor-bar', 'Roots & Pairings'),
         ('aghor-experience', 'Aghor study'), ('research', 'Discovery research')]
PACK_DIRS = {'music': 'music-experience', 'film': 'film-experience',
             'bhakti': 'bhakti-experience', 'comics': 'comics-experience',
             'pairings': 'liquor-bar', 'aghor': 'aghor-experience'}
# route -> (file relative to the repository root, required content marker or None)
VIEWER_ROUTES = {
    '/': (None, 'Vyomaraj'),
    '/reports/next-session': ('ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_2026_10_04.txt', None),
    '/reports/handover-notepad': ('ops/vyomaraj-core/handover/SESSION_UPDATE_2026_10_06.md', 'DR replication completed'),
    '/reports/monitor': (None, 'Local service monitor'),
    '/reports/post-pr25-handover': ('ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_POST_PR25_2026_10_04.txt', 'POST-PR25 COMPANION UPDATE'),
    '/reports/dr-sync': ('ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md', 'BLOCKED'),
    '/reports/integration-audit': ('ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md', 'The final offline gate passed'),
    '/reports/peer-architecture': ('ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md', 'Shared peer architecture and heartbeat plan'),
    '/reports/contents': ('ops/vyomaraj-core/handover/EXPERIENCE_CONTENTS_2026_10_03.md', 'All Experience Contents'),
    '/reports/go-live': ('ops/vyomaraj-core/handover/NAVARATRI_GO_LIVE_PLAN_2026_10_11.md', 'Navaratri 2026 go-live plan'),
    '/reports/stack': ('ops/vyomaraj-core/handover/STACK_AND_PLATFORM_RECORD_2026_10_06.md', 'Stack and platform record'),
    '/reports/live-wiring': ('ops/vyomaraj-core/handover/LIVE_WIRING_STATE_2026_10_06.json', 'blocking_checks'),
    '/reports/test-evidence': ('ops/vyomaraj-core/handover/TEST_EVIDENCE_2026_10_04.json', 'python_tests_total'),
    '/reports/issues': ('ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md', 'New-session runbook (in order)'),
    '/reports/next-session-plan': ('ops/vyomaraj-core/handover/NEXT_SESSION_PLAN_2026_10_07.md', 'NEXT-SESSION PLAN'),
    '/reports/session-update': ('ops/vyomaraj-core/handover/SESSION_UPDATE_2026_10_06.md', 'SESSION UPDATE'),
}
REPLICA_ROUTES = ['/music/', '/film/', '/bhakti/', '/comics/', '/pairings/', '/aghor/', '/research/',
                  '/agents/', '/reports/contents', '/reports/go-live', '/reports/live-wiring',
                  '/reports/stack', '/reports/network-diagram', '/reports/post-pr25-handover',
                  '/reports/market-readiness', '/reports/screenshots', '/reports/realtime',
                  '/reports/integration-audit', '/reports/peer-architecture',
                  '/reports/full-handover', '/api/realtime', '/reports/ai-handoff', '/reports/runbook', '/reports/recovery-index', '/reports/go-live-gaps',
                  '/reports/next-session-plan', '/reports/session-update', '/reports/handover-notepad',
                  '/reports/monitor']
# Captured pages are served from a dedicated /reports/screenshot/<name> branch (any capture,
# allowlisted by filename shape), not from the DOWNLOADS dictionary, so they are checked separately.
SCREENSHOT_ROUTES = {
    '/reports/screenshot/product-page.jpg': 'ops/vyomaraj-core/handover/screenshots/product-page.jpg',
    '/reports/screenshot/lane-music.jpg': 'ops/vyomaraj-core/handover/screenshots/lane-music.jpg',
}
# route -> repository path whose bytes the download must be identical to
DOWNLOADS = {
    '/reports/download/next-session.txt': 'ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_2026_10_04.txt',
    '/reports/download/handover-notepad.txt': 'ops/vyomaraj-core/handover/SESSION_UPDATE_2026_10_06.md',
    '/reports/download/post-pr25-handover.txt': 'ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_POST_PR25_2026_10_04.txt',
    '/reports/download/transfer-package.zip': 'ops/vyomaraj-core/handover/transfer/NEXT_SESSION_TRANSFER_2026_10_04.zip',
    '/reports/download/post-pr25-transfer.zip': 'ops/vyomaraj-core/handover/transfer/NEXT_SESSION_UPDATE_POST_PR25_2026_10_04.zip',
    '/reports/download/network-diagram.svg': 'ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg',
    '/reports/download/full-handover.md': 'ops/vyomaraj-core/handover/VYOMARAJ_FULL_HANDOVER_2026_10_06.md',
    '/reports/download/full-handover.zip': 'ops/vyomaraj-core/handover/transfer/VYOMARAJ_FULL_HANDOVER_2026_10_06.zip',
    '/reports/download/full-handover-current.zip': 'ops/vyomaraj-core/handover/transfer/VYOMARAJ_FULL_HANDOVER_2026_10_07.zip',
    '/reports/download/integration-audit.md': 'ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md',
    '/reports/download/peer-architecture.md': 'ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md',
    '/reports/download/ai-handoff.md': 'ops/vyomaraj-core/handover/AI_PLATFORM_HANDOFF_2026_10_06.md',
    '/reports/download/ai-context-pack.json': 'ops/vyomaraj-core/handover/AI_CONTEXT_PACK_2026_10_06.json',
    '/reports/download/runbook.md': 'ops/vyomaraj-core/handover/VYOMARAJ_RUNBOOK_2026_10_06.md',
    '/reports/download/recovery-index.md': 'ops/vyomaraj-core/handover/ARENA_SESSION_RECOVERY_INDEX_2026_10_06.md',
    '/reports/download/recovery-manifest.json': 'ops/vyomaraj-core/handover/ARENA_SESSION_RECOVERY_MANIFEST_2026_10_06.json',
    '/reports/download/go-live-gaps.md': 'ops/vyomaraj-core/handover/GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md',
    '/reports/download/ai-handoff.zip': 'ops/vyomaraj-core/handover/transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip',
    '/reports/download/ai-handoff-current.zip': 'ops/vyomaraj-core/handover/transfer/AI_PLATFORM_HANDOFF_2026_10_07.zip',
    '/reports/download/network-diagram.png': 'ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.png',
    '/reports/download/next-session-plan.md': 'ops/vyomaraj-core/handover/NEXT_SESSION_PLAN_2026_10_07.md',
    '/reports/download/next-session-plan.txt': 'ops/vyomaraj-core/handover/NEXT_SESSION_PLAN_2026_10_07.md',
    '/reports/download/session-update.md': 'ops/vyomaraj-core/handover/SESSION_UPDATE_2026_10_06.md',
    '/reports/download/session-update.txt': 'ops/vyomaraj-core/handover/SESSION_UPDATE_2026_10_06.md',

}
REQUIRED_FILES = [
    'Vyomaraj-App.apk', 'index.html', 'landing.html', 'flow-diagram.html',
    'ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg',
    'ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.png',
    'ops/vyomaraj-core/handover/MARKET_READINESS_AND_WIRING_2026_10_06.md',
    'ops/vyomaraj-core/handover/screenshots/SCREENSHOT_CAPTURE_RAW.json',
    'ops/vyomaraj-core/handover/screenshots/product-page.jpg',
    'ops/vyomaraj-core/handover/VYOMARAJ_FULL_HANDOVER_2026_10_06.md',
    'ops/vyomaraj-core/handover/transfer/VYOMARAJ_FULL_HANDOVER_2026_10_06.zip',
    'ops/vyomaraj-core/handover/realtime_status.py',
    'ops/vyomaraj-core/handover/probes.py',
    'ops/vyomaraj-core/handover/test_probes.py',
    'ops/vyomaraj-core/handover/AI_PLATFORM_HANDOFF_2026_10_06.md',
    'ops/vyomaraj-core/handover/AI_CONTEXT_PACK_2026_10_06.json',
    'ops/vyomaraj-core/handover/VYOMARAJ_RUNBOOK_2026_10_06.md',
    'ops/vyomaraj-core/handover/ARENA_SESSION_RECOVERY_INDEX_2026_10_06.md',
    'ops/vyomaraj-core/handover/ARENA_SESSION_RECOVERY_MANIFEST_2026_10_06.json',
    'ops/vyomaraj-core/handover/sanitize_personal_data.py',
    'ops/vyomaraj-core/handover/GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md',
    'ops/vyomaraj-core/handover/build_go_live_brief.py',
    'ops/vyomaraj-core/handover/transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip',
    'ops/vyomaraj-core/music-experience/content.json',
    'ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json',
    'ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json',
    'ops/vyomaraj-core/handover/NAVARATRI_GO_LIVE_PLAN_2026_10_11.md',
    'ops/vyomaraj-core/handover/STACK_AND_PLATFORM_RECORD_2026_10_06.md',
    'ops/vyomaraj-core/handover/LINK_AND_ARCHIVE_LEDGER_2026_10_06.json',
    'ops/vyomaraj-core/experience/voice_enrollment.py',
    'ops/vyomaraj-core/governance/VOICE_ENROLLMENT_POLICY.json',
    'ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md',
    'ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md',
    'ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md',
    'ops/vyomaraj-core/handover/transfer/VYOMARAJ_FULL_HANDOVER_2026_10_07.zip',
    'ops/vyomaraj-core/handover/transfer/AI_PLATFORM_HANDOFF_2026_10_07.zip',
    'ops/vyomaraj-core/experience/public_landing_server.py',
    'ops/dr/DEPLOYED_MATCH_2026_10_04.json',
    'ops/vyomaraj-core/handover/transfer/NEXT_SESSION_TRANSFER_2026_10_04.zip',
    'ops/vyomaraj-core/handover/transfer/NEXT_SESSION_UPDATE_POST_PR25_2026_10_04.zip',
    'ops/vyomaraj-core/handover/NEXT_SESSION_PLAN_2026_10_07.md',
    'ops/vyomaraj-core/handover/SESSION_UPDATE_2026_10_06.md',
]
FLOW_REPORTER = 'https://uidai.in'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def fetch(url, timeout=5):
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read()
            return {'status': response.status, 'bytes': len(body), 'sha256': sha256(body),
                    'seconds': round(time.perf_counter() - started, 3), 'body': body,
                    'content_type': response.headers.get('Content-Type')}
    except urllib.error.HTTPError as error:
        return {'status': error.code, 'bytes': 0, 'sha256': None, 'seconds': round(time.perf_counter() - started, 3),
                'body': b'', 'content_type': None}
    except (urllib.error.URLError, OSError) as error:
        return {'status': None, 'bytes': 0, 'sha256': None, 'seconds': round(time.perf_counter() - started, 3),
                'body': b'', 'content_type': None, 'error': str(error)}


def check_routes(base, routes, label, problems):
    results = []
    for route in routes:
        if isinstance(route, tuple):
            route, source, marker = route
        else:
            source, marker = VIEWER_ROUTES.get(route, (None, None))
        result = fetch(base + route)
        row = {'route': route, 'status': result['status'], 'bytes': result['bytes'],
               'sha256': result['sha256'], 'content_type': result['content_type'],
               'seconds': result['seconds']}
        if result['status'] != 200:
            problems.append(f'{label} {route} returned {result["status"]}')
        elif marker and marker.encode() not in result['body']:
            problems.append(f'{label} {route} is missing the expected content marker')
        elif source and route in VIEWER_ROUTES:
            row['source'] = source
        results.append(row)
    return results


def check_downloads(base, label, problems):
    results = []
    for route, source in list(DOWNLOADS.items()) + list(SCREENSHOT_ROUTES.items()):
        expected = (ROOT / source).read_bytes()
        result = fetch(base + route)
        identical = result['body'] == expected
        results.append({'route': route, 'source': source, 'status': result['status'],
                        'bytes': result['bytes'], 'sha256': result['sha256'],
                        'byte_identical_to_source': identical})
        if result['status'] != 200:
            problems.append(f'{label} {route} returned {result["status"]}')
        elif not identical:
            problems.append(f'{label} {route} is not byte-identical to {source}')
    return results


def check_packs(problems):
    registry_path = CORE / 'agents/AGENT_REGISTRY_CURRENT.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    known = set()
    for category in registry.get('categories', []):
        for slot in category.get('slots', []):
            for key in ('slot', 'id', 'slot_id'):
                if slot.get(key):
                    known.add(slot[key])
    lanes = []
    for lane, directory in PACK_DIRS.items():
        path = CORE / directory / 'content.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        # Packs differ by lane: some list 'items', others stories/chapters/collections. Count every
        # top-level list of records that carry an id, so the check works without a fixed schema.
        records = [entry for key, value in data.items()
                   if isinstance(value, list)
                   for entry in value if isinstance(entry, dict) and 'id' in entry]
        source_ids = {source['id'] for source in data.get('sources', []) if 'id' in source}
        dangling = sorted({sid for entry in records for sid in entry.get('source_ids', [])
                           if source_ids and sid not in source_ids})
        slots = [agent['slot'] for agent in data.get('agents', []) if agent.get('slot')]
        unknown_slots = sorted(slot for slot in slots if known and slot not in known)
        null_names = sum(1 for agent in data.get('agents', [])
                         if agent.get('canonical_name') == 'UNKNOWN')
        if dangling:
            problems.append(f'{lane}: records cite unknown sources {dangling}')
        if unknown_slots:
            problems.append(f'{lane}: agent slots not in the current registry {unknown_slots}')
        lanes.append({'lane': lane, 'pack': path.relative_to(ROOT).as_posix(),
                      'records': len(records), 'sources': len(source_ids),
                      'dangling_sources': dangling, 'agent_slots': slots,
                      'slots_absent_from_registry': unknown_slots,
                      'canonical_names_unknown': null_names,
                      'registered_slot_count': len(known)})
    return lanes


APK_SIGNING_MAGIC = b'APK Sig Block 42'
APK_SIGNATURE_SCHEMES = {
    0x7109871A: 'v2',
    0xF05368C0: 'v3',
    0x1B93AD61: 'v3.1',
}


def parse_apk_signing_block(data, central_directory_offset):
    """Inspect APK v2/v3 signing-block structure without claiming cryptographic validity.

    APK v2/v3 signature pairs live before the ZIP central directory, not in META-INF/.SF/.RSA
    entries. A pair's presence is only structural evidence: verifying signer certificates and the
    signed-content digest requires apksigner/a trusted Android SDK, and installation requires a
    real device. This parser intentionally performs neither.
    """
    result = {
        'present': False,
        'structure_valid': False,
        'block_size_bytes': None,
        'pair_ids': [],
        'signature_schemes': [],
        'error': None,
    }
    if not isinstance(data, (bytes, bytearray)) or not isinstance(central_directory_offset, int):
        result['error'] = 'invalid_input'
        return result
    if central_directory_offset < 24 or central_directory_offset > len(data):
        result['error'] = 'central_directory_offset_out_of_range'
        return result
    if data[central_directory_offset - 16:central_directory_offset] != APK_SIGNING_MAGIC:
        return result

    result['present'] = True
    footer_size = struct.unpack_from('<Q', data, central_directory_offset - 24)[0]
    block_start = central_directory_offset - footer_size - 8
    result['block_size_bytes'] = footer_size + 8
    if footer_size < 24 or block_start < 0:
        result['error'] = 'invalid_block_size'
        return result
    start_size = struct.unpack_from('<Q', data, block_start)[0]
    if start_size != footer_size:
        result['error'] = 'size_fields_mismatch'
        return result

    pos = block_start + 8
    pairs_end = central_directory_offset - 24
    while pos < pairs_end:
        if pos + 8 > pairs_end:
            result['error'] = 'truncated_pair_length'
            return result
        pair_size = struct.unpack_from('<Q', data, pos)[0]
        pos += 8
        if pair_size < 4 or pos + pair_size > pairs_end:
            result['error'] = 'invalid_pair_length'
            return result
        pair_id = struct.unpack_from('<I', data, pos)[0]
        result['pair_ids'].append(f'0x{pair_id:08x}')
        pos += pair_size
    if pos != pairs_end:
        result['error'] = 'pair_table_boundary_mismatch'
        return result

    result['structure_valid'] = True
    result['signature_schemes'] = [
        APK_SIGNATURE_SCHEMES[int(pair_id, 16)]
        for pair_id in result['pair_ids'] if int(pair_id, 16) in APK_SIGNATURE_SCHEMES
    ]
    return result


def check_apk(problems):
    if not APK.is_file():
        problems.append('Vyomaraj-App.apk is missing')
        return {'path': APK.relative_to(ROOT).as_posix(), 'present': False}
    import zipfile
    data = APK.read_bytes()
    state = {'path': APK.relative_to(ROOT).as_posix(), 'present': True, 'bytes': len(data),
             'sha256': sha256(data)}
    try:
        with zipfile.ZipFile(APK) as archive:
            names = archive.namelist()
            central_directory_offset = archive.start_dir
        v1_signatures = [name for name in names
                         if name.upper().startswith('META-INF/')
                         and name.upper().endswith(('.RSA', '.DSA', '.EC', '.SF'))]
        signing_block = parse_apk_signing_block(data, central_directory_offset)
        dex = [name for name in names if name.endswith('.dex')]
        signature_material = bool(v1_signatures or signing_block['signature_schemes'])
        if signing_block['present'] and not signing_block['structure_valid']:
            install_claim = ('UNSAFE / UNVERIFIED — an APK signing block is present but malformed; '
                             'do not install or distribute this file.')
        elif signature_material:
            schemes = ', '.join(signing_block['signature_schemes']) or 'v1'
            install_claim = (f'INSTALLATION UNVERIFIED — {schemes} signature material is present, '
                             'but cryptographic verification and real-device installation were not run.')
        else:
            install_claim = ('INSTALLATION UNVERIFIED — no v1 signature entries or recognized v2/v3 '
                             'signing scheme was detected; do not distribute as a release.')
        state.update({
            'zip_entries': len(names),
            'android_manifest_present': 'AndroidManifest.xml' in names,
            'dex_files': dex,
            'v1_signature_files': v1_signatures,
            'apk_signing_block': signing_block,
            'signature_material_present': signature_material,
            'signature_cryptographically_verified': False,
            'install_claim': install_claim,
            'rebuildable_from_this_repository': False,
            'rebuild_note': ('No Android project (Gradle source, AndroidManifest.xml source, Java or '
                             'Kotlin) exists in this repository, so this binary cannot be rebuilt '
                             'here. Recover its source and confirm signer provenance before release.'),
        })
    except zipfile.BadZipFile:
        problems.append('Vyomaraj-App.apk is not a readable zip archive')
        state['readable_zip'] = False
    state.setdefault('advisory', 'Do not present this APK as a release until its signing material is '
                                 'cryptographically verified, signer provenance is reviewed, and a '
                                 'real-device installation test succeeds.')
    return state


def check_enrollment():
    """State the truth about voice/biometric enrollment: there is no capture code in this repo.

    Only executable sources count as an implementation. Documentation and this checker naturally
    mention the words, so they are reported separately instead of being mistaken for a feature.
    """
    hits, mentions = [], []
    pattern = re.compile(r'voiceprint|voice_template|enrollment_capture|biometric_capture|'
                         r'voice_enroll(ment)?_?capture')
    # This checker and its own output necessarily contain the pattern; neither is an implementation.
    skip = {Path(__file__).resolve(), OUTPUT.resolve()}
    for path in ROOT.rglob('*'):
        if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:
            continue
        if path.resolve() in skip:
            continue
        suffix = path.suffix.lower()
        if suffix not in {'.py', '.js', '.json', '.md', '.cjs'}:
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='ignore').lower()
        except OSError:
            continue
        if pattern.search(text):
            hits.append(path.relative_to(ROOT).as_posix())
        elif suffix in {'.py', '.js', '.cjs'} and re.search(r'\bbiometric|voice[_ ]?enroll', text):
            mentions.append(path.relative_to(ROOT).as_posix())
    return {'enrollment_capture_implementation': 'ABSENT' if not hits else 'REVIEW',
            'implementation_files': hits[:20],
            'files_merely_discussing_voice_or_biometric_terms': mentions[:20],
            'identity_documents_route': {'rule': 'uidai.in web only; no in-app biometric capture',
                                         'reference': FLOW_REPORTER},
            'required_before_shipping': [
                'explicit consent screen with a plain-language purpose',
                'delete-my-voice control and a stated retention period',
                'a test that fails if a voice template is written into the repository or uploaded',
                'legal review for any identity-document step before it is announced',
            ]}


def check_databases():
    """Report where runtime state lives; Git-snapshot DR does not cover it."""
    state = {'git_snapshot_dr_covers_runtime_databases': False,
             'note': 'Replication in this repository covers Git tracked files only.', 'stores': []}
    for pattern, label in (('ops/vyomaraj-core/research/.state', 'research discovery store'),
                           ('*.sqlite', 'SQLite store'), ('*.db', 'SQLite store')):
        for path in ROOT.glob(pattern):
            if '.git' in path.parts:
                continue
            entry = {'label': label, 'path': path.relative_to(ROOT).as_posix(),
                     'kind': 'directory' if path.is_dir() else 'file'}
            if path.is_file():
                entry['bytes'] = path.stat().st_size
            state['stores'].append(entry)
    state['backup_required_before_launch'] = True
    return state


def check_web_urls():
    urls = [{'label': 'Owner repository', 'url': 'https://github.com/Vyomaraj1356/Vyomarajai'},
            {'label': 'Owner Pages', 'url': 'https://Vyomaraj1356.github.io/Vyomarajai/'},
            {'label': 'Identity-documents route (web only)', 'url': FLOW_REPORTER}]
    return {'declared_public_urls': urls,
            'production_url': 'NOT SET — no launch domain is recorded in this repository yet',
            'note': 'A preview link dies with its sandbox and cannot be the launch address.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--viewer-port', type=int, default=4174)
    parser.add_argument('--gateway-port', type=int, default=4176)
    parser.add_argument('--lane-a-port', type=int, default=4181)
    parser.add_argument('--lane-b-port', type=int, default=4182)
    args = parser.parse_args()
    viewer, gateway = f'http://127.0.0.1:{args.viewer_port}', f'http://127.0.0.1:{args.gateway_port}'
    lane_a, lane_b = f'http://127.0.0.1:{args.lane_a_port}', f'http://127.0.0.1:{args.lane_b_port}'
    problems, advisory = [], []

    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    for path in missing:
        problems.append(f'required artifact missing: {path}')

    viewer_routes = check_routes(viewer, list(VIEWER_ROUTES), 'viewer', problems)
    gateway_routes = check_routes(gateway, list(VIEWER_ROUTES), 'gateway', problems)
    lane_a_routes = check_routes(lane_a, REPLICA_ROUTES, 'replica-4181', problems)
    lane_b_routes = check_routes(lane_b, REPLICA_ROUTES, 'replica-4182', problems)
    viewer_downloads = check_downloads(viewer, 'viewer', problems)
    gateway_downloads = check_downloads(gateway, 'gateway', problems)

    lanes = check_packs(problems)
    apk = check_apk(problems)
    enrollment = check_enrollment()
    databases = check_databases()
    web_urls = check_web_urls()

    advisory.append('APK build, signature and device behaviour are unverified.')
    advisory.append('Voice/biometric enrollment has no implementation in this repository yet.')
    advisory.append('Runtime databases are outside Git-snapshot replication and need a tested backup.')
    advisory.append('No production URL is recorded; preview links die with their sandbox.')
    advisory.append('No independent-site DR and no zero-RPO/RTO claim: zero_rpo_verified=false, '
                    'zero_rto_verified=false in ops/dr/DR_POLICY.json.')

    report = {
        'checked_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'scope': 'READ_ONLY_LIVE_WIRING_CHECK — local preview stack plus checked-in packs',
        'git': {'commit': _git('rev-parse', 'HEAD'), 'branch': _git('rev-parse', '--abbrev-ref', 'HEAD')},
        'blocking_checks': {'failures': problems, 'passed': not problems},
        'viewer_routes': viewer_routes, 'gateway_routes': gateway_routes,
        'replica_4181_routes': lane_a_routes, 'replica_4182_routes': lane_b_routes,
        'viewer_downloads': viewer_downloads, 'gateway_downloads': gateway_downloads,
        'lanes_and_packs': lanes, 'missing_artifacts': missing,
        'apk': apk, 'enrollment': enrollment, 'databases': databases, 'web_urls': web_urls,
        'advisory': advisory,
        'limitations': ['Only responses observed at the recorded time are asserted.',
                        'A green result means the wiring works, not that the product is live or paid.',
                        'The preview stack is unauthenticated and runs on one host.'],
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for row in viewer_routes:
        print(f"  {row['status']}  viewer  {row['route']:<42} {row['bytes']} bytes")
    for row in lanes:
        print(f"  ok  pack  {row['lane']:<14} {row['records']:>3} records, {row['sources']:>3} sources, "
              f"{len(row['agent_slots'])} slots")
    print(f"  {'FAIL' if problems else 'ok  '}  blocking checks: {len(problems)} problem(s)")
    for problem in problems:
        print('    - ' + problem)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 1 if problems else 0


def _git(*args):
    import subprocess
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


if __name__ == '__main__':
    raise SystemExit(main())
