"""Offline checks for the timestamped read-only GitHub metadata follow-up."""
import unittest

import build_issue_ledger as ledger


class BuildIssueLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ledger.load()
        cls.text = ledger.OUTPUT.read_text(encoding="utf-8")

    def test_checked_in_ledger_matches_builder(self):
        self.assertEqual(self.text, ledger.render(),
                         "ISSUES_AND_PRS_LEDGER_2026_10_04.md is out of date")

    def test_new_scheduled_annotation_followup_keeps_reread_scope_explicit(self):
        followup = self.data["current_dr_annotation_followup_2026_10_07"]
        self.assertEqual(followup["workflow_run_id"], 37605789908)
        self.assertEqual(followup["check_run_id"], 112741170924)
        self.assertEqual(followup["run_completed_at_utc"], "2026-10-07T10:13:11Z")
        self.assertEqual(followup["status"], "MATCH")
        self.assertTrue(followup["data_match"])
        self.assertEqual(followup["traffic_switched"], "NONE")
        self.assertFalse(followup["replication_write_in_this_run"])
        self.assertEqual(followup["previous_checkpoints_reread"], 0)
        self.assertIn("## Latest scheduled DR annotation follow-up", self.text)
        self.assertIn("112741170924", self.text)
        self.assertIn("previous 40 annotations were not reread", self.text)

    def test_scoped_followup_records_current_issue_pr_main_and_pages_reads(self):
        followup = self.data["current_github_metadata_followup_2026_10_07"]
        self.assertEqual(followup["observed_at_utc"], "2026-10-07T10:06:21Z")
        self.assertEqual(followup["issue_6"]["state"], "OPEN")
        self.assertEqual(followup["issue_6"]["priority"], "P0")
        self.assertEqual(followup["pull_requests"]["39"]["state"], "OPEN")
        self.assertTrue(followup["pull_requests"]["39"]["draft"])
        self.assertEqual(followup["pull_requests"]["41"]["state"], "OPEN")
        self.assertFalse(followup["pull_requests"]["41"]["draft"])
        self.assertTrue(followup["pull_requests"]["42"]["draft"])
        self.assertEqual(followup["main_sha"], "04b7ae60ce2855b1d48043d80f790488e894ee79")
        self.assertEqual(followup["pages"]["source_branch"], "main")
        self.assertEqual(followup["pages"]["source_path"], "/")
        self.assertIn("## Scoped GitHub metadata follow-up", self.text)
        self.assertIn("2026-10-07T10:06:21Z", self.text)
        self.assertIn("PR #39 is `OPEN/DRAFT`", self.text)
        self.assertIn("Read-only recheck; left untouched", followup["pull_requests"]["39"]["note"])
        self.assertIn("Candidate secondary 404s and Actions settings 403s were not re-queried", self.text)


if __name__ == "__main__":
    unittest.main()
