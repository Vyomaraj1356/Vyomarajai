import json
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
AGENTS=ROOT/"ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
OWN=ROOT/"ops/vyomaraj-core/agents/CONTENT_OWNERSHIP_CURRENT.json"

class ContentAlignmentMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads(AGENTS.read_text())
        self.ownership=json.loads(OWN.read_text())

    def test_all_counted_active_slots_are_named(self):
        active=[a for a in self.registry["agents"] if a.get("counted") and a.get("name")]
        unnamed=[a for a in self.registry["agents"] if a.get("counted") and not a.get("name") and a.get("name_status")!="MERGED_INTO_EDU-S10_DATA_PRESERVED"]
        self.assertEqual(self.registry["totals"]["sub_agents"],153)
        self.assertEqual(len(active),151)
        self.assertEqual(unnamed,[])

    def test_education_merge_preserves_legacy_ids(self):
        for legacy in ("EDU-S11","EDU-S12"):
            a=next(x for x in self.registry["agents"] if x["id"]==legacy)
            self.assertEqual(a["merge_target_id"],"EDU-S10")
            self.assertEqual(a["name_status"],"MERGED_INTO_EDU-S10_DATA_PRESERVED")

    def test_education_alignment(self):
        names={x["id"]:x["name"] for x in self.registry["agents"]}
        self.assertEqual(names["EDU-S8"],"Metals, Numismatics, Stamps & Collectibles")
        self.assertEqual(names["EDU-S13"],"Ancient Scripts, Epigraphy & Knowledge Transmission")

    def test_wit_hasya_expansion(self):
        names={x["id"]:x["name"] for x in self.registry["agents"]}
        self.assertIn("Satire",names["ENT-WIT-S1"])
        self.assertIn("Kavi Sammelan",names["ENT-HASYA-S1"])
        self.assertIn("published", " ".join(self.registry["agents"][next(i for i,a in enumerate(self.registry["agents"]) if a["id"]=="ENT-HASYA-S1")].get("content_requirements",[])).lower())

    def test_maintenance_command_files_exist(self):
        for p in [
            ROOT/"config/maintenance/CONTENT_ALIGNMENT_CLEANING_POLICY_v1.0.yaml",
            ROOT/"config/maintenance/VOICE_CONTENT_ALIGNMENT_COMMANDS_v1.0.yaml",
            ROOT/"ops/vyomaraj/maintenance/content_alignment_cleaner.py",
            ROOT/"ops/vyomaraj/maintenance/run-content-alignment.sh",
            ROOT/".github/workflows/vyomaraj-content-alignment.yml",
        ]:
            self.assertTrue(p.exists(),str(p))

if __name__=="__main__":
    unittest.main()
