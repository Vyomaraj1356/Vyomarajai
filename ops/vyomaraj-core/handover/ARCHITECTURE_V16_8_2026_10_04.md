# Vyomaraj AI Agent OS — Architecture V16.8 — 2026-10-04

**Owner-approved architecture upgrade, integrated without deleting any old structure, function
or feature.** This document describes the complete governing principle and every layer of the
Vyomaraj platform as requested by the owner on 4 October 2026, and records where each layer
lives in this repository. The interactive diagram is `flow-diagram.html`; the earlier layers
(main control and recovery) are preserved and the new layers are added on top of them.

## 1. The one governing principle

```
You (Owner)
  → ShriYantra (authority and control root)
    → Vyomaraj/Bharath (central intelligence)  +  Jarvis/Laxman (coordination and content movement)
      → Agents and sub-agents (sovereign + 13 main-agent categories + sub-agents)
        → Content creation and verification (comics, film, music, bhakti, food, education, research…)
          → OWNER APPROVAL — central nostalgic camera queue (approve / reject / rework / submit)
            → Approved publishing (never automatic; every item passes the camera first)
              → Social platforms (YouTube, Instagram, Facebook, TikTok, X, Telegram, WhatsApp…)
                → Analytics and monetization (revenue dashboard, CPM, subscriptions, collabs)
                  → Finance and audit follow-up (payments, delayed payments, reminders)
                    → Learning and improvement (Evolution self-refining loop)
                      → back to the agents
```

- **Hermes** guards integrity and recovery across the **entire** process — every layer, not
  just the recovery lane.
- **Arena** executes approved tasks. It is **not** the owner and **not** the authority root.
- **Vyomaraj and Jarvis are the owner's left and right buddies.** They always notify the
  owner — every decision point, every escalation, every morning briefing.

## 2. The layers, and where they live

| Layer | What it is | Where it lives |
|---|---|---|
| Owner | Deepak Goyal (Vyomarajai@gmail.com), Owner primary locked | Repository owner; approvals desk |
| ShriYantra | Authority and control root; every instruction is aligned here before anything moves | Authority chain recorded in every governance module |
| Vyomaraj/Bharath | Central intelligence: validates, routes, assembles plans | `ops/vyomaraj-core/experience/local_planner.py` (deterministic router) |
| Jarvis/Laxman | Coordination and content movement: handoffs, review gates, routing to the owner gate | `role_handoff` in every planner; `ops/jarvis/` |
| Agents and sub-agents | 11 sovereign roles + 13 main-agent categories + sub-agents (133 historical slots) | `ops/vyomaraj-core/agents/` (current registry) |
| Content creation & verification | Comics (trilingual hi/en/hinglish, past+future versions), film, music, bhakti, food, education, research lanes | `ops/vyomaraj-core/*-experience/`, `ops/vyomaraj-core/research/` |
| Owner approval — nostalgic camera | Wooden old-style shutter camera; queue dropdown; video+sound review; approve/reject/rework/submit with voice instructions; the same cycle repeats for reworked items | `ops/vyomaraj-core/approvals/` (viewer `/approvals/`) |
| Approved publishing | Nothing publishes without the owner's camera decision; the gate stays recorded | `owner_gate` in every plan; approvals records |
| Social platforms | Platform roster and contracts | `ops/hanuman/social-platforms.json`, `ops/vyomaraj-core/handover/SOCIAL_PLATFORMS_CONTRACTS.json` |
| Analytics & monetization | Revenue dashboard data lane | Revenue lanes in the experience packs |
| Finance & audit follow-up | Payment reminders (gentle email → firm email → call script → owner escalation), delayed-payment tracking, audit checks before any reminder | `ops/vyomaraj-core/finance/` (viewer `/finance/`) |
| Morning briefing | Every morning, updates and data to the owner by voice, email, text or WhatsApp | `ops/vyomaraj-core/finance/finance_followup.py` (briefing drafts) |
| Learning & improvement | Evolution self-refining loop feeding back into the agents | Evolution lane (sovereign roles) |
| Integrity & recovery guard | Hermes: integrity and recovery across the whole path; DR snapshot replication primary ↔ secondary | `ops/dr/`, Hermes sovereign role |
| Change management (post-deployment) | Owner instruction → ShriYantra alignment → agent coordination → version-controlled change → separate testing → permission → upgrade; backup plan + rollback on failure | `ops/vyomaraj-core/upgrades/` (viewer `/upgrades/`) |

## 3. Hardware / software and multi-AI integration layer

The owner asked for multiple AI agents, hardware and software integration, a high-pixel
camera, voice and audio, a content creator mixer, Meta AI alignment, and 3D/4D/5D integration
— with a clear rule for **who picks what, and how, for the best results**:

- **Who picks:** Vyomaraj/Bharath (central intelligence) selects the lane and the agent slot;
  Jarvis/Laxman coordinates the handoff; the owner approves the result in the camera queue.
  No external AI provider is called automatically (`ai_calls_made: false` everywhere).
- **High-pixel camera:** the owner's review device for the central nostalgic camera — capture
  quality is a device property, not a repository claim; the queue plays the item's video and
  sound for review.
- **Voice and audio:** Jarvis voice lane (bilingual Devanagari/Hinglish, wake words, family
  voices) proposes narration; the comics and film lanes carry Hindi/English/Hinglish samples.
- **Content creator mixer:** the film lane's local cut room (authorized files only, hard cuts,
  edit-decision export) and the music lane's programme planner.
- **Meta AI alignment:** the platform stays aligned with the Meta AI family
  (Llama 3/3.1/3.2/3.3, Emu Video/Edit, SeamlessM4T, Voicebox) as recorded in the sovereign
  and platform lanes — alignment is configuration, not an automatic call.
- **3D/4D/5D:** experience modes exist in the planner (`3d`, `4d`, `5d`) as planning modes,
  not physical sensory claims.

## 4. The nostalgic camera approval cycle (exact behaviour)

1. Vyomaraj and Jarvis finish creation and verification and place the candidate in the
   **queue**, shown as a **dropdown**.
2. The owner **picks** an item; the **wooden shutter opens**; the item's **video and sound
   play** for review.
3. The owner takes the appropriate action: **approve**, **reject**, **rework** or
   **submit**, optionally with a **voice instruction**.
4. **Rework** returns the item to the creating agents with the instruction; it resubmits and
   the **same cycle repeats**. Nothing skips the camera.
5. Vyomaraj and Jarvis **always notify** the owner at every step.
6. In this repository the camera is a deterministic local prototype: decisions are recorded
   as metadata, no media is hosted, nothing is published and no notification is sent.

## 5. Finance, audit and the every-morning briefing

- Jarvis and Vyomaraj follow up with the **Finance and auditing agents**; the agents check the
  data (amount, due date, platform, reminder history) before anything goes out.
- Reminders climb a ladder: gentle email → due email → firm email → call script →
  **escalation to the owner** for anything more than 14 days late. A disputed amount stops
  the ladder and reaches the owner the same morning.
- **Every morning** the owner receives the briefing by **voice or email, text or WhatsApp**:
  payments pending, overdue escalations, approvals awaiting in the camera queue, DR sync
  state, yesterday's highlights.
- In this repository everything is drafted, never sent (`emails_sent/calls_made/messages_sent:
  false`); ledger amounts are planning figures.

## 6. Post-deployment change management (live in the market)

When Vyomaraj is deployed and live, the owner can instruct any change, fix or upgrade:

```
Owner instruction
  → Vyomaraj + Jarvis align internally with ShriYantra
    → talk to each other and to all affected AI agents
      → make the change under version control (branch + commits, no history deleted)
        → test everything separately (offline suites, separate preview, results checked)
          → PENDING_OWNER_PERMISSION gate
            → upgrade (snapshot the current version first; zero business impact)
              → post-upgrade verification
                → on ANY failure: backup plan engages → roll back → continue with the
                  current version, no business impact
```

The same rules as the DR lane apply: no force-push, no history deletion, no blind two-way
overwrite. `ops/vyomaraj-core/upgrades/upgrade-controller.sh` is the stage-by-stage
controller skeleton (dry-run by default; the owner's permission is a hand-written gate file).

## 7. Comics lane — trilingual, past and future

`ops/vyomaraj-core/comics-experience/` (viewer `/comics/`, planner `comics_planner.py`):

- Binds the **existing** cartoon slots `ENT-CARTOON-S1–S3` (canonical names remain UNKNOWN;
  no duplicate agents created; registry totals unchanged).
- **Every title and every edition carries all three languages — Hindi, English and Hinglish.**
- **Past versions are preserved** in history (never overwritten); **future versions stay
  plannable** (issue arcs, specials, sequels) — each again in all three languages.
- Heritage publishers (Amar Chitra Katha, Tinkle, Chacha Chaudhary, Raj Comics, Indrajal,
  Chandamama) are context references only — no characters, artwork or stories are copied.
- Every plan ends at the owner gate (`PENDING_OWNER_PERMISSION`), routed to the nostalgic
  camera queue.

## 8. What is NOT claimed (unchanged honesty rules)

- No runtime/site disaster recovery, no zero-RPO/RTO, no traffic switch — the DR record covers
  Git snapshot replication of `main` only.
- No external AI provider is called automatically; no media is hosted; nothing publishes
  automatically; no email, call or message is sent from these prototypes.
- Unknown names stay UNKNOWN; view-only is not operational; historical snapshots are marked
  NOT CURRENT; generated files are rebuilt by their builders, never edited by hand.
- The preview stack is unauthenticated, single-sandbox and dies with its sandbox; the
  repository is what lasts.

## 9. Version history of this architecture

- V16.7.24 and earlier — preserved registry snapshot, historical architecture (see
  `flow-diagram.html` history cards and `ops/vyomaraj-core/handover/`).
- V16.8 — 2026-10-04 — this document: full agent/sub-agent hierarchy, content pipeline,
  Jarvis communication paths, publishing systems, social platforms, nostalgic camera approval
  queue, finance/audit follow-up, morning briefing, learning loop, hardware/software and
  multi-AI layer, and post-deployment change management with backup and rollback. Nothing old
  was deleted; every earlier layer is preserved and upgraded in place.
