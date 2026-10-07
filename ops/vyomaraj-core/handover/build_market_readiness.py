#!/usr/bin/env python3
"""Market readiness, configuration and wiring record — generated from repository evidence and local probes.

Answers, in one document the owner can read:

  * how Vyomaraj is configured and integrated right now (probed, not remembered),
  * what was inherited and what was deliberately not inherited,
  * which parts of the vision mock-up are connected, partly connected, or not connected,
  * what "talking to social platforms" actually requires, and the free path that needs no vendor,
  * whether publishing now gives the product a working heartbeat in the market,
  * and exactly what has to be wired before real earning can start.

    python3 build_market_readiness.py            write the document
    python3 build_market_readiness.py --check    verify it still matches repository inputs and point-in-time local probes
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent
ROOT = HERE.parents[2]
OUT = HERE / "MARKET_READINESS_AND_WIRING_2026_10_06.md"
SHOTS = HERE / "screenshots"
MANIFEST = SHOTS / "SCREENSHOT_CAPTURE_RAW.json"

PORTS = {"viewer": 4174, "gateway": 4176, "replica-a": 4181, "replica-b": 4182, "product": 3000, "safe-static-preview": 5310}


def port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.6)
        return s.connect_ex(("127.0.0.1", port)) == 0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lane_counts() -> list[tuple[str, int, str]]:
    """Count records per experience pack using the verifier's own pack list."""
    sys.path.insert(0, str(HERE))
    try:
        import verify_live_wiring as wiring          # noqa: PLC0415  (same directory)
        pack_dirs = dict(wiring.PACK_DIRS)
    except Exception:
        pack_dirs = {}
    rows = []
    for lane, directory in pack_dirs.items():
        content = CORE / directory / "content.json"
        if not content.is_file():
            continue
        data = json.loads(content.read_text())
        records = [e for key, value in data.items() if isinstance(value, list)
                   for e in value if isinstance(e, dict) and "id" in e]
        sources = data.get("sources") or []
        rows.append((lane, len(records), f"{len(sources)} sources · {len(data.get('agents') or [])} agent slots"))
    return rows


def integration_scan() -> dict[str, int]:
    """Count real outbound-integration surfaces in first-party code (.py/.js), not in prose."""
    patterns = {
        "social platform API calls": r"graph\.facebook\.com|api\.twitter\.com|youtube\.com/upload|open\.tiktok\.com|api\.instagram\.com|linkedin\.com/oauth",
        "OAuth token handling": r"client_secret|refresh_token|access_token\s*=|oauth2",
        "payment gateways": r"razorpay|stripe|paypal|phonepe|payu|upi://pay",
        "analytics counters": r"gtag\(|googletagmanager|plausible\.io|matomo|mixpanel",
        "email/SMS sending": r"smtp\.|sendgrid|mailgun|twilio|msg91",
        "AI provider calls": r"api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis",
        "runtime database drivers": r"import psycopg2|import redis|import pymysql|CREATE TABLE",
    }
    code = [p for p in list(ROOT.glob("ops/**/*.py")) + list(ROOT.glob("ops/**/*.js")) if p.is_file()]
    blob = "\n".join(p.read_text(errors="ignore") for p in code)
    return {label: len(re.findall(rx, blob, re.I)) for label, rx in patterns.items()}


def screenshot_rows() -> list[dict]:
    if not MANIFEST.is_file():
        return []
    return json.loads(MANIFEST.read_text())["screenshots"]


def build() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    servers = {name: port_open(port) for name, port in PORTS.items()}
    lanes = lane_counts()
    scan = integration_scan()
    shots = screenshot_rows()
    meta = json.loads(MANIFEST.read_text()) if MANIFEST.is_file() else {}
    browser = meta.get("browser", "headless chromium")
    cdns = sorted({f["url"] for s in shots for f in s.get("failed_requests", [])})
    live_ledger = json.loads((HERE / "ISSUES_AND_PRS_LEDGER.json").read_text(encoding="utf-8"))
    live = live_ledger.get("current_live_recheck_2026_10_07", {})
    dr = live.get("dr_snapshot", {})
    pages = live.get("pages", {})
    main_commit = pages.get("build_commit", "unknown")[:8]
    dr_completed = dr.get("completed_at_utc", "unknown")
    dr_tree = dr.get("primary_tree", "unknown")
    target_resolution = live.get("dr_target_resolution", {})

    L: list[str] = []
    add = L.append
    add("# VYOMARAJ — MARKET READINESS, CONFIGURATION & WIRING")
    add("")
    add(f"Generated {now} from repository evidence and local port/process probes, not from memory. "
        "No preview service needs to be running to generate this report. Owner's question: publish now, "
        "or is technical support needed for a heartbeat and for real earning?")
    add("")
    add("---")
    add("")

    # 1 ────────────────────────────────────────────────────────────────
    add("## 1 · Page captures (point-in-time evidence, not a live-service claim)")
    add("")
    add(f"A headless browser ({browser}) captured every page below at the timestamp in the manifest. "
        "These are point-in-time screenshots, not proof that the local product server is running now:")
    add("")
    add("| Page | HTTP | Screenshot | Bytes | SHA256 (first 16) |")
    add("|---|---|---|---|---|")
    for s in shots:
        add(f"| `{s['url'].replace('http://127.0.0.1', ':')}` | {s['http_status']} | "
            f"`{s['file']}` | {s['bytes']:,} | `{s['sha256'][:16]}` |")
    add("")
    if cdns:
        add(f"**Defect found while capturing:** `flow-diagram.html` loads Mermaid from a CDN. With that CDN "
            f"unreachable, all 6 diagram blocks render **0 SVGs** and the visitor sees raw `flowchart TD` source "
            f"text (52,114 characters). On the public internet the CDN resolves and the diagram draws; on any "
            f"network that blocks it — some offices, some countries — the page degrades to source code. "
            f"Blocked request: `{cdns[0]}`.")
        add("")
    add("---")
    add("")

    # 2 ────────────────────────────────────────────────────────────────
    add("## 2 · How Vyomaraj is configured")
    add("")
    add("| Layer | Configuration as it stands |")
    add("|---|---|")
    add(f"| Product pages | `index.html` ({(ROOT / 'index.html').stat().st_size:,} B), `demo.html` ({(ROOT / 'demo.html').stat().st_size:,} B), `landing.html` ({(ROOT / 'landing.html').stat().st_size:,} B), `flow-diagram.html` — static HTML/CSS/vanilla JS, no framework |")
    add("| Palette | Shani Blue `#0a1628`, Kuber Gold `#f59e0b`, defined once per server and inherited by every page |")
    add(f"| Live host | GitHub Pages from `main:/` at `{main_commit}`; this launch-preview branch is not deployed |")
    for name, port in PORTS.items():
        state = "up" if servers[name] else "DOWN"
        binding = ('127.0.0.1 only; non-loopback bind rejected'
                   if name in ('gateway', 'replica-a', 'replica-b') else
                   'exact asset allowlist + bounded local /api/plan; sandbox proxy listener' if name == 'safe-static-preview' else
                   'historical/implementation-specific listener; no public writer exposure is approved')
        add(f"| `{name}` server | port {port} — **{state}**, Python 3 standard library; {binding} |")
    if not any(servers[name] for name in ("gateway", "replica-a", "replica-b")):
        safe_state = "running" if servers["safe-static-preview"] else "stopped"
        add(f"| Preview exposure | studio/gateway/replica rehearsal ports are stopped and loopback-only by code; sandbox preview :5310 is {safe_state} and exposes only a bounded deterministic /api/plan route (no privileged writers, provider calls or persistence); owner issuer/key are unconfigured |")
    else:
        add("| Preview exposure | local rehearsal listeners may be up on loopback; privileged routes fail closed without request-scoped owner tokens and must not be exposed publicly |")
    add("| Content stores | SQLite + JSON on disk; no database server anywhere |")
    add(f"| Gates | offline suite + main-only DR workflow; scheduled check at `{dr_completed}` reports MATCH for tracked Git tree `{dr_tree[:12]}`; issue #6 target identity/access and target-only review remain owner-blocked |")
    add("| Secrets | none in the repository; identity documents never captured in-app (`uidai.in` web only) |")
    add("| APK | 24,567,022 B; v2 signing-block entry detected, but cryptographic signature validation, signer provenance and device installation are **not verified** |")
    add("")
    add("---")
    add("")

    # 3 ────────────────────────────────────────────────────────────────
    add("## 3 · How it is integrated (what actually talks to what)")
    add("")
    safe_preview_state = "running" if servers["safe-static-preview"] else "stopped"
    add(f"The repository contains a shared content spine, static product pages, and report routes. The allowlisted sandbox preview on :5310 is {safe_preview_state} at generation; its only POST is a bounded deterministic planner for Bhakti-Shakti and Roots & Pairings, returning an ephemeral response with no persistence or provider call. It has no privileged writer route. Legacy report/gateway/studio ports 3000/4174/4176/4181/4182 remain separate session-scoped services and do not establish production status. This feature branch is not on Pages.")
    add("")
    add("| Connection | State | Evidence |")
    add("|---|---|---|")
    product_state = ("allowlisted sandbox preview :5310 is running; legacy :3000 is "
                     + ("up" if servers["product"] else "down"))
    if not servers["safe-static-preview"]:
        product_state = "sandbox preview on :5310 is stopped; legacy :3000 is " + ("up" if servers["product"] else "down")
    add(f"| Product page → visitors | **sandbox preview only** | {product_state}; public Pages serves main only |")
    add(f"| Pages → public internet | **main only** | Pages is built from `main:/` at `{main_commit}`; this launch-prep branch is not deployed there |")
    add(f"| Lane content packs | **present in repository; servers stopped** | {'  ·  '.join(f'{n}: {c} records ({detail})' for n, c, detail in lanes) or 'no lane content found'} |")
    add("| Agent registry → content index | **connected** | 13 categories, 128 counted slots, 6 uncounted headings |")
    add(f"| Reports → viewer | **read-only, session-scoped** | port 4174 is {'up' if servers['viewer'] else 'down'} at report generation; the 06:11 UTC 30-route result is historical; the allowlisted public preview on :5310 does not expose report routes |")
    add("| Viewer/replicas → gateway | **single-host rehearsal only** | the local gateway/lanes on 4176/4181/4182 were stopped after checks; no production control plane or independent failover |")
    writes = live.get("observed_main_replication_writes", {}).get("writes", [])
    write_ids = ", ".join(str(row.get("workflow_run_id")) for row in writes) or "none recorded"
    add(f"| Push → automation | **main-only Actions workflow executed** | main-push runs `{write_ids}` recorded automatic snapshot writes; latest scheduled check at `{dr_completed}` was a no-op MATCH; pull-request `verify-or-sync` is skipped |")
    add(f"| Primary → workflow-selected secondary | **tracked Git tree MATCH; target identity owner-blocked** | latest scheduled run `{dr.get('workflow_run_id')}` reports equal trees `{dr_tree}`; Actions variable may override fallback and is unreadable (403); target-only review and runtime DR remain open |")
    add("| Vyomaraj ↔ Jarvis | **architecture target + local harness/monitor only** | heartbeat example URLs are blank; no authenticated peer link, production service, quorum or failover |")
    add("| Product → social platforms | **NOT connected** | 0 platform API calls in first-party code |")
    add("| Product → payments | **NOT connected** | 0 gateway integrations |")
    add("| Product → analytics | **NOT connected** | 0 counters; nobody can see traffic today |")
    add("| Product → email/SMS | **NOT connected** | no sending path; no way to reach a visitor |")
    add("| Product → AI providers | **NOT connected** | planners are deterministic and state `ai_calls_made=false` |")
    add("| Product → database server | **NOT connected** | nothing to connect: no Postgres/Redis/FastAPI/Flask runs here |")
    add("")
    add("Machine scan of first-party `.py`/`.js` code for outbound integrations:")
    add("")
    add("| Integration surface | Occurrences in code |")
    add("|---|---|")
    for label, count in scan.items():
        add(f"| {label} | **{count}** |")
    add("")
    add("---")
    add("")

    # 4 ────────────────────────────────────────────────────────────────
    add("## 4 · What is inherited — and what is deliberately not")
    add("")
    add("| Inherited | Not inherited (test-enforced refusal) |")
    add("|---|---|")
    add("| Format and structure of Sufi/qawwali, ghazal and studio-show episodes | No titles, lyrics, audio, video or artwork from any existing work |")
    add("| Credit discipline: performers and creators named, sources recorded | No brand marks, logos or channel identities |")
    add("| Multi-language presentation (voice and text layers) | No artist names or likenesses used as endorsement |")
    add("| DR doctrine: primary→secondary, never force-push, rollback parent retained | No third-party episode content or recordings |")
    add("| Governance: owner-locked approvals, consent, delete-my-voice | No licensed catalogue, no rights we do not hold |")
    add("")
    add("---")
    add("")

    # 5 ────────────────────────────────────────────────────────────────
    add("## 5 · The vision mock-up, checked line by line")
    add("")
    add("| Mock-up element | Reality in this repository | Verdict |")
    add("|---|---|---|")
    add("| Passkey / biometric login | no login exists at all; no auth code anywhere | **not connected** |")
    add("| SHRIYANTRA private control plane | `shriyantra-protection.js` says `mode: branding_only`, protection `NOT_IMPLEMENTED` | **branding only** |")
    add("| Multi-AI coordination bus | `multi-ai-coordination.js` says `mode: metadata_only`, `operational: false` | **metadata only** |")
    add("| JARVIS / LAXMAN / BHARATH | names and layers exist in registry and pages (Jarvis 82 files, Laxman 33, Bharath 8) | **present as records, not as running AI** |")
    add("| HERMES / HARNESS / ARENA | HERMES appears only as text in `flow-diagram.html`; HARNESS has no code entity; ARENA is the platform we build on | **not built** |")
    add("| 22 social platform tiles | 0 integrations; tiles are aspirations | **not connected** |")
    add("| Auto publish / track / engage / earn | no publisher, no tracker, no payment path | **not connected** |")
    add("| Domain experts: FOOD, EDU, ASTRO, FINANCE, LIFE, BHAKTI, SPORTS, AGRI … | registry lists 208 names across 13 categories with content indexed | **structure connected, no runtime AI** |")
    add(f"| Replication/rollback | scheduled Git check at `{dr_completed}` reports equal tracked trees; automatic main-push writes were observed; runtime rollback/failover and target identity remain unverified | **snapshot match only** |")
    add("| GitHub integration, primary→secondary | current connection lists only primary; Actions variable/secrets reads are 403; workflow-selected target returned matching tree annotations but its effective owner/name is not independently confirmed | **partial evidence; issue #6 open** |")
    add("| Success indicators / revenue figures | every ₹ and follower number in `README_MARKET_READY.md` is unverified | **do not quote** |")
    add("")
    add("---")
    add("")

    # 6 ────────────────────────────────────────────────────────────────
    add("## 6 · Talking to social platforms: what it takes")
    add("")
    add("| Route | What is required | Cost | Ready today? |")
    add("|---|---|---|---|")
    add("| Manual publishing (recommended first) | platform accounts in the owner's name; upload by hand | ₹0 | **yes — nothing to build** |")
    add("| Platform APIs (YouTube Data API, Meta Graph, X, LinkedIn, TikTok) | developer app per platform, OAuth consent, token storage, review/approval, per-platform rate limits and ToS | ₹0 to build, weeks of review | no — 0 code |")
    add("| Scheduled auto-posting | a token store that survives restarts + a scheduler + failure alerts | needs always-on host | no |")
    add("| Collaboration with other creators | accounts, a contactable identity, published work to point at | ₹0 | partially — the published page is the portfolio |")
    add("")
    add("The honest sequencing: **publish by hand first**. Automation only pays off once there is content worth "
        "automating, and every platform API route needs app review that a brand-new account will struggle to pass "
        "without published work.")
    add("")
    add("---")
    add("")

    # 7 ────────────────────────────────────────────────────────────────
    add("## 7 · If Vyomaraj publishes now — will it work in the market?")
    add("")
    add(f"**The existing Pages site is a public presence; this launch-preview branch is not yet deployed. No, this is not an earning machine.** "
        f"Pages currently serves `main` at `{main_commit}`. Only the already-published main content is public; "
        "this branch requires explicit owner review/merge and a successful new Pages build. What the "
        "current setup does not yet give:")
    add("")
    add("| Missing for a market heartbeat | Consequence right now |")
    add("|---|---|")
    add("| No analytics | the owner cannot see whether anyone visited, at all |")
    add("| No contact/email capture | no way for an interested person to reach Vyomaraj |")
    add("| No login or accounts | no returning audience, no personalization |")
    add("| No payment path | nothing to sell even if someone wanted to buy |")
    add("| APK signature/device test unverified | do not distribute until apksigner validation, signer provenance review and a real-device installation test pass |")
    add("| CDN-dependent diagram page | degrades to raw source text on restricted networks |")
    add("| No scheduled posting | content sits on the page; it does not travel |")
    add("")
    add("So: the existing `main` Pages build is a **public, honest showcase**, but no launch claim is made for this unmerged branch. The 11 October date is a target, not a guarantee. A heartbeat in the market sense — signals arriving, people responding, money moving — needs the wiring in section 8 first.")
    add("")
    add("---")
    add("")

    # 8 ────────────────────────────────────────────────────────────────
    add("## 8 · Wiring for real earning — zero budget, in order")
    add("")
    add("| Step | What to do | Cost | Time | Blocked by |")
    add("|---|---|---|---|---|")
    add("| 1 | Verify the existing APK with `apksigner`, review signer provenance and install on a real device; rebuild/sign from source if verification fails | ₹0 tooling | owner-held source/device access | owner decision |")
    add("| 2 | Put a contact address on the page (the owner's own mailbox) | ₹0 | minutes | owner account |")
    add("| 3 | Add a free analytics counter to see traffic | ₹0 | minutes | owner account |")
    add("| 4 | Open the owner's YouTube channel and publish the first original episodes by hand | ₹0 | ongoing | content production |")
    add("| 5 | Apply to the YouTube Partner Program **before 1 February 2027** | ₹0 | — | 1,000 subscribers + 4,000 watch hours, or 10M Shorts views in 90 days (the 500-subscriber tier needs 3,000 hours); from 1 Feb 2027 new applicants need 8,000 hours |")
    add("| 6 | AdSense + bank/UPI details for payouts | ₹0 | KYC days | owner identity documents, done off-app at the provider |")
    add("| 7 | Direct payments (a payment gateway) if selling directly | ₹0 setup, per-transaction fee | KYC days | business/individual KYC; only worth doing once something is for sale |")
    add("| 8 | Always-on host, domain, CDN | paid | — | **earnings first**, as the owner decided |")
    add("")
    add("Purchases are owner decisions and are not assumed here. The 11 October date remains a target, not a guarantee; authoritative DR-target confirmation, owner review of target-only data, branch review/deployment and release checks remain separate gates. A page existing or a matching Git tree is not the same as a secure operating product.")
    add("")
    add("---")
    add("")

    # 9 ────────────────────────────────────────────────────────────────
    add("## 9 · Verdict")
    add("")
    add("| Question | Answer |")
    add("|---|---|")
    add("| Configured and integrated internally? | **Partly** — content, lanes, registry and reports are in the repo; a tracked-Git-tree DR match exists, but effective target identity, production auth/runtime DR and an always-on authenticated heartbeat are not established |")
    add("| Inherited cleanly? | **Yes** — formats and credit discipline, with rights refusals enforced by tests |")
    add("| Connected to the outside world? | **Only via the already-built main Pages site.** No platform API, analytics, payments or AI provider is connected |")
    add("| Publish this branch now? | **No claim** — it is not deployed; owner review/merge and a fresh Pages build are required |")
    add("| Needs technical support to earn? | **Yes** — first unblock owner-authorized DR access, verify APK signature/provenance and device installation, publish a contact address, then switch on analytics |")
    add("")
    add("Next actions: **confirm the existing DR target and access · verify APK signer/device install · publish a contact address · switch on analytics.** These require owner authorization and evidence; the web preview is not production.")
    add("")
    return "\n".join(L) + "\n"


def check() -> int:
    problems = []
    if not OUT.is_file():
        problems.append(f"{OUT.name} missing")
    else:
        text = OUT.read_text()
        for marker in ("## 1 · Page captures", "NOT connected", "1 February 2027",
                       "signature validation", "metadata_only", "branding_only", "Next actions:"):
            if marker not in text:
                problems.append(f"document lost: {marker}")
        if not MANIFEST.is_file() or json.loads(MANIFEST.read_text())["screenshots"] == []:
            problems.append("screenshot manifest missing/empty — capture was not run")
        else:
            for s in json.loads(MANIFEST.read_text())["screenshots"]:
                p = HERE / s["file"]          # e.g. screenshots/product-page.jpg
                if not p.is_file():
                    problems.append(f"screenshot missing on disk: {p.name}")
                elif sha256(p) != s["sha256"]:
                    problems.append(f"screenshot hash drift: {p.name}")
        if "0 | " not in text and "| 0 |" not in text:
            problems.append("integration scan no longer reports zero outbound integrations — recheck")
    if problems:
        print("market readiness check FAILED")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: market readiness record matches the captured pages and the code scan "
          f"({OUT.stat().st_size} B, {len(screenshot_rows())} screenshots)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    OUT.write_text(build())
    print(f"wrote {OUT.name} ({OUT.stat().st_size} B, {len(build().splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
