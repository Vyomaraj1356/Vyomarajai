# Vyomaraj Security Guard
Defensive security package for VYOMARAJ-AI-STUDIO.

Capabilities: SHA-256 integrity baselining, suspicious script/persistence indicators, scheduled-task inspection, Microsoft Defender status where available, secret-pattern detection without recording values, optional authenticated Primary/DR SHA verification, and incident evidence.

Safety: no stealth/evasion, credential harvesting, destructive deletion, blind force-push, automatic DR-to-Primary promotion, or automatic execution of suspicious files.

Remote verification environment variables:
VYOMARAJ_PRIMARY_REPO=Vyomaraj1356/Vyomarajai
VYOMARAJ_DR_REPO=deepakGoyal1356/Vyomaraj-Agent-6d64
VYOMARAJ_PAT=<token from secure environment/secret store>

Do not commit the token. Exit codes: 0 PASS, 1 REVIEW REQUIRED, 2 CRITICAL.