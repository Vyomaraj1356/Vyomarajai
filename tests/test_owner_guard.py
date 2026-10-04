"""Unit tests for owner approval claim policy; no secrets or live provider required."""
import os
import unittest
from unittest.mock import patch

from ops.shriyantra.owner_guard import AuthorizationDenied, canonical_target, validate_claims


class OwnerGuardTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "VYOMARAJ_OWNER_SUBJECT": "owner-test-id",
            "VYOMARAJ_AUTH_ISSUER": "shriyantra-control-plane",
            "VYOMARAJ_AUTH_AUDIENCE": "shriyantra",
            "VYOMARAJ_SECURITY_EPOCH": "epoch-test-1",
        })
        self.env.start()
        self.now = 2_000_000_000
        self.claims = {
            "sub": "owner-test-id", "iss": "shriyantra-control-plane",
            "aud": "shriyantra", "iat": self.now - 10, "exp": self.now + 60,
            "jti": "one-time-test-id", "action": "arena.execute",
            "target": canonical_target("check", "BHARATH", "LOW"),
            "scope": ["arena.execute"], "security_epoch": "epoch-test-1",
            "authn": "webauthn", "step_up": False,
        }

    def tearDown(self):
        self.env.stop()

    def test_valid_owner_approval_claims(self):
        validate_claims(self.claims, action="arena.execute",
                        target=self.claims["target"], required_scope="arena.execute",
                        now=self.now)

    def test_non_owner_is_denied(self):
        claims = dict(self.claims, sub="agent")
        with self.assertRaises(AuthorizationDenied):
            validate_claims(claims, action="arena.execute",
                            target=claims["target"], required_scope="arena.execute",
                            now=self.now)

    def test_wrong_target_is_denied(self):
        with self.assertRaises(AuthorizationDenied):
            validate_claims(self.claims, action="arena.execute", target="different",
                            required_scope="arena.execute", now=self.now)

    def test_stale_security_epoch_is_denied(self):
        claims = dict(self.claims, security_epoch="old-epoch")
        with self.assertRaises(AuthorizationDenied):
            validate_claims(claims, action="arena.execute",
                            target=claims["target"], required_scope="arena.execute",
                            now=self.now)

    def test_privileged_action_requires_step_up(self):
        claims = dict(self.claims, action="user.create", scope=["user.create"])
        with self.assertRaises(AuthorizationDenied):
            validate_claims(claims, action="user.create", target=claims["target"],
                            required_scope="user.create", now=self.now)

    def test_expired_approval_is_denied(self):
        claims = dict(self.claims, exp=self.now - 1)
        with self.assertRaises(AuthorizationDenied):
            validate_claims(claims, action="arena.execute",
                            target=claims["target"], required_scope="arena.execute",
                            now=self.now)


if __name__ == "__main__":
    unittest.main()
