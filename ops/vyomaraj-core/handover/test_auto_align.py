"""Regression tests for the bounded auto-align execution plan."""
import json
import unittest

import auto_align as align


class AutoAlignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = align.load(align.PLAN_PATH)
        cls.items = align.load(align.ITEMS_PATH)
        cls.text = align.render(cls.plan, cls.items)

    def test_expected_plan_shape(self):
        self.assertEqual(len(self.plan['steps']), 21)
        self.assertEqual(len(self.plan['phases']), 5)
        self.assertEqual(len(self.plan['local_sequence']), 14)

    def test_eighteen_owner_steps_and_one_agent_action_remain_pending(self):
        statuses = [step['status'] for step in self.plan['steps']]
        self.assertEqual(statuses.count('OWNER_ACTION_REQUIRED'), 18)
        self.assertEqual(statuses.count('AWAITING_AGENT'), 1)
        self.assertEqual(statuses.count('READY_AUTOMATIC'), 2)

    def test_all_forty_one_open_items_have_one_path(self):
        _, _, problems = align.validate(self.plan, self.items)
        self.assertEqual(problems, [])
        covered = [item for step in self.plan['steps'] for item in step['covers']]
        ids = [item['id'] for item in self.items['items']]
        self.assertEqual(set(covered), set(ids))
        self.assertEqual(len(covered), len(ids))

    def test_every_step_has_verification_and_done_condition(self):
        for step in self.plan['steps']:
            with self.subTest(step=step['id']):
                self.assertTrue(step['verify'].strip())
                self.assertTrue(step['done_when'].strip())
                self.assertTrue(step['evidence_path'].strip())

    def test_local_commands_are_argv_only_and_contain_no_external_actions(self):
        for step in self.plan['local_sequence']:
            if step['kind'] == 'command':
                self.assertIsInstance(step['argv'], list)
                self.assertIsNone(align.FORBIDDEN_COMMAND.search(' '.join(step['argv'])))
                self.assertNotIn('--run', step['argv'])

    def test_self_check_exception_is_narrow_and_explicit(self):
        entry = next(step for step in self.plan['local_sequence'] if step['id'] == 'l03-align-self-check')
        self.assertTrue(entry['allow_runner_check'])
        self.assertEqual(entry['argv'], ['python3', 'ops/vyomaraj-core/handover/auto_align.py', '--check'])
        for step in self.plan['local_sequence']:
            if step['id'] != entry['id']:
                self.assertFalse(step.get('allow_runner_check', False))

    def test_preview_checks_are_local_and_explicitly_skippable(self):
        previews = [step for step in self.plan['local_sequence'] if step['kind'] == 'preview']
        self.assertEqual([step['port'] for step in previews], [4174, 4176])
        self.assertTrue(all(step['skip_if_unavailable'] for step in previews))
        self.assertTrue(all(route.startswith('/') for step in previews for route in step['routes']))

    def test_plan_text_explains_owner_actions_and_evidence_gate(self):
        for fragment in ('Phase 0 — automatic readiness and publication', 'Phase 1 — Owner decisions',
                         'Phase 2 — Provider connections', 'Phase 3 — Studio and services',
                         'Phase 4 — Disaster recovery and operations', 'moves to DONE only'):
            self.assertIn(fragment, self.text)

    def test_no_claimed_setup_or_automatic_external_action(self):
        self.assertIn('not a claim that an account, provider, service or control is configured', self.text)
        for phrase in ('install packages', 'purchase services', 'connect provider accounts',
                       'publish content', 'push or merge code'):
            self.assertIn(phrase, self.text)

    def test_rendered_page_matches_checked_in_file(self):
        self.assertEqual(align.REPORT_PATH.read_text(encoding='utf-8'), self.text)

    def test_generated_state_relationship_is_subset_not_exact_evidence_equality(self):
        # Evidence is written after suites execute. Only enforce that recorded entries are in
        # the configured command scope; never require pre-run output to equal future test counts.
        if align.STATE_PATH.is_file():
            state = json.loads(align.STATE_PATH.read_text(encoding='utf-8'))
            script_ids = {step['id'] for step in self.plan['local_sequence']}
            recorded_ids = {step['id'] for step in state.get('local_steps', [])}
            self.assertLessEqual(recorded_ids, script_ids)
            self.assertIn('run_offline_suites.py', state.get('evidence', {}).get('source_script', ''))


if __name__ == '__main__':
    unittest.main()
