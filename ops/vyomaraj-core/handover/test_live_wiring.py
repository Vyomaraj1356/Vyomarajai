"""Offline checks for the live-wiring verifier.

These run without any server: they lock the contract between the verifier, the report viewer's
route allowlist and the checked-in artifacts, and they prove that a dead route is reported as a
problem rather than passing as if the wiring worked.
"""
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import preview_reports as viewer
import verify_live_wiring as wiring


class RouteContractTests(unittest.TestCase):
    def test_every_advertised_route_is_actually_served(self):
        served = set(viewer.REPORTS) | set(viewer.REFERENCE_REPORTS) | set(viewer.DYNAMIC_REPORTS)
        for route in wiring.VIEWER_ROUTES:
            self.assertIn(route, served, f'{route} is checked by the verifier but not served')

    def test_every_download_is_served_and_has_a_source(self):
        for route, source in wiring.DOWNLOADS.items():
            self.assertIn(route, viewer.DOWNLOADS, f'{route} is not in the viewer download allowlist')
            self.assertTrue((wiring.ROOT / source).is_file(), f'{source} is missing')

    def test_every_captured_page_is_served_by_the_screenshot_branch(self):
        # Screenshots travel through the /reports/screenshot/<name> prefix branch, which allowlists
        # names by shape. The contract: the viewer must publish that prefix and the name must match
        # the published pattern, and the file must exist.
        self.assertIn('/reports/screenshot/', (wiring.ROOT / 'ops/vyomaraj-core/handover/'
                                               'preview_reports.py').read_text(encoding='utf-8'))
        for route, source in wiring.SCREENSHOT_ROUTES.items():
            with self.subTest(route=route):
                name = route.rsplit('/', 1)[-1]
                self.assertTrue(viewer.SCREENSHOT_NAME.fullmatch(name), f'{name} is not allowlisted')
                self.assertTrue((wiring.ROOT / source).is_file(), f'{source} is missing')

    def test_replica_routes_are_served_by_the_lanes(self):
        # The replicas serve their own route table and also consult the shared renderer's
        # allowlists, so a route counts as served if either place knows it.
        studio = (wiring.CORE / 'experience/studio_server.py').read_text(encoding='utf-8')
        known = (set(viewer.REPORTS) | set(viewer.REFERENCE_REPORTS) |
                 set(viewer.DYNAMIC_REPORTS) | set(viewer.DOWNLOADS))
        for route in wiring.REPLICA_ROUTES:
            with self.subTest(route=route):
                self.assertTrue(route in studio or route in known,
                                f'{route} is neither routed by studio_server.py nor allowlisted '
                                f'by the shared renderer')

    def test_stack_record_and_enrollment_artifacts_are_registered(self):
        for path in ('ops/vyomaraj-core/handover/STACK_AND_PLATFORM_RECORD_2026_10_06.md',
                     'ops/vyomaraj-core/handover/LINK_AND_ARCHIVE_LEDGER_2026_10_06.json',
                     'ops/vyomaraj-core/experience/voice_enrollment.py',
                     'ops/vyomaraj-core/governance/VOICE_ENROLLMENT_POLICY.json'):
            with self.subTest(path=path):
                self.assertTrue((wiring.ROOT / path).is_file())
                self.assertIn(path, wiring.REQUIRED_FILES)

    def test_required_artifacts_exist(self):
        missing = [path for path in wiring.REQUIRED_FILES if not (wiring.ROOT / path).is_file()]
        self.assertEqual(missing, [], f'required launch artifacts are missing: {missing}')


class FailureReportingTests(unittest.TestCase):
    def test_dead_route_is_a_problem_not_a_pass(self):
        problems = []
        with patch.object(wiring, 'fetch', return_value={'status': 503, 'bytes': 0, 'sha256': None,
                                                         'seconds': 0.0, 'body': b'', 'content_type': None}):
            wiring.check_routes('http://127.0.0.1:1', ['/'], 'viewer', problems)
        self.assertEqual(len(problems), 1)
        self.assertIn('returned 503', problems[0])

    def test_wrong_bytes_are_a_problem_not_a_pass(self):
        problems = []
        with patch.object(wiring, 'fetch', return_value={'status': 200, 'bytes': 3, 'sha256': None,
                                                         'seconds': 0.0, 'body': b'nope',
                                                         'content_type': 'text/plain'}):
            wiring.check_downloads('http://127.0.0.1:1', 'viewer', problems)
        # the byte check covers the download allowlist plus the captured-page branch
        self.assertEqual(len(problems), len(wiring.DOWNLOADS) + len(wiring.SCREENSHOT_ROUTES))
        for problem in problems:
            self.assertIn('not byte-identical', problem)

    def test_missing_content_marker_is_a_problem(self):
        problems = []
        with patch.object(wiring, 'fetch', return_value={'status': 200, 'bytes': 3, 'sha256': None,
                                                         'seconds': 0.0, 'body': b'abc',
                                                         'content_type': 'text/html'}):
            wiring.check_routes('http://127.0.0.1:1', [('/reports/dr-sync', None, 'BLOCKED')],
                                'viewer', problems)
        self.assertEqual(len(problems), 1)
        self.assertIn('content marker', problems[0])


class ApkSigningBlockTests(unittest.TestCase):
    @staticmethod
    def make_apk_region(pair_ids):
        import struct
        pairs = b''.join(struct.pack('<Q', 4) + struct.pack('<I', pair_id)
                         for pair_id in pair_ids)
        size = len(pairs) + 24  # pair data + repeated size + 16-byte magic
        block = struct.pack('<Q', size) + pairs + struct.pack('<Q', size) + wiring.APK_SIGNING_MAGIC
        prefix = b'zip-local-file-data'
        data = prefix + block + b'central-directory'
        return data, len(prefix) + len(block)

    def test_v2_signature_pair_is_detected_without_claiming_verification(self):
        data, offset = self.make_apk_region([0x7109871A, 0x42726577])
        result = wiring.parse_apk_signing_block(data, offset)
        self.assertTrue(result['present'])
        self.assertTrue(result['structure_valid'])
        self.assertEqual(result['signature_schemes'], ['v2'])
        self.assertIn('0x42726577', result['pair_ids'])

    def test_malformed_pair_is_not_treated_as_a_valid_signature_block(self):
        import struct
        data, offset = self.make_apk_region([0x7109871A])
        mutable = bytearray(data)
        block_start = offset - struct.unpack_from('<Q', data, offset - 24)[0] - 8
        struct.pack_into('<Q', mutable, block_start + 8, 0xFFFFFFFF)
        result = wiring.parse_apk_signing_block(mutable, offset)
        self.assertTrue(result['present'])
        self.assertFalse(result['structure_valid'])
        self.assertEqual(result['error'], 'invalid_pair_length')
        self.assertEqual(result['signature_schemes'], [])

    def test_missing_signing_block_is_reported_as_absent(self):
        data = b'ordinary zip data with no signing footer'
        result = wiring.parse_apk_signing_block(data, len(data))
        self.assertFalse(result['present'])
        self.assertFalse(result['structure_valid'])


class TruthfulnessTests(unittest.TestCase):
    def test_enrollment_is_reported_absent_until_code_exists(self):
        state = wiring.check_enrollment()
        if state['enrollment_capture_implementation'] == 'ABSENT':
            self.assertEqual(state['implementation_files'], [])
        else:
            self.assertTrue(state['implementation_files'], 'REVIEW must name the files it found')
        self.assertIn('uidai.in', state['identity_documents_route']['rule'])

    def test_databases_are_declared_outside_git_snapshot_replication(self):
        state = wiring.check_databases()
        self.assertFalse(state['git_snapshot_dr_covers_runtime_databases'])
        self.assertTrue(state['backup_required_before_launch'])

    def test_apk_v2_material_is_not_misreported_as_unsigned_or_verified(self):
        state = wiring.check_apk([])
        if not state['present']:
            self.fail('Vyomaraj-App.apk is missing from the repository')
        self.assertTrue(state['apk_signing_block']['present'])
        self.assertTrue(state['apk_signing_block']['structure_valid'])
        self.assertIn('v2', state['apk_signing_block']['signature_schemes'])
        self.assertTrue(state['signature_material_present'])
        self.assertFalse(state['signature_cryptographically_verified'])
        self.assertIn('INSTALLATION UNVERIFIED', state['install_claim'])
        self.assertFalse(state['rebuildable_from_this_repository'])
        self.assertEqual(state['bytes'], len((wiring.ROOT / state['path']).read_bytes()))

    def test_state_file_records_the_route_table_it_checked(self):
        state_path = wiring.OUTPUT
        if not state_path.is_file():
            self.skipTest('verifier has not been run in this checkout yet')
        recorded = json.loads(state_path.read_text(encoding='utf-8'))
        # This JSON is the timestamped 06:11 route snapshot, so newly added 7 October routes must
        # not be backfilled into its historical result. Verify its original routes remain allowlisted
        # and ordered; current additions are independently covered by RouteContractTests above.
        for key in ('viewer_routes', 'gateway_routes'):
            recorded_routes = [row['route'] for row in recorded[key]]
            self.assertTrue(recorded_routes)
            self.assertEqual(recorded_routes,
                             [route for route in wiring.VIEWER_ROUTES if route in set(recorded_routes)])
        self.assertIn('/reports/integration-audit', wiring.VIEWER_ROUTES)
        self.assertIn('/reports/peer-architecture', wiring.VIEWER_ROUTES)
        self.assertIn('limitations', recorded)
        self.assertTrue(recorded['advisory'])


if __name__ == '__main__':
    unittest.main()
