import json
import subprocess
import sys
import unittest
from pathlib import Path

from ops.vyomaraj import agent_change


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"


class AgentChangePlanTests(unittest.TestCase):
    def test_add_plan_is_read_only_and_owner_approval_bound(self):
        before = REGISTRY.read_bytes()
        plan = agent_change.plan_add("FOOD", "FOOD-S99", "Test planning slot")
        self.assertEqual(plan["status"], "PLAN_ONLY_NOT_APPLIED")
        self.assertEqual(plan["target"]["action"], "agent.add")
        self.assertEqual(len(plan["target_sha256"]), 64)
        self.assertTrue(plan["owner_authorization"]["required"])
        self.assertTrue(plan["owner_authorization"]["step_up_required"])
        self.assertFalse(plan["owner_authorization"]["token_checked"])
        self.assertEqual(plan["transaction"]["runtime_mutation_api"], "NOT_CONFIGURED")
        self.assertEqual(plan["effects"], [])
        self.assertEqual(REGISTRY.read_bytes(), before)

    def test_remove_plan_never_deletes_and_preserves_history(self):
        plan = agent_change.plan_remove("FOOD-REF-01", "Owner review required before retirement")
        self.assertEqual(plan["status"], "PLAN_ONLY_NOT_APPLIED")
        self.assertEqual(plan["target"]["action"], "agent.remove")
        self.assertEqual(plan["transaction"]["peer_synchronization"], "NOT_CONFIGURED")
        self.assertIn("Preserve historical records", plan["note"])

    def test_duplicate_or_wrong_category_add_is_rejected(self):
        with self.assertRaisesRegex(agent_change.ChangePlanError, "already exists"):
            agent_change.plan_add("FOOD", "FOOD-REF-01", "Duplicate")
        with self.assertRaisesRegex(agent_change.ChangePlanError, "namespaced"):
            agent_change.plan_add("FOOD", "EDU-S99", "Wrong category")
        with self.assertRaisesRegex(agent_change.ChangePlanError, "not present"):
            agent_change.plan_add("REAL_ESTATE", "REAL_ESTATE-S01", "Not yet in registry")

    def test_name_and_remove_reason_are_required_and_bounded(self):
        with self.assertRaisesRegex(agent_change.ChangePlanError, "printable"):
            agent_change.plan_add("FOOD", "FOOD-S99", "Bad\nName")
        with self.assertRaisesRegex(agent_change.ChangePlanError, "reason"):
            agent_change.plan_remove("FOOD-REF-01", "")
        with self.assertRaisesRegex(agent_change.ChangePlanError, "not present"):
            agent_change.plan_remove("NO-SUCH-AGENT", "Review")

    def test_apply_is_blocked_before_owner_token_consumption_or_mutation(self):
        before = REGISTRY.read_bytes()
        proc = subprocess.run(
            [sys.executable, str(ROOT / "ops/vyomaraj/agent_change.py"), "apply"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 4)
        self.assertIn("transactional mutation", proc.stderr)
        self.assertEqual(REGISTRY.read_bytes(), before)

    def test_registry_validation_is_read_only(self):
        self.assertEqual(agent_change.validate(), 0)


if __name__ == "__main__":
    unittest.main()
