"""Unit tests for the read-only Primary/DR diff plan."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops" / "dr"))
from dr_diff_plan import compare_entries  # noqa: E402


def e(path, sha, mode="100644"):
    return {"path": path, "sha": sha, "mode": mode, "type": "blob"}


class DrDiffPlanTests(unittest.TestCase):
    def test_reports_source_only_target_only_and_changed_common_paths(self):
        primary = [e("same.txt", "a"), e("changed.txt", "p"), e("source-only.txt", "s")]
        secondary = [e("same.txt", "a"), e("changed.txt", "d"), e("target-only.txt", "t")]
        src = {"commit": "a" * 40, "tree": "1" * 40}
        dst = {"commit": "b" * 40, "tree": "2" * 40}
        result = compare_entries(primary, secondary, src, dst)
        self.assertEqual(result["status"], "MISMATCH")
        self.assertFalse(result["writes_attempted"])
        self.assertEqual(result["counts"], {
            "primary_only": 1, "secondary_only": 1, "changed_common": 1,
            "unchanged_common": 1, "primary_files": 3, "secondary_files": 3,
        })
        self.assertEqual([x["path"] for x in result["primary_only"]], ["source-only.txt"])
        self.assertEqual([x["path"] for x in result["secondary_only"]], ["target-only.txt"])
        self.assertEqual(result["changed_common"][0]["path"], "changed.txt")
        self.assertEqual(result["changed_common"][0]["primary_sha"], "p")
        self.assertEqual(result["changed_common"][0]["secondary_sha"], "d")

    def test_detects_mode_change(self):
        primary = [e("run.sh", "same", "100755")]
        secondary = [e("run.sh", "same", "100644")]
        result = compare_entries(primary, secondary, {"tree": "1"}, {"tree": "2"})
        self.assertEqual(result["counts"]["changed_common"], 1)

    def test_identical_tree_is_match_and_read_only(self):
        entries = [e("a.txt", "a")]
        snap = {"commit": "a" * 40, "tree": "1" * 40}
        result = compare_entries(entries, entries, snap, snap)
        self.assertEqual(result["status"], "MATCH")
        self.assertEqual(result["counts"]["primary_only"], 0)
        self.assertEqual(result["counts"]["secondary_only"], 0)
        self.assertFalse(result["writes_attempted"])
        self.assertFalse(result["traffic_switched"])


if __name__ == "__main__":
    unittest.main()
