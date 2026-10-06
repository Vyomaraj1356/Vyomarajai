#!/usr/bin/env python3
"""Vyomaraj product server — the public pages plus two honest status endpoints.

Why this exists instead of `python3 -m http.server`: the landing page asks for replication status,
and a bare static server answers 404, which is why the product log filled with `/api/sync/status`
404 lines and the status box had nothing to show. This server serves exactly the same static files
and answers two endpoints from measured values:

    GET /api/sync/status   replication facts from checked-in DR evidence
    GET /api/realtime      live probe of every Vyomaraj port on this host

Standing policy for this project: never print a status the host cannot prove. Both endpoints say
`live_sync_process_running: false` because no sync process runs here — replication is a GitHub
Actions job.

    python3 product_server.py --port 3000 --root /path/to/repo
"""
from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent
HANDOVER = CORE / "handover"

spec_ok = True
try:
    import importlib.util

    _spec = importlib.util.spec_from_file_location("realtime_status", HANDOVER / "realtime_status.py")
    realtime = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(realtime)
except Exception as exc:  # pragma: no cover - only hit if the module is missing
    spec_ok = False
    realtime = None
    print(f"warning: realtime_status unavailable ({exc})", file=sys.stderr)


def sync_facts() -> dict:
    """Replication facts read from the checked-in DR record. No invented progress numbers."""
    path = HANDOVER / "DR_SYNC_RESULTS_2026_10_04.md"
    text = path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
    date = re.search(r"DR sync results — (\d{4}-\d{2}-\d{2})", text)
    tip = re.search(r"Main tip covered by this record: `([0-9a-f]{7,40})`", text)
    schedule = re.search(r"schedule: `([^`]+)`", text)
    return {
        "schema": "vyomaraj-sync-status/1",
        "mode": "repository_evidence_only",
        "isSyncing": False,
        "live_sync_process_running": False,
        "progress": None,
        "sub_agents_syncing": None,
        "evidence_date": date.group(1) if date else None,
        "main_tip_covered": tip.group(1)[:8] if tip else None,
        "workflow_schedule_utc": schedule.group(1) if schedule else None,
        "detail": ("Replication is a GitHub Actions job on push and schedule, "
                   "not a background process in this page"),
        "source": str(path.relative_to(CORE.parents[1])) if path.is_file() else None,
    }


class ProductHandler(SimpleHTTPRequestHandler):
    server_version = "VyomarajProduct/1.0"

    def _json(self, payload: dict, code: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802 - stdlib naming
        route = posixpath.normpath(self.path.split("?", 1)[0])
        if route == "/api/sync/status":
            self._json(sync_facts())
            return
        if route == "/api/realtime":
            if not spec_ok:
                self._json({"error": "realtime module unavailable"}, 503)
                return
            self._json(realtime.realtime_facts())
            return
        super().do_GET()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=3000)
    ap.add_argument("--root", default=None, help="directory to serve (default: repository root)")
    a = ap.parse_args()
    root = Path(a.root).resolve() if a.root else HERE.parents[2]
    handler = partial(ProductHandler, directory=str(root))
    ThreadingHTTPServer(("0.0.0.0", a.port), handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
