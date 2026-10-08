# Primary ↔ secondary sync, DR test and package parity — 8 October 2026

**Scope of this record.** It states what was actually checked from this session, what was
repaired, and what still cannot be confirmed from here. It is a repository-level record.
It is not a production disaster-recovery certification, a failover drill, an RPO/RTO
measurement, or evidence that any application was installed or restored.

---

## 1. Headline: the DR verification pipeline was dead, and that was the real blocker

The request was "sync primary and secondary, run a DR test, confirm the same packages".
Before any of that could mean anything, the pipeline that performs it had to work.

The consolidated workflow `.github/workflows/vyomaraj-sync-both.yml` runs three jobs. The
`verify-or-sync` job — the one that actually compares primary against secondary — declares
`needs: offline-tests`. When `offline-tests` fails, `verify-or-sync` is **skipped**, not
failed, so nothing compares the two repositories and no annotation is produced.

That is exactly what had been happening.

| Fact | Value |
| --- | --- |
| Last `verify-or-sync` that actually ran | check-run `112880681037`, completed `2026-10-07T15:50:01Z` |
| Main at that time | `04b7ae60ce2855b1d48043d80f790488e894ee79` |
| Result then | `status=MATCH; data_match=true; primary_tree=secondary_tree=986288ee2cc4ec4d89400320150ea893f7a7a2de; traffic_switched=NONE` |
| First failing run after it | `37647660697`, `2026-10-07T15:53:39Z`, on main `ae92895` |
| Consecutive failed scheduled runs before this session | 37 |
| Outcome of every one of them | `offline-tests` **failure** → `verify-or-sync` **skipped** |
| Elapsed time with no primary↔secondary verification | ≈ 15 h 24 min (15:50 UTC 7 Oct → 07:14 UTC 8 Oct) |

So the honest statement of the starting position is: **the secondary had not been compared
to the primary for roughly sixteen hours, across four merges to main.** No sync and no DR
test could be claimed in that window, and none was.

## 2. Root cause: five canonical files were overwritten by the 7 October consolidation merges

The breakage was not flaky CI. Four "FINAL: …consolidate/reconcile…" merges (PRs #45–#48)
replaced files that were already the source of truth for other code, instead of adding
alongside them. Every clobbered file is listed here with the commit that did it.

| File | Clobbered by | What was lost | Consequence |
| --- | --- | --- | --- |
| `config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json` | `94deaa8` (PR #46) | 9,334-byte policy contract with the `inheritance` block → 2,516-byte summary | `rebuild_registry.py` raised `KeyError: 'inheritance'`; **30 errors** in the agents suite |
| `config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_MODEL.yaml` | `94deaa8` (PR #46) | JSON-formatted reference contract → narrative YAML | `capability_fabric` could not load it; the suite's `json.tool` gate failed |
| `ops/vyomaraj/capability_fabric.py` | `94deaa8` (PR #46) | 259-line read-only contract resolver → 29-line routing stub | `capability_fabric.py check` silently exited 0 **without checking anything** |
| `ops/engineering/verify_2026_stack.py` | `9ee4fbc` (PR #47) | repository inspector with `--check`/`--status` → dependency checker ignoring both flags | `process-control.sh status` and `final-readiness-gate.sh` broke |
| `ops/vyomaraj/publish-gate.sh`, `process-control.sh`, `final-readiness-gate.sh` | `9ee4fbc` (PR #47) | deny-by-default safety gates | see §3 |
| `docs/architecture/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE.md` | `9ee4fbc` (PR #47) | 8,914-byte document → 2,217-byte summary | current handover archives no longer matched the tree |

### 3. A safety regression, not only a test failure

Two of the clobbered items were deny-by-default guards, and the replacements did not deny:

- **`process-control.sh`** previously answered `start`, `stop`, `restart`, `failover` and
  `failback` with exit code 4 and `BLOCKED: … No legacy gateway/studio writer service was
  contacted`. The replacement printed a usage line and **exited 0** for all five. A caller
  checking the exit status would have read "failover succeeded".
- **`final-readiness-gate.sh`**, **`publish-gate.sh`**, `agent-change.sh`,
  `media-capability-gate.sh` and `run-content-alignment.sh` were written with a literal
  `\${BASH_SOURCE[0]}`. `$ROOT` therefore resolved to the wrong place, every required
  contract was reported `MISSING`, and the gate still **exited 0** — a gate that always
  passed without reading anything. `bash -n` accepts `\$`, so the syntax check never caught it.

Neither of these is hypothetical; both are reproduced in the restored tests.

A sixth artifact, `ops/vyomar/final-readiness-gate.sh`, was created at a **typo of the
directory name** by the same commit. It asserted an aspirational registry (15 categories /
168 sub-agents) that contradicts the reconciled registry (13 / 128), so it could never agree
with the canonical gate.

## 4. What was repaired

Every canonical file was restored from the last commit at which it was correct, and the
content that the consolidation merges were trying to add was **preserved additively** rather
than discarded:

- `verify_2026_stack.py` — the two divergent versions were **merged**. `--check`/`--status`
  keep the offline repository inspection; the engineering-baseline invariants, contract-file
  presence and the 128-agent inheritance check from the other version were folded in. Missing
  third-party modules are now reported as `engineering_runtime_dependencies: BLOCKED` (an
  environment fact) instead of a repository failure, and a new `--runtime` mode — the default
  when no flag is passed, which is how `bootstrap-2026.sh` calls it — still requires them.
- `capability_fabric.py` — the full resolver was restored and the routing helpers
  (`CAPABILITIES`, `capability_domains`, `authorize_capabilities`) were appended, so both
  APIs and both test files work.
- Preserved variants: `config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_SUMMARY_v1.0.json`,
  `config/engineering/HANUMAN_PANCH_BROTHER_CAPABILITY_COUNCIL_v1.0.yaml`,
  `docs/architecture/UNIVERSAL_KNOWLEDGE_EVOLUTION_SUMMARY_v1.0.md` — each carries a header
  naming the commit it came from and stating that it is not the authoritative contract.
- The five `\$`-escaped scripts were fixed. `ops/vyomar/final-readiness-gate.sh` now forwards
  to the canonical gate and prints a deprecation notice rather than acting as a second,
  divergent gate; its original text stays recoverable with `git show 9ee4fbc:…`.

**Result:** `run_offline_suites.py --ci` goes from `52/60` with 8 failures to **`61/61`** —
585 Python tests across 15 suites, 15 Node checks, 31 builders. Once this reaches `main`,
`verify-or-sync` stops being skipped and the 30-minute DR schedule resumes.

## 5. The DR test

### 5.1 From this sandbox — BLOCKED, as expected

```
DR_REPO=deepakGoyal1356/Vyomaraj-Agent-6d64e bash ops/dr/run-dr.sh test
```

```json
{
  "status": "BLOCKED",
  "detail": "GitHub HTTP 404: Repository/ref missing OR hidden by permissions; do not infer nonexistence.",
  "failed_http_status": 404,
  "traffic_switched": false,
  "requested_operation": "read_only_verification",
  "primary_repository": "Vyomaraj1356/Vyomarajai",
  "secondary_repository": "deepakGoyal1356/Vyomaraj-Agent-6d64e"
}
```

Exit code 2. The Arena credential is scoped to `Vyomaraj1356/Vyomarajai` only: it returns
404 for every candidate secondary path and 403 for `actions/variables`. **A 404 is ambiguous
— it does not prove the repository is absent.** This is the long-standing constraint recorded
against issue #6, not a new failure, and it is why the authoritative test must run inside
Actions with `VYOMARAJ_PAT`.

### 5.2 Inside Actions — restored, and now reports packages too

`ops/dr/actions_read_probe.py` runs with the real `VYOMARAJ_PAT` on any `arena/**` branch
push and performs a GET-only comparison of both repositories. It was extended in this change
to compute package parity as well, so its public annotation now ends with
`packages=…; package_identical_package_files=…; installed_environment_verified=false`.

Annotations carry counts and enums only — never filenames, file contents or credentials.

## 6. Package parity — "the same packages"

A new verifier, `ops/dr/package_parity.py`, answers this in both senses of the word.

### 6.1 What it inventories

Enumerated from `git ls-files`, so it covers exactly what DR replicates:

| Kind | Count | Bytes |
| --- | --- | --- |
| Dependency manifests | 4 | — |
| Distributable packages (`.zip`, `.apk`, `.tar.gz`) | 50 | — |
| **Total tracked package files** | **54** | **491,188,294** |

Each record carries the size, the SHA-256 and the **Git blob SHA**. The blob SHA is the point:
it can be compared directly against a GitHub tree entry, so a 24 MB APK is verified without
being downloaded.

### 6.2 Declaration consistency — PASS

All eight pins in `requirements-2026-lock.txt` satisfy the bounds in `requirements-2026.txt`,
`requirements-2026-patch.txt` agrees with the canonical bounds, and nothing is declared twice:

| Distribution | Locked | Declared bound |
| --- | --- | --- |
| `cryptography` | 46.0.0 | `>=42,<47` |
| `jsonschema` | 4.26.0 | `>=4.23,<5` |
| `PyYAML` | 6.0.3 | `>=6.0,<7` |
| `temporalio` | 1.34.0 | `>=1.34,<2` |
| `opentelemetry-api` | 1.45.1 | `>=1.37,<2` |
| `opentelemetry-sdk` | 1.45.1 | `>=1.37,<2` |
| `mcp` | 2.3.0 | `>=2,<3` |
| `a2a-sdk` | 1.2.2 | `>=1,<2` |

`pytest` is declared but deliberately unpinned; that is recorded, not failed.

### 6.3 Index availability — PASS (checked once, from this session)

`python3 ops/dr/package_parity.py --index` queried pypi.org: **all 8 locked releases exist**.
This confirms the lock file is installable in principle. It did **not** download, install,
resolve the transitive tree, or verify hashes or signatures. It is a network check and is
therefore deliberately excluded from the offline suite and from the committed inventory.

### 6.4 Primary vs secondary — BLOCKED from here

`package_parity.py --remote` returns the same 404 as §5.1. It is now wired into
`verify-or-sync` for both `verify` and `sync` modes, so every future DR run states the answer:
a package `MISMATCH` or a broken declaration fails the job; an access failure is recorded as
a warning and **never** reported as parity.

Note the logical relationship: package files are a subset of the tracked tree, so a tree
`MATCH` already implies package equality. The value of reporting it separately is that when
trees diverge, the next question — "did the dependency manifests or the release archives
change?" — is answered directly instead of requiring a manual diff.

## 7. What is still not true

- **No sync was performed.** Replication requires `workflow_dispatch` with `mode=sync` from
  primary `main`, `VYOMARAJ_DR_SYNC_ENABLED=true`, and a confirmed target.
  `DR_POLICY.json` keeps `sync_approved_on_main: false` while issue #6 is OPEN/P0, and this
  session has neither the permission nor the owner approval to change that.
- **The effective secondary is still unconfirmed.** The Actions variable `VYOMARAJ_DR_REPO`
  may override the in-repository fallback, and the Arena credential gets 403 on the Actions
  settings endpoints, so which repository the workflow actually writes to cannot be read
  from here. Owner confirmation remains required.
- **Issue #6 stays OPEN/P0.** Nothing here closes it.
- **Installed-environment parity is unverified.** Every statement above is about repository
  content. No `site-packages` directory, container image, or deployed host was compared.
  `installed_environment_verified` is `false` everywhere, by construction.
- **Still not evidence of:** runtime DR, failover, failback, RPO, RTO, traffic switching,
  APK signature validity, signer provenance, or real-device installation.

## 8. Reproduce

```sh
# Offline — no credentials, no network
python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci   # expect 61/61
python3 ops/dr/package_parity.py --check
python3 -m unittest discover -s ops/dr -p 'test_*.py'

# Package inventory and declaration report
python3 ops/dr/package_parity.py

# Network: confirm every locked pin exists on the index
python3 ops/dr/package_parity.py --index

# Credentialed, read-only (needs access to the confirmed secondary)
DR_REPO=<confirmed-owner/repository> bash ops/dr/run-dr.sh test
DR_REPO=<confirmed-owner/repository> python3 ops/dr/package_parity.py --remote
```
