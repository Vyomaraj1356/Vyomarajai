#!/usr/bin/env python3
"""Validate universal and special-domain media capability inheritance.

Deterministic architecture contract only. No external provider calls.
"""
from __future__ import annotations
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json"
CONFIG = ROOT / "config/engineering/SPECIAL_DOMAIN_MEDIA_CAPABILITY_INHERITANCE_v1.0.yaml"
CIV = ROOT / "config/knowledge/CIVILIZATION_KNOWLEDGE_INHERITANCE_v1.0.yaml"

SPECIAL_CATEGORIES = {"FOOD", "EDU", "WAR"}

def validate() -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    civ = yaml.safe_load(CIV.read_text(encoding="utf-8"))
    agents = registry["agents"]
    global_caps = set(cfg["global_inheritance"]["all_authorized_agents"])
    required = {
        "multimodal_reasoning", "image_generation_adapter",
        "video_generation_adapter", "animation_engine",
        "3d_model_generation", "rendering_pipeline"
    }
    errors = []
    if not required.issubset(global_caps):
        errors.append("global multimodal/3D/animation inheritance is incomplete")
    for category in SPECIAL_CATEGORIES:
        if category not in cfg["special_domains"]:
            errors.append(f"missing special-domain profile: {category}")
    for scope in (
        "GLOBAL_WORLD_CIVILIZATIONS",
        "INDIA_CIVILIZATIONS",
        "STATE_AND_REGIONAL_CULTURES",
        "DISTRICT_CITY_TOWN_VILLAGE_LOCAL_HISTORY",
    ):
        if scope not in civ["civilization_scopes"]:
            errors.append(f"missing civilization scope: {scope}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "registry_agents": len(agents),
        "global_capability_contract": sorted(required & global_caps),
        "special_domain_profiles": sorted(cfg["special_domains"]),
        "civilization_scopes": civ["civilization_scopes"],
        "runtime_provider_calls": False,
        "external_renderer_verified": False,
        "errors": errors,
    }

if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, ensure_ascii=False))
