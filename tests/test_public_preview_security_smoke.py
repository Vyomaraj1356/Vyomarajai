from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import public_preview_security_smoke as smoke


class FakeResponse:
    def __init__(self, payload: bytes, status: int = 200, headers=None):
        self.payload = payload
        self.status = status
        self.headers = headers or {"Content-Type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int = -1) -> bytes:
        return self.payload


class TestPublicPreviewSecuritySmoke(unittest.TestCase):
    def test_request_retries_cold_start_timeout_with_bounded_backoff(self):
        response = FakeResponse(b'{"status":"ok"}')
        with (
            patch.object(smoke.urllib.request, "urlopen", side_effect=[TimeoutError(), response]) as opener,
            patch.object(smoke.time, "sleep") as sleep,
        ):
            result = smoke.request("/healthz", retries=2, timeout=15)

        self.assertEqual(result[0], 200)
        self.assertEqual(opener.call_count, 2)
        self.assertEqual(opener.call_args_list[0].kwargs["timeout"], 15)
        sleep.assert_called_once_with(1.0)

    def test_request_retries_transient_http_503(self):
        transient = HTTPError(
            "https://preview.example/healthz", 503, "unavailable",
            hdrs=None, fp=io.BytesIO(b"warming"),
        )
        response = FakeResponse(b'{"status":"ok"}')
        with (
            patch.object(smoke.urllib.request, "urlopen", side_effect=[transient, response]) as opener,
            patch.object(smoke.time, "sleep") as sleep,
        ):
            result = smoke.request("/healthz", retries=2)

        self.assertEqual(result[0], 200)
        self.assertEqual(opener.call_count, 2)
        sleep.assert_called_once_with(1.0)

    def test_request_returns_nontransient_http_status_without_retry(self):
        not_found = HTTPError(
            "https://preview.example/missing", 404, "not found",
            hdrs={"X-Frame-Options": "DENY"}, fp=io.BytesIO(b"not found"),
        )
        with (
            patch.object(smoke.urllib.request, "urlopen", side_effect=not_found) as opener,
            patch.object(smoke.time, "sleep") as sleep,
        ):
            result = smoke.request("/missing", retries=7)

        self.assertEqual(result[0], 404)
        self.assertEqual(result[1].get("X-Frame-Options"), "DENY")
        opener.assert_called_once()
        sleep.assert_not_called()

    def test_request_returns_last_transient_http_response_after_bounded_retries(self):
        first = HTTPError("https://preview.example/healthz", 503, "unavailable", hdrs=None, fp=io.BytesIO(b"warm"))
        second = HTTPError("https://preview.example/healthz", 503, "unavailable", hdrs=None, fp=io.BytesIO(b"still warm"))
        with (
            patch.object(smoke.urllib.request, "urlopen", side_effect=[first, second]) as opener,
            patch.object(smoke.time, "sleep") as sleep,
        ):
            result = smoke.request("/healthz", retries=2)

        self.assertEqual(result[0], 503)
        self.assertEqual(opener.call_count, 2)
        sleep.assert_called_once_with(1.0)

    def test_network_retry_exhaustion_does_not_echo_base_url_or_payload(self):
        with (
            patch.object(smoke.urllib.request, "urlopen", side_effect=TimeoutError()) as opener,
            patch.object(smoke.time, "sleep") as sleep,
        ):
            with self.assertRaisesRegex(RuntimeError, "GET /healthz did not respond after 2 attempts: TimeoutError") as raised:
                smoke.request("/healthz", retries=2)

        self.assertNotIn("preview.onrender.com", str(raised.exception))
        opener.assert_called()
        sleep.assert_called_once_with(1.0)

    def test_main_uses_longer_health_retry_and_checks_all_security_routes(self):
        calls = []
        headers = dict(smoke.REQUIRED_HEADERS)
        headers["Content-Security-Policy"] = "; ".join(smoke.REQUIRED_CSP)

        def fake_request(path, method="GET", payload=None, **kwargs):
            calls.append((path, method, payload, kwargs))
            if path == "/healthz":
                return 200, headers, json.dumps({
                    "status": "ok", "service": "vyomaraj-public-preview",
                    "scope": "process_liveness_only",
                }).encode()
            if path == "/api/plan" and method == "GET":
                headers_with_allow = dict(headers, Allow="POST")
                return 405, headers_with_allow, b""
            if path == "/api/catalog" and method == "POST":
                return 405, dict(headers, Allow="GET"), b""
            if path == "/api/plan?unexpected=1":
                return 400, headers, b""
            if path == "/api/plan" and kwargs.get("content_type") == "text/plain":
                return 415, headers, b""
            if kwargs.get("raw") is not None:
                return 400, headers, b""
            if path == "/__not_an_allowlisted_route__":
                return 404, headers, b""
            raise AssertionError(f"unexpected request: {path} {method}")

        with patch("builtins.print"):
            smoke.run_checks(request_fn=fake_request)

        self.assertEqual(len(calls), 7)
        self.assertEqual(calls[0][0:2], ("/healthz", "GET"))
        self.assertEqual(calls[0][3], {"retries": 7, "timeout": 15})
        self.assertEqual(calls[1][0:2], ("/api/plan", "GET"))

    def test_security_header_assertion_rejects_missing_header(self):
        with self.assertRaises(AssertionError):
            smoke.assert_security_headers({}, "fixture")


if __name__ == "__main__":
    unittest.main()
