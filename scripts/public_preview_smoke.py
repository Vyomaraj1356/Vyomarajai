#!/usr/bin/env python3
"""Credential-free smoke checks for the public Vyomaraj preview."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://vyomaraj-public-preview.onrender.com"
TRANSIENT_HTTP_STATUSES = frozenset({408, 425, 429, 500, 502, 503, 504})


def request(
    path: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    *,
    retries: int = 3,
    timeout: int = 12,
    backoff_initial: float = 1.0,
    backoff_max: float = 8.0,
) -> tuple[int, str, bytes]:
    """Request a public-preview route, retrying transient failures only.

    The first /healthz call can wake a free instance after spin-down, so the
    caller may request a longer retry window for that one liveness probe.
    """
    if retries < 1:
        raise ValueError("retries must be at least one")
    if timeout < 1:
        raise ValueError("timeout must be positive")

    base = os.environ.get("BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"User-Agent": "Vyomaraj-Public-Preview-Smoke/1.1"}
    if data is not None:
        headers["Content-Type"] = "application/json"

    last_error: BaseException | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                base + path, data=data, headers=headers, method=method
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read(300_000)
                return (
                    response.status,
                    response.headers.get("Content-Type", ""),
                    raw,
                )
        except urllib.error.HTTPError as exc:
            if exc.code not in TRANSIENT_HTTP_STATUSES:
                raise RuntimeError(
                    f"{method} {path} failed with non-retryable HTTP {exc.code}"
                ) from None
            last_error = exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc

        if attempt < retries - 1:
            delay = min(backoff_initial * (2**attempt), backoff_max)
            time.sleep(delay)

    raise RuntimeError(
        f"{method} {path} did not respond after {retries} attempts: "
        f"{type(last_error).__name__ if last_error is not None else 'UnknownError'}"
    ) from None


def json_response(
    path: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    *,
    retries: int = 3,
    timeout: int = 12,
) -> dict[str, Any]:
    status, content_type, raw = request(
        path, method, payload, retries=retries, timeout=timeout
    )
    if status != 200:
        raise AssertionError(f"{method} {path}: expected HTTP 200, got {status}")
    if "json" not in content_type.lower():
        raise AssertionError(f"{method} {path}: expected JSON content type")
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise AssertionError(f"{method} {path}: invalid JSON response") from None
    if not isinstance(decoded, dict):
        raise AssertionError(f"{method} {path}: expected a JSON object")
    return decoded


def main() -> int:
    # A cold Render Free instance may take around a minute to wake. Allow a
    # bounded longer window for this first liveness request only.
    health = json_response("/healthz", retries=7, timeout=15)
    assert health.get("status") == "ok", "health endpoint status mismatch"
    assert health.get("service") == "vyomaraj-public-preview", "unexpected service identity"
    assert health.get("scope") == "process_liveness_only", "health scope must not overclaim readiness"
    print("PASS: /healthz — process liveness only")

    for experience in ("bhakti", "liquor-bar"):
        path = "/api/catalog?" + urllib.parse.urlencode({"experience": experience})
        catalog = json_response(path)
        assert catalog.get("status") == "local_catalog_loaded", f"{experience}: catalog did not load"
        assert isinstance(catalog.get("items"), list), f"{experience}: catalog items missing or invalid"
        assert isinstance(catalog.get("overview_source_references"), list), f"{experience}: source references missing or invalid"
        assert catalog.get("provider") is None, f"{experience}: unexpected provider claim"
        assert catalog.get("ai_calls_made") is False, f"{experience}: unexpected AI-call claim"
        assert catalog.get("publishing_enabled") is False, f"{experience}: publishing must remain disabled"
        assert catalog.get("production_deployed") is False, f"{experience}: production must not be claimed"
        print(
            f"PASS: /api/catalog?experience={experience} — "
            f"{len(catalog['items'])} local items; no provider or publishing claim"
        )

    for mode in ("3d", "4d", "5d"):
        plan = json_response(
            "/api/plan",
            method="POST",
            payload={
                "experience": "bhakti",
                "topic_id": "overview",
                "mode": mode,
                "diet": "all",
            },
        )
        assert plan.get("status") == "local_plan_created", f"{mode}: local planner did not create a plan"
        assert plan.get("experience") == "bhakti", f"{mode}: planner experience mismatch"
        assert plan.get("mode") == mode, f"{mode}: planner mode mismatch"
        assert isinstance(plan.get("role_handoff"), list) and len(plan["role_handoff"]) >= 1, f"{mode}: planner role handoff missing"
        assert isinstance(plan.get("source_references"), list), f"{mode}: planner source references missing"
        assert isinstance(plan.get("review_gates"), list) and plan["review_gates"], f"{mode}: planner review gates missing"
        assert plan.get("provider") is None, f"{mode}: local planner must not claim a live provider"
        assert plan.get("ai_calls_made") is False, f"{mode}: local planner must not claim AI calls"
        assert plan.get("publishing_enabled") is False, f"{mode}: publishing must remain disabled"
        assert plan.get("production_deployed") is False, f"{mode}: production must not be claimed"
        assert plan.get("dr_sync_verified") is False, f"{mode}: local planner must not claim DR verification"
        print(
            f"PASS: POST /api/plan mode={mode} — deterministic local plan; "
            "no live AI/provider or production claim"
        )

    print(
        "PASS: all public preview smoke checks completed; "
        "no credentials used and no persistent writes performed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
