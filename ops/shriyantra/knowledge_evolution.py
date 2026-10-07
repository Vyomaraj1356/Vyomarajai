#!/usr/bin/env python3
"""Offline reference resolver and structural validator for shared temporal knowledge.

This module does not call models, retrieve sources, persist memories, or connect peer runtimes.
Production enforcement must integrate the same policy in the trusted Harness/CAG boundary.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json"
POLICY_REF = "config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json"

REQUIRED_LAYER_IDS = (
    "primitive_origin",
    "old",
    "historical_evolution",
    "history",
    "present",
    "current_state",
    "trends",
    "future",
    "possible_futures",
)
REQUIRED_EVIDENCE_CLASSES = (
    "FACT",
    "HISTORICAL_RECORD",
    "CURRENT_VERIFIED_STATE",
    "TREND",
    "FORECAST",
    "SCENARIO",
    "SPECULATION",
    "UNKNOWN_UNVERIFIED",
)
FUTURE_FACTUAL_CLASSES = {"FACT", "HISTORICAL_RECORD", "CURRENT_VERIFIED_STATE", "TREND"}


class KnowledgeContractError(ValueError):
    """Raised when a policy or knowledge record violates the shared contract."""


def validate_policy_document(policy: Mapping[str, Any]) -> None:
    """Check the non-negotiable policy shape without third-party dependencies."""
    if not isinstance(policy, Mapping):
        raise KnowledgeContractError("policy must be a JSON object")
    if policy.get("policy_id") != "UNIVERSAL_KNOWLEDGE_EVOLUTION_V1":
        raise KnowledgeContractError("unexpected knowledge policy ID")
    if policy.get("policy_version") != 1:
        raise KnowledgeContractError("unsupported knowledge policy version")

    model = policy.get("temporal_model")
    layers = model.get("ordered_layers") if isinstance(model, Mapping) else None
    layer_ids = [row.get("id") for row in layers] if isinstance(layers, list) else []
    if tuple(layer_ids) != REQUIRED_LAYER_IDS:
        raise KnowledgeContractError("temporal layers are missing, reordered, or unknown")

    classes = policy.get("evidence_classes")
    class_ids = [row.get("id") for row in classes] if isinstance(classes, list) else []
    if set(class_ids) != set(REQUIRED_EVIDENCE_CLASSES) or len(class_ids) != len(set(class_ids)):
        raise KnowledgeContractError("required evidence classes are missing or duplicated")

    inheritance = policy.get("inheritance")
    if not isinstance(inheritance, Mapping):
        raise KnowledgeContractError("shared inheritance declaration is missing")
    if inheritance.get("mode") != "shared_policy_reference":
        raise KnowledgeContractError("entities must inherit the policy by shared reference")
    if inheritance.get("policy_ref") != POLICY_REF:
        raise KnowledgeContractError("policy reference does not resolve to the canonical file")
    required_entities = {"category", "agent", "sub_agent", "topic", "content", "chapter", "product"}
    if not required_entities.issubset(set(inheritance.get("entity_types", []))):
        raise KnowledgeContractError("one or more required entity types do not inherit the policy")
    if inheritance.get("future_entities_inherit_by_default") is not True:
        raise KnowledgeContractError("future entities must inherit the shared policy by default")
    if inheritance.get("per_entity_copy_required") is not False:
        raise KnowledgeContractError("per-entity policy copies are not the inheritance mechanism")

    rules = policy.get("classification_rules")
    if not isinstance(rules, Mapping):
        raise KnowledgeContractError("classification rules are missing")
    if rules.get("future_claims_must_never_be_presented_as_facts") is not True:
        raise KnowledgeContractError("future-claim guard must be enabled")
    if set(rules.get("future_layer_allowed_classes", [])) != {
        "FORECAST", "SCENARIO", "SPECULATION", "UNKNOWN_UNVERIFIED"
    }:
        raise KnowledgeContractError("future-layer evidence classes are unsafe or incomplete")


def load_policy(path: Path | str = POLICY_PATH) -> dict[str, Any]:
    """Load and validate the canonical JSON policy."""
    policy_path = Path(path)
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KnowledgeContractError("knowledge policy is unavailable or invalid JSON") from exc
    validate_policy_document(policy)
    return policy


def resolve_inheritance(
    entity_type: str,
    entity_id: str,
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a shared policy reference for a known or future entity, without copying policy.

    The result is an envelope for a trusted caller to place in task context. It does not
    connect an agent runtime or prove that any deployed system consumes the envelope.
    """
    selected = policy or load_policy()
    validate_policy_document(selected)
    if not isinstance(entity_type, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", entity_type.strip()):
        raise KnowledgeContractError("entity_type must be a lowercase identifier")
    if not isinstance(entity_id, str) or not entity_id.strip() or len(entity_id.strip()) > 240:
        raise KnowledgeContractError("entity_id must be a non-empty bounded string")

    inheritance = selected["inheritance"]
    known = entity_type.strip() in inheritance["entity_types"]
    if not known and inheritance.get("future_entities_inherit_by_default") is not True:
        raise KnowledgeContractError("entity type is not covered by the inheritance policy")
    return {
        "policy_id": selected["policy_id"],
        "policy_version": selected["policy_version"],
        "policy_ref": inheritance["policy_ref"],
        "entity": {"type": entity_type.strip(), "id": entity_id.strip()},
        "inheritance_status": "inherited_by_shared_reference",
        "coverage": "listed_entity_type" if known else "future_entity_default",
        "temporal_layers": [row["id"] for row in selected["temporal_model"]["ordered_layers"]],
        "standard_questions": list(selected["temporal_model"]["standard_questions"]),
        "evidence_classes": [row["id"] for row in selected["evidence_classes"]],
        "future_claim_guard": selected["classification_rules"]["future_claims_must_never_be_presented_as_facts"],
        "runtime_status": selected["implementation_status"],
    }


def _require_text(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeContractError(f"{key} must be a non-empty string")
    return value.strip()


def _require_utc_timestamp(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeContractError(f"{label} must be an ISO-8601 UTC timestamp")
    raw = value.strip()
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise KnowledgeContractError(f"{label} must be an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise KnowledgeContractError(f"{label} must include an explicit UTC offset")


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (Mapping, list, tuple, set)):
        return bool(value)
    return value is not None


def validate_knowledge_record(
    record: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> None:
    """Validate record structure and epistemic labels; this cannot validate source truth.

    Future claims labelled as facts or historical/current verified records are rejected.
    Citation retrieval, source credibility, factual correctness, and forecast calibration
    remain the responsibility of an authorized evidence pipeline and domain reviewers.
    """
    selected = policy or load_policy()
    validate_policy_document(selected)
    if not isinstance(record, Mapping):
        raise KnowledgeContractError("knowledge record must be an object")

    for key in ("record_id", "entity_type", "entity_id", "claim", "temporal_layer", "evidence_class"):
        _require_text(record, key)
    for key in ("scope", "uncertainty"):
        if not _nonempty(record.get(key)):
            raise KnowledgeContractError(f"{key} must be stated; use an explicit unknown when needed")
    _require_utc_timestamp(record.get("recorded_at_utc"), "recorded_at_utc")

    temporal_layer = record["temporal_layer"]
    layer_ids = {row["id"] for row in selected["temporal_model"]["ordered_layers"]}
    if temporal_layer not in layer_ids:
        raise KnowledgeContractError("temporal_layer is not in the shared model")
    evidence_class = record["evidence_class"]
    class_by_id = {row["id"]: row for row in selected["evidence_classes"]}
    if evidence_class not in class_by_id:
        raise KnowledgeContractError("evidence_class is not in the shared classification")

    rules = selected["classification_rules"]
    if temporal_layer in set(rules["future_layers"]):
        if evidence_class in FUTURE_FACTUAL_CLASSES:
            raise KnowledgeContractError("future-layer claims cannot be labeled as facts or verified past/current records")
        if evidence_class not in set(rules["future_layer_allowed_classes"]):
            raise KnowledgeContractError("evidence_class is not allowed for a future layer")
    if evidence_class == "TREND" and temporal_layer != "trends":
        raise KnowledgeContractError("TREND claims must use the trends temporal layer")
    if evidence_class == "FORECAST" and temporal_layer not in set(rules["future_layers"]):
        raise KnowledgeContractError("FORECAST claims must use a future temporal layer")
    if evidence_class == "SCENARIO" and temporal_layer not in set(rules["future_layers"]):
        raise KnowledgeContractError("SCENARIO claims must use a future temporal layer")
    if evidence_class == "CURRENT_VERIFIED_STATE" and temporal_layer not in {"present", "current_state"}:
        raise KnowledgeContractError("CURRENT_VERIFIED_STATE must use present or current_state")

    sources = record.get("sources")
    if not isinstance(sources, list):
        raise KnowledgeContractError("sources must be a list, including an empty list for explicitly unsourced speculation")
    if class_by_id[evidence_class].get("sources_required") and not sources:
        raise KnowledgeContractError(f"{evidence_class} requires at least one provenance source")
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise KnowledgeContractError(f"sources[{index}] must be an object")
        for key in ("source_id", "source_ref", "access_label"):
            _require_text(source, key)
        _require_utc_timestamp(source.get("retrieved_at_utc"), f"sources[{index}].retrieved_at_utc")
        source_ids.add(source["source_id"].strip())

    if evidence_class == "CURRENT_VERIFIED_STATE":
        _require_utc_timestamp(record.get("as_of_utc"), "as_of_utc")
        _require_text(record, "verification_method")
    elif evidence_class == "TREND":
        _require_text(record, "observation_window")
        observations = record.get("supporting_observations")
        minimum = int(rules["trend_minimum_dated_observations"])
        if not isinstance(observations, list) or len(observations) < minimum:
            raise KnowledgeContractError(f"TREND requires at least {minimum} supporting dated observations")
        for index, observation in enumerate(observations):
            if not isinstance(observation, Mapping):
                raise KnowledgeContractError(f"supporting_observations[{index}] must be an object")
            _require_utc_timestamp(observation.get("observed_at_utc"), f"supporting_observations[{index}].observed_at_utc")
            source_id = _require_text(observation, "source_id")
            if source_id not in source_ids:
                raise KnowledgeContractError(f"supporting_observations[{index}] must refer to a listed source")
    elif evidence_class == "FORECAST":
        _require_text(record, "prediction_horizon")
        _require_text(record, "method")
        assumptions = record.get("assumptions")
        if not isinstance(assumptions, list) or not assumptions or not all(_nonempty(item) for item in assumptions):
            raise KnowledgeContractError("FORECAST requires explicit non-empty assumptions")
    elif evidence_class == "SCENARIO":
        _require_text(record, "conditional_on")
        assumptions = record.get("assumptions")
        if not isinstance(assumptions, list) or not assumptions or not all(_nonempty(item) for item in assumptions):
            raise KnowledgeContractError("SCENARIO requires explicit non-empty assumptions")
    elif evidence_class == "SPECULATION":
        _require_text(record, "why_speculative")


def main() -> int:
    """Small offline check for the canonical policy; no network or mutation."""
    policy = load_policy()
    print(
        "PASS: "
        f"{policy['policy_id']} v{policy['policy_version']}; "
        f"{len(policy['temporal_model']['ordered_layers'])} temporal layers; "
        f"{len(policy['evidence_classes'])} evidence classes; "
        f"{policy['inheritance']['mode']} inheritance; "
        f"status={policy['implementation_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
