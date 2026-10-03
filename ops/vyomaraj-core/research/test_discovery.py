import io
import json
import os
import sys
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch, Mock
import urllib.error
import discovery as d

MB_ID='01234567-1234-1234-1234-123456789abc'

def fixture(url,payload=None):
    if 'musicbrainz.org' in url:return {'release-groups':[{'id':MB_ID,'title':'Fixture album','first-release-date':'2025-01-02'}]}
    if 'loc.gov' in url:return {'results':[{'id':'https://www.loc.gov/item/123/','url':'https://www.loc.gov/item/123/','title':'Fixture archive','date':'1930'}]}
    if 'openlibrary.org' in url:return {'docs':[{'key':'/works/OL123W','title':'Fixture play','first_publish_year':1967}]}
    if '/api/chat' in url:return {'message':{'content':json.dumps({'summary':'Fixture advisory note.'})}}
    if '/search?' in url:return {'results':[{'url':'https://example.org/film','title':'Fixture search lead'}]}
    raise AssertionError('Unexpected fixture endpoint')

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=d.Store(Path(self.temp.name)/'db.sqlite3');self.store.throttle=lambda p:None
        p=patch.dict(os.environ,{'VYOMARAJ_SEARXNG_URL':'','VYOMARAJ_OLLAMA_URL':'','VYOMARAJ_OLLAMA_MODEL':''});p.start();self.addCleanup(p.stop)
    def record(self):return d.candidate('fixture','one','Sample','https://example.org/source','classic-films')
    def test_public_url_rejects_unsafe(self):
        for url in ['javascript:alert(1)','http://127.0.0.1/a','http://169.254.169.254/x','http://localhost/x','http://x.local/a','http://[::1]/','https://user:pass@example.org','https://example.org:444/a','https://example.org\\@localhost/x','http://127.1/a','http://0x7f.0.0.1/a','http://localhost./a','file:///etc/passwd','http://10.0.0.1/a','https://example.org/a b']:
            self.assertIsNone(d.public_url(url),url)
        self.assertEqual(d.public_url('https://example.org/a#x'),'https://example.org/a')
    def test_musicbrainz_normalization(self):
        rows=d.adapter('musicbrainz','classic-music',fixture)
        self.assertEqual(rows[0]['external_id'],MB_ID);self.assertEqual(rows[0]['rights_status'],'UNKNOWN');self.assertIsNone(rows[0]['media_url'])
    def test_musicbrainz_bounded_query_identification(self):
        f=Mock(side_effect=fixture);d.adapter('musicbrainz','recent-music',f)
        self.assertIn('limit=5',f.call_args.args[0]);self.assertIn('firstreleasedate',f.call_args.args[0]);self.assertIn('github.com',d.USER_AGENT)
    def test_loc_and_openlibrary_provenance(self):
        r=d.adapter('loc','classic-films',fixture)[0];self.assertEqual(r['provider_date'],'1930');self.assertIn('loc.gov',r['source_url'])
        r=d.adapter('openlibrary','marathi-theatre',fixture)[0];self.assertIn('not a theatre recording',r['description']);self.assertEqual(r['proposed_slots'],['ENT-MOVIE-S4'])
    def test_invalid_provider_payloads(self):
        for p,profile in [('musicbrainz','classic-music'),('loc','classic-films'),('openlibrary','marathi-theatre')]:
            with self.assertRaises(d.DiscoveryError):d.adapter(p,profile,lambda u:{'docs':'not a list'})
    def test_bad_result_rows_skipped(self):
        f=lambda u:{'docs':[None,{}, {'key':'../../secret','title':'Do not use'}]}
        self.assertEqual(d.adapter('openlibrary','hindi-theatre',f),[])
    def test_loc_external_host_not_accepted(self):
        self.assertEqual(d.adapter('loc','classic-films',lambda u:{'results':[{'id':'https://evil.org/a','title':'wrong host'}]}),[])
    def test_catalog_reuses_attributed_packs(self):
        rows=d.catalog('marathi-theatre');self.assertGreater(len(rows),0)
        self.assertTrue(all(r['provider']=='catalog' for r in rows));self.assertLessEqual(len(rows),5)
    def test_unknown_profile_refused(self):
        with self.assertRaises(d.DiscoveryError):self.store.enqueue('https://evil.org')
    def test_enqueue_dedup(self):
        a=self.store.enqueue('classic-films');b=self.store.enqueue('classic-films');self.assertEqual(a['id'],b['id']);self.assertTrue(b['reused'])
    def test_single_claim_across_store_instances(self):
        self.store.enqueue('classic-films');self.store.enqueue('classic-music')
        self.assertIsNotNone(self.store.claim());self.assertIsNone(d.Store(self.store.path).claim())
    def test_expired_worker_recovery(self):
        a=self.store.enqueue('classic-films');self.store.claim()
        with self.store.db() as c:c.execute('UPDATE jobs SET updated=?',(time.time()-601,))
        self.store.claim();self.assertEqual(self.store.status()['jobs'][0]['state'],'interrupted')
        self.assertEqual(self.store.status()['jobs'][0]['id'],a['id'])
    def test_queue_capacity(self):
        with self.store.db() as c:
            for i in range(10):c.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?)',(str(i),'other','queued',time.time(),time.time(),'{}'))
        with self.assertRaisesRegex(d.DiscoveryError,'queue_full'):self.store.enqueue('classic-films')
    def test_success_cache_and_expiry(self):
        self.store.cache('key',[]);self.assertEqual(self.store.cached('key'),[])
        with self.store.db() as c:c.execute('UPDATE cache SET expires=0')
        self.assertIsNone(self.store.cached('key'))
    def test_saves_preserve_review_until_metadata_changes(self):
        r=self.record();self.assertTrue(self.store.save(r));self.store.review(r['id'],'accepted_metadata_only')
        self.assertFalse(self.store.save(self.record()));self.assertEqual(self.store.records()[0]['review_status'],'accepted_metadata_only')
        r=self.record();r['title']='Changed';self.store.save(r);self.assertEqual(self.store.records()[0]['review_status'],'pending_review')
    def test_multi_profile_merge_does_not_merge_different_provider(self):
        r=self.record();self.store.save(r);r['profiles']=['marathi-theatre'];r['proposed_slots']=['ENT-MOVIE-S4'];self.store.save(r)
        self.assertEqual(len(self.store.records()[0]['profiles']),2)
        r=d.candidate('different','one','Sample','https://example.org/source','classic-films');self.store.save(r);self.assertEqual(len(self.store.records()),2)
    def test_review_never_clears_rights_or_publishes(self):
        r=self.record();self.store.save(r);self.store.review(r['id'],'accepted_metadata_only');saved=self.store.records()[0]
        self.assertEqual(saved['rights_status'],'UNKNOWN');self.assertIsNone(saved['media_url']);self.assertFalse(self.store.status()['automatic_publishing'])
        self.assertEqual(self.store.status()['review_events_retained'],1)
    def test_unknown_review_decision_rejected(self):
        with self.assertRaises(d.DiscoveryError):self.store.review('x','licensed')
        with self.assertRaises(d.DiscoveryError):self.store.review('x','accepted_metadata_only')
    def test_runtime_failures_not_empty_success(self):
        self.store.enqueue('classic-music')
        def fail(*args):raise d.DiscoveryError('network_unavailable')
        result=d.process_one(self.store,fail)
        self.assertEqual(result['state'],'partial');self.assertEqual(result['sources']['musicbrainz']['status'],'blocked')
        self.assertEqual(result['sources']['catalog']['origin'],'existing_editorial_pack')
        self.assertIsNone(self.store.cached('musicbrainz:classic-music:v1'))
    def test_real_provider_empty_result_is_success_not_failure(self):
        self.store.enqueue('recent-music');r=d.process_one(self.store,lambda u:{'release-groups':[]})
        self.assertEqual(r['sources']['musicbrainz']['records'],0);self.assertEqual(r['sources']['musicbrainz']['status'],'ok')
    def test_optional_searxng_not_misreported(self):
        self.store.enqueue('recent-films');r=d.process_one(self.store,fixture)
        self.assertEqual(r['state'],'blocked');self.assertEqual(r['sources']['searxng']['status'],'not_configured')
    def test_searxng_local_service_fixture(self):
        with patch.dict(os.environ,{'VYOMARAJ_SEARXNG_URL':'http://127.0.0.1:8080'}):
            self.assertEqual(len(d.adapter('searxng','recent-films',fixture)),1)
    def test_local_services_refuse_arbitrary_egress(self):
        for url in ['https://evil.org','http://169.254.169.254:8080','http://localhost:8080/private','http://user:pass@localhost:8080','http://localhost:8080/?token=x']:
            with patch.dict(os.environ,{'VYOMARAJ_SEARXNG_URL':url}):
                with self.assertRaises(d.DiscoveryError):d.local_base('searxng',8080)
    def test_invalid_local_port_is_redacted(self):
        with patch.dict(os.environ,{'VYOMARAJ_SEARXNG_URL':'http://localhost:PRIVATE_VALUE'}):
            with self.assertRaisesRegex(d.DiscoveryError,'^invalid_local_service_configuration$'):d.local_base('searxng',8080)
    def test_ollama_output_is_advisory_only(self):
        r=self.record()
        with patch.dict(os.environ,{'VYOMARAJ_OLLAMA_URL':'http://127.0.0.1:11434','VYOMARAJ_OLLAMA_MODEL':'fixture'}):
            note=d.ai_note(r,fixture);self.assertEqual(note['status'],'AI_ADVISORY_UNVERIFIED');self.assertEqual(r['rights_status'],'UNKNOWN')
    def test_ollama_malformed_and_extra_actions_rejected(self):
        with patch.dict(os.environ,{'VYOMARAJ_OLLAMA_URL':'http://127.0.0.1:11434','VYOMARAJ_OLLAMA_MODEL':'fixture'}):
            for body in ['bad',json.dumps({'summary':'x','publish':True}),json.dumps({'summary':[]})]:
                with self.assertRaises(d.DiscoveryError):d.ai_note(self.record(),lambda *a:{'message':{'content':body}})
    def test_complete_fixture_run_then_cache_no_network(self):
        with patch.dict(os.environ,{'VYOMARAJ_SEARXNG_URL':'http://127.0.0.1:8080'}):
            self.store.enqueue('classic-music');result=d.process_one(self.store,fixture);self.assertEqual(result['state'],'completed')
            with self.store.db() as c:c.execute('UPDATE jobs SET created=0')
            self.store.enqueue('classic-music');f=Mock(side_effect=AssertionError('Unexpected network call'))
            result=d.process_one(self.store,f);self.assertEqual(result['state'],'completed');f.assert_not_called();self.assertEqual(result['new_records'],0)
    def test_throttle_shared_and_at_least_one_second(self):
        s=d.Store(self.store.path)
        with patch.object(d.time,'time',return_value=100),patch.object(d.time,'sleep') as sleep:
            s.throttle('musicbrainz');s.throttle('musicbrainz');sleep.assert_called_once();self.assertGreaterEqual(sleep.call_args.args[0],1)
    def test_fetch_redacts_http_error(self):
        opener=Mock();opener.open.side_effect=urllib.error.HTTPError('https://example.org',403,'private body token',{},None)
        with patch.object(d.urllib.request,'build_opener',return_value=opener):
            with self.assertRaisesRegex(d.DiscoveryError,'^http_403$'):d.fetch_json('https://example.org')
    def test_bounded_response_and_json_content_type(self):
        for raw,ct,code in [(b'x'*(d.MAX_RESPONSE+1),'application/json','response_too_large'),(b'{}','text/html','non_json_response'),(b'bad','application/json','invalid_json'),(b'[]','application/json','invalid_response_shape')]:
            response=Mock();response.headers={'Content-Type':ct};response.read.return_value=raw
            opener=Mock();opener.open.return_value.__enter__=Mock(return_value=response);opener.open.return_value.__exit__=Mock(return_value=False)
            with patch.object(d.urllib.request,'build_opener',return_value=opener):
                with self.assertRaisesRegex(d.DiscoveryError,code):d.fetch_json('https://example.org')
    def test_redirects_not_followed(self):
        self.assertIsNone(d.NoRedirect().redirect_request(None,None,302,'',{},'http://127.0.0.1/private'))
    def test_record_storage_capacity_is_explicit(self):
        with self.store.db() as c:c.executemany('INSERT INTO records VALUES(?,?)',[(str(i),'{}') for i in range(5000)])
        with self.assertRaisesRegex(d.DiscoveryError,'record_capacity'):self.store.save(self.record())
    def test_cli_active_job_does_not_return_false_success(self):
        self.store.enqueue('recent-films');self.store.claim()
        with patch.object(sys,'argv',['discovery.py','run','--profile','recent-films','--db',str(self.store.path)]),patch('builtins.print'):
            self.assertEqual(d.main(),2)
    def test_cli_reused_blocked_job_does_not_return_false_success(self):
        self.store.enqueue('recent-films');d.process_one(self.store,fixture)
        with patch.object(sys,'argv',['discovery.py','run','--profile','recent-films','--db',str(self.store.path)]),patch('builtins.print'):
            self.assertEqual(d.main(),2)
    def test_no_remote_ai_by_default(self):
        f=Mock();self.assertIsNone(d.ai_note(self.record(),f));f.assert_not_called()

if __name__=='__main__':unittest.main()
