from pathlib import Path
import json
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from contextlib import redirect_stdout
from io import StringIO
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import preview_reports as preview
import build_full_handover as full_handover
import build_ai_handoff as ai_handoff

HERE = Path(preview.__file__).resolve().parent


class InternalLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for attribute in ('href', 'src'):
            if values.get(attribute):
                self.links.append(values[attribute])


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

    def test_handover_notepad_page_and_download_show_the_current_update(self):
        update = (HERE / preview.SESSION_UPDATE).read_bytes()
        with urllib.request.urlopen(self.url + '/reports/handover-notepad') as response:
            page = response.read().decode()
        self.assertIn('DR replication completed', page)
        self.assertIn('href="/reports/next-session"', page)
        self.assertIn('href="/reports/download/handover-notepad.txt"', page)
        with urllib.request.urlopen(self.url + '/reports/download/handover-notepad.txt') as response:
            self.assertEqual(response.read(), update)
            self.assertIn('attachment', response.headers['Content-Disposition'])
            self.assertIn(preview.SESSION_UPDATE, response.headers['Content-Disposition'])

    def test_monitor_route_is_allowlisted_read_only_and_navigable(self):
        self.assertIn('/reports/monitor', preview.DYNAMIC_REPORTS)
        with patch.object(preview, 'render_monitor_fragment',
                          return_value='<h1>Local service monitor</h1><p>snapshot only</p>') as render:
            with urllib.request.urlopen(self.url + '/reports/monitor') as response:
                self.assertEqual(response.status, 200)
                page = response.read().decode()
        render.assert_called_once_with()
        self.assertIn('Local monitor, read-only view', page)
        self.assertIn('snapshot only', page)
        self.assertIn('href="/reports/monitor">Local monitor</a>', page)
        self.assertIn('href="/reports/handover-notepad"', page)

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

    def test_current_handoff_archive_counts_include_the_readme_member(self):
        cases = (
            (full_handover.ZIP, full_handover.MEMBERS, 'HANDOVER_README.txt', full_handover.check),
            (ai_handoff.ZIP, ai_handoff.MEMBERS, 'HOW_TO_USE_THIS_PACKAGE.txt', ai_handoff.check),
        )
        for archive_path, members, readme, check in cases:
            with self.subTest(archive=archive_path.name), zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
                expected = {readme} | {rel for rel in members if (full_handover.ROOT / rel).is_file()}
                self.assertEqual(set(names), expected)
                self.assertEqual(len(names), len(expected), 'zip entries must not be duplicated')
                self.assertIsNone(archive.testzip())
                output = StringIO()
                with redirect_stdout(output):
                    self.assertEqual(check(), 0)
                self.assertIn(f'{len(names)} members', output.getvalue())

    def test_current_handoffs_carry_shared_knowledge_policy_and_context(self):
        policy_ref = 'config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json'
        architecture_doc = 'docs/architecture/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE.md'
        resolver = 'ops/shriyantra/knowledge_evolution.py'
        for archive_path in (full_handover.ZIP, ai_handoff.ZIP):
            with self.subTest(archive=archive_path.name), zipfile.ZipFile(archive_path) as archive:
                for member in (policy_ref, architecture_doc, resolver):
                    self.assertIn(member, archive.namelist())
                    self.assertEqual(archive.read(member), (full_handover.ROOT / member).read_bytes())
        pack = json.loads(ai_handoff.PACK.read_text(encoding='utf-8'))
        shared = pack['agents']['shared_knowledge_inheritance']
        self.assertEqual(shared['policy_id'], 'UNIVERSAL_KNOWLEDGE_EVOLUTION_V1')
        self.assertEqual(shared['current_coverage']['agent_count'], 128)
        self.assertIn('Universal Knowledge Evolution inheritance', ai_handoff.DOC.read_text(encoding='utf-8'))
        self.assertIn('Universal Knowledge Evolution inheritance', full_handover.DOC.read_text(encoding='utf-8'))

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

    def test_issue_six_page_warns_historical_resolution_is_not_current(self):
        with urllib.request.urlopen(self.url + '/reports/issue-6') as response:
            text = response.read().decode()
        self.assertIn('OPEN/P0', text)
        self.assertIn('Do not post this historical text or close the issue', text)
        self.assertIn('SUPERSEDED', text)

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
                 ('/reports/live-wiring', 'Timestamped preview result, not current production status', 'blocking_checks'))
        for route, marker, extra in cases:
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.status, 200)
                    text = response.read().decode()
                self.assertIn(marker, text)
                self.assertIn(extra, text)
                if route == '/reports/live-wiring':
                    self.assertIn('Timestamped preview result, not current production status', text)
                    self.assertIn('A follow-up port/process probe at 08:15 UTC', text)
                    self.assertIn('no listener on 3000, 4174, 4176, 4181 or 4182', text)

    def test_stack_record_page_states_the_real_stack_and_the_money_rule(self):
        with urllib.request.urlopen(self.url + '/reports/stack') as response:
            text = response.read().decode()
        for marker in ('Stack and platform record', 'GitHub Pages', 'Python 3 standard library',
                       'apksigner verify', 'signer provenance', 'zero-cost launch path', 'When Vyomaraj earns'):
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
                      '/reports/test-evidence', '/reports/handover-notepad', '/reports/monitor', '/reports/auto-align',
                      '/reports/platform-check', '/reports/issues'):
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    text = response.read().decode()
                for link in ('href="/reports/chats"', 'href="/reports/issue-6"',
                             'href="/reports/test-evidence"', 'href="/reports/auto-align"',
                             'href="/reports/platform-check"', 'href="/reports/issues"',
                             'href="/reports/monitor">Local monitor</a>',
                             'New-session runbook (in order)'):
                    self.assertIn(link, text)

    def test_every_internal_viewer_link_resolves_from_every_report_page(self):
        page_routes = (set(preview.REPORTS) | set(preview.REFERENCE_REPORTS)
                       | set(preview.DYNAMIC_REPORTS) | {'/reports/realtime'})
        local_netloc = urlsplit(self.url).netloc
        linked = {}
        for page_route in sorted(page_routes):
            with self.subTest(page=page_route), urllib.request.urlopen(self.url + page_route) as response:
                self.assertEqual(response.status, 200)
                if not response.headers.get('Content-Type', '').startswith('text/html'):
                    continue
                parser = InternalLinkParser()
                parser.feed(response.read().decode())
            for raw_url in parser.links:
                target = urlsplit(urljoin(self.url + page_route, raw_url))
                if target.netloc == local_netloc and target.path:
                    linked.setdefault(target.path, page_route)

        for target_path, source_page in sorted(linked.items()):
            with self.subTest(source=source_page, target=target_path):
                try:
                    with urllib.request.urlopen(self.url + target_path, timeout=5) as response:
                        self.assertEqual(response.status, 200)
                        response.read()  # Drain downloads so the test server does not log a broken pipe.
                except Exception as exc:
                    self.fail(f'{source_page} links to broken viewer route {target_path}: {exc}')

    def test_current_integration_and_peer_reports_are_allowlisted_and_downloadable(self):
        for route, marker in (('/reports/integration-audit', 'Integration alignment and release audit'),
                              ('/reports/peer-architecture', 'Shared peer architecture and heartbeat plan')):
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.status, 200)
                    page = response.read().decode()
                self.assertIn(marker, page)
                self.assertIn('href="/reports/integration-audit"', page)
                self.assertIn('href="/reports/peer-architecture"', page)
                evidence = json.loads((HERE / 'TEST_EVIDENCE_2026_10_04.json').read_text())
                gate_summary = (f"{evidence['python_tests_total']} Python tests across "
                                f"{len(evidence['python_suites'])} suites, {len(evidence['node_checks'])} Node checks "
                                f"and {len(evidence['builders'])} builders; {len(evidence.get('failures', []))} failures")
                self.assertIn(gate_summary, page)
        for route, path in (('/reports/download/integration-audit.md', HERE / preview.INTEGRATION_AUDIT),
                            ('/reports/download/peer-architecture.md', HERE / preview.PEER_ARCHITECTURE)):
            with self.subTest(download=route), urllib.request.urlopen(self.url + route) as response:
                self.assertEqual(response.read(), path.read_bytes())
                self.assertIn('attachment', response.headers['Content-Disposition'])
        for route, path in (('/reports/download/full-handover-current.zip', HERE / preview.CURRENT_FULL_ZIP),
                            ('/reports/download/ai-handoff-current.zip', HERE / preview.CURRENT_AI_ZIP)):
            with self.subTest(download=route), urllib.request.urlopen(self.url + route) as response:
                self.assertEqual(response.read(), path.read_bytes())
                self.assertEqual(response.headers['Content-Type'], 'application/zip')
        self.assertTrue((HERE / 'transfer/VYOMARAJ_FULL_HANDOVER_2026_10_06.zip').is_file())
        self.assertTrue((HERE / 'transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip').is_file())

    def test_realtime_view_separates_current_ports_from_timestamped_dr_and_heartbeat(self):
        with urllib.request.urlopen(self.url + '/reports/realtime') as response:
            page = response.read().decode()
        for marker in ('Latest scheduled DR checkpoint', '986288ee2cc4',
                       'Effective target identity', 'authenticated heartbeat:', 'production peer/DR verified:'):
            self.assertIn(marker, page)
        with urllib.request.urlopen(self.url + '/api/realtime') as response:
            import json
            state = json.loads(response.read())
        ports = {entry['port']: entry['listening'] for entry in state['services']}
        self.assertIn(5310, ports)
        self.assertTrue(state['sync']['latest_scheduled_checkpoint']['data_match'])
        self.assertIn('UNCONFIRMED', state['sync']['effective_target_identity'])
        self.assertFalse(state['local_peer_monitor']['heartbeat_authenticated'])

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

    def test_next_session_plan_and_session_update_pages(self):
        for route, marker in (('/reports/next-session-plan', 'NEXT-SESSION PLAN'),
                              ('/reports/session-update', 'SESSION UPDATE')):
            with self.subTest(route=route):
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.status, 200)
                    text = response.read().decode()
                self.assertIn(marker, text)
                self.assertIn('href="/reports/next-session-plan"', text)
                self.assertIn('href="/reports/session-update"', text)

    def test_plan_and_update_downloads_are_byte_identical(self):
        cases = (
            ('/reports/download/next-session-plan.md', 'NEXT_SESSION_PLAN_2026_10_07.md'),
            ('/reports/download/next-session-plan.txt', 'NEXT_SESSION_PLAN_2026_10_07.md'),
            ('/reports/download/session-update.md', 'SESSION_UPDATE_2026_10_06.md'),
            ('/reports/download/session-update.txt', 'SESSION_UPDATE_2026_10_06.md'),
        )
        for route, name in cases:
            with self.subTest(route=route):
                expected = (HERE / name).read_bytes()
                with urllib.request.urlopen(self.url + route) as response:
                    self.assertEqual(response.read(), expected)
                    self.assertTrue(response.headers['Content-Type'].startswith('text/plain'))
                    self.assertIn('attachment', response.headers['Content-Disposition'])
                    self.assertIn(name, response.headers['Content-Disposition'])

    def test_reference_pages_never_serve_unallowlisted_paths(self):
        for path in ('/reports/chats/../../README.md', '/reports/chats/../.git/config',
                     '/reports/chats/extra', '/reports/issue-6/../dr.env'):
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(self.url + path)
            self.assertEqual(error.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
