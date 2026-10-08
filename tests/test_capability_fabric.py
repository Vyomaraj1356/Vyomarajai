"""Capability routing and the two authorization refusals.

Collected by `unittest discover` as well as pytest. These were module-level pytest
functions, which `unittest discover` does not collect, so the offline suite — the gate that
runs in every workflow, including the DR one — was not executing them. Only the pytest-based
`engineering-foundation` job was, and that job had been failing for an unrelated reason, so
in practice nothing enforced these refusals. Assertions are unchanged; only the wrapper is.
"""
import unittest

from ops.vyomaraj.capability_fabric import authorize_capabilities, capability_domains


class CapabilityFabricRoutingTests(unittest.TestCase):
    def test_capability_domains_route(self):
        self.assertIn("matiman", capability_domains({"reasoning"}))
        self.assertIn("shrutiman", capability_domains({"research"}))
        self.assertIn("ketuman", capability_domains({"monitoring"}))
        self.assertIn("gatiman", capability_domains({"execution"}))
        self.assertIn("dhritiman", capability_domains({"recovery"}))

    def test_owner_authorization_required(self):
        with self.assertRaises(PermissionError):
            authorize_capabilities({"reasoning"}, False)

    def test_high_risk_requires_step_up(self):
        with self.assertRaises(PermissionError):
            authorize_capabilities({"execution"}, True, high_risk=True)


if __name__ == "__main__":
    unittest.main()
