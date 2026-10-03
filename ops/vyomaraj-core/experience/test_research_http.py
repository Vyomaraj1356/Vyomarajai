import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
import studio_server as server

class ResearchHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.old=server.RESEARCH_STORE
        server.RESEARCH_STORE=server.discovery.Store(Path(cls.temp.name)/'db.sqlite3')
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.http.server_port)
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.thread.join();server.RESEARCH_STORE=cls.old;cls.temp.cleanup()
    def request(self,path,data=None,headers=None):
        req=urllib.request.Request(self.base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers or ({'Content-Type':'application/json'} if data is not None else {}))
        try:
            with urllib.request.urlopen(req) as r:return r.status,r.read(),r.headers
        except urllib.error.HTTPError as e:return e.code,e.read(),e.headers
    def test_status_and_assets(self):
        for route in ['/research/','/research/app.js','/research/styles.css','/api/research/status']:
            status,body,headers=self.request(route);self.assertEqual(status,200)
            self.assertIn("default-src 'none'",headers['Content-Security-Policy'])
        data=json.loads(self.request('/api/research/status')[1]);self.assertFalse(data['automatic_publishing'])
    def test_enqueue_closed_fields_and_profile(self):
        self.assertEqual(self.request('/api/research/run',{'profile':'hindi-theatre'})[0],202)
        for body in [{'profile':'evil'}, {'profile':'hindi-theatre','url':'http://localhost/private'}, [], {'profile':[]}]:
            self.assertEqual(self.request('/api/research/run',body)[0],400)
    def test_cross_origin_refused(self):
        self.assertEqual(self.request('/api/research/run',{'profile':'classic-films'},{'Content-Type':'application/json','Origin':'https://evil.example'})[0],403)
    def test_same_origin_accepted(self):
        self.assertEqual(self.request('/api/research/run',{'profile':'classic-films'},{'Content-Type':'application/json','Origin':self.base})[0],202)
    def test_review_requires_ack_and_does_not_publish(self):
        r=server.discovery.candidate('fixture','one','Fixture','https://example.org/source','classic-films');server.RESEARCH_STORE.save(r)
        body={'record_id':r['id'],'decision':'accepted_metadata_only','acknowledge_metadata_only':False}
        self.assertEqual(self.request('/api/research/review',body)[0],400)
        body['acknowledge_metadata_only']=True;status,raw,_=self.request('/api/research/review',body);data=json.loads(raw)
        self.assertEqual(status,200);self.assertEqual(data['rights_status'],'UNKNOWN');self.assertIsNone(data['media_url'])
    def test_export_and_pagination(self):
        self.assertEqual(self.request('/api/research/records?offset=-1')[0],400)
        self.assertEqual(self.request('/api/research/records?offset=abc')[0],400)
        self.assertEqual(json.loads(self.request('/api/research/records?offset=5000')[1])['records'],[])
        self.assertEqual(json.loads(self.request('/api/research/export')[1])['scope'],'unverified_metadata_not_media_or_licences')
    def test_private_state_and_templates_not_served(self):
        for path in ['/research/.state/discovery.sqlite3','/research/.env','/research/compose.example.yml','/research/discovery.py','/.git/config','/api/research/settings']:
            self.assertEqual(self.request(path)[0],404)
    def test_json_required_no_form_posts(self):
        self.assertEqual(self.request('/api/research/run',{'profile':'classic-films'},{'Content-Type':'text/plain'})[0],415)

if __name__=='__main__':unittest.main()
