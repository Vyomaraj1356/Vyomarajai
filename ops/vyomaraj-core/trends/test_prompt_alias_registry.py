import json
import tempfile
import unittest
from pathlib import Path

import prompt_alias_registry


class PromptAliasRegistryTests(unittest.TestCase):
    def test_seed_is_valid_and_not_claimed_live(self):
        self.assertEqual(prompt_alias_registry.validate(), [])
        data = json.loads(prompt_alias_registry.DEFAULT.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "CANDIDATE_ALIASES_NOT_RUNTIME_VERIFIED")
        self.assertGreaterEqual(len(data["aliases"]), 50)

    def test_duplicate_alias_is_rejected(self):
        data = {"schema_version": 1, "status": "CANDIDATE_ALIASES_NOT_RUNTIME_VERIFIED",
                "aliases": [["MindMap", "x", "one"], ["/mindmap", "y", "two"]]}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "aliases.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertTrue(any("duplicate normalized alias" in x for x in prompt_alias_registry.validate(path)))


if __name__ == "__main__":
    unittest.main()
