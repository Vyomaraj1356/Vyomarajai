import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ops" / "vyomaraj"))
import verify_media_capabilities as media

class MediaCapabilityContractTests(unittest.TestCase):
    def test_contract_valid_and_truthful(self):
        result = media.validate()
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertFalse(result["runtime_tests_performed"])
        self.assertFalse(result["hardware_or_license_presence_verified"])
        self.assertEqual(result["runtime_verified_capabilities"], [])

    def test_contract_has_all_device_media_lanes(self):
        data = json.loads(media.CONTRACT.read_text(encoding="utf-8"))
        ids = {item["id"] for item in data["capabilities"]}
        self.assertTrue(media.REQUIRED_CAPABILITIES.issubset(ids))

    def test_verification_needs_evidence(self):
        original = media.CONTRACT.read_text(encoding="utf-8")
        try:
            data = json.loads(original)
            next(item for item in data["capabilities"] if item["id"] == "dolby_atmos")["runtime_state"] = "verified"
            media.CONTRACT.write_text(json.dumps(data), encoding="utf-8")
            result = media.validate()
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("dolby_atmos", " ".join(result["errors"]))
        finally:
            media.CONTRACT.write_text(original, encoding="utf-8")

if __name__ == "__main__":
    unittest.main()
