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
VIEWER_ROUTES = ['/', '/sovereign/', '/contracts/', '/reports/agents', '/reports/next-session',
                 '/reports/recovery', '/reports/download/next-session.txt',
                 '/reports/download/transfer-package.zip', '/not-an-allowlisted-route']
GATEWAY_ROUTES = ['/aghor/', '/reports/next-session', '/reports/recovery', '/reports/agents',
                  '/sovereign/', '/contracts/', '/not-an-allowlisted-route']


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
        checks.append({'route': route, 'expected_status': expected,
                       **{k: v for k, v in result.items() if k != 'body'}})
    return checks, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--viewer-port', type=int, default=4174)
    parser.add_argument('--gateway-port', type=int, default=4176)
    args = parser.parse_args()
    viewer, gateway = f'http://127.0.0.1:{args.viewer_port}', f'http://127.0.0.1:{args.gateway_port}'
    problems = []

    viewer_checks, p = check(viewer, VIEWER_ROUTES)
    gateway_checks, p2 = check(gateway, GATEWAY_ROUTES)
    problems += p + p2

    note_bytes = NOTE.read_bytes()
    package_bytes = PACKAGE.read_bytes()
    manifest = json.loads(MANIFEST.read_text())
    note_download = fetch(viewer + '/reports/download/next-session.txt')
    package_download = fetch(viewer + '/reports/download/transfer-package.zip')
    gateway_note_download = fetch(gateway + '/reports/download/next-session.txt')
    gateway_package_download = fetch(gateway + '/reports/download/transfer-package.zip')
    if note_download['body'] != note_bytes:
        problems.append('viewer next-session download is not byte-identical to the canonical note')
    if gateway_note_download['body'] != note_bytes:
        problems.append('gateway next-session download is not byte-identical to the canonical note')
    if package_download['body'] != package_bytes:
        problems.append('viewer transfer-package download is not byte-identical to the packaged artifact')
    if gateway_package_download['body'] != package_bytes:
        problems.append('gateway transfer-package download is not byte-identical to the packaged artifact')
    if sha256(package_bytes) != manifest['package_sha256']:
        problems.append('packaged artifact differs from TRANSFER_MANIFEST package_sha256')

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
            'viewer_transfer_package_download_sha256': package_download['sha256'],
            'gateway_transfer_package_download_sha256': gateway_package_download['sha256'],
        },
        'viewer_routes': viewer_checks,
        'gateway_routes': gateway_checks,
        'gateway_availability': availability,
        'problems': problems,
        'limitations': ['Single sandbox host; both replicas share one checkout, filesystem and SQLite queue.',
                        'The preview stack is unauthenticated and is not a production DR approval.',
                        'Only HTTP responses observed at the recorded time are asserted.'],
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    for entry in viewer_checks + gateway_checks:
        print(f"  {entry['status']:>3}  {entry['route']:<42} {entry['content_type'] or ''}")
    print(f"canonical note sha256 {report['canonical_note']['sha256']}")
    print(f"package sha256        {report['transfer_package']['sha256']}")
    print('problems:', problems or 'none')
    print('wrote', REPORT.relative_to(ROOT).as_posix())
    raise SystemExit(1 if problems else 0)


if __name__ == '__main__':
    main()
