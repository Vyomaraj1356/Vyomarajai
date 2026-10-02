#!/usr/bin/env python3
"""Allowlisted static preview server for the Experience Studio.

Unlike a repository-root SimpleHTTPServer, this serves only the public studio,
its safe registry/config metadata, and the already-public index page. Jarvis env,
device, controller, and unrelated repository files are not addressable.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ALLOWLIST = {
    "/": (REPO_ROOT / "experience-studio.html", "text/html; charset=utf-8"),
    "/experience-studio.html": (REPO_ROOT / "experience-studio.html", "text/html; charset=utf-8"),
    "/index.html": (REPO_ROOT / "index.html", "text/html; charset=utf-8"),
    "/ops/vyomaraj-core/experience/studio.css": (HERE / "studio.css", "text/css; charset=utf-8"),
    "/ops/vyomaraj-core/experience/studio.js": (HERE / "studio.js", "text/javascript; charset=utf-8"),
    "/ops/vyomaraj-core/experience/EXPERIENCE_ORCHESTRATOR.json": (HERE / "EXPERIENCE_ORCHESTRATOR.json", "application/json; charset=utf-8"),
    "/ops/vyomaraj-core/experience/CONTENT_CATALOG.json": (HERE / "CONTENT_CATALOG.json", "application/json; charset=utf-8"),
    "/ops/vyomaraj-core/handover/AGENT_CONTENT_REGISTRY_V16_7_24.json": (
        REPO_ROOT / "ops/vyomaraj-core/handover/AGENT_CONTENT_REGISTRY_V16_7_24.json",
        "application/json; charset=utf-8",
    ),
    "/ops/vyomaraj-core/handover/CONTENT_SAFETY_POLICY_V16_7_24.json": (
        REPO_ROOT / "ops/vyomaraj-core/handover/CONTENT_SAFETY_POLICY_V16_7_24.json",
        "application/json; charset=utf-8",
    ),
}


class SafePreviewHandler(BaseHTTPRequestHandler):
    server_version = "ExperienceStudioPreview/1.0"
    sys_version = ""

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        self._serve(head_only=False)

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib handler API
        self._serve(head_only=True)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        self._send_error(405, "Method not allowed.")

    def _serve(self, *, head_only: bool) -> None:
        path = urlsplit(self.path).path
        item = ALLOWLIST.get(path)
        if item is None:
            self._send_error(404, "Not found.")
            return
        file_path, content_type = item
        try:
            payload = file_path.read_bytes()
        except OSError:
            self._send_error(404, "Not found.")
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        if path == "/index.html":
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'self'"
        else:
            csp = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'"
        self.send_header("Content-Security-Policy", csp)
        self.end_headers()
        if not head_only:
            self.wfile.write(payload)

    def _send_error(self, status: int, message: str) -> None:
        body = (message + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        # Log only method, status, and allowlisted path; never request bodies.
        path = urlsplit(self.path).path
        print(f"{self.command} {path} - {args[1] if len(args) > 1 else ''}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Experience Studio from a safe file allowlist")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=4174)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), SafePreviewHandler)
    print(f"Experience Studio preview listening on {args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
