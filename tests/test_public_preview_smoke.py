from __future__ import annotations

import io
import json
import unittest
from unittest.mock import call, patch
from urllib.error import HTTPError

from scripts import public_preview_smoke as smoke


class FakeResponse:
    def __init__(self, payload: bytes, status: int = 200, content_type: str = "application/json"):
        self.payload = payload
        self.status = status
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int = -1) -> bytes:
        return self.payload


class TestPublicPreviewSmoke(unittest.TestCase):
    def test_request_retries_cold_start_timeout_with_bounded_backoff(self):
        response = FakeResponse(b'{"status":"ok"}')
        with (
            patch.object(smoke.urllib.request, "urlopen", side_effect=[TimeoutError(), response]) as opener,
            patch.object(smoke.time, "sleep") as sleep,
        ):
            result = smoke.request("/healthz", retries=2, timeout=15)

        self.assertEqual(result, (200, "application/json", b'{"status":"ok"}'))
        self.assertEqual(opener.call_count, 2)
        sleep.assert_called_once_with(1.0)
        self.assertEqual(opener.call_args_list[0].kwargs["timeout"], 15)

    def test_request_retries_transient_http_503(self):
        transient = HTTPError(
            "https://preview.example/healthz",
            503,
            "unavailable",
            hdrs=None,
            fp=io.BytesIO(b"warming"),
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

    def test_request_does_not_retry_nontransient_http_404(self):
        not_found = HTTPError(
            "https://preview.example/missing",
            404,
            "not found",
            hdrs=None,
            fp=io.BytesIO(b"not found"),
        )
        with (
            patch.object(smoke.urllib.request, "urlopen", side_effect=not_found) as opener,
            patch.object(smoke.time, "sleep") as sleep,
        ):
            with self.assertRaisesRegex(RuntimeError, "non-retryable HTTP 404"):
                smoke.request("/missing", retries=7)

        opener.assert_called_once()
        sleep.assert_not_called()

    def test_request_reports_bounded_retry_exhaustion_without_url_or_payload(self):
        with (
            patch.object(smoke.urllib.request, "urlopen", side_effect=TimeoutError()) as opener,
            patch.object(smoke.time, "sleep") as sleep,
        ):
            with self.assertRaisesRegex(RuntimeError, "GET /healthz did not respond after 2 attempts: TimeoutError") as raised:
                smoke.request("/healthz", retries=2)

        self.assertNotIn("preview.onrender.com", str(raised.exception))
        self.assertEqual(opener.call_count, 2)
        sleep.assert_called_once_with(1.0)

    def test_main_checks_routes_and_keeps_preview_capability_claims_bounded(self):
        calls = []

        def fake_json_response(path, method="GET", payload=None, **_kwargs):
            calls.append((path, method, payload))
            if path == "/healthz":
                return {
                    "status": "ok",
                    "service": "vyomaraj-public-preview",
                    "scope": "process_liveness_only",
                }
            if path.startswith("/api/catalog?"):
                return {
                    "status": "local_catalog_loaded",
                    "items": [],
                    "overview_source_references": [],
                    "provider": None,
                    "ai_calls_made": False,
                    "publishing_enabled": False,
                    "production_deployed": False,
                }
            mode = payload["mode"]
            return {
                "status": "local_plan_created",
                "experience": "bhakti",
                "mode": mode,
                "role_handoff": ["review"],
                "source_references": [],
                "review_gates": ["owner"],
                "provider": None,
                "ai_calls_made": False,
                "publishing_enabled": False,
                "production_deployed": False,
                "dr_sync_verified": False,
            }

        with (
            patch.object(smoke, "json_response", side_effect=fake_json_response),
            patch("builtins.print"),
        ):
            self.assertEqual(smoke.main(), 0)

        self.assertEqual(len(calls), 6)
        self.assertEqual(calls[0][0:2], ("/healthz", "GET"))
        self.assertEqual([c[2]["mode"] for c in calls if c[0] == "/api/plan"], ["3d", "4d", "5d"])


if __name__ == "__main__":
    unittest.main()
