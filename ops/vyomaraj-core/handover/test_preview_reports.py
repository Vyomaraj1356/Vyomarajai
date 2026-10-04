from pathlib import Path
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import preview_reports as preview

HERE = Path(preview.__file__).resolve().parent


class PreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), preview.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_readable_inventory_table(self):
        with urllib.request.urlopen(self.url + '/') as response:
            text = response.read().decode()
            self.assertIn('<table>', text)
            self.assertIn('<td>FOOD</td>', text)
            self.assertIn('X-Content-Type-Options', response.headers)

    def test_markdown_download(self):
        with urllib.request.urlopen(self.url + '/download/inventory.md') as response:
            self.assertIn('attachment', response.headers['Content-Disposition'])
            self.assertIn(b'# Vyomaraj / Jarvis', response.read())

    def test_private_files_and_traversal_not_served(self):
        for path in ['/ops/jarvis/jarvis.env', '/ops/jarvis/devices.json', '/.git/config',
                     '/../README.md', '/%2e%2e/README.md', '/dr.env', '/unknown']:
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(self.url + path)
            self.assertEqual(error.exception.code, 404)

    def test_next_session_note_download_is_byte_identical(self):
        note = (HERE / preview.HANDOVER_NOTE).read_bytes()
        with urllib.request.urlopen(self.url + '/reports/next-session') as response:
            self.assertIn('<pre>', response.read().decode())
        with urllib.request.urlopen(self.url + '/reports/download/next-session.txt') as response:
            self.assertEqual(response.read(), note)
            disposition = response.headers['Content-Disposition']
            self.assertIn('attachment', disposition)
            self.assertIn(preview.HANDOVER_NOTE, disposition)

    def test_build_configuration_report_route(self):
        with urllib.request.urlopen(self.url + '/reports/build') as response:
            text = response.read().decode()
        for expected in ('Vyomaraj — build, configuration and inventory', '<table>', 'Agents — current',
                         'Jarvis configuration'):
            self.assertIn(expected, text)

    def test_recovery_page_links_handover_and_package(self):
        with urllib.request.urlopen(self.url + '/reports/recovery') as response:
            text = response.read().decode()
        for fragment in ('href="/reports/next-session"', 'href="/reports/download/next-session.txt"',
                         'href="/reports/download/transfer-package.zip"'):
            self.assertIn(fragment, text)

    def test_handover_notepad_page_and_download_alias_the_note(self):
        note = (HERE / preview.HANDOVER_NOTE).read_bytes()
        with urllib.request.urlopen(self.url + '/reports/handover-notepad') as response:
            page = response.read().decode()
        self.assertIn('<pre>', page)
        self.assertIn('href="/reports/handover-notepad"', page)
        self.assertIn('href="/reports/dr-sync"', page)
        with urllib.request.urlopen(self.url + '/reports/download/handover-notepad.txt') as response:
            self.assertEqual(response.read(), note)
            self.assertIn('attachment', response.headers['Content-Disposition'])

    def test_dr_sync_report_page_is_generated_from_evidence(self):
        with urllib.request.urlopen(self.url + '/reports/dr-sync') as response:
            text = response.read().decode()
        self.assertIn('DR sync results', text)
        self.assertIn('<table>', text)
        self.assertIn('Replication writes', text)
        self.assertIn('BLOCKED', text)
        self.assertIn('production disaster-recovery approval', text)

    def test_transfer_package_download_is_the_packaged_artifact(self):
        artifact = (HERE / preview.TRANSFER_ZIP).read_bytes()
        with urllib.request.urlopen(self.url + '/reports/download/transfer-package.zip') as response:
            self.assertEqual(response.read(), artifact)
            self.assertEqual(response.headers['Content-Type'], 'application/zip')

    def test_html_injection_escaped(self):
        rendered = preview.markdown('# <script>alert(1)</script>\n| X |\n|---|\n| <img src=x> |')
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('<img ', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_three_new_allowlisted_pages(self):
        for route, marker in (('/reports/chats', 'All Chats from Arena Database'),
                              ('/reports/issue-6', 'Issue #6 resolution statement'),
                              ('/reports/test-evidence', 'python_tests_total')):
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.status, 200)
                    text = response.read().decode()
                self.assertIn(marker, text)

    def test_every_report_page_carries_the_three_new_nav_links(self):
        for route in ('/', '/reports/build', '/reports/chats', '/reports/issue-6',
                      '/reports/test-evidence', '/reports/handover-notepad'):
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    text = response.read().decode()
                for link in ('href="/reports/chats"', 'href="/reports/issue-6"',
                             'href="/reports/test-evidence"'):
                    self.assertIn(link, text)

    def test_theme_is_inherited_by_every_page(self):
        # One shared constant carries the Vyomaraj palette (Shani Blue + Kuber Gold); every page
        # of the viewer must inherit it rather than style itself.
        self.assertIn('#0a1628', preview.STYLE)
        self.assertIn('#f59e0b', preview.STYLE)
        for route in ('/', '/reports/chats', '/reports/issue-6', '/reports/test-evidence',
                      '/reports/handover-notepad', '/reports/build'):
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    text = response.read().decode()
                self.assertIn('#0a1628', text)
                self.assertIn('#f59e0b', text)
                self.assertIn('<meta name="theme-color" content="#0a1628">', text)

    def test_reference_pages_never_serve_unallowlisted_paths(self):
        for path in ('/reports/chats/../../README.md', '/reports/chats/../.git/config',
                     '/reports/chats/extra', '/reports/issue-6/../dr.env'):
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(self.url + path)
            self.assertEqual(error.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
