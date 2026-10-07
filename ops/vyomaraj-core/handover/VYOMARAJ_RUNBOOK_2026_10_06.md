# VYOMARAJ — RUNBOOK: CONFIGURE · INTEGRATE · INHERIT · VERIFY

Generated 2026-10-07 04:08 UTC. The procedure for running this project, in the order it should be done. Copy-pasteable. Every command is run from the repository root.

---

## A · Start everything (sandbox or laptop)

Five servers, five terminals, or five background processes. Bind `0.0.0.0` so a browser elsewhere can reach them.

| # | Command | Serves |
|---|---|---|
| 1 | `python3 ops/vyomaraj-core/experience/product_server.py --port 3000` | product pages + `/api/sync/status` + `/api/realtime` |
| 2 | `python3 ops/vyomaraj-core/handover/preview_reports.py --port 4174` | reports viewer, downloads, captures |
| 3 | `python3 ops/vyomaraj-core/experience/studio_server.py --port 4181 --home aghor` | lane studio A |
| 4 | `python3 ops/vyomaraj-core/experience/studio_server.py --port 4182 --home aghor` | lane studio B |
| 5 | `python3 ops/availability/gateway.py --port 4176 --primary-port 4181 --secondary-port 4182` | failover rehearsal gateway |

Do not use `python3 -m http.server` for the product page: it cannot answer the status routes, which is exactly the fault that was fixed. Use `product_server.py`.

---

## B · Verify (run this before trusting anything)

```bash
python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci   # tests, node checks, builders
python3 ops/vyomaraj-core/handover/verify_live_wiring.py       # every route on every server
python3 ops/vyomaraj-core/handover/verify_preview.py           # page contracts + packages
python3 ops/vyomaraj-core/handover/realtime_status.py          # live port probe as JSON
python3 ops/vyomaraj-core/handover/probes.py --once             # manual, fixed-loopback snapshot
```

`probes.py --once` appends to `/tmp/vyomaraj-probes.jsonl` and atomically writes `/tmp/vyomaraj-probes.latest.json`; `/reports/monitor` reads that latest file and never starts a probe. This is a local manual preview check, not scheduled or production monitoring, alerting, replication-lag, backup, or independent-site DR.

Rule learned the hard way: **restart the servers before running the verifiers**, or a route added in this session will read as 404 and look like a failure.

---

## C · Regenerate the evidence after any change

Order matters. Generated documents first, then the packages that embed them.

```bash
for b in build_stack_record architecture_diagram build_market_readiness build_full_handover \
         build_configuration_report build_ai_handoff; do
  python3 ops/vyomaraj-core/handover/$b.py
done
python3 ops/vyomaraj-core/handover/build_transfer_package.py
python3 ops/vyomaraj-core/handover/build_post_pr25_package.py
```

Each builder also supports `--check`, which fails if the checked-in copy has drifted.

---

## D · Configure a real thing (procedure that has worked here)

1. **Measure first.** Probe the current state; never assume.
2. **Write the smallest checkable artifact** — JSON or Markdown — that states the new fact.
3. **Add a `--check`** so the artifact cannot silently drift.
4. **Gate it** by adding the command to `run_offline_suites.py`.
5. **Wire it** to the viewer, both lane studios and the gateway.
6. **Add it to the verifier's required files** so a missing file is a failure.
7. **Restart the servers**, re-run the gates, regenerate, commit.

This is why the project can be trusted: every claim has a command that fails when the claim stops being true.

---

## E · Integrate with a platform (the honest sequence)

| Step | Do this | Cost |
|---|---|---|
| 1 | Publish by hand from the owner's own account | ₹0 |
| 2 | Add a contact address to the page so a viewer can reach the owner | ₹0 |
| 3 | Add a free analytics counter and confirm it records a visit | ₹0 |
| 4 | Grow the audience until the platform's own threshold is met | ₹0 |
| 5 | Only then request API access for automation | ₹0, needs review |
| 6 | Only after earnings: host, domain, payments, vendors | paid |

Do not build a publisher before there is published content — and do not promise a platform integration in any document until an API call exists in code with a credential behind it.

---

## F · Inherit content correctly

| Take | Leave |
|---|---|
| The format: how a Sufi/qawwali or ghazal performance is structured and credited | The recording, the lyrics, the melody |
| The studio-show shape: house band, guest pairing, one episode one story | The show's name, branding or episode content |
| The documentation habit: name every creator, record every source | Any claim of endorsement by a named artist |

The test that enforces this in the repository fails the build if inherited titles, lyrics or artwork are copied in.

---

## G · Recover, hand over, and protect

- **Hand over:** `build_full_handover.py` and `build_ai_handoff.py` produce the documents and the downloadable archives. Both are safe to share: no token, no credential, no environment file, and the owner's email is redacted in the AI-facing one.
- **Back up:** replication is a GitHub Actions job (`verify-or-sync`) on every push plus a schedule. It replicates **tracked files**, never runtime state, and never force-pushes; the prior secondary commit is the rollback parent.
- **Protect:** the reports viewer serves an allowlist only and sends a hardened `Content-Security-Policy`. Same-origin images are permitted (`img-src 'self'`); scripts and external hosts are not.

---

## H · The three free actions that make it earn-capable

1. **Sign the APK** with the owner's own key: `keytool -genkeypair` then `apksigner`; publish the signed file. Android refuses the current unsigned build.
2. **Publish a contact address** on the public page.
3. **Switch on a free analytics counter** and confirm one real visit is recorded.

Then hand-publish the first episodes and apply to the YouTube Partner Program **before 1 February 2027** — the threshold for new applicants rises to 8,000 watch hours that day, from 4,000 today. The 500-subscriber tier opens fan funding earlier at 3,000 hours.

---

## I · Known limits, stated so nobody is surprised

| Limit | Consequence |
|---|---|
| Preview links are session-scoped | they die with the sandbox; the Pages URL is the durable address |
| `flow-diagram.html` loads Mermaid from a CDN | on a network that blocks that CDN, the diagrams do not render |
| No analytics | nobody can see visits |
| No login | no returning audience |
| No payments | nothing can be sold |
| DR covers files, not runtime | a live database would not be covered |

