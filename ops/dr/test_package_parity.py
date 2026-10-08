"""Offline tests for the primary/secondary package-parity verifier.

No network, no credentials, no repository writes.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import package_parity as pp  # noqa: E402
from dr_sync import CheckError  # noqa: E402


class NormalizationTests(unittest.TestCase):
    def test_pep503_normalization(self):
        self.assertEqual(pp.normalize('PyYAML'), 'pyyaml')
        self.assertEqual(pp.normalize('a2a_sdk'), 'a2a-sdk')
        self.assertEqual(pp.normalize('opentelemetry.api'), 'opentelemetry-api')

    def test_version_ordering_is_numeric_not_lexical(self):
        self.assertLess(pp.version_key('1.9.0'), pp.version_key('1.10.0'))
        self.assertLess(pp.version_key('4.26.0'), pp.version_key('5'))
        self.assertGreater(pp.version_key('46.0.0'), pp.version_key('42'))


class SpecifierTests(unittest.TestCase):
    def test_bounds(self):
        self.assertTrue(pp.satisfies('46.0.0', '>=', '42'))
        self.assertTrue(pp.satisfies('46.0.0', '<', '47'))
        self.assertFalse(pp.satisfies('47.0.1', '<', '47'))
        self.assertFalse(pp.satisfies('41.9', '>=', '42'))

    def test_equality_tolerates_padding(self):
        self.assertTrue(pp.satisfies('6.0.3', '==', '6.0.3'))
        self.assertFalse(pp.satisfies('6.0.3', '==', '6.0.4'))

    def test_unknown_operator_is_refused(self):
        with self.assertRaises(CheckError):
            pp.satisfies('1.0', '<=>', '1.0')


class ParseRequirementsTests(unittest.TestCase):
    def test_extras_comments_and_bounds(self):
        parsed = pp.parse_requirements(
            '# comment\n'
            'mcp[cli]>=2,<3\n'
            '\n'
            'PyYAML>=6.0,<7  # inline\n'
        )
        requirements = parsed['requirements']
        self.assertEqual(sorted(requirements), ['mcp', 'pyyaml'])
        self.assertEqual(requirements['mcp']['extras'], ['cli'])
        self.assertEqual(requirements['mcp']['specifiers'], [('>=', '2'), ('<', '3')])
        self.assertEqual(parsed['unsupported_lines'], [])

    def test_unsupported_constructs_are_recorded_not_guessed(self):
        parsed = pp.parse_requirements(
            '-r other.txt\n'
            'thing @ https://example.invalid/thing.whl\n'
            'marked; python_version < "3.11"\n'
        )
        self.assertEqual(parsed['requirements'], {})
        self.assertEqual(len(parsed['unsupported_lines']), 3)

    def test_duplicate_declaration_is_flagged(self):
        parsed = pp.parse_requirements('pytest>=8\npytest>=7\n')
        self.assertTrue(parsed['requirements']['pytest']['duplicate'])


class ClassificationTests(unittest.TestCase):
    def test_dependency_manifests_are_recognised(self):
        for path in ('ops/engineering/requirements-2026.txt',
                     'ops/shriyantra/requirements.txt',
                     'constraints.txt', 'package.json', 'poetry.lock', 'go.sum'):
            self.assertEqual(pp.classify(path), 'dependency_manifest', path)

    def test_distributables_are_recognised(self):
        for path in ('Vyomaraj-App.apk', 'a/b/Vyomaraj-V9.0.zip', 'x.tar.gz'):
            self.assertEqual(pp.classify(path), 'distributable_package', path)

    def test_ordinary_sources_are_not_packages(self):
        for path in ('README.md', 'ops/dr/dr_sync.py', 'index.html', 'requirements.md'):
            self.assertIsNone(pp.classify(path), path)


class CompareTests(unittest.TestCase):
    def test_identical_maps_match(self):
        left = {'requirements.txt': 'a' * 40, 'app.apk': 'b' * 40}
        result = pp.compare_maps(left, dict(left))
        self.assertEqual(result['status'], 'MATCH')
        self.assertEqual(result['identical_package_files'], 2)
        self.assertEqual(result['missing_on_secondary'], [])

    def test_differing_content_is_a_mismatch_not_a_match(self):
        result = pp.compare_maps({'requirements.txt': 'a' * 40},
                                 {'requirements.txt': 'c' * 40})
        self.assertEqual(result['status'], 'MISMATCH')
        self.assertEqual(result['content_differs'], ['requirements.txt'])

    def test_missing_and_secondary_only_are_reported_separately(self):
        result = pp.compare_maps({'one.zip': 'a' * 40}, {'two.zip': 'b' * 40})
        self.assertEqual(result['status'], 'MISMATCH')
        self.assertEqual(result['missing_on_secondary'], ['one.zip'])
        self.assertEqual(result['secondary_only'], ['two.zip'])


class DeclarationTests(unittest.TestCase):
    def test_repository_declarations_are_consistent(self):
        result = pp.validate_declarations()
        self.assertEqual(result['status'], 'PASS', result['findings'])
        self.assertIn('cryptography', result['locked_distributions'])
        self.assertFalse(result['installed_environment_verified'])

    def test_every_locked_pin_satisfies_its_declared_bounds(self):
        result = pp.validate_declarations()
        canonical = pp.parse_requirements(
            (pp.ROOT / pp.CANONICAL_REQUIREMENTS).read_text(encoding='utf-8'))['requirements']
        for name, version in result['locked_distributions'].items():
            for operator, bound in canonical[name]['specifiers']:
                self.assertTrue(pp.satisfies(version, operator, bound),
                                f'{name}=={version} violates {operator}{bound}')


class InventoryTests(unittest.TestCase):
    def test_committed_inventory_matches_the_working_tree(self):
        self.assertEqual(pp.main(['--check']), 0)

    def test_inventory_records_both_package_kinds(self):
        report = pp.local_report()
        kinds = report['package_files_by_kind']
        self.assertGreaterEqual(kinds.get('dependency_manifest', 0), 1)
        self.assertGreaterEqual(kinds.get('distributable_package', 0), 1)
        self.assertFalse(report['runtime_package_parity_verified'])

    def test_every_inventory_record_carries_a_comparable_hash(self):
        for record in pp.local_report()['inventory']:
            self.assertRegex(record['git_blob_sha'], r'^[0-9a-f]{40}$')
            self.assertRegex(record['sha256'], r'^[0-9a-f]{64}$')

    def test_evidence_file_is_valid_json_without_timestamps(self):
        data = json.loads(pp.EVIDENCE.read_text(encoding='utf-8'))
        self.assertNotIn('checked_at_utc', data)
        self.assertNotIn('secondary_comparison', data)
        self.assertNotIn('index_availability', data)


class SafetyTests(unittest.TestCase):
    def test_remote_comparison_requires_a_confirmed_target(self):
        for target in ('', 'not-a-repo', 'https://github.com/a/b', pp.PRIMARY):
            with self.subTest(target=target), self.assertRaises(CheckError):
                pp.validate_target(target)

    def test_truncated_tree_is_refused(self):
        class Client:
            def request(self, method, path):
                return {'truncated': True, 'tree': []}
        with self.assertRaises(CheckError):
            pp.remote_package_map(Client(), 'owner/repo', 'f' * 40)


if __name__ == '__main__':
    unittest.main()
