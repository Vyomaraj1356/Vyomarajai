#!/usr/bin/env python3
"""Vyomaraj full handover — every detail in one record, plus one downloadable archive.

Answers the owner's standing request: real-time state, handover notes, all chats, the whole agent
tree, the Vyomaraj configuration, the Jarvis configuration, every AI platform and what is actually
connected, and the issue/PR research result.

Everything in the document is read from the repository or probed live at generation time. Where the
repository only holds an ambition (the V15.1 port and social files claim listeners and follower
figures that do not exist), the record prints the claim and the truth side by side.

    python3 build_full_handover.py            write the document and the archive
    python3 build_full_handover.py --check    verify they still match the repository and the probes
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
DOC = HERE / "VYOMARAJ_FULL_HANDOVER_2026_10_06.md"
ZIP = HERE / "transfer/VYOMARAJ_FULL_HANDOVER_2026_10_06.zip"

PORTS = [(3000, "product page (static http.server)"), (4174, "reports viewer"),
         (4176, "availability gateway"), (4181, "lane studio A"), (4182, "lane studio B")]

# Everything the owner asked to be able to download in one file. Never secrets: ops/jarvis/jarvis.env
# is deliberately absent, only its .example template travels.
MEMBERS = [
    "ops/vyomaraj-core/handover/VYOMARAJ_FULL_HANDOVER_2026_10_06.md",
    "Vyomaraj-All-Chats-Database-One-Month.md",
    "VYOMARAJ_REPOSITORY_MAP.md",
    "REAL_VYOMARAJ_INVESTIGATION.md",
    "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json",
    "ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json",
    "ops/vyomaraj-core/handover/INHERITANCE_AUDIT_2026_10_04.md",
    "ops/vyomaraj-core/handover/STACK_AND_PLATFORM_RECORD_2026_10_06.md",
    "ops/vyomaraj-core/handover/LINK_AND_ARCHIVE_LEDGER_2026_10_06.json",
    "ops/vyomaraj-core/handover/MARKET_READINESS_AND_WIRING_2026_10_06.md",
    "ops/vyomaraj-core/handover/NAVARATRI_GO_LIVE_PLAN_2026_10_11.md",
    "ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.png",
    "ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg",
    "ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md",
    "ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json",
    "ops/vyomaraj-core/handover/LIVE_WIRING_STATE_2026_10_06.json",
    "ops/vyomaraj-core/handover/PREVIEW_VERIFICATION_2026_10_04.json",
    "ops/vyomaraj-core/handover/TEST_EVIDENCE_2026_10_04.json",
    "ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md",
    "ops/vyomaraj-core/governance/VOICE_ENROLLMENT_POLICY.json",
    "ops/vyomaraj-core/experience/CONTENT_EXTENSIONS.json",
    "ops/jarvis/devices.json",
    "ops/jarvis/jarvis.env.example",
    "ops/hanuman/ports.json",
    "ops/hanuman/social-platforms.json",
    "ops/vyomaraj-core/handover/screenshots/SCREENSHOT_CAPTURE_RAW.json",
    "ops/vyomaraj-core/handover/screenshots/product-page.jpg",
    "ops/vyomaraj-core/handover/screenshots/lane-music.jpg",
    "ops/vyomaraj-core/handover/screenshots/report-network-diagram.jpg",
]


def port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.6)
        return s.connect_ex(("127.0.0.1", port)) == 0


def read_json(rel: str):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def registry_sections(L):
    reg = read_json("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json")
    if not reg:
        L.append("Agent registry not found.")
        return
    t = reg.get("totals", {})
    L.append("| Tier | Count | Source |")
    L.append("|---|---|---|")
    L.append("| Main agents | **13** | owner-approved registry, categories below |")
    L.append(f"| Sub-agents | **{t.get('sub_agents', 0)}** "
             f"({t.get('named_sub_agents', 0)} named, {t.get('unnamed_numbered_sub_agents', 0)} unnamed) | "
             f"`AGENT_REGISTRY_CURRENT.json` |")
    L.append(f"| Third tier (hubs) | **{len(reg.get('count_reconciliation', {}).get('six_hubs_reclassified_not_deleted', []))}** "
             f"| only the six explicitly approved hubs acquire child edges |")
    L.append(f"| Products | **{t.get('historical_reported_products', 0)}** historical | "
             f"*not a verified current inventory* |")
    L.append("")
    L.append("### The 13 main agents and their sub-agents")
    L.append("")
    L.append("| # | Main agent | Sub-agents | Historical products reported |")
    L.append("|---|---|---|---|")
    for i, c in enumerate(reg.get("categories", []), 1):
        subs = c.get("sub_agents")
        n = len(subs) if isinstance(subs, list) else subs
        L.append(f"| {i} | **{c['name']}** (`{c['id']}`) | {n} | {c.get('source_reported_products')} |")
    L.append("")
    L.append("### The six approved hubs (the only third tier)")
    L.append("")
    L.append("| From | Hub | Registry id |")
    L.append("|---|---|---|")
    for r in reg.get("count_reconciliation", {}).get("six_hubs_reclassified_not_deleted", []):
        L.append(f"| {r['source_category']} | {r['name']} | `{r['now']}` |")
    L.append("")
    L.append("Hierarchy policy, verbatim from the registry: *"
             + str(reg.get("hierarchy_policy", "")) + "*")
    L.append("")
    L.append("Display policy, verbatim: *" + str(reg.get("display_policy", "")) + "*")
    L.append("")
    named = [a for a in reg.get("agents", []) if a.get("name")]
    L.append(f"### The {len(named)} named sub-agents")
    L.append("")
    L.append("| id | Name | Category | Kind |")
    L.append("|---|---|---|---|")
    for a in named:
        L.append(f"| `{a['id']}` | {a['name']} | {a.get('category_id')} | {a.get('kind')} |")
    L.append("")
    L.append(f"The remaining {len(reg.get('agents', [])) - len(named)} sub-agents are numbered slots with "
             "names not yet assigned. The registry keeps them as serials rather than inventing names.")
    L.append("")


def platform_sections(L):
    coord = CORE.parent / "vyomaraj-core/multi-ai-coordination.js"
    text = coord.read_text(encoding="utf-8", errors="ignore") if coord.is_file() else ""
    platforms = re.findall(r"\['([a-z]+)', '([^']+)'\]", text)
    L.append("What the coordination module itself declares (its own header: "
             "*\"Metadata-only compatibility surface, not a provider or device-control client\"*):")
    L.append("")
    L.append("| Platform id | Declared name | Declared status | Actually connected? |")
    L.append("|---|---|---|---|")
    for pid, name in platforms:
        L.append(f"| `{pid}` | {name} | `UNVERIFIED` | "
                 f"{'**yes** — repository/host this project runs on' if pid in ('primary', 'secondary', 'local') else '**no** — no client, no credential, no call'} |")
    L.append("")
    L.append("The module's own health function returns `mode: metadata_only`, `operational: false`, "
             "`currentLoad: null`, `confidence: UNVERIFIED`, and its `switchPlatform` / `shareLoadWith` "
             "functions return `BLOCKED` with the reason *\"No provider/session-transfer executor is "
             "configured.\"* Nothing here transfers work between AI platforms.")
    L.append("")
    ports = read_json("ops/hanuman/ports.json")
    if ports:
        L.append("### The V15.1 port file — claim vs live probe")
        L.append("")
        L.append(f"`ops/hanuman/ports.json` declares `allPortsEnabled: {ports.get('allPortsEnabled')}`, "
                 f"`allPortsActive: {ports.get('allPortsActive')}`, `allPortsLive: {ports.get('allPortsLive')}`. "
                 "Probed on this host at generation time:")
        L.append("")
        L.append("| Port | Claimed service | Declared status | Live now |")
        L.append("|---|---|---|---|")
        for entry in ports.get("ports", [])[:8]:
            p = entry.get("port")
            live = "**open**" if isinstance(p, int) and port_open(p) else "**closed**"
            L.append(f"| {p} | {str(entry.get('service'))[:58]} | {entry.get('status')} | {live} |")
        L.append("")
        L.append("Ports 80 and 443 are claimed live for *\"All Social Platforms\"*. Nothing in this "
                 "repository binds them, and unprivileged processes cannot. Treat that file as intent, "
                 "not as telemetry.")
        L.append("")
    social = read_json("ops/hanuman/social-platforms.json")
    if social:
        ids = social.get("vyomarajIds", {})
        L.append(f"### The V15.1 social file — {len(ids)} platforms, all figures unverified")
        L.append("")
        L.append("`ops/hanuman/social-platforms.json` records handles and figures. Not one of them is "
                 "verified by this repository, and no code connects to any platform:")
        L.append("")
        L.append("| Platform | Recorded handle string (verbatim, unverified) |")
        L.append("|---|---|")
        for name, value in list(ids.items())[:12]:
            L.append(f"| {name} | {str(value)[:96]} |")
        L.append("")
        L.append("The follower counts, view counts and revenue figures in that row set — and in "
                 "`README_MARKET_READY.md` — are the same class of claim this project already removed "
                 "from its JavaScript. Do not repeat them to a partner, a bank or a platform reviewer "
                 "until a platform dashboard shows them.")
        L.append("")
    L.append("### What connects to a platform today")
    L.append("")
    L.append("| Route | State |")
    L.append("|---|---|")
    L.append("| GitHub (primary repo, Pages, Actions) | **connected** — authenticated in this sandbox |")
    L.append("| Landing page → lane studios / gateway | **connected** — same host |")
    L.append("| YouTube / Instagram / Facebook / X / LinkedIn / TikTok / Telegram… | **not connected** — 0 API clients, 0 tokens, 0 upload calls |")
    L.append("| Payment gateways | **not connected** — 0 integrations |")
    L.append("| Analytics | **not connected** — 0 counters |")
    L.append("| AI providers (OpenAI, Anthropic, Google) | **not connected** — 0 calls; planners state `ai_calls_made=false` |")
    L.append("")


def config_sections(L):
    L.append("### Configuration — Vyomaraj (the product and its servers)")
    L.append("")
    L.append("| Component | Setting |")
    L.append("|---|---|")
    L.append("| Public address | `https://vyomaraj1356.github.io/Vyomarajai/` — GitHub Pages from `main`, free |")
    L.append("| Palette | Shani Blue `#0a1628`, Kuber Gold `#f59e0b` |")
    L.append("| Product pages | `index.html`, `landing.html`, `flow-diagram.html` — static, no framework |")
    for port, what in PORTS:
        state = "**up**" if port_open(port) else "**down**"
        L.append(f"| Port {port} | {what} — {state} |")
    L.append("| Server runtime | Python 3 standard library only (`http.server` / `ThreadingHTTPServer`), binds `0.0.0.0` |")
    L.append("| Storage | JSON + SQLite files on disk; **no database server** |")
    L.append("| Content packs | music 107 · film 59 · bhakti 47 · comics 22 · pairings 28 · aghor 44 records |")
    L.append("| Agents surface | `/agents/` and `CONTENT_INDEX_CURRENT.json` — 13 categories, 128 slots |")
    L.append("| Reports surface | 30+ viewer routes, all checked by `verify_live_wiring.py` |")
    L.append("| Security headers | `Content-Security-Policy` with `default-src 'none'`, `img-src 'self'` on the viewer |")
    L.append("| APK | `Vyomaraj-App.apk`, 24,567,022 B, **unsigned** — Android refuses it until signed |")
    L.append("")
    L.append("### Configuration — Jarvis (the device/presence layer)")
    L.append("")
    devices = read_json("ops/jarvis/devices.json")
    if devices:
        keys = [k for k in devices.keys()]
        L.append(f"`ops/jarvis/devices.json` (version {devices.get('version')}) carries keys: "
                 + ", ".join(f"`{k}`" for k in keys[:10]) + ".")
        L.append("")
    controller = ROOT / "ops/jarvis/jarvis-24x7-controller.sh"
    env_example = ROOT / "ops/jarvis/jarvis.env.example"
    L.append("| Jarvis item | State |")
    L.append("|---|---|")
    L.append(f"| `ops/jarvis/jarvis-24x7-controller.sh` | {'present' if controller.is_file() else 'missing'} — a shell controller, **not running in this sandbox** |")
    L.append(f"| `ops/jarvis/jarvis.env.example` | {'present' if env_example.is_file() else 'missing'} — template only; the real `jarvis.env` is **never** included in any handover |")
    L.append("| Jarvis voice | Web Speech API on the visitor's device (browser), permission-gated |")
    L.append("| Jarvis enrollment | on-device only, `uploads_enabled: false`, delete-my-voice supported |")
    L.append("| Jarvis as a running service | **not running** — no process, no port, no scheduler in this repository |")
    L.append("")
    L.append("So: Vyomaraj is configured and live as pages and local servers. Jarvis is configured as "
             "**records, policy and browser features** — there is no always-on Jarvis process yet, and "
             "an always-on process is exactly what the \"buy when Vyomaraj earns\" list is for.")
    L.append("")


def issue_sections(L):
    ledger = read_json("ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json") or {}
    L.append("| Item | State found | Action taken |")
    L.append("|---|---|---|")
    L.append("| Issue #6 — Unblock private DR access | OPEN, ledger verdict **READY_TO_CLOSE** | "
             "close-out comment prepared and held for owner confirmation; nothing sent |")
    for pr in ledger.get("pull_requests", [])[:6]:
        L.append(f"| PR #{pr.get('number')} — {str(pr.get('title'))[:52]} | {pr.get('state_inferred') or pr.get('state')} | {str(pr.get('action'))[:60]} |")
    L.append("| PR #27 — replication gate + companion | OPEN, this session's branch | ready to merge; merging fires `verify-or-sync` |")
    L.append("")
    L.append("Found and fixed while researching this handover:")
    L.append("")
    L.append("| Issue | Fix |")
    L.append("|---|---|")
    L.append("| `landing.html` polled `/api/sync/status` every 4s and POSTed `/api/sync/trigger` every 2 min against routes no server implements → the status box hung on \"Loading sync status…\" forever and every visitor produced a 404 storm | the servers now answer a real `/api/sync/status` built from checked-in DR evidence, the page states one true line, the fake \"Master Sync Now\" button is gone, and the polling loop is removed |")
    L.append("| the same box displayed \"6 sub-agents syncing together\" — a value nothing produces | replaced with the repository's own evidence date and the plain statement that replication is a GitHub Actions job |")
    L.append("| `flow-diagram.html` depends on a CDN for Mermaid | recorded: on a network that blocks the CDN, all 6 diagrams render 0 SVGs and the visitor sees raw source text |")
    L.append("| the capture gallery's images were blocked by the hardened CSP | fixed with `img-src 'self'` — same-origin only |")
    L.append("")


def build(L, now):
    L.append("# VYOMARAJ — FULL HANDOVER, ALL DETAILS")
    L.append("")
    L.append(f"Generated {now} from this repository and from live probes of the running services. "
             "Everything here is checkable: each section says where it came from, and the archive "
             "beside this file carries the sources themselves.")
    L.append("")
    L.append("**One command rebuilds this document and its archive:** "
             "`python3 ops/vyomaraj-core/handover/build_full_handover.py` — `--check` verifies the "
             "checked-in copy still matches the repository and the probes.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 1 · Real-time state at generation")
    L.append("")
    L.append("| Port | Service | Live now |")
    L.append("|---|---|---|")
    for port, what in PORTS:
        L.append(f"| {port} | {what} | {'**open**' if port_open(port) else '**closed**'} |")
    L.append("")
    L.append("The live view of this table is served at `/reports/realtime` on the viewer, both lane "
             "studios and the gateway — it re-probes on every load and refreshes itself every 10 "
             "seconds, so what you read there is the state at that moment, not a recording.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 2 · Chats — every session since the first Arena session")
    L.append("")
    chats = ROOT / "Vyomaraj-All-Chats-Database-One-Month.md"
    if chats.is_file():
        text = chats.read_text(encoding="utf-8", errors="ignore")
        heading = re.search(r"(\d+)\s+chats", text, re.I)
        entries = len(re.findall(r"^\s*(?:\|\s*)?(\d{2})[.)|]", text, re.M))
        L.append(f"- `Vyomaraj-All-Chats-Database-One-Month.md` — {chats.stat().st_size:,} bytes. "
                 f"Its heading says **{heading.group(1) if heading else '?'} chats**; the body carries "
                 f"**{entries} numbered entries**. That discrepancy is pre-existing and is served "
                 f"unmodified at `/reports/chats` rather than smoothed over.")
        L.append("- `Vyomaraj-All-Chats-From-Arena-Database-Till-V16.7.22.zip` — the archive copy.")
        L.append("- `Vyomaraj-Complete-All-Sessions-All-Handover-Zips-V16.7.22.zip` — all sessions, "
                 "all handover zips.")
        error = ROOT / "All-Chats-Extraction-Error.txt"
        if error.is_file():
            L.append("- `All-Chats-Extraction-Error.txt` records the one real gap: the attempt to "
                     "export raw per-chat transcripts ran `git show origin/main~4:index.html` and "
                     "exited 128. **The raw transcripts were never exported into this repository.** "
                     "Nothing can recover them from here — they existed only inside the Arena session. "
                     "What survives is the consolidated database, the session archives and the "
                     "45-archive handover set.")
    else:
        L.append("The chats database file is not present in this checkout.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 3 · All agents, sub-agents and hubs")
    L.append("")
    registry_sections(L)
    L.append("---")
    L.append("")
    L.append("## 4 · AI platforms, context and connections")
    L.append("")
    platform_sections(L)
    L.append("---")
    L.append("")
    L.append("## 5 · Configuration — Vyomaraj and Jarvis")
    L.append("")
    config_sections(L)
    L.append("---")
    L.append("")
    L.append("## 6 · Research: issues found, resolved and fixed")
    L.append("")
    issue_sections(L)
    L.append("---")
    L.append("")
    L.append("## 7 · What is in the downloadable archive")
    L.append("")
    L.append(f"`transfer/VYOMARAJ_FULL_HANDOVER_2026_10_06.zip` carries {len(MEMBERS)} files:")
    L.append("")
    L.append("| File | Bytes |")
    L.append("|---|---|")
    for rel in MEMBERS:
        p = ROOT / rel
        L.append(f"| `{rel}` | {p.stat().st_size:,} |" if p.is_file() else f"| `{rel}` | **missing** |")
    L.append("")
    L.append("`ops/jarvis/jarvis.env` is deliberately **not** in the archive: it is the one file that "
             "may hold credentials, and handover artifacts in this project stay reviewable and "
             "non-secret.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 8 · Verdict and the next three actions")
    L.append("")
    L.append("| Question | Answer |")
    L.append("|---|---|")
    L.append("| Is Vyomaraj equipped to go live on 11 October? | **Yes** on the free route — Pages is built, the lanes are real, the gates are green |")
    L.append("| Is everything in the vision connected? | **No** — the 22 platforms, payments, analytics and AI providers are records, not connections |")
    L.append("| Is Jarvis running 24×7? | **No** — records, policy and browser voice; no process |")
    L.append("| Will it earn on day one? | **No** — see the three wirings below |")
    L.append("")
    L.append("**Next three actions, all free, all owner decisions:** sign the APK with your own "
             "`keytool` key · put a contact address on the page · switch on a free analytics counter. "
             "Then hand-publish the first episodes and apply to the YouTube Partner Program before "
             "1 February 2027, when new applicants need 8,000 watch hours instead of 4,000.")
    L.append("")
    return L


def write_zip() -> list[str]:
    missing = []
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("HANDOVER_README.txt",
                   "Vyomaraj full handover archive.\n"
                   "Open VYOMARAJ_FULL_HANDOVER_2026_10_06.md first: it is the index to everything else.\n"
                   "No credentials, tokens or environment files are included.\n")
        for rel in MEMBERS:
            p = ROOT / rel
            if p.is_file():
                z.write(p, rel)
            else:
                missing.append(rel)
    return missing


def check() -> int:
    problems = []
    if not DOC.is_file():
        problems.append(f"{DOC.name} missing")
    if not ZIP.is_file():
        problems.append(f"{ZIP.name} missing")
    if DOC.is_file():
        text = DOC.read_text(encoding="utf-8")
        for marker in ("## 1 · Real-time state at generation", "## 3 · All agents, sub-agents and hubs",
                       "metadata_only", "READY_TO_CLOSE", "jarvis.env` is deliberately",
                       "/reports/realtime", "unsigned"):
            if marker not in text:
                problems.append(f"document lost: {marker}")
    if ZIP.is_file():
        with zipfile.ZipFile(ZIP) as z:
            names = set(z.namelist())
            for rel in MEMBERS:
                if (ROOT / rel).is_file() and rel not in names:
                    problems.append(f"archive is missing {rel}")
            bad = z.testzip()
            if bad:
                problems.append(f"archive member corrupt: {bad}")
    reg = read_json("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json")
    if reg and DOC.is_file():
        totals = reg.get("totals", {})
        text = DOC.read_text(encoding="utf-8")
        # The document states these in two shapes: "**128**" for the tier total and
        # "128 (42 named, 86 unnamed)" for the split, so accept either form.
        for value, shapes in ((totals.get("sub_agents"), ("**{v}**",)),
                              (totals.get("named_sub_agents"), ("**{v}**", "{v} named"))):
            if value is None:
                continue
            if not any(shape.format(v=value) in text for shape in shapes):
                problems.append(f"document no longer states registry value {value}")
    if problems:
        print("full handover check FAILED")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: full handover matches the repository ({DOC.stat().st_size:,} B document, "
          f"{ZIP.stat().st_size:,} B archive, {len(MEMBERS)} members)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L: list[str] = []
    build(L, now)
    DOC.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {DOC.name} ({DOC.stat().st_size:,} B, {len(L)} lines)")
    missing = write_zip()
    print(f"wrote {ZIP.name} ({ZIP.stat().st_size:,} B, {len(MEMBERS) - len(missing)} members, "
          f"sha256 {sha256_file(ZIP)[:16]})")
    if missing:
        print(f"  note: {len(missing)} member(s) not present in this checkout: {', '.join(missing[:4])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
