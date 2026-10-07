import http.client
import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from ops.jarvis import heartbeat_monitor as monitor


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, limit):
        return self.payload[:limit]


class FakeOpener:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.request = None
        self.timeout = None

    def open(self, request, timeout):
        self.request = request
        self.timeout = timeout
        if self.error:
            raise self.error
        return self.response


class HeartbeatMonitorTests(unittest.TestCase):
    def config(self, directory, urls=None):
        urls = urls or ["", ""]
        path = Path(directory) / "monitor.json"
        path.write_text(json.dumps({
            "schema_version": 1,
            "interval_seconds": 60,
            "timeout_seconds": 3,
            "state_file": str(Path(directory) / "state.json"),
            "peers": [
                {"id": "vyomaraj-bharath", "label": "Vyomaraj / Bharath", "health_url": urls[0]},
                {"id": "jarvis-laxman", "label": "Jarvis / Laxman", "health_url": urls[1]},
            ],
        }), encoding="utf-8")
        return monitor.load_config(path)

    def test_example_config_is_intentionally_unconfigured(self):
        config = monitor.load_config(monitor.DEFAULT_CONFIG)
        state = monitor.run_check(config)
        self.assertEqual(state["summary"], "not_configured")
        self.assertEqual(state["configured_peer_count"], 0)
        self.assertFalse(state["heartbeat_authenticated"])
        self.assertFalse(state["production_peer_health_verified"])
        self.assertFalse(state["production_dr_verified"])
        self.assertFalse(state["failover_enabled"])
        self.assertTrue(all(peer["reachability"] == "not_configured" for peer in state["peers"]))

    def test_partial_peer_configuration_is_not_reported_as_a_complete_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self.config(directory, ["https://peer.example/healthz", ""])
            fake = FakeOpener(FakeResponse(b'{"ready":true}'))
            state = monitor.run_check(config, opener=fake)
            self.assertEqual(state["summary"], "partially_configured")
            self.assertEqual(state["configured_peer_count"], 1)
            self.assertEqual(state["peers"][0]["reachability"], "reachable")
            self.assertEqual(state["peers"][1]["reachability"], "not_configured")
            self.assertFalse(state["heartbeat_authenticated"])
            self.assertFalse(state["production_peer_health_verified"])
            self.assertFalse(state["production_dr_verified"])
            self.assertFalse(state["failover_enabled"])

    def test_url_policy_allows_https_and_loopback_only_http(self):
        self.assertEqual(monitor._safe_url("https://peer.example/healthz"), "https://peer.example/healthz")
        self.assertEqual(monitor._safe_url("http://127.0.0.1:8080/healthz"), "http://127.0.0.1:8080/healthz")
        for value in (
            "http://peer.example/healthz", "https://user:pass@peer.example/healthz",
            "https://peer.example/healthz?token=secret", "https://peer.example/api/health",
        ):
            with self.subTest(value=value), self.assertRaises(monitor.ConfigError):
                monitor._safe_url(value)

    def test_get_response_is_reachability_only_not_authenticated_health(self):
        payload = json.dumps({
            "ready": True,
            "scope": "local_application_metadata_only",
            "peer_id": "some-other-service",
        }).encode()
        fake = FakeOpener(FakeResponse(payload))
        peer = {"id": "vyomaraj-bharath", "label": "Vyomaraj / Bharath", "health_url": "http://127.0.0.1:8000/healthz"}
        result = monitor.probe_endpoint(peer, 3, opener=fake)
        self.assertEqual(result["reachability"], "reachable")
        self.assertTrue(result["readiness_claim"])
        self.assertFalse(result["identity_claim_matches"])
        self.assertFalse(result["heartbeat_authenticated"])
        self.assertFalse(result["production_health_verified"])
        self.assertEqual(fake.request.get_method(), "GET")
        self.assertEqual(fake.timeout, 3)

    def test_http_failure_is_not_healthy(self):
        error = HTTPError("https://peer.example/healthz", 503, "unavailable", http.client.HTTPMessage(), None)
        fake = FakeOpener(error=error)
        peer = {"id": "jarvis-laxman", "label": "Jarvis / Laxman", "health_url": "https://peer.example/healthz"}
        result = monitor.probe_endpoint(peer, 4, opener=fake)
        self.assertEqual(result["reachability"], "unreachable")
        self.assertEqual(result["http_status"], 503)
        self.assertFalse(result["production_health_verified"])

    def test_oversized_response_is_invalid(self):
        fake = FakeOpener(FakeResponse(b"x" * (monitor.MAX_RESPONSE_BYTES + 1)))
        peer = {"id": "jarvis-laxman", "label": "Jarvis / Laxman", "health_url": "https://peer.example/healthz"}
        result = monitor.probe_endpoint(peer, 4, opener=fake)
        self.assertEqual(result["reachability"], "invalid_response")

    def test_state_is_written_atomically_with_private_file_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private" / "state.json"
            monitor.write_state(path, {"schema_version": 1, "summary": "not_configured"})
            self.assertEqual(json.loads(path.read_text())["summary"], "not_configured")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_device_shift_is_explicitly_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.json"
            config_path.write_text(json.dumps({
                "schema_version": 1,
                "interval_seconds": 60,
                "timeout_seconds": 3,
                "state_file": str(Path(directory) / "state.json"),
                "peers": [],
            }), encoding="utf-8")
            with patch("sys.stderr"):
                self.assertEqual(monitor.main(["--config", str(config_path), "shift"]), 4)


if __name__ == "__main__":
    unittest.main()
