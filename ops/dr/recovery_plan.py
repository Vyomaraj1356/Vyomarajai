#!/usr/bin/env python3
"""Prepare a GET-only secondary-to-primary recovery REVIEW, never an overwrite."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
from dr_sync import GitHub,PRIMARY,validate_target,snapshot,assert_unchanged,CheckError

def plan(target,primary,secondary):
    validate_target(target)
    for client,repo in [(primary,PRIMARY),(secondary,target)]:
        info=client.request('GET',f'repos/{repo}')
        if info.get('full_name','').lower()!=repo.lower():raise CheckError('Repository identity mismatch')
    p=snapshot(primary,PRIMARY);s=snapshot(secondary,target)
    assert_unchanged(primary,PRIMARY,p);assert_unchanged(secondary,target,s)
    return {'created_at_utc':datetime.now(timezone.utc).isoformat(),'mode':'READ_ONLY_RECOVERY_REVIEW',
        'source_secondary':{'repository':target,**s},'destination_primary':{'repository':PRIMARY,**p},
        'trees_equal':p['tree']==s['tree'],'writes_performed':False,'automatic_reverse_sync':False,
        'required_gates':['Fence the previous writer and pause scheduled replication before promotion.',
          'Select a reviewed known-good snapshot; a matching or newer tree is not proof it is safe.',
          'Back up current primary state and runtime databases outside the failure domain.',
          'Review diff, secrets, permissions and malware before a protected restore PR.',
          'Recheck BOTH refs immediately before any restore; this plan is not a write capability.',
          'Test application readiness, data recovery and traffic switching on independent infrastructure.'],
        'execution':'not_implemented_no_primary_or_secondary_ref_write','rto_rpo':'not_measured'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',required=True);p.add_argument('--output',type=Path);a=p.parse_args()
    try:d=plan(a.target,GitHub(os.environ.get('PRIMARY_TOKEN')),GitHub(os.environ.get('DR_TOKEN')))
    except (CheckError,KeyError,TypeError,ValueError):d={'status':'BLOCKED','reason':'read_access_or_snapshot_validation_failed','writes_performed':False}
    value=json.dumps(d,indent=2)+'\n'
    if a.output:a.output.write_text(value)
    else:print(value,end='')
    raise SystemExit(2 if d.get('status')=='BLOCKED' else 0)
