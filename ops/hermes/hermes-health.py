#!/usr/bin/env python3
"""Local Hermes decision journal for Bharath and Laxman.

This utility records peer heartbeats and evaluates whether a guarded failover
condition is satisfied. It does not change Git refs, credentials, networks, or
production traffic.
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path

STATE = Path('.hermes-state.json')
HEADS = ('bharath', 'laxman')

def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    now = time.time()
    return {'active':'bharath','heads':{h:{'healthy':True,'last_heartbeat':now,'fenced':False,'seq':0} for h in HEADS},'conflicts':[]}

def save(s):
    STATE.write_text(json.dumps(s, indent=2, sort_keys=True))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('command', choices=['status','heartbeat','evaluate'])
    p.add_argument('--head', choices=HEADS)
    p.add_argument('--seq', type=int, default=0)
    p.add_argument('--timeout', type=int, default=90)
    a=p.parse_args()
    s=load()
    if a.command=='heartbeat':
        if not a.head: p.error('--head required')
        s['heads'][a.head].update(healthy=True,last_heartbeat=time.time(),seq=max(a.seq,s['heads'][a.head]['seq']))
        save(s)
        print(json.dumps({'accepted':True,'head':a.head,'seq':s['heads'][a.head]['seq']},indent=2))
        return
    if a.command=='status':
        print(json.dumps(s,indent=2,sort_keys=True))
        return
    if not a.head: p.error('--head required')
    survivor='laxman' if a.head=='bharath' else 'bharath'
    failed=s['heads'][a.head]
    peer_timeout=(time.time()-failed['last_heartbeat'])>a.timeout
    survivor_ok=s['heads'][survivor]['healthy'] and not s['heads'][survivor]['fenced']
    unresolved=any(x.get('status')=='UNRESOLVED' for x in s['conflicts'])
    decision=peer_timeout and survivor_ok and not unresolved
    print(json.dumps({'failed_head':a.head,'survivor':survivor,'peer_timeout':peer_timeout,'survivor_ok':survivor_ok,'unresolved_conflict':unresolved,'failover_gate': 'OPEN' if decision else 'CLOSED','note':'Promotion still requires an external fencing, integrity and business-probe implementation.'},indent=2))

if __name__=='__main__':
    main()
