"""Runtime capability inheritance for the owner-approved agent registry.

Every registered agent inherits the five capability domains through ShriYantra.
Inheritance grants capability availability, not authority: owner policy, least
privilege, step-up approval, tool policy and provider isolation remain enforced.
"""
from __future__ import annotations

import json
from pathlib import Path

from ops.vyomaraj.capability_fabric import CAPABILITIES

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"

ALL_DOMAINS = tuple(CAPABILITIES)
CATEGORY_RECOMMENDATIONS = {
    "FOOD": ("shrutiman", "matiman", "gatiman"),
    "EDU": ("shrutiman", "matiman", "gatiman"),
    "ASTRO": ("shrutiman", "matiman", "ketuman"),
    "FINANCE": ("matiman", "shrutiman", "ketuman", "dhritiman"),
    "LIFE": ("shrutiman", "matiman", "dhritiman"),
    "BHAKTI": ("shrutiman", "matiman"),
    "SPORTS": ("shrutiman", "matiman", "ketuman", "gatiman"),
    "AGRI": ("shrutiman", "ketuman", "gatiman", "dhritiman"),
    "ENTERTAINMENT": ("shrutiman", "matiman", "gatiman"),
    "PLATFORM": ("matiman", "gatiman", "ketuman", "dhritiman"),
    "TOUR": ("shrutiman", "ketuman", "gatiman"),
    "WAR": ("matiman", "ketuman", "gatiman", "dhritiman"),
    "PODCAST": ("shrutiman", "matiman", "gatiman"),
}

def load_registry(path: Path = REGISTRY) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    agents = data.get("agents")
    if not isinstance(agents, list) or not agents:
        raise ValueError("agent registry contains no agents")
    return data

def inherited_agent_capabilities(path: Path = REGISTRY) -> dict[str, dict]:
    data = load_registry(path)
    result = {}
    for agent in data["agents"]:
        agent_id = agent.get("id")
        category = agent.get("category_id")
        if not agent_id or not category:
            raise ValueError("agent registry contains an invalid agent record")
        recommended = CATEGORY_RECOMMENDATIONS.get(category, ALL_DOMAINS)
        result[agent_id] = {
            "agent_id": agent_id,
            "category_id": category,
            "inherited_domains": list(ALL_DOMAINS),
            "recommended_domains": list(recommended),
            "owner_policy_required": True,
            "high_risk_step_up_required": True,
            "self_elevation_forbidden": True,
            "runtime_status": agent.get("runtime_status", "NOT_VERIFIED"),
        }
    return result

def validate_inheritance(path: Path = REGISTRY) -> dict:
    data = load_registry(path)
    inherited = inherited_agent_capabilities(path)
    expected = len(data["agents"])
    missing = [a.get("id") for a in data["agents"] if a.get("id") not in inherited]
    invalid = [agent_id for agent_id, profile in inherited.items()
               if tuple(profile["inherited_domains"]) != ALL_DOMAINS]
    return {
        "registry_agents": expected,
        "profiles": len(inherited),
        "all_agents_inherit_all_domains": not missing and not invalid,
        "missing_profiles": missing,
        "invalid_profiles": invalid,
    }
