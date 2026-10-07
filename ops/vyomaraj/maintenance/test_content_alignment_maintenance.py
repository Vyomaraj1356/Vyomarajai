import json
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
AGENTS=ROOT/"ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
OWN=ROOT/"ops/vyomaraj-core/agents/CONTENT_OWNERSHIP_CURRENT.json"

class ContentAlignmentMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads(AGENTS.read_text())
        self.ownership=json.loads(OWN.read_text())

    def test_registry(self):
        self.assertEqual(self.registry["totals"]["sub_agents"],153)
        active=[a for a in self.registry["agents"] if a.get("counted") and a.get("name")]
        self.assertEqual(len(active),151)

    def test_education_merge(self):
        for legacy in ("EDU-S11","EDU-S12"):
            a=next(x for x in self.registry["agents"] if x["id"]==legacy)
            self.assertEqual(a["merge_target_id"],"EDU-S10")

    def test_education_alignment(self):
        names={x["id"]:x["name"] for x in self.registry["agents"]}
        self.assertEqual(names["EDU-S8"],"Metals, Numismatics, Stamps & Collectibles")
        self.assertEqual(names["EDU-S13"],"Ancient Scripts, Epigraphy & Knowledge Transmission")

    def test_media_contract(self):
        self.assertTrue((ROOT/"config/engineering/SPECIAL_DOMAIN_MEDIA_CAPABILITY_INHERITANCE_v1.0.yaml").exists())
        self.assertTrue((ROOT/"config/knowledge/CIVILIZATION_KNOWLEDGE_INHERITANCE_v1.0.yaml").exists())
        self.assertTrue((ROOT/"ops/vyomaraj/media_capability_inheritance.py").exists())

if __name__=="__main__":
    unittest.main()
