"""Real Ed25519 JWT verifier tests using disposable in-memory test keys only."""
import base64
import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from ops.shriyantra import owner_guard


HAS_CRYPTOGRAPHY = importlib.util.find_spec('cryptography') is not None


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


@unittest.skipUnless(HAS_CRYPTOGRAPHY, 'install ops/shriyantra/requirements.txt for Ed25519 tests')
class Ed25519OwnerTokenTests(unittest.TestCase):
    def setUp(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        self.temp = tempfile.TemporaryDirectory()
        self.key_path = Path(self.temp.name) / 'test-public-key.pem'
        self.private = Ed25519PrivateKey.generate()
        self.key_path.write_bytes(self.private.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        self.environment = patch.dict(os.environ, {
            'VYOMARAJ_OWNER_SUBJECT': 'ephemeral-owner-test',
            'VYOMARAJ_AUTH_ISSUER': 'ephemeral-shriyantra-test',
            'VYOMARAJ_AUTH_AUDIENCE': 'shriyantra',
            'VYOMARAJ_SECURITY_EPOCH': 'test-epoch-only',
            'VYOMARAJ_AUTH_PUBLIC_KEY': str(self.key_path),
        })
        self.environment.start()
        self.payload = {'item_id': 'example-item', 'decision': 'approve'}
        self.target = owner_guard.canonical_action_target('approval.decide', self.payload)

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def token(self, *, target=None, jti='test-jti'):
        now = int(time.time())
        header = {'alg': 'EdDSA', 'typ': 'JWT'}
        claims = {
            'sub': 'ephemeral-owner-test', 'iss': 'ephemeral-shriyantra-test',
            'aud': 'shriyantra', 'iat': now, 'exp': now + 120, 'jti': jti,
            'action': 'approval.decide', 'target': target or self.target,
            'scope': ['approval.decide'], 'security_epoch': 'test-epoch-only',
            'authn': 'passkey', 'step_up': True,
        }
        first = b64url(json.dumps(header, sort_keys=True, separators=(',', ':')).encode())
        second = b64url(json.dumps(claims, sort_keys=True, separators=(',', ':')).encode())
        signing_input = f'{first}.{second}'.encode('ascii')
        signature = b64url(self.private.sign(signing_input))
        return f'{first}.{second}.{signature}'

    def test_valid_request_scoped_ed25519_owner_token(self):
        claims = owner_guard.verify_owner_approval(
            self.token(), action='approval.decide', target=self.target,
            required_scope='approval.decide',
        )
        self.assertEqual(claims['sub'], 'ephemeral-owner-test')
        self.assertEqual(claims['action'], 'approval.decide')
        self.assertTrue(claims['step_up'])

    def test_tampered_signature_and_wrong_target_are_refused(self):
        token = self.token()
        first, second, signature = token.split('.')
        sig = bytearray(base64.urlsafe_b64decode(signature + '=' * (-len(signature) % 4)))
        sig[0] ^= 1
        tampered = f'{first}.{second}.{b64url(bytes(sig))}'
        for candidate, target in ((tampered, self.target),
                                  (self.token(target='0' * 64), self.target)):
            with self.subTest(target=target), self.assertRaises(owner_guard.AuthorizationDenied):
                owner_guard.verify_owner_approval(
                    candidate, action='approval.decide', target=target,
                    required_scope='approval.decide',
                )


if __name__ == '__main__':
    unittest.main()
