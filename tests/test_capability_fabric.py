from ops.vyomaraj.capability_fabric import authorize_capabilities, capability_domains

def test_capability_domains_route():
    assert "matiman" in capability_domains({"reasoning"})
    assert "shrutiman" in capability_domains({"research"})
    assert "ketuman" in capability_domains({"monitoring"})
    assert "gatiman" in capability_domains({"execution"})
    assert "dhritiman" in capability_domains({"recovery"})

def test_owner_authorization_required():
    try:
        authorize_capabilities({"reasoning"}, False)
        assert False
    except PermissionError:
        pass

def test_high_risk_requires_step_up():
    try:
        authorize_capabilities({"execution"}, True, high_risk=True)
        assert False
    except PermissionError:
        pass
