"""Unit tests for owner approval claim policy; no secrets or live provider required."""
import os
import tempfile
import unittest
from unittest.mock import patch

from ops.shriyantra.owner_guard import (
    AuthorizationDenied, canonical_action_target, canonical_target,
    consume_approval_jti, require_owner_approval, validate_claims,
)


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

    def test_canonical_action_target_binds_action_and_stable_json_payload(self):
        payload = {"item_id": "comics-monsoon", "decision": "approve"}
        target = canonical_action_target("approval.decide", payload)
        self.assertEqual(target, canonical_action_target(
            "approval.decide", {"decision": "approve", "item_id": "comics-monsoon"},
        ))
        self.assertNotEqual(target, canonical_action_target("approval.decide", {
            "item_id": "comics-monsoon", "decision": "reject",
        }))
        self.assertNotEqual(target, canonical_action_target("research.run", payload))

    def test_http_approval_is_request_scoped_not_taken_from_process_environment(self):
        with patch.dict(os.environ, {"VYOMARAJ_AUTHZ_TOKEN": "ambient-process-token"}):
            with patch("ops.shriyantra.owner_guard.verify_owner_approval", return_value=self.claims) as verify:
                with patch("ops.shriyantra.owner_guard.consume_approval_jti"):
                    require_owner_approval(
                        action="arena.execute", target=self.claims["target"],
                        required_scope="arena.execute", token="request-bearer-token",
                    )
            self.assertEqual(verify.call_args.args[0], "request-bearer-token")

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

    def test_owner_queue_and_change_desk_decisions_require_step_up(self):
        for action in ("approval.decide", "upgrade.approve", "upgrade.report_failure"):
            with self.subTest(action=action):
                claims = dict(self.claims, action=action, scope=[action], step_up=False)
                with self.assertRaises(AuthorizationDenied):
                    validate_claims(claims, action=action, target=claims["target"],
                                    required_scope=action, now=self.now)
                claims["step_up"] = True
                validate_claims(claims, action=action, target=claims["target"],
                                required_scope=action, now=self.now)

    def test_agent_registry_mutations_require_step_up(self):
        privileged_actions = (
            "agent.add", "agent.remove", "agent.rename", "agent.move", "agent.permission.change",
        )
        for action in privileged_actions:
            with self.subTest(action=action):
                claims = dict(self.claims, action=action, scope=[action], step_up=False)
                with self.assertRaises(AuthorizationDenied):
                    validate_claims(claims, action=action, target=claims["target"],
                                    required_scope=action, now=self.now)
                claims["step_up"] = True
                validate_claims(claims, action=action, target=claims["target"],
                                required_scope=action, now=self.now)

    def test_expired_approval_is_denied(self):
        claims = dict(self.claims, exp=self.now - 1)
        with self.assertRaises(AuthorizationDenied):
            validate_claims(claims, action="arena.execute",
                            target=claims["target"], required_scope="arena.execute",
                            now=self.now)

    def test_approval_jti_can_only_be_consumed_once(self):
        with tempfile.TemporaryDirectory() as replay_dir:
            with patch.dict(os.environ, {"VYOMARAJ_AUTHZ_REPLAY_DIR": replay_dir}):
                consume_approval_jti(self.claims)
                with self.assertRaises(AuthorizationDenied):
                    consume_approval_jti(self.claims)


if __name__ == "__main__":
    unittest.main()
