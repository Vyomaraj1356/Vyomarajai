#!/usr/bin/env python3
"""Validate Hanuman capability metadata without claiming running agents or heartbeats."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "hanuman-panch-shakti.json"
REQUIRED_CAPABILITIES = ("matiman", "shrutiman", "ketuman", "gatiman", "dhritiman")


class MetadataError(ValueError):
    pass


def inspect_metadata(path: Path = SOURCE) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise MetadataError("capability mapping is unavailable or invalid JSON") from None
    mapping = data.get("panchShakti") if isinstance(data, dict) else None
    if not isinstance(mapping, dict):
        raise MetadataError("panchShakti capability mapping is missing")
    missing = [name for name in REQUIRED_CAPABILITIES if not isinstance(mapping.get(name), dict)]
    if missing:
        raise MetadataError("required capability entries are missing: " + ", ".join(missing))
    return {
        "schema_version": 1,
        "checked_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "metadata_status": "present",
        "capabilities": list(REQUIRED_CAPABILITIES),
        "runtime_capability_fabric": "not_implemented",
        "agent_heartbeats": "not_configured",
        "social_platform_integrations": "not_connected",
        "production_verified": False,
        "root_authority_inherited": False,
        "source": path.name,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "test", "heartbeat", "shift"), nargs="?", default="status")
    args = parser.parse_args(argv)
    if args.command in ("heartbeat", "shift"):
        print("BLOCKED: no live capability agents, authenticated peer protocol, or owner-authorized failover service is configured.", file=sys.stderr)
        return 4
    try:
        status = inspect_metadata()
    except MetadataError as exc:
        print(f"Hanuman capability metadata: {exc}", file=sys.stderr)
        return 1
    if args.command == "test":
        print(f"CAPABILITY METADATA CHECK: PASS ({len(status['capabilities'])} mappings present)")
        print("RUNTIME: NOT IMPLEMENTED · HEARTBEATS: NOT CONFIGURED · PRODUCTION: NOT VERIFIED")
        return 0
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
