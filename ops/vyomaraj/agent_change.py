#!/usr/bin/env python3
"""Plan-only guard for registry changes while no authenticated mutation runtime exists.

The module deliberately does not write registry/configuration files, consume owner
tokens, call peers, synchronize DR, or mutate production. Planning is not approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
REBUILD = ROOT / "ops/vyomaraj-core/agents/rebuild_registry.py"
SAFE_ID = re.compile(r"^[A-Z0-9][A-Z0-9_-]{0,79}$")


class ChangePlanError(ValueError):
    pass


def _load_registry(path: Path = REGISTRY) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ChangePlanError("current registry is unavailable or invalid") from exc
    if not isinstance(value, dict):
        raise ChangePlanError("current registry must be a JSON object")
    return value


def _digest(target: dict[str, Any]) -> str:
    raw = json.dumps(target, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _validate_registry(registry: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    category_rows = registry.get("categories")
    heading_rows = registry.get("headings")
    agent_rows = registry.get("agents")
    if not all(isinstance(rows, list) for rows in (category_rows, heading_rows, agent_rows)):
        raise ChangePlanError("registry hierarchy arrays are invalid")
    all_rows = category_rows + heading_rows + agent_rows
    if any(not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]
           for row in all_rows):
        raise ChangePlanError("registry identity set is invalid")
    identities = [row["id"] for row in all_rows]
    if len(identities) != len(set(identities)):
        raise ChangePlanError("registry identity set contains duplicates")
    totals = registry.get("totals")
    if (not isinstance(totals, dict) or totals.get("main_agents") != len(category_rows)
            or totals.get("sub_agents") != len(agent_rows)):
        raise ChangePlanError("registry totals do not match its hierarchy")
    categories = {row["id"]: row for row in category_rows}
    agents = agent_rows
    return categories, agents


def plan_add(category_id: str, agent_id: str, name: str, *, registry_path: Path = REGISTRY) -> dict[str, Any]:
    """Validate a proposed addition and return a deterministic, non-applying plan."""
    registry = _load_registry(registry_path)
    categories, agents = _validate_registry(registry)
    if not SAFE_ID.fullmatch(category_id or ""):
        raise ChangePlanError("category ID is invalid")
    if category_id not in categories:
        raise ChangePlanError("category is not present in the current registry")
    if not SAFE_ID.fullmatch(agent_id or ""):
        raise ChangePlanError("agent ID is invalid")
    if not agent_id.startswith(category_id + "-"):
        raise ChangePlanError("new sub-agent ID must be namespaced under its category")
    if not isinstance(name, str) or not name.strip() or len(name) > 120 or any(ord(char) < 32 for char in name):
        raise ChangePlanError("agent name must be 1-120 printable characters")
    name = name.strip()
    existing_ids = {row.get("id") for row in agents}
    existing_ids.update(row.get("id") for row in registry.get("headings", []) if isinstance(row, dict))
    existing_ids.update(row.get("id") for row in registry.get("categories", []) if isinstance(row, dict))
    if agent_id in existing_ids:
        raise ChangePlanError("agent ID already exists")
    if any(row.get("category_id") == category_id and isinstance(row.get("name"), str)
           and row["name"].strip().casefold() == name.casefold() for row in agents):
        raise ChangePlanError("name already exists in this category; resolve identity before proposing a duplicate")
    target = {"action": "agent.add", "category_id": category_id, "agent_id": agent_id, "name": name}
    return {
        "status": "PLAN_ONLY_NOT_APPLIED",
        "target": target,
        "target_sha256": _digest(target),
        "registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        "owner_authorization": {
            "required": True,
            "step_up_required": True,
            "exact_action_binding_required": True,
            "token_checked": False,
        },
        "transaction": {
            "runtime_mutation_api": "NOT_CONFIGURED",
            "atomic_registry_and_dependency_update": "NOT_IMPLEMENTED",
            "peer_synchronization": "NOT_CONFIGURED",
            "dr_replication": "NOT_VERIFIED",
            "audit_append_and_hash": "NOT_IMPLEMENTED",
            "rollback_and_recovery": "NOT_IMPLEMENTED",
        },
        "effects": [],
        "note": "This is a static plan only. It does not approve, create, rename, move, remove, or activate an agent.",
    }


def plan_remove(agent_id: str, reason: str, *, registry_path: Path = REGISTRY) -> dict[str, Any]:
    """Validate a proposed removal without mutating the current registry."""
    registry = _load_registry(registry_path)
    _, agents = _validate_registry(registry)
    if not SAFE_ID.fullmatch(agent_id or ""):
        raise ChangePlanError("agent ID is invalid")
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 300 or any(ord(char) < 32 for char in reason):
        raise ChangePlanError("a printable, bounded removal reason is required")
    record = next((row for row in agents if row.get("id") == agent_id), None)
    if record is None:
        raise ChangePlanError("agent is not present in the current registry")
    target = {"action": "agent.remove", "agent_id": agent_id, "category_id": record.get("category_id"), "reason": reason.strip()}
    return {
        "status": "PLAN_ONLY_NOT_APPLIED",
        "target": target,
        "target_sha256": _digest(target),
        "registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        "owner_authorization": {
            "required": True,
            "step_up_required": True,
            "exact_action_binding_required": True,
            "token_checked": False,
        },
        "transaction": {
            "runtime_mutation_api": "NOT_CONFIGURED",
            "dependent_state_updates": "NOT_IMPLEMENTED",
            "peer_synchronization": "NOT_CONFIGURED",
            "dr_replication": "NOT_VERIFIED",
            "audit_append_and_hash": "NOT_IMPLEMENTED",
            "rollback_and_recovery": "NOT_IMPLEMENTED",
        },
        "effects": [],
        "note": "Removal remains unapplied. Preserve historical records and dependent content until an owner-authorized transaction is available.",
    }


def validate() -> int:
    """Run deterministic registry validation without applying any changes."""
    try:
        result = subprocess.run([sys.executable, str(REBUILD), "--check"], cwd=ROOT, check=False)
    except OSError as exc:
        print(f"BLOCKED: could not start registry validation: {exc}", file=sys.stderr)
        return 2
    if result.returncode:
        print("BLOCKED: current registry validation failed", file=sys.stderr)
        return result.returncode
    print("AGENT CHANGE VALIDATION: PASS (read-only; mutation API not configured)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="run read-only registry consistency checks")
    add_parser = sub.add_parser("plan-add", help="validate a proposed addition; never applies it")
    add_parser.add_argument("category_id")
    add_parser.add_argument("agent_id")
    add_parser.add_argument("name")
    remove_parser = sub.add_parser("plan-remove", help="validate a proposed removal; never applies it")
    remove_parser.add_argument("agent_id")
    remove_parser.add_argument("reason")
    sub.add_parser("apply", help="always blocked until a transactional runtime is configured")
    args = parser.parse_args(argv)
    if args.command == "validate":
        return validate()
    if args.command == "apply":
        print("BLOCKED: owner-authenticated transactional mutation, dependent-state update, peer sync, DR verification, audit, rollback, and recovery APIs are not configured.", file=sys.stderr)
        return 4
    try:
        result = (plan_add(args.category_id, args.agent_id, args.name)
                  if args.command == "plan-add" else plan_remove(args.agent_id, args.reason))
    except ChangePlanError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
