import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch
import studio_server as studio
import local_planner as planner

class CurrentRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),studio.Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def get(self,path):
        with urllib.request.urlopen(self.base+path) as r:return r.read()
    def test_directory_and_education_routes(self):
        for route in ['/agents/','/education/','/agents/app.js','/agents/styles.css']:
            self.assertGreater(len(self.get(route)),100)
    def test_active_json_routes(self):
        d=json.loads(self.get('/agents/AGENT_REGISTRY_CURRENT.json'));self.assertEqual(d['totals']['sub_agents'],168)
        i=json.loads(self.get('/agents/CONTENT_INDEX_CURRENT.json'));self.assertEqual(i['education_topic_count'],21)
        o=json.loads(self.get('/agents/CONTENT_OWNERSHIP_CURRENT.json'));self.assertTrue(all(t['owner_category']=='EDU' for t in o['education_topics']))
    def test_reports_current_vs_historical(self):
        self.assertIn(b'15 categories',self.get('/reports/'))
        self.assertIn(b'Government Schemes',self.get('/reports/agents'))
        self.assertIn(b'133',self.get('/reports/history'))
    def test_rules_builder_and_private_paths_not_served(self):
        for route in ['/agents/rebuild_registry.py','/agents/RECONCILIATION_RULES.json','/agents/../../.git/config','/education/../jarvis.env']:
            with self.assertRaises(urllib.error.HTTPError) as e:self.get(route)
            self.assertEqual(e.exception.code,404)
    def test_planner_refuses_uncounted_heading_as_agent(self):
        with patch.object(planner,'_build_plan',return_value={'category_id':'ENTERTAINMENT','canonical_agent_ids':['ENT-HUB-MUS']}):
            with self.assertRaisesRegex(planner.InvalidPlan,'Agent mapping'):planner.build_plan({})
    def test_planner_refuses_unknown_category(self):
        with patch.object(planner,'_build_plan',return_value={'category_id':'UNKNOWN-CATEGORY','canonical_agent_ids':[]}):
            with self.assertRaisesRegex(planner.InvalidPlan,'Category'):planner.build_plan({})
