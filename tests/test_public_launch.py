import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class PublicLaunchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text(encoding='utf-8')
        cls.manifest = json.loads((ROOT / 'manifest.webmanifest').read_text(encoding='utf-8'))
        cls.worker = (ROOT / 'sw.js').read_text(encoding='utf-8')

    def test_public_page_states_target_date_without_claiming_launch_complete(self):
        self.assertIn('11 October 2026', self.html)
        self.assertIn('release target', self.html)
        self.assertIn('not a claim that every planned service or app is already live', self.html)
        self.assertIn('NOT LIVE', self.html)
        self.assertIn('NOT RELEASED', self.html)
        self.assertIn('NOT VERIFIED', self.html)

    def test_public_page_does_not_repeat_retired_sandbox_or_release_claims(self):
        forbidden = (
            'e2b.app', '24.8 MB signed APK', 'All Social Platforms Activated',
            'Heartbeats LIVE', 'Native SwiftUI macOS app', 'Vite + React + Framer Motion',
        )
        for claim in forbidden:
            with self.subTest(claim=claim):
                self.assertNotIn(claim.casefold(), self.html.casefold())
        self.assertIn('v2 signing-block entry', self.html.casefold())
        self.assertIn('cryptographic validity and signer provenance are unverified', self.html.casefold())
        self.assertIn('installation has not been tested on a real device', self.html.casefold())
        self.assertIn('not offered as a release', self.html.casefold())

    def test_local_page_links_resolve_and_are_scoped(self):
        hrefs = re.findall(r'href="([^"]+)"', self.html)
        for href in hrefs:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or href.startswith('#'):
                continue
            path = parsed.path
            if not path or path == './':
                continue
            with self.subTest(href=href):
                self.assertTrue((ROOT / path.removeprefix('./')).is_file(), f'missing local target: {href}')

    def test_manifest_is_project_path_relative_and_has_real_icons(self):
        self.assertEqual(self.manifest['start_url'], './')
        self.assertEqual(self.manifest['scope'], './')
        self.assertEqual(self.manifest['display'], 'standalone')
        for icon in self.manifest['icons']:
            if icon['type'] == 'image/png':
                path = ROOT / icon['src'].removeprefix('./')
                self.assertTrue(path.is_file())
                data = path.read_bytes()
                self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')

    def test_service_worker_caches_only_public_shell_and_never_mutates(self):
        self.assertIn("'vyomaraj-public-shell-v1'", self.worker)
        self.assertIn("request.method !== 'GET'", self.worker)
        for private_or_mutating in ('/api/approvals', '/api/finance', '/api/research', '/api/upgrades'):
            self.assertNotIn(private_or_mutating, self.worker)
        self.assertIn("'./offline.html'", self.worker)

    def test_legacy_landing_routes_to_current_page_and_warns(self):
        legacy = (ROOT / 'landing.html').read_text(encoding='utf-8')
        self.assertIn('http-equiv="refresh" content="0; url=./"', legacy)
        self.assertIn('not verified or release-ready', legacy)

    def test_old_market_readiness_file_is_marked_historical(self):
        readme = (ROOT / 'README_MARKET_READY.md').read_text(encoding='utf-8')
        self.assertTrue(readme.startswith('> **Historical draft — not a release-status source.**'))


if __name__ == '__main__':
    unittest.main()
