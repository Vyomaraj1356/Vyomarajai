#!/usr/bin/env python3
"""GET-only Actions credential probe; no blobs, filenames, secret values or writes."""
import json
import os
from pathlib import Path
import sys
from dr_sync import GitHub, PRIMARY, CheckError, APIError, snapshot, assert_unchanged, validate_target, source_entries
from dr_diagnostics import diagnose

class ReadOnlyClient:
    def __init__(self, client):
        self.client = client
        # Diagnostics need only credential presence, never its value.
        self.token = bool(getattr(client, 'token', None))
    def request(self, method, path, body=None):
        if method != 'GET' or body is not None:
            raise CheckError('Read-only diagnostic refuses all writes')
        return self.client.request(method, path)

def probe(primary, secondary, target):
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
    return '; '.join(parts)

def main():
    if os.environ.get('GITHUB_REPOSITORY') != PRIMARY or os.environ.get('GITHUB_EVENT_NAME') != 'push' or os.environ.get('GITHUB_REF') != 'refs/heads/arena/01a10140-vyomarajai':
        print('Read-only probe is restricted to the trusted review-branch push.');return 2
    if not os.environ.get('PRIMARY_TOKEN') or not os.environ.get('DR_TOKEN'):
        result = {'status':'BLOCKED','tree_comparison':'NOT_ATTEMPTED','reason':'required_actions_secret_unavailable',
                  'writes_attempted':False,'replication_executed':False,'write_authorization_verified':False,'dr_sync_verified':False}
    else:
        target = json.loads(Path(__file__).with_name('DR_POLICY.json').read_text())['secondary']
        result = probe(GitHub(os.environ['PRIMARY_TOKEN']), GitHub(os.environ['DR_TOKEN']), target)
    Path('dr-read-probe.json').write_text(json.dumps(result, indent=2) + '\n')
    print('::notice title=DR READ-ONLY DIAGNOSTIC::' + annotation(result))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write('## DR credential read diagnostic\n\n' + annotation(result) + '\n\nNo data or refs written. Green means readable, not replicated or write-authorized.\n')
    return 0 if result['status'] == 'READ_ACCESS_CONFIRMED' else 2

if __name__ == '__main__': sys.exit(main())
