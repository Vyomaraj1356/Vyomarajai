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
PROTECTED_DR_PATHS = frozenset({'ops/jarvis/jarvis.env'})
API = 'https://api.github.com'


class CheckError(Exception):
    pass


class TargetOnlyRemovalRequired(CheckError):
    def __init__(self, count):
        self.count = count
        super().__init__(f'Secondary has {count} unprotected target-only files; refusing removal without explicit DR_ALLOW_TARGET_ONLY_REMOVAL=true review approval.')


class ProtectedPathApprovalRequired(CheckError):
    def __init__(self):
        self.count = 1
        super().__init__('DR contains a protected configuration path; sync is blocked until explicit workflow_dispatch approval preserves it. No file content is read or logged.')


def compose_target_entries(source_entries_list, target_entries_list, preserve_protected_path=False):
    """Compose the approved mirror manifest from tree metadata only."""
    source = {entry['path']: entry for entry in source_entries_list}
    target = {entry['path']: entry for entry in target_entries_list}
    protected = PROTECTED_DR_PATHS if preserve_protected_path else frozenset()
    if protected - set(target):
        raise CheckError('Protected DR path is missing from the destination; refusing to synthesize or overwrite it.')
    extras = (set(target) - set(source)) - protected
    combined = {path: entry for path, entry in source.items() if path not in protected}
    for path in protected:
        combined[path] = target[path]
    return [dict(combined[path]) for path in sorted(combined)], extras


def entries_match(expected, observed):
    """Compare path/mode/type/blob identity without fetching file contents."""
    def key(entry):
        return (entry.get('path'), entry.get('mode'), entry.get('type'), entry.get('sha'))
    return sorted(map(key, expected)) == sorted(map(key, observed))


def safe_api_error_reason(status, body):
    """Return a coarse, allow-listed reason; never expose GitHub response bodies."""
    if status != 422:
        return None
    try:
        payload = json.loads(body.decode('utf-8', errors='replace'))
    except (ValueError, TypeError, AttributeError):
        return 'github_validation_rejected'
    message = str(payload.get('message', '')).lower() if isinstance(payload, dict) else ''
    errors = payload.get('errors', []) if isinstance(payload, dict) else []
    details = ' '.join(
        str(item.get('message', '')).lower()
        for item in errors if isinstance(item, dict)
    )
    text = message + ' ' + details
    # Do not infer a size-limit failure from the number 100000 alone: GitHub
    # may mention its general API limit even when this request is far below it.
    if 'tree' in text and any(phrase in text for phrase in (
            'too large', 'size limit exceeded', 'maximum tree size',
            'maximum number of tree entries exceeded')):
        return 'tree_size_limit'
    if 'tree' in text and ('invalid' in text or 'conflict' in text):
        return 'tree_validation_rejected'
    if 'path' in text and ('invalid' in text or 'conflict' in text):
        return 'path_validation_rejected'
    if 'sha' in text and ('invalid' in text or 'missing' in text):
        return 'object_reference_rejected'
    return 'github_validation_rejected'


def safe_validation_fields(status, body):
    """Extract only allowlisted structured GitHub validation fields; never messages."""
    if status != 422:
        return []
    try:
        payload = json.loads(body.decode('utf-8', errors='replace'))
    except (ValueError, TypeError, AttributeError):
        return []
    errors = payload.get('errors', []) if isinstance(payload, dict) else []
    allowed_resources = {'tree', 'git_tree', 'commit', 'blob', 'repository', 'other'}
    allowed_fields = {'tree', 'path', 'sha', 'mode', 'type', 'base_tree', 'commit', 'parent', 'ref', 'message', 'content', 'encoding', 'other'}
    allowed_codes = {'invalid', 'missing', 'already_exists', 'custom', 'unprocessable', 'other'}
    safe = []
    for item in errors[:20] if isinstance(errors, list) else []:
        if not isinstance(item, dict):
            continue
        resource_raw = str(item.get('resource', '')).lower()
        # GitHub serializes this resource as GitTree; normalize its lowercase form.
        resource = {'gittree': 'git_tree'}.get(resource_raw, resource_raw)
        field = str(item.get('field', '')).lower()
        code = str(item.get('code', '')).lower()
        safe.append({
            'resource': resource if resource in allowed_resources else 'other',
            'field': field if field in allowed_fields else 'other',
            'code': code if code in allowed_codes else 'other',
        })
    return safe


def safe_request_metrics(body):
    """Return payload shape metrics only; do not retain paths, SHAs, or file contents."""
    if body is None:
        return {'request_payload_bytes': 0}
    try:
        # Match GitHub.request's exact json.dumps(body).encode() serialization.
        encoded = json.dumps(body).encode('utf-8')
        metrics = {'request_payload_bytes': len(encoded)}
        if isinstance(body, dict) and isinstance(body.get('tree'), list):
            entries = body['tree']
            paths = [item.get('path') for item in entries if isinstance(item, dict) and isinstance(item.get('path'), str)]
            metrics.update({
                'tree_entry_count': len(entries),
                'unique_path_count': len(set(paths)),
                'max_path_length': max((len(path) for path in paths), default=0),
            })
        return metrics
    except (TypeError, ValueError):
        return {'request_payload_bytes': None}


class APIError(CheckError):
    def __init__(self, status, operation=None, safe_reason=None, validation_fields=None, request_metrics=None):
        self.status = status
        self.operation = operation
        self.safe_reason = safe_reason
        self.validation_fields = validation_fields or []
        self.request_metrics = request_metrics or {}
        explanation = {
            401: 'Invalid or expired credentials; reconnect GitHub / review the Actions secret.',
            403: 'Access denied or rate limited; review repository/Actions permissions.',
            404: 'Repository/ref missing OR hidden by permissions; do not infer nonexistence.',
        }.get(status, 'GitHub request failed; response details withheld.')
        reason = f'; reason={safe_reason}' if safe_reason else ''
        super().__init__(f'GitHub HTTP {status}: {explanation}{reason}')


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
                response_body = exc.read()
                safe_reason = safe_api_error_reason(exc.code, response_body)
                validation_fields = safe_validation_fields(exc.code, response_body)
                request_metrics = safe_request_metrics(body) if exc.code == 422 else {}
                raise APIError(exc.code, operation, safe_reason, validation_fields, request_metrics) from None
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


def replicate(primary, secondary, target, src, dst, metrics=None, allow_target_only_removal=False,
             preserve_protected_path=False):
    """Publish an approved snapshot, optionally retaining protected DR paths.

    Protected blob contents are never fetched. The complete approved tree manifest
    is checked before publication and after read-back. With an exception, this is
    approved-scope replication, not exact Primary/DR tree parity.
    """
    source_tree_sha = src['tree']
    target_tree_sha = dst['tree']
    source = primary.request('GET', f'repos/{PRIMARY}/git/trees/{source_tree_sha}?recursive=1')
    entries = source_entries(source)
    old_entries = source_entries(secondary.request('GET', f'repos/{target}/git/trees/{target_tree_sha}?recursive=1'), allow_empty=True)
    target_entries, extra = compose_target_entries(entries, old_entries, preserve_protected_path)
    if extra and not allow_target_only_removal:
        raise TargetOnlyRemovalRequired(len(extra))
    available = {entry['sha'] for entry in old_entries}
    protected = PROTECTED_DR_PATHS if preserve_protected_path else frozenset()
    metrics = {} if metrics is None else metrics
    metrics.update(uploaded_blobs=0, reused_blobs=0,
                   target_only_files_removed_from_snapshot=len(extra),
                   protected_paths_preserved=sorted(protected & {e['path'] for e in old_entries}))
    published_entries = []
    for entry in target_entries:
        if entry['path'] in protected:
            published_entries.append({k: entry[k] for k in ('path', 'mode', 'type', 'sha')})
            metrics['reused_blobs'] += 1
            continue
        if entry['sha'] in available:
            published_entries.append({k: entry[k] for k in ('path', 'mode', 'type', 'sha')})
            metrics['reused_blobs'] += 1
            continue
        source_blob_sha = entry['sha']
        blob = primary.request('GET', f'repos/{PRIMARY}/git/blobs/{source_blob_sha}')
        if blob.get('encoding') != 'base64':
            raise CheckError('Unsupported blob encoding')
        raw = base64.b64decode(''.join(blob['content'].split()), validate=True)
        if git_blob_sha(raw) != source_blob_sha:
            raise CheckError('Source blob integrity mismatch')
        created = secondary.request('POST', f'repos/{target}/git/blobs',
                                    {'encoding': 'base64', 'content': base64.b64encode(raw).decode()})
        if created['sha'] != source_blob_sha:
            raise CheckError('Target blob integrity mismatch')
        available.add(source_blob_sha)
        metrics['uploaded_blobs'] += 1
        published_entries.append({k: entry[k] for k in ('path', 'mode', 'type', 'sha')})
    tree = secondary.request('POST', f'repos/{target}/git/trees', {'tree': published_entries})['sha']
    metrics['intended_tree'] = tree
    created_tree = source_entries(secondary.request('GET', f'repos/{target}/git/trees/{tree}?recursive=1'),
                                  allow_empty=not published_entries)
    if not entries_match(published_entries, created_tree):
        raise CheckError('New DR tree does not match the approved manifest; refusing to update DR ref')
    if not preserve_protected_path and tree != source_tree_sha:
        raise CheckError('New DR tree differs from source; refusing to update DR ref')
    assert_unchanged(primary, PRIMARY, src)
    assert_unchanged(secondary, target, dst)
    source_commit_sha = src['commit']
    message = f'chore(dr): approved snapshot {PRIMARY}:{BRANCH} at {source_commit_sha}'
    if preserve_protected_path:
        message += ' with protected DR configuration retained'
    commit = secondary.request('POST', f'repos/{target}/git/commits',
                               {'message': message, 'tree': tree, 'parents': [dst['commit']]})['sha']
    metrics['intended_commit'] = commit
    assert_unchanged(primary, PRIMARY, src)
    assert_unchanged(secondary, target, dst)
    patch_result = secondary.request('PATCH', f'repos/{target}/git/refs/heads/{BRANCH}',
                                    {'sha': commit, 'force': False})
    patch_object = patch_result.get('object', {}) if isinstance(patch_result, dict) else {}
    metrics['ref_update_confirmed'] = patch_object.get('sha') == commit
    if not metrics['ref_update_confirmed']:
        raise CheckError('DR ref update response did not confirm the intended commit; no sync success claimed')
    observed = snapshot(secondary, target)
    metrics['readback_commit'] = observed.get('commit')
    metrics['readback_tree'] = observed.get('tree')
    if observed != {'commit': commit, 'tree': tree}:
        raise CheckError('Read-after-write mismatch; no sync success claimed')
    observed_entries = source_entries(secondary.request('GET', f'repos/{target}/git/trees/{tree}?recursive=1'),
                                      allow_empty=not published_entries)
    metrics['readback_manifest_match'] = entries_match(published_entries, observed_entries)
    if not metrics['readback_manifest_match']:
        raise CheckError('Read-after-write manifest mismatch; no sync success claimed')
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
    preserve_protected_path = env.get('DR_PROTECTED_PATH_EXCEPTION_APPROVED') == 'true'
    if sync:
        if preserve_protected_path and env.get('GITHUB_EVENT_NAME') != 'workflow_dispatch':
            raise CheckError('Protected-path exception approval is accepted only from explicit workflow_dispatch')
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
        target_tree_sha = dst['tree']
        target_tree = source_entries(secondary.request('GET', f'repos/{target}/git/trees/{target_tree_sha}?recursive=1'), allow_empty=True)
        has_protected = bool(PROTECTED_DR_PATHS & {entry['path'] for entry in target_tree})
        if has_protected and not preserve_protected_path:
            raise ProtectedPathApprovalRequired()
        dst = replicate(primary, secondary, target, src, dst, transfer,
                        env.get('DR_ALLOW_TARGET_ONLY_REMOVAL') == 'true' or pinned_removal_approval(target, dst, env),
                        preserve_protected_path=preserve_protected_path)
        changed = True
    assert_unchanged(primary, PRIMARY, src)
    assert_unchanged(secondary, target, dst)
    return {'primary_repository': PRIMARY, 'secondary_repository': target, 'branch': BRANCH,
            'primary': src, 'secondary': dst, 'data_match': src['tree'] == dst['tree'],
            'replication_performed': changed, 'rollback_commit': previous_secondary['commit'] if changed else None,
            'pre_sync_secondary_commit': previous_secondary['commit'], 'pre_sync_secondary_tree': previous_secondary['tree'],
            'intended_secondary_commit': transfer.get('intended_commit'),
            'intended_secondary_tree': transfer.get('intended_tree'),
            'ref_update_confirmed': transfer.get('ref_update_confirmed', False),
            'readback_commit': transfer.get('readback_commit'), 'readback_tree': transfer.get('readback_tree'),
            'readback_manifest_match': transfer.get('readback_manifest_match', False),
            'traffic_switched': False, 'transfer': transfer,
            'status': ('PROTECTED_PATH_EXCEPTION' if changed and preserve_protected_path else ('MATCH' if src['tree'] == dst['tree'] else 'MISMATCH')),
            'protected_path_exception_applied': bool(changed and preserve_protected_path),
            'approved_scope_match': bool(changed and preserve_protected_path) or src['tree'] == dst['tree']}


def actions_result_annotation(result):
    """Closed-vocabulary public signal; include sanitized 422 shape evidence."""
    status = result.get('status')
    if status not in ('MATCH', 'MISMATCH', 'BLOCKED', 'PROTECTED_PATH_EXCEPTION'): status = 'UNKNOWN'
    operation = result.get('failed_api_operation')
    allowed = {m + ':' + p for m in ('GET','POST','PATCH') for p in ('git/blobs','git/trees','git/commits','git/refs','git/ref','identity','repository')}
    if operation not in allowed: operation = 'NONE_OR_UNCLASSIFIED'
    http = result.get('failed_http_status')
    http = str(http) if type(http) is int and 100 <= http <= 599 else 'UNAVAILABLE'
    count = result.get('target_only_files_awaiting_review')
    gate = f'; target_only_files_awaiting_review={count}' if type(count) is int and 0 < count <= 10000000 else ''
    evidence = ''
    for label, value in [('primary_tree', result.get('primary', {}).get('tree')), ('secondary_tree', result.get('secondary', {}).get('tree')), ('pre_sync_secondary_commit', result.get('pre_sync_secondary_commit')), ('pre_sync_secondary_tree', result.get('pre_sync_secondary_tree')), ('intended_secondary_commit', result.get('intended_secondary_commit')), ('intended_secondary_tree', result.get('intended_secondary_tree')), ('readback_commit', result.get('readback_commit')), ('readback_tree', result.get('readback_tree')), ('rollback_commit', result.get('rollback_commit'))]:
        if isinstance(value, str) and re.fullmatch(r'[0-9a-f]{40}', value): evidence += f'; {label}={value}'
    if result.get('data_match') is True: evidence += '; data_match=true'
    if result.get('protected_path_exception_applied') is True: evidence += '; protected_path_exception=APPLIED; full_tree_match=NOT_CLAIMED; approved_scope_match=true'
    if result.get('replication_performed') is True:
        evidence += '; ref_update_confirmed=' + ('true' if result.get('ref_update_confirmed') is True else 'false')
        evidence += '; readback_manifest_match=' + ('true' if result.get('readback_manifest_match') is True else 'false')

    # Only emit fixed allowlisted enums; never echo API messages, paths, SHAs from
    # request payloads, or raw response bodies into public workflow annotations.
    safe_values = {
        'resource': {'tree', 'git_tree', 'commit', 'blob', 'repository', 'other'},
        'field': {'tree', 'path', 'sha', 'mode', 'type', 'base_tree', 'commit', 'parent', 'ref', 'message', 'content', 'encoding', 'other'},
        'code': {'invalid', 'missing', 'already_exists', 'custom', 'unprocessable', 'other'},
    }
    fields = []
    raw_fields = result.get('safe_validation_fields', [])
    if isinstance(raw_fields, list):
        for item in raw_fields[:20]:
            if not isinstance(item, dict): continue
            values = []
            for key in ('resource', 'field', 'code'):
                value = item.get(key)
                values.append(value if isinstance(value, str) and value in safe_values[key] else 'other')
            fields.append(':'.join(values))
    if fields: evidence += '; validation_fields=' + ','.join(fields)

    metrics = result.get('request_metrics', {})
    metric_parts = []
    if isinstance(metrics, dict):
        for key in ('request_payload_bytes', 'tree_entry_count', 'unique_path_count', 'max_path_length'):
            value = metrics.get(key)
            if type(value) is int and 0 <= value <= 1000000000:
                metric_parts.append(f'{key}={value}')
    if metric_parts: evidence += '; request_metrics=' + ','.join(metric_parts)
    return f'status={status}; failed_api_operation={operation}; http={http}; traffic_switched=NONE' + gate + evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', default=os.environ.get('DR_REPO', ''))
    parser.add_argument('--sync', action='store_true', help='Approved primary-main workflow only')
    parser.add_argument('--output', type=Path, help='Write sanitized evidence JSON')
    args = parser.parse_args()
    try:
        # In the trusted Actions sync job, capture a GET-only path diff before
        # any replication attempt. A target-only-file block must still leave a
        # reviewable artifact; no file contents or credentials are emitted.
        if args.sync and os.environ.get('GITHUB_ACTIONS') == 'true':
            diff_result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name('dr_diff_plan.py')),
                 '--target', args.target, '--output', 'dr-diff-plan.json'],
                capture_output=True, text=True, timeout=180,
            )
            if diff_result.returncode != 0:
                raise CheckError('Read-only DR preflight diff failed; refusing sync')
        result = execute(args.target, args.sync)
        code = 0 if result['data_match'] or result.get('protected_path_exception_applied') else 1
    except (CheckError, ValueError, KeyError, TypeError) as exc:
        # Only CheckError messages are controlled. Other failures may embed raw
        # input in exception messages; never emit them or provider response bodies.
        result = {'status': 'BLOCKED', 'detail': str(exc) if isinstance(exc, CheckError)
                  else 'Malformed source/API response; no success claimed',
                  'traffic_switched': False, 'failed_api_operation': getattr(exc, 'operation', None), 'failed_http_status': getattr(exc, 'status', None),
                  'target_only_files_awaiting_review': exc.count if isinstance(exc, (TargetOnlyRemovalRequired, ProtectedPathApprovalRequired)) else None,
                  'safe_validation_fields': getattr(exc, 'validation_fields', []),
                  'request_metrics': getattr(exc, 'request_metrics', {})}
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
