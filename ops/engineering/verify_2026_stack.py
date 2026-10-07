#!/usr/bin/env python3
"""Read-only repository inspection for the 2026 Vyomaraj/Jarvis target.

This tool performs static checks only. It intentionally does not check version
numbers, contact external services, reveal environment secrets, start processes,
or interpret configuration as production evidence.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
REBUILD_PATH = ROOT / "ops/vyomaraj-core/agents/rebuild_registry.py"
OWNER_POLICY_PATH = ROOT / "config/security/owner-authority.yaml"
RESILIENCE_PATH = ROOT / "config/resilience/bharath-laxman-hermes.yaml"


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _yaml_section(text: str, name: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(name)}:\s*\n(.*?)(?=^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:\n|$)|\Z)", text)
    return match.group(1) if match else ""


def _has_scalar(text: str, key: str, value: str) -> bool:
    return re.search(rf"(?m)^\s*{re.escape(key)}:\s*{re.escape(value)}\s*(?:#.*)?$", text) is not None


def _builder_check() -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [sys.executable, str(REBUILD_PATH), "--check"], cwd=ROOT,
            text=True, capture_output=True, timeout=60, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, "registry builder could not be checked"
    return proc.returncode == 0, "deterministic registry output matches" if proc.returncode == 0 else "registry builder output is stale or invalid"


def inspect() -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    required = [
        "config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml",
        "config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json",
        "ops/vyomaraj/capability_fabric.py",
        "ops/vyomaraj/agent-change.sh",
        "ops/vyomaraj/process-control.sh",
        "ops/vyomaraj/final-readiness-gate.sh",
        "ops/shriyantra/owner_guard.py",
        "tests/test_capability_fabric.py",
        "tests/test_agent_capability_inheritance.py",
    ]
    missing = [rel for rel in required if not (ROOT / rel).is_file()]
    checks["required_reference_files"] = {"status": "PASS" if not missing else "FAIL", "missing": missing}

    registry = _load_json(REGISTRY_PATH)
    registry_ok = bool(registry and isinstance(registry.get("categories"), list)
                       and isinstance(registry.get("agents"), list)
                       and isinstance(registry.get("totals"), dict)
                       and registry["totals"].get("main_agents") == len(registry["categories"])
                       and registry["totals"].get("sub_agents") == len(registry["agents"]))
    checks["registry_internal_arithmetic"] = {
        "status": "PASS" if registry_ok else "FAIL",
        "main_categories": registry.get("totals", {}).get("main_agents") if registry else None,
        "counted_sub_agents": registry.get("totals", {}).get("sub_agents") if registry else None,
        "historical_reported_products": registry.get("totals", {}).get("historical_reported_products") if registry else None,
    }

    target = {"main_categories": 14, "counted_sub_agents": 153, "historical_reported_products": 421}
    current = checks["registry_internal_arithmetic"]
    additions_present = all(current.get(key) == value for key, value in target.items())
    checks["requested_taxonomy_target"] = {
        "status": "PASS" if additions_present else "BLOCKED",
        "target": target,
        "current": {key: current.get(key) for key in target},
        "detail": "The exact FOOD, EDU, and REAL_ESTATE additions must be reconciled into the current source of truth before its counts change; this checker never infers agent names.",
    }

    owner_text = OWNER_POLICY_PATH.read_text(encoding="utf-8") if OWNER_POLICY_PATH.is_file() else ""
    owner_ok = all((
        re.search(r"(?m)^\s*mode:\s*owner_only\s*$", owner_text),
        re.search(r"(?m)^\s*default_decision:\s*deny_unless_explicitly_granted\s*$", owner_text),
        re.search(r"(?m)^\s*agents_may_self_elevate:\s*false\s*$", owner_text),
        re.search(r"(?m)^\s*arena_is_authority_root:\s*false\s*$", owner_text),
    ))
    checks["owner_authority_policy"] = {
        "status": "PASS" if owner_ok else "FAIL",
        "read_only_static_policy_check": True,
        "owner_guard_present": (ROOT / "ops/shriyantra/owner_guard.py").is_file(),
    }

    resilience_text = RESILIENCE_PATH.read_text(encoding="utf-8") if RESILIENCE_PATH.is_file() else ""
    sync_section = _yaml_section(resilience_text, "sync")
    failover_section = _yaml_section(resilience_text, "failover")
    failback_section = _yaml_section(resilience_text, "failback")
    resilience_safe = all((
        _has_scalar(resilience_text, "runtime_activation_enabled", "false"),
        _has_scalar(sync_section, "enabled", "false"),
        _has_scalar(failover_section, "enabled", "false"),
        _has_scalar(failover_section, "automatic", "false"),
        _has_scalar(failback_section, "enabled", "false"),
        _has_scalar(failback_section, "automatic", "false"),
    ))
    checks["peer_and_dr_activation"] = {
        "status": "PASS" if resilience_safe else "FAIL",
        "configuration_activation_disabled": resilience_safe,
        "runtime_peer_connection": "NOT_VERIFIED",
        "production_failover": "NOT_VERIFIED",
    }

    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from ops.vyomaraj.capability_fabric import status as capability_status
        cap = capability_status()
        cap_ok = (cap.get("check") == "PASS" and cap.get("runtime_execution") == "NOT_IMPLEMENTED"
                  and cap.get("production_enforcement") == "NOT_VERIFIED"
                  and cap.get("root_owner_authority_inherited") is False)
    except Exception:
        cap = {}
        cap_ok = False
    checks["shared_capability_fabric"] = {
        "status": "PASS" if cap_ok else "FAIL",
        "runtime_execution": cap.get("runtime_execution", "UNKNOWN"),
        "production_enforcement": cap.get("production_enforcement", "UNKNOWN"),
        "root_owner_authority_inherited": cap.get("root_owner_authority_inherited", "UNKNOWN"),
    }

    builder_ok, builder_detail = _builder_check()
    checks["deterministic_registry_builder"] = {"status": "PASS" if builder_ok else "FAIL", "detail": builder_detail}

    publish_gate = ROOT / "ops/vyomaraj/publish-gate.sh"
    gate_text = publish_gate.read_text(encoding="utf-8") if publish_gate.is_file() else ""
    no_deploy_gate = ("PUBLISH GATE: PASS (static public-preview scope only)" in gate_text
                      and "PRODUCTION STATUS: BLOCKED" in gate_text
                      and "No deployment was performed" in gate_text)
    checks["publish_gate_boundary"] = {"status": "PASS" if no_deploy_gate else "FAIL", "deployment_performed": False}

    statuses = [row["status"] for row in checks.values()]
    static_ok = all(status == "PASS" for status in statuses if status != "BLOCKED")
    blockers = [name for name, row in checks.items() if row["status"] == "BLOCKED"]
    failures = [name for name, row in checks.items() if row["status"] == "FAIL"]
    return {
        "schema_version": 1,
        "scope": "read-only repository inspection; no version gates; no network; no processes started or changed",
        "static_inspection": "PASS" if static_ok else "FAIL",
        "readiness": "BLOCKED" if blockers or failures else "STATIC_ONLY_NOT_PRODUCTION_VERIFIED",
        "checks": checks,
        "blockers": blockers + failures,
        "production_status": "NOT_VERIFIED",
        "no_live_connections_claimed": True,
        "owner_approval": "REQUIRED_FOR_PRIVILEGED_ACTIONS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="exit non-zero only for failed static invariants")
    modes.add_argument("--status", action="store_true", help="print static and blocked-runtime status")
    args = parser.parse_args(argv)
    result = inspect()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["static_inspection"] != "PASS":
        return 2
    if args.status:
        return 0
    print("STATIC REPOSITORY CHECK: PASS; REQUESTED INTEGRATIONS/PRODUCTION: BLOCKED OR NOT VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
