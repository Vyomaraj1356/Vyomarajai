import unittest
from datetime import datetime,timezone
import dr_sync as dr

class PinnedApprovalTests(unittest.TestCase):
    def setUp(self):
        self.target='example/dr';self.dst={'commit':'a'*40,'tree':'b'*40}
        self.env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':dr.PRIMARY,'GITHUB_REF':'refs/heads/main'}
        self.policy={'primary':dr.PRIMARY,'secondary':self.target,'one_snapshot_removal_approval':{
            'approved':True,'secondary':self.target,'expected_commit':'a'*40,'expected_tree':'b'*40,'expires_at_utc':'2026-10-04T00:00:00+00:00'}}
        self.now=datetime(2026,10,3,tzinfo=timezone.utc)
    def allowed(self):return dr.pinned_removal_approval(self.target,self.dst,self.env,self.policy,self.now)
    def test_owner_approved_exact_snapshot(self):self.assertTrue(self.allowed())
    def test_changed_snapshot_not_approved(self):
        for key in ['commit','tree']:
            with self.subTest(key=key):
                old=self.dst[key];self.dst[key]='c'*40;self.assertFalse(self.allowed());self.dst[key]=old
    def test_expired_or_naive_approval_not_approved(self):
        for date in ['2026-10-02T00:00:00+00:00','2026-10-04T00:00:00','invalid']:
            self.policy['one_snapshot_removal_approval']['expires_at_utc']=date;self.assertFalse(self.allowed())
    def test_not_review_branch_or_local(self):
        self.env['GITHUB_REF']='refs/heads/arena/01a10140-vyomarajai';self.assertFalse(self.allowed())
        self.env['GITHUB_REF']='refs/heads/main';self.env.pop('GITHUB_ACTIONS');self.assertFalse(self.allowed())
    def test_wrong_target_or_disabled(self):
        self.policy['one_snapshot_removal_approval']['secondary']='other/repo';self.assertFalse(self.allowed())
        self.policy['one_snapshot_removal_approval']['secondary']=self.target
        self.policy['one_snapshot_removal_approval']['approved']=False;self.assertFalse(self.allowed())

if __name__=='__main__':unittest.main()
