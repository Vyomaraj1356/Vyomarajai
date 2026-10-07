import json
import unittest
from gateway import Router,UpstreamUnavailable,validate_loopback_host

class Tests(unittest.TestCase):
    def test_gateway_bind_policy_is_loopback_only(self):
        self.assertEqual(validate_loopback_host('127.0.0.1'),'127.0.0.1')
        for host in ('0.0.0.0','192.0.2.1','::1','localhost'):
            with self.subTest(host=host),self.assertRaises(ValueError):
                validate_loopback_host(host)

    def test_get_fallback(self):
        calls=[]
        def fake(p,*args,**kwargs):
            calls.append(p)
            if p==1:raise UpstreamUnavailable()
            return 200,{},b'healthy'
        r=Router((1,2),fake);self.assertEqual(r.route('GET','/')[0],200);self.assertEqual(calls,[1,2])
        self.assertEqual(r.stats['secondary_responses'],1)
    def test_http_503_fallback(self):
        r=Router((1,2),lambda p,*a,**k:(503 if p==1 else 200,{},b'body'))
        self.assertEqual(r.route('GET','/')[0],200)
    def test_404_is_not_hidden_by_failover(self):
        calls=[]
        def fake(p,*a,**k):calls.append(p);return 404,{},b'not found'
        self.assertEqual(Router((1,2),fake).route('GET','/absent')[0],404);self.assertEqual(calls,[1])
    def test_both_down_not_false_success(self):
        def fail(*args,**kw):raise UpstreamUnavailable()
        r=Router((1,2),fail);self.assertEqual(r.route('GET','/')[0],503)
        s=r.status();self.assertFalse(s['production_dr_verified']);self.assertFalse(s['zero_rto_claimed'])
    def test_post_never_replayed(self):
        writes=[]
        def fake(p,method,*args,**kwargs):
            if method=='GET':return 200,{},b'{"ready":true}'
            writes.append(p);raise UpstreamUnavailable()
        r=Router((1,2),fake);code,h,b=r.route('POST','/api/plan',{},b'{}')
        self.assertEqual(code,503);self.assertEqual(writes,[1]);self.assertIn(b'not_retried',b)
    def test_post_selects_live_replica_once(self):
        writes=[]
        def fake(p,method,*args,**kwargs):
            if p==1:raise UpstreamUnavailable()
            if method=='GET':return 200,{},b'{"ready":true}'
            writes.append(p);return 200,{},b'ok'
        self.assertEqual(Router((1,2),fake).route('POST','/api/plan')[0],200);self.assertEqual(writes,[2])
    def test_arbitrary_proxy_routes_refused(self):
        def no_call(*a,**k):raise AssertionError()
        r=Router((1,2),no_call)
        for method,url in [('DELETE','/'),('GET','https://example.com'),('GET','//evil.test/')]:self.assertEqual(r.route(method,url)[0],400)
    def test_health_shape_not_fake_ready(self):
        for body in (b'no JSON',b'[]',b'{"ready":false}'):
            r=Router((1,2),lambda *a,**k:(200,{},body));self.assertFalse(r.ready(1))

if __name__=='__main__':unittest.main()
