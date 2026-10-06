import os
import unittest
from unittest.mock import Mock, patch
from actions_read_probe import ReadOnlyClient, probe, annotation, trusted_push
from test_dr_sync import FakeGitHub,TARGET
from dr_sync import PRIMARY,CheckError


class TrustedPushTests(unittest.TestCase):
    """The probe must run on any arena/ session branch, and nowhere else.

    It was pinned to one branch name (arena/01a10140-vyomarajai); when that session ended the
    probe could never run again, so every later session lost the read-only credential
    diagnostic. These cases lock the prefix rule in both directions.
    """
    def setUp(self):
        self.env = patch.dict(os.environ, {'GITHUB_REPOSITORY': PRIMARY, 'GITHUB_EVENT_NAME': 'push',
                                           'GITHUB_REF': 'refs/heads/arena/582559e8-vyomarajai'})
        self.env.start(); self.addCleanup(self.env.stop)

    def test_current_session_branch_is_trusted(self):
        self.assertTrue(trusted_push())

    def test_any_arena_branch_is_trusted(self):
        for ref in ('refs/heads/arena/01a10655-vyomarajai', 'refs/heads/arena/some-future-session'):
            with self.subTest(ref=ref), patch.dict(os.environ, {'GITHUB_REF': ref}):
                self.assertTrue(trusted_push())

    def test_main_and_other_refs_are_not_probed(self):
        for ref in ('refs/heads/main', 'refs/heads/feature/x', 'refs/pull/27/merge'):
            with self.subTest(ref=ref), patch.dict(os.environ, {'GITHUB_REF': ref}):
                self.assertFalse(trusted_push())

    def test_foreign_repository_and_non_push_events_are_not_probed(self):
        with patch.dict(os.environ, {'GITHUB_REPOSITORY': 'someone/fork'}):
            self.assertFalse(trusted_push())
        with patch.dict(os.environ, {'GITHUB_EVENT_NAME': 'pull_request'}):
            self.assertFalse(trusted_push())

    def test_missing_ref_is_not_trusted(self):
        with patch.dict(os.environ, {'GITHUB_REF': ''}):
            self.assertFalse(trusted_push())

class ProbeTests(unittest.TestCase):
    def test_write_guard(self):
        delegate=Mock();client=ReadOnlyClient(delegate)
        for method in ['POST','PUT','PATCH','DELETE']:
            with self.assertRaises(CheckError):client.request(method,'repos/example/repo',{})
        with self.assertRaises(CheckError):client.request('GET','repos/example/repo',{})
        delegate.request.assert_not_called()
    def test_token_value_not_retained(self):
        delegate=Mock();delegate.token='DO_NOT_PRINT'
        self.assertIs(ReadOnlyClient(delegate).token,True)
    def compare(self,tree):
        primary=FakeGitHub(PRIMARY,'source-tree','a'*40);secondary=FakeGitHub(TARGET,tree,'b'*40)
        # /user isn't needed for an installation token and returns an API error.
        from dr_sync import APIError
        for client in [primary,secondary]:
            original=client.request
            def request(method,path,body=None,original=original):
                if path=='user':raise APIError(403)
                return original(method,path,body)
            client.request=request
        result=probe(primary,secondary,TARGET)
        self.assertTrue(all(m=='GET' for c in [primary,secondary] for m,p,b in c.calls))
        self.assertFalse(result['dr_sync_verified']);self.assertFalse(result['write_authorization_verified'])
        self.assertNotIn('a'*40,str(result));self.assertEqual(result['secondary_snapshot']['commit'],'b'*40)
        return result
    def test_matching_read_never_claims_sync(self):
        result=self.compare('source-tree');self.assertEqual(result['tree_comparison'],'MATCH')
        self.assertEqual(result['status'],'READ_ACCESS_CONFIRMED')
    def test_mismatch_is_diagnostic_not_write(self):
        result=self.compare('old-tree')
        self.assertEqual(result['tree_comparison'],'MISMATCH')
        self.assertEqual(result['difference_counts']['changed_content_or_mode'],1)
        self.assertNotIn('safe.txt',str(result))
    def test_annotation_closed_values_prevent_injection(self):
        text=annotation({'status':'DO_NOT_PRINT\n::error::oops','secondary_main':{'status':'BLOCKED','http_status':403},'tree_comparison':'MISMATCH'})
        self.assertNotIn('DO_NOT_PRINT',text);self.assertNotIn('\n',text);self.assertIn('HTTP_403',text)

class ResultAnnotationTests(unittest.TestCase):
    def test_error_operation_and_http_without_raw_body(self):
        from dr_sync import actions_result_annotation
        text=actions_result_annotation({'status':'BLOCKED','failed_api_operation':'POST:git/blobs','failed_http_status':403,'detail':'DO_NOT_PRINT'})
        self.assertIn('http=403',text);self.assertIn('POST:git/blobs',text);self.assertNotIn('DO_NOT_PRINT',text)
    def test_untrusted_values_cannot_inject_annotations(self):
        from dr_sync import actions_result_annotation
        text=actions_result_annotation({'status':'bad\n::error::','failed_api_operation':'secret','failed_http_status':'secret'})
        self.assertNotIn('secret',text);self.assertNotIn('\n',text)

if __name__=='__main__':unittest.main()
