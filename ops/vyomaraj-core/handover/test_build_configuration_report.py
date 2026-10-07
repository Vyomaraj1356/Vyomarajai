"""The build/configuration report must match its generator and the registry it cites."""
import json
import unittest

import build_configuration_report as report


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(report.REGISTRY.read_text())

    def test_checked_in_report_exists_and_generator_reflects_current_registry(self):
        self.assertTrue(report.OUTPUT.is_file())
        text = report.render()
        self.assertIn(f"Main agents: **{self.registry['totals']['main_agents']}**", text)
        self.assertIn(f"counted sub-agent slots: **{self.registry['totals']['sub_agents']}**", text)

    def test_totals_match_the_registry(self):
        text = report.render()
        totals = self.registry['totals']
        for expected in (f"Main agents: **{totals['main_agents']}**",
                         f"counted sub-agent slots: **{totals['sub_agents']}**",
                         f"named: **{totals['named_sub_agents']}**",
                         f"serial-only (name UNKNOWN): **{totals['unnamed_numbered_sub_agents']}**"):
            self.assertIn(expected, text)

    def test_named_agents_are_listed(self):
        text = report.render()
        named = [a for a in self.registry['agents'] if a.get('name')]
        self.assertEqual(len(named), 152)
        for agent in named:
            self.assertIn(agent['name'], text)

    def test_no_secret_values_are_printed(self):
        text = report.render()
        for line in report.JARVIS_ENV.read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                value = line.split('=', 1)[1].strip()
                if value and len(value) > 3:
                    self.assertNotIn(value, text, f'Jarvis env value leaked for {line.split("=")[0]}')

    def test_report_uses_repository_relative_paths(self):
        # A checkout-path leak makes the report unmatchable on any other machine (for example CI),
        # which is exactly how the first generation of this file failed.
        text = report.render()
        self.assertNotIn(report.ROOT.as_posix(), text)
        self.assertNotIn('/home/', text)
        self.assertNotIn('runner/work', text)

    def test_change_summary_is_present(self):
        text = report.render()
        for expected in ('ENTERTAINMENT 38 → 32', 'FINANCE 8 → 7 and EDU 15 → 16', 'BHAKTI 2 → 3',
                         'runtime_status'):
            self.assertIn(expected, text)


if __name__ == '__main__':
    unittest.main()
