import hashlib
import json
from pathlib import Path
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from unittest.mock import patch
import local_planner as planner
import studio_server as studio


class FilmContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(planner.PACKS['film'].read_text())

    def test_existing_slots_names_and_proposals(self):
        self.assertEqual([a['slot'] for a in self.data['agents']], [f'ENT-MOVIE-S{i}' for i in range(1, 7)])
        self.assertTrue(all(a['canonical_name'] == 'UNKNOWN' for a in self.data['agents']))
        self.assertTrue(all(a['assignment_status'] == 'proposed_functional_binding' for a in self.data['agents']))
        self.assertEqual(self.data['ownership']['additional_agents_created'], 0)

    def test_ids_sources_resolve(self):
        self.assertEqual(len(self.data['items']), 27)
        self.assertEqual(len({i['id'] for i in self.data['items']}), 27)
        sources = {s['id'] for s in self.data['sources']}
        for item in self.data['items']:
            self.assertTrue(set(item['source_ids']) <= sources)
            if item['era'] != 'proposal' and item['kind'] != 'clip':
                self.assertTrue(item['source_ids'])

    def test_conflicts_and_licences_preserved(self):
        d = {i['id']: i for i in self.data['items']}
        self.assertEqual(d['natsamrat-check']['kind'], 'version-check')
        self.assertIn('1993 and 1994', d['cadbury-old']['summary'])
        self.assertIn('2026', d['adhe']['summary'])
        self.assertIn('past', d['adhe']['summary'].lower())
        self.assertEqual(d['ekzunj']['production_minutes'], 150)
        self.assertIn('CC_BY_3.0', d['sintel']['rights'])
        self.assertIn('entire credits', d['sintel']['summary'])

    def test_all_content_index_current_and_reads_only_four_packs(self):
        import rebuild_contents
        original = Path.read_text
        seen = []
        def read(path, *args, **kw):
            self.assertIn(path, set(planner.PACKS.values()))
            seen.append(path)
            return original(path, *args, **kw)
        with patch.object(Path, 'read_text', read):
            content = rebuild_contents.build()
        self.assertEqual(len(seen), 4)
        self.assertEqual(content, (planner.CORE / 'handover/EXPERIENCE_CONTENTS_2026_10_03.md').read_text())

    def test_no_media_or_connected_provider_claims(self):
        self.assertFalse(any(self.data['scope'].values()))
        self.assertTrue(all(i['media_url'] is None for i in self.data['items']))
        self.assertEqual(len(self.data['formats']), 7)
        for seed in self.data['original_seeds'].values():
            self.assertEqual(set(seed['dialogue']), {'English', 'Marathi', 'Hindi'})

    def test_pinned_registry_catalog_unchanged(self):
        for path, digest in [('handover/AGENT_CONTENT_REGISTRY_V16_7_24.json','9e301bfcb1c6e8b23c1bea4fbdcf0d9d12d4c457fe62d7ef60e3161ac3a908a9'),('experience/CONTENT_CATALOG.json','86f2fc0a5b5c9adb606b5f72aa5047fa8ed0bf5bc6c7d9bcd9c82dbcf5b95f70')]:
            self.assertEqual(hashlib.sha256((planner.CORE / path).read_bytes()).hexdigest(), digest)


class FilmPlanTests(unittest.TestCase):
    def plan(self, **kw):
        return planner.build_plan({'experience': 'film', **kw})

    def test_all_formats_contiguous_budget(self):
        for format in ('feature', 'short', 'clip', 'long-play', 'one-act', 'advert', 'mix'):
            p = self.plan(format=format)
            elapsed = 0
            for beat in p['beats']:
                self.assertEqual(beat['start_seconds'], elapsed)
                elapsed += beat['budget_seconds']
            self.assertEqual(elapsed, p['duration_seconds'])
            self.assertFalse(p['media_rendered'])

    def test_marathi_hindi_theatre_routes(self):
        self.assertEqual(self.plan(format='one-act', language='Marathi')['canonical_agent_ids'], ['ENT-MOVIE-S4'])
        self.assertEqual(self.plan(format='long-play', language='Hindi')['canonical_agent_ids'], ['ENT-MOVIE-S5'])
        self.assertEqual(self.plan(format='advert')['canonical_agent_ids'], ['ENT-MOVIE-S6'])

    def test_reference_context_not_adaptation(self):
        a = self.plan(item_ids=['sairat', 'lalitaji'], seed='shelf')
        b = self.plan(seed='shelf')
        self.assertEqual(a['sample_dialogue'], b['sample_dialogue'])
        self.assertIn('not_adaptation', a['reference_usage'])
        self.assertIn('not_full_screenplay', a['script_status'])
        self.assertFalse(a['publishing_enabled'])
        self.assertIsNone(a['provider'])
        self.assertEqual(a['canonical_agent_ids'], ['ENT-MOVIE-S1', 'ENT-MOVIE-S2', 'ENT-MOVIE-S6'])

    def test_advert_review_and_no_external_claims(self):
        p = self.plan(format='advert', seed='repair', language='Hindi')
        self.assertIn('asci', [s['id'] for s in p['source_references']])
        for k in ('ai_calls_made', 'media_rendered', 'streaming_connected', 'publishing_enabled', 'legacy_device_config_loaded', 'production_deployed', 'dr_sync_verified'):
            self.assertFalse(p[k])

    def test_invalid_requests_rejected(self):
        for kw in ({'format': {}}, {'format': 'publish'}, {'language': []}, {'seed': '../file'},
                   {'item_ids': [{}]}, {'item_ids': ['sairat'] * 9}, {'item_ids': ['sairat', 'sairat']},
                   {'item_ids': ['binaca']}, {'duration_seconds': True}, {'duration_seconds': 30.5},
                   {'duration_seconds': 0}, {'format': 'advert', 'duration_seconds': 121},
                   {'format': 'feature', 'duration_seconds': 300}, {'files': 'secret'}, {'url': 'https://example.com'}):
            with self.subTest(kw=kw), self.assertRaises(planner.InvalidPlan):
                self.plan(**kw)

    def test_reads_only_selected_pack_and_active_registry_metadata(self):
        original = Path.read_text
        def read(path, *args, **kw):
            self.assertIn(path, {planner.PACKS['film'], planner.CORE / 'agents/AGENT_REGISTRY_CURRENT.json'})
            return original(path, *args, **kw)
        with patch.object(Path, 'read_text', read):
            self.plan()


class FilmServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), studio.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start(); cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def test_assets_and_reports(self):
        for route in ('/film/', '/film/app.js', '/film/styles.css', '/film/content.json', '/reports/film', '/reports/contents', '/assets/fonts.css', '/assets/devanagari.woff2'):
            with urllib.request.urlopen(self.url + route) as r:
                self.assertEqual(r.status, 200)
                self.assertIn('media-src blob:', r.headers['Content-Security-Policy'])

    def test_http_outline(self):
        req = urllib.request.Request(self.url + '/api/plan', data=b'{"experience":"film","format":"one-act","language":"Hindi"}', headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req) as r:
            p = json.load(r)
            self.assertEqual(p['sample_dialogue_language'], 'Hindi')
            self.assertEqual(p['canonical_agent_ids'], ['ENT-MOVIE-S5'])

    def test_no_upload_or_private_routes(self):
        for route in ('/api/upload', '/film/../../jarvis/jarvis.env', '/film/film_planner.py'):
            with self.subTest(route=route), self.assertRaises(urllib.error.HTTPError) as e:
                urllib.request.urlopen(self.url + route)
            self.assertEqual(e.exception.code, 404)

    def test_all_contents_includes_four_extensions(self):
        with urllib.request.urlopen(self.url + '/reports/contents') as r:
            body = r.read().decode()
            for title in ('Frame &amp; Stage', 'Memory &amp; Melody', 'Bhakti', 'Pairings'):
                self.assertIn(title, body)


if __name__ == '__main__':
    unittest.main()
