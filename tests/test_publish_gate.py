import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "ops/vyomaraj/publish-gate.sh"


class PublishGateTests(unittest.TestCase):
    def test_gate_runs_offline_verification_and_never_deploys(self):
        script = GATE.read_text(encoding="utf-8")
        self.assertIn("run_offline_suites.py --ci", script)
        self.assertIn("capability_status.py test", script)
        self.assertIn("PUBLISH GATE: PASS (static public-preview scope only)", script)
        self.assertIn("PRODUCTION STATUS: BLOCKED", script)
        self.assertNotIn("git push", script)
        self.assertNotIn("gh release", script)
        self.assertNotIn("curl ", script)

    def test_no_argument_can_bypass_production_block_or_deploy(self):
        script = GATE.read_text(encoding="utf-8")
        self.assertIn("Unsupported option", script)
        self.assertIn("it has no deploy or production override", script)
        self.assertIn("No deployment was performed", script)


if __name__ == "__main__":
    unittest.main()
