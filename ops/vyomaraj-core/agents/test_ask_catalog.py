"""Tests for the ask-the-catalog retrieval slice.

The point of the slice is that it answers from the two checked-in files and cites
them, and that it returns nothing when the catalog has no answer. These tests hold
both halves: real hits for the known probes, and an empty result for nonsense.
"""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import ask_catalog
import ask_server

HERE = Path(__file__).resolve().parent


def resolve(citation):
    """Open a citation of the form '<file>#/agents/<id>' in the source file itself."""
    file_name, _, pointer = citation.partition('#')
    data = json.loads((HERE / file_name).read_text(encoding='utf-8'))
    node = data
    for step in pointer.strip('/').split('/'):
        if not step:
            continue
        if isinstance(node, list):
            node = next(item for item in node if str(item.get('id')) == step)
        else:
            node = node[step]
    return node


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = ask_catalog.Catalog()

    def test_stats_count_the_checked_in_files(self):
        stats = self.catalog.stats()
        self.assertEqual(stats['positions'], 128)
        self.assertEqual(stats['content_references'], 197)
        self.assertEqual(stats['categories'], 13)
        self.assertEqual(stats['headings_uncounted'], 6)
        self.assertEqual(stats['named_positions'] + stats['unnamed_positions'], 128)
        self.assertEqual(stats['generation'], 'none — retrieval only, no model call')

    def test_gita_returns_the_topic_and_the_position(self):
        ids = [r['id'] for r in self.catalog.ask('gita')['results']]
        self.assertIn('EDU-TOPIC-gita', ids)
        self.assertIn('EDU-S3', ids)
        gita_acharya = next(r for r in self.catalog.ask('gita')['results'] if r['id'] == 'EDU-S3')
        self.assertEqual(gita_acharya['display'], 'Gita Acharya')

    def test_government_schemes_answers(self):
        result = self.catalog.ask('government schemes')
        ids = [r['id'] for r in result['results']]
        self.assertIn('EDU-GOV-S1', ids)
        self.assertIn('EDU-TOPIC-government-schemes', ids)
        self.assertEqual(result['results'][0]['id'], 'EDU-GOV-S1')
        self.assertEqual(result['aliases_applied'], {})

    def test_music_returns_positions_heading_and_references(self):
        result = self.catalog.ask('music')
        ids = [r['id'] for r in result['results']]
        self.assertIn('ENT-HUB-MUS', ids)
        self.assertTrue(any(i.startswith('ENT-MUS-') for i in ids))
        self.assertTrue(any(r['kind'] == 'content_reference' for r in result['results']))
        self.assertGreater(result['matches'], 0)

    def test_film_alias_reaches_the_movie_records(self):
        result = self.catalog.ask('film')
        ids = [r['id'] for r in result['results']]
        self.assertIn('ENT-HUB-MOVIE', ids)
        self.assertIn('movie', result['aliases_applied']['film'])

    def test_shayari_and_cartoon_headings_are_findable(self):
        for query, expected in (('shayari', 'ENT-HUB-SHAYARI'), ('cartoon', 'ENT-HUB-CARTOON')):
            ids = [r['id'] for r in self.catalog.ask(query)['results']]
            self.assertIn(expected, ids, query)

    def test_nonsense_returns_nothing_and_says_so(self):
        for query in ('xyzzy quux flibbertigibbet', 'zzzzzz', 'quantum blockchain unicorn'):
            result = self.catalog.ask(query)
            self.assertEqual(result['results'], [], query)
            self.assertEqual(result['matches'], 0, query)
            self.assertIn('nothing is invented', result['note'], query)

    def test_one_unknown_word_rejects_the_whole_query(self):
        # AND semantics: a real word plus a nonsense word is not a free pass to guess.
        self.assertEqual(self.catalog.ask('gita zzzz')['results'], [])

    def test_empty_query_is_empty_not_a_catalogue_dump(self):
        result = self.catalog.ask('   ')
        self.assertEqual(result['results'], [])
        self.assertEqual(result['note'], 'empty query — nothing to look up')

    def test_every_result_cites_a_record_that_exists(self):
        for query in ('gita', 'music', 'government schemes', 'film', 'aghor', 'youtube', 'cartoon'):
            for result in self.catalog.ask(query)['results']:
                record = resolve(result['citation'])
                if result['kind'] == 'content_reference':
                    self.assertEqual(record['title'], result['title'])
                    self.assertEqual(record['id'], result['id'])
                else:
                    self.assertEqual(record['id'], result['id'])

    def test_unnamed_positions_are_never_given_a_name(self):
        registry = json.loads((HERE / 'AGENT_REGISTRY_CURRENT.json').read_text(encoding='utf-8'))
        names = {a['id']: a['name'] for a in registry['agents']}
        unnamed_found = 0
        for query in ('music', 'movie', 'comedy', 'education', 'slots'):
            for result in self.catalog.ask(query)['results']:
                if result['kind'] != 'position' or result['named']:
                    continue
                unnamed_found += 1
                self.assertIsNone(result['title'])
                self.assertIsNone(names[result['id']])
                self.assertTrue(result['display'].startswith('UNNAMED SLOT ' + result['id']))
        self.assertGreater(unnamed_found, 0, 'expected at least one unnamed slot in the probes')

    def test_matching_is_case_and_punctuation_insensitive_and_deterministic(self):
        first = self.catalog.ask('Gītā!')
        second = self.catalog.ask('  gita ')
        self.assertEqual([r['id'] for r in first['results']], [r['id'] for r in second['results']])
        self.assertEqual(first['results'][0]['id'], 'EDU-TOPIC-gita')
        self.assertEqual(self.catalog.ask('music'), self.catalog.ask('music'))

    def test_limit_is_respected(self):
        result = self.catalog.ask('music', limit=3)
        self.assertEqual(result['returned'], 3)
        self.assertLessEqual(len(result['results']), 3)
        self.assertGreater(result['matches'], 3)
        self.assertIn('showing the top 3', result['note'])

    def test_response_carries_no_generated_answer_field(self):
        payload = self.catalog.ask('gita')
        self.assertNotIn('answer', payload)
        self.assertNotIn('summary', payload)
        for result in payload['results']:
            self.assertIn('#/', result['citation'])


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), ask_server.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_address[1]}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        try:
            with urlopen(self.base + path, timeout=5) as response:
                return response.status, json.loads(response.read().decode('utf-8'))
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode('utf-8'))

    def test_health_and_stats(self):
        status, health = self.get('/health')
        self.assertEqual((status, health['status']), (200, 'ok'))
        status, stats = self.get('/api/stats')
        self.assertEqual((status, stats['positions'], stats['content_references']), (200, 128, 197))

    def test_api_answers_and_refuses(self):
        status, hit = self.get('/api/ask?q=government%20schemes')
        self.assertEqual(status, 200)
        self.assertTrue(any(r['id'] == 'EDU-GOV-S1' for r in hit['results']))
        status, miss = self.get('/api/ask?q=xyzzy%20quux')
        self.assertEqual(status, 200)
        self.assertEqual(miss['results'], [])

    def test_unknown_path_is_404(self):
        status, body = self.get('/api/nope')
        self.assertEqual(status, 404)
        self.assertIn('paths', body)

    def test_index_page_is_served(self):
        with urlopen(self.base + '/', timeout=5) as response:
            page = response.read().decode('utf-8')
        self.assertIn('Ask the catalog', page)
        self.assertIn('/api/ask?q=', page)


if __name__ == '__main__':
    unittest.main()
