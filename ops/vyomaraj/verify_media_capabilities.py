#!/usr/bin/env python3
"""Validate the cross-device media capability contract; this is not a device test."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "config" / "media" / "VYOMARAJ_JARVIS_MEDIA_CAPABILITY_CONTRACT_v1.json"
REQUIRED_POLICY = {"provider_neutral","device_capability_detection_required","fallback_required","owner_approval_required_for_external_publish_or_paid_activation","never_claim_physical_hardware_or_license_without_evidence","fail_closed_on_unknown_capability"}
REQUIRED_CAPABILITIES = {"audio_playback","speech_input","speech_output","audio_processing","spatial_audio","dolby_atmos","video_playback","adaptive_streaming","4k_video","hdr10","dolby_vision","captions_accessibility"}
VERIFIED = {"verified","runtime_verified","production_verified"}
ALLOWED_STATES = {"unverified","verified","runtime_verified","production_verified","blocked","not_applicable"}

def validate(data: dict[str, Any] | None = None) -> dict:
    """Validate supplied contract data or the checked-in file without mutating it."""
    if data is None:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    errors: list[str] = []
    policy = data.get("policy", {})
    missing_policy = sorted(REQUIRED_POLICY - set(policy))
    if missing_policy: errors.append("missing policy keys: " + ", ".join(missing_policy))
    capabilities = data.get("capabilities", [])
    by_id = {item.get("id"): item for item in capabilities if isinstance(item, dict)}
    missing_caps = sorted(REQUIRED_CAPABILITIES - set(by_id))
    if missing_caps: errors.append("missing capability entries: " + ", ".join(missing_caps))
    invalid_states, overclaims = [], []
    for cap_id, item in by_id.items():
        if item.get("runtime_state") not in ALLOWED_STATES: invalid_states.append(cap_id)
        if item.get("runtime_state") in VERIFIED and not item.get("evidence"): overclaims.append(cap_id)
        if not item.get("fallback"): errors.append(f"{cap_id}: missing fallback")
    if invalid_states: errors.append("invalid runtime state: " + ", ".join(sorted(invalid_states)))
    if overclaims: errors.append("verified state lacks evidence: " + ", ".join(sorted(overclaims)))
    verification = data.get("verification_contract", {})
    for key in ("runtime_verified_requires","physical_capability_requires","licensed_format_requires","provider_connected_requires"):
        if not verification.get(key): errors.append(f"missing verification requirements: {key}")
    return {"status":"PASS" if not errors else "FAIL","contract_valid":not errors,"capabilities_in_contract":len(by_id),"runtime_verified_capabilities":sorted(k for k,v in by_id.items() if v.get("runtime_state") in VERIFIED),"runtime_tests_performed":False,"hardware_or_license_presence_verified":False,"errors":errors}

if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
