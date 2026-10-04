# Vyomaraj repository map — confirmation required for DR

- **Primary source:** `Vyomaraj1356/Vyomarajai`, branch `main`.
- **Current session branch:** `arena/01a105da-vyomarajai` (earlier repair branch: `arena/01a10140-vyomarajai`).
- **Secondary (snapshot replication target): CONFIRMED in use** — `deepakGoyal1356/Vyomaraj-Agent-6d64e`, recorded in `ops/dr/DR_POLICY.json` and evidenced by the 15 MATCH checkpoints in `ops/dr/DEPLOYED_MATCH_2026_10_04.json` (each re-read live from the GitHub API; latest: merge #20, check-run 111386365434, rollback parent f2bfd8a5… retained). Confirmation basis: the primary's own Actions workflow annotations, not a 404 inference. A sandbox credential that cannot see the private secondary does not disprove it.
- **Authoritative setting after confirmation:** primary repository Actions variable `VYOMARAJ_DR_REPO`.
- **Write approval:** `VYOMARAJ_DR_SYNC_ENABLED=true` only after a successful authorized access check and review of exact-snapshot behavior.

Historical references to `Vyomaraj-Agent`, `Vyomaraj-Agent-6d64`, `Vyomaraj-Agent-6d64e` and `Vyomraj-Agent-6d64` under the secondary owner conflict. All returned 404 using this Arena connection on 3 October 2026. A private repository can be hidden by permissions. No destination was verified and no new repository was created.

One-way primary-main → approved DR-main snapshots only. Feature branches are not replicated. No force updates, reverse synchronization, traffic switching or automatic takeover. See `ops/dr/README.md` for validation and authorization gates. Historical environment files, README claims and repository maps from older branches do not override the explicit configuration/approval requirement.
