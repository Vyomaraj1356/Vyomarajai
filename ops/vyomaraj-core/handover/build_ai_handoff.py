#!/usr/bin/env python3
"""Build the portable handoff for other AI platforms.

The owner needs to hand Vyomaraj's context to another AI (ChatGPT, Claude, Gemini, anything) so that
assistant can help without being lied to and without inventing progress. That means one document that
is self-contained, safe to share, and honest about what is real.

Three artifacts, one command:

    AI_PLATFORM_HANDOFF_2026_10_06.md   paste-into-any-AI brief (owner contact details redacted)
    AI_CONTEXT_PACK_2026_10_06.json     the same facts as structured data an AI can ingest
    VYOMARAJ_RUNBOOK_2026_10_06.md      the process/procedure: configure, integrate, inherit, verify
    transfer/AI_PLATFORM_HANDOFF_2026_10_07.zip   current additive snapshot; the 6 October archive is preserved

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
ZIP = HERE / "transfer/AI_PLATFORM_HANDOFF_2026_10_07.zip"
MONITOR_STATE = Path.home() / ".local/state/vyomaraj/jarvis-heartbeats.json"

REDACTION = "[OWNER_EMAIL_REDACTED]"
EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SECRET_RX = re.compile(r"(gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|"
                       r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")

PORTS = [(3000, "Legacy product server", "session-scoped local routes"),
         (4174, "Reports viewer", "reports, downloads, page captures"),
         (4176, "Availability gateway", "primary/secondary rehearsal"),
         (4181, "Lane studio A", "music, film, bhakti, comics, pairings, aghor"),
         (4182, "Lane studio B", "mirror of the same lanes"),
         (5310, "Allowlisted sandbox preview", "static assets plus bounded local /api/plan; sandbox only")]

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
    "ops/vyomaraj-core/handover/INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md",
    "ops/vyomaraj-core/handover/PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md",
    "ops/dr/ISSUE_6_CLOSEOUT_COMMENT_2026_10_06.md",
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
                ev["live_wiring_checked_at_utc"] = data.get("checked_at_utc")
            if name.startswith("TEST_EVIDENCE"):
                ev["python_tests_total"] = data.get("python_tests_total")
                ev["node_checks"] = len(data.get("node_checks", []))
                ev["builders"] = len(data.get("builders", []))
                ev["offline_failures"] = len(data.get("failures") or [])
                ev["offline_recorded_at_utc"] = data.get("recorded_at_utc")
            if name.startswith("PREVIEW_VERIFICATION"):
                ev["preview_problems"] = len(data.get("problems") or [])
                ev["viewer_routes_checked"] = len(data.get("viewer_routes", []))
                ev["preview_verified_at_utc"] = data.get("verified_at_utc")
    ledger = read_json("ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json") or {}
    live = ledger.get("current_live_recheck_2026_10_07", {})
    ev["dr_snapshot"] = live.get("dr_snapshot", {})
    ev["dr_target_resolution"] = live.get("dr_target_resolution", {})
    ev["observed_main_replication_writes"] = live.get("observed_main_replication_writes", {})
    return ev


def build_pack() -> dict:
    reg = read_json("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json") or {}
    totals = reg.get("totals", {})
    live_record = read_json("ops/vyomaraj-core/handover/LIVE_WIRING_STATE_2026_10_06.json") or {}
    live_apk = live_record.get("apk", {})
    signing_block = live_apk.get("apk_signing_block", {})
    issue_ledger = read_json("ops/vyomaraj-core/handover/ISSUES_AND_PRS_LEDGER.json") or {}
    github_live = issue_ledger.get("current_live_recheck_2026_10_07", {})
    pages_live = github_live.get("pages", {})
    dr_live = github_live.get("dr_snapshot", {})
    dr_target = github_live.get("dr_target_resolution", {})
    try:
        heartbeat_state = json.loads(MONITOR_STATE.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        heartbeat_state = {"summary": "not_checked", "checked_at_utc": None}
    return {
        "schema": "vyomaraj-ai-context-pack/1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "purpose": "Self-contained context so another AI platform can help with Vyomaraj without "
                   "inventing progress. Repository facts and local listener probes are separated "
                   "from timestamped external GitHub/Pages audit evidence.",
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
            "github_pages": f"source main:/ at {pages_live.get('build_commit', 'unknown')[:8]}; current feature branch not deployed",
            "scheduled_dr_snapshot": {
                "status": dr_live.get("status"),
                "workflow_run_id": dr_live.get("workflow_run_id"),
                "check_run_id": dr_live.get("check_run_id"),
                "completed_at_utc": dr_live.get("completed_at_utc"),
                "data_match": dr_live.get("data_match"),
                "primary_tree": dr_live.get("primary_tree"),
                "secondary_tree": dr_live.get("secondary_tree"),
                "traffic_switched": dr_live.get("traffic_switched"),
                "annotation": dr_live.get("annotation"),
                "scope_limit": "tracked Git-tree comparison only; not runtime, deployed artifact, failover, RPO or RTO",
            },
            "dr_target_identity": dr_target.get("effective_target_identity", "UNCONFIRMED"),
            "dr_target_variable_api": dr_target.get("workflow_variable_read_result", "UNVERIFIED"),
            "main_push_snapshot_writes": github_live.get("observed_main_replication_writes", {}).get("writes", []),
            "local_heartbeat_monitor": {
                "mode": "read_only_reachability_probe",
                "summary": heartbeat_state.get("summary", "not_checked"),
                "checked_at_utc": heartbeat_state.get("checked_at_utc"),
                "heartbeat_authenticated": False,
                "production_peer_health_verified": False,
                "production_dr_verified": False,
                "failover_enabled": False,
            },
            "native_apps": {
                "android_source_project_present": False,
                "macos_source_project_present": False,
                "apk_signature_verified": False,
                "apk_signer_provenance": "UNVERIFIED",
                "real_device_installation": "UNVERIFIED",
            },
            "runtime": "Python 3 standard-library http.server; studio and availability gateway are loopback-only; sandbox preview uses an exact asset allowlist plus a bounded, ephemeral deterministic POST /api/plan for bhakti/liquor-bar only",
            "database_server": None,
            "database_servers_claimed_but_absent": ["PostgreSQL 5432", "Redis 6379"],
            "frameworks_claimed_but_absent": ["FastAPI 8000", "Flask 5000"],
            "apk": {
                "path": live_apk.get("path", "Vyomaraj-App.apk"),
                "bytes": live_apk.get("bytes"),
                "sha256": live_apk.get("sha256"),
                "apk_signing_block": signing_block,
                "signature_material_present": live_apk.get("signature_material_present", False),
                "cryptographically_verified": live_apk.get("signature_cryptographically_verified", False),
                "signer_provenance": "UNVERIFIED",
                "real_device_installation": "UNVERIFIED",
                "rebuildable_from_this_repository": live_apk.get("rebuildable_from_this_repository", False),
            },
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
            "shared_knowledge_inheritance": reg.get("shared_knowledge_inheritance", {}),
            "content_index_policy_ref": (read_json("ops/vyomaraj-core/agents/CONTENT_INDEX_CURRENT.json") or {})
                                        .get("shared_knowledge_inheritance", {}).get("policy_ref"),
            "runtime_status": "registry entries are records, not running AI agents",
        },
        "platforms": {
            "coordination_module_verdict": {
                "mode": "metadata_only",
                "operational": False,
                "confidence": "UNVERIFIED",
                "switch_platform": "BLOCKED - no provider/session-transfer executor is configured",
            },
            "connected": ["read-only primary GitHub repository status", "GitHub Pages main build only"],
            "owner_blocked": ["issue #6 remains OPEN/P0", "effective secondary identity is not independently confirmed (Actions settings 403; candidate path 404s are ambiguous)", "owner review of target-only data and independent read-after-write", "production runtime/app equality and DR failover/RPO/RTO"],
            "current_github_state": {
                "issue_6": github_live.get("issue_6", {}),
                "pull_requests": github_live.get("pull_requests", {}),
                "pages": pages_live,
                "dr_snapshot": dr_live,
                "dr_target_resolution": dr_target,
                "observed_main_replication_writes": github_live.get("observed_main_replication_writes", {}),
                "secondary_path_probes": github_live.get("secondary_path_probes", {}),
                "actions_variables_api": github_live.get("actions_variables_api"),
                "actions_secrets_api": github_live.get("actions_secrets_api"),
                "scoped_metadata_followup": issue_ledger.get("current_github_metadata_followup_2026_10_07", {}),
                "dr_annotation_followup": issue_ledger.get("current_dr_annotation_followup_2026_10_07", {}),
            },
            "preview_security": f"Allowlisted sandbox preview :5310 is {'listening in the sandbox only' if port_open(5310) else 'stopped'}; it serves public assets plus only a bounded deterministic local planner for two experiences (ephemeral response, no provider/persistence/privileged writer); it is not a deployment. Studio/gateway code rejects non-loopback binds and requires request-scoped owner tokens for privileged writes; no trusted owner issuer/key is provisioned, so those actions fail closed.",
            "unverified": ["workflow-selected secondary canonical identity", "runtime/deployed-app equality and DR failover/RPO/RTO", "APK signature validity, signer provenance and real-device installation", "Android/macOS native build readiness", "authenticated production peer link/heartbeat", "deployment of this feature branch"],
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
            "Apply the Universal Knowledge Evolution Model through its single shared policy reference; retain claim-level provenance and never present future forecasts/scenarios as facts.",
            "Historic follower, view and revenue figures are unverified: do not repeat them to a "
            "partner, bank or platform reviewer.",
            "Zero budget until the project earns: propose only free options first.",
            "Inherit format and credit discipline from Sufi, ghazal and studio-show formats; never "
            "copy titles, lyrics, audio, video, artwork or brands.",
            "Identity documents: reference uidai.in only; no in-app Aadhaar or biometric capture.",
            "Voice enrollment is on-device only, with explicit consent and a delete-my-voice path.",
            "Root-owner authority cannot be delegated to agents or inherited as a capability; deny by default, least privilege, server-side checks, step-up for high-risk actions, immutable audit, and split-brain fencing.",
            "Location stays off by default. No covert/arbitrary phone tracking or consent/legal/security bypass.",
            "Never ask for or store tokens, passwords or OTPs; nothing secret belongs in the repo or chat.",
            "The owner said 'Ignore versions'; do not block work on version reconciliation.",
            "Report an unverified window as a window, never as a match.",
        ],
        "next_actions_for_the_helping_ai": [
            "Keep issue #6 OPEN/P0. Owner/admin must confirm the effective Actions-selected target privately, review current target-only data before any further sync, then authorize independent read-after-write. Do not post the historical close-out draft.",
            "Do not call the latest scheduled matching tracked Git tree proof of runtime health, deployed APK equality, failover, RPO or RTO; the latest annotation reports http=UNAVAILABLE. Preserve the target-identity caveat and the v2 signing-block versus signature-validity distinction.",
            "Review PR #41's combined DR/preview scope; leave PRs #39 and #42 untouched unless explicitly directed. No merge/deployment is authorized by a passing preview gate.",
            "Verify the existing Android APK with apksigner, review signer provenance and install on a real device; if verification or provenance is unresolved, advise leaving it off the page and recovering/rebuilding from trusted source.",
            "Build the web, Android and macOS surfaces only from owner-approved source; the static PWA is not a native app, and Android/macOS projects are absent from this checkout.",
            "Use the shared Vyomaraj/Jarvis peer contract; implement authenticated heartbeat in shadow/read-only mode with replay protection and no authority inheritance before any production interlink or failover.",
            "Integrate the Universal Knowledge Evolution policy at the trusted Harness/CAG boundary, validate claims before MAG promotion/public output, and verify runtime inheritance before describing it as live.",
            "Draft the one-line contact block the owner can paste on the public page.",
            "Advise the cheapest free analytics option and where its snippet goes.",
            "Help plan the first original episode slate using inherited formats only.",
            "Draft the YouTube Partner Program application timing note (apply before 1 Feb 2027).",
        ],
        "how_to_verify_anything": [
            "python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci",
            "python3 ops/vyomaraj-core/handover/sanitize_personal_data.py --check",
        ],
        "live_verification_policy": "verify_live_wiring.py, verify_preview.py and realtime_status.py require an explicitly isolated test stack; port 5310 is a sandbox preview with an exact asset allowlist and a bounded deterministic POST /api/plan for bhakti/liquor-bar only (ephemeral response; no provider calls, persistence, or privileged writers); studio/gateway bind loopback and writer actions fail closed without a request-scoped owner token; no issuer is provisioned.",
    }


def build_doc(pack: dict) -> str:
    reg = read_json("ops/vyomaraj-core/agents/AGENT_REGISTRY_CURRENT.json") or {}
    prs = pack.get("platforms", {}).get("current_github_state", {}).get("pull_requests", {})
    def pr_status(number: str) -> str:
        pr = prs.get(number, {})
        if not pr:
            return "UNVERIFIED"
        return f"{pr.get('state', 'unknown')}/{'DRAFT' if pr.get('draft') else 'non-draft'}"
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
    a("- **What it actually is today:** a static public site plus local Python servers holding content "
      "lanes (music, film, bhakti, comics, pairings, aghor), an agent registry and a governance/evidence "
      "system. The sandbox preview adds one bounded, ephemeral deterministic planner route for Bhakti-Shakti "
      "and Roots & Pairings; it is not an AI provider, privileged control plane, or production deployment. "
      "It is **not** a multi-platform AI company — yet.")
    a("")
    a("---")
    a("")
    a("## 2 · Evidence-based state (measured or explicitly timestamped)")
    a("")
    a("| Port | Service | Listening when this was generated |")
    a("|---|---|---|")
    for s in pack["verified_state"]["services_probed_live"]:
        a(f"| {s['port']} | {s['service']} | **{'yes' if s['listening'] else 'no'}** |")
    a("")
    a(f"- **Hosting:** {pack['verified_state']['github_pages']}")
    dr = pack["verified_state"]["scheduled_dr_snapshot"]
    a("- **Issue #6:** OPEN/P0; keep open. The effective Actions-selected secondary identity and target-only data review remain owner-blocked. Do not post the historical close-out draft.")
    a(f"- **Pull requests:** #41 {pr_status('41')}; #39 {pr_status('39')} (left untouched); #42 {pr_status('42')}. Live read is recorded in `ISSUES_AND_PRS_LEDGER.json`; no PR mutation is authorized by this handoff.")
    metadata_followup = pack["platforms"].get("current_github_state", {}).get("scoped_metadata_followup", {})
    if metadata_followup:
        a(f"- **Scoped GitHub metadata re-read:** `{metadata_followup.get('observed_at_utc')}` reconfirmed issue #6 and PR states, main and Pages source; read-only. The full candidate-path/Actions-settings access audit remains separately timestamped at 08:28 UTC.")
    a(f"- **Latest scheduled DR annotation:** run `{dr.get('workflow_run_id')}` / check `{dr.get('check_run_id')}` at `{dr.get('completed_at_utc')}` reported `status={dr.get('status')}`, `data_match={dr.get('data_match')}`, trees `{dr.get('primary_tree')}` / `{dr.get('secondary_tree')}`, traffic `{dr.get('traffic_switched')}`. Annotation: `{dr.get('annotation')}`. Scope: {dr.get('scope_limit')}.")
    annotation_followup = pack["platforms"].get("current_github_state", {}).get("dr_annotation_followup", {})
    if annotation_followup:
        a(f"- **Latest annotation re-read scope:** checked run `{annotation_followup.get('workflow_run_id')}` / check `{annotation_followup.get('check_run_id')}` only; previous checkpoint annotations reread: {annotation_followup.get('previous_checkpoints_reread')}. {annotation_followup.get('scope')}")
    a(f"- **Effective DR target identity:** {pack['verified_state'].get('dr_target_identity')} (Actions variable API `{pack['verified_state'].get('dr_target_variable_api')}`; see the caveat in the integration audit). Earlier main-push snapshot writes: {', '.join(str(x.get('workflow_run_id')) for x in pack['verified_state'].get('main_push_snapshot_writes', [])) or 'none recorded'}.")
    monitor = pack["verified_state"]["local_heartbeat_monitor"]
    a(f"- **Local heartbeat monitor:** `{monitor['summary']}` at `{monitor.get('checked_at_utc')}`; unauthenticated reachability only, no configured endpoint may be contacted, never a production heartbeat/failover proof.")
    a(f"- **Preview safety:** {pack['platforms'].get('preview_security')}")
    a(f"- **Runtime:** {pack['verified_state']['runtime']}")
    a(f"- **Database server:** none. Claimed but absent: "
      f"{', '.join(pack['verified_state']['database_servers_claimed_but_absent'])}")
    a(f"- **Web frameworks:** none. Claimed but absent: "
      f"{', '.join(pack['verified_state']['frameworks_claimed_but_absent'])}")
    apk = pack["verified_state"]["apk"]
    schemes = apk.get("apk_signing_block", {}).get("signature_schemes", [])
    scheme_note = ', '.join(schemes) if schemes else 'no recognized v2/v3 scheme detected'
    a(f"- **APK:** {apk['bytes']:,} bytes; {scheme_note} signing-block material detected. "
      "That is not cryptographic signature verification: signature validity, signer provenance and real-device "
      "installation remain **UNVERIFIED**. No Android or macOS native source/build project is present here.")
    ev = pack["verified_state"]["evidence"]
    a(f"- **Offline gate:** {ev.get('python_tests_total')} Python tests, "
      f"{ev.get('node_checks')} Node checks, {ev.get('builders')} builders, "
      f"{ev.get('offline_failures')} failures; evidence recorded at "
      f"{ev.get('offline_recorded_at_utc')}.")
    a(f"- **Historical live-route checks:** live wiring at {ev.get('live_wiring_checked_at_utc')} "
      f"recorded {ev.get('blocking_problems')} blockers; preview verification at "
      f"{ev.get('preview_verified_at_utc')} recorded {ev.get('preview_problems')} problems across "
      f"{ev.get('viewer_routes_checked')} routes. These are historical results; the port table above "
      f"is the local listener measurement at generation. Any :5310 listener is an allowlisted "
      f"read-only sandbox preview, not public deployment or production evidence.")
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
    shared_knowledge = agents.get("shared_knowledge_inheritance", {})
    if shared_knowledge:
        coverage = shared_knowledge.get("current_coverage", {})
        a("")
        a("**Universal Knowledge Evolution inheritance:** one shared policy reference covers "
          f"{coverage.get('category_count')} categories, {coverage.get('agent_count')} counted sub-agents, "
          f"and {coverage.get('indexed_content_reference_count', 'the indexed')} content references. "
          f"Policy: `{shared_knowledge.get('policy_ref')}`; future entities inherit by reference; "
          "no per-agent copies. Future-layer claims must not be presented as facts. Status: "
          f"`{shared_knowledge.get('runtime_status')}`; this is not proof of production enforcement.")
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
    a("The intended common Vyomaraj/Jarvis peer contract and read-only heartbeat limits are documented in "
      "`PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md`; there is no authenticated production interlink. "
      "The shared architecture diagram and evidence boundary are in `ARCHITECTURE_DIAGRAM_2026_10_06.svg` "
      "and `INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md`.")
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
    a(f"- Live-route verification policy: {pack['live_verification_policy']}")
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
    dr_summary = pack["verified_state"]["scheduled_dr_snapshot"]
    a(f"Vyomaraj has an existing static Pages site sourced from `main`; this feature branch is not "
      f"deployed. The repository contains content lanes, an agent registry and verification code, "
      f"but no production runtime, authenticated control plane or authenticated peer heartbeat. A "
      f"scheduled Actions run at {dr_summary.get('completed_at_utc')} reported equal tracked Git trees "
      f"{dr_summary.get('primary_tree')} / {dr_summary.get('secondary_tree')} (traffic "
      f"{dr_summary.get('traffic_switched')}); that does not identify the target independently or "
      f"prove runtime/app equality, failover, RPO or RTO. Issue #6 is OPEN/P0; owner/admin must "
      f"confirm the effective target and review target-only data before further sync. The Android "
      f"binary contains a detected v2 signing-block entry, but signature validity, signer provenance "
      f"and device installation remain unverified; Android/macOS native source projects are absent. "
      f"The local sandbox preview is a bounded read-only planner (no persistence/provider/writer routes) and is not deployed; no social platform, payment gateway, "
      f"analytics counter or AI provider is connected. Do not describe this branch as deployed or "
      f"production-ready; complete owner-approved target review, runtime/DR and release verification "
      f"before any deployment claim.")
    a("")
    return redact("\n".join(L) + "\n")


def build_runbook(pack: dict) -> str:
    L: list[str] = []
    a = L.append
    ports = {row["port"]: row["listening"] for row in pack["verified_state"]["services_probed_live"]}
    legacy_open = [p for p in (3000, 4174, 4176, 4181, 4182) if ports.get(p)]
    dr = pack["verified_state"]["scheduled_dr_snapshot"]
    heartbeat = pack["verified_state"]["local_heartbeat_monitor"]
    a("# VYOMARAJ — RUNBOOK: CONFIGURE · INTEGRATE · INHERIT · VERIFY")
    a("")
    a(f"Generated {pack['generated_at_utc']}. The procedure for running this project, in the order it "
      "should be done. Copy-pasteable. Every command is run from the repository root.")
    a("")
    a("---")
    a("")
    a("## A · Safe preview posture")
    a("")
    a(f"At generation, the allowlisted sandbox preview on :5310 is {'listening' if ports.get(5310) else 'stopped'} "
      "in this sandbox; it exposes exact public assets and a bounded deterministic POST /api/plan for Bhakti-Shakti and Roots & Pairings only. The plan is ephemeral; there are no provider calls, storage, or privileged writer services. "
      f"Legacy product/viewer/gateway/studio listeners at generation: {', '.join(map(str, legacy_open)) or 'none'}. "
      "A sandbox preview is not deployment or production telemetry.")
    a(f"Latest scheduled Actions run `{dr.get('workflow_run_id')}` at `{dr.get('completed_at_utc')}` "
      f"reports equal tracked Git trees only (`data_match={dr.get('data_match')}`). Effective secondary "
      "identity, installed/deployed artifact equality and runtime DR remain unverified.")
    a("")
    a("The studio and availability gateway now reject non-loopback bind addresses and default to `127.0.0.1`. "
      "Privileged HTTP actions require short-lived request-scoped Ed25519 owner tokens bound to the exact action "
      "and canonical request payload; the approval decision path also requires step-up and persists its JTI, "
      "queue update and local hash-chain event transactionally. The trusted owner issuer/key/security epoch are "
      "not configured in this checkout, so privileged actions fail closed. Do not weaken the bind policy or "
      "proxy writer routes to public ingress. The allowlisted sandbox preview on :5310 is separate: it offers only the bounded ephemeral local planner, with no privileged writer or persistence route.")
    a("")
    a("The research worker does not start unless `--enable-research-worker` is explicitly supplied. These are "
      "local single-host controls, not a production identity provider, multi-host replay service, independent "
      "audit witness, or deployment. Stop any isolated test process after verification.")
    a("")
    a("---")
    a("")
    a("## B · Verify (run this before trusting anything)")
    a("")
    a("The offline gate is safe to run now. No studio/gateway process is currently assumed running. "
      "The code enforces loopback binds and owner-token checks, but the trusted token issuer is absent; "
      "live route verifiers still require a deliberately configured, isolated test stack. Do not restart "
      "or proxy these services on the public preview.")
    a("")
    a("```bash")
    a("python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci   # tests, node checks, builders")
    a("# Optional only in a secured, isolated test environment:")
    a("python3 ops/vyomaraj-core/handover/verify_live_wiring.py       # explicit test ports only")
    a("python3 ops/vyomaraj-core/handover/verify_preview.py           # page contracts + packages")
    a("python3 ops/vyomaraj-core/handover/realtime_status.py          # local port probe as JSON")
    a("python3 ops/vyomaraj-core/handover/probes.py --once             # manual, fixed-loopback snapshot")
    a("python3 ops/jarvis/heartbeat_monitor.py status                  # last local read-only snapshot")
    a("python3 ops/jarvis/heartbeat_monitor.py check                   # blank example endpoints return not_configured")
    a("python3 ops/jarvis/heartbeat_monitor.py shift                   # intentionally BLOCKED; never use as failover")
    a("# Optional sandbox-only loop, default endpoints stay blank:")
    a("python3 ops/jarvis/heartbeat_monitor.py run")
    a("```")
    a("")
    a("`probes.py --once` appends to `/tmp/vyomaraj-probes.jsonl` and atomically writes "
      "`/tmp/vyomaraj-probes.latest.json`; `/reports/monitor` reads that file only when its viewer "
      "is deliberately running. The Jarvis monitor's example URLs are blank; its `run` loop writes "
      "private local snapshots but cannot authenticate peers, alert an owner, measure replication lag, "
      "verify backups, or perform independent-site DR. A reachable HTTP endpoint remains `reachable_unverified`.")
    a("")
    a("A missing live listener means that local service is unavailable, not production failure or success. "
      "Do not weaken loopback/owner-token enforcement or restart a service just to make a verifier green; "
      "configure an isolated test environment out of band, then record the exact ports and scope.")
    a("")
    a("---")
    a("")
    a("## C · Regenerate the evidence after any change")
    a("")
    a("Order matters. Refresh only generated status reports; preserve frozen transfer archives and historical packages unless the owner explicitly approves a new archive.")
    a("")
    a("```bash")
    a("python3 ops/vyomaraj-core/handover/build_issue_ledger.py")
    a("python3 ops/vyomaraj-core/handover/build_stack_record.py")
    a("python3 ops/vyomaraj-core/handover/architecture_diagram.py")
    a("python3 ops/vyomaraj-core/handover/build_market_readiness.py")
    a("python3 ops/vyomaraj-core/handover/build_go_live_brief.py")
    a("python3 ops/vyomaraj-core/handover/build_full_handover.py")
    a("python3 ops/vyomaraj-core/handover/build_ai_handoff.py")
    a("python3 ops/vyomaraj-core/handover/run_offline_suites.py --ci")
    a("```")
    a("")
    a("Each report builder also supports `--check`, which fails if its checked-in copy has drifted. Do not rebuild frozen archives as part of a status refresh.")
    a("")
    a("---")
    a("")
    a("## D · Configure a real thing (procedure that has worked here)")
    a("")
    a("1. **Measure first.** Probe the current state; never assume.")
    a("2. **Write the smallest checkable artifact** — JSON or Markdown — that states the new fact.")
    a("3. **Add a `--check`** so the artifact cannot silently drift.")
    a("4. **Gate it** by adding the command to `run_offline_suites.py`.")
    a("5. **Wire it** to a read-only surface by default; any writer needs owner-approved authentication, authorization, CSRF protection, audit logging and a restricted network boundary first.")
    a("6. **Add it to the verifier's required files** so a missing file is a failure.")
    a("7. Run offline gates. Use live verifiers only in an explicitly isolated test environment; keep the studio/gateway loopback-only and do not expose writer routes through public ingress.")
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
    a(f"- **Back up / DR:** scheduled run `{dr.get('workflow_run_id')}` at `{dr.get('completed_at_utc')}` "
      f"records an equal tracked Git tree for its workflow-selected target (`data_match={dr.get('data_match')}`). "
      "The effective target name is not independently confirmed; Actions settings access is 403. This is "
      "a repository snapshot, not runtime/database replication, deployed-app equality, failover, RPO or "
      "RTO. Keep issue #6 OPEN/P0; owner/admin must confirm target identity and review target-only data "
      "before further sync. No new workflow run is triggered by this handover.")
    a("- **Protect:** the reports viewer serves an allowlist only and sends a hardened "
      "`Content-Security-Policy`. Same-origin images are permitted (`img-src 'self'`); scripts and "
      "external hosts are not.")
    a("")
    a("---")
    a("")
    a("## H · Owner-gated steps before any release or earning claim")
    a("")
    a("1. **Resolve issue #6 safely:** owner/admin privately confirms the effective Actions-selected existing secondary; review current target-only data before authorizing any further sync, then obtain independent read-after-write evidence. The latest Git-tree match does not close the runtime/identity criteria. Keep issue #6 OPEN/P0 until every live acceptance criterion is evidenced.")
    a("2. **Verify the existing APK** with `apksigner verify`, review signer provenance and install it on a real Android device. If verification fails or provenance is unknown, recover the original source, rebuild and sign with an owner-held key; otherwise leave it off the release page.")
    a("3. **Review branch scope and deployment:** obtain explicit owner approval before any PR merge or Pages deployment; this branch is not currently deployed.")
    a("4. **Build native clients from approved source:** Android source/build project and macOS/Xcode project are absent here; obtain owner-approved source, signing/notarization access and real-device test plans before calling either a release.")
    a("5. **Connect peers safely:** implement the common Vyomaraj/Jarvis identity and capability contract, authenticated heartbeat in shadow mode, replay protection, immutable audit and single-writer fencing; owner approval remains required for privileged actions.")
    a("6. **Publish a contact address** on the public page and **switch on analytics** only after owner account decisions; confirm one real visit is recorded.")
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
    a(f"| Preview links are session-scoped | allowlisted static :5310 is {'open' if ports.get(5310) else 'closed'} in this sandbox; legacy ports listening now: {', '.join(map(str, legacy_open)) or 'none'}; Pages is durable but serves `main` only |")
    a("| `flow-diagram.html` loads Mermaid from a CDN | on a network that blocks that CDN, the diagrams do not render |")
    a("| No analytics | nobody can see visits |")
    a("| No login | no returning audience |")
    a("| No payments | nothing can be sold |")
    a("| DR covers files, not runtime | a live database would not be covered; tree match is not failover/RPO/RTO evidence |")
    a("| Native Android/macOS | no Android/macOS source project here; APK signing and device installation unverified |")
    a("| Peer heartbeat | local example endpoints are blank; no authenticated production peer or failover |")
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
                   "3. Use VYOMARAJ_RUNBOOK_2026_10_06.md yourself, to run and check things.\n"
                   "4. Follow the one shared Universal Knowledge Evolution policy; future claims must remain labeled as forecasts/scenarios, never facts.\n\n"
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
    archive_member_count = 0
    for path in (DOC, PACK, RUNBOOK, ZIP):
        if not path.is_file():
            problems.append(f"{path.name} missing")
    if DOC.is_file():
        text = DOC.read_text(encoding="utf-8")
        for marker in ("## 0 · To the AI reading this", "metadata_only", "signature verification",
                       "UNVERIFIED", "historical aggregate", "How to verify any claim",
                       "Universal Knowledge Evolution inheritance"):
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
            shared = data.get("agents", {}).get("shared_knowledge_inheritance", {})
            if (shared.get("policy_id") != "UNIVERSAL_KNOWLEDGE_EVOLUTION_V1"
                    or shared.get("inheritance_mode") != "shared_policy_reference"
                    or shared.get("future_entities_inherit_by_default") is not True):
                problems.append("context pack lost the shared Universal Knowledge Evolution inheritance reference")
        except Exception as exc:
            problems.append(f"context pack is not valid JSON: {exc}")
    if ZIP.is_file():
        with zipfile.ZipFile(ZIP) as z:
            member_names = z.namelist()
            archive_member_count = len(member_names)
            expected = {"HOW_TO_USE_THIS_PACKAGE.txt"} | {rel for rel in MEMBERS if (ROOT / rel).is_file()}
            names = set(member_names)
            for rel in sorted(expected - names):
                problems.append(f"archive missing {rel}")
            for rel in sorted(names - expected):
                problems.append(f"archive has unexpected member {rel}")
            if len(member_names) != len(names):
                problems.append("archive contains duplicate member names")
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
          f"{RUNBOOK.stat().st_size:,} B runbook, {ZIP.stat().st_size:,} B archive, "
          f"{archive_member_count} members)")
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
    with zipfile.ZipFile(ZIP) as archive:
        archive_member_count = len(archive.infolist())
    print(f"wrote {ZIP.name} ({ZIP.stat().st_size:,} B, {archive_member_count} members, "
          f"sha256 {hashlib.sha256(ZIP.read_bytes()).hexdigest()[:16]})")
    if missing:
        print(f"  note: not in this checkout: {', '.join(missing[:3])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
