import unittest
from recovery_plan import plan
from dr_sync import PRIMARY,CheckError
from test_dr_sync import FakeGitHub,TARGET

class Tests(unittest.TestCase):
    def test_reverse_review_has_no_writes(self):
        p=FakeGitHub(PRIMARY,'primary-tree','primary-commit');s=FakeGitHub(TARGET,'secondary-tree','secondary-commit')
        r=plan(TARGET,p,s);self.assertFalse(r['writes_performed']);self.assertFalse(r['automatic_reverse_sync']);self.assertFalse(r['trees_equal'])
        self.assertTrue(all(m=='GET' for m,path,b in p.calls+s.calls))
    def test_missing_target_fails(self):
        with self.assertRaises(CheckError):plan('',None,None)
    def test_unreachable_secondary_is_not_ready(self):
        p=FakeGitHub(PRIMARY,'p','p');s=FakeGitHub(TARGET,'s','s');s.fail_status=404
        with self.assertRaises(CheckError):plan(TARGET,p,s)

if __name__=='__main__':unittest.main()
