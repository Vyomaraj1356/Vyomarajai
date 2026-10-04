"""Offline checks for the change desk: authority chain, version control, separate testing,
permission gate and the backup/rollback plan."""
import unittest

import change_manager as desk


class ChangePlanningTests(unittest.TestCase):
    def test_owner_instruction_becomes_a_planned_change_with_all_stages(self):
        record = desk.plan_change({'instruction': 'Add Hinglish editions to the comics lane.',
                                   'kind': 'feature', 'affected_lanes': ['comics']})
        self.assertEqual(record['status'], 'change_planned_awaiting_owner_permission')
        self.assertTrue(record['change_id'].startswith('CHG-'))
        self.assertTrue(record['authority_chain']['shriyantra_aligned'])
        self.assertIn('ShriYantra', record['authority_chain']['alignment'])
        self.assertIn('not the owner', record['authority_chain']['arena_role'])
        self.assertTrue(record['version_control']['branch'].startswith('upgrade/'))
        self.assertFalse(record['version_control']['history_deleted'])
        self.assertEqual([t['stage'] for t in record['testing_plan']], [1, 2, 3, 4])
        self.assertTrue(all(t['result'] == 'pending_separate_execution' for t in record['testing_plan']))
        self.assertEqual(record['permission_gate']['status'], 'PENDING_OWNER_PERMISSION')
        self.assertEqual(len(record['upgrade_plan']['steps']), 6)
        self.assertFalse(record['upgrade_plan']['running_business_interrupted'])
        self.assertFalse(record['rollback_plan']['engaged'])
        self.assertFalse(record['applied'] or record['rolled_back'] or record['live_system_touched'])

    def test_upgrade_plan_snapshots_before_applying(self):
        record = desk.plan_change({'instruction': 'Upgrade the morning briefing voice pack.'})
        self.assertEqual(record['upgrade_plan']['steps'][0], 'snapshot the current running version (backup first)')

    def test_invalid_instructions_are_refused(self):
        for bad in ('tiny', 'x' * 501, 42, None):
            with self.assertRaises(desk.InvalidChange, msg=repr(bad)):
                desk.plan_change({'instruction': bad})
        with self.assertRaises(desk.InvalidChange):
            desk.plan_change({'instruction': 'A valid instruction.', 'kind': 'rewrite-history'})
        with self.assertRaises(desk.InvalidChange):
            desk.plan_change({'instruction': 'A valid instruction.', 'surprise': True})
        with self.assertRaises(desk.InvalidChange):
            desk.plan_change({'instruction': 'A valid instruction.', 'affected_agents': 'everyone'})

    def test_all_change_kinds_are_accepted(self):
        for kind in ('feature', 'fix', 'upgrade'):
            record = desk.plan_change({'instruction': 'A valid instruction.', 'kind': kind})
            self.assertEqual(record['kind'], kind)


class ChangePermissionTests(unittest.TestCase):
    def record(self, **kw):
        return desk.plan_change({'instruction': 'Fix the camera queue order oldest first.', **kw})

    def test_owner_approval_schedules_the_upgrade_with_rollback_ready(self):
        approved = desk.apply_permission(self.record(), 'approve')
        self.assertEqual(approved['status'], 'upgrade_scheduled_with_rollback_ready')
        self.assertEqual(approved['permission_gate']['status'], 'OWNER_APPROVED')
        self.assertIn('ShriYantra', approved['permission_gate']['decided_by'])
        self.assertFalse(approved['applied'])
        self.assertFalse(approved['live_system_touched'])

    def test_owner_rejection_keeps_the_current_version(self):
        rejected = desk.apply_permission(self.record(), 'reject')
        self.assertEqual(rejected['status'], 'not_applied_current_version_continues')
        self.assertEqual(rejected['permission_gate']['status'], 'OWNER_REJECTED')
        self.assertFalse(rejected['applied'] or rejected['rolled_back'])

    def test_only_planned_changes_can_be_decided(self):
        approved = desk.apply_permission(self.record(), 'approve')
        with self.assertRaises(desk.InvalidChange):
            desk.apply_permission(approved, 'approve')
        with self.assertRaises(desk.InvalidChange):
            desk.apply_permission({'status': 'something-else'}, 'approve')
        with self.assertRaises(desk.InvalidChange):
            desk.apply_permission(self.record(), 'publish-anyway')


class RollbackTests(unittest.TestCase):
    def test_failed_verification_engages_the_backup_plan(self):
        record = desk.apply_permission(desk.plan_change({'instruction': 'Add Hinglish editions.'}), 'approve')
        failure = desk.report_failure(record, 'post-upgrade verification')
        self.assertEqual(failure['status'], 'backup_plan_engaged_rolled_back')
        self.assertTrue(failure['rollback_plan']['engaged'])
        self.assertEqual(failure['failed_stage'], 'post-upgrade verification')
        self.assertIn('current version', failure['action'])
        self.assertIn('no commit is deleted', failure['history'])
        self.assertFalse(failure['owner_notified']['sent'])

    def test_only_scheduled_upgrades_can_fail(self):
        with self.assertRaises(desk.InvalidChange):
            desk.report_failure(desk.plan_change({'instruction': 'Add Hinglish editions.'}), 'stage 1')
        with self.assertRaises(desk.InvalidChange):
            desk.report_failure(desk.apply_permission(
                desk.plan_change({'instruction': 'Add Hinglish editions.'}), 'approve'), '')


if __name__ == '__main__':
    unittest.main()
