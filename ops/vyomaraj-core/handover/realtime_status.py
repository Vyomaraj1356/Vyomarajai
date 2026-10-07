#!/usr/bin/env python3
"""Separate live local port probes from timestamped GitHub and monitor evidence.

Local listeners are measured at request time. DR results and the local peer-monitor snapshot keep
their own timestamps and scope; neither is silently upgraded into current production health.

Used by the reports viewer (page + JSON) and the lane studios (JSON).
"""
from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

LIVE_PORTS = [
    (3000, "Product page — static http.server", "index / landing / flow / APK"),
    (4174, "Reports viewer", "reports, downloads, captures"),
    (4176, "Availability gateway", "primary/secondary rehearsal"),
    (4181, "Lane studio A", "music, film, bhakti, comics, pairings, aghor"),
    (4182, "Lane studio B", "mirror of the same lanes"),
    (5310, "Allowlisted sandbox planner preview", "sandbox-only, bounded deterministic local planner; no persistence or privileged writers"),
]

EVIDENCE = [
    ("DR snapshot", "DR_SYNC_RESULTS_2026_10_04.md"),
    ("live wiring", "LIVE_WIRING_STATE_2026_10_06.json"),
    ("test evidence", "TEST_EVIDENCE_2026_10_04.json"),
    ("full handover", "VYOMARAJ_FULL_HANDOVER_2026_10_06.md"),
    ("integration audit", "INTEGRATION_ALIGNMENT_AND_RELEASE_AUDIT_2026_10_07.md"),
    ("peer architecture", "PEER_ARCHITECTURE_AND_HEARTBEAT_2026_10_07.md"),
]
ISSUES_LEDGER = HERE / "ISSUES_AND_PRS_LEDGER.json"
HEARTBEAT_STATE = Path.home() / ".local/state/vyomaraj/jarvis-heartbeats.json"


def port_state(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def realtime_facts() -> dict:
    """Probe listeners now; attach timestamped records without relabeling them as live health."""
    facts = {
        "schema": "vyomaraj-realtime/1",
        "checked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "services": [
            {"port": port, "service": what, "detail": detail, "listening": port_state(port)}
            for port, what, detail in LIVE_PORTS
        ],
        "evidence": {},
        "sync": {
            "live_sync_process_running": False,
            "mode": "repository_evidence_only",
            "detail": "replication is a GitHub Actions job on push and schedule, "
                      "not a background process in this server",
        },
        "not_probed": [80, 443],
        "not_probed_reason": "nothing in this repository binds privileged ports",
    }
    try:
        ledger = json.loads(ISSUES_LEDGER.read_text(encoding="utf-8"))
        current = ledger.get("current_live_recheck_2026_10_07", {})
    except (OSError, UnicodeError, json.JSONDecodeError):
        current = {}
    dr = current.get("dr_snapshot", {})
    target = current.get("dr_target_resolution", {})
    facts["sync"]["latest_scheduled_checkpoint"] = {
        "status": dr.get("status", "UNVERIFIED"),
        "workflow_run_id": dr.get("workflow_run_id"),
        "check_run_id": dr.get("check_run_id"),
        "completed_at_utc": dr.get("completed_at_utc"),
        "data_match": dr.get("data_match"),
        "primary_tree": dr.get("primary_tree"),
        "secondary_tree": dr.get("secondary_tree"),
        "traffic_switched": dr.get("traffic_switched"),
        "scope_limit": "tracked Git tree only; not runtime/app equality, failover, RPO or RTO",
    }
    facts["sync"]["effective_target_identity"] = target.get("effective_target_identity", "UNCONFIRMED")
    try:
        heartbeat = json.loads(HEARTBEAT_STATE.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        heartbeat = {"summary": "not_checked", "checked_at_utc": None}
    facts["local_peer_monitor"] = {
        "summary": heartbeat.get("summary", "not_checked"),
        "checked_at_utc": heartbeat.get("checked_at_utc"),
        "heartbeat_authenticated": False,
        "production_peer_health_verified": False,
        "production_dr_verified": False,
        "failover_enabled": False,
    }
    for label, name in EVIDENCE:
        path = HERE / name
        if path.is_file():
            facts["evidence"][label] = {"file": name, "bytes": path.stat().st_size}
    wiring = HERE / "LIVE_WIRING_STATE_2026_10_06.json"
    if wiring.is_file():
        try:
            data = json.loads(wiring.read_text(encoding="utf-8"))
            blocking = data.get("blocking_problems") or data.get("problems") or []
            facts["blocking_problems"] = len(blocking)
        except Exception:
            facts["blocking_problems"] = None
    facts["services_listening"] = sum(1 for s in facts["services"] if s["listening"])
    facts["services_total"] = len(facts["services"])
    return facts


def realtime_page() -> str:
    """A live page. `meta refresh` re-probes; there is no JavaScript and no cached value."""
    import html as _html

    f = realtime_facts()
    rows = []
    for s in f["services"]:
        state = "LISTENING" if s["listening"] else "NOT LISTENING"
        colour = "#22c55e" if s["listening"] else "#ef4444"
        rows.append(
            f"<tr><td><code>:{s['port']}</code></td><td>{_html.escape(s['service'])}</td>"
            f"<td>{_html.escape(s['detail'])}</td>"
            f'<td style="color:{colour};font-weight:700">{state}</td></tr>'
        )
    evidence = "".join(
        f"<li><code>{_html.escape(k)}</code> — {v['file']} ({v['bytes']:,} B)</li>"
        for k, v in f["evidence"].items()
    )
    blocking = f.get("blocking_problems")
    blocking_line = (f"<p>Blocking problems recorded in the last wiring run: "
                     f"<strong>{blocking}</strong></p>") if blocking is not None else ""
    checkpoint = f["sync"].get("latest_scheduled_checkpoint", {})
    dr_html = (
        f"<p>Scheduled GitHub run <code>{_html.escape(str(checkpoint.get('workflow_run_id')))}</code> / "
        f"check <code>{_html.escape(str(checkpoint.get('check_run_id')))}</code> at "
        f"<code>{_html.escape(str(checkpoint.get('completed_at_utc')))}</code>: "
        f"status <strong>{_html.escape(str(checkpoint.get('status')))}</strong>, "
        f"<code>data_match={str(checkpoint.get('data_match')).lower()}</code>, "
        f"primary tree <code>{_html.escape(str(checkpoint.get('primary_tree')))}</code>, "
        f"secondary tree <code>{_html.escape(str(checkpoint.get('secondary_tree')))}</code>, "
        f"traffic switched <code>{_html.escape(str(checkpoint.get('traffic_switched')))}</code>. "
        f"Scope: {_html.escape(str(checkpoint.get('scope_limit')))}. "
        f"Effective target identity: <code>{_html.escape(str(f['sync'].get('effective_target_identity')))}</code>.</p>"
    )
    peer = f.get("local_peer_monitor", {})
    peer_html = (
        f"<p>Local monitor summary <code>{_html.escape(str(peer.get('summary')))}</code> "
        f"at <code>{_html.escape(str(peer.get('checked_at_utc')))}</code>; "
        "authenticated heartbeat: <strong>false</strong>; production peer/DR verified: "
        "<strong>false</strong>; failover enabled: <strong>false</strong>.</p>"
    )
    return (
        '<meta http-equiv="refresh" content="10">'
        '<p class="notice"><strong>Local port state is re-probed on every load.</strong> This page refreshes '
        "itself every 10 seconds. The DR checkpoint and peer-monitor snapshot below are timestamped records, "
        f'not live production health. Port probe checked at <strong>{f["checked_at_utc"]}</strong>.</p>'
        f'<h2>Services — {f["services_listening"]} of {f["services_total"]} listening</h2>'
        '<div class="table"><table><tbody><tr><th>Port</th><th>Service</th><th>What it serves</th>'
        f'<th>State right now</th></tr>{"".join(rows)}</tbody></table></div>'
        "<h2>Replication — what is actually running</h2>"
        f'<p>Live sync process running: <strong>{f["sync"]["live_sync_process_running"]}</strong> · '
        f'mode: <code>{f["sync"]["mode"]}</code><br>{_html.escape(f["sync"]["detail"])}</p>'
        "<h2>Latest scheduled DR checkpoint (timestamped, tracked-tree scope)</h2>"
        f"{dr_html}"
        "<h2>Local peer monitor (read-only snapshot)</h2>"
        f"{peer_html}"
        "<h2>Evidence on disk in this checkout</h2>"
        f"<ul>{evidence}</ul>"
        f"{blocking_line}"
        "<h2>Honest limits of this page</h2>"
        "<ul><li>It reports the state of <em>this host</em>. The public site is GitHub Pages, whose "
        "state this page cannot see.</li>"
        "<li>Ports 80 and 443 are not probed because nothing in this repository binds them, and no "
        "social-platform listener exists to probe.</li>"
        "<li>This page lives in the sandbox: when the sandbox ends, so does it. The durable copy is "
        "the repository and the Pages URL.</li></ul>"
    )


if __name__ == "__main__":
    print(json.dumps(realtime_facts(), indent=2))
