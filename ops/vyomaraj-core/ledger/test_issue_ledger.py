"""Tests for the owner-review issue/PR ledger and prepared close-out."""
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

    def test_issue_six_is_ready_to_close_but_not_closed_or_posted(self):
        self.assertEqual(self.data['snapshot']['issue_6_state'], 'OPEN')
        self.assertEqual(self.by_id['issue-6']['status'], 'READY_TO_CLOSE')
        self.assertTrue(self.data['issue_6_closeout']['prepared_but_not_sent'])
        self.assertIn('no comment or close action has been performed', self.by_id['issue-6']['summary'])

    def test_issue_six_checkpoint_matches_the_live_snapshot_values(self):
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

    def test_runbook_is_ordered_and_contains_403_stop_rule(self):
        runbook = self.data['issue_6_closeout']['runbook']
        self.assertEqual(len(runbook), 5)
        self.assertIn('Before any GitHub write', runbook[0])
        self.assertIn('re-read every check-run annotation', runbook[0])
        self.assertIn('rollback_commit row by row', runbook[0])
        self.assertIn('gh issue comment 6', runbook[2])
        self.assertIn('gh issue close 6', runbook[3])
        self.assertIn('403', runbook[4])
        self.assertIn('New-session runbook (in order)', self.text)

    def test_report_matches_builder_and_contains_no_secrets_or_money_claims(self):
        report = ledger.OUTPUT.read_text(encoding='utf-8')
        self.assertEqual(report, self.text)
        lowered = report.lower()
        for marker in ('ghp_', 'github_pat_', 'token=', 'password='):
            self.assertNotIn(marker, lowered)
        self.assertIn('No prices, plan limits or earnings projections', self.text)


if __name__ == '__main__':
    unittest.main()
