"""Offline checks for the change desk: authorization, plan-only status and rollback honesty."""
from pathlib import Path
import subprocess
import unittest

import change_manager as desk


class ChangePlanningTests(unittest.TestCase):
    def test_owner_instruction_becomes_a_planned_change_with_all_stages(self):
        record = desk.plan_change({'instruction': 'Add Hinglish editions to the comics lane.',
                                   'kind': 'feature', 'affected_lanes': ['comics']})
        self.assertEqual(record['status'], 'change_planned_awaiting_owner_permission')
        self.assertTrue(record['change_id'].startswith('CHG-'))
        self.assertFalse(record['authority_chain']['shriyantra_aligned'])
        self.assertFalse(record['authority_chain']['owner_approval_verified'])
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

    def test_owner_approval_records_plan_only_and_does_not_schedule_or_apply(self):
        approved = desk.apply_permission(self.record(), 'approve', decided_by='owner-subject-test')
        self.assertEqual(approved['status'], 'owner_approved_change_plan_not_applied')
        self.assertEqual(approved['permission_gate']['status'], 'OWNER_APPROVED_PLAN_ONLY')
        self.assertEqual(approved['permission_gate']['decided_by'], 'owner-subject-test')
        self.assertTrue(approved['authority_chain']['shriyantra_aligned'])
        self.assertTrue(approved['authority_chain']['owner_approval_verified'])
        self.assertEqual(approved['scheduling_status'], 'NOT_SCHEDULED_RUNTIME_ADAPTER_UNAVAILABLE')
        self.assertFalse(approved['applied'])
        self.assertFalse(approved['live_system_touched'])

    def test_owner_rejection_keeps_the_current_version(self):
        rejected = desk.apply_permission(self.record(), 'reject', decided_by='owner-subject-test')
        self.assertEqual(rejected['status'], 'owner_rejected_change_plan_not_applied')
        self.assertEqual(rejected['permission_gate']['status'], 'OWNER_REJECTED')
        self.assertFalse(rejected['applied'] or rejected['rolled_back'])

    def test_only_planned_changes_can_be_decided(self):
        approved = desk.apply_permission(self.record(), 'approve', decided_by='owner-subject-test')
        with self.assertRaises(desk.InvalidChange):
            desk.apply_permission(approved, 'approve', decided_by='owner-subject-test')
        with self.assertRaises(desk.InvalidChange):
            desk.apply_permission({'status': 'something-else'}, 'approve', decided_by='owner-subject-test')
        with self.assertRaises(desk.InvalidChange):
            desk.apply_permission(self.record(), 'publish-anyway', decided_by='owner-subject-test')
        with self.assertRaises(desk.InvalidChange):
            desk.apply_permission(self.record(), 'approve', decided_by='')


class RollbackTests(unittest.TestCase):
    def test_failed_verification_prepares_but_does_not_execute_rollback(self):
        record = desk.apply_permission(
            desk.plan_change({'instruction': 'Add Hinglish editions.'}), 'approve',
            decided_by='owner-subject-test',
        )
        failure = desk.report_failure(record, 'post-upgrade verification')
        self.assertEqual(failure['status'], 'rollback_plan_prepared_not_executed')
        self.assertFalse(failure['rollback_plan']['engaged'])
        self.assertEqual(failure['rollback_plan']['execution_status'], 'NOT_EXECUTED')
        self.assertEqual(failure['failed_stage'], 'post-upgrade verification')
        self.assertIn('No service action was taken', failure['action'])
        self.assertIn('No repository history was changed', failure['history'])
        self.assertFalse(failure['rolled_back'])
        self.assertEqual(failure['business_impact'], 'UNKNOWN_NOT_CHECKED_BY_THIS_PLANNER')
        self.assertFalse(failure['owner_notified']['sent'])

    def test_only_verified_approved_plans_can_prepare_failure_report(self):
        with self.assertRaises(desk.InvalidChange):
            desk.report_failure(desk.plan_change({'instruction': 'Add Hinglish editions.'}), 'stage 1')
        approved = desk.apply_permission(
            desk.plan_change({'instruction': 'Add Hinglish editions.'}), 'approve',
            decided_by='owner-subject-test',
        )
        with self.assertRaises(desk.InvalidChange):
            desk.report_failure(approved, '')


class UpgradeControllerTests(unittest.TestCase):
    def test_execute_flag_fails_before_snapshot_or_process_side_effects(self):
        script = Path(desk.CONTENT_PATH).with_name('upgrade-controller.sh')
        result = subprocess.run(
            ['bash', str(script), '--execute'], capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 4)
        self.assertIn('authenticated owner approval', result.stderr)
        self.assertIn('No snapshot, test, service, or repository mutation was performed', result.stderr)


if __name__ == '__main__':
    unittest.main()
