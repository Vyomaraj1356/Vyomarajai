#!/usr/bin/env python3
"""Read-only DR verification by default; explicit, main-only snapshot replication.

Never loads dr.env. Uses process credentials, or gh for local read-only checks.
Reports status/SHAs only, not response bodies, tokens or device configuration.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

PRIMARY = 'Vyomaraj1356/Vyomarajai'
BRANCH = 'main'
API = 'https://api.github.com'


class CheckError(Exception):
    pass


class TargetOnlyRemovalRequired(CheckError):
    def __init__(self, count):
        self.count = count
        super().__init__(f'Secondary has {count} target-only files; refusing removal without explicit DR_ALLOW_TARGET_ONLY_REMOVAL=true review approval.')


class APIError(CheckError):
    def __init__(self, status, operation=None):
        self.status = status
        self.operation = operation
        explanation = {
            401: 'Invalid or expired credentials; reconnect GitHub / review the Actions secret.',
            403: 'Access denied or rate limited; review repository/Actions permissions.',
            404: 'Repository/ref missing OR hidden by permissions; do not infer nonexistence.',
        }.get(status, 'GitHub request failed; no response body was logged.')
        super().__init__(f'GitHub HTTP {status}: {explanation}')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHub:
    def __init__(self, token=None):
        self.token = token
        self.next_write_at = 0.0
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, method, path, body=None):
        if (not path.startswith('repos/') and not (method == 'GET' and path == 'user')) or '..' in path or '://' in path:
            raise CheckError('Invalid GitHub API path')
        if not self.token:
            if method != 'GET':
                raise CheckError('Writes require explicit process credentials; gh fallback is read-only')
            try:
                result = subprocess.run(['gh', 'api', '--method', 'GET', path],
                                        capture_output=True, text=True, timeout=60)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise CheckError('GitHub CLI unavailable or timed out') from exc
            if result.returncode:
                match = re.search(r'HTTP (\d{3})', result.stderr)
                raise APIError(int(match.group(1)) if match else 'unavailable')
            return json.loads(result.stdout)
        operation = method + ':' + next((part for part in ('git/blobs','git/trees','git/commits','git/refs','git/ref') if part in path), 'identity' if path == 'user' else 'repository')
        headers = {'Authorization': f'Bearer {self.token}',
                   'Accept': 'application/vnd.github+json',
                   'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Vyomaraj-DR-Check'}
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(API + '/' + path, data=data, headers=headers, method=method)
        # Pace serial mutations; never automatically replay an ambiguous write.
        if method != 'GET':
            delay = self.next_write_at - time.monotonic()
            if delay > 0: time.sleep(delay)
            self.next_write_at = time.monotonic() + 1.1
        for attempt in range(3):
            try:
                with self.opener.open(req, timeout=60) as response:
                    return json.load(response)
            except urllib.error.HTTPError as exc:
                if method == 'GET' and exc.code in (429, 502, 503, 504) and attempt < 2:
                    delay = 2 ** attempt
                    retry_after = exc.headers.get('Retry-After') if exc.headers else None
                    if retry_after is not None:
                        try: delay = int(retry_after)
                        except ValueError: raise APIError(exc.code, operation) from None
                    if not 0 <= delay <= 60: raise APIError(exc.code, operation) from None
                    time.sleep(max(1, delay)); continue
                raise APIError(exc.code, operation) from None
            except (urllib.error.URLError, TimeoutError, OSError):
                if method == 'GET' and attempt < 2:
                    time.sleep(2 ** attempt); continue
                raise CheckError('GitHub network request failed; response details withheld; writes are never blindly retried') from None


def validate_target(target):
    if not target:
        raise CheckError('DR_REPO is unset. Confirm the private secondary full name, then set '
                         'the GitHub repository variable VYOMARAJ_DR_REPO. No target is guessed.')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', target):
        raise CheckError('DR_REPO must be an owner/repository name, not a URL')
    if target.lower() == PRIMARY.lower() or '..' in target:
        raise CheckError('DR_REPO must be a separate repository')
    return target


def snapshot(client, repo):
    ref = client.request('GET', f'repos/{repo}/git/ref/heads/{BRANCH}')
    commit = ref['object']['sha']
    tree = client.request('GET', f'repos/{repo}/git/commits/{commit}')['tree']['sha']
    return {'commit': commit, 'tree': tree}


def assert_unchanged(client, repo, expected):
    if snapshot(client, repo) != expected:
        raise CheckError('Source or target changed during the operation; refusing stale replication')


def source_entries(response, allow_empty=False):
    if response.get('truncated') or not isinstance(response.get('tree'), list):
        raise CheckError('Truncated/invalid source tree; refusing partial replication')
    entries = []
    seen = set()
    for entry in response['tree']:
        if entry['type'] == 'tree':
            continue
        if entry['type'] != 'blob' or entry['mode'] not in ('100644', '100755', '120000'):
            raise CheckError('Unsupported source entry (including submodules); refusing partial replication')
        path = entry['path']
        if path in seen or path.startswith('/') or '..' in path.split('/'):
            raise CheckError('Invalid or duplicate source path')
        seen.add(path)
        entries.append(entry)
    if not entries and not allow_empty:
        raise CheckError('Empty source snapshot refused')
    return entries


def git_blob_sha(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def replicate(primary, secondary, target, src, dst, metrics=None, allow_target_only_removal=False):
    """Build exact tree, verify before publication, preserve prior DR history.

    Target-only files are removed from the new snapshot, not its history. This
    is an explicit mirror operation. Unknown/empty targets are never initialized.
    """
    source = primary.request('GET', f'repos/{PRIMARY}/git/trees/{src["tree"]}?recursive=1')
    entries = source_entries(source)
    old_entries = source_entries(secondary.request('GET', f'repos/{target}/git/trees/{dst["tree"]}?recursive=1'), allow_empty=True)
    extra = {entry['path'] for entry in old_entries} - {entry['path'] for entry in entries}
    if extra and not allow_target_only_removal:
        raise TargetOnlyRemovalRequired(len(extra))
    available = {entry['sha'] for entry in old_entries}
    metrics = {} if metrics is None else metrics
    metrics.update(uploaded_blobs=0, reused_blobs=0, target_only_files_removed_from_snapshot=len(extra))
    target_entries = []
    for entry in entries:
        if entry['sha'] in available:
            target_entries.append({k: entry[k] for k in ('path', 'mode', 'type', 'sha')})
            metrics['reused_blobs'] += 1
            continue
        blob = primary.request('GET', f'repos/{PRIMARY}/git/blobs/{entry["sha"]}')
        if blob.get('encoding') != 'base64':
            raise CheckError('Unsupported blob encoding')
        raw = base64.b64decode(''.join(blob['content'].split()), validate=True)
        if git_blob_sha(raw) != entry['sha']:
            raise CheckError('Source blob integrity mismatch')
        created = secondary.request('POST', f'repos/{target}/git/blobs',
                                    {'encoding': 'base64', 'content': base64.b64encode(raw).decode()})
        if created['sha'] != entry['sha']:
            raise CheckError('Target blob integrity mismatch')
        available.add(entry['sha'])
        metrics['uploaded_blobs'] += 1
        target_entries.append({k: entry[k] for k in ('path', 'mode', 'type', 'sha')})
    # No base_tree: retaining it would preserve deleted source files on DR.
    tree = secondary.request('POST', f'repos/{target}/git/trees', {'tree': target_entries})['sha']
    if tree != src['tree']:
        raise CheckError('New DR tree differs from source; refusing to update DR ref')
    assert_unchanged(primary, PRIMARY, src)
    assert_unchanged(secondary, target, dst)
    commit = secondary.request('POST', f'repos/{target}/git/commits', {
        'message': f'chore(dr): snapshot {PRIMARY}:{BRANCH} at {src["commit"]}',
        'tree': tree, 'parents': [dst['commit']],
    })['sha']
    # Recheck immediately before publication. force:false also rejects a
    # concurrent divergent target advance; it never force-overwrites a branch.
    assert_unchanged(primary, PRIMARY, src)
    assert_unchanged(secondary, target, dst)
    secondary.request('PATCH', f'repos/{target}/git/refs/heads/{BRANCH}',
                      {'sha': commit, 'force': False})
    observed = snapshot(secondary, target)
    if observed != {'commit': commit, 'tree': tree}:
        raise CheckError('Read-after-write mismatch; no sync success claimed')
    assert_unchanged(primary, PRIMARY, src)
    return observed


def pinned_removal_approval(target, dst, env, policy=None, now=None):
    """One-snapshot owner approval, never a standing permission to remove files."""
    if (env.get('GITHUB_ACTIONS') != 'true' or env.get('GITHUB_REPOSITORY') != PRIMARY
            or env.get('GITHUB_REF') != 'refs/heads/main'):
        return False
    try:
        policy = policy if policy is not None else json.loads(Path(__file__).with_name('DR_POLICY.json').read_text())
        approval = policy.get('one_snapshot_removal_approval', {})
        expires = datetime.fromisoformat(approval.get('expires_at_utc', ''))
        now = now or datetime.now(timezone.utc)
        return (approval.get('approved') is True and policy.get('primary') == PRIMARY
                and policy.get('secondary') == target and approval.get('secondary') == target
                and approval.get('expected_commit') == dst['commit']
                and approval.get('expected_tree') == dst['tree']
                and all(re.fullmatch(r'[0-9a-f]{40}', dst[k]) for k in ('commit','tree'))
                and expires.tzinfo is not None and now < expires)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def execute(target, sync=False, primary=None, secondary=None, environ=None):
    env = os.environ if environ is None else environ
    target = validate_target(target)
    if sync:
        if env.get('GITHUB_REPOSITORY') != PRIMARY or env.get('GITHUB_REF') != 'refs/heads/main':
            raise CheckError('Replication is restricted to the primary repository main workflow')
        if env.get('DR_SYNC_APPROVED') != 'true':
            raise CheckError('Replication requires explicit DR_SYNC_APPROVED=true')
        if not env.get('PRIMARY_TOKEN') or not env.get('DR_TOKEN'):
            raise CheckError('Replication credentials are missing; do not paste tokens in chat')
    primary = primary or GitHub(env.get('PRIMARY_TOKEN'))
    secondary = secondary or GitHub(env.get('DR_TOKEN'))
    for client, repo in ((primary, PRIMARY), (secondary, target)):
        info = client.request('GET', f'repos/{repo}')
        if info.get('full_name', '').lower() != repo.lower():
            raise CheckError('Repository identity mismatch or rename; confirmation required')
        if info.get('archived') or info.get('disabled'):
            raise CheckError('Repository is archived/disabled')
    src, dst = snapshot(primary, PRIMARY), snapshot(secondary, target)
    # Never fabricate an initial target on a 404: permission failure is ambiguous.
    previous_secondary = dict(dst)
    changed = False
    transfer = {'uploaded_blobs': 0, 'reused_blobs': 0, 'target_only_files_removed_from_snapshot': 0}
    if src['tree'] != dst['tree'] and sync:
        dst = replicate(primary, secondary, target, src, dst, transfer, env.get('DR_ALLOW_TARGET_ONLY_REMOVAL') == 'true' or pinned_removal_approval(target, dst, env))
        changed = True
    assert_unchanged(primary, PRIMARY, src)
    assert_unchanged(secondary, target, dst)
    return {'primary_repository': PRIMARY, 'secondary_repository': target, 'branch': BRANCH,
            'primary': src, 'secondary': dst, 'data_match': src['tree'] == dst['tree'],
            'replication_performed': changed, 'rollback_commit': previous_secondary['commit'] if changed else None, 'traffic_switched': False, 'transfer': transfer,
            'status': 'MATCH' if src['tree'] == dst['tree'] else 'MISMATCH'}


def actions_result_annotation(result):
    """Closed-vocabulary public error/success signal, available without log downloads."""
    status = result.get('status')
    if status not in ('MATCH', 'MISMATCH', 'BLOCKED'): status = 'UNKNOWN'
    operation = result.get('failed_api_operation')
    allowed = {m + ':' + p for m in ('GET','POST','PATCH') for p in ('git/blobs','git/trees','git/commits','git/refs','git/ref','identity','repository')}
    if operation not in allowed: operation = 'NONE_OR_UNCLASSIFIED'
    http = result.get('failed_http_status')
    http = str(http) if type(http) is int and 100 <= http <= 599 else 'UNAVAILABLE'
    count = result.get('target_only_files_awaiting_review')
    gate = f'; target_only_files_awaiting_review={count}' if type(count) is int and count > 0 else ''
    evidence = ''
    for label, value in [('primary_tree', result.get('primary', {}).get('tree')), ('secondary_tree', result.get('secondary', {}).get('tree')), ('rollback_commit', result.get('rollback_commit'))]:
        if isinstance(value, str) and re.fullmatch(r'[0-9a-f]{40}', value): evidence += f'; {label}={value}'
    if result.get('data_match') is True: evidence += '; data_match=true'
    return f'status={status}; failed_api_operation={operation}; http={http}; traffic_switched=NONE' + gate + evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', default=os.environ.get('DR_REPO', ''))
    parser.add_argument('--sync', action='store_true', help='Approved primary-main workflow only')
    parser.add_argument('--output', type=Path, help='Write sanitized evidence JSON')
    args = parser.parse_args()
    try:
        result = execute(args.target, args.sync)
        code = 0 if result['data_match'] else 1
    except (CheckError, ValueError, KeyError, TypeError) as exc:
        # Only CheckError messages are controlled. Other failures may embed raw
        # input in exception messages; never emit them or provider response bodies.
        result = {'status': 'BLOCKED', 'detail': str(exc) if isinstance(exc, CheckError)
                  else 'Malformed source/API response; no success claimed',
                  'traffic_switched': False, 'failed_api_operation': getattr(exc, 'operation', None), 'failed_http_status': getattr(exc, 'status', None),
                  'target_only_files_awaiting_review': exc.count if isinstance(exc, TargetOnlyRemovalRequired) else None}
        code = 2
    result['checked_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['requested_operation'] = 'sync' if args.sync else 'read_only_verification'
    result['primary_repository'] = PRIMARY
    try:
        result['secondary_repository'] = validate_target(args.target)
    except CheckError:
        result['secondary_repository'] = None
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        level = 'error' if code else 'notice'
        print(f'::{level} title=DR SNAPSHOT RESULT::' + actions_result_annotation(result))
    return code


if __name__ == '__main__':
    sys.exit(main())
