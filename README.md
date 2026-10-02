# Vyomaraj — The King of Sky

Vyomaraj is a private AI-agent orchestration and creation system.

## Public experience

The public surface is intentionally limited to approved creations and published experiences:

- AI-generated and human-approved content
- Knowledge, education and research experiences
- Culture, food, travel, sports and entertainment content
- Social-platform publishing outputs
- Approved public web experiences

## Current release and handover links

- [Current V16.7.24 release page](index.html)
- [Current DR replication status and session addendum](ops/vyomaraj-core/handover/DR_REPLICATION_STATUS_2026_10_02.md)
- [Read-only session-recovery importer and limitations](ops/integration/README.md)
- [V16.7.24 / v194 handover archive](Vyomaraj-Handover-V16.7.24-v194.zip)
- [34-chat archive ZIP (V15.0–V16.7.22)](Vyomaraj-All-Chats-From-Arena-Database-Till-V16.7.22.zip)
- [34-chat database](Vyomaraj-All-Chats-Database-One-Month.md) · [Image 1 session-label index](All-Chats-Array-From-Index.txt) · [Git commit references](Git-Commits-One-Month.txt)
- [Repository Android APK](Vyomaraj-App.apk) — artifact presence only; signing/version was not independently verified in this session.

The review branch is not deployed to GitHub Pages; see the DR status addendum for the current PR and deployment boundary.

## Private control plane

Internal orchestration, credentials, agent routing, infrastructure, recovery controls, private data, operational logs and other sensitive implementation details are kept out of the public-facing experience.

The repository contains operational material for authorized development and recovery. Secrets must remain in GitHub Actions secrets or another secure secret store and must never be committed to source files.

## Repository roles

- **Primary:** `Vyomaraj1356/Vyomarajai`
- **DR / secondary:** `deepakGoyal1356/Vyomaraj-Agent-6d64e`
- Primary-to-DR replication is authenticated and controlled.
- DR-to-primary promotion is a controlled recovery operation; no blind two-way overwrite or force-push is used.

## Verification policy

A commit message, screenshot, archive name, old preview URL, or previous "synced" statement is not proof of a current state.

Current claims should be backed by:

1. source commit/ref verification,
2. authenticated DR access verification,
3. replication evidence containing source and target state,
4. preview verification,
5. explicit separation of recovered, missing, reconciled and verified information.

## Development

Use review branches and pull requests for changes. Do not push experimental Arena changes directly over `main`.

## Security

Never commit:

- personal financial/account information,
- access tokens or API keys,
- private contact information,
- internal authentication material,
- private operational URLs,
- database credentials,
- recovery secrets.

If sensitive information is discovered in a public file, remove it and rotate the affected credential where applicable.

© 2026 Vyomaraj
