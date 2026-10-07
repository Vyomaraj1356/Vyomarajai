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
        for path in (dr.RECORD, dr.POLICY, dr.WORKFLOW, dr.ISSUES_LEDGER):
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
        self.assertIn('39 selected MATCH checkpoints and 27 recorded replication writes', self.text)

    def test_latest_main_tip_and_scheduled_match_are_recorded_with_scope_limits(self):
        self.assertEqual(self.record['checkpoints_total'], 41)
        self.assertEqual(self.record['replication_writes_total'], 27)
        self.assertIn('## 5k. Main-tip and scheduled-match extension', self.text)
        self.assertIn('112618764790', self.text)
        self.assertIn('112620862227', self.text)
        self.assertIn('112696426971', self.text)
        self.assertIn('986288ee2cc4ec4d89400320150ea893f7a7a2de', self.text)
        self.assertIn('tracked repository-tree match only', self.text)
        self.assertIn('signature, signer provenance and real-device installation remain unverified', self.text)
        self.assertIn('2 commits ahead', self.text)

    def test_followup_scheduled_checkpoint_is_additive_and_scope_limited(self):
        extension = self.record['record_extension_2026_10_07_c']
        latest = extension['latest_scheduled_match']
        self.assertEqual(latest['workflow_run_id'], 37602725866)
        self.assertEqual(latest['check_run_id'], 112730920825)
        self.assertEqual(latest['completed_at_utc'], '2026-10-07T09:45:42Z')
        self.assertEqual(latest['status'], 'MATCH')
        self.assertTrue(latest['data_match'])
        self.assertEqual(latest['primary_tree'], latest['secondary_tree'])
        self.assertEqual(latest['traffic_switched'], 'NONE')
        self.assertFalse(latest['replication_write_in_this_run'])
        self.assertEqual(extension['annotation_audit']['previous_checkpoints_reread'], 0)
        self.assertIn('## 5l. Follow-up scheduled checkpoint', self.text)
        self.assertIn('112730920825', self.text)
        self.assertIn('37602725866', self.text)
        self.assertIn('http=UNAVAILABLE', self.text)
        self.assertIn('not runtime, deployed-app, authenticated-heartbeat, failover, RPO or RTO evidence', self.text)

    def test_latest_scheduled_checkpoint_followup_is_additive_and_scope_limited(self):
        extension = self.record['record_extension_2026_10_07_d']
        latest = extension['latest_scheduled_match']
        self.assertEqual(latest['workflow_run_id'], 37605789908)
        self.assertEqual(latest['check_run_id'], 112741170924)
        self.assertEqual(latest['completed_at_utc'], '2026-10-07T10:13:11Z')
        self.assertEqual(latest['status'], 'MATCH')
        self.assertTrue(latest['data_match'])
        self.assertEqual(latest['primary_tree'], latest['secondary_tree'])
        self.assertEqual(latest['traffic_switched'], 'NONE')
        self.assertFalse(latest['replication_write_in_this_run'])
        self.assertEqual(extension['annotation_audit']['previous_checkpoints_reread'], 0)
        self.assertIn('## 5m. Latest scheduled checkpoint follow-up', self.text)
        self.assertIn('112741170924', self.text)
        self.assertIn('37605789908', self.text)
        self.assertIn('http=UNAVAILABLE', self.text)
        self.assertIn('prior checkpoint annotations reread in this addendum: 0', self.text)

    def test_current_access_recheck_is_separate_from_historical_sync_checkpoints(self):
        live = dr.load(dr.ISSUES_LEDGER)['current_live_recheck_2026_10_07']
        self.assertIn('Current GitHub / DR access recheck — 7 October 2026', self.text)
        self.assertIn(live['checked_at_utc'], self.text)
        self.assertIn('OPEN/P0', self.text)
        self.assertIn('four candidate secondary paths returned 404', self.text)
        self.assertIn('403 Resource not accessible by integration', self.text)
        self.assertIn('Current authoritative-target identity/access and target-only data review remain owner-blocked', self.text)
        self.assertIn('Latest scheduled DR run', self.text)
        self.assertIn('tracked repository-tree match only', self.text)
        self.assertIn('Automatic main-push replication writes', self.text)
        self.assertIn('PR #39 was left untouched', self.text)
        self.assertIn('feature branch is not deployed', self.text)

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
        self.assertIn('## 5c. Checkpoint selection and the next-read rule', self.text)
        self.assertIn('one successful verify-or-sync checkpoint for each newly observed main tip', self.text)
        self.assertIn('After an owner-approved merge', self.text)
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
