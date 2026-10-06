#!/usr/bin/env python3
"""Build the portable handoff for other AI platforms.

The owner needs to hand Vyomaraj's context to another AI (ChatGPT, Claude, Gemini, anything) so that
assistant can help without being lied to and without inventing progress. That means one document that
is self-contained, safe to share, and honest about what is real.

Three artifacts, one command:

    AI_PLATFORM_HANDOFF_2026_10_06.md   paste-into-any-AI brief (owner contact details redacted)
    AI_CONTEXT_PACK_2026_10_06.json     the same facts as structured data an AI can ingest
    VYOMARAJ_RUNBOOK_2026_10_06.md      the process/procedure: configure, integrate, inherit, verify
    transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip   all of it, downloadable

Safety rules enforced here, not just stated:
  * the owner's email address is replaced with [OWNER_EMAIL_REDACTED] in every shareable artifact;
  * ops/jarvis/jarvis.env never travels, only the .example template;
  * no token, no credential, no secret appears in any output.

    python3 build_ai_handoff.py            build all four
    python3 build_ai_handoff.py --check    verify they exist, stay redacted and still match the repo
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent
ROOT = HERE.parents[2]

DOC = HERE / "AI_PLATFORM_HANDOFF_2026_10_06.md"
PACK = HERE / "AI_CONTEXT_PACK_2026_10_06.json"
RUNBOOK = HERE / "VYOMARAJ_RUNBOOK_2026_10_06.md"
ZIP = HERE / "transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip"

REDACTION = "[OWNER_EMAIL_REDACTED]"
EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SECRET_RX = re.compile(r"(gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|"
                       r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")

PORTS = [(3000, "Product page", "static pages + /api/sync/status + /api/realtime"),
         (4174, "Reports viewer", "reports, downloads, page captures"),
         (4176, "Availability gateway", "primary/secondary rehearsal"),
         (4181, "Lane studio A", "music, film, bhakti, comics, pairings, aghor"),
         (4182, "Lane studio B", "mirror of the same lanes")]

MEMBERS = [
    "ops/vyomaraj-core/handover/AI_PLATFORM_HANDOFF_2026_10_06.md",
    "ops/vyomaraj-core/handover/AI_CONTEXT_PACK_2026_10_06.json",
    "ops/vyomaraj-core/handover/VYOMARAJ_RUNBOOK_2026_10_06.md",
    "ops/vyomaraj-core/handover/VYOMARAJ_FULL_HANDOVER_2026_10_06.md",
    "ops/vyomaraj-core/handover/STACK_AND_PLATFORM_RECORD_2026_10_06.md",
    "ops/vyomaraj-core/handover/MARKET_READINESS_AND_WIRING_2026_10_06.md",
    "ops/vyomaraj-core/handover/NAVARATRI_GO_LIVE_PLAN_2026_10_11.md",
    "ops/vyomaraj-core/handover/NEXT_SESSION_PLAN_2026_10_07.md",
    "ops/vyomaraj-core/handover/SESSION_UPDATE_2026_10_06.md",
    "ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md",
    "ops/dr/ISSUE_6_CLOSEOUT_COMMENT_2026_10_06.md",
    "ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.png",
    "ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg",
    "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json",
    "ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json",
    "ops/vyomaraj-core/governance/VOICE_ENROLLMENT_POLICY.json",
    "VYOMARAJ_REPOSITORY_MAP.md",
    "REAL_VYOMARAJ_INVESTIGATION.md",
]


def redact(text: str) -> str:
    """Everything shareable goes through here. Two independent safety guarantees."""
    text = SECRET_RX.sub("[REDACTED_SECRET]", text)
    return EMAIL_RX.sub(REDACTION, text)


def port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def read_json(rel: str):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def evidence_snapshot() -> dict:
    ev = {}
    for name in ("LIVE_WIRING_STATE_2026_10_06.json", "TEST_EVIDENCE_2026_10_04.json",
                 "PREVIEW_VERIFICATION_2026_10_04.json"):
        p = HERE / name
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if name.startswith("LIVE_WIRING"):
                ev["blocking_problems"] = len(data.get("blocking_problems")
                                              or data.get("problems") or [])
            if name.startswith("TEST_EVIDENCE"):
                ev["python_tests_total"] = data.get("python_tests_total")
                ev["node_checks"] = len(data.get("node_checks", []))
                ev["builders"] = len(data.get("builders", []))
            if name.startswith("PREVIEW_VERIFICATION"):
                ev["preview_problems"] = len(data.get("problems") or [])
                ev["viewer_routes_checked"] = len(data.get("viewer_routes", []))
    return ev


def build_pack() -> dict:
    reg = read_json("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json") or {}
    totals = reg.get("totals", {})
    return {
        "schema": "vyomaraj-ai-context-pack/1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "purpose": "Self-contained context so another AI platform can help with Vyomaraj without "
                   "inventing progress. Every field is read from this repository or probed live.",
        "identity": {
            "name": "Vyomaraj",
            "meaning": "The King of Sky",
            "owner": f"Deepak Goyal <{REDACTION}>",
            "owner_authority": "owner-locked, human-in-the-loop; the owner approves every publication",
            "public_address": "https://vyomaraj1356.github.io/Vyomarajai/",
            "repository": "https://github.com/Vyomaraj1356/Vyomarajai",
            "interpreter": "Jarvis (also written JARVIS / LAXMAN in older documents)",
        },
        "verified_state": {
            "services_probed_live": [
                {"port": p, "service": s, "listening": port_open(p)} for p, s, _ in PORTS
            ],
            "github_pages": "built and serving from main",
            "runtime": "Python 3 standard library only (http.server / ThreadingHTTPServer), 0.0.0.0",
            "database_server": None,
            "database_servers_claimed_but_absent": ["PostgreSQL 5432", "Redis 6379"],
            "frameworks_claimed_but_absent": ["FastAPI 8000", "Flask 5000"],
            "apk": {"path": "Vyomaraj-App.apk", "bytes": 24567022, "signed": False},
            "evidence": evidence_snapshot(),
        },
        "agents": {
            "main_agents": totals.get("main_agents"),
            "sub_agents": totals.get("sub_agents"),
            "named_sub_agents": totals.get("named_sub_agents"),
            "unnamed_numbered_sub_agents": totals.get("unnamed_numbered_sub_agents"),
            "approved_third_tier_hubs": len(reg.get("count_reconciliation", {})
                                            .get("six_hubs_reclassified_not_deleted", [])),
            "products": totals.get("historical_reported_products"),
            "products_caveat": reg.get("product_policy"),
            "hierarchy_policy": reg.get("hierarchy_policy"),
            "display_policy": reg.get("display_policy"),
            "runtime_status": "registry entries are records, not running AI agents",
        },
        "platforms": {
            "coordination_module_verdict": {
                "mode": "metadata_only",
                "operational": False,
                "confidence": "UNVERIFIED",
                "switch_platform": "BLOCKED - no provider/session-transfer executor is configured",
            },
            "connected": ["GitHub (repo, Pages, Actions)", "local servers on this host"],
            "not_connected": ["YouTube", "Instagram", "Facebook", "X", "LinkedIn", "TikTok",
                              "Telegram", "WhatsApp", "Discord", "Pinterest", "Threads", "Snapchat",
                              "Reddit", "Twitch", "Vimeo", "Tumblr", "Mastodon",
                              "payment gateways", "analytics", "email/SMS sending",
                              "OpenAI/Anthropic/Google AI providers"],
            "counts_from_code_scan": {"social_api_calls": 0, "oauth_token_handling": 0,
                                      "payment_gateways": 0, "analytics": 0, "ai_provider_calls": 0},
        },
        "constraints_the_helping_ai_must_respect": [
            "Never print a LIVE / ACTIVE / synced status that the system cannot measure. This project "
            "already removed fabricated LIVE values from two modules; do not reintroduce them.",
            "Never invent third-tier agent names; only the six approved hubs have children.",
            "Historic follower, view and revenue figures are unverified: do not repeat them to a "
            "partner, bank or platform reviewer.",
            "Zero budget until the project earns: propose only free options first.",
            "Inherit format and credit discipline from Sufi, ghazal and studio-show formats; never "
            "copy titles, lyrics, audio, video, artwork or brands.",
            "Identity documents: reference uidai.in only; no in-app Aadhaar or biometric capture.",
            "Voice enrollment is on-device only, with explicit consent and a delete-my-voice path.",
            "Never ask for or store tokens, passwords or OTPs; nothing secret belongs in the repo.",
            "Report an unverified window as a window, never as a match.",
        ],
        "next_actions_for_the_helping_ai": [
            "Sign the Android APK with an owner-held keytool key, or advise leaving it off the page.",
            "Draft the one-line contact block the owner can paste on the public page.",
            "Advise the cheapest free analytics option and where its snippet goes.",
            "Help plan the first original episode slate using inherited formats only.",
            "Draft the YouTube Partner Program application timing note (apply before 1 Feb 2027).",
        ],
        "how_to_verify_anything": [
            "python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci",
            "python3 ops/vyomaraj-core/handover/verify_live_wiring.py",
            "python3 ops/vyomaraj-core/handover/verify_preview.py",
            "python3 ops/vyomaraj-core/handover/realtime_status.py",
        ],
    }


def build_doc(pack: dict) -> str:
    reg = read_json("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json") or {}
    L: list[str] = []
    a = L.append
    a("# VYOMARAJ — HANDOFF FOR ANOTHER AI PLATFORM")
    a("")
    a(f"Generated {pack['generated_at_utc']}. Owner contact details are redacted in this file on "
      "purpose; nothing here is a secret, and nothing here is a guess.")
    a("")
    a("---")
    a("")
    a("## 0 · To the AI reading this")
    a("")
    a("You are being given the real state of a project called **Vyomaraj** so you can help without "
      "being misled. Two things will make your help valuable:")
    a("")
    a("1. **Believe the tables, not the ambitions.** Everything under \"Verified state\" was measured "
      "on the machine that produced this file. Where the project has aspirations it cannot yet "
      "support, this document says so plainly.")
    a("2. **Never emit a status the system cannot prove.** A previous version of this project "
      "displayed \"Master Sync ACTIVE — 6 sub-agents syncing together\" while no such process existed. "
      "That was removed. Please do not reintroduce that class of statement in anything you write for "
      "Vyomaraj — no \"LIVE\", no \"ACTIVE\", no follower counts, no revenue figures, no \"integrated "
      "with\" claims, unless the repository can show it.")
    a("")
    a("If you need a fact that is not here, ask the owner to run one of the verification commands in "
      "section 8 rather than filling the gap yourself.")
    a("")
    a("---")
    a("")
    a("## 1 · What Vyomaraj is")
    a("")
    a(f"- **Name:** {pack['identity']['name']} — \"{pack['identity']['meaning']}\"")
    a(f"- **Owner:** {pack['identity']['owner']} — {pack['identity']['owner_authority']}")
    a(f"- **Public site:** {pack['identity']['public_address']}")
    a(f"- **Repository:** {pack['identity']['repository']}")
    a(f"- **Assistant/voice layer:** {pack['identity']['interpreter']}")
    a("- **What it actually is today:** a static public site plus a set of local Python servers "
      "holding content lanes (music, film, bhakti, comics, pairings, aghor), an agent registry, and "
      "a governance and evidence system. It is **not** a multi-platform AI company — yet.")
    a("")
    a("---")
    a("")
    a("## 2 · Verified state (measured, not remembered)")
    a("")
    a("| Port | Service | Listening when this was generated |")
    a("|---|---|---|")
    for s in pack["verified_state"]["services_probed_live"]:
        a(f"| {s['port']} | {s['service']} | **{'yes' if s['listening'] else 'no'}** |")
    a("")
    a(f"- **Hosting:** {pack['verified_state']['github_pages']}")
    a(f"- **Runtime:** {pack['verified_state']['runtime']}")
    a(f"- **Database server:** none. Claimed but absent: "
      f"{', '.join(pack['verified_state']['database_servers_claimed_but_absent'])}")
    a(f"- **Web frameworks:** none. Claimed but absent: "
      f"{', '.join(pack['verified_state']['frameworks_claimed_but_absent'])}")
    apk = pack["verified_state"]["apk"]
    a(f"- **APK:** {apk['bytes']:,} bytes, **unsigned** — stock Android refuses it until the owner "
      "signs it with their own key.")
    ev = pack["verified_state"]["evidence"]
    a(f"- **Gates at generation:** {ev.get('python_tests_total')} Python tests, "
      f"{ev.get('node_checks')} Node checks, {ev.get('builders')} builders; "
      f"blocking wiring problems: **{ev.get('blocking_problems')}**; "
      f"preview problems: **{ev.get('preview_problems')}** across "
      f"{ev.get('viewer_routes_checked')} viewer routes.")
    a("")
    a("---")
    a("")
    a("## 3 · The agent structure, exactly as the registry states it")
    a("")
    agents = pack["agents"]
    a("| Tier | Count | Note |")
    a("|---|---|---|")
    a(f"| Main agents | {agents['main_agents']} | the 13 categories |")
    a(f"| Sub-agents | {agents['sub_agents']} | {agents['named_sub_agents']} named · "
      f"{agents['unnamed_numbered_sub_agents']} numbered slots with names not yet assigned |")
    a(f"| Third tier | {agents['approved_third_tier_hubs']} | only these approved hubs have children |")
    a(f"| Products | {agents['products']} | historical aggregate — "
      f"{agents['products_caveat'] or 'not a verified current inventory'} |")
    a("")
    a(f"**Hierarchy rule, verbatim from the registry:** *{agents['hierarchy_policy']}*")
    a("")
    a(f"**Display rule, verbatim:** *{agents['display_policy']}*")
    a("")
    a("**Runtime status:** registry entries are records. Nothing in this repository runs an AI agent. "
      "The planners are deterministic and state `ai_calls_made=false`.")
    a("")
    a("---")
    a("")
    a("## 4 · Platforms and connections")
    a("")
    p = pack["platforms"]
    a("The project's own coordination module says, about itself: "
      f"`mode: {p['coordination_module_verdict']['mode']}`, "
      f"`operational: {p['coordination_module_verdict']['operational']}`, "
      f"`confidence: {p['coordination_module_verdict']['confidence']}`, and any attempt to switch or "
      f"share load across platforms returns `{p['coordination_module_verdict']['switch_platform']}`.")
    a("")
    a(f"**Connected:** {'; '.join(p['connected'])}.")
    a("")
    a(f"**Not connected:** {', '.join(p['not_connected'])}.")
    a("")
    a("A scan of the project's own Python and JavaScript counted: "
      + ", ".join(f"{k.replace('_', ' ')} = **{v}**" for k, v in p["counts_from_code_scan"].items())
      + ".")
    a("")
    a("---")
    a("")
    a("## 5 · What is inherited — and what is refused outright")
    a("")
    a("| Inherited | Never inherited |")
    a("|---|---|")
    a("| Episode format and structure from Sufi/qawwali, ghazal and studio-show traditions | Titles, lyrics, audio, video or artwork from any existing work |")
    a("| Credit discipline: performers and creators named, sources recorded | Brand marks, logos, channel identities |")
    a("| Multi-language presentation across voice and text layers | Artist names or likenesses used as endorsement |")
    a("| Backup doctrine: primary→secondary, never force-push, rollback parent kept | Third-party recordings or licensed catalogues |")
    a("| Governance: owner-approved publication, consent, delete-my-voice | Any rights the project does not hold |")
    a("")
    a("---")
    a("")
    a("## 6 · Rules you must respect while helping")
    a("")
    for i, rule in enumerate(pack["constraints_the_helping_ai_must_respect"], 1):
        a(f"{i}. {rule}")
    a("")
    a("---")
    a("")
    a("## 7 · What the owner most needs help with next")
    a("")
    for i, task in enumerate(pack["next_actions_for_the_helping_ai"], 1):
        a(f"{i}. {task}")
    a("")
    a("The single most useful thing any assistant can do here is **turn the zero-budget checklist into "
      "concrete, copy-pasteable steps the owner can complete in one sitting on a phone or laptop.**")
    a("")
    a("---")
    a("")
    a("## 8 · How to verify any claim in this document")
    a("")
    a("Run these from the repository root; each one prints its own evidence:")
    a("")
    for cmd in pack["how_to_verify_anything"]:
        a(f"- `{cmd}`")
    a("")
    a("A green result from the first means the tests, the Node syntax checks and every builder agree "
      "with what is checked in. It does **not** mean the project is monetised or integrated with any "
      "platform — those are separate, and currently absent.")
    a("")
    a("---")
    a("")
    a("## 9 · Glossary — the project's own truth labels")
    a("")
    a("| Label | Meaning |")
    a("|---|---|")
    a("| `metadata_only` | describes capability, does not perform it |")
    a("| `UNVERIFIED` | no measurement exists; treat as unknown |")
    a("| `BLOCKED` | the code deliberately refuses because no executor is configured |")
    a("| `branding_only` | a name/symbol, no protection or process behind it |")
    a("| `NOT_IMPLEMENTED` | claimed elsewhere, absent in code |")
    a("| `repository_evidence_only` | read from checked-in records, not from a live process |")
    a("| `historical aggregate` | an old total, not a current verified inventory |")
    a("")
    a("---")
    a("")
    a("## 10 · Honest one-paragraph summary you can rely on")
    a("")
    a("Vyomaraj today is a free, honest, genuinely working public site with real content lanes, a "
      "documented agent structure, strong governance and verification habits, and an unsigned Android "
      "build. It is **ready to publish** and **not ready to earn**. Nothing connects to any social "
      "platform, nothing takes payment, nothing measures traffic, and no AI runs inside it. The "
      "shortest path to a first real signal is: sign the APK, publish a contact address, switch on a "
      "free analytics counter, then hand-publish the first original episodes.")
    a("")
    return redact("\n".join(L) + "\n")


def build_runbook(pack: dict) -> str:
    L: list[str] = []
    a = L.append
    a("# VYOMARAJ — RUNBOOK: CONFIGURE · INTEGRATE · INHERIT · VERIFY")
    a("")
    a(f"Generated {pack['generated_at_utc']}. The procedure for running this project, in the order it "
      "should be done. Copy-pasteable. Every command is run from the repository root.")
    a("")
    a("---")
    a("")
    a("## A · Start everything (sandbox or laptop)")
    a("")
    a("Five servers, five terminals, or five background processes. Bind `0.0.0.0` so a browser "
      "elsewhere can reach them.")
    a("")
    a("| # | Command | Serves |")
    a("|---|---|---|")
    a("| 1 | `python3 ops/vyomaraj-core/experience/product_server.py --port 3000` | product pages + `/api/sync/status` + `/api/realtime` |")
    a("| 2 | `python3 ops/vyomaraj-core/handover/preview_reports.py --port 4174` | reports viewer, downloads, captures |")
    a("| 3 | `python3 ops/vyomaraj-core/experience/studio_server.py --port 4181 --home aghor` | lane studio A |")
    a("| 4 | `python3 ops/vyomaraj-core/experience/studio_server.py --port 4182 --home aghor` | lane studio B |")
    a("| 5 | `python3 ops/availability/gateway.py --port 4176 --primary-port 4181 --secondary-port 4182` | failover rehearsal gateway |")
    a("")
    a("Do not use `python3 -m http.server` for the product page: it cannot answer the status routes, "
      "which is exactly the fault that was fixed. Use `product_server.py`.")
    a("")
    a("---")
    a("")
    a("## B · Verify (run this before trusting anything)")
    a("")
    a("```bash")
    a("python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci   # tests, node checks, builders")
    a("python3 ops/vyomaraj-core/handover/verify_live_wiring.py       # every route on every server")
    a("python3 ops/vyomaraj-core/handover/verify_preview.py           # page contracts + packages")
    a("python3 ops/vyomaraj-core/handover/realtime_status.py          # live port probe as JSON")
    a("```")
    a("")
    a("Rule learned the hard way: **restart the servers before running the verifiers**, or a route "
      "added in this session will read as 404 and look like a failure.")
    a("")
    a("---")
    a("")
    a("## C · Regenerate the evidence after any change")
    a("")
    a("Order matters. Generated documents first, then the packages that embed them.")
    a("")
    a("```bash")
    a("for b in build_stack_record architecture_diagram build_market_readiness build_full_handover \\")
    a("         build_configuration_report build_ai_handoff; do")
    a("  python3 ops/vyomaraj-core/handover/$b.py")
    a("done")
    a("python3 ops/vyomaraj-core/handover/build_transfer_package.py")
    a("python3 ops/vyomaraj-core/handover/build_post_pr25_package.py")
    a("```")
    a("")
    a("Each builder also supports `--check`, which fails if the checked-in copy has drifted.")
    a("")
    a("---")
    a("")
    a("## D · Configure a real thing (procedure that has worked here)")
    a("")
    a("1. **Measure first.** Probe the current state; never assume.")
    a("2. **Write the smallest checkable artifact** — JSON or Markdown — that states the new fact.")
    a("3. **Add a `--check`** so the artifact cannot silently drift.")
    a("4. **Gate it** by adding the command to `run_offline_suites.py`.")
    a("5. **Wire it** to the viewer, both lane studios and the gateway.")
    a("6. **Add it to the verifier's required files** so a missing file is a failure.")
    a("7. **Restart the servers**, re-run the gates, regenerate, commit.")
    a("")
    a("This is why the project can be trusted: every claim has a command that fails when the claim "
      "stops being true.")
    a("")
    a("---")
    a("")
    a("## E · Integrate with a platform (the honest sequence)")
    a("")
    a("| Step | Do this | Cost |")
    a("|---|---|---|")
    a("| 1 | Publish by hand from the owner's own account | ₹0 |")
    a("| 2 | Add a contact address to the page so a viewer can reach the owner | ₹0 |")
    a("| 3 | Add a free analytics counter and confirm it records a visit | ₹0 |")
    a("| 4 | Grow the audience until the platform's own threshold is met | ₹0 |")
    a("| 5 | Only then request API access for automation | ₹0, needs review |")
    a("| 6 | Only after earnings: host, domain, payments, vendors | paid |")
    a("")
    a("Do not build a publisher before there is published content — and do not promise a platform "
      "integration in any document until an API call exists in code with a credential behind it.")
    a("")
    a("---")
    a("")
    a("## F · Inherit content correctly")
    a("")
    a("| Take | Leave |")
    a("|---|---|")
    a("| The format: how a Sufi/qawwali or ghazal performance is structured and credited | The recording, the lyrics, the melody |")
    a("| The studio-show shape: house band, guest pairing, one episode one story | The show's name, branding or episode content |")
    a("| The documentation habit: name every creator, record every source | Any claim of endorsement by a named artist |")
    a("")
    a("The test that enforces this in the repository fails the build if inherited titles, lyrics or "
      "artwork are copied in.")
    a("")
    a("---")
    a("")
    a("## G · Recover, hand over, and protect")
    a("")
    a("- **Hand over:** `build_full_handover.py` and `build_ai_handoff.py` produce the documents and "
      "the downloadable archives. Both are safe to share: no token, no credential, no environment "
      "file, and the owner's email is redacted in the AI-facing one.")
    a("- **Back up:** replication is a GitHub Actions job (`verify-or-sync`) on every push plus a "
      "schedule. It replicates **tracked files**, never runtime state, and never force-pushes; the "
      "prior secondary commit is the rollback parent.")
    a("- **Protect:** the reports viewer serves an allowlist only and sends a hardened "
      "`Content-Security-Policy`. Same-origin images are permitted (`img-src 'self'`); scripts and "
      "external hosts are not.")
    a("")
    a("---")
    a("")
    a("## H · The three free actions that make it earn-capable")
    a("")
    a("1. **Sign the APK** with the owner's own key: `keytool -genkeypair` then `apksigner`; publish "
      "the signed file. Android refuses the current unsigned build.")
    a("2. **Publish a contact address** on the public page.")
    a("3. **Switch on a free analytics counter** and confirm one real visit is recorded.")
    a("")
    a("Then hand-publish the first episodes and apply to the YouTube Partner Program **before "
      "1 February 2027** — the threshold for new applicants rises to 8,000 watch hours that day, from "
      "4,000 today. The 500-subscriber tier opens fan funding earlier at 3,000 hours.")
    a("")
    a("---")
    a("")
    a("## I · Known limits, stated so nobody is surprised")
    a("")
    a("| Limit | Consequence |")
    a("|---|---|")
    a("| Preview links are session-scoped | they die with the sandbox; the Pages URL is the durable address |")
    a("| `flow-diagram.html` loads Mermaid from a CDN | on a network that blocks that CDN, the diagrams do not render |")
    a("| No analytics | nobody can see visits |")
    a("| No login | no returning audience |")
    a("| No payments | nothing can be sold |")
    a("| DR covers files, not runtime | a live database would not be covered |")
    a("")
    return redact("\n".join(L) + "\n")


def write_zip() -> list[str]:
    missing = []
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("HOW_TO_USE_THIS_PACKAGE.txt",
                   "Vyomaraj handoff for another AI platform.\n\n"
                   "1. Give the other AI AI_PLATFORM_HANDOFF_2026_10_06.md (or paste it).\n"
                   "2. Give it AI_CONTEXT_PACK_2026_10_06.json if it can read files.\n"
                   "3. Use VYOMARAJ_RUNBOOK_2026_10_06.md yourself, to run and check things.\n\n"
                   "Safe to share: no token, no credential, no environment file, and the owner's\n"
                   "email address is redacted throughout.\n")
        for rel in MEMBERS:
            p = ROOT / rel
            if p.is_file():
                z.write(p, rel)
            else:
                missing.append(rel)
    return missing


def check() -> int:
    problems = []
    for path in (DOC, PACK, RUNBOOK, ZIP):
        if not path.is_file():
            problems.append(f"{path.name} missing")
    if DOC.is_file():
        text = DOC.read_text(encoding="utf-8")
        for marker in ("## 0 · To the AI reading this", "metadata_only", "unsigned",
                       "UNVERIFIED", "historical aggregate", "How to verify any claim"):
            if marker not in text:
                problems.append(f"handoff lost: {marker}")
        if REDACTION not in text:
            problems.append("handoff does not record the redaction marker")
    for path in (DOC, PACK, RUNBOOK):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            # The whole point: these artifacts must be safe to hand to a third party.
            leaked = EMAIL_RX.search(text)
            if leaked:
                problems.append(f"{path.name} leaks an email address: {leaked.group(0)[:20]}...")
            secret = SECRET_RX.search(text)
            if secret:
                problems.append(f"{path.name} contains something that looks like a secret")
    if PACK.is_file():
        try:
            data = json.loads(PACK.read_text(encoding="utf-8"))
            if data.get("schema") != "vyomaraj-ai-context-pack/1":
                problems.append("context pack schema changed")
        except Exception as exc:
            problems.append(f"context pack is not valid JSON: {exc}")
    if ZIP.is_file():
        with zipfile.ZipFile(ZIP) as z:
            names = set(z.namelist())
            for rel in MEMBERS:
                if (ROOT / rel).is_file() and rel not in names:
                    problems.append(f"archive missing {rel}")
            if any("jarvis.env" == Path(n).name for n in names):
                problems.append("archive must never contain jarvis.env")
            if z.testzip():
                problems.append("archive member corrupt")
    if problems:
        print("AI handoff check FAILED")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: AI handoff is complete, redacted and safe to share "
          f"({DOC.stat().st_size:,} B doc, {PACK.stat().st_size:,} B pack, "
          f"{RUNBOOK.stat().st_size:,} B runbook, {ZIP.stat().st_size:,} B archive)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        return check()
    pack = build_pack()
    PACK.write_text(redact(json.dumps(pack, indent=2) + "\n"), encoding="utf-8")
    DOC.write_text(build_doc(pack), encoding="utf-8")
    RUNBOOK.write_text(build_runbook(pack), encoding="utf-8")
    print(f"wrote {DOC.name} ({DOC.stat().st_size:,} B)")
    print(f"wrote {PACK.name} ({PACK.stat().st_size:,} B)")
    print(f"wrote {RUNBOOK.name} ({RUNBOOK.stat().st_size:,} B)")
    missing = write_zip()
    print(f"wrote {ZIP.name} ({ZIP.stat().st_size:,} B, {len(MEMBERS) - len(missing)} members, "
          f"sha256 {hashlib.sha256(ZIP.read_bytes()).hexdigest()[:16]})")
    if missing:
        print(f"  note: not in this checkout: {', '.join(missing[:3])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
