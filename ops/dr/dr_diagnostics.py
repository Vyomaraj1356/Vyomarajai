#!/usr/bin/env python3
"""Redacted GET-only preflight. Identity success is not repository or write authorization."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from dr_sync import GitHub, PRIMARY, validate_target, CheckError, APIError


def probe(client, path, repo=None):
    try:
        data = client.request('GET', path)
        if not isinstance(data, dict):
            return {'status': 'BLOCKED', 'reason': 'invalid_response_shape'}
        if path == 'user' and (type(data.get('id')) is not int or data['id'] <= 0):
            return {'status': 'BLOCKED', 'reason': 'invalid_identity_response'}
        if repo and str(data.get('full_name', '')).lower() != repo.lower():
            return {'status': 'BLOCKED', 'reason': 'repository_identity_mismatch'}
        if '/git/ref/' in path and (not isinstance(data.get('object'), dict) or not isinstance(data['object'].get('sha'), str) or len(data['object']['sha']) != 40):
            return {'status': 'BLOCKED', 'reason': 'missing_ref_sha'}
        return {'status': 'READABLE'}
    except APIError as exc:
        return {'status': 'BLOCKED', 'http_status': exc.status,
                'reason': {401:'credential_rejected',403:'permission_or_rate_limit',404:'missing_or_hidden_by_permissions'}.get(exc.status,'request_failed')}
    except (CheckError, ValueError, KeyError, TypeError):
        return {'status': 'BLOCKED', 'reason': 'request_or_response_unavailable'}


def diagnose(primary, secondary, target):
    evidence = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'mode': 'GET_only',
                'primary_credential_source': 'explicit_process_token' if getattr(primary, 'token', None) else 'local_gh_fallback',
                'secondary_credential_source': 'explicit_process_token' if getattr(secondary, 'token', None) else 'local_gh_fallback',
                'writes_attempted': False, 'write_authorization_verified': False,
                'pat_identity_proves_repo_access': False, 'dr_sync_verified': False,
                'identity': probe(secondary, 'user'),
                'primary_repository': probe(primary, f'repos/{PRIMARY}', PRIMARY),
                'primary_main': probe(primary, f'repos/{PRIMARY}/git/ref/heads/main')}
    try:
        validate_target(target)
    except CheckError:
        evidence['secondary_repository'] = {'status':'BLOCKED','reason':'confirmed_target_required'}
        evidence['secondary_main'] = {'status':'NOT_ATTEMPTED'}
    else:
        evidence['secondary_repository'] = probe(secondary, f'repos/{target}', target)
        evidence['secondary_main'] = probe(secondary, f'repos/{target}/git/ref/heads/main') if evidence['secondary_repository']['status']=='READABLE' else {'status':'NOT_ATTEMPTED'}
    evidence['status'] = 'READ_ACCESS_CONFIRMED' if all(evidence[k]['status']=='READABLE' for k in ('primary_repository','primary_main','secondary_repository','secondary_main')) else 'BLOCKED'
    evidence['note'] = 'Identity endpoint may be unavailable for an installation token. Repository/ref GETs are authoritative for read access only; neither they nor /user verify writes or tree equality.'
    return evidence


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args=parser.parse_args()
    result=diagnose(GitHub(os.environ.get('PRIMARY_TOKEN')),GitHub(os.environ.get('DR_TOKEN')),os.environ.get('DR_REPO',''))
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text,end='')
    raise SystemExit(0 if result['status']=='READ_ACCESS_CONFIRMED' else 2)
