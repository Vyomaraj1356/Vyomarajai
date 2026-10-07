# Vyomaraj — Navaratri 2026 go-live plan (Ghatasthapana, Sunday 11 October 2026)

**Written 6 October 2026 · updated with a live-state correction on 7 October 2026.** The day-by-day
schedule below is the original plan, not a guarantee. Current live read: Pages still serves `main`
at `04b7ae60`; this branch is not deployed. PR #41 remains open with combined DR and preview scope;
P0 issue #6 remains owner/admin-blocked. The preview gate passes its static scope, while production
remains blocked. The 11 October date is a target, not a guarantee.

Festival anchors used throughout: **Ghatasthapana Sunday 11 October 2026**, **Maha Ashtami /
Maha Navami Monday 19 October 2026**, **Vijayadashami Tuesday 20 October 2026** (public almanac
references; the muhurat window for Ghatasthapana is given as 06:19–10:12 by those references,
with Abhijit 11:44–12:31). The owner's live date is the first night.

---

## 1. The one-page position, as of today

**Point-in-time wiring status (not a current production claim):** the 7 October route checks passed;
`LIVE_WIRING_STATE_2026_10_06.json` records its 0-blocking result at 06:11 UTC for viewer 4174,
gateway 4176 and lane studios 4181/4182. After the checks, the unauthenticated write-capable
gateway and studios were stopped. A follow-up port/process probe at 08:15 UTC found no listener on
3000, 4174, 4176, 4181 or 4182. The recorded PASS is historical, not evidence of current service
availability, production security or DR.

**What is real and verified in this repository right now**

- Music lane holds **63 starter cards** (was 39) including the new Sufi / ghazal / studio-show
  **format layer** and **four original programme formats** that are ours to produce.
- Preview server code exists. The viewer at 4174 is read-only and session-scoped; the gateway
  and studios at 4176/4181/4182 were stopped after the point-in-time route check because they were
  unauthenticated and write-capable. At the 08:15 UTC follow-up probe, all checked preview
  listeners (3000/4174/4176/4181/4182) were stopped. Do not restart writer services on a publicly
  reachable preview.
- Agent and content wiring: 13 categories / 128 counted slots / 6 uncounted headings is
  **pinned and unchanged**; every lane pack's slots resolve against the current registry, and
  canonical names stay `UNKNOWN` where they are unknown.
- DR: historical records contain a matching Git snapshot through the PR #40 main tip. As of
  7 October, the exact existing secondary and Actions access are unverified (secondary-name probes
  returned 404; Actions variables/secrets returned 403); no new replication was attempted. Issue
  #6 remains OPEN/P0 and owner/admin-blocked. Do not claim the current target is synchronized.
- Handover artifacts: canonical note (`8acd71f0…`), 41-member canonical package, 49-member
  post-PR25 companion package, all with manifests and tests.

**What is NOT real yet — do not let anyone present these as live**

| Item | Actual state | Consequence for 11 October |
|---|---|---|
| Pages hosting | GitHub Pages is built from `main` at `04b7ae60` (live read 7 Oct); this branch's new preview is not deployed. The Python stack is local/session-scoped only | The Pages URL exists, but it still serves the older `main` content until an owner-reviewed merge and successful Pages build |
| Independent DR | Current secondary access/sync unverified; historical Git snapshot records only (`zero_rpo_verified=false`, `zero_rto_verified=false`) | No supported claim of independent-site or runtime recovery; issue #6 remains the owner/admin gate |
| APK | `Vyomaraj-App.apk`, 24,567,022 bytes, sha256 `948e60b0…`, 222 ZIP entries, 8 dex files and `AndroidManifest.xml` present. Current parser finds v2 signing-block ID `0x7109871a`; cryptographic validity, signer provenance and device installation are **unverified**. No Android source project exists here | Run `apksigner verify`, review signer provenance, recover trusted source if needed, and test on a real device. Keep it off release downloads until all checks pass |
| Voice / biometric enrollment | **On-device path now implemented** (`voice_enrollment.py` + policy + 14 tests): consent text, delete-my-voice, no upload path, guard that fails the build if a template ever lands in the repo | Free, no vendor, no contract. Capture UI wires into the lanes on Day 2 |
| Content media | No recording, episode, lyric, artwork or brand asset is hosted — by design | Launch programming must be our own produced material |
| Publications/domains | Not registered here; DNS and TLS are outside this repo | Register and point before 11 October |

---

## 2. Decisions only the owner can make

**Budget rule for this launch: nothing is bought.** GitHub Pages currently serves `main`; Actions
workflow definitions exist, but the current secondary target/authorization is unverified. All
checked preview listeners (3000/4174/4176/4181/4182) were found stopped by the 08:15 UTC
follow-up probe; the unauthenticated gateway/studios were stopped after checks. Purchases wait
until Vyomaraj earns — the order to buy in is in
`STACK_AND_PLATFORM_RECORD_2026_10_06.md` section 5.

Blocks the launch if unanswered:
1. **The nine opening programmes** — which four of the new originals record first, in which order,
   and who signs them off (trilingual proof: Hindi, English, Hinglish).
2. **The APK** — verify the existing v2 signing block with `apksigner verify`, confirm the signer
   is trusted, and install on a real Android device. If signature validity or provenance is unknown,
   recover the original source and rebuild; otherwise keep the APK off public release downloads. The
   repository does not include an Android source project or a device/signing environment.
3. **Launch address** — confirm `https://vyomaraj1356.github.io/Vyomarajai/` as the 11 October
   address (free, already built). A bought domain can replace it later without changing anything
   else.

Answered by default unless the owner objects:
4. **Voice enrollment** — on-device only, as implemented. No cloud vendor, no cloning of anyone
   else's voice, no identity-document capture.
5. **Identity / KYC** — `uidai.in` **web only**. In-app Aadhaar capture needs AUA/KUA licensing and
   legal review; that is a post-earnings purchase, not a launch blocker.

---

## 3. Day-by-day plan

### Day 0 — historical schedule from 6 October (superseded)
- The original plan named PR #27 and predicted a new checkpoint. That instruction is stale and is
  not authorization to merge. Current live read: PR #41 is open with combined DR/preview scope,
  and its PR-event `verify-or-sync` was skipped. Issue #6 remains OPEN/P0; do not infer a current
  replication result or dispatch a workflow. Owner/admin access and explicit review are required.
- Owner answers §2, at minimum questions 1, 3 and 4.
- Confirm the music lane's new cards render: `/music/` shows 63 cards, the new tradition and
  show-format filters return results, and `/reports/contents` lists them.

### Day 1 — Wednesday 7 October · wiring day
- Run the **offline suite** against the checkout. Live route verification is optional only in a
  secured, isolated test environment; the writer-capable preview services are currently stopped.
  Do not restart them on a public preview just to make the live verifier green. A verifier PASS is
  route evidence only, not production authorization.
- After explicit owner review/merge of the preview PR, confirm a new **Pages build** for that
  commit, then open the Pages URL on a real phone. The Pages address is free, but currently serves
  `main` at `04b7ae60`; this branch is not live there yet.
- **APK QA:** the committed binary has a v2 signing-block entry, but validity and provenance are
  unknown and the repository has no Android source project. Run `apksigner verify` with a trusted
  Android SDK, identify/approve the signer, and install the exact hash on a real device. If those
  checks cannot be completed, the APK stays off the launch page; a structurally present signing block
  is not proof of a trustworthy or installable release.
- **Voice enrollment:** the policy, consent text, withdrawal control and the repository guard are
  already implemented and tested (`ops/vyomaraj-core/experience/voice_enrollment.py`,
  `VOICE_ENROLLMENT_POLICY.json`, 14 tests). Day 1 adds the capture screen to the product page:
  read three phrases, keep the template in browser storage, show the delete button beside it.
- Content: freeze the nine-night programme outline; commission the first four originals; put the
  credit line (poet, composer, performer, source) on every piece before recording.

### Day 2 — Thursday 8 October · build day
- Implement and land the enrollment work from Day 1 behind the consent gate, with tests that fail
  if a voice template is ever written to a repository path or a server upload.
- For launch, keep Pages static and use the four local processes only for dry runs. The current
  branch preview is not production until review, merge and a successful Pages build. The reports
  viewer shows the wiring state (`/reports/live-wiring`). **Do not** claim DR: Pages is hosting, not
  disaster recovery.
- Database: confirm where runtime state lives (the research store and queue), take a backup of it,
  and record the restore steps. Git-snapshot DR does not cover runtime databases.
- **Full test run #1** with all configurations: web routes, app flows, music/film/bhakti/comics
  lanes, approvals and finance desks, plans, downloads — every screen at phone width.

### Day 3 — Friday 9 October · rehearsal day
- **Full dry run #2** end to end on the production host, following the runbook exactly as it will
  be followed on the 11th, including the rollback step.
- Load and soak: the same host serving the four processes for several hours; note the ceiling and
  write it down honestly.
- Proof the content: trilingual review of every opening programme; legal read of the credit and
  licence lines; confirm no rehosted media anywhere.
- Backups: verify a restore actually works, on a copy, and record how long it took.

### Day 4 — Saturday 10 October · freeze
- Content freeze. No copy, card or programme changes after this point without the owner's word.
- Regenerate the offline evidence set. Run live-wiring verification only in a secured, isolated
  test stack; the current writer endpoints are stopped. Commit or deploy only after explicit owner
  approval; capture any approved commit hash in the launch record.
- On-call: who watches what, what page they open first, who can stop the launch, and the exact
  rollback command. Print the runbook; the phone will be busy.

### Day 5 — Sunday 11 October · **go live**
- Open in the Ghatasthapana window (06:19–10:12 muhurat; Abhijit 11:44–12:31).
- First night programme: `original-navaratri-cycle` night 1, with the bhakti lane's first night.
- Announce only what the live-wiring verifier and the health check can show on the screen in
  front of you.

---

## 4. The gates (a feature ships only if all three pass)

1. **Wiring gate** — `verify_live_wiring.py` reports no problems: every advertised route answers,
   every download is byte-identical to its source, every lane pack resolves to the registry.
2. **Evidence gate** — offline suites green (currently 350 tests, 12 Node checks, 14 builders) and
   the generated documents match their builders (`--check` clean).
3. **Truth gate** — anything not verified is described as unverified in the same sentence it is
   mentioned. No "live", "paid", "integrated" or "DR-ready" language without a recorded check.

---

## 5. Risks, in order of what actually kills a launch

1. **A sandbox link is not a host.** If the launch address is a preview link it dies with its
   sandbox. Pages is free and serves `main` at `04b7ae60`, but this feature branch is not deployed.
   Fix: owner-review/merge explicitly, then verify a successful Pages build; keep the session viewer
   labelled as a preview only.
2. **DR target and current synchronization unverified.** Historical Git-snapshot matches do not
   prove current access or independent-site recovery. Fix: owner/admin confirms the exact existing
   target and authorizes access; then run an approved replication and verify a fresh tree match,
   rollback evidence, and separately tested runtime backups before making any DR claim.
3. **Unverified APK release.** Fix: run `apksigner verify`, review signer provenance, and install
   the exact artifact on a real device; if any check is unresolved, keep it off release downloads.
4. **Identity documents.** Aadhaar work stays on `uidai.in` web; no in-app biometric capture
   without the paperwork. Fix: legal review scheduled, feature not promised for the 11th.
5. **Content rights.** The new Sufi/ghazal/show cards are context only; the launch needs our own
   recordings. Fix: commission and record the four originals first, credit them properly.
6. **Notifications and payments.** The approvals, finance and upgrade desks draft only; they send
   nothing, and with no gateway there is no payment rail. Do not announce either on the 11th.
7. **The money trap.** A document in this repository claims PostgreSQL, Redis, FastAPI, Flask,
   live social APIs and revenue figures. None of it runs here (section 3 of
   `STACK_AND_PLATFORM_RECORD_2026_10_06.md`). Quoting those numbers to a partner or a buyer would
   be the fastest way to lose the room.

---

## 6. Where each live thing is meant to sit (the wiring map)

| Surface | Route | Served by | State today |
|---|---|---|---|
| Music lane (63 cards, new format layer) | `/music/` | studios 4181/4182 + gateway 4176 | defined in repo; preview writers stopped; not production |
| Film, Bhakti, Comics, Pairings, Aghor, Research lanes | `/film/`, `/bhakti/`, `/comics/`, `/pairings/`, `/aghor/`, `/research/` | same | defined in repo; preview writers stopped |
| Agents and ownership | `/agents/`, `/reports/agents` | studio/gateway preview | local-only route; studios/gateway stopped |
| All contents index | `/reports/contents` | viewer 4174 | read-only report route; session-scoped |
| Handover notepad (canonical) | `/reports/handover-notepad` | viewer 4174 | read-only route; session-scoped |
| Post-PR25 companion | `/reports/post-pr25-handover` | viewer 4174 | read-only route; byte-identity verified at prior check |
| DR sync results | `/reports/dr-sync` | viewer 4174 | historical evidence only; current DR target/access unverified |
| This plan | `/reports/go-live` | viewer 4174 | read-only, session-scoped |
| Live wiring state (generated) | `/reports/live-wiring` | viewer 4174 | timestamped pre-shutdown observation; not current service proof |
| Stack, platforms and archive record | `/reports/stack` | viewer 4174 | read-only, session-scoped |

---

## 7. Owner sign-off lines

- [ ] Day 0 — original PR #27/checkpoint #21 step superseded; current issue #6 remains OPEN/P0 and owner/admin-blocked
- [ ] Day 1 — Pages URL confirmed on a phone as the launch address, APK decision made, enrollment capture screen added
- [ ] Day 2 — launch stack confirmed on the free route, runtime backup + restore recorded, test run #1 complete
- [ ] Day 3 — dry run #2 complete, content proofed trilingually, rollback rehearsed
- [ ] Day 4 — freeze, evidence snapshot committed, runbook printed
- [ ] Day 5 — go live inside the Ghatasthapana window

**END OF GO-LIVE PLAN**
