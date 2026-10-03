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

The [DR resolution report](ops/vyomaraj-core/handover/DR_RESOLUTION_2026_10_03.md) records the current 404/403 access blockers, local fixes and GitHub PR/CI evidence. For readable tables, run `python ops/vyomaraj-core/handover/preview_reports.py --port 4174` and use the Arena live preview. Only the three sanitized reports are served; do not replace this with unrestricted repository-root file serving.

## Music, radio, audio and video

[Memory & Melody](ops/vyomaraj-core/music-experience/README.md) fills the dedicated music experience gap without duplicating the six existing ENT-MUS slots. It adds researched nostalgia/album/folk/world/chart/video discovery, a browser-local authorized-file player, and source-linked Vyomaraj/Jarvis programme plans. Run the shared studio on port 4176 and open `/music/`. [Updated audit and feature report](ops/vyomaraj-core/handover/MUSIC_AUDIO_VIDEO_UPDATE_2026_10_03.md). Slot functions are proposals; streaming, live charts and external AI are not connected.

## Bhakti-Shakti and the integrated local studio

The [Bhakti-Shakti feature report](ops/vyomaraj-core/handover/BHAKTI_FEATURE_UPDATE_2026_10_03.md) covers Shiv–Shakti, a 12-chapter proposed Shiva story guide, a Dashavatara overview, nine Shakti Peetha/regional starter profiles and Mahadev television context. The [content guide](ops/vyomaraj-core/bhakti-experience/README.md) explains sources and limitations.

Run `python ops/vyomaraj-core/experience/studio_server.py --port 4176` for a unified preview of Bhakti, Liquor/Bar and updated reports. Its local `/api/plan` implements deterministic Vyomaraj topic routing and Jarvis review handoffs. Prasad-style food rotation, preparation sequences and preference controls are illustrative. External AI, production publishing and DR synchronization remain disabled/unverified. No canonical agent totals or old content files were overwritten.

## Liquor + Bar: Roots & Pairings

The [Liquor/Bar content expansion](ops/vyomaraj-core/liquor-bar/README.md) adds local tadi/toddy, regional/global cultural research, event-source records, and eight chakhna/snack concepts with preparation, allergen preferences and non-alcoholic pairings. Run `python ops/vyomaraj-core/liquor-bar/server.py --port 4175` for the interactive browser prototype. Its 3D-style plate, 4D sequence and 5D preference controls are illustrative; no AI renderer or alcohol service is connected. Proposed chapters live in a separate extension catalog without changing the original 133/421 counts or 32-file snapshot.

## Priority recovery / cleanup status

The [non-destructive recovery audit](ops/vyomaraj-core/handover/PRIORITY_RECOVERY_AUDIT_2026_10_03.md) records the full available primary fetch, duplicate archive candidates and the ordered reconciliation plan. Secondary access is still blocked; see [priority issue #6](https://github.com/Vyomaraj1356/Vyomarajai/issues/6). Do not delete historical archives or enable exact-snapshot DR writes before secondary-only work has been inspected and preserved.

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
