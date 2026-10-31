"""Regression tests for strict, fail-closed capability routing inputs."""
import unittest

from ops.vyomaraj.capability_fabric import (
    authorize_capabilities,
    capability_domains,
)


class CapabilityFabricInputValidationTests(unittest.TestCase):
    def test_valid_set_and_frozenset_route(self):
        self.assertIn("matiman", capability_domains({"reasoning"}))
        self.assertIn("gatiman", capability_domains(frozenset({"execution"})))

    def test_unknown_capability_is_not_silently_ignored(self):
        with self.assertRaisesRegex(ValueError, "unsupported capability"):
            capability_domains({"reasoning", "unknown.capability"})
        with self.assertRaisesRegex(ValueError, "unsupported capability"):
            authorize_capabilities(
                {"reasoning", "unknown.capability"}, True,
            )

    def test_required_capabilities_must_be_a_set_or_frozenset(self):
        for value in ("reasoning", ["reasoning"], None, 7):
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    capability_domains(value)

    def test_capability_tokens_must_be_non_empty_canonical_strings(self):
        malformed = (
            {""},
            {" reasoning"},
            {"reasoning "},
            {"reasoning planning"},
            {"reasoning\nplanning"},
            {7},
            {None},
        )
        for value in malformed:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    capability_domains(value)

    def test_empty_request_does_not_produce_a_route_or_authorization(self):
        self.assertEqual(capability_domains(set()), [])
        with self.assertRaisesRegex(ValueError, "no registered capability"):
            authorize_capabilities(set(), True)

    def test_truthy_non_boolean_owner_claim_is_rejected(self):
        for value in ("true", 1, [], {"approved": True}):
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    authorize_capabilities({"reasoning"}, value)

    def test_owner_denial_remains_fail_closed(self):
        with self.assertRaisesRegex(PermissionError, "owner authorization"):
            authorize_capabilities({"reasoning"}, False)

    def test_risk_and_step_up_flags_must_be_actual_booleans(self):
        for kwargs in (
            {"high_risk": "false"},
            {"high_risk": 1},
            {"step_up_confirmed": "true"},
            {"step_up_confirmed": 1},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(TypeError):
                    authorize_capabilities({"execution"}, True, **kwargs)

    def test_high_risk_requires_explicit_boolean_step_up(self):
        with self.assertRaisesRegex(PermissionError, "step-up"):
            authorize_capabilities(
                {"execution"}, True, high_risk=True, step_up_confirmed=False,
            )
        self.assertIn(
            "gatiman",
            authorize_capabilities(
                {"execution"}, True, high_risk=True, step_up_confirmed=True,
            ),
        )

    def test_returned_domains_remain_routing_metadata_not_permission_grants(self):
        self.assertEqual(
            authorize_capabilities({"reasoning"}, True),
            ["matiman"],
        )


if __name__ == "__main__":
    unittest.main()
