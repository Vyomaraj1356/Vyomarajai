"""Optional real-signature HTTP integration test; keys are disposable and test-only."""
import base64
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import studio_server as server


HAS_CRYPTOGRAPHY = importlib.util.find_spec('cryptography') is not None


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


@unittest.skipUnless(HAS_CRYPTOGRAPHY, 'install ops/shriyantra/requirements.txt for signed HTTP integration')
class SignedOwnerHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        cls.temp = tempfile.TemporaryDirectory()
        cls.old_store = server.APPROVAL_STORE
        cls.store = server.APPROVAL_STORE_MODULE.ApprovalStore(
            Path(cls.temp.name) / 'approvals.sqlite3'
        )
        server.APPROVAL_STORE = cls.store
        cls.private = Ed25519PrivateKey.generate()
        cls.public_path = Path(cls.temp.name) / 'owner-test-public.pem'
        cls.public_path.write_bytes(cls.private.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        cls.env = patch.dict(os.environ, {
            'VYOMARAJ_OWNER_SUBJECT': 'disposable-http-owner-test',
            'VYOMARAJ_AUTH_ISSUER': 'disposable-shriyantra-issuer-test',
            'VYOMARAJ_AUTH_AUDIENCE': 'shriyantra',
            'VYOMARAJ_SECURITY_EPOCH': 'disposable-epoch',
            'VYOMARAJ_AUTH_PUBLIC_KEY': str(cls.public_path),
            'VYOMARAJ_AUTHZ_TOKEN': 'ambient-token-must-not-be-used-by-http',
        })
        cls.env.start()
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.http.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()
        server.APPROVAL_STORE = cls.old_store
        cls.env.stop()
        cls.temp.cleanup()

    @classmethod
    def signed_token(cls, payload, *, action='approval.decide', scope='approval.decide',
                     jti='http-test-jti', step_up=True):
        now = int(time.time())
        claims = {
            'sub': 'disposable-http-owner-test',
            'iss': 'disposable-shriyantra-issuer-test',
            'aud': 'shriyantra',
            'iat': now,
            'exp': now + 120,
            'jti': jti,
            'action': action,
            'target': server.OWNER_GUARD.canonical_action_target(action, payload),
            'scope': [scope],
            'security_epoch': 'disposable-epoch',
            'authn': 'passkey',
            'step_up': step_up,
        }
        header = {'alg': 'EdDSA', 'typ': 'JWT'}
        first = b64url(json.dumps(header, sort_keys=True, separators=(',', ':')).encode())
        second = b64url(json.dumps(claims, sort_keys=True, separators=(',', ':')).encode())
        signature = cls.private.sign(f'{first}.{second}'.encode('ascii'))
        return f'{first}.{second}.{b64url(signature)}'

    def request(self, body, token=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = urllib.request.Request(
            self.base + '/api/approvals/decide',
            data=json.dumps(body).encode('utf-8'), headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_signed_owner_decision_persists_once_and_replay_is_blocked(self):
        comics = {'item_id': 'comics-monsoon-post-issue', 'decision': 'approve'}
        status, missing = self.request(comics)
        self.assertEqual(status, 401)
        self.assertEqual(missing['required']['action'], 'approval.decide')
        self.assertEqual(self.store.item(comics['item_id'])['status'], 'awaiting_owner')

        token = self.signed_token(comics, jti='same-signed-jti')
        status, result = self.request(comics, token)
        self.assertEqual(status, 200)
        self.assertEqual(result['status'], 'owner_decision_recorded_locally')
        self.assertEqual(result['decided_by'], 'disposable-http-owner-test')
        self.assertTrue(self.store.verify_audit_chain()['valid'])

        # A second valid signature with the same JTI but a different target must still be rejected.
        film = {'item_id': 'film-monsoon-outline', 'decision': 'reject'}
        second_token = self.signed_token(film, jti='same-signed-jti')
        status, replay = self.request(film, second_token)
        self.assertEqual(status, 409)
        self.assertIn('already been used', replay['error'])
        self.assertEqual(self.store.item(film['item_id'])['status'], 'awaiting_owner')
        self.assertEqual(self.store.verify_audit_chain()['event_count'], 1)

    def test_bad_signature_and_wrong_step_up_fail_closed(self):
        body = {'item_id': 'film-monsoon-outline', 'decision': 'approve'}
        token = self.signed_token(body, jti='bad-signature')
        first, second, signature = token.split('.')
        raw = bytearray(base64.urlsafe_b64decode(signature + '=' * (-len(signature) % 4)))
        raw[0] ^= 1
        status, result = self.request(body, f'{first}.{second}.{b64url(bytes(raw))}')
        self.assertEqual(status, 403)
        self.assertEqual(result['error'], 'owner_authorization_denied')
        self.assertEqual(self.store.item(body['item_id'])['status'], 'awaiting_owner')

        no_step_up = self.signed_token(body, jti='no-step-up', step_up=False)
        status, result = self.request(body, no_step_up)
        self.assertEqual(status, 403)
        self.assertIn('step-up', result['detail'])
        self.assertEqual(self.store.verify_audit_chain()['event_count'], 0)


if __name__ == '__main__':
    unittest.main()
