import base64
import unittest

import dr_sync as dr

TARGET = 'example/confirmed-recovery'
RAW = b'verified source file\n'
BLOB = dr.git_blob_sha(RAW)
ENV = {'GITHUB_REPOSITORY': dr.PRIMARY, 'GITHUB_REF': 'refs/heads/main',
       'DR_SYNC_APPROVED': 'true', 'PRIMARY_TOKEN': 'test-only', 'DR_TOKEN': 'test-only'}


class FakeGitHub:
    def __init__(self, repo, tree, commit):
        self.repo, self.tree, self.commit = repo, tree, commit
        self.calls = []
        self.created_tree = 'source-tree'
        self.truncated = False
        self.entry_type = 'blob'
        self.fail_status = None
        self.bad_blob = False
        self.bad_readback = False
        self.advance_after_tree = False

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        if self.fail_status:
            raise dr.APIError(self.fail_status)
        if method == 'GET' and path == f'repos/{self.repo}':
            return {'full_name': self.repo}
        if method == 'GET' and '/git/ref/heads/' in path:
            return {'object': {'sha': self.commit}}
        if method == 'GET' and '/git/commits/' in path:
            return {'tree': {'sha': self.tree}}
        if method == 'GET' and '/git/trees/' in path:
            return {'truncated': self.truncated, 'tree': [
                {'path': 'safe.txt', 'mode': '100644', 'type': self.entry_type, 'sha': BLOB}]}
        if method == 'GET' and '/git/blobs/' in path:
            return {'encoding': 'base64', 'content': base64.b64encode(RAW).decode()}
        if method == 'POST' and path.endswith('/git/blobs'):
            return {'sha': 'wrong' if self.bad_blob else BLOB}
        if method == 'POST' and path.endswith('/git/trees'):
            if self.advance_after_tree:
                self.commit = 'concurrent-target-update'
            return {'sha': self.created_tree}
        if method == 'POST' and path.endswith('/git/commits'):
            return {'sha': 'new-commit'}
        if method == 'PATCH':
            if not self.bad_readback:
                self.commit, self.tree = body['sha'], self.created_tree
            return {}
        raise AssertionError((method, path))


class DRTests(unittest.TestCase):
    def setUp(self):
        self.primary = FakeGitHub(dr.PRIMARY, 'source-tree', 'source-commit')
        self.secondary = FakeGitHub(TARGET, 'old-tree', 'old-commit')

    def run_check(self, sync=False, env=None):
        return dr.execute(TARGET, sync, self.primary, self.secondary, ENV if env is None else env)

    def assert_no_ref_writes(self):
        self.assertFalse(any(m == 'PATCH' or (m == 'POST' and '/git/refs' in p)
                             for m, p, _ in self.secondary.calls))

    def test_default_is_read_only_mismatch(self):
        self.assertEqual(self.run_check()['status'], 'MISMATCH')
        self.assertTrue(all(m == 'GET' for m, _, _ in self.secondary.calls))

    def test_equal_tree_different_commit_is_match(self):
        self.secondary.tree = 'source-tree'
        result = self.run_check()
        self.assertEqual(result['status'], 'MATCH')
        self.assertFalse(result['replication_performed'])

    def test_sync_already_equal_is_noop(self):
        self.secondary.tree = 'source-tree'
        self.assertFalse(self.run_check(True)['replication_performed'])
        self.assertTrue(all(m == 'GET' for m, _, _ in self.secondary.calls))

    def test_sync_exact_tree_preserves_parent_never_force(self):
        result = self.run_check(True)
        self.assertTrue(result['data_match'])
        self.assertFalse(result['traffic_switched'])
        tree_body = next(b for m, p, b in self.secondary.calls if m == 'POST' and p.endswith('/trees'))
        self.assertNotIn('base_tree', tree_body)
        commit_body = next(b for m, p, b in self.secondary.calls if m == 'POST' and p.endswith('/commits'))
        self.assertEqual(commit_body['parents'], ['old-commit'])
        patch = next(b for m, p, b in self.secondary.calls if m == 'PATCH')
        self.assertIs(patch['force'], False)

    def test_target_404_does_not_initialize(self):
        self.secondary.fail_status = 404
        with self.assertRaisesRegex(dr.CheckError, 'hidden by permissions'):
            self.run_check(True)
        self.assertTrue(all(m == 'GET' for m, _, _ in self.secondary.calls))

    def test_invalid_token_report_is_redacted(self):
        self.secondary.fail_status = 401
        with self.assertRaisesRegex(dr.CheckError, 'reconnect GitHub'):
            self.run_check()

    def test_branch_write_guard(self):
        with self.assertRaisesRegex(dr.CheckError, 'primary repository main'):
            self.run_check(True, {**ENV, 'GITHUB_REF': 'refs/heads/arena/01a10140-vyomarajai'})
        self.assertEqual(self.primary.calls, [])

    def test_repository_write_guard(self):
        with self.assertRaises(dr.CheckError):
            self.run_check(True, {**ENV, 'GITHUB_REPOSITORY': TARGET})

    def test_approval_guard(self):
        with self.assertRaisesRegex(dr.CheckError, 'explicit'):
            self.run_check(True, {**ENV, 'DR_SYNC_APPROVED': 'false'})

    def test_missing_token_guard(self):
        with self.assertRaisesRegex(dr.CheckError, 'credentials are missing'):
            self.run_check(True, {**ENV, 'DR_TOKEN': ''})

    def test_no_target_guessed(self):
        for target in ('', dr.PRIMARY, dr.PRIMARY.lower(), 'https://github.com/a/b', 'a/../b'):
            with self.subTest(target=target), self.assertRaises(dr.CheckError):
                dr.validate_target(target)

    def test_truncated_tree(self):
        self.primary.truncated = True
        with self.assertRaisesRegex(dr.CheckError, 'Truncated'):
            self.run_check(True)
        self.assert_no_ref_writes()

    def test_submodule_rejected(self):
        self.primary.entry_type = 'commit'
        with self.assertRaisesRegex(dr.CheckError, 'Unsupported'):
            self.run_check(True)
        self.assert_no_ref_writes()

    def test_bad_blob_hash(self):
        self.secondary.bad_blob = True
        with self.assertRaisesRegex(dr.CheckError, 'blob integrity'):
            self.run_check(True)
        self.assert_no_ref_writes()

    def test_bad_tree_never_published(self):
        self.secondary.created_tree = 'bad-tree'
        with self.assertRaisesRegex(dr.CheckError, 'differs from source'):
            self.run_check(True)
        self.assert_no_ref_writes()

    def test_concurrent_target_change_never_published(self):
        self.secondary.advance_after_tree = True
        with self.assertRaisesRegex(dr.CheckError, 'changed during'):
            self.run_check(True)
        self.assert_no_ref_writes()

    def test_bad_read_after_write_is_failure(self):
        self.secondary.bad_readback = True
        with self.assertRaisesRegex(dr.CheckError, 'Read-after-write mismatch'):
            self.run_check(True)

    def test_empty_source_refused(self):
        with self.assertRaisesRegex(dr.CheckError, 'Empty'):
            dr.source_entries({'tree': []})

    def test_duplicate_source_refused(self):
        entry = {'type': 'blob', 'mode': '100644', 'path': 'same', 'sha': BLOB}
        with self.assertRaisesRegex(dr.CheckError, 'duplicate'):
            dr.source_entries({'tree': [entry, entry]})

    def test_redirect_refused(self):
        self.assertIsNone(dr.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other'))


if __name__ == '__main__':
    unittest.main()
