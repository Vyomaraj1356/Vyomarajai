import json
import unittest
from pathlib import Path

from ops.vyomaraj import capability_fabric as fabric


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
EXPECTED_DOMAINS = ["MATIMAN", "SHRUTIMAN", "KETUMAN", "GATIMAN", "DHRITIMAN"]


class AgentCapabilityInheritanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def assert_shared_reference_only(self, resolved):
        self.assertEqual(resolved["inheritance"]["mode"], "shared_policy_reference")
        self.assertEqual(resolved["inheritance"]["owner"], "SHRIYANTRA_UNIVERSAL_KNOWLEDGE_FABRIC")
        self.assertEqual(resolved["inheritance"]["capability_model_ref"], fabric.MODEL_REF)
        self.assertEqual(resolved["inheritance"]["shriyantra_registry_ref"], fabric.SHRIYANTRA_REGISTRY_REF)
        self.assertEqual(resolved["inheritance"]["knowledge_policy_ref"], fabric.KNOWLEDGE_POLICY_REF)
        self.assertEqual([row["id"] for row in resolved["inherited_capability_domains"]], EXPECTED_DOMAINS)
        self.assertFalse(resolved["authorization"]["capability_domains_are_permissions"])
        self.assertFalse(resolved["authorization"]["permission_grants_inherited"])
        self.assertEqual(resolved["authorization"]["permission_grants"], [])
        self.assertTrue(resolved["authorization"]["owner_approval_required_for_any_grant"])
        self.assertFalse(resolved["authorization"]["agent_self_elevation_allowed"])
        self.assertFalse(resolved["authorization"]["root_owner_authority_inherited"])
        self.assertEqual(resolved["execution_status"], "METADATA_RESOLUTION_ONLY_NOT_A_RUNNING_AGENT")
        self.assertEqual(resolved["production_enforcement_status"], "NOT_VERIFIED")

    def test_all_current_categories_and_sub_agents_resolve_through_one_shared_policy(self):
        for category in self.registry["categories"]:
            with self.subTest(entity_type="category", entity_id=category["id"]):
                self.assert_shared_reference_only(fabric.resolve("category", category["id"]))
        for agent in self.registry["agents"]:
            with self.subTest(entity_type="sub_agent", entity_id=agent["id"]):
                self.assert_shared_reference_only(fabric.resolve("sub_agent", agent["id"]))

    def test_future_content_entity_types_inherit_the_reference_not_permissions(self):
        for entity_type in ("topic", "content", "chapter", "product"):
            with self.subTest(entity_type=entity_type):
                resolved = fabric.resolve(entity_type, "future-example-001")
                self.assertFalse(resolved["entity"]["known_in_registry"])
                self.assert_shared_reference_only(resolved)

    def test_policy_is_not_duplicated_on_individual_agent_records(self):
        forbidden = {"shared_capability_inheritance", "capability_domains", "capabilities", "permissions"}
        for agent in self.registry["agents"]:
            self.assertTrue(forbidden.isdisjoint(agent), agent["id"])
        shared = self.registry["shared_capability_inheritance"]
        self.assertEqual(shared["policy_ref"], fabric.KNOWLEDGE_POLICY_REF)
        self.assertFalse(shared["per_entity_copy_required"])
        self.assertFalse(shared["permission_grants_inherited"])

    def test_arbitrary_agent_cannot_be_invented_by_resolver(self):
        with self.assertRaisesRegex(fabric.FabricError, "not in the current registry"):
            fabric.resolve("sub_agent", "AGENT-DOES-NOT-EXIST")


if __name__ == "__main__":
    unittest.main()
