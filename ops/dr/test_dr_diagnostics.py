import json
import unittest
from dr_diagnostics import diagnose
from dr_sync import APIError, CheckError, GitHub, PRIMARY

class Fake:
    def __init__(self, identity=200, repo=200):
        self.identity=identity; self.repo=repo; self.calls=[]
    def request(self, method,path,body=None):
        self.calls.append((method,path)); assert method=='GET'
        code=self.identity if path=='user' else self.repo
        if code!=200: raise APIError(code)
        if path=='user': return {'id':123,'login':'PRIVATE_LOGIN','token':'DO_NOT_LOG'}
        if '/git/ref/' in path: return {'object':{'sha':'a'*40}}
        return {'full_name':path.removeprefix('repos/')}

class Tests(unittest.TestCase):
    def test_user_success_does_not_authorize_repository(self):
        r=diagnose(Fake(),Fake(repo=404),'owner/secondary')
        self.assertEqual(r['status'],'BLOCKED'); self.assertEqual(r['identity']['status'],'READABLE')
        self.assertEqual(r['secondary_repository']['reason'],'missing_or_hidden_by_permissions')
    def test_installation_identity_403_not_false_read_failure(self):
        r=diagnose(Fake(),Fake(identity=403),'owner/secondary')
        self.assertEqual(r['status'],'READ_ACCESS_CONFIRMED');self.assertFalse(r['write_authorization_verified'])
        self.assertFalse(r['dr_sync_verified'])
    def test_missing_target_not_guessed(self):
        f=Fake();r=diagnose(Fake(),f,'');self.assertEqual(r['status'],'BLOCKED')
        self.assertEqual(f.calls,[('GET','user')])
    def test_no_login_or_body_output(self):
        text=json.dumps(diagnose(Fake(),Fake(),'owner/secondary'))
        self.assertNotIn('PRIVATE_LOGIN',text);self.assertNotIn('DO_NOT_LOG',text)
    def test_401_redacted(self):
        r=diagnose(Fake(),Fake(identity=401,repo=401),'owner/secondary')
        self.assertEqual(r['identity']['reason'],'credential_rejected')
    def test_primary_as_target_rejected(self):
        r=diagnose(Fake(),Fake(),PRIMARY);self.assertEqual(r['secondary_repository']['reason'],'confirmed_target_required')
    def test_invalid_identity_shape_not_success(self):
        f=Fake();f.request=lambda *args:{}
        self.assertEqual(diagnose(Fake(),f,'owner/secondary')['identity']['reason'],'invalid_identity_response')
    def test_invalid_repository_shape_is_redacted(self):
        f=Fake();f.request=lambda *args:['raw private response']
        r=diagnose(Fake(),f,'owner/secondary');self.assertEqual(r['secondary_repository']['reason'],'invalid_response_shape')
        self.assertNotIn('raw private',json.dumps(r))
    def test_user_write_and_external_paths_refused(self):
        for method,path in [('POST','user'),('GET','https://evil.test/user'),('GET','../user')]:
            with self.assertRaises(CheckError):GitHub().request(method,path)

if __name__=='__main__':unittest.main()
