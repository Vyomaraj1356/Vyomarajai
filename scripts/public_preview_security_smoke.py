#!/usr/bin/env python3
"""Credential-free public-preview security smoke checks with bounded cold-start retries."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://vyomaraj-public-preview.onrender.com"
TRANSIENT_HTTP_STATUSES = frozenset({408, 425, 429, 500, 502, 503, 504})
REQUIRED_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Resource-Policy": "same-origin",
    "X-Robots-Tag": "noindex, nofollow",
    "Cache-Control": "no-store",
}
REQUIRED_CSP = (
    "default-src 'self'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'none'",
    "frame-ancestors 'none'",
)


def request(
    path: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    *,
    raw: bytes | None = None,
    content_type: str | None = None,
    retries: int = 3,
    timeout: int = 12,
    backoff_initial: float = 1.0,
    backoff_max: float = 8.0,
) -> tuple[int, Any, bytes]:
    """Return status/headers/body; retry only bounded transient failures."""
    if retries < 1:
        raise ValueError("retries must be at least one")
    if timeout < 1:
        raise ValueError("timeout must be positive")
    if not path.startswith("/") or path.startswith("//"):
        raise ValueError("path must be a local absolute route")

    base = os.environ.get("BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    data = raw
    headers = {"User-Agent": "Vyomaraj-Public-Preview-Security-Gate/1.1"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if content_type is not None:
        headers["Content-Type"] = content_type

    last_error: BaseException | None = None
    last_response: tuple[int, Any, bytes] | None = None
    for attempt in range(retries):
        req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status, response.headers, response.read(300_000)
        except urllib.error.HTTPError as exc:
            try:
                response = (exc.code, exc.headers, exc.read(300_000))
            finally:
                exc.close()
            if response[0] not in TRANSIENT_HTTP_STATUSES:
                return response
            last_response = response
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc

        if attempt < retries - 1:
            time.sleep(min(backoff_initial * (2**attempt), backoff_max))

    if last_response is not None:
        return last_response
    error_name = type(last_error).__name__ if last_error is not None else "UnknownError"
    raise RuntimeError(
        f"{method} {path} did not respond after {retries} attempts: {error_name}"
    ) from None


def assert_security_headers(headers: Any, label: str) -> None:
    for name, expected in REQUIRED_HEADERS.items():
        actual = headers.get(name)
        assert actual == expected, f"{label}: {name} expected {expected!r}, got {actual!r}"
    csp = headers.get("Content-Security-Policy", "")
    for directive in REQUIRED_CSP:
        assert directive in csp, f"{label}: CSP missing {directive!r}"
    print(f"PASS: {label}: security headers and restrictive CSP")


def run_checks(request_fn=request) -> None:
    status, headers, body = request_fn("/healthz", retries=7, timeout=15)
    assert status == 200, f"/healthz expected 200, got {status}"
    assert_security_headers(headers, "/healthz")
    try:
        health = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise AssertionError("/healthz must return valid JSON") from None
    assert health == {
        "status": "ok",
        "service": "vyomaraj-public-preview",
        "scope": "process_liveness_only",
    }, "health response must remain explicitly liveness-only"

    status, headers, _ = request_fn("/api/plan")
    assert status == 405, f"GET /api/plan expected 405, got {status}"
    assert headers.get("Allow") == "POST", "GET /api/plan must advertise POST only"
    assert_security_headers(headers, "GET /api/plan")

    status, headers, _ = request_fn(
        "/api/catalog", method="POST", payload={"experience": "bhakti"}
    )
    assert status == 405, f"POST /api/catalog expected 405, got {status}"
    assert headers.get("Allow") == "GET", "catalog must remain read-only"
    assert_security_headers(headers, "POST /api/catalog")

    status, headers, _ = request_fn(
        "/api/plan?unexpected=1", method="POST", payload={"experience": "bhakti"}
    )
    assert status == 400, f"planner query string expected 400, got {status}"
    assert_security_headers(headers, "POST /api/plan with query string")

    status, headers, _ = request_fn(
        "/api/plan", method="POST", payload={"experience": "bhakti"},
        content_type="text/plain",
    )
    assert status == 415, f"unsupported content type expected 415, got {status}"
    assert_security_headers(headers, "POST /api/plan with unsupported content type")

    status, headers, _ = request_fn(
        "/api/plan", method="POST",
        raw=b'{"experience":"bhakti","experience":"liquor-bar"}',
        content_type="application/json",
    )
    assert status == 400, f"duplicate JSON keys expected 400, got {status}"
    assert_security_headers(headers, "POST /api/plan with duplicate JSON keys")

    status, headers, _ = request_fn("/__not_an_allowlisted_route__")
    assert status == 404, f"unknown route expected 404, got {status}"
    assert_security_headers(headers, "unknown route")


def main() -> int:
    run_checks()
    print(
        "PASS: public preview security gate; no credentials, external AI calls, "
        "persistent writes, publishing, or traffic changes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
