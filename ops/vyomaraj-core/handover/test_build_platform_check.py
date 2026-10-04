"""Coverage tests for the generated platform-configuration report."""
import unittest

import build_platform_check as platform


class PlatformCheckTests(unittest.TestCase):
    def setUp(self):
        self.items = platform.load(platform.ITEMS)
        self.plan = platform.load(platform.PLAN)
        self.text = platform.render()

    def test_all_open_items_have_exactly_one_completion_step(self):
        paths, problems = platform.coverage(self.items, self.plan)
        self.assertEqual(problems, [])
        self.assertEqual(len(self.items['items']), 41)
        self.assertEqual(set(paths), {item['id'] for item in self.items['items']})
        self.assertTrue(all(len(value) == 1 for value in paths.values()))

    def test_every_report_row_shows_the_step_id(self):
        paths, _ = platform.coverage(self.items, self.plan)
        for item_id, step_ids in paths.items():
            with self.subTest(item=item_id):
                self.assertIn(f'`{item_id}`', self.text)
                self.assertIn(f'`{step_ids[0]}`', self.text)

    def test_configured_path_is_not_misreported_as_readiness(self):
        for phrase in ('not proof of installation', 'not substitutes for independent production DR',
                       'status changes to DONE'):
            self.assertIn(phrase, self.text)

    def test_section_title_is_the_expected_viewer_marker(self):
        self.assertIn('How it gets configured (auto-align plan)', self.text)

    def test_no_money_or_earnings_claims(self):
        self.assertIn('No prices, plan limits or earnings projections', self.text)
        for marker in ('₹', '$', 'USD', 'INR'):
            self.assertNotIn(marker, self.text)

    def test_checked_in_report_matches_generated_report(self):
        self.assertEqual(platform.OUTPUT.read_text(encoding='utf-8'), self.text)


if __name__ == '__main__':
    unittest.main()
