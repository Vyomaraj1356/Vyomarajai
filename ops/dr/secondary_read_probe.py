#!/usr/bin/env python3
"""Read-only secondary probe that publishes closed-vocabulary annotations.

Same guarantees as ops/dr/actions_read_probe.py (GET only, no writes, sanitized annotation),
but runnable from a trusted same-repository pull request or manual dispatch instead of only
from the review-branch push, so a sandbox that cannot download Actions logs can still read
the secondary's exact commit and tree. Never replicates, never switches traffic.
"""
import json
import os
from pathlib import Path

from actions_read_probe import annotation, probe
from dr_sync import GitHub, PRIMARY


def allowed_event():
    if os.environ.get('GITHUB_REPOSITORY') != PRIMARY:
        return False
    event = os.environ.get('GITHUB_EVENT_NAME')
    if event == 'push':
        return True  # same-repository trusted push
    if event in ('pull_request', 'workflow_dispatch'):
        # Fork pull requests never receive the DR secret; refuse them explicitly as well.
        head_repo = os.environ.get('GITHUB_HEAD_REPOSITORY', PRIMARY)
        return head_repo == PRIMARY
    return False


def main():
    if not allowed_event():
        print('Read-only probe refused: untrusted event context.')
        return 2
    if not os.environ.get('PRIMARY_TOKEN') or not os.environ.get('DR_TOKEN'):
        result = {'status': 'BLOCKED', 'tree_comparison': 'NOT_ATTEMPTED',
                  'reason': 'required_actions_secret_unavailable', 'writes_attempted': False,
                  'replication_executed': False, 'write_authorization_verified': False,
                  'dr_sync_verified': False}
    else:
        target = json.loads(Path(__file__).with_name('DR_POLICY.json').read_text())['secondary']
        result = probe(GitHub(os.environ['PRIMARY_TOKEN']), GitHub(os.environ['DR_TOKEN']),
                       target, os.environ.get('GITHUB_SHA'))
    Path('dr-read-probe.json').write_text(json.dumps(result, indent=2) + '\n')
    print('::notice title=DR READ-ONLY DIAGNOSTIC::' + annotation(result), flush=True)
    return 0 if result['status'] == 'READ_ACCESS_CONFIRMED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
