"""Shared capability inheritance: one policy reference, no per-agent permission copies.

This file merges two generations of coverage that briefly replaced one another:

* ``AgentCapabilityInheritanceTests`` is the original ``capability_fabric`` contract
  (restored from ``9ee4fbc^``). PR #47 overwrote it, and because the replacement used
  bare pytest functions instead of ``unittest.TestCase``, ``unittest discover`` stopped
  collecting this module entirely — the offline suite silently lost the coverage and only
  the pytest-based ``engineering-foundation`` job still ran anything here.
* ``AgentCapabilityInheritanceProfileTests`` keeps the genuinely new coverage PR #47 added
  for ``ops/vyomaraj/agent_capability_inheritance``.

The replacement also asserted ``registry_agents == 168``. The reconciled registry is
13 categories / 128 sub-agents, so that assertion could never pass; 168 is the older
unreconciled claim. Counts below are derived from the registry and pinned to the
canonical totals, so neither a stale literal nor a silent registry edit can slip through.
"""
import json
import unittest
from pathlib import Path

from ops.vyomaraj import capability_fabric as fabric
from ops.vyomaraj.agent_capability_inheritance import (
    ALL_DOMAINS,
    inherited_agent_capabilities,
    validate_inheritance,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
EXPECTED_DOMAINS = ["MATIMAN", "SHRUTIMAN", "KETUMAN", "GATIMAN", "DHRITIMAN"]

# The reconciled owner-approved totals. See ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json.
CANONICAL_CATEGORIES = 13
CANONICAL_SUB_AGENTS = 128


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


class AgentCapabilityInheritanceProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_still_holds_the_reconciled_canonical_totals(self):
        # Guards the literals the two tests below rely on. If the owner-approved registry
        # legitimately changes, this is the single place to update, and the change is explicit.
        self.assertEqual(len(self.registry["categories"]), CANONICAL_CATEGORIES)
        self.assertEqual(len(self.registry["agents"]), CANONICAL_SUB_AGENTS)
        self.assertEqual(self.registry["totals"]["main_agents"], CANONICAL_CATEGORIES)
        self.assertEqual(self.registry["totals"]["sub_agents"], CANONICAL_SUB_AGENTS)

    def test_all_current_agents_inherit_panch_brother_domains(self):
        result = validate_inheritance()
        self.assertEqual(result["registry_agents"], CANONICAL_SUB_AGENTS)
        self.assertEqual(result["profiles"], CANONICAL_SUB_AGENTS)
        self.assertEqual(result["profiles"], len(self.registry["agents"]))
        self.assertTrue(result["all_agents_inherit_all_domains"])
        self.assertEqual(result["missing_profiles"], [])
        self.assertEqual(result["invalid_profiles"], [])

    def test_inherited_capabilities_are_policy_controlled(self):
        profiles = inherited_agent_capabilities()
        self.assertEqual(len(profiles), CANONICAL_SUB_AGENTS)
        for agent_id, profile in profiles.items():
            with self.subTest(agent_id=agent_id):
                self.assertTrue(profile["owner_policy_required"])
                self.assertTrue(profile["high_risk_step_up_required"])
                self.assertTrue(profile["self_elevation_forbidden"])
                self.assertEqual(tuple(profile["inherited_domains"]), ALL_DOMAINS)
                # Inheritance must never be reported as a verified running capability.
                self.assertEqual(profile["runtime_status"], "NOT_VERIFIED")

    def test_recommended_domains_are_a_subset_and_never_an_authority_grant(self):
        for agent_id, profile in inherited_agent_capabilities().items():
            with self.subTest(agent_id=agent_id):
                self.assertTrue(set(profile["recommended_domains"]).issubset(set(ALL_DOMAINS)))
                self.assertNotIn("permissions", profile)
                self.assertNotIn("permission_grants", profile)


if __name__ == "__main__":
    unittest.main()
