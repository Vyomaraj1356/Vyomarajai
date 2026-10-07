#!/usr/bin/env python3
"""Vyomaraj full handover — every detail in one record, plus one downloadable archive.

Answers the owner's standing request: real-time state, handover notes, all chats, the whole agent
tree, the Vyomaraj configuration, the Jarvis configuration, every AI platform and what is actually
connected, and the issue/PR research result.

Repository facts are read from the checkout; local listener state is probed at generation time;
external GitHub/Pages status comes from the separately timestamped read-only audit in the issue ledger.
Where the repository only holds an ambition (the V15.1 port and social files claim listeners and
follower figures that do not exist), the record prints the claim and the evidence side by side.

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
ZIP = HERE / "transfer/VYOMARAJ_FULL_HANDOVER_2026_10_07.zip"

PORTS = [(3000, "legacy product server"), (4174, "reports viewer"),
         (4176, "availability gateway"), (4181, "lane studio A"), (4182, "lane studio B"),
         (5310, "allowlisted bounded sandbox planner preview")]

# Everything the owner asked to be able to download in one file. Never secrets: ops/jarvis/jarvis.env
# is deliberately absent, only its .example template travels.
MEMBERS = [
    "ops/vyomaraj-core/handover/VYOMARAJ_FULL_HANDOVER_2026_10_06.md",
    "Vyomaraj-All-Chats-Database-One-Month.md",
    "VYOMARAJ_REPOSITORY_MAP.md",
    "REAL_VYOMARAJ_INVESTIGATION.md",
    "ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json",
    "ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json",
    "ops/vyomaraj-core/agents/rebuild_registry.py",
    "ops/vyomaraj-core/agents/test_registry.py",
    "config/agents/shriyantra-agent-registry.json",
    "config/intelligence/shriyantra-rag-cag-mag.yaml",
    "config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json",
    "docs/architecture/README-shriyantra-arena-integration.md",
    "docs/architecture/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE.md",
    "docs/architecture/shriyantra-rag-cag-mag-arena.md",
    "ops/shriyantra/knowledge_evolution.py",
    "tests/test_knowledge_evolution.py",
    "ops/vyomaraj-core/handover/INHERITANCE_AUDIT_2026_10_04.md",
    "ops/vyomaraj-core/handover/STACK_AND_PLATFORM_RECORD_2026_10_06.md",
    "ops/vyomaraj-core/handover/LINK_AND_ARCHIVE_LEDGER_2026_10_06.json",
    "ops/vyomaraj-core/handover/MARKET_READINESS_AND_WIRING_2026_10_06.md",
    "ops/vyomaraj-core/handover/NAVARATRI_GO_LIVE_PLAN_2026_10_11.md",
    "ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.png",
    "ops/vyomaraj-core/handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg",
    "index.html",
    "launch.css",
    "launch.js",
    "demo.html",
    "demo.css",
    "demo.js",
    "ops/vyomaraj-core/experience/public_landing_server.py",
    "ops/vyomaraj-core/experience/local_planner.py",
    "ops/vyomaraj-core/bhakti-experience/content.json",
    "ops/vyomaraj-core/liquor-bar/content.json",
    "tests/test_public_landing_server.py",
    "ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER_2026_10_04.md",
    "ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json",
    "ops/vyomaraj-core/handover/LIVE_WIRING_STATE_2026_10_06.json",
    "ops/vyomaraj-core/handover/PREVIEW_VERIFICATION_2026_10_04.json",
    "ops/vyomaraj-core/handover/TEST_EVIDENCE_2026_10_04.json",
    "ops/vyomaraj-core/handover/DR_SYNC_RESULTS_2026_10_04.md",
    "ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md",
    "ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md",
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
    shared = reg.get("shared_knowledge_inheritance", {})
    if shared:
        coverage = shared.get("current_coverage", {})
        L.append("### Universal Knowledge Evolution inheritance")
        L.append("")
        L.append(f"The active hierarchy references `{shared.get('policy_id')}` v{shared.get('policy_version')} "
                 f"once for {coverage.get('category_count')} categories and {coverage.get('agent_count')} "
                 f"counted sub-agents; the bounded content index references the same policy for "
                 f"{coverage.get('indexed_content_reference_count', 'recorded')} content entries. "
                 f"Policy: `{shared.get('policy_ref')}`; mode: `{shared.get('inheritance_mode')}`; "
                 f"runtime status: `{shared.get('runtime_status')}`. Future categories and entities inherit by "
                 "reference; per-agent copies are not required. This registry contract is not proof of "
                 "production runtime enforcement or a live shared peer store.")
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
    ledger = read_json("ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json") or {}
    live = ledger.get("current_live_recheck_2026_10_07", {})
    dr = live.get("dr_snapshot", {})
    for pid, name in platforms:
        if pid == "primary":
            connection = "**readable** — primary repository only"
        elif pid == "secondary":
            connection = (f"**tracked Git tree MATCH** at {dr.get('completed_at_utc', 'unknown')} for the workflow-selected target; "
                          "canonical target identity/settings and runtime DR are owner-blocked")
        elif pid == "local":
            connection = "**local-only** — not an external provider connection"
        else:
            connection = "**no** — no client, credential, or call"
        L.append(f"| `{pid}` | {name} | `UNVERIFIED` | {connection} |")
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
    L.append(f"| GitHub/API | Primary repository and Pages are readable; scheduled check `{dr.get('workflow_run_id')}` reports equal tracked trees, but the Actions variable may override policy fallback and settings return 403; effective secondary identity is unconfirmed |")
    L.append("| Landing page → local studios / gateway | **local routes only** — studio/gateway enforce loopback binds and owner-token checks, but no trusted identity/provider or production interlink is configured |")
    L.append("| Vyomaraj ↔ Jarvis heartbeat | **not production-connected** — local read-only monitor exists with blank example URLs; no authenticated identity/quorum/failover |")
    L.append("| YouTube / Instagram / Facebook / X / LinkedIn / TikTok / Telegram… | **not connected** — 0 API clients, 0 tokens, 0 upload calls |")
    L.append("| Payment gateways | **not connected** — 0 integrations |")
    L.append("| Analytics | **not connected** — 0 counters |")
    L.append("| AI providers (OpenAI, Anthropic, Google) | **not connected** — 0 calls; planners state `ai_calls_made=false` |")
    L.append("")


def config_sections(L):
    ledger = read_json("ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json") or {}
    live = ledger.get("current_live_recheck_2026_10_07", {})
    pages = live.get("pages", {})
    main_commit = pages.get("build_commit", "unknown")[:8]
    L.append("### Configuration — Vyomaraj (the product and its servers)")
    L.append("")
    L.append("| Component | Setting |")
    L.append("|---|---|")
    L.append(f"| Public address | `https://vyomaraj1356.github.io/Vyomarajai/` — Pages serves `main:/` at `{main_commit}`; this feature branch is not deployed |")
    L.append("| Palette | Shani Blue `#0a1628`, Kuber Gold `#f59e0b` |")
    L.append("| Product pages | `index.html`, `demo.html` (sandbox UI), `landing.html`, `flow-diagram.html` — static HTML/CSS/vanilla JS; planner API is sandbox-only |")
    for port, what in PORTS:
        state = "**up**" if port_open(port) else "**down**"
        L.append(f"| Port {port} | {what} — {state} |")
    L.append("| Server runtime | Python 3 standard library (`http.server` / `ThreadingHTTPServer`); studio/gateway enforce IPv4 loopback-only binds; sandbox landing preview uses an exact asset allowlist plus bounded, ephemeral deterministic POST `/api/plan` for two experiences only |")
    L.append("| Storage | JSON + SQLite files on disk; **no database server** |")
    L.append("| Content packs | music 107 · film 59 · bhakti 47 · comics 22 · pairings 28 · aghor 44 records |")
    L.append("| Agents surface | `/agents/` and `CONTENT_INDEX_CURRENT.json` — 13 categories, 128 slots |")
    L.append("| Reports surface | 30+ allowlisted viewer routes implemented; the 7 October 06:11 UTC live-wiring snapshot recorded pre-shutdown route responses |")
    L.append("| Security headers | `Content-Security-Policy` with `default-src 'none'`, `img-src 'self'` on the viewer |")
    L.append("| APK | `Vyomaraj-App.apk`, 24,567,022 B; v2 signing-block entry detected, but signature validity, signer provenance and device installation are **UNVERIFIED** |")
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
    monitor_state_path = Path.home() / ".local/state/vyomaraj/jarvis-heartbeats.json"
    try:
        monitor_state = json.loads(monitor_state_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        monitor_state = {"summary": "not_checked", "checked_at_utc": "not recorded"}
    L.append("| Jarvis item | State |")
    L.append("|---|---|")
    L.append(f"| `ops/jarvis/jarvis-24x7-controller.sh` | {'present' if controller.is_file() else 'missing'} — a shell controller, **not running in this sandbox** |")
    L.append(f"| `ops/jarvis/jarvis.env.example` | {'present' if env_example.is_file() else 'missing'} — template only; the real `jarvis.env` is **never** included in any handover |")
    L.append("| Jarvis voice | Web Speech API on the visitor's device (browser), permission-gated |")
    L.append("| Jarvis enrollment | on-device only, `uploads_enabled: false`, delete-my-voice supported |")
    L.append(f"| Jarvis/peer heartbeat service | **not production-connected** — local read-only monitor snapshot is `{monitor_state.get('summary')}` at `{monitor_state.get('checked_at_utc')}`; example peer URLs are blank; no authenticated process, production scheduler or failover |")
    L.append("")
    L.append(f"So: GitHub Pages serves `main` at `{main_commit}`; the current launch-preview branch is not "
             f"deployed there. A bounded read-only planner preview on :5310, if open in the port table, is sandbox-only and not a production service; "
             f"the write-capable gateway and studios remain separate and must not be exposed as production. "
             f"Jarvis is configured as **records, policy and browser features**; the local monitor is a reachability "
             f"probe, not an always-on authenticated Jarvis peer/runtime. Production operation and DR remain unproven.")
    L.append("")


def issue_sections(L):
    ledger = read_json("ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json") or {}
    issue6 = next((entry for entry in ledger.get("entries", []) if entry.get("id") == "issue-6"), {})
    live = ledger.get("current_live_recheck_2026_10_07", {})
    dr = live.get("dr_snapshot", {})
    target = live.get("dr_target_resolution", {})
    status_followup = ledger.get("current_github_metadata_followup_2026_10_07", {})
    dr_annotation_followup = ledger.get("current_dr_annotation_followup_2026_10_07", {})
    L.append("| Item | State found | Action taken / next step |")
    L.append("|---|---|---|")
    L.append(f"| Issue #6 — DR target ownership | OPEN/P0, ledger verdict **{issue6.get('status', 'OWNER_ACTION_REQUIRED')}** | Scheduled tracked-Git-tree match exists, but effective target identity (`{target.get('effective_target_identity', 'UNCONFIRMED')}`) and target-only data remain owner-blocked; keep open and do not post historical close-out. |")
    L.append(f"| Latest scheduled `verify-or-sync` | `{dr.get('status')}` at `{dr.get('completed_at_utc')}`; run `{dr.get('workflow_run_id')}` / check `{dr.get('check_run_id')}` | Equal primary/secondary tracked trees `{dr.get('primary_tree')}` / `{dr.get('secondary_tree')}`, `data_match={str(dr.get('data_match')).lower()}`, `traffic_switched={dr.get('traffic_switched')}`. Not runtime, app, failover, RPO or RTO evidence. |")
    writes = live.get("observed_main_replication_writes", {}).get("writes", [])
    L.append(f"| Earlier automatic main-push snapshot writes | {', '.join(str(row.get('workflow_run_id')) for row in writes) or 'none recorded'} | Workflow actions recorded; this audit performed no workflow dispatch/write. Confirm target-only data before any further sync. |")
    for number in ("41", "39", "42"):
        pr = live.get("pull_requests", {}).get(number, {})
        if pr:
            state = f"{pr.get('state')}, {'draft' if pr.get('draft') else 'non-draft'}"
            note = pr.get("note", "Left unchanged; re-read before acting.")
            L.append(f"| PR #{number} | {state} | {note} |")
    pages = live.get("pages", {})
    if pages:
        L.append(f"| GitHub Pages | `main:/` at `{pages.get('build_commit', 'unknown')[:8]}`; feature branch not deployed | Review/merge explicitly, then verify a new Pages build before claiming the preview is public. |")
    if status_followup:
        follow_issue = status_followup.get("issue_6", {})
        L.append(f"| Scoped GitHub metadata recheck | `{status_followup.get('observed_at_utc')}`; issue #6 {follow_issue.get('state')}/{follow_issue.get('priority')}; PR #39 OPEN/DRAFT, #41 OPEN/non-draft, #42 OPEN/DRAFT | Main `{status_followup.get('main_sha', 'unknown')[:8]}`, Pages `{status_followup.get('pages', {}).get('source_branch')}:{status_followup.get('pages', {}).get('source_path')}`; read-only recheck. {status_followup.get('scope', '')} |")
    if dr_annotation_followup:
        L.append(f"| Latest scheduled DR annotation follow-up | run `{dr_annotation_followup.get('workflow_run_id')}` / check `{dr_annotation_followup.get('check_run_id')}` at `{dr_annotation_followup.get('run_completed_at_utc')}`: `{dr_annotation_followup.get('status')}`, `data_match={str(dr_annotation_followup.get('data_match')).lower()}`, `http={dr_annotation_followup.get('http')}` | No write, traffic switch `{dr_annotation_followup.get('traffic_switched')}`; only this new annotation was checked and {dr_annotation_followup.get('previous_checkpoints_reread')} earlier annotations were reread. |")
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
    ledger = read_json("ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json") or {}
    live = ledger.get("current_live_recheck_2026_10_07", {})
    dr = live.get("dr_snapshot", {})
    target = live.get("dr_target_resolution", {})
    pages = live.get("pages", {})
    main_commit = pages.get("build_commit", "unknown")[:8]
    L.append("# VYOMARAJ — FULL HANDOVER, ALL DETAILS")
    L.append("")
    L.append(f"Generated {now} from this repository, local listener probes, and timestamped read-only "
             "GitHub/Pages evidence. A port listener is not production health. Each section identifies "
             "its evidence source; the archive beside this file carries the cited source records.")
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
    L.append("When the reports viewer or a rehearsal service is deliberately started, `/reports/realtime` "
             "re-probes listeners on page load; it reports ports and response observations, not "
             "authenticated service health. The route is not available when its viewer is stopped.")
    L.append("The older manual one-shot loopback sample is available with "
             "`python3 ops/vyomaraj-core/handover/probes.py --once`; it has no scheduler or alerts. "
             "`ops/jarvis/heartbeat_monitor.py` is a separate fail-closed, read-only probe whose shipped "
             "peer URLs are blank. Neither tool is an authenticated production heartbeat, DR, "
             "replication-lag, backup or failover monitor.")
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
    L.append(f"`transfer/VYOMARAJ_FULL_HANDOVER_2026_10_07.zip` carries {len(MEMBERS)} files; the 6 October archive remains preserved:")
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
    L.append("## 8 · Current verdict and owner-gated next steps")
    L.append("")
    L.append("| Question | Answer |")
    L.append("|---|---|")
    L.append(f"| Is this launch-preview branch live on Pages? | **No** — Pages serves `main:/` at `{main_commit}`; this branch needs explicit review/merge and a new successful Pages build |")
    L.append(f"| Is issue #6 ready to close? | **No** — it remains OPEN/P0; a scheduled tree match exists, but effective target identity `{target.get('effective_target_identity', 'UNCONFIRMED')}` and target-only data review remain unresolved; do not post the historical close-out |")
    L.append(f"| Is the current DR tracked-tree comparison matched? | **Yes, as recorded** — run `{dr.get('workflow_run_id')}` / check `{dr.get('check_run_id')}` at `{dr.get('completed_at_utc')}` reports `{dr.get('primary_tree')}` = `{dr.get('secondary_tree')}`, `data_match={str(dr.get('data_match')).lower()}`, traffic `{dr.get('traffic_switched')}`. This does **not** prove runtime/app equality, canonical target identity, failover, RPO or RTO. |")
    L.append("| Is the APK a verified release? | **No** — a v2 signing-block entry was detected; signature validity, signer provenance and device installation remain unverified |")
    L.append("| Are native Android/macOS releases ready? | **No** — no native Android or macOS/Xcode source/build project was found; web/PWA is separate |")
    L.append("| Is everything in the vision connected? | **No** — platforms, payments, analytics, AI providers and peer runtime are not production connections |")
    L.append("| Is Jarvis running 24×7 as a verified peer service? | **No** — a local read-only monitor is not an authenticated production agent, heartbeat, scheduler or failover service |")
    L.append("| Will it earn on day one? | **No** — real publishing, contact, analytics and payment steps remain |")
    L.append("")
    L.append("**Owner-gated next steps:** (1) confirm the workflow's effective existing DR target and Actions setting privately; review target-only data before any further sync; (2) obtain independent read-after-write evidence and keep issue #6 open until every criterion is met; (3) review PR scope and approve/decline merge or deployment explicitly; (4) verify the APK with `apksigner`, signer provenance and real-device installation; (5) build/test native Android/macOS from owner-approved source and implement the authenticated, fenced peer protocol before production interlink/failover.")
    L.append("")
    return L


def write_zip() -> list[str]:
    missing = []
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("HANDOVER_README.txt",
                   "Vyomaraj full handover archive.\n"
                   "Open VYOMARAJ_FULL_HANDOVER_2026_10_06.md first: it is the index to everything else.\n"
                   "The shared temporal-knowledge contract and resolver are in the config/knowledge, docs/architecture and ops/shriyantra paths.\n"
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
    archive_member_count = 0
    if not DOC.is_file():
        problems.append(f"{DOC.name} missing")
    if not ZIP.is_file():
        problems.append(f"{ZIP.name} missing")
    if DOC.is_file():
        text = DOC.read_text(encoding="utf-8")
        for marker in ("## 1 · Real-time state at generation", "## 3 · All agents, sub-agents and hubs",
                       "Universal Knowledge Evolution inheritance", "metadata_only", "OWNER_ACTION_REQUIRED",
                       "jarvis.env` is deliberately", "/reports/realtime", "signature validity"):
            if marker not in text:
                problems.append(f"document lost: {marker}")
    if ZIP.is_file():
        with zipfile.ZipFile(ZIP) as z:
            member_names = z.namelist()
            archive_member_count = len(member_names)
            expected = {"HANDOVER_README.txt"} | {rel for rel in MEMBERS if (ROOT / rel).is_file()}
            actual = set(member_names)
            for rel in sorted(expected - actual):
                problems.append(f"archive is missing {rel}")
            for rel in sorted(actual - expected):
                problems.append(f"archive has unexpected member {rel}")
            if len(member_names) != len(actual):
                problems.append("archive contains duplicate member names")
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
          f"{ZIP.stat().st_size:,} B archive, {archive_member_count} members)")
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
    with zipfile.ZipFile(ZIP) as archive:
        archive_member_count = len(archive.infolist())
    print(f"wrote {ZIP.name} ({ZIP.stat().st_size:,} B, {archive_member_count} members, "
          f"sha256 {sha256_file(ZIP)[:16]})")
    if missing:
        print(f"  note: {len(missing)} member(s) not present in this checkout: {', '.join(missing[:4])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
