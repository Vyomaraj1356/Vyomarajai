# Vyomaraj repository map — confirmation required for DR

- **Primary source:** `Vyomaraj1356/Vyomarajai`, branch `main`.
- **This repair branch:** `arena/01a10140-vyomarajai`.
- **Secondary:** UNCONFIRMED. Do not infer it from a 404 or select a spelling silently.
- **Authoritative setting after confirmation:** primary repository Actions variable `VYOMARAJ_DR_REPO`.
- **Write approval:** `VYOMARAJ_DR_SYNC_ENABLED=true` only after a successful authorized access check and review of exact-snapshot behavior.

Historical references to `Vyomaraj-Agent`, `Vyomaraj-Agent-6d64`, `Vyomaraj-Agent-6d64e` and `Vyomraj-Agent-6d64` under the secondary owner conflict. All returned 404 using this Arena connection on 3 October 2026. A private repository can be hidden by permissions. No destination was verified and no new repository was created.

One-way primary-main → approved DR-main snapshots only. Feature branches are not replicated. No force updates, reverse synchronization, traffic switching or automatic takeover. See `ops/dr/README.md` for validation and authorization gates. Historical environment files, README claims and repository maps from older branches do not override the explicit configuration/approval requirement.
