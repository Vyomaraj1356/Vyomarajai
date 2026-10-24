"""Regression tests for the owner-approved Podcast → EDU/ENTERTAINMENT taxonomy move."""
import hashlib
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent
REGISTRY = HERE / "AGENT_REGISTRY_CURRENT.json"
LEGACY = CORE / "handover" / "AGENT_CONTENT_REGISTRY_V16_7_24.json"


class CurrentPodcastTaxonomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.legacy_bytes = LEGACY.read_bytes()
        cls.legacy = json.loads(cls.legacy_bytes)

    def test_current_top_level_taxonomy_has_twelve_categories(self):
        ids = [row["id"] for row in self.current["categories"]]
        self.assertEqual(len(ids), 12)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn("PODCAST", ids)
        self.assertEqual(self.current["totals"]["main_agents"], 12)

    def test_platform_category_uses_social_platform_display_name(self):
        row = next(row for row in self.current["categories"] if row["id"] == "PLATFORM")
        self.assertEqual(row["name"], "Social Platform — Social Channels, AI & Monetization")

    def test_all_five_podcast_capabilities_are_reparented_without_id_loss(self):
        expected = {
            "PODCAST-REF-01": ("RESEARCH", "EDU"),
            "PODCAST-REF-02": ("SCRIPT", "ENTERTAINMENT"),
            "PODCAST-REF-03": ("PRODUCE", "ENTERTAINMENT"),
            "PODCAST-REF-04": ("ANALYSIS", "EDU"),
            "PODCAST-REF-05": ("PUBLISH", "ENTERTAINMENT"),
        }
        rows = {row["id"]: row for row in self.current["agents"]
                if row["id"] in expected}
        self.assertEqual(set(rows), set(expected))
        for agent_id, (name, category_id) in expected.items():
            with self.subTest(agent_id=agent_id):
                self.assertEqual(rows[agent_id]["name"], name)
                self.assertEqual(rows[agent_id]["category_id"], category_id)
                self.assertEqual(rows[agent_id]["parent_id"], category_id)
        self.assertFalse(any(row["category_id"] == "PODCAST"
                             for row in self.current["agents"]))

    def test_category_counts_and_serials_are_consistent(self):
        self.assertEqual(self.current["totals"]["sub_agents"], len(self.current["agents"]))
        self.assertEqual(sum(row["sub_agents"] for row in self.current["categories"]),
                         len(self.current["agents"]))
        for category in self.current["categories"]:
            rows = [row for row in self.current["agents"]
                    if row["category_id"] == category["id"]]
            with self.subTest(category=category["id"]):
                self.assertEqual(len(rows), category["sub_agents"])
                self.assertEqual([row["serial"] for row in rows],
                                 list(range(1, len(rows) + 1)))

    def test_legacy_source_and_product_counts_are_preserved_not_guessed(self):
        expected_hash = self.current["source_snapshot_sha256"]
        self.assertEqual(hashlib.sha256(self.legacy_bytes).hexdigest(), expected_hash)
        self.assertTrue(any(row["id"] == "PODCAST"
                            for row in self.legacy["categories"]))
        self.assertEqual(self.legacy["rosters"]["PODCAST"],
                         ["RESEARCH", "SCRIPT", "PRODUCE", "ANALYSIS", "PUBLISH"])
        self.assertEqual(self.current["totals"]["historical_reported_products"], 421)
        self.assertIsNone(self.current["totals"]["active_products"])


if __name__ == "__main__":
    unittest.main()
