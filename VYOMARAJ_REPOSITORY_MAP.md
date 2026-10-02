# VYOMARAJ REPOSITORY MAP — SINGLE SOURCE OF TRUTH

PRIMARY = Vyomaraj1356/Vyomarajai : main : SOURCE OF TRUTH
DR SECONDARY = deepakGoyal1356/Vyomaraj-Agent-6d64 : main : RECOVERY MIRROR

Rules:
- Arena codes and opens PRs only in PRIMARY.
- Arena never guesses repositories.
- Normal replication is PRIMARY/main -> DR/main only.
- PR and feature branches are never replicated to DR.
- DR -> PRIMARY is recovery-only, manual, and integrity-gated.
- No force-push, blind overwrite, split-brain promotion, or automatic DR takeover.
- Do not create another PRIMARY/SECONDARY pair.
- If another document conflicts with this map, this map wins.
