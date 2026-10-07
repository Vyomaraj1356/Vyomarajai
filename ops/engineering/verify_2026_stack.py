#!/usr/bin/env python3
"""Verify the 2026 engineering foundation without claiming external deployment.

This checks dependency availability, configuration invariants, and protocol/runtime
contracts. It does not connect to production providers or execute agent tools.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQ = ROOT / "ops/engineering/requirements-2026.txt"
CFG = ROOT / "config/engineering/ENGINEERING_2026_BASELINE.yaml"\nGEO = ROOT / "config/engineering/GEOSPATIAL_AND_DAILY_STARTUP.yaml"

REQUIRED_MODULES = {
    "cryptography": "security",
    "jsonschema": "schema_validation",
    "yaml": "configuration",
    "temporalio": "durable_execution",
    "opentelemetry": "observability",
    "mcp": "mcp_protocol",
    "a2a": "a2a_protocol",
}

REQUIRED_TEXT = [
    "architecture_lock: true",
    "mutual_backup: true",
    "mutual_recovery: true",
    "split_brain_protection: fencing_and_epoch_required",
    "mcp:",
    "a2a:",
    "implementation: temporal",
    "standard: opentelemetry",
    "policy_as_code: true",
    "retrieved_content_is_untrusted: true",
    "git_replication_is_not_application_dr: true",
    "voice_not_sole_root: true",
]

def main() -> int:
    errors = []
    if not REQ.is_file():
        errors.append(f"missing dependency manifest: {REQ}")
    if not CFG.is_file():
        errors.append(f"missing engineering config: {CFG}")

    for module, purpose in REQUIRED_MODULES.items():
        if importlib.util.find_spec(module) is None:
            errors.append(f"missing Python module: {module} ({purpose})")

    if not GEO.is_file():\n        errors.append(f"missing geospatial/startup config: {GEO}")\n\n    if CFG.is_file():
        text = CFG.read_text(encoding="utf-8")
        for needle in REQUIRED_TEXT:
            if needle not in text:
                errors.append(f"missing required invariant: {needle}")

    result = {
        "baseline": "VYOMARAJ_AI_AGENT_OS_v1.2_ENGINEERING_BASELINE",
        "status": "PASS" if not errors else "FAIL",
        "external_runtime_verified": False,
        "production_credentials_tested": False,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
