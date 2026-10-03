import json
from pathlib import Path
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import server

ROOT = Path(__file__).resolve().parent


class ContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'content.json').read_text())

    def test_chapters_are_proposed_not_recovered(self):
        chapters = self.data['chapter_mapping']
        self.assertEqual(chapters['status'], 'proposed_not_recovered_original_titles')
        self.assertEqual(len(chapters['liquor']), 12)
        self.assertEqual(len(chapters['bar']), 10)

    def test_canonical_ids_and_counts_unchanged(self):
        registry = json.loads((ROOT.parent / 'handover/AGENT_CONTENT_REGISTRY_V16_7_24.json').read_text())
        ids = {g['ids'] for g in registry['rosters']['ENTERTAINMENT']['groups']}
        for key in ('liquor_agent_id', 'bar_agent_id'):
            self.assertIn(self.data['ownership'][key], ids)
        self.assertEqual(self.data['ownership']['canonical_relationship'], 'siblings')
        self.assertFalse(self.data['ownership']['hierarchy_change'])
        self.assertEqual(sum(c['sub_agents'] for c in registry['categories']), 133)
        self.assertEqual(sum(c['products'] for c in registry['categories']), 421)

    def test_no_connected_provider_or_fabricated_specs(self):
        self.assertIsNone(self.data['ai']['provider'])
        self.assertFalse(self.data['ai']['execution_enabled'])
        for record in self.data['traditions']:
            self.assertIsNone(record['abv_percent'])
            self.assertIsNone(record['producer'])
            self.assertIsNone(record['local_legal_age'])

    def test_sources_resolve_and_candidates_stay_marked(self):
        ids = {s['id'] for s in self.data['sources']}
        for section in ('traditions', 'events', 'research_backlog'):
            for item in self.data[section]:
                self.assertTrue(set(item['source_ids']).issubset(ids))
                if item.get('research_status') == 'source_backed_overview':
                    self.assertTrue(item['source_ids'])
        self.assertEqual(self.data['traditions'][0]['research_status'], 'research_candidate')
        for s in self.data['sources']:
            self.assertTrue(s['url'].startswith('https://'))
            self.assertIn(s['url'], s['citation'])

    def test_events_separate_past_confirmed_and_unconfirmed(self):
        by_id = {e['id']: e for e in self.data['events']}
        self.assertEqual(by_id['spirit-goa']['date_status'], 'historical_edition_only')
        self.assertTrue(by_id['oktoberfest']['date_status'].startswith('organiser_published'))
        self.assertIsNone(by_id['local-calendar']['start'])
        self.assertIsNone(by_id['local-calendar']['end'])

    def test_snack_procedures_allergens_and_zero_alcohol_options(self):
        snacks = self.data['snacks']
        self.assertEqual(len({s['id'] for s in snacks}), 8)
        self.assertEqual(next(s for s in snacks if s['id'] == 'peanuts')['allergens'], ['peanut'])
        self.assertEqual(next(s for s in snacks if s['id'] == 'tofu')['allergens'], ['soy'])
        self.assertEqual(next(s for s in snacks if s['id'] == 'fish')['allergens'], ['fish'])
        for s in snacks:
            self.assertEqual(len(s['procedure']), 4)
            self.assertTrue(s['ingredients'])
            self.assertTrue(s['non_alcoholic_pairing'])
            self.assertIsNone(s['nutrient_values'])
            self.assertIn('cross-contact', s['allergen_note'])

    def test_extension_does_not_rewrite_historical_catalog(self):
        catalog = json.loads((ROOT.parent / 'experience/CONTENT_CATALOG.json').read_text())
        self.assertEqual(sum(len(p['files']) for p in catalog['packs']), 32)
        extensions = json.loads((ROOT.parent / 'experience/CONTENT_EXTENSIONS.json').read_text())
        self.assertFalse(extensions['extensions'][0]['registry_totals_changed'])


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_assets_served_with_same_origin_policy(self):
        for path in server.FILES:
            with urllib.request.urlopen(self.url + path) as response:
                self.assertEqual(response.status, 200)
                self.assertIn("connect-src 'self'", response.headers['Content-Security-Policy'])

    def test_private_and_non_allowlisted_files_rejected(self):
        for path in ['/../jarvis/jarvis.env', '/.git/config', '/ops/jarvis/devices.json',
                     '/README.md', '/%2e%2e/dr/dr.env', '/server.py']:
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(self.url + path)
            self.assertEqual(error.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
