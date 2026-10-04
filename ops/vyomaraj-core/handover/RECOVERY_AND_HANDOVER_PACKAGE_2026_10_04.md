# Recovery and handover package — 2026-10-04

**This page is generated from the repository, not from memory.** It records what was reported
lost, what was rebuilt, and how a reader can re-verify every claim in it. It describes two
rebuilds on the same day: one after the first sandbox was re-provisioned, and one after that
sandbox was deleted outright.

## Rebuild 2 (this session) — after the first session's sandbox was deleted

| Item | Status |
|---|---|
| Local commit `7f60778` and the 12,782-byte note it carried (reported SHA256 `ba084682…`) | ABSENT — the sandbox that held them (`…ir9cja5hdxih69wns3dlj`) answers "Sandbox not found"; bytes unrecoverable, **not** reproduced |
| Ad-hoc downloads server on port 4190, and every preview link under that sandbox | GONE with the sandbox; links are per-sandbox and cannot be restored |
| The first session's final report/notepad refresh | Rebuilt here from live evidence, with new SHA256 values |
| DR record coverage of merge #18 | Recorded here: 13 MATCH checkpoints, 9 replication writes, 1 correctly blocked run |

What rebuild 2 added or regenerated, all committed on this branch:

- `NEXT_SESSION_HANDOVER_2026_10_04.txt` — rebuilt notepad (section 0 explains its provenance).
- `DR_SYNC_RESULTS_2026_10_04.md` + `build_dr_sync_report.py` + `test_dr_sync_report.py` — a
  generated DR sync results report. It is rebuilt from `ops/dr/DEPLOYED_MATCH_2026_10_04.json`,
  `ops/dr/DR_POLICY.json` and the workflow file; `--check` fails if it drifts from that evidence.
- `ops/dr/DEPLOYED_MATCH_2026_10_04.json` — extended with the #18 checkpoint, PR/head mapping,
  workflow run ids, the live annotation of the blocked #11 run and of the read-only probe, and
  two corrected `completed_at` timestamps (status, trees and rollback commits were unchanged).
- `preview_reports.py` / `studio_server.py` — new `/reports/dr-sync`, `/reports/handover-notepad`
  and `/reports/download/handover-notepad.txt` routes plus nav entries on both viewers.
- Regenerated: `TRANSFER_MANIFEST_2026_10_04.json`, the transfer package,
  `BUILD_AND_CONFIGURATION_2026_10_04.md`, `PREVIEW_VERIFICATION_2026_10_04.json` and
  `TEST_EVIDENCE_2026_10_04.json` (247 Python tests across 7 suites, node checks, rebuild checks).

## Rebuild 1 (earlier session) — after a sandbox re-provision

| Item | Status in this checkout |
|---|---|
| Local commits `65dda1e`, `1b496d2` | ABSENT — not in history and not on any remote ref |
| Prior note `NEXT_SESSION_HANDOVER_2026_10_03.txt` (reported SHA256 `9d5fc218…`) | ABSENT — bytes unrecoverable; **not** reproduced byte-for-byte |
| Root-level copies of the note, Git bundle and ZIP | ABSENT from `/home/user` |
| `/reports/next-session`, `/reports/recovery`, `/reports/download/next-session.txt` routes | Rebuilt by that session and still live |
| Drill/verification evidence for the above | Re-run and re-recorded with real observations |

## What the package contains

| Member | Purpose |
|---|---|
| `NEXT_SESSION_HANDOVER_2026_10_04.txt` | Canonical handover notepad for the next session |
| `RECOVERY_AND_HANDOVER_PACKAGE_2026_10_04.md` | This recovery page |
| `DR_SYNC_RESULTS_2026_10_04.md` (+ builder and test) | Generated DR sync results report and its reproduction |
| `HANDOVER_ALL_UPDATES_2026_10_03.txt` | Existing reconstructed roster/catalog handover |
| `preview_reports.py`, `studio_server.py`, `gateway.py` | The served preview components |
| `test_preview_reports.py`, `test_transfer_package.py`, `test_gateway.py` | Offline checks |
| `DEPLOYED_MATCH_2026_10_04.json` | The DR evidence the report is generated from |
| `LOCAL_FAILOVER_DRILL_2026_10_03.json`, `LOCAL_FAILOVER_DRILL_2026_10_04.json` | Drill evidence |

No secrets, tokens, PATs, environment files or private configuration are included. The package is
deliberately small (documents plus scripts) so it can be reviewed by a human.

## How to re-verify (all read-only, from the repository root)

```
python3 ops/vyomaraj-core/handover/build_dr_sync_report.py --check
python3 ops/vyomaraj-core/handover/build_transfer_package.py --check
python3 ops/vyomaraj-core/handover/build_configuration_report.py --check
python3 -m unittest discover -s ops/vyomaraj-core/handover -p 'test_*.py'
python3 -m unittest discover -s ops/availability -p 'test_*.py'
sha256sum ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_2026_10_04.txt
curl -s -D - -o /dev/null http://127.0.0.1:4174/reports/download/handover-notepad.txt
curl -s http://127.0.0.1:4176/api/availability
```

## Honest limitations

Both replicas share one sandbox, one checkout and one SQLite queue, and the gateway is itself a
single point of failure. The drill measures one GET per fault with process-level stops; it is not
an independent-site DR test, not a production RTO/RPO, and not a backup/restore or machine-loss
exercise. The preview stack is unauthenticated. Metadata counts are source-reported;
agent/provider operational readiness is not verified. Sandbox preview links are not durable
artifacts — the repository, not a preview URL, is the record that survives.
