"""Offline tests for the issue #6 close-out tool.

They hold the two things that matter: the checked-in comment may only cite
check-runs the record actually holds, and the tool may never report a close it did
not observe. No network call is made here; the posting path is tested with an
injected runner.
"""
import json
import subprocess
import unittest

import post_issue_closeout as tool

BLOCKED_OUTPUT = '{"message":"Resource not accessible by integration","status":403}'


class ValidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(tool.RECORD.read_text(encoding='utf-8'))
        cls.comment = tool.COMMENT.read_text(encoding='utf-8')

    def test_checked_in_comment_is_valid_against_the_record(self):
        self.assertEqual(tool.validate(self.comment, self.record), [])

    def test_comment_cites_real_check_runs(self):
        cited = tool.cited_ids(self.comment)
        self.assertTrue(cited)
        self.assertTrue(set(cited) <= tool.known_ids(self.record))
        self.assertTrue(tool.known_check_runs(self.record))
        self.assertIn(112253587690, tool.known_check_runs(self.record))

    def test_recheck_file_is_consulted_for_probe_evidence(self):
        probe_id = 112302972786
        self.assertIn(probe_id, tool.known_ids(self.record))
        self.assertNotIn(probe_id, tool.known_ids(self.record, extra_paths=()))
        text = self.comment + f'\nProbe check-run {probe_id} confirms the tree.\n'
        self.assertEqual(tool.validate(text, self.record), [])
        self.assertTrue(tool.validate(text, self.record, extra_paths=()))

    def test_unknown_check_run_is_refused(self):
        problems = tool.validate(self.comment + '\nSee check-run 999999999999.\n', self.record)
        self.assertTrue(any('999999999999' in problem for problem in problems))

    def test_comment_must_state_the_result_and_scope(self):
        stripped = self.comment.replace('status=MATCH', 'status=SOMETHING').replace('traffic_switched=NONE', 'traffic_switched=YES')
        problems = tool.validate(stripped, self.record)
        self.assertEqual(len(problems), 2)

    def test_default_mode_prints_the_plan_and_exits_blocked(self):
        proc = subprocess.run(['python3', str(tool.__file__)], capture_output=True, text=True, cwd=str(tool.HERE))
        self.assertEqual(proc.returncode, tool.EXIT_BLOCKED_OWNER)
        self.assertIn('Would run: gh issue comment 6', proc.stdout)
        self.assertIn('issues=read only', proc.stdout)

    def test_help_is_offline(self):
        proc = subprocess.run(['python3', str(tool.__file__), '--check'], capture_output=True, text=True,
                              cwd=str(tool.HERE))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn('OK:', proc.stdout)
        self.assertNotIn('Resource not accessible', proc.stdout)


class PostTests(unittest.TestCase):
    def test_blocked_comment_never_claims_a_close(self):
        calls = []

        def runner(command):
            calls.append(command)
            return 1, BLOCKED_OUTPUT

        outcome = tool.post(runner=runner)
        self.assertTrue(outcome['blocked'])
        self.assertFalse(outcome['closed'])
        self.assertEqual(len(calls), 1, 'close must not be attempted after a failed comment')
        self.assertIn('not attempted', outcome['close']['output'])

    def test_successful_comment_closes_and_reports_both(self):
        calls = []

        def runner(command):
            calls.append(command)
            return 0, 'posted' if command[1] == 'issue' and command[2] == 'comment' else 'closed'

        outcome = tool.post(runner=runner)
        self.assertFalse(outcome['blocked'])
        self.assertTrue(outcome['closed'])
        self.assertEqual([c[2] for c in calls], ['comment', 'close'])

    def test_close_failure_is_reported_as_not_closed(self):
        def runner(command):
            return (0, 'posted') if command[2] == 'comment' else (1, BLOCKED_OUTPUT)

        outcome = tool.post(runner=runner)
        self.assertTrue(outcome['blocked'])
        self.assertFalse(outcome['closed'])


if __name__ == '__main__':
    unittest.main()
