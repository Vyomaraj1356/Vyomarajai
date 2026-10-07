from ops.vyomaraj.agent_capability_inheritance import (
    ALL_DOMAINS,
    inherited_agent_capabilities,
    validate_inheritance,
)

def test_all_current_agents_inherit_panch_brother_domains():
    result = validate_inheritance()
    assert result["registry_agents"] == 133
    assert result["profiles"] == 133
    assert result["all_agents_inherit_all_domains"] is True

def test_inherited_capabilities_are_policy_controlled():
    profiles = inherited_agent_capabilities()
    assert profiles
    assert all(p["owner_policy_required"] for p in profiles.values())
    assert all(p["high_risk_step_up_required"] for p in profiles.values())
    assert all(p["self_elevation_forbidden"] for p in profiles.values())
    assert all(tuple(p["inherited_domains"]) == ALL_DOMAINS for p in profiles.values())
