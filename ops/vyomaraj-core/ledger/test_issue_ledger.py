"""Tests for the current owner-blocked issue/PR ledger and historical close-out draft."""
import json
import sys
import unittest
from pathlib import Path

HANDOVER = Path(__file__).resolve().parents[1] / 'handover'
sys.path.insert(0, str(HANDOVER))
import build_issue_ledger as ledger  # noqa: E402


class IssueLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ledger.load()
        cls.text = ledger.render(data=cls.data)
        cls.by_id = {entry['id']: entry for entry in cls.data['entries']}

    def test_fourteen_ledger_entries_and_unique_ids(self):
        self.assertEqual(len(self.data['entries']), 14)
        self.assertEqual(len(self.by_id), 14)
        self.assertEqual(ledger.validate(self.data), [])

    def test_issue_six_remains_owner_blocked_and_historical_draft_is_not_for_posting(self):
        self.assertEqual(self.data['snapshot']['issue_6_state'], 'OPEN')
        self.assertEqual(self.by_id['issue-6']['status'], 'OWNER_ACTION_REQUIRED')
        issue = self.data['issue_6_closeout']
        self.assertTrue(issue['prepared_but_not_sent'])
        self.assertTrue(issue['historical_snapshot_only'])
        self.assertTrue(issue['do_not_post_or_close'])
        self.assertEqual(issue['current_live_state'], 'OPEN/P0')
        self.assertIn('Owner/admin', self.by_id['issue-6']['next_action'])
        self.assertIn('DO NOT POST OR CLOSE', self.text)

    def test_live_recheck_records_pr_pages_and_access_blocks(self):
        live = self.data['current_live_recheck_2026_10_07']
        self.assertEqual(live['issue_6']['state'], 'OPEN')
        self.assertEqual(live['issue_6']['priority'], 'P0')
        self.assertEqual(live['actions_variables_api'][:3], '403')
        self.assertTrue(live['checked_at_utc'].startswith('2026-10-07T08:28'))
        self.assertEqual(live['dr_snapshot']['status'], 'MATCH')
        self.assertEqual(live['dr_snapshot']['primary_tree'], live['dr_snapshot']['secondary_tree'])
        self.assertEqual(live['dr_snapshot']['traffic_switched'], 'NONE')
        self.assertTrue(live['dr_target_resolution']['effective_target_identity'].startswith('UNCONFIRMED:'))
        self.assertEqual(live['observed_main_replication_writes']['count_since_previous_recorded_checkpoint'], 2)
        self.assertEqual(live['pull_requests']['41']['state'], 'OPEN')
        self.assertTrue(live['pull_requests']['39']['draft'])
        self.assertEqual(live['pages']['status'], 'built')
        self.assertFalse(live['pages']['feature_branch_deployed'])
        self.assertIn('do not prove', live['secondary_path_probes']['interpretation'])

    def test_current_dr_tree_match_is_separate_from_owner_acceptance(self):
        live = self.data['current_live_recheck_2026_10_07']
        self.assertIn('status=MATCH', self.text)
        self.assertIn(str(live['dr_snapshot']['check_run_id']), self.text)
        self.assertIn(live['dr_snapshot']['primary_tree'], self.text)
        self.assertIn('repository-tree equality only', self.text)
        self.assertIn('target-only-data review remain owner-blocked', self.text)
        self.assertIn('Automatic main-push replication writes observed', self.text)
        self.assertIn('signature validity', self.text)
        self.assertIn('UNVERIFIED', self.text)

    def test_issue_six_checkpoint_is_historical_not_current_acceptance(self):
        record = self.data['snapshot']['merge_checkpoint']
        self.assertEqual(record['pull_request'], 24)
        self.assertEqual(record['check_run_id'], 111404791435)
        self.assertEqual(record['status'], 'MATCH')
        self.assertEqual(record['primary_tree'], record['secondary_tree'])
        self.assertEqual(self.data['issue_6_closeout']['checkpoint'], '#19')
        self.assertEqual(self.data['issue_6_closeout']['replication_writes'], 15)

    def test_divergent_pull_requests_remain_owner_decisions(self):
        for pr in ('pr-2', 'pr-3', 'pr-4', 'pr-7'):
            with self.subTest(pr=pr):
                self.assertEqual(self.by_id[pr]['status'], 'OWNER_DECISION_REQUIRED')
                self.assertIn('Do not merge', self.by_id[pr]['summary'])

    def test_pr_nine_is_watch_only(self):
        self.assertEqual(self.by_id['pr-9']['status'], 'WATCH')
        self.assertIn('not reviewed', self.by_id['pr-9']['summary'])

    def test_merged_chain_is_documented_through_pr_twenty_four(self):
        self.assertEqual(self.by_id['merge-chain-10-24']['status'], 'RESOLVED_DOCUMENTED')
        self.assertIn('#10–#24', self.by_id['merge-chain-10-24']['reference'])

    def test_chat_count_notice_preserves_source_and_both_counts(self):
        entry = self.by_id['chats-count-conflict']
        self.assertEqual(entry['status'], 'FIX_APPLIED_OFFLINE')
        self.assertIn('28', entry['title'])
        self.assertIn('34', entry['title'])
        self.assertIn('source file is preserved unchanged', entry['summary'])

    def test_contract_conflict_is_not_resolved_by_the_ledger(self):
        entry = self.by_id['contract-status-conflict']
        self.assertEqual(entry['status'], 'OWNER_DECISION_REQUIRED')
        self.assertIn('does not guess', entry['summary'])

    def test_all_open_platform_actions_point_to_the_auto_align_plan(self):
        for entry_id in ('secret-manager', 'tool-accounts-plans', 'posilki',
                         'provider-readiness', 'runtime-and-dr-readiness'):
            with self.subTest(entry=entry_id):
                self.assertTrue(any('AUTO_ALIGN_NEXT_SESSION.json' in path
                                    for path in self.by_id[entry_id]['evidence']))

    def test_runbook_is_owner_read_only_and_has_403_404_stop_rule(self):
        runbook = self.data['issue_6_closeout']['runbook']
        self.assertEqual(len(runbook), 5)
        self.assertIn('Keep issue #6 OPEN', runbook[0])
        self.assertIn('canonical owner/name', runbook[1])
        self.assertIn('Do not request or transmit secret values in chat', runbook[2])
        self.assertIn('read-only', runbook[3])
        self.assertIn('403 or 404', self.text)
        self.assertNotIn('gh issue comment 6', self.text)
        self.assertNotIn('gh issue close 6', self.text)
        self.assertIn('Owner/admin runbook (no writes; do not run automatically)', self.text)

    def test_report_matches_builder_and_contains_no_secrets_or_money_claims(self):
        report = ledger.OUTPUT.read_text(encoding='utf-8')
        self.assertEqual(report, self.text)
        lowered = report.lower()
        for marker in ('ghp_', 'github_pat_', 'token=', 'password='):
            self.assertNotIn(marker, lowered)
        self.assertIn('No prices, plan limits or earnings projections', self.text)


if __name__ == '__main__':
    unittest.main()
