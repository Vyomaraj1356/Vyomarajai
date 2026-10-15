#!/usr/bin/env python3
"""Safe, offline-first intake and scoring for approved Vyomaraj trend adapters.

Input is JSONL emitted by an authorized API/feed connector. This tool does not
browse, scrape, call AI providers, publish content, or execute captured prompts.
Dry-run is the default; --write only appends review-queue records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCORE_FIELDS = (
    "momentum", "audience_fit", "original_value", "shelf_life",
    "competition_opportunity", "monetization_fit", "confidence",
)
RISK_FIELDS = {
    "medical", "financial", "legal", "minors", "privacy", "tragedy",
    "allegations", "misinformation", "copyright", "harassment", "election",
}
REQUIRED = ("source_url", "observed_at", "topic", "summary", "category", "language")


class IntakeError(ValueError):
    pass


def parse_time(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise IntakeError("observed_at must be an ISO-8601 timestamp with timezone") from None
    if dt.tzinfo is None:
        raise IntakeError("observed_at must include a timezone")
    return dt.astimezone(timezone.utc)


def stable_id(record: dict[str, Any]) -> str:
    # Avoid treating an untrusted remote ID as an authoritative queue key.
    material = "|".join((
        str(record.get("source_url", "")).strip(),
        str(record.get("topic", "")).strip().casefold(),
        parse_time(str(record.get("observed_at", ""))).date().isoformat(),
    ))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def normalize(record: dict[str, Any], now: datetime) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise IntakeError("each JSONL line must be a JSON object")
    missing = [key for key in REQUIRED if not isinstance(record.get(key), str) or not record[key].strip()]
    if missing:
        raise IntakeError("missing required non-empty fields: " + ", ".join(missing))
    observed = parse_time(record["observed_at"])
    if observed > now:
        raise IntakeError("observed_at cannot be in the future")
    scores = record.get("scores", {})
    if not isinstance(scores, dict):
        raise IntakeError("scores must be an object with values from 0 to 5")
    clean_scores = {}
    for field in SCORE_FIELDS:
        value = scores.get(field, 0)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 5:
            raise IntakeError(f"scores.{field} must be a number from 0 to 5")
        clean_scores[field] = round(float(value), 2)
    risks = record.get("risk_flags", [])
    if not isinstance(risks, list) or any(not isinstance(x, str) for x in risks):
        raise IntakeError("risk_flags must be a list of strings")
    risks = sorted({x.strip().casefold() for x in risks if x.strip()})
    known_risks = sorted(set(risks) & RISK_FIELDS)
    # Risk terms from an adapter are labels only, never instructions.
    score = round(sum(clean_scores.values()) / len(SCORE_FIELDS) * 20, 1)
    access_ok = record.get("terms_checked") is True and record.get("access_authorized") is True
    status = "HOLD_SOURCE_ACCESS_UNVERIFIED" if not access_ok else ("HUMAN_REVIEW_REQUIRED" if known_risks else "REVIEW_QUEUE")
    return {
        "schema_version": 1,
        "record_id": stable_id(record),
        "record_type": str(record.get("record_type", "trend")).strip().casefold(),
        "status": status,
        "captured_at": now.isoformat().replace("+00:00", "Z"),
        "source": {
            "url": record["source_url"].strip(),
            "observed_at": observed.isoformat().replace("+00:00", "Z"),
            "adapter": str(record.get("adapter", "unspecified")).strip()[:100],
            "terms_checked": record.get("terms_checked") is True,
            "access_authorized": record.get("access_authorized") is True,
        },
        "topic": record["topic"].strip()[:300],
        "summary": record["summary"].strip()[:3000],
        "category": record["category"].strip()[:100],
        "region": str(record.get("region", "unspecified")).strip()[:100],
        "language": record["language"].strip()[:40],
        "scores_0_to_5": clean_scores,
        "priority_score_0_to_100": score,
        "risk_flags": risks,
        "known_escalation_flags": known_risks,
        "access_gate": "PASS" if access_ok else "HOLD_SOURCE_ACCESS_UNVERIFIED",
        "next_action": "human review; verify provenance, source terms, originality and claims",
        "content": {
            "prompt_or_instruction_executed": False,
            "publishing_enabled": False,
            "external_actions_enabled": False,
        },
    }


def load_existing(path: Path) -> set[str]:
    ids: set[str] = set()
    if not path.exists():
        return ids
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if isinstance(item, dict) and isinstance(item.get("record_id"), str):
                ids.add(item["record_id"])
        except json.JSONDecodeError:
            raise IntakeError(f"existing queue has invalid JSON on line {number}; refusing to append") from None
    return ids


def process(input_path: Path, output_path: Path, write: bool, now: datetime) -> dict[str, Any]:
    try:
        raw_lines = input_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise IntakeError(f"cannot read input file ({type(exc).__name__})") from None
    existing = load_existing(output_path)
    batch_ids: set[str] = set()
    accepted = []
    errors = []
    duplicates = 0
    for number, line in enumerate(raw_lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            item = normalize(record, now)
            if item["record_id"] in existing or item["record_id"] in batch_ids:
                duplicates += 1
                continue
            batch_ids.add(item["record_id"])
            accepted.append(item)
        except (json.JSONDecodeError, IntakeError) as exc:
            errors.append({"line": number, "error": str(exc)})
    if write and accepted:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as handle:
            for item in accepted:
                handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    return {
        "mode": "write" if write else "dry_run",
        "input_records": sum(bool(line.strip()) for line in raw_lines),
        "accepted_new": len(accepted),
        "duplicates_skipped": duplicates,
        "invalid_records": len(errors),
        "written": len(accepted) if write else 0,
        "review_records": accepted if not write else [],
        "errors": errors,
        "external_calls": 0,
        "publishing_actions": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSONL from an authorized adapter")
    parser.add_argument("--output", type=Path, default=Path("var/trend-review-queue.jsonl"))
    parser.add_argument("--write", action="store_true", help="append new records; without this, only dry-run")
    args = parser.parse_args()
    try:
        report = process(args.input, args.output, args.write, datetime.now(timezone.utc))
    except IntakeError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc), "written": 0}), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["invalid_records"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
