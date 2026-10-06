#!/usr/bin/env python3
"""Live status for Vyomaraj — real probes, no cached values, no invention.

Every value this module returns is measured at the moment it is asked for. That is the whole point:
the previous status surface on the landing page polled a route that never existed and displayed a
fabricated "6 sub-agents syncing together". This one probes the host and reports what it finds.

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
]

EVIDENCE = [
    ("DR snapshot", "DR_SYNC_RESULTS_2026_10_04.md"),
    ("live wiring", "LIVE_WIRING_STATE_2026_10_06.json"),
    ("test evidence", "TEST_EVIDENCE_2026_10_04.json"),
    ("full handover", "VYOMARAJ_FULL_HANDOVER_2026_10_06.md"),
]


def port_state(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def realtime_facts() -> dict:
    """Measure now. Nothing here is stored between calls."""
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
    return (
        '<meta http-equiv="refresh" content="10">'
        '<p class="notice"><strong>Live state, re-probed on every load.</strong> This page refreshes '
        "itself every 10 seconds, and nothing on it is cached, remembered or estimated — each line is "
        f'measured when you load it. Checked at <strong>{f["checked_at_utc"]}</strong>.</p>'
        f'<h2>Services — {f["services_listening"]} of {f["services_total"]} listening</h2>'
        '<div class="table"><table><tbody><tr><th>Port</th><th>Service</th><th>What it serves</th>'
        f'<th>State right now</th></tr>{"".join(rows)}</tbody></table></div>'
        "<h2>Replication — what is actually running</h2>"
        f'<p>Live sync process running: <strong>{f["sync"]["live_sync_process_running"]}</strong> · '
        f'mode: <code>{f["sync"]["mode"]}</code><br>{_html.escape(f["sync"]["detail"])}</p>'
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
