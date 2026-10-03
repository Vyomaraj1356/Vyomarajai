import io
import unittest
from unittest.mock import Mock,patch
from urllib.error import HTTPError,URLError
from dr_sync import GitHub,APIError,CheckError

class Tests(unittest.TestCase):
    def test_transient_read_retry(self):
        client=GitHub('test-only');client.opener=Mock();client.opener.open.side_effect=[URLError('private details'),io.BytesIO(b'{"ok":true}')]
        with patch('dr_sync.time.sleep') as sleep:self.assertEqual(client.request('GET','repos/example/repo'),{'ok':True})
        self.assertEqual(client.opener.open.call_count,2);sleep.assert_called_once_with(1)
    def test_write_is_not_retried(self):
        client=GitHub('test-only');client.opener=Mock();client.opener.open.side_effect=URLError('DO_NOT_PRINT')
        with self.assertRaises(CheckError) as e:client.request('POST','repos/example/repo/git/blobs',{})
        self.assertEqual(client.opener.open.call_count,1);self.assertNotIn('DO_NOT_PRINT',str(e.exception))
    def test_403_scope_failure_not_retried(self):
        client=GitHub('test-only');client.opener=Mock();client.opener.open.side_effect=HTTPError('https://api.github.com',403,'private',{},None)
        with self.assertRaises(APIError):client.request('GET','repos/example/repo')
        self.assertEqual(client.opener.open.call_count,1)
    def test_retry_after_too_long_stops(self):
        client=GitHub('test-only');client.opener=Mock();client.opener.open.side_effect=HTTPError('https://api.github.com',429,'private',{'Retry-After':'120'},None)
        with patch('dr_sync.time.sleep') as sleep:
            with self.assertRaises(APIError):client.request('GET','repos/example/repo')
            sleep.assert_not_called()

if __name__=='__main__':unittest.main()
