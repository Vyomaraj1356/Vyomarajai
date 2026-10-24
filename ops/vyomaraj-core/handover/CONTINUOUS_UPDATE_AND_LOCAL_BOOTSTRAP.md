# Vyomaraj + Jarvis: Continuous Update and Local Bootstrap Policy

## Goal

Reduce manual setup and update friction while keeping production, credentials, the owner's computer, and disaster recovery safe. An update is complete only when the installed or deployed version and its behavior have been verified.

## Enabled by this change

- Dependabot proposes weekly Python dependency and GitHub Actions updates through pull requests.
- Updates remain reviewable and auditable; this configuration does not silently install dependencies into production.
- Use existing GitHub Actions checks as merge gates. Do not enable blanket auto-merge for production dependencies until test coverage and branch protections are confirmed.
- Hosted CI cannot install software on the owner's Windows computer or verify camera/audio/Dolby hardware.

## Standard update lifecycle

1. Discover outdated dependencies using Dependabot.
2. Review release notes, compatibility, licenses, security advisories and lockfile changes.
3. Build in a clean environment and run the offline suites and relevant CI workflows.
4. Stage in a non-production environment where supported.
5. Verify the actual deployed commit, health endpoint and functional smoke tests.
6. Promote only after required checks pass; preserve a known-good deployment.
7. Roll back failed deployments and create an issue with sanitized evidence.
8. Record versions, approvals, tests, deployment and rollback status without secrets.

## Windows local environment bootstrap

Run from a trusted clone of the primary repository in PowerShell. Use a user-scoped environment; do not run as Administrator unless a reviewed dependency genuinely requires elevation.

    git status --short
    python --version
    if ($LASTEXITCODE -ne 0) { throw "Python is missing or not on PATH. Install the repository-supported Python version first." }
    if (-not (Test-Path ".venv")) { python -m venv .venv }
    . .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    if (Test-Path "requirements-2026-lock.txt") {
      python -m pip install --requirement requirements-2026-lock.txt
    } elseif (Test-Path "requirements.txt") {
      Write-Warning "No requirements-2026-lock.txt found; confirm requirements.txt is the intended manifest."
      python -m pip install --requirement requirements.txt
    } else {
      throw "No recognized root dependency manifest. Inspect project-specific setup instructions instead of guessing."
    }
    python -m pip check

If PowerShell blocks activation, do not weaken machine-wide execution policy. Use the environment interpreter directly: .\.venv\Scripts\python.exe -m pip check

The bootstrap commands do not copy environment files, print secrets, change Windows services, install drivers or deploy to production.

## Local hardware integrations

Camera, microphone, speaker routing, Dolby and device drivers must be tested on the actual target machine with explicit user permission. Keep captures local unless the owner separately approves an upload workflow. A browser test page is not proof of Dolby licensing or end-to-end audio certification.

## Production and disaster recovery safeguards

- Never write to DR unless the target identity, protected-path exception for ops/jarvis/jarvis.env, and explicit write authorization have all been validated.
- Preserve ops/jarvis/jarvis.env under the approved protected-path policy; do not claim exact tree equality where that exception applies.
- Never place API keys, PATs, access tokens, environment file contents or credential-bearing URLs in logs, artifacts, PRs or chat.
- Use least-privilege credentials and protected deployment environments; require owner approval for privileged changes.
- Do not automatically apply major dependency, OS, driver, firmware, model, database-schema, financial or security-policy changes.

## Completion evidence checklist

- [ ] Dependency PR merged after checks and review
- [ ] CI green on the exact release commit
- [ ] Hosted service reports the intended commit and passes health and functional smoke tests
- [ ] Local target environment reports expected versions and pip check passes
- [ ] Provider calls verified with authorized credentials, without logging secrets
- [ ] Device capabilities verified on actual target hardware
- [ ] DR write/read-back and recovery drill verified separately under approved policy
- [ ] Rollback path tested and evidence retained

A checklist item requires actual evidence. Repository files or a successful build alone do not certify runtime installation or hardware operation.