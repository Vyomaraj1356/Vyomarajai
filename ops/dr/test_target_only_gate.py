import unittest
from test_dr_sync import FakeGitHub, TARGET, BLOB, ENV
import dr_sync as dr

class TargetOnlyGateTests(unittest.TestCase):
    def setup_clients(self):
        primary=FakeGitHub(dr.PRIMARY,'source-tree','source-commit')
        secondary=FakeGitHub(TARGET,'old-tree','old-commit')
        original=secondary.request
        def request(method,path,body=None):
            response=original(method,path,body)
            if method=='GET' and '/git/trees/' in path:
                response['tree'].append({'path':'secondary-only.txt','mode':'100644','type':'blob','sha':BLOB})
            return response
        secondary.request=request
        return primary,secondary
    def test_default_blocks_before_any_write(self):
        primary,secondary=self.setup_clients()
        with self.assertRaises(dr.TargetOnlyRemovalRequired) as error:
            dr.execute(TARGET,True,primary,secondary,ENV)
        self.assertEqual(error.exception.count,1)
        self.assertTrue(all(m=='GET' for m,p,b in secondary.calls))
        self.assertEqual(secondary.commit,'old-commit')
    def test_explicit_approval_exact_tree_preserves_history(self):
        primary,secondary=self.setup_clients()
        result=dr.execute(TARGET,True,primary,secondary,{**ENV,'DR_ALLOW_TARGET_ONLY_REMOVAL':'true'})
        self.assertTrue(result['data_match'])
        body=next(b for m,p,b in secondary.calls if m=='POST' and p.endswith('/trees'))
        self.assertNotIn('base_tree',body)
        self.assertEqual([r['path'] for r in body['tree']],['safe.txt'])
        commit=next(b for m,p,b in secondary.calls if m=='POST' and p.endswith('/commits'))
        self.assertEqual(commit['parents'],['old-commit'])
        self.assertEqual(result['transfer']['target_only_files_removed_from_snapshot'],1)
    def test_truthy_nonliteral_not_approval(self):
        for value in ['1','yes','TRUE']:
            primary,secondary=self.setup_clients()
            with self.assertRaises(dr.TargetOnlyRemovalRequired):
                dr.execute(TARGET,True,primary,secondary,{**ENV,'DR_ALLOW_TARGET_ONLY_REMOVAL':value})

if __name__=='__main__':unittest.main()
