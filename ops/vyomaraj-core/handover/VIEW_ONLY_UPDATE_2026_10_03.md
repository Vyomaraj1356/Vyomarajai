# Vyomaraj — View-only Policy & Preview Update

**New GitHub-side evidence:** real Actions reads confirm all 125 primary-main files match on secondary, with 149 additional secondary-only files. The old base-tree construction retains extras while requiring whole-tree equality. The correction and explicit removal-review gate are in PR #5, not yet deployed on main. See `/reports/resilience` for the findings and actual run evidence; this is more specific than the earlier Arena 404/403 observations below.

**Owner-directed update · 3 October 2026**

## Completed changes

- Added visible **Sovereign** and **Contracts** sections to the reports viewer and experience navigation.
- Published the entertainment/view-only, voluntary-participation, non-harm policy at `/sovereign/`; machine-readable policy at `/policy.json`.
- Published draft creator/participation terms at `/contracts/`. These are not signed contracts, legal-compliance certification or consent collected from a page visit.
- Aghor is now **view-only**: removed plan creation/download controls and all practice sequences; disabled plan generation in the server-side API, including older study/reflection/service requests. History, sources, profiles, filters and general care information remain viewable.
- Clarified respect for humans, animals, religious and cultural sentiments, religions, castes, creeds and communities. No coercion, hazardous ritual instructions or presentation of rituals as cures.
- Clarified that earning means possible lawful creator opportunities, subject to rights, consent, law and platform rules—not guaranteed income. No payment or payout service is connected.
- Preserved the current 128-slot hierarchy, 173-reference index, earlier unnamed Bhakti slots and immutable historical snapshots. This is a platform policy layer, not a transfer of Bhakti into the Entertainment category.

## Preview availability

At investigation time the existing preview processes were still listening and local HTTP requests to ports 4174, 4175 and 4176 returned 200. Therefore a backend crash was **not established** as the reason the preview was unavailable in the user's browser. Local HTTP success alone does not establish that the browser-side preview link was reachable.

The gateway was restarted through the live-preview tool to expose a fresh **Vyomaraj reports & entertainment viewer** entry. Its two replica processes are refreshed with Reports as the landing page. The updated viewer is served through port 4176, with relative browser URLs and listeners bound to `0.0.0.0`. This is a session preview—not permanent hosting or a production uptime guarantee.

## What remains genuinely pending

The earlier main Actions run passed authentication but failed Git replication. Arena's separate connection had secondary 404 / Actions settings 403; a successful local preview does not resolve those permissions. The improved workflow remains review-branch code until an authorized merge. Successful exact-tree verification/sync, independent hosts, durable runtime backups and production failover/failback tests remain required. No zero-RPO/RTO or production DR completion is claimed.

Before launching real earning contracts: qualified legal review, contracting parties, rights/consent records, commercial disclosures, complaint handling, explicit acceptance and tested payments/refunds remain unimplemented. The new tabs do not pretend to execute these services.

## Earlier reports

Earlier Aghor and DR reports describe the previous implementation and its measured drill. Their statements about available Aghor practice plans are superseded by this view-only update; the actual prior drill measurements are preserved, not re-labelled as new production evidence.

## Revalidation results

**212 automated checks PASS:** DR 38; local availability 8; handover/report safety 13; Pairings 9; experience/HTTP/governance 77; research 36; current hierarchy 28; Node metadata safety 3.

**Six real Chromium suites PASS:** Aghor view-only and governance tabs; Agents/Education; Research; Film; Music; and Bhakti/Pairings. Tests include server-side rejection of every former Aghor planning mode, absence of practice steps/plan controls, source browsing, policy/contract navigation, preserved older features and mobile layouts.

Both rebuilt metadata checks, JavaScript syntax, YAML parsing and Git whitespace checks pass. The standalone reports viewer on 4174 was also refreshed; Sovereign, Contracts and the latest policy report return HTTP 200 in both that viewer and the integrated gateway on 4176.

A new GET-only audit at 12:56 UTC (`ops/dr/LIVE_AUDIT_VIEW_ONLY_2026_10_03.json`) confirms the production blockers remain: secondary 404 and Actions settings 403; observed main run `37123060948` still reports replication failure after successful authentication. No credentials, settings, secondary refs or production traffic were changed by this update.
