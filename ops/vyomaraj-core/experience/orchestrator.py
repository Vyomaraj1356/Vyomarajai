#!/usr/bin/env python3
"""Plan-only router for Vyomaraj/Jarvis experience jobs.

This module reads the canonical agent registry and declarative adapter config. It
never calls image/video/3D/render/publish providers. Optional LLM drafting is
available only as an explicit local CLI action and uses the existing no-tools
Jarvis LLM harness.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, TextIO
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_CONFIG = HERE / "EXPERIENCE_ORCHESTRATOR.json"
DEFAULT_CATALOG = HERE / "CONTENT_CATALOG.json"


class PlanError(ValueError):
    """Safe input or configuration error suitable for a CLI message."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PlanError(f"Could not read JSON configuration: {path.name}") from None
    if not isinstance(value, dict):
        raise PlanError(f"Expected an object in {path.name}.")
    return value


def load_sources(
    config_path: Path = DEFAULT_CONFIG,
    catalog_path: Path = DEFAULT_CATALOG,
    registry_path: Path | None = None,
    policy_path: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    config = read_json(config_path)
    catalog = read_json(catalog_path)
    registry_file = registry_path or (REPO_ROOT / config["system"]["source_agent_registry"])
    policy_file = policy_path or (REPO_ROOT / config["system"]["source_safety_policy"])
    registry = read_json(registry_file)
    policy = read_json(policy_file)
    return config, catalog, registry, policy


def _text(value: Any, field: str, limit: int, required: bool = False) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise PlanError(f"{field} must be text.")
    value = value.strip()
    if "\x00" in value:
        raise PlanError(f"{field} contains an unsupported control character.")
    if len(value) > limit:
        raise PlanError(f"{field} exceeds the {limit}-character limit.")
    if required and not value:
        raise PlanError(f"{field} is required.")
    return value


def _registry_index(registry: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    categories = registry.get("categories")
    if not isinstance(categories, list):
        raise PlanError("The agent registry does not contain a category list.")
    result: dict[str, dict[str, Any]] = {}
    for item in categories:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def _domain_index(config: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    routes = config.get("domain_routes")
    if not isinstance(routes, list):
        raise PlanError("The orchestrator configuration does not contain domain routes.")
    return {
        item["id"]: item
        for item in routes
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _experience_index(config: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    modes = config.get("experience_modes")
    if not isinstance(modes, dict):
        raise PlanError("The orchestrator configuration does not contain experience modes.")
    return {str(key): value for key, value in modes.items() if isinstance(value, dict)}


def _adapter_index(config: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    adapters = config.get("tool_adapters")
    if not isinstance(adapters, list):
        raise PlanError("The orchestrator configuration does not contain tool adapters.")
    return {
        item["id"]: item
        for item in adapters
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _roster_detail(category_id: str, registry: Mapping[str, Any]) -> dict[str, Any] | None:
    roster = registry.get("rosters", {}).get(category_id)
    if roster is None:
        return None
    # Preserve the owner-supplied roster shape exactly; do not manufacture names
    # for ranges, count-only groups, or unmapped slots.
    if isinstance(roster, list):
        return {"shape": "named_list_as_supplied", "items": roster}
    if isinstance(roster, dict):
        if "entries" in roster:
            return {"shape": "partial_entries_as_supplied", **roster}
        if "groups" in roster:
            return {"shape": "grouped_roster_as_supplied", **roster}
        if "lanes" in roster:
            return {"shape": "partial_lanes_as_supplied", **roster}
        return {"shape": "source_object_as_supplied", **roster}
    return None


def _valid_reference_url(value: str) -> bool:
    if not value:
        return True
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.hostname)
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
    )


def _content_pack_index(catalog: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    packs = catalog.get("packs")
    if not isinstance(packs, list):
        raise PlanError("The content catalog does not contain a pack list.")
    return {
        item["id"]: item
        for item in packs
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _selected_content_packs(
    supplied: Any,
    category_ids: list[str],
    catalog: Mapping[str, Any],
) -> list[str]:
    pack_index = _content_pack_index(catalog)
    if supplied is None:
        selected = [
            pack_id
            for pack_id, pack in pack_index.items()
            if set(pack.get("category_ids", [])) & set(category_ids)
        ]
    else:
        if not isinstance(supplied, list) or any(not isinstance(value, str) for value in supplied):
            raise PlanError("content_pack_ids must be a list of catalog pack IDs.")
        selected = list(dict.fromkeys(supplied))
        unknown = [pack_id for pack_id in selected if pack_id not in pack_index]
        if unknown:
            raise PlanError("Unknown content pack ID; select a pack from CONTENT_CATALOG.json.")
    return selected


def _build_content_metadata(pack_ids: list[str], catalog: Mapping[str, Any]) -> list[dict[str, Any]]:
    packs = _content_pack_index(catalog)
    return [
        {
            "id": pack_id,
            "label": packs[pack_id].get("label", pack_id),
            "path": packs[pack_id].get("path"),
            "category_ids": packs[pack_id].get("category_ids", []),
            "files": packs[pack_id].get("files", []),
            "ingestion_mode": packs[pack_id].get("ingestion_mode", "metadata_only_by_default"),
            "source_contents_loaded": False,
            "review_before_external_use": packs[pack_id].get("review_before_external_use", True),
        }
        for pack_id in pack_ids
    ]


def build_plan(
    job: Mapping[str, Any],
    config: Mapping[str, Any],
    catalog: Mapping[str, Any],
    registry: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    created_at: str | None = None,
    plan_id: str | None = None,
) -> dict[str, Any]:
    """Return a validated route manifest. No visual provider or agent is invoked."""
    if not isinstance(job, Mapping):
        raise PlanError("The job must be a JSON object.")

    title = _text(job.get("title"), "title", 120, required=True)
    brief = _text(job.get("brief"), "brief", 4000, required=True)
    audience = _text(job.get("audience"), "audience", 240)
    domain_id = _text(job.get("domain_id"), "domain_id", 80, required=True)
    experience_mode = _text(job.get("experience_mode"), "experience_mode", 40, required=True)
    trend_source = _text(job.get("trend_source"), "trend_source", 500)
    trend_observed_at = _text(job.get("trend_observed_at"), "trend_observed_at", 40)
    publish_target = _text(job.get("publish_target"), "publish_target", 160)

    if trend_source and not _valid_reference_url(trend_source):
        raise PlanError("trend_source must be an HTTP or HTTPS URL without embedded credentials, query, or fragment. It is recorded only, not fetched.")
    if trend_observed_at:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", trend_observed_at):
                raise ValueError
            date.fromisoformat(trend_observed_at)
        except ValueError:
            raise PlanError("trend_observed_at must be a valid YYYY-MM-DD date.") from None

    domains = _domain_index(config)
    if domain_id not in domains:
        raise PlanError("Unknown domain_id; choose a route from EXPERIENCE_ORCHESTRATOR.json.")
    modes = _experience_index(config)
    if experience_mode not in modes:
        raise PlanError("Unknown experience_mode; choose 3d, 4d, 5d, or ar.")
    domain = domains[domain_id]
    mode = modes[experience_mode]

    output_index = config.get("outputs", {})
    requested_outputs = job.get("requested_outputs")
    if requested_outputs is None:
        requested_outputs = list(mode.get("default_outputs", []))
    if not isinstance(requested_outputs, list) or any(not isinstance(value, str) for value in requested_outputs):
        raise PlanError("requested_outputs must be a list of output IDs.")
    requested_outputs = list(dict.fromkeys(requested_outputs))
    if not requested_outputs:
        raise PlanError("Select at least one output type.")
    unknown_outputs = [item for item in requested_outputs if item not in output_index]
    if unknown_outputs:
        raise PlanError("Unknown output ID; select from the configured output list.")

    category_index = _registry_index(registry)
    category_ids = domain.get("category_ids", [])
    if not isinstance(category_ids, list) or any(not isinstance(value, str) for value in category_ids):
        raise PlanError(f"Invalid category route in domain {domain_id}.")
    unknown_categories = [value for value in category_ids if value not in category_index]
    if unknown_categories:
        raise PlanError(f"Domain {domain_id} references a category absent from the canonical registry.")

    category_routes = []
    for category_id in category_ids:
        category = category_index[category_id]
        category_routes.append({
            "id": category_id,
            "description": category.get("description"),
            "sub_agents": category.get("sub_agents"),
            "products": category.get("products"),
            "named_roster_status": category.get("named_roster_status", "not stated"),
            "roster_detail": _roster_detail(category_id, registry),
        })

    pack_ids = _selected_content_packs(job.get("content_pack_ids"), category_ids, catalog)
    content_metadata = _build_content_metadata(pack_ids, catalog)

    required_adapter_ids: list[str] = []
    for output_id in requested_outputs:
        for adapter_id in output_index[output_id].get("required_adapters", []):
            if adapter_id not in required_adapter_ids:
                required_adapter_ids.append(adapter_id)
    for adapter_id in domain.get("required_adapter_ids", []):
        if adapter_id not in required_adapter_ids:
            required_adapter_ids.append(adapter_id)
    if trend_source and "trend_source" not in required_adapter_ids:
        required_adapter_ids.append("trend_source")
    if publish_target and "publisher" not in required_adapter_ids:
        required_adapter_ids.append("publisher")

    adapters = _adapter_index(config)
    tool_routes = []
    for adapter_id in required_adapter_ids:
        adapter = adapters.get(adapter_id)
        if adapter is None:
            tool_routes.append({
                "id": adapter_id,
                "status": "unregistered",
                "execution_enabled": False,
                "provider": None,
            })
        else:
            tool_routes.append({
                "id": adapter_id,
                "label": adapter.get("label", adapter_id),
                "status": adapter.get("status", "not_configured"),
                "provider": adapter.get("provider"),
                "execution_enabled": bool(adapter.get("execution_enabled", False)),
            })

    adapters_ready = bool(tool_routes) and all(
        item["execution_enabled"] and item["status"] == "configured"
        for item in tool_routes
    )
    policy_status = policy.get("status", config.get("release_gates", {}).get("policy_status"))
    risk_tags = list(domain.get("risk_tags", []))
    approval_gates = [
        "Owner/human review required before any public release.",
        "The source content-safety policy is a proposal, not a deployed moderation filter.",
    ]
    if "non_operational_only" in domain.get("route_note", "") or "restricted_scope" in domain.get("mapping_status", ""):
        approval_gates.append("Keep all war/arms content historical or fictional and non-operational; no functional weapon design or use instructions.")
    if risk_tags:
        approval_gates.append("Review applicable risk tags before creating or releasing assets: " + ", ".join(risk_tags) + ".")
    if publish_target:
        approval_gates.append("Publishing requires a configured channel adapter and explicit owner approval; neither is granted by this plan.")

    warnings = []
    if domain.get("mapping_status") in ("owner_mapping_required", "provisional_composite_owner_review", "partial_roster_owner_review"):
        warnings.append(domain.get("route_note", "Owner review is required for this route."))
    if not trend_source:
        warnings.append("No trend source supplied; no live trend discovery or freshness claim is available.")
    else:
        warnings.append("Trend reference is user-supplied and unverified; the planner does not fetch or validate it.")
    if not adapters_ready:
        warnings.append("One or more required visual/tool adapters are not configured; this is a route plan, not generated media.")
    warnings.append("No visual-tool dispatch executor is implemented; this orchestrator emits plans only, even if an adapter is later configured.")
    if policy_status != "deployed":
        warnings.append("Safety policy is not an operating filter; human review remains necessary.")
    if not category_routes:
        warnings.append("No canonical specialist category is mapped; owner mapping is required before specialist assignment.")

    timestamp = created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    registry_totals = registry.get("totals", {})
    readiness = registry.get("content_readiness", {})
    return {
        "schema_version": 1,
        "plan_id": plan_id or str(uuid.uuid4()),
        "created_at_utc": timestamp,
        "status": "PLAN_ONLY_REQUIRES_HUMAN_REVIEW",
        "execution_enabled": False,
        "job": {
            "title": title,
            "domain_id": domain_id,
            "domain_label": domain.get("label"),
            "experience_mode": experience_mode,
            "experience_label": mode.get("label"),
            "brief": brief,
            "audience": audience,
            "requested_outputs": [
                {"id": output_id, "label": output_index[output_id].get("label", output_id)}
                for output_id in requested_outputs
            ],
            "publish_target": publish_target,
        },
        "experience_definition": mode.get("definition"),
        "system_configuration_status": config.get("existing_configuration_audit", {}),
        "agent_route": {
            "orchestrators": config.get("orchestrators", []),
            "flow": config.get("agent_hierarchy", {}).get("flow", []),
            "mapping_status": domain.get("mapping_status"),
            "route_note": domain.get("route_note"),
            "categories": category_routes,
            "unknown_names_policy": config.get("agent_hierarchy", {}).get("unknown_names_policy"),
            "execution_note": config.get("agent_hierarchy", {}).get("execution_note"),
        },
        "content_route": {
            "catalog_scope": catalog.get("scope"),
            "selected_packs": content_metadata,
            "source_contents_loaded": False,
            "source_contents_sent_to_llm_or_tools": False,
        },
        "trend": {
            "source": trend_source or None,
            "observed_at": trend_observed_at or None,
            "verification_status": "owner_supplied_unverified" if trend_source else "not_supplied",
            "live_discovery_enabled": False,
            "adaptation_rule": "Use as inspiration for new work; rights-check and do not copy protected source assets.",
        },
        "tool_routes": tool_routes,
        "adapter_configuration_status": "ready" if adapters_ready else "incomplete",
        "required_adapters_ready": adapters_ready,
        "execution_status": "PLAN_ONLY_NO_VISUAL_TOOL_DISPATCH_EXECUTOR",
        "llm": {
            "status": config.get("llm", {}).get("status", "provider_unconfigured"),
            "automatic_calls": False,
            "provider_call_made": False,
            "note": config.get("llm", {}).get("note"),
        },
        "safety": {
            "source_policy_status": policy_status,
            "requires_human_review": True,
            "risk_tags": risk_tags,
            "approval_gates": approval_gates,
            "weapon_scope": config.get("release_gates", {}).get("weapon_scope"),
        },
        "publication": {
            "requested": bool(publish_target),
            "target": publish_target or None,
            "status": "blocked_adapter_unconfigured_and_owner_approval_required" if publish_target else "disabled_not_requested",
            "publisher_configured": False,
            "auto_publish": False,
        },
        "registry_snapshot": {
            "release": registry.get("release"),
            "totals": registry_totals,
            "content_readiness": readiness,
            "content_readiness_reconciliation_status": readiness.get("reconciliation_status"),
        },
        "warnings": warnings,
    }


def _add_llm_draft(plan: dict[str, Any], job: Mapping[str, Any], role: str) -> None:
    """Explicit opt-in only: draft text with the existing no-tools LLM harness."""
    jarvis_dir = REPO_ROOT / "ops" / "jarvis"
    if str(jarvis_dir) not in sys.path:
        sys.path.insert(0, str(jarvis_dir))
    try:
        import llm_harness  # type: ignore[import-not-found]
    except ImportError:
        raise PlanError("The existing Jarvis LLM harness is unavailable.") from None

    try:
        env = llm_harness.read_environment()
        llm_config = llm_harness.load_config(env)
        prompt = json.dumps(
            {
                "task": "Write a concise, original creative brief draft for human review. Do not assert live trends or unverified facts. Do not produce functional weapon design or operational guidance.",
                "job": {
                    "title": plan["job"]["title"],
                    "domain": plan["job"]["domain_label"],
                    "experience": plan["job"]["experience_label"],
                    "brief": job.get("brief", ""),
                    "audience": job.get("audience", ""),
                    "trend_reference_status": plan["trend"]["verification_status"],
                },
                "route_status": plan["status"],
                "constraints": [
                    "This is a draft only; a human must review it.",
                    "Do not claim the route plan has generated or published an asset.",
                    "Do not invent agent names, provider integrations, or factual claims.",
                ],
            },
            ensure_ascii=False,
        )
        text = llm_harness.complete(prompt, role, llm_config)
    except (ImportError, llm_harness.HarnessError) as exc:  # type: ignore[name-defined]
        # The harness exception is safe-to-display and contains no credentials.
        raise PlanError(f"Optional LLM draft could not run: {exc}") from None
    plan["llm"]["provider_call_made"] = True
    plan["llm"]["draft"] = {"status": "unreviewed_human_review_required", "role": role, "text": text}


def _read_input(path: str, stdin: TextIO) -> dict[str, Any]:
    try:
        if path == "-":
            raw = stdin.read(16_385)
        else:
            with Path(path).open("r", encoding="utf-8") as source:
                raw = source.read(16_385)
        if len(raw) > 16_384:
            raise PlanError("Input JSON exceeds the 16 KiB limit.")
        value = json.loads(raw)
    except PlanError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise PlanError("Could not read a valid JSON job object.") from None
    if not isinstance(value, dict):
        raise PlanError("Input must be a JSON object.")
    return value


def main(
    argv: list[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    parser = argparse.ArgumentParser(description="Plan-only Vyomaraj/Jarvis experience orchestrator")
    parser.add_argument("input", nargs="?", default="-", help="JSON job file, or - for standard input")
    parser.add_argument("--output", default="-", help="write plan JSON to a file, or - for standard output")
    parser.add_argument("--llm-draft", action="store_true", help="explicitly send the job brief to the locally configured no-tools LLM harness")
    parser.add_argument("--llm-role", choices=("vyomaraj", "jarvis"), default="vyomaraj")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--policy", type=Path, default=None)
    args = parser.parse_args(argv)
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        job = _read_input(args.input, stdin)
        config, catalog, registry, policy = load_sources(args.config, args.catalog, args.registry, args.policy)
        plan = build_plan(job, config, catalog, registry, policy)
        if args.llm_draft:
            _add_llm_draft(plan, job, args.llm_role)
        rendered = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
        if args.output == "-":
            stdout.write(rendered)
        else:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding="utf-8")
    except PlanError as exc:
        print(f"Experience orchestrator: {exc}", file=stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
