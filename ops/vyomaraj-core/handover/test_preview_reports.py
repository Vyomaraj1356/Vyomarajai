import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import preview_reports as preview


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

    def test_html_injection_escaped(self):
        rendered = preview.markdown('# <script>alert(1)</script>\n| X |\n|---|\n| <img src=x> |')
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('<img ', rendered)
        self.assertIn('&lt;script&gt;', rendered)


if __name__ == '__main__':
    unittest.main()
