#!/usr/bin/env python3
"""Read-only resolver for the shared Panch-Brother capability reference.

This module validates and resolves repository metadata only. It does not create
agents, grant permissions, invoke models/tools, access providers, or prove that a
production Harness enforces the reference.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml"
KNOWLEDGE_POLICY_PATH = ROOT / "config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json"
REGISTRY_PATH = ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
SHRIYANTRA_REGISTRY_PATH = ROOT / "config/agents/shriyantra-agent-registry.json"
MODEL_REF = "config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml"
SHRIYANTRA_REGISTRY_REF = "config/agents/shriyantra-agent-registry.json"
KNOWLEDGE_POLICY_REF = "config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json"
REQUIRED_DOMAINS = ("MATIMAN", "SHRUTIMAN", "KETUMAN", "GATIMAN", "DHRITIMAN")
ENTITY_TYPES = ("category", "agent", "sub_agent", "topic", "content", "chapter", "product")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")


class FabricError(ValueError):
    """Raised when policy references, registry metadata, or entity inputs are unsafe."""


def _read_object(path: Path, description: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FabricError(f"{description} is missing or invalid") from exc
    if not isinstance(value, dict):
        raise FabricError(f"{description} must be a JSON object")
    return value


def load_contract(*, model_path: Path = MODEL_PATH,
                  policy_path: Path = KNOWLEDGE_POLICY_PATH,
                  registry_path: Path = REGISTRY_PATH) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load metadata and fail closed on divergence; no network or state writes occur."""
    model = _read_object(model_path, "Panch-Brother capability model")
    policy = _read_object(policy_path, "Universal Knowledge Fabric policy")
    registry = _read_object(registry_path, "current agent registry")
    shriyantra_registry = _read_object(SHRIYANTRA_REGISTRY_PATH, "ShriYantra shared capability registry")

    domains = model.get("domains")
    if not isinstance(domains, list) or [d.get("id") for d in domains if isinstance(d, dict)] != list(REQUIRED_DOMAINS):
        raise FabricError("exactly the five canonical Panch-Brother capability domains are required")
    inheritance = model.get("inheritance")
    if not isinstance(inheritance, dict):
        raise FabricError("shared capability inheritance reference is missing")
    if (inheritance.get("mode") != "shared_policy_reference"
            or inheritance.get("owner") != "SHRIYANTRA_UNIVERSAL_KNOWLEDGE_FABRIC"
            or inheritance.get("knowledge_policy_ref") != KNOWLEDGE_POLICY_REF
            or inheritance.get("per_entity_copy_required") is not False
            or inheritance.get("all_current_and_future_entities_inherit_by_default") is not True
            or inheritance.get("entity_types") != list(ENTITY_TYPES)):
        raise FabricError("capability inheritance must use the canonical shared Universal Knowledge Fabric reference")

    boundary = model.get("authority_boundary")
    if not isinstance(boundary, dict):
        raise FabricError("capability authority boundary is missing")
    if (boundary.get("capability_domains_are_permissions") is not False
            or boundary.get("permission_grants_inherited") is not False
            or boundary.get("default_decision") != "DENY_UNLESS_EXPLICITLY_GRANTED_BY_OWNER"
            or boundary.get("owner_approval_required_for_grants") is not True
            or boundary.get("agent_self_elevation_allowed") is not False
            or boundary.get("root_owner_authority_inherited") is not False
            or boundary.get("root_owner_authority_delegable_to_peers") is not False
            or boundary.get("external_content_is_authority") is not False):
        raise FabricError("unsafe capability or authority inheritance configuration")

    policy_inheritance = policy.get("inheritance")
    if not isinstance(policy_inheritance, dict) or (
            policy_inheritance.get("mode") != "shared_policy_reference"
            or policy_inheritance.get("policy_ref") != KNOWLEDGE_POLICY_REF
            or policy.get("owner") != "SHRIYANTRA_UNIVERSAL_KNOWLEDGE_FABRIC"
            or policy_inheritance.get("future_entities_inherit_by_default") is not True
            or policy_inheritance.get("per_entity_copy_required") is not False):
        raise FabricError("canonical Universal Knowledge Fabric policy reference is inconsistent")

    configured = [row for row in shriyantra_registry.get("shared_capabilities", [])
                  if isinstance(row, dict) and row.get("id") == "HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL"]
    if (len(configured) != 1
            or configured[0].get("owner") != "SHRIYANTRA_UNIVERSAL_KNOWLEDGE_FABRIC"
            or configured[0].get("policy_ref") != MODEL_REF
            or configured[0].get("knowledge_policy_ref") != KNOWLEDGE_POLICY_REF
            or configured[0].get("inheritance_mode") != "shared_policy_reference"
            or configured[0].get("future_entities_inherit_by_default") is not True
            or configured[0].get("per_entity_copy_required") is not False
            or configured[0].get("permission_grants_inherited") is not False
            or configured[0].get("root_owner_authority_inherited") is not False):
        raise FabricError("ShriYantra shared capability registry reference is missing or unsafe")

    if registry.get("status") != "CURRENT_OWNER_APPROVED_STRUCTURE_not_runtime_inventory":
        raise FabricError("registry status must remain explicitly non-runtime")
    categories = registry.get("categories")
    agents = registry.get("agents")
    if not isinstance(categories, list) or not isinstance(agents, list):
        raise FabricError("registry hierarchy is incomplete")
    totals = registry.get("totals")
    if not isinstance(totals, dict) or totals.get("main_agents") != len(categories) or totals.get("sub_agents") != len(agents):
        raise FabricError("registry totals do not match the current hierarchy")

    knowledge_ref = registry.get("shared_knowledge_inheritance", {})
    if (knowledge_ref.get("policy_ref") != KNOWLEDGE_POLICY_REF
            or knowledge_ref.get("inheritance_mode") != "shared_policy_reference"
            or knowledge_ref.get("current_coverage", {}).get("category_count") != len(categories)
            or knowledge_ref.get("current_coverage", {}).get("agent_count") != len(agents)):
        raise FabricError("registry does not inherit the canonical knowledge policy by reference")

    capability_ref = registry.get("shared_capability_inheritance", {})
    if (capability_ref.get("model_ref") != MODEL_REF
            or capability_ref.get("policy_ref") != KNOWLEDGE_POLICY_REF
            or capability_ref.get("inheritance_mode") != "shared_policy_reference"
            or capability_ref.get("capability_domain_ids") != list(REQUIRED_DOMAINS)
            or capability_ref.get("permission_grants_inherited") is not False
            or capability_ref.get("root_owner_authority_inherited") is not False
            or capability_ref.get("current_coverage", {}).get("category_count") != len(categories)
            or capability_ref.get("current_coverage", {}).get("agent_count") != len(agents)):
        raise FabricError("registry capability reference is missing, stale, or unsafe")

    for agent in agents:
        if not isinstance(agent, dict):
            raise FabricError("invalid registry agent entry")
        if any(key in agent for key in ("capabilities", "capability_domains", "permissions", "root_authority")):
            raise FabricError("individual agent copies or inherited permissions are prohibited")
    return model, policy, registry


def resolve(entity_type: str, entity_id: str, *, model_path: Path = MODEL_PATH,
            policy_path: Path = KNOWLEDGE_POLICY_PATH,
            registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Resolve one entity to the shared policy reference without granting authority."""
    if entity_type not in ENTITY_TYPES:
        raise FabricError("unsupported entity type")
    if not isinstance(entity_id, str) or not SAFE_ID.fullmatch(entity_id):
        raise FabricError("entity ID is empty or contains unsupported characters")
    model, policy, registry = load_contract(
        model_path=model_path, policy_path=policy_path, registry_path=registry_path,
    )
    entity: dict[str, Any] = {"id": entity_id, "type": entity_type, "known_in_registry": False}
    categories = registry["categories"]
    agents = registry["agents"]
    if entity_type == "category":
        match = next((row for row in categories if row.get("id") == entity_id), None)
        if match is None:
            raise FabricError("category is not in the current registry")
        entity["known_in_registry"] = True
    elif entity_type in ("agent", "sub_agent"):
        match = next((row for row in agents if row.get("id") == entity_id), None)
        if match is None:
            raise FabricError("agent is not in the current registry")
        if entity_type == "sub_agent" and match.get("kind") != "sub_agent":
            raise FabricError("entity is not a registered sub-agent")
        entity["known_in_registry"] = True
        entity["category_id"] = match["category_id"]

    domains = [
        {"id": row["id"], "display_name": row["display_name"]}
        for row in model["domains"]
    ]
    return {
        "entity": entity,
        "inherited_capability_domains": domains,
        "inheritance": {
            "owner": model["inheritance"]["owner"],
            "mode": "shared_policy_reference",
            "capability_model_ref": MODEL_REF,
            "shriyantra_registry_ref": SHRIYANTRA_REGISTRY_REF,
            "knowledge_policy_ref": policy["inheritance"]["policy_ref"],
            "future_entities_inherit_by_default": True,
            "per_entity_copy_required": False,
        },
        "authorization": {
            "capability_domains_are_permissions": False,
            "permission_grants_inherited": False,
            "permission_grants": [],
            "owner_approval_required_for_any_grant": True,
            "default_decision": "DENY_UNLESS_EXPLICITLY_GRANTED_BY_OWNER",
            "agent_self_elevation_allowed": False,
            "root_owner_authority_inherited": False,
            "external_content_is_authority": False,
        },
        "execution_status": "METADATA_RESOLUTION_ONLY_NOT_A_RUNNING_AGENT",
        "production_enforcement_status": "NOT_VERIFIED",
    }


def status(*, model_path: Path = MODEL_PATH, policy_path: Path = KNOWLEDGE_POLICY_PATH,
           registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    model, _, registry = load_contract(model_path=model_path, policy_path=policy_path,
                                       registry_path=registry_path)
    return {
        "check": "PASS",
        "scope": "repository metadata only; read-only; no network calls",
        "capability_domains": [row["id"] for row in model["domains"]],
        "category_count": registry["totals"]["main_agents"],
        "sub_agent_count": registry["totals"]["sub_agents"],
        "permission_grants_inherited": False,
        "root_owner_authority_inherited": False,
        "runtime_execution": "NOT_IMPLEMENTED",
        "production_enforcement": "NOT_VERIFIED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="validate shared references and authority boundaries")
    resolve_parser = sub.add_parser("resolve", help="resolve an entity to the shared reference")
    resolve_parser.add_argument("entity_type", choices=ENTITY_TYPES)
    resolve_parser.add_argument("entity_id")
    args = parser.parse_args(argv)
    try:
        result = status() if args.command == "check" else resolve(args.entity_type, args.entity_id)
    except FabricError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "check":
        print("RUNTIME EXECUTION: NOT IMPLEMENTED · PRODUCTION ENFORCEMENT: NOT VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
