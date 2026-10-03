#!/usr/bin/env python3
"""GET-only GitHub audit; no secret values, raw logs or identity responses are emitted."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent

def get(path):
    try:r=subprocess.run(['gh','api','--method','GET',path],capture_output=True,text=True,timeout=45)
    except (OSError,subprocess.TimeoutExpired):return {'status':'unavailable'},None
    if r.returncode:
        m=re.search(r'HTTP (\d{3})',r.stderr)
        return {'http':int(m[1]) if m else None,'status':'blocked'},None
    try:return {'http':200,'status':'readable'},json.loads(r.stdout)
    except ValueError:return {'status':'invalid_response'},None

def audit():
    policy=json.loads((ROOT/'DR_POLICY.json').read_text());primary=policy['primary'];target=policy['secondary']
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'credential_context':'Arena gh connection, distinct from Actions PAT',
            'confirmed_main_target':target,'mode':'GET_only','writes_attempted':False,'replication_verified':False,'production_failover_verified':False,'zero_rpo_or_rto_claimed':False,'checks':{}}
    paths={'primary':f'repos/{primary}','primary_main':f'repos/{primary}/git/ref/heads/main','secondary':f'repos/{target}',
           'variables':f'repos/{primary}/actions/variables','secret_names_only':f'repos/{primary}/actions/secrets',
           'workflow_permissions':f'repos/{primary}/actions/permissions/workflow'}
    for name,path in paths.items():
        status,data=get(path)
        if data and name=='primary':status['reported_repository_permissions']=data.get('permissions',{})
        if data and name=='primary_main':status['sha']=data.get('object',{}).get('sha')
        if data and name=='secret_names_only':status['pat_secret_name_present']=any(s['name']=='VYOMARAJ_PAT' for s in data.get('secrets',[]))
        report['checks'][name]=status
    status,data=get(f'repos/{primary}/actions/workflows/vyomaraj-sync-both.yml/runs?branch=main&per_page=1')
    if data and data.get('workflow_runs'):
        run=data['workflow_runs'][0];status.update({k:run[k] for k in ('id','head_sha','status','conclusion','html_url')})
        js,jobs=get(f'repos/{primary}/actions/runs/{run["id"]}/jobs')
        if jobs:
            status['jobs']=[{'name':j['name'],'status':j['status'],'conclusion':j['conclusion'],
                'steps':[{'name':s['name'],'conclusion':s['conclusion'],'status':s['status']} for s in j['steps']]} for j in jobs['jobs']]
            # Job success alone is evidence of its workflow checks, NOT production service DR.
            status['authentication_step_passed']=any(s['name']=='Authenticate DR' and s['conclusion']=='success' for j in jobs['jobs'] for s in j['steps'])
    report['main_workflow_observation']=status
    report['interpretation']='A private 404 through Arena does not invalidate a successful Actions-PAT read. Repository admin metadata does not grant missing token endpoint scopes. No failed-log cause is inferred from unavailable logs.'
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    value=json.dumps(audit(),indent=2)+'\n'
    if a.output:a.output.write_text(value)
    else:print(value,end='')
