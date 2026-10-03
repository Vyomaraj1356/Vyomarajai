"""Owner-requested view-only restriction. No Aghor practice plans are generated."""

def build_aghor_plan(request, path):
    raise ValueError('Aghor is entertainment and view-only. Plan generation is disabled; no ritual, reflection, service or treatment instructions are generated.')
