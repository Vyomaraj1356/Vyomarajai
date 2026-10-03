#!/usr/bin/env python3
"""Single-host application failover rehearsal, NOT an independent DR site.
Fixed loopback upstreams only. GET can fall back; a POST is never replayed.
"""
import argparse
import http.client
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import threading
from urllib.parse import urlsplit

MAX_REQUEST=16384
MAX_RESPONSE=16*1024*1024
HOP={'connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailer','transfer-encoding','upgrade','content-length','host'}

class UpstreamUnavailable(Exception):pass

def call(port,method,path,headers=None,body=None,timeout=2):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=timeout)
    try:
        c.request(method,path,body=body,headers=headers or {})
        r=c.getresponse();payload=r.read(MAX_RESPONSE+1)
        if len(payload)>MAX_RESPONSE:raise UpstreamUnavailable('response_limit')
        return r.status,dict(r.getheaders()),payload
    except (OSError,http.client.HTTPException):raise UpstreamUnavailable('upstream_unavailable') from None
    finally:c.close()

class Router:
    def __init__(self,ports,transport=call):
        self.ports=ports;self.transport=transport;self.lock=threading.Lock()
        self.stats={'primary_responses':0,'secondary_responses':0,'ambiguous_post_failures':0,'unavailable_responses':0}
    def ready(self,p):
        try:
            code,headers,body=self.transport(p,'GET','/healthz',timeout=0.75)
            return code==200 and json.loads(body).get('ready') is True
        except (UpstreamUnavailable,ValueError,TypeError,AttributeError):return False
    def status(self):
        with self.lock:stats=dict(self.stats)
        return {'mode':'SINGLE_HOST_REHEARSAL_NOT_PRODUCTION_DR','independent_failure_domains':False,
            'shared_filesystem_and_queue':True,'production_dr_verified':False,'zero_rto_claimed':False,
            'replicas':[{'role':role,'metadata_ready':self.ready(p)} for role,p in zip(('Vyomaraj replica','Jarvis replica'),self.ports)],
            'write_policy':'POST is sent once, never replayed after an ambiguous failure','counters':stats}
    def route(self,method,path,headers=None,body=None):
        if method not in ('GET','POST') or not path.startswith('/') or path.startswith('//') or urlsplit(path).scheme:
            return 400,{},b'{"error":"invalid_route"}'
        if method=='POST':
            candidates=[p for p in self.ports if self.ready(p)][:1]
        else:candidates=list(self.ports)
        for port in candidates:
            try:
                code,h,payload=self.transport(port,method,path,headers,body)
                if method=='GET' and code>=500:continue
                key='primary_responses' if port==self.ports[0] else 'secondary_responses'
                with self.lock:self.stats[key]+=1
                h['X-Vyomaraj-Replica']='primary' if port==self.ports[0] else 'secondary'
                return code,h,payload
            except UpstreamUnavailable:
                if method=='POST':
                    with self.lock:self.stats['ambiguous_post_failures']+=1
                    return 503,{'Content-Type':'application/json'},b'{"error":"write_outcome_unknown_not_retried","action":"Inspect job/review state before retrying."}'
        with self.lock:self.stats['unavailable_responses']+=1
        return 503,{'Content-Type':'application/json'},b'{"error":"no_ready_replica","production_dr_verified":false}'

class Handler(BaseHTTPRequestHandler):
    router=None
    def reply(self,code,headers,body):
        self.send_response(code)
        for k,v in headers.items():
            if k.lower() not in HOP|{'server','date','cache-control','x-content-type-options'}:self.send_header(k,v)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.end_headers();self.wfile.write(body)
    def dispatch(self):
        if self.headers.get('Transfer-Encoding'):
            self.close_connection=True;self.reply(400,{},b'Chunked requests are not supported');return
        try:length=int(self.headers.get('Content-Length','0'))
        except ValueError:self.reply(400,{},b'Invalid content length');return
        if not 0<=length<=MAX_REQUEST:
            self.close_connection=True;self.reply(413,{},b'Request too large');return
        self.connection.settimeout(10)
        try:body=self.rfile.read(length) if length else None
        except OSError:self.reply(408,{},b'Request timeout');return
        if body is not None and len(body)!=length:self.reply(400,{},b'Incomplete body');return
        if self.command=='GET' and self.path=='/api/availability':
            self.reply(200,{'Content-Type':'application/json'},json.dumps(self.router.status()).encode());return
        headers={k:v for k,v in self.headers.items() if k.lower() not in HOP}
        # Preserve original same-origin identity; browsers never call backend localhost URLs.
        headers['Host']=self.headers.get('Host','')
        self.reply(*self.router.route(self.command,self.path,headers,body))
    do_GET=dispatch
    do_POST=dispatch
    def log_message(self,*args):pass

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=4176)
    p.add_argument('--primary-port',type=int,default=4181);p.add_argument('--secondary-port',type=int,default=4182);a=p.parse_args()
    if len({a.port,a.primary_port,a.secondary_port})!=3 or any(not 1024<=v<=65535 for v in (a.port,a.primary_port,a.secondary_port)):raise SystemExit('Use three distinct unprivileged ports.')
    Handler.router=Router((a.primary_port,a.secondary_port))
    print(f'Local failover rehearsal gateway on 0.0.0.0:{a.port}; not independent-site DR',flush=True)
    ThreadingHTTPServer(('0.0.0.0',a.port),Handler).serve_forever()
