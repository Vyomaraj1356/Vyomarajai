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


if __name__ == '__main__':
    unittest.main()
