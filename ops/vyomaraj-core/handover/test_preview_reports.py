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

    def test_auto_align_platform_check_and_issue_ledger_pages(self):
        cases = (
            ('/reports/auto-align', 'AUTO-ALIGN EXECUTION PLAN'),
            ('/reports/platform-check', 'How it gets configured (auto-align plan)'),
            ('/reports/issues', 'New-session runbook (in order)'),
        )
        for route, marker in cases:
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.status, 200)
                    text = response.read().decode()
                self.assertIn(marker, text)

    def test_new_report_downloads_are_byte_identical(self):
        cases = (
            ('/reports/download/auto-align.json', 'AUTO_ALIGN_NEXT_SESSION.json', 'application/json'),
            ('/reports/download/platform-check.md', 'PLATFORM_CONFIGURATION_CHECK_2026_10_04.md', 'text/plain'),
            ('/reports/download/issues-ledger.json', 'ISSUES_AND_PRS_LEDGER.json', 'application/json'),
        )
        for route, name, mime in cases:
            with self.subTest(route=route):
                expected = (HERE / name).read_bytes()
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.read(), expected)
                    self.assertTrue(response.headers['Content-Type'].startswith(mime))
                    self.assertIn('attachment', response.headers['Content-Disposition'])

    def test_go_live_plan_and_live_wiring_pages_are_allowlisted(self):
        cases = (('/reports/go-live', 'Navaratri 2026 go-live plan', 'Ghatasthapana'),
                 ('/reports/live-wiring', 'Live wiring state', 'blocking_checks'))
        for route, marker, extra in cases:
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.status, 200)
                    text = response.read().decode()
                self.assertIn(marker, text)
                self.assertIn(extra, text)

    def test_stack_record_page_states_the_real_stack_and_the_money_rule(self):
        with urllib.request.urlopen(self.url + '/reports/stack') as response:
            text = response.read().decode()
        for marker in ('Stack and platform record', 'GitHub Pages', 'Python 3 standard library',
                       'UNSIGNED', 'zero-cost launch path', 'When Vyomaraj earns'):
            self.assertIn(marker, text)

    def test_go_live_plan_names_the_launch_date_and_the_open_decisions(self):
        with urllib.request.urlopen(self.url + '/reports/go-live') as response:
            text = response.read().decode()
        for marker in ('11 October 2026', 'Ghatasthapana', 'uidai.in', 'NOT real yet',
                       'Owner sign-off lines'):
            self.assertIn(marker, text)

    def test_post_pr25_companion_page_is_allowlisted_with_its_marker(self):
        with urllib.request.urlopen(self.url + '/reports/post-pr25-handover') as response:
            self.assertEqual(response.status, 200)
            text = response.read().decode()
        self.assertIn('POST-PR25 COMPANION UPDATE', text)
        self.assertIn('checkpoint #20', text)

    def test_post_pr25_downloads_are_byte_identical(self):
        cases = (('/reports/download/post-pr25-handover.txt', preview.POST_PR25_NOTE, 'text/plain'),
                 ('/reports/download/post-pr25-transfer.zip', preview.POST_PR25_ZIP, 'application/zip'))
        for route, name, mime in cases:
            with self.subTest(route=route):
                expected = (HERE / name).read_bytes()
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.read(), expected)
                    self.assertTrue(response.headers['Content-Type'].startswith(mime))
                    self.assertIn('attachment', response.headers['Content-Disposition'])

    def test_chats_notice_states_both_counts_and_owner_confirmation(self):
        with urllib.request.urlopen(self.url + '/reports/chats') as response:
            text = response.read().decode()
        for marker in ('heading says 28 chats', '34 numbered entries', 'owner confirmation'):
            self.assertIn(marker, text)

    def test_every_report_page_carries_the_three_new_nav_links(self):
        for route in ('/', '/reports/build', '/reports/chats', '/reports/issue-6',
                      '/reports/test-evidence', '/reports/handover-notepad', '/reports/auto-align',
                      '/reports/platform-check', '/reports/issues'):
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    text = response.read().decode()
                for link in ('href="/reports/chats"', 'href="/reports/issue-6"',
                             'href="/reports/test-evidence"', 'href="/reports/auto-align"',
                             'href="/reports/platform-check"', 'href="/reports/issues"',
                             'New-session runbook (in order)'):
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
