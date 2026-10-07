#!/usr/bin/env python3
"""Serve only the public, static Vyomaraj launch shell for an isolated preview.

This is not an AI API, approval service, private control plane, or production host.
The exact path allowlist prevents the preview listener from exposing the repository.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
ROUTES = {
    "/": (ROOT / "index.html", "text/html; charset=utf-8"),
    "/index.html": (ROOT / "index.html", "text/html; charset=utf-8"),
    "/landing.html": (None, "text/html; charset=utf-8"),
    "/launch.css": (ROOT / "launch.css", "text/css; charset=utf-8"),
    "/launch.js": (ROOT / "launch.js", "text/javascript; charset=utf-8"),
    "/manifest.webmanifest": (ROOT / "manifest.webmanifest", "application/manifest+json; charset=utf-8"),
    "/sw.js": (ROOT / "sw.js", "text/javascript; charset=utf-8"),
    "/offline.html": (ROOT / "offline.html", "text/html; charset=utf-8"),
    "/assets/vyomaraj-icon.svg": (ROOT / "assets/vyomaraj-icon.svg", "image/svg+xml"),
    "/assets/vyomaraj-icon-192.png": (ROOT / "assets/vyomaraj-icon-192.png", "image/png"),
    "/assets/vyomaraj-icon-512.png": (ROOT / "assets/vyomaraj-icon-512.png", "image/png"),
}
MAX_FILE_BYTES = 2 * 1024 * 1024


class PublicLandingHandler(BaseHTTPRequestHandler):
    server_version = "VyomarajPublicPreview/1"
    sys_version = ""

    def _headers(self, content_type: str, size: int, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(size))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
            "connect-src 'self'; manifest-src 'self'; worker-src 'self'; object-src 'none'; "
            "base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        self.end_headers()

    def _serve(self, include_body: bool) -> None:
        path = urlsplit(self.path).path
        if path == "/landing.html":
            self.send_response(302)
            self.send_header("Location", "./")
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        entry = ROUTES.get(path)
        if entry is None or entry[0] is None:
            body = b"Not found\n"
            self._headers("text/plain; charset=utf-8", len(body), 404)
            if include_body:
                self.wfile.write(body)
            return
        file_path, content_type = entry
        try:
            resolved = file_path.resolve(strict=True)
            if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                raise OSError("Not an approved public file")
            size = resolved.stat().st_size
            if size > MAX_FILE_BYTES:
                raise OSError("Approved public file exceeds size limit")
            body = resolved.read_bytes() if include_body else b""
        except OSError:
            body = b"Preview asset unavailable\n"
            self._headers("text/plain; charset=utf-8", len(body), 503)
            if include_body:
                self.wfile.write(body)
            return
        self._headers(content_type, size)
        if include_body:
            self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._serve(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._serve(include_body=False)

    def log_message(self, _format: str, *args) -> None:
        # No query strings, IP addresses, or browser identifiers are logged.
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5310)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    server = ThreadingHTTPServer((args.host, args.port), PublicLandingHandler)
    print(
        f"Vyomaraj public preview on {args.host}:{args.port}; "
        f"serving {len(ROUTES) - 1} allowlisted public assets only; no API or private files",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
