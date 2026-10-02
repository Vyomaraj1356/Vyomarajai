#!/usr/bin/env python3
"""Offline tests for the plan-only experience router."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import orchestrator
import preview_server


class ExperienceOrchestratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config, cls.catalog, cls.registry, cls.policy = orchestrator.load_sources()

    def job(self, **overrides):
        value = {
            "title": "Sample experience",
            "domain_id": "food_menu",
            "experience_mode": "3d",
            "brief": "Create an original, accessible concept for human review.",
        }
        value.update(overrides)
        return value

    def plan(self, job=None):
        return orchestrator.build_plan(
            job or self.job(),
            self.config,
            self.catalog,
            self.registry,
            self.policy,
            created_at="2026-10-02T00:00:00Z",
            plan_id="test-plan",
        )

    def test_every_domain_and_experience_mode_produces_a_safe_plan(self):
        for route in self.config["domain_routes"]:
            for mode_id in self.config["experience_modes"]:
                with self.subTest(domain=route["id"], mode=mode_id):
                    plan = self.plan(self.job(domain_id=route["id"], experience_mode=mode_id))
                    self.assertFalse(plan["execution_enabled"])
                    self.assertEqual(plan["status"], "PLAN_ONLY_REQUIRES_HUMAN_REVIEW")

    def test_catalog_files_exist_and_counts_match(self):
        for pack in self.catalog["packs"]:
            folder = orchestrator.REPO_ROOT / pack["path"]
            self.assertEqual(len(pack["files"]), pack["module_count"])
            for filename in pack["files"]:
                with self.subTest(pack=pack["id"], file=filename):
                    self.assertTrue((folder / filename).is_file())

    def test_canonical_registry_totals_are_preserved(self):
        totals = self.registry["totals"]
        self.assertEqual(len(self.registry["categories"]), 13)
        self.assertEqual(sum(row["sub_agents"] for row in self.registry["categories"]), 133)
        self.assertEqual(sum(row["products"] for row in self.registry["categories"]), 421)
        self.assertEqual(totals["sub_agents"], 133)
        self.assertEqual(totals["products"], 421)

    def test_food_route_connects_registry_and_content_metadata_without_loading_content(self):
        plan = self.plan()
        self.assertEqual(plan["agent_route"]["categories"][0]["id"], "FOOD")
        self.assertIsNone(plan["agent_route"]["categories"][0]["roster_detail"])
        self.assertEqual(plan["agent_route"]["categories"][0]["sub_agents"], 3)
        self.assertEqual(plan["content_route"]["selected_packs"][0]["id"], "food-agent")
        self.assertFalse(plan["content_route"]["source_contents_loaded"])
        self.assertFalse(plan["content_route"]["source_contents_sent_to_llm_or_tools"])

    def test_vehicle_route_does_not_invent_a_specialist(self):
        plan = self.plan(self.job(domain_id="vehicle_configurator"))
        self.assertEqual(plan["agent_route"]["categories"], [])
        self.assertEqual(plan["agent_route"]["mapping_status"], "owner_mapping_required")
        self.assertTrue(any("No canonical specialist" in warning for warning in plan["warnings"]))

    def test_platform_roster_keeps_unmapped_slot_unassigned(self):
        platform = next(row for row in self.registry["categories"] if row["id"] == "PLATFORM")
        detail = orchestrator._roster_detail("PLATFORM", self.registry)
        self.assertEqual(platform["sub_agents"], 20)
        self.assertEqual(len(detail["lanes"]), 19)
        self.assertEqual(detail["unmapped_slot_count"], 1)
        self.assertIsNone(detail["unmapped_slot_id"])

    def test_war_history_route_is_non_operational_and_review_gated(self):
        plan = self.plan(self.job(domain_id="war_history_visualization", experience_mode="ar"))
        self.assertEqual([item["id"] for item in plan["agent_route"]["categories"]], ["WAR"])
        self.assertTrue(plan["safety"]["requires_human_review"])
        self.assertEqual(
            plan["safety"]["weapon_scope"],
            "non_operational_historical_or_fictional_visualization_only",
        )
        self.assertTrue(any("non-operational" in gate for gate in plan["safety"]["approval_gates"]))

    def test_trend_reference_is_never_claimed_verified(self):
        plan = self.plan(self.job(
            domain_id="trend_campaign",
            trend_source="https://example.org/trend",
            trend_observed_at="2026-10-01",
        ))
        self.assertEqual(plan["trend"]["verification_status"], "owner_supplied_unverified")
        trend_tool = next(item for item in plan["tool_routes"] if item["id"] == "trend_source")
        self.assertEqual(trend_tool["status"], "manual_reference_only")
        self.assertFalse(plan["trend"]["live_discovery_enabled"])

    def test_missing_publish_adapter_blocks_publication(self):
        plan = self.plan(self.job(publish_target="YouTube"))
        self.assertEqual(
            plan["publication"]["status"],
            "blocked_adapter_unconfigured_and_owner_approval_required",
        )
        self.assertFalse(plan["publication"]["auto_publish"])
        publisher = next(item for item in plan["tool_routes"] if item["id"] == "publisher")
        self.assertFalse(publisher["execution_enabled"])

    def test_all_visual_adapters_remain_disabled_and_plan_only(self):
        plan = self.plan()
        self.assertFalse(plan["execution_enabled"])
        self.assertEqual(plan["execution_status"], "PLAN_ONLY_NO_VISUAL_TOOL_DISPATCH_EXECUTOR")
        self.assertEqual(plan["adapter_configuration_status"], "incomplete")
        self.assertFalse(plan["required_adapters_ready"])
        self.assertTrue(all(not adapter["execution_enabled"] for adapter in plan["tool_routes"]))
        self.assertFalse(plan["llm"]["provider_call_made"])

    def test_source_policy_is_not_misrepresented_as_deployed(self):
        plan = self.plan()
        self.assertEqual(
            plan["safety"]["source_policy_status"],
            "proposed_owner_policy_specification_not_a_deployed_filter",
        )

    def test_content_readiness_is_kept_separate_and_unreconciled(self):
        plan = self.plan()
        readiness = plan["registry_snapshot"]["content_readiness"]
        self.assertEqual(readiness["active_content_products_reported"], 394)
        self.assertEqual(readiness["placeholder_videos_shared"], 12)
        self.assertEqual(readiness["pending_products_requiring_chapters"], 52)
        self.assertEqual(readiness["planned_products_requiring_chapters"], 5)
        self.assertIn("not reconciled", plan["registry_snapshot"]["content_readiness_reconciliation_status"])

    def test_invalid_output_and_url_are_rejected(self):
        with self.assertRaises(orchestrator.PlanError):
            self.plan(self.job(requested_outputs=["unknown_output"]))
        with self.assertRaises(orchestrator.PlanError):
            self.plan(self.job(trend_source="file:///etc/passwd"))
        with self.assertRaises(orchestrator.PlanError):
            self.plan(self.job(trend_source="https://example.org/trend?token=secret"))
        with self.assertRaises(orchestrator.PlanError):
            self.plan(self.job(trend_observed_at="2026-99-45"))

    def test_unknown_content_pack_is_rejected(self):
        with self.assertRaises(orchestrator.PlanError):
            self.plan(self.job(content_pack_ids=["invented-pack"]))

    def test_preview_server_excludes_jarvis_environment_and_device_files(self):
        self.assertNotIn("/ops/jarvis/jarvis.env", preview_server.ALLOWLIST)
        self.assertNotIn("/ops/jarvis/devices.json", preview_server.ALLOWLIST)
        self.assertNotIn("/ops/jarvis/jarvis-24x7-controller.sh", preview_server.ALLOWLIST)

    def test_every_preview_allowlist_target_exists(self):
        for path, _content_type in preview_server.ALLOWLIST.values():
            self.assertTrue(path.is_file(), path.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
