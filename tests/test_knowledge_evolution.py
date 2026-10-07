import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ops.shriyantra.knowledge_evolution import (  # noqa: E402
    KnowledgeContractError,
    load_policy,
    resolve_inheritance,
    validate_knowledge_record,
)


class UniversalKnowledgeEvolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_policy()

    def test_policy_has_all_nine_temporal_layers_in_order(self):
        self.assertEqual(
            [row["id"] for row in self.policy["temporal_model"]["ordered_layers"]],
            [
                "primitive_origin",
                "old",
                "historical_evolution",
                "history",
                "present",
                "current_state",
                "trends",
                "future",
                "possible_futures",
            ],
        )
        self.assertEqual(len(self.policy["temporal_model"]["standard_questions"]), 9)

    def test_registry_and_rag_cag_mag_config_reference_one_shared_policy(self):
        registry = json.loads((ROOT / "config/agents/shriyantra-agent-registry.json").read_text())
        capability = next(
            item for item in registry["shared_capabilities"]
            if item["id"] == "UNIVERSAL_KNOWLEDGE_EVOLUTION"
        )
        self.assertEqual(capability["policy_ref"], self.policy["inheritance"]["policy_ref"])
        self.assertEqual(capability["runtime_status"], self.policy["implementation_status"])
        self.assertTrue(capability["future_entities_inherit_by_default"])
        self.assertFalse(capability["per_entity_copy_required"])
        config = (ROOT / "config/intelligence/shriyantra-rag-cag-mag.yaml").read_text()
        self.assertIn("policy_id: UNIVERSAL_KNOWLEDGE_EVOLUTION_V1", config)
        self.assertIn(self.policy["inheritance"]["policy_ref"], config)
        self.assertIn("runtime_status: reference_contract_not_deployed", config)

    def test_current_and_future_entity_types_resolve_by_reference(self):
        current = resolve_inheritance("agent", "RESEARCH_AGENT", policy=self.policy)
        future = resolve_inheritance("knowledge_domain", "NEW_DOMAIN", policy=self.policy)
        self.assertEqual(current["policy_id"], future["policy_id"])
        self.assertEqual(current["inheritance_status"], "inherited_by_shared_reference")
        self.assertEqual(current["coverage"], "listed_entity_type")
        self.assertEqual(future["coverage"], "future_entity_default")
        self.assertEqual(current["temporal_layers"], future["temporal_layers"])
        self.assertEqual(len(current["standard_questions"]), 9)
        self.assertTrue(current["future_claim_guard"])

    def test_future_claim_cannot_be_labeled_fact(self):
        record = self._record(temporal_layer="future", evidence_class="FACT")
        with self.assertRaisesRegex(KnowledgeContractError, "future-layer claims"):
            validate_knowledge_record(record, policy=self.policy)

    def test_forecast_requires_horizon_method_assumptions_and_sources(self):
        record = self._record(
            temporal_layer="future",
            evidence_class="FORECAST",
            prediction_horizon="illustrative five-year horizon",
            method="illustrative projection method",
            assumptions=["hypothetical assumption"],
        )
        validate_knowledge_record(record, policy=self.policy)
        del record["prediction_horizon"]
        with self.assertRaisesRegex(KnowledgeContractError, "prediction_horizon"):
            validate_knowledge_record(record, policy=self.policy)

    def test_current_verified_state_requires_as_of_time_and_method(self):
        record = self._record(
            temporal_layer="current_state",
            evidence_class="CURRENT_VERIFIED_STATE",
            as_of_utc="2026-10-07T10:00:00Z",
            verification_method="example structural test only",
        )
        validate_knowledge_record(record, policy=self.policy)
        del record["as_of_utc"]
        with self.assertRaisesRegex(KnowledgeContractError, "as_of_utc"):
            validate_knowledge_record(record, policy=self.policy)

    def test_trend_requires_multiple_dated_observations_with_source_lineage(self):
        record = self._record(
            temporal_layer="trends",
            evidence_class="TREND",
            sources=[self._source("source-1"), self._source("source-2")],
            observation_window="illustrative interval",
            supporting_observations=[
                {"observed_at_utc": "2026-10-01T00:00:00Z", "source_id": "source-1"},
                {"observed_at_utc": "2026-10-07T00:00:00Z", "source_id": "source-2"},
            ],
        )
        validate_knowledge_record(record, policy=self.policy)
        record["supporting_observations"] = record["supporting_observations"][:1]
        with self.assertRaisesRegex(KnowledgeContractError, "at least 2"):
            validate_knowledge_record(record, policy=self.policy)

    def test_scenario_requires_conditions_and_assumptions(self):
        record = self._record(
            temporal_layer="possible_futures",
            evidence_class="SCENARIO",
            sources=[],
            conditional_on="a stated hypothetical condition",
            assumptions=["hypothetical assumption"],
        )
        validate_knowledge_record(record, policy=self.policy)
        del record["conditional_on"]
        with self.assertRaisesRegex(KnowledgeContractError, "conditional_on"):
            validate_knowledge_record(record, policy=self.policy)

    def test_source_provenance_requires_retrieval_time_and_access_label(self):
        record = self._record(temporal_layer="history", evidence_class="HISTORICAL_RECORD")
        del record["sources"][0]["retrieved_at_utc"]
        with self.assertRaisesRegex(KnowledgeContractError, "retrieved_at_utc"):
            validate_knowledge_record(record, policy=self.policy)

    def _record(self, *, temporal_layer, evidence_class, sources=None, **extra):
        return {
            "record_id": "structural-test-record",
            "entity_type": "topic",
            "entity_id": "topic.example",
            "claim": "Placeholder claim used only to test record structure.",
            "scope": {"context": "illustrative test fixture"},
            "temporal_layer": temporal_layer,
            "evidence_class": evidence_class,
            "uncertainty": {"level": "explicitly illustrative"},
            "recorded_at_utc": "2026-10-07T10:00:00Z",
            "sources": [self._source("source-1")] if sources is None else sources,
            **extra,
        }

    @staticmethod
    def _source(source_id):
        return {
            "source_id": source_id,
            "source_ref": "https://example.invalid/source",
            "retrieved_at_utc": "2026-10-07T10:00:00Z",
            "access_label": "public-test-fixture",
        }


if __name__ == "__main__":
    unittest.main()
