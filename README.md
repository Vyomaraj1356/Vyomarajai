# Vyomaraj — The King of Sky

Vyomaraj is a private AI-agent orchestration and creation system.

## Public experience

The public surface is intentionally limited to approved creations and published experiences:

- AI-generated and human-approved content
- Knowledge, education and research experiences
- Culture, food, travel, sports and entertainment content
- Social-platform publishing outputs
- Approved public web experiences

## Private control plane

Internal orchestration, credentials, agent routing, infrastructure, recovery controls, private data, operational logs and other sensitive implementation details are kept out of the public-facing experience.

The repository contains operational material for authorized development and recovery. Secrets must remain in GitHub Actions secrets or another secure secret store and must never be committed to source files.

## Repository roles

- **Primary:** `Vyomaraj1356/Vyomarajai`
- **DR / secondary:** not yet verified; historical names conflict and authenticated checks returned 404. Confirm the destination through the [repository map](VYOMARAJ_REPOSITORY_MAP.md), then set Actions variable `VYOMARAJ_DR_REPO`.
- Primary-to-DR replication is authenticated, opt-in and main-only; see the [DR verification runbook](ops/dr/README.md). A 404 is not proof that a private repository does not exist.
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

## Reconstructed handover — 3 October 2026

The [handover notepad](ops/vyomaraj-core/handover/HANDOVER_ALL_UPDATES_2026_10_03.txt) was reconstructed from the verified roster and content catalog on the reconciled Arena branch. It is **not the recovered original 365-line file**. It preserves `UNKNOWN` names and `UNMAPPED` slots, lists only the 32 cataloged JSON filenames (not all 421 product titles), and excludes populated runtime/device values.

Validate it locally with `python ops/vyomaraj-core/handover/rebuild_handover.py --check`.

For the expanded agent roster, historical candidates, content-label index, platform/technology configuration, and unresolved work, see the [full system inventory](ops/vyomaraj-core/handover/FULL_SYSTEM_INVENTORY_2026_10_03.md). It distinguishes local files, remote-only implementations and unverified historical claims; private configuration values are excluded.

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
