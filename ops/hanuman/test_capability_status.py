import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import capability_status


class CapabilityStatusTests(unittest.TestCase):
    def test_five_mapping_entries_are_reported_as_metadata_only(self):
        result = capability_status.inspect_metadata()
        self.assertEqual(result["metadata_status"], "present")
        self.assertEqual(result["capabilities"], list(capability_status.REQUIRED_CAPABILITIES))
        self.assertEqual(result["capability_metadata_resolver"], "present_read_only")
        self.assertEqual(result["runtime_capability_fabric"], "not_implemented")
        self.assertEqual(result["agent_heartbeats"], "not_configured")
        self.assertFalse(result["production_verified"])
        self.assertFalse(result["root_authority_inherited"])

    def test_missing_capability_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "incomplete.json"
            path.write_text(json.dumps({"panchShakti": {"matiman": {}}}), encoding="utf-8")
            with self.assertRaises(capability_status.MetadataError):
                capability_status.inspect_metadata(path)

    def test_heartbeat_and_shift_are_blocked(self):
        for command in ("heartbeat", "shift"):
            with self.subTest(command=command), patch("sys.stderr"):
                self.assertEqual(capability_status.main([command]), 4)


if __name__ == "__main__":
    unittest.main()
