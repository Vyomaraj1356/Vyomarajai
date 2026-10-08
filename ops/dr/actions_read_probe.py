#!/usr/bin/env python3
"""GET-only Actions credential probe; no blobs, filenames, secret values or writes."""
import json
import os
import re
from pathlib import Path
import sys
from dr_sync import GitHub, PRIMARY, CheckError, APIError, snapshot, assert_unchanged, validate_target, source_entries
from dr_diagnostics import diagnose
from package_parity import classify as classify_package

class ReadOnlyClient:
    def __init__(self, client):
        self.client = client
        # Diagnostics need only credential presence, never its value.
        self.token = bool(getattr(client, 'token', None))
    def request(self, method, path, body=None):
        if method != 'GET' or body is not None:
            raise CheckError('Read-only diagnostic refuses all writes')
        return self.client.request(method, path)

def probe(primary, secondary, target, candidate_commit=None):
    validate_target(target)
    primary, secondary = ReadOnlyClient(primary), ReadOnlyClient(secondary)
    result = diagnose(primary, secondary, target)
    result['source'] = 'Actions_existing_credentials_GET_only'
    result['tree_comparison'] = 'NOT_ATTEMPTED'
    result['writes_attempted'] = False
    result['replication_executed'] = False
    if result['status'] == 'READ_ACCESS_CONFIRMED':
        try:
            p, s = snapshot(primary, PRIMARY), snapshot(secondary, target)
            if p['tree'] != s['tree']:
                a = {x['path']: x for x in source_entries(primary.request('GET', f'repos/{PRIMARY}/git/trees/{p["tree"]}?recursive=1'))}
                b = {x['path']: x for x in source_entries(secondary.request('GET', f'repos/{target}/git/trees/{s["tree"]}?recursive=1'), allow_empty=True)}
                result['difference_counts'] = {
                    'primary_files': len(a), 'secondary_files': len(b),
                    'missing_on_secondary': len(a.keys() - b.keys()),
                    'secondary_only': len(b.keys() - a.keys()),
                    'changed_content_or_mode': sum(any(a[k][f] != b[k][f] for f in ('sha','mode','type')) for k in a.keys() & b.keys()),
                }
            result['secondary_snapshot'] = s
            # Same-packages confirmation from the credentialed context. Package files are a
            # subset of the tree, so a tree MATCH implies this; recording it explicitly means
            # the answer is visible even when the overall trees diverge for other reasons.
            pa = {x['path']: x['sha'] for x in source_entries(
                primary.request('GET', f'repos/{PRIMARY}/git/trees/{p["tree"]}?recursive=1'))
                if classify_package(x['path'])}
            pb = {x['path']: x['sha'] for x in source_entries(
                secondary.request('GET', f'repos/{target}/git/trees/{s["tree"]}?recursive=1'), allow_empty=True)
                if classify_package(x['path'])}
            result['package_parity'] = {
                'primary_package_files': len(pa),
                'secondary_package_files': len(pb),
                'identical_package_files': sum(1 for k in pa.keys() & pb.keys() if pa[k] == pb[k]),
                'missing_on_secondary': len(pa.keys() - pb.keys()),
                'secondary_only': len(pb.keys() - pa.keys()),
                'content_differs': sum(1 for k in pa.keys() & pb.keys() if pa[k] != pb[k]),
                'status': 'MATCH' if pa == pb else 'MISMATCH',
                'installed_environment_verified': False,
            }
            if candidate_commit is not None:
                if not re.fullmatch(r'[0-9a-f]{40}', candidate_commit): raise CheckError('Invalid candidate commit')
                candidate_tree = primary.request('GET', f'repos/{PRIMARY}/git/commits/{candidate_commit}')['tree']['sha']
                a = {x['path']: x for x in source_entries(primary.request('GET', f'repos/{PRIMARY}/git/trees/{candidate_tree}?recursive=1'))}
                b = {x['path']: x for x in source_entries(secondary.request('GET', f'repos/{target}/git/trees/{s["tree"]}?recursive=1'), allow_empty=True)}
                result['candidate_counts'] = {'files':len(a), 'secondary_only':len(b.keys()-a.keys()),
                    'missing':len(a.keys()-b.keys()),'changed':sum(any(a[k][f]!=b[k][f] for f in ('sha','mode','type')) for k in a.keys() & b.keys())}
            assert_unchanged(primary, PRIMARY, p)
            assert_unchanged(secondary, target, s)
            result['tree_comparison'] = 'MATCH' if p['tree'] == s['tree'] else 'MISMATCH'
        except APIError as exc:
            result['status'] = 'BLOCKED'
            result['tree_comparison'] = 'UNAVAILABLE'
            result['comparison_http_status'] = exc.status
        except (CheckError, KeyError, ValueError, TypeError):
            result['status'] = 'BLOCKED'
            result['tree_comparison'] = 'UNAVAILABLE_OR_CHANGED'
    # A matching read is not proof of a successful sync or authorization to write.
    result['write_authorization_verified'] = False
    result['dr_sync_verified'] = False
    return result

def annotation(result):
    # Only fixed field names/enums/HTTP integers may enter a public annotation.
    allowed = {'READABLE', 'BLOCKED', 'NOT_ATTEMPTED', 'READ_ACCESS_CONFIRMED',
               'MATCH', 'MISMATCH', 'UNAVAILABLE', 'UNAVAILABLE_OR_CHANGED'}
    def enum(value): return value if isinstance(value, str) and value in allowed else 'UNKNOWN'
    parts = ['read_access=' + enum(result.get('status'))]
    for key in ('identity','primary_repository','primary_main','secondary_repository','secondary_main'):
        value = result.get(key, {})
        status = value.get('http_status')
        parts.append(key + '=' + enum(value.get('status')) + (f':HTTP_{status}' if type(status) is int and 100 <= status <= 599 else ''))
    parts += ['tree=' + enum(result.get('tree_comparison')), 'writes=NONE', 'write_permission=UNVERIFIED']
    for key in ('primary_files', 'secondary_files', 'missing_on_secondary', 'secondary_only', 'changed_content_or_mode'):
        count = result.get('difference_counts', {}).get(key)
        if type(count) is int and 0 <= count <= 10000000: parts.append(f'{key}={count}')
    for key in ('commit','tree'):
        value = result.get('secondary_snapshot',{}).get(key)
        if isinstance(value,str) and re.fullmatch(r'[0-9a-f]{40}',value): parts.append(f'secondary_{key}={value}')
    for key in ('files','secondary_only','missing','changed'):
        value = result.get('candidate_counts',{}).get(key)
        if type(value) is int and 0 <= value <= 10000000: parts.append(f'candidate_{key}={value}')
    parity = result.get('package_parity', {})
    parts.append('packages=' + enum(parity.get('status')) if parity else 'packages=NOT_ATTEMPTED')
    for key in ('primary_package_files','identical_package_files','missing_on_secondary','content_differs'):
        value = parity.get(key)
        if type(value) is int and 0 <= value <= 10000000: parts.append(f'package_{key}={value}')
    parts.append('installed_environment_verified=false')
    return '; '.join(parts)

def trusted_push():
    """A trusted review-branch push: this repository, a push event, an arena/ session branch.

    The branch name is matched by prefix, never pinned to one session. Pinning it to a single
    dead branch (arena/01a10140-vyomarajai) meant the probe refused on every later session, and
    the job that calls it was skipped before it could even refuse; both are fixed together.
    """
    return (os.environ.get('GITHUB_REPOSITORY') == PRIMARY
            and os.environ.get('GITHUB_EVENT_NAME') == 'push'
            and os.environ.get('GITHUB_REF', '').startswith('refs/heads/arena/'))


def main():
    if not trusted_push():
        print('Read-only probe is restricted to the trusted review-branch push.');return 2
    if not os.environ.get('PRIMARY_TOKEN') or not os.environ.get('DR_TOKEN'):
        result = {'status':'BLOCKED','tree_comparison':'NOT_ATTEMPTED','reason':'required_actions_secret_unavailable',
                  'writes_attempted':False,'replication_executed':False,'write_authorization_verified':False,'dr_sync_verified':False}
    else:
        target = json.loads(Path(__file__).with_name('DR_POLICY.json').read_text())['secondary']
        result = probe(GitHub(os.environ['PRIMARY_TOKEN']), GitHub(os.environ['DR_TOKEN']), target, os.environ.get('GITHUB_SHA'))
    Path('dr-read-probe.json').write_text(json.dumps(result, indent=2) + '\n')
    print('::notice title=DR READ-ONLY DIAGNOSTIC::' + annotation(result))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write('## DR credential read diagnostic\n\n' + annotation(result) + '\n\nNo data or refs written. Green means readable, not replicated or write-authorized.\n')
    return 0 if result['status'] == 'READ_ACCESS_CONFIRMED' else 2

if __name__ == '__main__': sys.exit(main())
