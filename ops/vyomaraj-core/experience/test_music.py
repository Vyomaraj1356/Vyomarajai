import hashlib
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import local_planner as planner
import studio_server as studio


class MusicContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(planner.PACKS['music'].read_text())

    def test_existing_slots_only_proposed_names(self):
        agents = self.data['agents']
        self.assertEqual([a['slot'] for a in agents], [f'ENT-MUS-S{i}' for i in range(1, 7)])
        for a in agents:
            self.assertEqual(a['canonical_name'], 'UNKNOWN')
            self.assertEqual(a['assignment_status'], 'proposed_functional_binding')
        self.assertEqual(self.data['ownership']['additional_agents_created'], 0)

    def test_sources_and_catalogue_ids(self):
        items = self.data['items']
        self.assertEqual(len(items), 63)
        self.assertEqual(len({i['id'] for i in items}), len(items))
        refs = {s['id'] for s in self.data['sources']}
        for i in items:
            self.assertTrue(set(i['source_ids']) <= refs)
            if i['licence_status'] == 'owned_original_not_yet_recorded':
                # An original programme may cite context, never material: it must state its own
                # rights basis and must not claim any performer or writer credit it does not have.
                self.assertTrue(i.get('rights_basis'))
                self.assertEqual(i['artists'], [])
            elif i['id'] not in ('audio', 'video'):
                self.assertTrue(i['source_ids'])
        self.assertTrue(all(s['url'].startswith('https://') for s in self.data['sources']))

    def test_no_bundled_or_live_media_claims(self):
        self.assertFalse(any(self.data['scope'].values()))
        for i in self.data['items']:
            self.assertIsNone(i['media_url'])
            self.assertIn(i['licence_status'],
                          ('not_licensed_for_rehosting', 'owned_original_not_yet_recorded'))
            self.assertIn(i['explicit_status'], ('not_reviewed', 'original_creator_owned'))

    def test_sufi_ghazal_and_show_formats_are_context_only(self):
        data = self.data
        extension = data['extension_2026_10_06']
        self.assertEqual(extension['new_items'], 24)
        self.assertEqual(extension['groups'],
                         {'sufi': 6, 'ghazal': 6, 'studio_and_show_formats': 8,
                          'original_programmes': 4})
        for key in ('heritage_items_are_context_only', 'original_programmes_have_own_rights_basis'):
            self.assertTrue(extension[key])
        for key in ('media_rehosted', 'episodes_imported', 'lyrics_imported', 'brand_assets_used',
                    'registry_totals_changed'):
            self.assertFalse(extension[key])
        self.assertEqual(extension['agents_created'], 0)
        items = {i['id']: i for i in data['items']}
        # The cards added by this extension are exactly the ones citing a source added with it.
        new_sources = {s['id'] for s in data['sources'] if s['checked'] == '2026-10-06'}
        self.assertEqual(len(new_sources), 17)
        added = [i for i in data['items'] if set(i['source_ids']) & new_sources]
        self.assertEqual(len(added), 24)
        for i in added:
            if i['licence_status'] != 'owned_original_not_yet_recorded':
                # Every inherited card must state the rule in its own words, not just in a policy file.
                self.assertIn('imported, copied or rehosted', i['summary'], i['id'])
        for original in ('original-mehfil-sessions', 'original-sufi-cycle', 'original-ghazal-cycle',
                         'original-navaratri-cycle'):
            self.assertEqual(items[original]['record_type'], 'original programme')
            self.assertEqual(items[original]['year'], 2026)
            self.assertNotIn('imported, copied or rehosted', items[original]['summary'])
        self.assertEqual(items['show-coke-studio-pk']['year'], 2008)
        self.assertEqual(extension['navaratri_window']['Ghatasthapana'], '2026-10-11')
        self.assertEqual(extension['navaratri_window']['Vijayadashami'], '2026-10-20')

    def test_dated_chart_not_current(self):
        c = self.data['chart_snapshot']
        self.assertEqual(c['period'], '2025')
        self.assertEqual(c['published'], '2026-02-19')
        self.assertEqual(c['status'], 'dated_annual_snapshot_not_live')
        self.assertEqual([e['rank'] for e in c['entries']], [1, 2, 3, 4, 5])
        self.assertEqual(c['entries'][0]['title'], 'APT.')

    def test_formats_and_eras_are_distinct(self):
        items = {i['id']: i for i in self.data['items']}
        self.assertEqual(items['aashiqui2']['record_type'], 'soundtrack')
        self.assertEqual(items['katchisera']['record_type'], 'single')
        self.assertEqual(items['katchi-video']['record_type'], 'music video')
        self.assertEqual(items['coldmess']['year'], 2020)
        self.assertIn('2018', items['coldmess']['summary'])
        self.assertIn('Arijit Singh', items['tumhiho']['artists'])

    def test_pinned_registry_and_historical_catalog(self):
        for path, digest in [
            ('handover/AGENT_CONTENT_REGISTRY_V16_7_24.json', '9e301bfcb1c6e8b23c1bea4fbdcf0d9d12d4c457fe62d7ef60e3161ac3a908a9'),
            ('experience/CONTENT_CATALOG.json', '86f2fc0a5b5c9adb606b5f72aa5047fa8ed0bf5bc6c7d9bcd9c82dbcf5b95f70')]:
            self.assertEqual(hashlib.sha256((planner.CORE / path).read_bytes()).hexdigest(), digest)


class MusicPlannerTests(unittest.TestCase):
    def plan(self, **kw):
        return planner.build_plan({'experience': 'music', 'item_ids': ['binaca', 'tumhiho', 'ifpi2025'], **kw})

    def test_rundown_exact_budget_and_contiguous_slots(self):
        for mode in ('radio', 'audio', 'video'):
            for duration in (15, 30, 60):
                p = self.plan(mode=mode, duration_minutes=duration)
                elapsed = 0
                for slot in p['rundown']:
                    self.assertEqual(slot['start_seconds'], elapsed)
                    elapsed += slot['budget_seconds']
                self.assertEqual(elapsed, duration * 60)
                self.assertEqual(p['duration_basis'], 'editorial_slot_budgets_not_recording_lengths')

    def test_routes_to_proposed_existing_bindings(self):
        p = self.plan(mode='video')
        self.assertEqual(p['canonical_agent_ids'], ['ENT-MUS-S1', 'ENT-MUS-S2', 'ENT-MUS-S4', 'ENT-MUS-S6'])
        self.assertEqual(p['assignment_status'], 'proposed_functional_bindings_not_recovered_names')
        self.assertEqual([r['role'] for r in p['role_handoff']], ['Vyomaraj', 'Jarvis'])
        self.assertEqual(p['rundown'][2]['catalogue_credits'], ['Mithoon', 'Arijit Singh'])

    def test_no_model_stream_publish_or_device_claims(self):
        p = self.plan()
        for k in ('ai_calls_made', 'streaming_connected', 'live_charts_connected', 'publishing_enabled',
                  'production_deployed', 'dr_sync_verified', 'legacy_device_config_loaded'):
            self.assertFalse(p[k])
        self.assertIsNone(p['provider'])

    def test_order_and_sources_preserved(self):
        p = self.plan(item_ids=['marathi', 'radical', 'binaca'])
        self.assertEqual([r['item_id'] for r in p['rundown'] if 'item_id' in r], ['marathi', 'radical', 'binaca'])
        self.assertEqual({s['id'] for s in p['source_references']}, {'marathi', 'dua', 'geetmala'})
        self.assertIsNone(p['chart_snapshot'])

    def test_only_reviewed_pack_read_and_active_registry_metadata(self):
        original = Path.read_text
        def read(path, *args, **kwargs):
            self.assertIn(path, {planner.PACKS['music'], planner.CORE / 'agents/AGENT_REGISTRY_CURRENT.json'})
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            self.plan()

    def test_invalid_ids_types_and_budget_rejected(self):
        for kw in ({'item_ids': []}, {'item_ids': ['unknown']}, {'item_ids': ['binaca', 'binaca']},
                   {'item_ids': [{}]}, {'item_ids': 'binaca'}, {'item_ids': ['binaca'] * 9},
                   {'mode': 'autopublish'}, {'mode': {}}, {'duration_minutes': '30'},
                   {'duration_minutes': True}, {'duration_minutes': 31},
                   {'upload': '/ops/jarvis/devices.json'}, {'recipe_id': 'fruit'}):
            with self.subTest(kw=kw), self.assertRaises(planner.InvalidPlan):
                self.plan(**kw)


class MusicServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), studio.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def test_music_assets_and_report(self):
        for route in ('/music/', '/music/app.js', '/music/styles.css', '/music/content.json', '/reports/music'):
            with urllib.request.urlopen(self.url + route) as r:
                self.assertEqual(r.status, 200)
                self.assertIn('media-src blob:', r.headers['Content-Security-Policy'])

    def test_http_music_handoff(self):
        body = json.dumps({'experience': 'music', 'item_ids': ['katchi-video'], 'mode': 'video'}).encode()
        req = urllib.request.Request(self.url + '/api/plan', data=body, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as r:
            p = json.load(r)
            self.assertEqual(p['canonical_agent_ids'], ['ENT-MUS-S6'])
            self.assertFalse(p['streaming_connected'])

    def test_no_upload_or_private_file_routes(self):
        for route in ('/music/../content.json', '/music/server.py', '/api/upload', '/ops/jarvis/devices.json'):
            with self.subTest(route=route), self.assertRaises(urllib.error.HTTPError) as e:
                urllib.request.urlopen(self.url + route)
            self.assertEqual(e.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
