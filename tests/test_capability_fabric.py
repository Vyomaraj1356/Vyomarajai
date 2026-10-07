import copy
import json
import tempfile
import unittest
from pathlib import Path

from ops.vyomaraj import capability_fabric as fabric


class CapabilityFabricTests(unittest.TestCase):
    def test_static_check_is_explicitly_not_runtime_verification(self):
        result = fabric.status()
        self.assertEqual(result["check"], "PASS")
        self.assertEqual(result["capability_domains"], list(fabric.REQUIRED_DOMAINS))
        self.assertFalse(result["permission_grants_inherited"])
        self.assertFalse(result["root_owner_authority_inherited"])
        self.assertEqual(result["runtime_execution"], "NOT_IMPLEMENTED")
        self.assertEqual(result["production_enforcement"], "NOT_VERIFIED")

    def test_non_object_model_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "model.yaml"
            model.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(fabric.FabricError, "must be a JSON object"):
                fabric.load_contract(model_path=model)

    def test_missing_domain_fails_closed(self):
        model, _, registry = fabric.load_contract()
        broken = copy.deepcopy(model)
        broken["domains"].pop()
        with tempfile.TemporaryDirectory() as tmp:
            model_path = Path(tmp) / "model.yaml"
            policy_path = Path(tmp) / "policy.json"
            registry_path = Path(tmp) / "registry.json"
            model_path.write_text(json.dumps(broken), encoding="utf-8")
            policy_path.write_text(json.dumps(json.loads(fabric.KNOWLEDGE_POLICY_PATH.read_text())), encoding="utf-8")
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            with self.assertRaisesRegex(fabric.FabricError, "five canonical"):
                fabric.load_contract(model_path=model_path, policy_path=policy_path, registry_path=registry_path)

    def test_root_authority_cannot_be_inherited_or_delegated(self):
        model, _, registry = fabric.load_contract()
        broken = copy.deepcopy(model)
        broken["authority_boundary"]["root_owner_authority_inherited"] = True
        with tempfile.TemporaryDirectory() as tmp:
            model_path = Path(tmp) / "model.yaml"
            model_path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaisesRegex(fabric.FabricError, "unsafe capability"):
                fabric.load_contract(model_path=model_path, registry_path=fabric.REGISTRY_PATH)

    def test_registry_inheritance_coverage_must_match_registry(self):
        model, policy, registry = fabric.load_contract()
        broken = copy.deepcopy(registry)
        broken["shared_capability_inheritance"]["current_coverage"]["agent_count"] += 1
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "registry.json"
            registry_path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaisesRegex(fabric.FabricError, "capability reference is missing, stale, or unsafe"):
                fabric.load_contract(registry_path=registry_path)

    def test_unknown_entity_type_and_unsafe_entity_id_are_rejected(self):
        with self.assertRaisesRegex(fabric.FabricError, "unsupported entity type"):
            fabric.resolve("service_account", "safe-id")
        with self.assertRaisesRegex(fabric.FabricError, "unsupported characters"):
            fabric.resolve("content", "../secret")

    def test_reference_resolver_does_not_write_files(self):
        before = {path: path.read_bytes() for path in (
            fabric.MODEL_PATH, fabric.KNOWLEDGE_POLICY_PATH, fabric.REGISTRY_PATH,
            fabric.SHRIYANTRA_REGISTRY_PATH,
        )}
        fabric.resolve("category", "FOOD")
        after = {path: path.read_bytes() for path in before}
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
