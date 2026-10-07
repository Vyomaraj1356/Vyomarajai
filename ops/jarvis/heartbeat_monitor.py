#!/usr/bin/env python3
"""Fail-closed, read-only reachability monitor for configured Vyomaraj/Jarvis endpoints.

A successful HTTP GET proves only that an endpoint answered. It does not authenticate a
peer, prove a persistent heartbeat, verify a database, or establish production DR health.
No state transfer, failover, publishing, device access, or remote mutation is performed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import json
import os
import signal
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "heartbeat-config.example.json"
MAX_CONFIG_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 16 * 1024
USER_AGENT = "Vyomaraj-Jarvis-Reachability-Monitor/1"


class ConfigError(ValueError):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, _request, _fp, _code, _message, _headers, _new_url):
        return None


def _safe_url(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("health_url must be an HTTPS URL or local loopback HTTP URL")
    value = value.strip()
    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").lower()
        parsed.port
    except ValueError:
        raise ConfigError("health_url is not a valid URL") from None
    if parsed.scheme not in ("https", "http") or not parsed.netloc or not host:
        raise ConfigError("health_url must be an HTTPS URL or local loopback HTTP URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigError("health_url must not contain credentials, query parameters, or fragments")
    if parsed.path.rstrip("/") != "/healthz":
        raise ConfigError("health_url must point to an explicit /healthz endpoint")
    if parsed.scheme == "http":
        loopback_names = {"localhost"}
        is_loopback = host in loopback_names
        try:
            is_loopback = is_loopback or ipaddress.ip_address(host).is_loopback
        except ValueError:
            pass
        if not is_loopback:
            raise ConfigError("unencrypted HTTP is allowed only for a loopback health endpoint")
    return value


def load_config(path: Path) -> dict[str, Any]:
    try:
        raw = path.expanduser().read_bytes()
        if len(raw) > MAX_CONFIG_BYTES:
            raise ConfigError("configuration exceeds the size limit")
        data = json.loads(raw.decode("utf-8"))
    except ConfigError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ConfigError("could not read valid UTF-8 JSON configuration") from None
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ConfigError("configuration schema_version must be 1")
    interval = data.get("interval_seconds", 60)
    timeout = data.get("timeout_seconds", 5)
    if not isinstance(interval, int) or isinstance(interval, bool) or not 15 <= interval <= 3600:
        raise ConfigError("interval_seconds must be between 15 and 3600")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 15:
        raise ConfigError("timeout_seconds must be between 1 and 15")
    peers = data.get("peers")
    if not isinstance(peers, list) or len(peers) > 20:
        raise ConfigError("peers must be a list with no more than 20 entries")
    seen: set[str] = set()
    checked_peers = []
    for peer in peers:
        if not isinstance(peer, dict) or set(peer) != {"id", "label", "health_url"}:
            raise ConfigError("each peer must contain exactly id, label, and health_url")
        peer_id, label, url = peer["id"], peer["label"], peer["health_url"]
        if (not isinstance(peer_id, str) or not peer_id or len(peer_id) > 80
                or not isinstance(label, str) or not label or len(label) > 120):
            raise ConfigError("peer id and label must be non-empty bounded strings")
        if peer_id in seen:
            raise ConfigError("peer IDs must be unique")
        seen.add(peer_id)
        if url is not None and url != "":
            url = _safe_url(url)
        else:
            url = ""
        checked_peers.append({"id": peer_id, "label": label, "health_url": url})
    state_file = data.get("state_file", "~/.local/state/vyomaraj/jarvis-heartbeats.json")
    if not isinstance(state_file, str) or not state_file or len(state_file) > 1024:
        raise ConfigError("state_file must be a non-empty path")
    return {
        "schema_version": 1,
        "interval_seconds": interval,
        "timeout_seconds": timeout,
        "state_file": Path(state_file).expanduser(),
        "peers": checked_peers,
    }


def probe_endpoint(peer: dict[str, str], timeout: int, *, opener=None) -> dict[str, Any]:
    """GET a configured /healthz URL and report reachability without trusting its claims."""
    checked_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    url = peer["health_url"]
    base = {
        "peer_id": peer["id"],
        "label": peer["label"],
        "checked_at_utc": checked_at,
        "endpoint_configured": bool(url),
        "reachability": "not_configured" if not url else "unreachable",
        "http_status": None,
        "duration_ms": None,
        "readiness_claim": None,
        "reported_scope": None,
        "identity_claim_matches": None,
        "heartbeat_authenticated": False,
        "production_health_verified": False,
    }
    if not url:
        return base
    request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}, method="GET")
    start = time.monotonic()
    try:
        client = opener or build_opener(_NoRedirect())
        with client.open(request, timeout=timeout) as response:
            status = int(response.status)
            payload = response.read(MAX_RESPONSE_BYTES + 1)
        base["http_status"] = status
        base["duration_ms"] = round((time.monotonic() - start) * 1000, 1)
        if len(payload) > MAX_RESPONSE_BYTES:
            base["reachability"] = "invalid_response"
            return base
        if not 200 <= status < 300:
            base["reachability"] = "unreachable"
            return base
        base["reachability"] = "reachable"
        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return base
        if isinstance(decoded, dict):
            if isinstance(decoded.get("ready"), bool):
                base["readiness_claim"] = decoded["ready"]
            if isinstance(decoded.get("scope"), str):
                base["reported_scope"] = decoded["scope"][:120]
            if isinstance(decoded.get("peer_id"), str):
                base["identity_claim_matches"] = decoded["peer_id"] == peer["id"]
        return base
    except HTTPError as exc:
        base["http_status"] = int(exc.code)
        base["duration_ms"] = round((time.monotonic() - start) * 1000, 1)
        base["reachability"] = "unreachable"
        return base
    except (URLError, TimeoutError, OSError, ValueError):
        base["duration_ms"] = round((time.monotonic() - start) * 1000, 1)
        return base


def run_check(config: dict[str, Any], *, opener=None) -> dict[str, Any]:
    peers = [probe_endpoint(peer, config["timeout_seconds"], opener=opener)
             for peer in config["peers"]]
    configured = [peer for peer in peers if peer["endpoint_configured"]]
    if not configured:
        summary = "not_configured"
    elif all(peer["reachability"] == "reachable" for peer in configured):
        summary = "reachable_unverified"
    else:
        summary = "unreachable"
    return {
        "schema_version": 1,
        "monitor_mode": "read_only_reachability_probe",
        "summary": summary,
        "checked_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "configured_peer_count": len(configured),
        "heartbeat_authenticated": False,
        "production_peer_health_verified": False,
        "production_dr_verified": False,
        "failover_enabled": False,
        "peers": peers,
    }


def write_state(path: Path, state: dict[str, Any]) -> None:
    target = path.expanduser()
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=".jarvis-heartbeat-", dir=target.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        os.chmod(target, 0o600)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def read_state(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.expanduser().read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {
            "schema_version": 1,
            "monitor_mode": "read_only_reachability_probe",
            "summary": "not_checked",
            "heartbeat_authenticated": False,
            "production_peer_health_verified": False,
            "production_dr_verified": False,
            "failover_enabled": False,
            "peers": [],
        }
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ConfigError("saved monitor state is unreadable") from None
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ConfigError("saved monitor state has an unsupported schema")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="run one read-only health endpoint probe")
    subparsers.add_parser("run", help="repeat read-only probes at the configured interval")
    subparsers.add_parser("status", help="show the last recorded probe without network access")
    subparsers.add_parser("shift", help="refuse unverified device shift or DR failover")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "status":
            state = read_state(config["state_file"])
            print(json.dumps(state, ensure_ascii=False, indent=2))
            return 0
        if args.command == "shift":
            print("BLOCKED: device shift/failover requires authenticated peers, shared durable state, quorum, fencing and owner authorization.", file=sys.stderr)
            return 4
        if args.command == "check":
            state = run_check(config)
            write_state(config["state_file"], state)
            print(json.dumps(state, ensure_ascii=False, indent=2))
            if state["summary"] == "not_configured":
                return 2
            return 0 if state["summary"] == "reachable_unverified" else 1
        if args.command == "run":
            interval = config["interval_seconds"]
            stop = False
            def request_stop(_signum, _frame):
                nonlocal stop
                stop = True
            signal.signal(signal.SIGTERM, request_stop)
            signal.signal(signal.SIGINT, request_stop)
            while not stop:
                state = run_check(config)
                write_state(config["state_file"], state)
                print(json.dumps(state, ensure_ascii=False, separators=(",", ":")), flush=True)
                deadline = time.monotonic() + interval
                while not stop and time.monotonic() < deadline:
                    time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))
            return 0
    except ConfigError as exc:
        print(f"Jarvis reachability monitor: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
