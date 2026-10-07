import json
from pathlib import Path
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import local_planner as planner
import studio_server as studio


class ContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(planner.PACKS['bhakti'].read_text())

    def test_proposed_chapter_scope(self):
        self.assertEqual(len(self.data['stories']), 12)
        self.assertTrue(all(s['chapter_status'] == 'proposed_editorial_mapping' for s in self.data['stories']))
        self.assertFalse(self.data['scope']['complete_peetha_list_verified'])
        self.assertIsNone(self.data['ownership']['canonical_subagent_slot'])

    def test_peetha_counts_and_variant_traditions(self):
        peethas = self.data['peethas']
        self.assertEqual(len(peethas), 9)
        self.assertEqual(len({p['id'] for p in peethas}), 9)
        self.assertTrue(any('52' in p['list_tradition'] for p in peethas))
        self.assertTrue(any('51' in p['list_tradition'] for p in peethas))
        self.assertTrue(any('Ardha' in p['list_tradition'] for p in peethas))
        for p in peethas:
            self.assertIsNone(p['body_part'])
            self.assertIsNone(p['bhairava'])
            self.assertIsNone(p['live_timings'])

    def test_sources_and_ids_resolve(self):
        source_ids = {s['id'] for s in self.data['sources']}
        all_ids = []
        for section in ('stories', 'avatars', 'peethas'):
            for item in self.data[section]:
                all_ids.append(item['id'])
                self.assertTrue(item['source_ids'])
                self.assertTrue(set(item['source_ids']).issubset(source_ids))
        self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_avatar_variant_and_tv_rights_explicit(self):
        self.assertEqual(len(self.data['avatars']), 10)
        self.assertIn('Balarama', self.data['avatars'][8]['note'])
        self.assertFalse(self.data['television']['copied_footage'])
        self.assertFalse(self.data['television']['actor_voice_cloning'])
        self.assertIsNone(self.data['television']['episode_count'])

    def test_food_allergens_and_procedures(self):
        self.assertEqual(len(self.data['recipes']), 3)
        self.assertEqual(self.data['recipes'][2]['allergens'], ['milk'])
        for recipe in self.data['recipes']:
            self.assertEqual(len(recipe['procedure']), 4)
            self.assertIsNone(recipe['nutrition_values'])

    def test_historical_totals_unchanged(self):
        registry = json.loads((planner.CORE / 'handover/AGENT_CONTENT_REGISTRY_V16_7_24.json').read_text())
        self.assertEqual(sum(c['sub_agents'] for c in registry['categories']), 133)
        self.assertEqual(sum(c['products'] for c in registry['categories']), 421)
        catalog = json.loads((planner.CORE / 'experience/CONTENT_CATALOG.json').read_text())
        self.assertEqual(sum(len(p['files']) for p in catalog['packs']), 32)


class PlannerTests(unittest.TestCase):
    def test_local_handoff_does_not_claim_ai_or_production(self):
        plan = planner.build_plan({'experience': 'bhakti', 'topic_id': 'sati-daksha', 'recipe_id': 'fruit', 'mode': '5d'})
        self.assertEqual(plan['status'], 'local_plan_created')
        self.assertEqual(plan['category_id'], 'BHAKTI')
        self.assertEqual(plan['canonical_agent_ids'], [])
        self.assertEqual([r['role'] for r in plan['role_handoff']], ['Vyomaraj', 'Jarvis'])
        for key in ('ai_calls_made', 'publishing_enabled', 'production_deployed', 'dr_sync_verified', 'legacy_device_config_loaded'):
            self.assertFalse(plan[key])
        self.assertIsNone(plan['provider'])

    def test_reads_only_selected_reviewed_pack_and_active_registry_metadata(self):
        original = Path.read_text
        seen = []
        def read(path, *args, **kwargs):
            self.assertIn(path, {planner.PACKS['bhakti'], planner.CORE / 'agents/AGENT_REGISTRY_CURRENT.json'})
            seen.append(path)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            planner.build_plan({'experience': 'bhakti'})
        self.assertEqual(set(seen), {planner.PACKS['bhakti'], planner.CORE / 'agents/AGENT_REGISTRY_CURRENT.json'})
        self.assertEqual(len(seen), 2)

    def test_pairing_pack_routes_to_existing_ids(self):
        plan = planner.build_plan({'experience': 'liquor-bar', 'recipe_id': 'chana'})
        self.assertEqual(plan['canonical_agent_ids'], ['ENT-LIQUOR-S1', 'ENT-BAR-S1'])
        self.assertEqual(plan['category_id'], 'ENTERTAINMENT')

    def test_cross_pack_topic_or_recipe_rejected(self):
        for body in ({'experience': 'bhakti', 'topic_id': 'kallu'},
                     {'experience': 'bhakti', 'recipe_id': 'chana'}):
            with self.subTest(body=body), self.assertRaises(planner.InvalidPlan):
                planner.build_plan(body)

    def test_dietary_conflicts_rejected(self):
        for body in ({'experience': 'bhakti', 'recipe_id': 'yogurt', 'diet': 'plant-based'},
                     {'experience': 'bhakti', 'recipe_id': 'yogurt', 'exclude_allergens': ['milk']}):
            with self.subTest(body=body), self.assertRaises(planner.InvalidPlan):
                planner.build_plan(body)

    def test_untrusted_fields_and_types_rejected(self):
        for body in ([], None, {'experience': '../../jarvis'}, {'experience': ['bhakti']},
                     {'experience': 'bhakti', 'command': 'publish'},
                     {'experience': 'bhakti', 'exclude_allergens': [None]},
                     {'experience': 'bhakti', 'mode': 'autonomous'},
                     {'experience': 'bhakti', 'topic_id': {}},
                     {'experience': 'bhakti', 'diet': ['all']}):
            with self.subTest(body=body), self.assertRaises(planner.InvalidPlan):
                planner.build_plan(body)

    def test_no_source_topic_requires_research(self):
        plan = planner.build_plan({'experience': 'liquor-bar', 'topic_id': 'tadi-local'})
        self.assertEqual(plan['source_references'], [])
        self.assertTrue(any('no cited source' in item for item in plan['review_gates']))


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), studio.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, body, content_type='application/json'):
        return urllib.request.urlopen(urllib.request.Request(self.url + '/api/plan', data=body,
                                    headers={'Content-Type': content_type}))

    def test_preview_assets_and_status(self):
        for route in ('/', '/bhakti/', '/pairings/', '/assets/pairings.css', '/api/status', '/reports/'):
            with urllib.request.urlopen(self.url + route) as response:
                self.assertEqual(response.status, 200)
        with urllib.request.urlopen(self.url + '/api/status') as response:
            self.assertEqual(json.load(response)['status'], 'local_preview_planning_only')

    def test_lane_serves_the_three_new_report_pages_with_shared_theme(self):
        for route, marker in (('/reports/chats', 'All Chats from Arena Database'),
                              ('/reports/issue-6', 'Issue #6 resolution statement'),
                              ('/reports/test-evidence', 'python_tests_total'),
                              ('/reports/auto-align', 'AUTO-ALIGN EXECUTION PLAN'),
                              ('/reports/platform-check', 'How it gets configured (auto-align plan)'),
                              ('/reports/issues', 'New-session runbook (in order)')):
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.status, 200)
                    text = response.read().decode()
                self.assertIn(marker, text)
                # The lane pages inherit the same single theme constant as the viewer.
                self.assertIn('#0a1628', text)
                self.assertIn('#f59e0b', text)
                self.assertIn('href="/reports/chats"', text)
                self.assertIn('href="/reports/issue-6"', text)
                self.assertIn('href="/reports/test-evidence"', text)
                self.assertIn('href="/reports/auto-align"', text)
                self.assertIn('href="/reports/platform-check"', text)
                self.assertIn('href="/reports/issues"', text)

    def test_lane_local_monitor_route_is_read_only_and_navigable(self):
        with patch.object(studio.reports, 'render_monitor_fragment',
                          return_value='<h1>Local service monitor</h1><p>snapshot only</p>') as render:
            with urllib.request.urlopen(self.url + '/reports/monitor') as response:
                self.assertEqual(response.status, 200)
                self.assertIn('no-store', response.headers.get('Cache-Control', ''))
                page = response.read().decode()
        render.assert_called_once_with()
        self.assertIn('Local monitor, read-only view', page)
        self.assertIn('snapshot only', page)
        self.assertIn('href="/reports/monitor">Local monitor</a>', page)

    def test_lane_downloads_new_plan_ledger_and_platform_report(self):
        cases = (
            ('/reports/download/auto-align.json', studio.CORE / 'handover/AUTO_ALIGN_NEXT_SESSION.json'),
            ('/reports/download/platform-check.md', studio.CORE / 'handover/PLATFORM_CONFIGURATION_CHECK_2026_10_04.md'),
            ('/reports/download/issues-ledger.json', studio.CORE / 'handover/ISSUES_AND_PRS_LEDGER.json'),
        )
        for route, path in cases:
            with self.subTest(route=route), urllib.request.urlopen(self.url + route) as response:
                self.assertEqual(response.read(), path.read_bytes())
                self.assertIn('attachment', response.headers['Content-Disposition'])

    def test_end_to_end_handoff(self):
        with self.post(json.dumps({'experience': 'bhakti', 'topic_id': 'kamakhya'}).encode()) as response:
            data = json.load(response)
            self.assertEqual(data['topic']['id'], 'kamakhya')
            self.assertFalse(data['ai_calls_made'])

    def test_unsupported_json_and_oversize(self):
        for body, mime, expected in ((b'{', 'application/json', 400),
                                     (b'{}', 'text/plain', 415),
                                     (b' ' * 16385, 'application/json', 413),
                                     (b'{"experience":"other"}', 'application/json', 400),
                                     (b'[' * 2000 + b']' * 2000, 'application/json', 400)):
            with self.subTest(expected=expected), self.assertRaises(urllib.error.HTTPError) as error:
                self.post(body, mime)
            self.assertEqual(error.exception.code, expected)

    def test_private_routes_blocked(self):
        for route in ('/.git/config', '/ops/jarvis/jarvis.env', '/bhakti/../server.py',
                      '/%2e%2e/README.md', '/api/secrets', '/LOCAL_INTEGRATION.json'):
            with self.subTest(route=route), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(self.url + route)
            self.assertEqual(error.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
