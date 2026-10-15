#!/usr/bin/env python3
"""Offline tests for trend_intake; no network, credentials, or publishing."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import trend_intake


class TrendIntakeTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 15, 12, tzinfo=timezone.utc)
        self.record = {
            "source_url": "https://example.test/trend/1",
            "observed_at": "2026-10-15T11:00:00Z",
            "topic": "Regional tea traditions",
            "summary": "Publicly documented trend; research before use.",
            "category": "education",
            "language": "en",
            "adapter": "test-fixture",
            "terms_checked": True,
            "access_authorized": True,
            "scores": {"momentum": 4, "audience_fit": 5, "original_value": 4,
                       "shelf_life": 5, "competition_opportunity": 3,
                       "monetization_fit": 2, "confidence": 4},
        }

    def test_normalizes_and_scores(self):
        item = trend_intake.normalize(self.record, self.now)
        self.assertEqual(item["priority_score_0_to_100"], 77.1)
        self.assertEqual(item["access_gate"], "PASS")
        self.assertFalse(item["content"]["prompt_or_instruction_executed"])
        self.assertFalse(item["content"]["publishing_enabled"])

    def test_high_risk_is_escalated(self):
        item = trend_intake.normalize(dict(self.record, risk_flags=["medical", "privacy"]), self.now)
        self.assertEqual(item["status"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(item["known_escalation_flags"], ["medical", "privacy"])

    def test_missing_source_authorization_is_held(self):
        item = trend_intake.normalize(dict(self.record, terms_checked=False), self.now)
        self.assertEqual(item["access_gate"], "HOLD_SOURCE_ACCESS_UNVERIFIED")
        self.assertEqual(item["status"], "HOLD_SOURCE_ACCESS_UNVERIFIED")

    def test_timezone_and_score_validation(self):
        with self.assertRaises(trend_intake.IntakeError):
            trend_intake.normalize(dict(self.record, observed_at="2026-10-15T11:00:00"), self.now)
        with self.assertRaises(trend_intake.IntakeError):
            trend_intake.normalize(dict(self.record, scores={"momentum": 8}), self.now)

    def test_dry_run_does_not_write_and_write_deduplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            incoming = root / "incoming.jsonl"
            queue = root / "queue.jsonl"
            incoming.write_text(json.dumps(self.record) + "\n", encoding="utf-8")
            report = trend_intake.process(incoming, queue, False, self.now)
            self.assertEqual(report["accepted_new"], 1)
            self.assertFalse(queue.exists())
            report = trend_intake.process(incoming, queue, True, self.now)
            self.assertEqual(report["written"], 1)
            report = trend_intake.process(incoming, queue, True, self.now)
            self.assertEqual(report["duplicates_skipped"], 1)
            self.assertEqual(len(queue.read_text(encoding="utf-8").splitlines()), 1)

    def test_corrupt_existing_queue_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            incoming, queue = root / "incoming.jsonl", root / "queue.jsonl"
            incoming.write_text(json.dumps(self.record), encoding="utf-8")
            queue.write_text("{not-json}\n", encoding="utf-8")
            with self.assertRaises(trend_intake.IntakeError):
                trend_intake.process(incoming, queue, True, self.now)


if __name__ == "__main__":
    unittest.main()
