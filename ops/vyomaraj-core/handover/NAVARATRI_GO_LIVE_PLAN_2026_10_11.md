# Vyomaraj — Navaratri 2026 go-live plan (Ghatasthapana, Sunday 11 October 2026)

**Written 6 October 2026 · four working days to the first night · single source of truth for the
launch.** Everything below states either something verified in this repository today or something
that must be decided or built. Nothing here is a promise that a date will be met: the dates are
the plan, and the gates are what make the plan real.

Festival anchors used throughout: **Ghatasthapana Sunday 11 October 2026**, **Maha Ashtami /
Maha Navami Monday 19 October 2026**, **Vijayadashami Tuesday 20 October 2026** (public almanac
references; the muhurat window for Ghatasthapana is given as 06:19–10:12 by those references,
with Abhijit 11:44–12:31). The owner's live date is the first night.

---

## 1. The one-page position, as of today

**Wiring status right now (generated, not asserted):** `verify_live_wiring.py` reports **0
blocking problems** against the running stack — viewer 4174, replicas 4181/4182 and gateway 4176
all answer the advertised routes, every download is byte-identical to the file on disk, and all
six lane packs resolve to the current agent registry. Read it yourself at `/reports/live-wiring`
(the JSON is `ops/vyomaraj-core/handover/LIVE_WIRING_STATE_2026_10_06.json`).

**What is real and verified in this repository right now**

- Music lane holds **63 starter cards** (was 39) including the new Sufi / ghazal / studio-show
  **format layer** and **four original programme formats** that are ours to produce.
- Local studio stack: report viewer (4174), replicas (4181, 4182), availability gateway (4176) —
  all `0.0.0.0`, all routes verified 200 in the last recorded preview run, downloads byte-identical.
- Agent and content wiring: 13 categories / 128 counted slots / 6 uncounted headings is
  **pinned and unchanged**; every lane pack's slots resolve against the current registry, and
  canonical names stay `UNKNOWN` where they are unknown.
- DR: the replication gate is fixed and the workflow now runs on this branch's pushes; the DR
  record carries 20 checkpoints + 16 writes, and the open window is documented, not hidden.
- Handover artifacts: canonical note (`8acd71f0…`), 41-member canonical package, 49-member
  post-PR25 companion package, all with manifests and tests.

**What is NOT real yet — do not let anyone present these as live**

| Item | Actual state | Consequence for 11 October |
|---|---|---|
| Production host | **Already solved, free**: GitHub Pages serves the product from `main` (status built). The Python stack is for local dry runs only | The launch address is the Pages URL, not a sandbox link — see §2.6 |
| Independent DR | Not verified (`zero_rpo_verified=false`, `zero_rto_verified=false`) | One machine losing its disk loses both replicas |
| APK | Inspected today: `Vyomaraj-App.apk`, 24,567,022 bytes, sha256 `948e60b0…`, 222 zip entries, 8 dex files, `AndroidManifest.xml` present — and **no signature block**, so a stock Android device rejects it. No Android project (Gradle, manifest source, Java/Kotlin) exists in this repository, so it cannot be rebuilt or re-signed here | Must be rebuilt and signed from its original project, then installed on real devices, before it appears on the launch page |
| Voice / biometric enrollment | **On-device path now implemented** (`voice_enrollment.py` + policy + 14 tests): consent text, delete-my-voice, no upload path, guard that fails the build if a template ever lands in the repo | Free, no vendor, no contract. Capture UI wires into the lanes on Day 2 |
| Content media | No recording, episode, lyric, artwork or brand asset is hosted — by design | Launch programming must be our own produced material |
| Publications/domains | Not registered here; DNS and TLS are outside this repo | Register and point before 11 October |

---

## 2. Decisions only the owner can make

**Budget rule for this launch: nothing is bought.** No host, no domain, no vendor, no gateway. The
free stack is already working (Pages + Actions + the local servers). Purchases wait until Vyomaraj
earns — the order to buy in is in `STACK_AND_PLATFORM_RECORD_2026_10_06.md` section 5.

Blocks the launch if unanswered:
1. **The nine opening programmes** — which four of the new originals record first, in which order,
   and who signs them off (trilingual proof: Hindi, English, Hinglish).
2. **The APK** — sign the existing binary with a key you hold (`keytool`, free) and publish it as a
   direct download, **or** leave it off the launch page until its project is recovered. Self-signed
   means an "unknown source" warning on the phone; that is acceptable, an unsigned file is not.
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

### Day 0 — today, 6 October (remaining hours)
- **Merge the open pull request (#27).** That merge triggers `verify-or-sync`, which becomes
  **checkpoint #21**, replicates the two unpublished commits to the secondary and closes the
  open replication window. Nothing else on this list matters until the gate is green.
- Owner answers §2, at minimum questions 1, 3 and 4.
- Confirm the music lane's new cards render: `/music/` shows 63 cards, the new tradition and
  show-format filters return results, and `/reports/contents` lists them.

### Day 1 — Wednesday 7 October · wiring day
- Run the **live-wiring verifier** (`python3 ops/vyomaraj-core/handover/verify_live_wiring.py`)
  against the running stack; fix every reported problem, then re-run until clean. This is the
  "agents and contents linked" gate: routes, byte identity, pack-to-registry bindings, downloads.
- Confirm the **Pages build** for the launch commit and open the Pages URL on a real phone. The
  Pages address is the launch address; nothing needs registering or paying for.
- **APK QA:** the committed binary is unsigned and unrebuildable from this repository (§1), so
  today the work is: recover or recreate the Android project, set a version name and version
  code, sign with the owner-held keystore, install on two real devices (one low-end Android, one
  current), and record the build metadata here. If that cannot be done by Day 1, the APK does not
  go on the launch page — an unsigned binary is worse than no binary.
- **Voice enrollment:** the policy, consent text, withdrawal control and the repository guard are
  already implemented and tested (`ops/vyomaraj-core/experience/voice_enrollment.py`,
  `VOICE_ENROLLMENT_POLICY.json`, 14 tests). Day 1 adds the capture screen to the product page:
  read three phrases, keep the template in browser storage, show the delete button beside it.
- Content: freeze the nine-night programme outline; commission the first four originals; put the
  credit line (poet, composer, performer, source) on every piece before recording.

### Day 2 — Thursday 8 October · build day
- Implement and land the enrollment work from Day 1 behind the consent gate, with tests that fail
  if a voice template is ever written to a repository path or a server upload.
- Build the launch web stack on the free route: the static product on Pages, and the four local
  processes only for dry runs. Add a page the owner can open on a phone to see the wiring state
  (`/reports/live-wiring`). **Do not** claim DR: Pages is hosting, not disaster recovery.
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
- Regenerate the evidence set one last time (preview verification, test evidence, live-wiring
  state) and commit it; capture the commit hash in the launch record.
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
   sandbox and takes the festival opening with it. Fix: Pages is the launch address (free, already
   built); sandbox links are for dry runs only and are labelled as such.
2. **No disaster recovery.** One disk, both replicas. Fix: at minimum, runtime database backups
   with a tested restore (Day 2-3) plus the Git-snapshot replication that already runs.
3. **Unverified APK.** Fix: sign it with a key the owner holds (free) and test on real devices, or
   drop it from the launch page (§3, Day 1).
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
| Music lane (63 cards, new format layer) | `/music/` | replicas 4181/4182, gateway 4176 | live in preview |
| Film, Bhakti, Comics, Pairings, Aghor, Research lanes | `/film/`, `/bhakti/`, `/comics/`, `/pairings/`, `/aghor/`, `/research/` | same | live in preview |
| Agents and ownership | `/agents/`, `/reports/agents` | same | live in preview |
| All contents index | `/reports/contents` | same | regenerated today |
| Handover notepad (canonical) | `/reports/handover-notepad` | viewer 4174 + gateway | live, byte-identical download |
| Post-PR25 companion | `/reports/post-pr25-handover` | viewer + replicas + gateway | live, byte-identical download |
| DR sync results (20 checkpoints, open window) | `/reports/dr-sync` | viewer + replicas | live |
| This plan | `/reports/go-live` | viewer + replicas | added with this document |
| Live wiring state (generated) | `/reports/live-wiring` | viewer + replicas | added with this document |
| Stack, platforms and archive record | `/reports/stack` | viewer + replicas | added 6 October — answers "what did we build on" |

---

## 7. Owner sign-off lines

- [ ] Day 0 — PR #27 merged and checkpoint #21 recorded
- [ ] Day 1 — Pages URL confirmed on a phone as the launch address, APK decision made, enrollment capture screen added
- [ ] Day 2 — launch stack confirmed on the free route, runtime backup + restore recorded, test run #1 complete
- [ ] Day 3 — dry run #2 complete, content proofed trilingually, rollback rehearsed
- [ ] Day 4 — freeze, evidence snapshot committed, runbook printed
- [ ] Day 5 — go live inside the Ghatasthapana window

**END OF GO-LIVE PLAN**
