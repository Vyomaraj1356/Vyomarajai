#!/usr/bin/env python3
"""Read-only check of the running local preview stack.

Records real HTTP status codes, content types and SHA256 values into
PREVIEW_VERIFICATION_2026_10_04.json. It never starts, stops or writes to the servers, and it
makes no claim beyond the responses it observed.
"""
import argparse
import hashlib
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPORT = HERE / 'PREVIEW_VERIFICATION_2026_10_04.json'
MANIFEST = HERE / 'TRANSFER_MANIFEST_2026_10_04.json'
NOTE = HERE / 'NEXT_SESSION_HANDOVER_2026_10_04.txt'
PACKAGE = HERE / 'transfer' / 'NEXT_SESSION_TRANSFER_2026_10_04.zip'
AUTO_ALIGN_JSON = HERE / 'AUTO_ALIGN_NEXT_SESSION.json'
PLATFORM_CHECK = HERE / 'PLATFORM_CONFIGURATION_CHECK_2026_10_04.md'
ISSUES_LEDGER = HERE / 'ISSUES_AND_PRS_LEDGER.json'
POST_PR25_NOTE = HERE / 'NEXT_SESSION_HANDOVER_POST_PR25_2026_10_04.txt'
POST_PR25_PACKAGE = HERE / 'transfer' / 'NEXT_SESSION_UPDATE_POST_PR25_2026_10_04.zip'
POST_PR25_MANIFEST = HERE / 'POST_PR25_MANIFEST_2026_10_04.json'
VIEWER_ROUTES = ['/', '/sovereign/', '/contracts/', '/reports/agents', '/reports/build', '/reports/architecture',
                 '/reports/next-session', '/reports/handover-notepad', '/reports/dr-sync',
                 '/reports/recovery', '/reports/chats', '/reports/issue-6', '/reports/test-evidence',
                 '/reports/download/next-session.txt',
                 '/reports/download/handover-notepad.txt',
                 '/reports/download/transfer-package.zip', '/reports/post-pr25-handover',
                 '/reports/download/post-pr25-handover.txt', '/reports/download/post-pr25-transfer.zip',
                 '/reports/go-live', '/reports/live-wiring', '/reports/stack', '/reports/network-diagram', '/reports/market-readiness', '/reports/screenshots', '/reports/realtime', '/reports/full-handover', '/reports/ai-handoff', '/reports/runbook', '/reports/recovery-index',
                 '/reports/auto-align', '/reports/platform-check',
                 '/reports/issues', '/reports/download/auto-align.json',
                 '/reports/download/platform-check.md', '/reports/download/issues-ledger.json',
                 '/not-an-allowlisted-route']
GATEWAY_ROUTES = ['/aghor/', '/comics/', '/approvals/', '/finance/', '/upgrades/', '/reports/build', '/reports/next-session', '/reports/handover-notepad',
                  '/reports/post-pr25-handover', '/reports/download/post-pr25-handover.txt',
                  '/reports/download/post-pr25-transfer.zip',
                  '/reports/dr-sync', '/reports/recovery', '/reports/chats', '/reports/issue-6',
                  '/reports/test-evidence', '/reports/download/handover-notepad.txt',
                  '/reports/agents', '/sovereign/', '/contracts/', '/reports/auto-align',
                  '/reports/platform-check', '/reports/issues', '/reports/download/auto-align.json',
                  '/reports/download/platform-check.md', '/reports/download/issues-ledger.json',
                  '/not-an-allowlisted-route']
LANE_REPORT_ROUTES = ['/reports/go-live', '/reports/live-wiring', '/reports/stack', '/reports/network-diagram', '/reports/market-readiness', '/reports/screenshots', '/reports/realtime', '/reports/full-handover', '/reports/ai-handoff', '/reports/runbook', '/reports/recovery-index',
                      '/reports/auto-align', '/reports/platform-check', '/reports/issues',
                      '/reports/post-pr25-handover', '/reports/download/post-pr25-handover.txt',
                      '/reports/download/auto-align.json', '/reports/download/platform-check.md',
                      '/reports/download/issues-ledger.json']
# A 200 alone is not enough for the three reference pages: require a known content marker too.
CONTENT_MARKERS = {'/reports/chats': 'All Chats from Arena Database',
                   '/reports/post-pr25-handover': 'POST-PR25 COMPANION UPDATE',
                   '/reports/issue-6': 'Issue #6 resolution statement',
                   '/reports/test-evidence': 'python_tests_total',
                   '/reports/auto-align': 'AUTO-ALIGN EXECUTION PLAN',
                   '/reports/platform-check': 'How it gets configured (auto-align plan)',
                   '/reports/issues': 'New-session runbook (in order)',
                   '/reports/go-live': 'Navaratri 2026 go-live plan',
                   '/reports/live-wiring': 'blocking_checks',
                   '/reports/stack': 'Stack and platform record',
                   '/reports/network-diagram': 'Network and architecture diagram',
                   '/reports/market-readiness': 'Market readiness and wiring',
                   '/reports/screenshots': 'Real captures of the running pages',
                   '/reports/realtime': 'Live state, re-probed on every load',
                   '/reports/full-handover': 'Full handover — all details',
                   '/reports/ai-handoff': 'HANDOFF FOR ANOTHER AI PLATFORM',
                   '/reports/runbook': 'RUNBOOK: CONFIGURE',
                   '/reports/recovery-index': 'ARENA SESSION RECOVERY INDEX'}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def fetch(url):
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            body = response.read()
            return {'status': response.status, 'content_type': response.headers.get('Content-Type'),
                    'content_disposition': response.headers.get('Content-Disposition'),
                    'bytes': len(body), 'sha256': sha256(body), 'body': body}
    except urllib.error.HTTPError as error:
        body = error.read()
        return {'status': error.code, 'content_type': error.headers.get('Content-Type'),
                'content_disposition': error.headers.get('Content-Disposition'),
                'bytes': len(body), 'sha256': sha256(body), 'body': body}


def check(base, routes):
    checks, problems = [], []
    for route in routes:
        result = fetch(base + route)
        expected = 404 if route == '/not-an-allowlisted-route' else 200
        if result['status'] != expected:
            problems.append(f'{base}{route}: expected {expected}, got {result["status"]}')
        elif expected == 200 and route in CONTENT_MARKERS and CONTENT_MARKERS[route].encode() not in result['body']:
            problems.append(f'{base}{route}: 200 but the expected content marker is missing')
        checks.append({'route': route, 'expected_status': expected,
                       **{k: v for k, v in result.items() if k != 'body'}})
    return checks, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--viewer-port', type=int, default=4174)
    parser.add_argument('--gateway-port', type=int, default=4176)
    parser.add_argument('--lane-a-port', type=int, default=4181)
    parser.add_argument('--lane-b-port', type=int, default=4182)
    args = parser.parse_args()
    viewer, gateway = f'http://127.0.0.1:{args.viewer_port}', f'http://127.0.0.1:{args.gateway_port}'
    lane_a, lane_b = f'http://127.0.0.1:{args.lane_a_port}', f'http://127.0.0.1:{args.lane_b_port}'
    problems = []

    viewer_checks, p = check(viewer, VIEWER_ROUTES)
    gateway_checks, p2 = check(gateway, GATEWAY_ROUTES)
    lane_a_checks, p3 = check(lane_a, LANE_REPORT_ROUTES)
    lane_b_checks, p4 = check(lane_b, LANE_REPORT_ROUTES)
    problems += p + p2 + p3 + p4

    note_bytes = NOTE.read_bytes()
    package_bytes = PACKAGE.read_bytes()
    manifest = json.loads(MANIFEST.read_text())
    note_download = fetch(viewer + '/reports/download/next-session.txt')
    package_download = fetch(viewer + '/reports/download/transfer-package.zip')
    gateway_note_download = fetch(gateway + '/reports/download/next-session.txt')
    gateway_package_download = fetch(gateway + '/reports/download/transfer-package.zip')
    notepad_download = fetch(viewer + '/reports/download/handover-notepad.txt')
    gateway_notepad_download = fetch(gateway + '/reports/download/handover-notepad.txt')
    if note_download['body'] != note_bytes:
        problems.append('viewer next-session download is not byte-identical to the canonical note')
    if gateway_note_download['body'] != note_bytes:
        problems.append('gateway next-session download is not byte-identical to the canonical note')
    if notepad_download['body'] != note_bytes:
        problems.append('viewer handover-notepad download is not byte-identical to the canonical note')
    if gateway_notepad_download['body'] != note_bytes:
        problems.append('gateway handover-notepad download is not byte-identical to the canonical note')
    if package_download['body'] != package_bytes:
        problems.append('viewer transfer-package download is not byte-identical to the packaged artifact')
    if gateway_package_download['body'] != package_bytes:
        problems.append('gateway transfer-package download is not byte-identical to the packaged artifact')
    if sha256(package_bytes) != manifest['package_sha256']:
        problems.append('packaged artifact differs from TRANSFER_MANIFEST package_sha256')

    extra_download_hashes = {}
    for label, path, route in (
            ('auto_align_json', AUTO_ALIGN_JSON, '/reports/download/auto-align.json'),
            ('platform_check', PLATFORM_CHECK, '/reports/download/platform-check.md'),
            ('issues_ledger_json', ISSUES_LEDGER, '/reports/download/issues-ledger.json'),
            ('post_pr25_note', POST_PR25_NOTE, '/reports/download/post-pr25-handover.txt'),
            ('post_pr25_package', POST_PR25_PACKAGE, '/reports/download/post-pr25-transfer.zip')):
        expected_bytes = path.read_bytes()
        for name, base in (('viewer', viewer), ('gateway', gateway)):
            result = fetch(base + route)
            if result['body'] != expected_bytes:
                problems.append(f'{name} {label} download is not byte-identical to its source')
            extra_download_hashes[f'{name}_{label}_download_sha256'] = result['sha256']

    post_pr25_manifest = json.loads(POST_PR25_MANIFEST.read_text())
    if sha256(POST_PR25_PACKAGE.read_bytes()) != post_pr25_manifest['package_sha256']:
        problems.append('post-PR25 package differs from POST_PR25_MANIFEST package_sha256')
    if sha256(POST_PR25_NOTE.read_bytes()) != post_pr25_manifest['note_sha256']:
        problems.append('post-PR25 note differs from POST_PR25_MANIFEST note_sha256')

    try:
        availability = json.loads(fetch(gateway + '/api/availability')['body'])
    except ValueError:
        availability, _ = None, problems.append('availability endpoint did not return JSON')
    if availability:
        if not all(replica['metadata_ready'] for replica in availability['replicas']):
            problems.append('not every replica reports metadata_ready=true')
        if availability['counters']['ambiguous_post_failures'] != 0:
            problems.append('ambiguous_post_failures is non-zero')

    def git(*args):
        return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()

    report = {
        'verified_at_utc': time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime()),
        'scope': 'READ_ONLY_LOCAL_PREVIEW_CHECK',
        'git': {'branch': git('rev-parse', '--abbrev-ref', 'HEAD'), 'commit': git('rev-parse', 'HEAD')},
        'canonical_note': {'path': NOTE.relative_to(ROOT).as_posix(), 'sha256': sha256(note_bytes),
                           'bytes': len(note_bytes)},
        'transfer_package': {'path': PACKAGE.relative_to(ROOT).as_posix(), 'sha256': sha256(package_bytes),
                             'bytes': len(package_bytes)},
        'byte_identity': {
            'viewer_next_session_download_sha256': note_download['sha256'],
            'gateway_next_session_download_sha256': gateway_note_download['sha256'],
            'viewer_handover_notepad_download_sha256': notepad_download['sha256'],
            'gateway_handover_notepad_download_sha256': gateway_notepad_download['sha256'],
            'viewer_transfer_package_download_sha256': package_download['sha256'],
            'gateway_transfer_package_download_sha256': gateway_package_download['sha256'],
            **extra_download_hashes,
        },
        'viewer_routes': viewer_checks,
        'gateway_routes': gateway_checks,
        'studio_lanes': {
            str(args.lane_a_port): lane_a_checks,
            str(args.lane_b_port): lane_b_checks,
        },
        'gateway_availability': availability,
        'problems': problems,
        'limitations': ['Single sandbox host; both replicas share one checkout, filesystem and SQLite queue.',
                        'The preview stack is unauthenticated and is not a production DR approval.',
                        'Only HTTP responses observed at the recorded time are asserted.'],
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    for entry in viewer_checks + gateway_checks + lane_a_checks + lane_b_checks:
        print(f"  {entry['status']:>3}  {entry['route']:<42} {entry['content_type'] or ''}")
    print(f"canonical note sha256 {report['canonical_note']['sha256']}")
    print(f"package sha256        {report['transfer_package']['sha256']}")
    print('problems:', problems or 'none')
    print('wrote', REPORT.relative_to(ROOT).as_posix())
    raise SystemExit(1 if problems else 0)


if __name__ == '__main__':
    main()
