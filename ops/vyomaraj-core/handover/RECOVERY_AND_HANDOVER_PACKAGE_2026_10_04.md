# Recovery and handover package — 2026-10-04

**This page is generated from the repository, not from memory.** It describes exactly what
was reported lost after the sandbox re-provision, what was rebuilt in this session, and how a
reader can re-verify every claim in it.

## What was reported lost

| Item | Status in this checkout |
|---|---|
| Local commits `65dda1e`, `1b496d2` | ABSENT — not in this clone's history and not on any remote ref |
| Prior note `NEXT_SESSION_HANDOVER_2026_10_03.txt` (reported SHA256 `9d5fc218…`) | ABSENT — bytes unrecoverable here; **not** reproduced byte-for-byte |
| Root-level copies of the note, Git bundle and ZIP | ABSENT from `/home/user` |
| `/reports/next-session`, `/reports/recovery`, `/reports/download/next-session.txt` routes | ABSENT — rebuilt and now live |
| Drill/verification evidence for the above | ABSENT — re-run and re-recorded with real observations |

The exact prior file bytes could not be recovered from the repository, its remote branches,
its tags or the working tree. The previous session's hash `9d5fc218…` is therefore **not**
re-asserted anywhere in this work; the rebuilt note is a new document with a new SHA256.

## What was rebuilt and committed in this session

- `NEXT_SESSION_HANDOVER_2026_10_04.txt` — canonical next-session handover (this package's
  primary document). The viewer's download route serves it byte-for-byte.
- `RECOVERY_AND_HANDOVER_PACKAGE_2026_10_04.md` — this page.
- `preview_reports.py` — added `/reports/next-session`, `/reports/recovery`,
  `/reports/download/next-session.txt`, `/reports/download/transfer-package.zip` and nav links.
- `studio_server.py` — the same four routes on the replicas behind the gateway (port 4176).
- `build_transfer_package.py` — deterministic builder for the package below.
- `TRANSFER_MANIFEST_2026_10_04.json` — SHA256 of every packaged member plus the package itself.
- `PREVIEW_VERIFICATION_2026_10_04.json` — recorded route checks and byte-identity checks.
- `ops/availability/LOCAL_FAILOVER_DRILL_2026_10_04.json` — the controlled failover drill re-run with
  real HTTP responses on 2026-10-04 05:45 UTC.

## Package contents

| Member | Purpose |
|---|---|
| `NEXT_SESSION_HANDOVER_2026_10_04.txt` | Canonical handover note for the next session |
| `RECOVERY_AND_HANDOVER_PACKAGE_2026_10_04.md` | This recovery page |
| `HANDOVER_ALL_UPDATES_2026_10_03.txt` | Existing reconstructed roster/catalog handover |
| `preview_reports.py`, `studio_server.py`, `gateway.py` | The served preview components |
| `test_preview_reports.py`, `test_transfer_package.py`, `test_gateway.py` | Offline checks |
| `LOCAL_FAILOVER_DRILL_2026_10_03.json`, `LOCAL_FAILOVER_DRILL_2026_10_04.json` | Drill evidence |

No secrets, tokens, PATs, environment files or private configuration are included. The
package is deliberately small (documents plus scripts) so it can be reviewed by a human.

## How to re-verify (all read-only, from the repository root)

```
python3 -m unittest discover -s ops/vyomaraj-core/handover -p 'test_*.py'
python3 -m unittest discover -s ops/availability -p 'test_*.py'
sha256sum ops/vyomaraj-core/handover/NEXT_SESSION_HANDOVER_2026_10_04.txt
curl -s -D - -o /dev/null http://127.0.0.1:4174/reports/download/next-session.txt
curl -s http://127.0.0.1:4176/api/availability
```

## Honest limitations

Both replicas share one sandbox, one checkout and one SQLite queue, and the gateway is itself
a single point of failure. The drill measures one GET per fault with process-level stops; it
is not an independent-site DR test, not a production RTO/RPO, and not a backup/restore or
machine-loss exercise. The preview stack is unauthenticated. Metadata counts are
source-reported; agent/provider operational readiness is not verified.
