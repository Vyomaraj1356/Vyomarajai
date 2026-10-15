#!/usr/bin/env python3
"""Validate the user-owned prompt alias seed without executing any alias."""
import argparse
import json
from pathlib import Path

DEFAULT = Path(__file__).with_name("prompt_alias_seed.json")


def validate(path=DEFAULT):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = []
    if data.get("schema_version") != 1:
        problems.append("schema_version must be 1")
    if data.get("status") != "CANDIDATE_ALIASES_NOT_RUNTIME_VERIFIED":
        problems.append("status must preserve the not-runtime-verified state")
    rows = data.get("aliases")
    if not isinstance(rows, list) or not rows:
        problems.append("aliases must be a non-empty list")
        return problems
    seen = set()
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != 3 or not all(isinstance(x, str) and x.strip() for x in row):
            problems.append(f"alias row {index} must contain alias, category and description")
            continue
        alias = row[0].strip().casefold().lstrip("/")
        if alias in seen:
            problems.append(f"duplicate normalized alias: {alias}")
        seen.add(alias)
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT)
    args = parser.parse_args()
    problems = validate(args.file)
    if problems:
        print("\n".join("FAIL: " + item for item in problems))
        return 1
    data = json.loads(args.file.read_text(encoding="utf-8"))
    print(f"OK: {len(data['aliases'])} candidate aliases validated; none are asserted runtime-enabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
