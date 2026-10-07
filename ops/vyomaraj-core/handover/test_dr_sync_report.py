"""Offline checks that the DR sync results report faithfully renders its evidence.

The report must never be edited by hand: these tests rebuild it from the recorded evidence and
compare byte-for-byte, then check the claims a reader relies on (counts, blocked run, limits).
"""
import unittest

import build_dr_sync_report as dr


class DrSyncReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = dr.load(dr.RECORD)
        cls.policy = dr.load(dr.POLICY)
        cls.text = dr.OUTPUT.read_text()

    def test_checked_in_report_matches_the_builder(self):
        self.assertEqual(self.text, dr.render(),
                         'DR_SYNC_RESULTS_2026_10_04.md is out of date; rebuild and review')

    def test_counts_match_the_record(self):
        checkpoints = len(self.record['observations'])
        writes = sum(1 for o in self.record['observations'] if o.get('replication_write_in_this_run'))
        self.assertEqual(checkpoints, self.record['checkpoints_total'])
        self.assertEqual(writes, self.record['replication_writes_total'])
        self.assertIn(f'## 3. Verification checkpoints ({checkpoints})', self.text)
        self.assertIn(f'## 4. Replication writes ({writes})', self.text)

    def test_every_checkpoint_appears_with_matching_trees(self):
        for o in self.record['observations']:
            run_id = o['workflow_run_id']
            check_id = o['check_run_id']
            self.assertIn(str(check_id), self.text)
            self.assertIn(str(run_id), self.text)
            self.assertIn(f'[`{run_id}`]({dr.REPO_URL}/actions/runs/{run_id})', self.text)
            self.assertIn(f'[`{check_id}`]({dr.REPO_URL}/actions/runs/{run_id}/job/{check_id})', self.text)
            self.assertIn(f'[`{o["head_sha"][:dr.SHORT]}`]({dr.REPO_URL}/commit/{o["head_sha"]})', self.text)
            if o.get('merge_pr'):
                self.assertIn(f'[#{o["merge_pr"]}]({dr.REPO_URL}/pull/{o["merge_pr"]})', self.text)
            self.assertEqual(o['primary_tree'], o['secondary_tree'])
            self.assertEqual(o['status'], 'MATCH')

    def test_blocked_run_is_reported_as_blocked_not_as_a_match(self):
        blocked = self.record['blocked_runs'][0]
        self.assertIn(f"check-run [`{blocked['check_run_id']}`]", self.text)
        self.assertIn('status=BLOCKED', self.text)
        self.assertIn(f"deliberately excluded from the checkpoint count", self.text)
        # the blocked check-run must never be counted among the MATCH rows
        self.assertNotIn(f"| {blocked['check_run_id']} |", self.text)

    def test_scope_limits_are_stated_explicitly(self):
        self.assertFalse(self.record['traffic_switched'])
        self.assertFalse(self.record['runtime_or_site_dr_verified'])
        self.assertFalse(self.record['zero_rpo_or_rto_claimed'])
        self.assertFalse(self.policy['zero_rpo_verified'])
        self.assertFalse(self.policy['zero_rto_verified'])
        for fragment in ('production disaster-recovery approval',
                         'Traffic was never switched', 'Runtime/site disaster recovery was not tested',
                         'No zero-RPO/RTO claim is made', 'Automatic target-only file removal is off'):
            self.assertIn(fragment, self.text)

    def test_report_carries_its_sources_and_hashes(self):
        for path in (dr.RECORD, dr.POLICY, dr.WORKFLOW):
            self.assertIn(path.relative_to(dr.ROOT).as_posix(), self.text)
            self.assertIn(dr.digest(path), self.text)

    def test_current_extension_renders_the_live_checkpoint_audit_and_pr_39_status(self):
        extension = self.record['record_extension_2026_10_07']
        self.assertEqual(extension['annotation_audit']['previous_checkpoints_re_read'], 34)
        self.assertEqual(extension['annotation_audit']['mismatches'], 0)
        self.assertIn('## 5j. Record extension', self.text)
        self.assertIn('112423653494', self.text)
        self.assertIn('112605459778', self.text)
        self.assertIn('PR #39 is OPEN and DRAFT', self.text)
        self.assertIn('[live PR page](https://github.com/Vyomaraj1356/Vyomarajai/pull/39)', self.text)
        self.assertIn('36 MATCH checkpoints (25 replication writes)', self.text)

    def test_publication_status_section_reports_the_record_not_a_wish(self):
        publication = self.record['publication_status']
        self.assertFalse(publication['pushed_at_record_time'])
        self.assertFalse(publication['local_sync_possible_from_this_sandbox'])
        self.assertIn('## 5b. Publication status of this record', self.text)
        self.assertIn(publication['recorded_by_session'], self.text)
        self.assertIn('→ pull request → merge to main', self.text)
        for item in publication['rebuilt_from_lost_local_commits']['rebuilt_in_this_merge']:
            self.assertIn(item, self.text)
        self.assertIn('2430a16', self.text)
        self.assertIn('ac2f741', self.text)
        self.assertIn(publication['published_as'], self.text)
        self.assertIn(publication['comics_and_architecture_coverage'][:80], self.text)

    def test_trailing_checkpoint_rule_is_stated_with_a_live_command(self):
        self.assertIn('## 5c. The trailing-checkpoint rule', self.text)
        self.assertIn('not an unverified merge', self.text)
        self.assertIn('commits/main/check-runs', self.text)
        self.assertIn('DR SNAPSHOT RESULT', self.text)

    def test_local_verification_attempt_is_reported_as_blocked(self):
        attempt = self.record['local_verification_attempt']
        self.assertIn('BLOCKED', attempt['result'])
        self.assertIn('## 5d. Local verification attempt', self.text)
        self.assertIn(attempt['command'], self.text)
        self.assertIn('404', self.text)
        self.assertIn('not evidence about the secondary', self.text)

    def test_no_secret_like_values(self):
        lowered = self.text.lower()
        for marker in ('ghp_', 'github_pat_', 'token=', 'password', 'secret='):
            self.assertNotIn(marker, lowered)


if __name__ == '__main__':
    unittest.main()
