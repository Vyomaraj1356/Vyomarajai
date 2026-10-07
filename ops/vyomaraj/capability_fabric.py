"""Capability routing for the Hanuman Panch-Brother design domains.

The names are used as engineering capability labels inspired by the
Brahmanda Purana tradition; this module does not assert scriptural software roles.
"""
CAPABILITIES = {
    "matiman": {"reasoning", "planning", "architecture_review", "risk_analysis", "decision_support"},
    "shrutiman": {"research", "retrieval", "knowledge", "provenance", "learning"},
    "ketuman": {"monitoring", "alerting", "anomaly_detection", "navigation", "routing"},
    "gatiman": {"execution", "automation", "tool_orchestration", "browser", "geospatial"},
    "dhritiman": {"health", "resilience", "recovery", "failover", "failback", "audit_continuity"},
}

def capability_domains(required: set[str]) -> list[str]:
    if not required:
        return []
    return [name for name, capabilities in CAPABILITIES.items()
            if required.intersection(capabilities)]

def authorize_capabilities(required: set[str], owner_authorized: bool,
                           high_risk: bool = False, step_up_confirmed: bool = False) -> list[str]:
    if not owner_authorized:
        raise PermissionError("owner authorization required")
    if high_risk and not step_up_confirmed:
        raise PermissionError("step-up confirmation required")
    domains = capability_domains(required)
    if not domains:
        raise ValueError("no registered capability domain satisfies request")
    return domains
