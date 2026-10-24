import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from ops.jarvis.provider_preflight import inspect_environment, main


class ProviderPreflightTests(unittest.TestCase):
    def test_empty_environment_is_not_configured_and_sends_no_request(self):
        result = inspect_environment({})
        self.assertEqual(result["status"], "not_configured")
        self.assertFalse(result["request_sent"])

    def test_malformed_allowlist_is_invalid_even_when_other_settings_are_absent(self):
        result = inspect_environment({"JARVIS_LLM_ALLOWED_HOSTS": "*.example.test"})
        self.assertEqual(result["status"], "invalid")
        self.assertFalse(result["request_sent"])
        self.assertIn("JARVIS_LLM_ALLOWED_HOSTS must contain exact DNS hostnames only.", result["issues"])

    def test_partial_configuration_is_incomplete(self):
        result = inspect_environment({"JARVIS_LLM_ENDPOINT": "https://api.openai.com/v1/chat/completions"})
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("JARVIS_LLM_MODEL is missing.", result["issues"])

    def test_valid_openai_compatible_configuration_is_unverified(self):
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "https://api.openai.com/v1/chat/completions",
            "JARVIS_LLM_MODEL": "approved-model",
            "JARVIS_LLM_API_KEY": "test-secret",
        })
        self.assertEqual(result["status"], "configured_unverified")
        self.assertTrue(result["checks"]["endpoint_valid"])
        self.assertFalse(result["request_sent"])

    def test_remote_provider_rejects_nondefault_https_port(self):
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "https://api.openai.com:8443/v1/chat/completions",
            "JARVIS_LLM_MODEL": "approved-model",
            "JARVIS_LLM_API_KEY": "test-secret",
        })
        self.assertEqual(result["status"], "invalid")
        self.assertFalse(result["checks"]["endpoint_valid"])
        self.assertIn("Remote provider endpoints must use the default HTTPS port.", result["issues"])

    def test_custom_compatible_host_requires_exact_explicit_allowlist(self):
        base = {
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "https://llm.example.test/v1/chat/completions",
            "JARVIS_LLM_MODEL": "approved-model",
            "JARVIS_LLM_API_KEY": "test-secret",
        }
        blocked = inspect_environment(base)
        self.assertEqual(blocked["status"], "invalid")
        self.assertFalse(blocked["checks"]["endpoint_valid"])
        self.assertNotIn("llm.example.test", json.dumps(blocked))
        allowed = inspect_environment(dict(base, JARVIS_LLM_ALLOWED_HOSTS="llm.example.test"))
        self.assertEqual(allowed["status"], "configured_unverified")
        self.assertTrue(allowed["checks"]["endpoint_valid"])
        self.assertFalse(allowed["request_sent"])

    def test_custom_host_allowlist_rejects_wildcards_urls_ports_and_ip_literals(self):
        base = {
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "https://llm.example.test/v1/chat/completions",
            "JARVIS_LLM_MODEL": "approved-model",
            "JARVIS_LLM_API_KEY": "test-secret",
        }
        for configured in ("*.example.test", "https://llm.example.test", "llm.example.test:443", "10.0.0.1"):
            with self.subTest(configured=configured):
                result = inspect_environment(dict(base, JARVIS_LLM_ALLOWED_HOSTS=configured))
                self.assertEqual(result["status"], "invalid")
                self.assertFalse(result["checks"]["endpoint_valid"])
                self.assertNotIn("test-secret", json.dumps(result))

    def test_valid_anthropic_configuration_requires_official_exact_endpoint(self):
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "anthropic",
            "JARVIS_LLM_ENDPOINT": "https://api.anthropic.com/v1/messages",
            "JARVIS_LLM_MODEL": "approved-claude-model",
            "JARVIS_LLM_API_KEY": "test-secret",
        })
        self.assertEqual(result["status"], "configured_unverified")
        self.assertTrue(result["checks"]["endpoint_valid"])

    def test_anthropic_rejects_gateway_noncanonical_path_and_invalid_ports(self):
        base = {
            "JARVIS_LLM_PROVIDER": "anthropic",
            "JARVIS_LLM_MODEL": "approved-claude-model",
            "JARVIS_LLM_API_KEY": "test-secret",
        }
        for endpoint in (
            "https://gateway.example/v1/messages",
            "https://api.anthropic.com/proxy/v1/messages",
            "http://api.anthropic.com/v1/messages",
            "https://api.anthropic.com:444/v1/messages",
            "https://api.anthropic.com:invalid/v1/messages",
        ):
            with self.subTest(endpoint=endpoint):
                result = inspect_environment(dict(base, JARVIS_LLM_ENDPOINT=endpoint))
                self.assertEqual(result["status"], "invalid")
                self.assertFalse(result["checks"]["endpoint_valid"])

    def test_rejects_endpoint_credentials_query_and_fragment(self):
        base = {
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_MODEL": "model",
            "JARVIS_LLM_API_KEY": "test-secret",
        }
        for endpoint in (
            "https://user:pass@api.openai.com/v1/chat/completions",
            "https://api.openai.com/v1/chat/completions?key=secret",
            "https://api.openai.com/v1/chat/completions#fragment",
        ):
            with self.subTest(endpoint=endpoint):
                result = inspect_environment(dict(base, JARVIS_LLM_ENDPOINT=endpoint))
                self.assertEqual(result["status"], "invalid")

    def test_rejects_non_public_and_noncanonical_ip_literal_hosts(self):
        base = {
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_MODEL": "model",
            "JARVIS_LLM_API_KEY": "test-secret",
        }
        for endpoint in (
            "https://169.254.169.254/v1/chat/completions",
            "https://10.0.0.8/v1/chat/completions",
            "https://192.168.1.2/v1/chat/completions",
            "https://[fd00::1]/v1/chat/completions",
            "https://127.1/v1/chat/completions",
            "https://2130706433/v1/chat/completions",
            "https://0x7f000001/v1/chat/completions",
        ):
            with self.subTest(endpoint=endpoint):
                result = inspect_environment(dict(base, JARVIS_LLM_ENDPOINT=endpoint))
                self.assertEqual(result["status"], "invalid")
                self.assertFalse(result["checks"]["endpoint_valid"])
                self.assertNotIn(endpoint, json.dumps(result))
                self.assertNotIn(base["JARVIS_LLM_API_KEY"], json.dumps(result))

    def test_remote_http_is_rejected(self):
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "http://api.openai.com/v1/chat/completions",
            "JARVIS_LLM_MODEL": "model",
            "JARVIS_LLM_API_KEY": "test-secret",
        })
        self.assertEqual(result["status"], "invalid")

    def test_loopback_http_can_be_configured_without_remote_key(self):
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "http://127.0.0.1:8000/v1/chat/completions",
            "JARVIS_LLM_MODEL": "local-model",
        })
        self.assertEqual(result["status"], "configured_unverified")

    def test_unsupported_provider_is_invalid(self):
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "unknown",
            "JARVIS_LLM_ENDPOINT": "https://api.openai.com/v1/chat/completions",
            "JARVIS_LLM_MODEL": "model",
            "JARVIS_LLM_API_KEY": "test-secret",
        })
        self.assertEqual(result["status"], "invalid")

    def test_invalid_limits_are_rejected_without_echoing_values(self):
        secret = "top-secret-do-not-print"
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "https://api.openai.com/v1/chat/completions",
            "JARVIS_LLM_MODEL": "model",
            "JARVIS_LLM_API_KEY": secret,
            "JARVIS_LLM_TIMEOUT_SECONDS": "0",
            "JARVIS_LLM_MAX_TOKENS": "99999",
        })
        rendered = json.dumps(result)
        self.assertEqual(result["status"], "invalid")
        self.assertNotIn(secret, rendered)
        self.assertNotIn("api.openai.com", rendered)

    def test_api_key_is_never_echoed_in_json_cli_output(self):
        secret = "top-secret-do-not-print"
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--json"], {
                "JARVIS_LLM_PROVIDER": "openai_compatible",
                "JARVIS_LLM_ENDPOINT": "https://api.openai.com/v1/chat/completions",
                "JARVIS_LLM_MODEL": "model",
                "JARVIS_LLM_API_KEY": secret,
            })
        self.assertEqual(code, 0)
        self.assertNotIn(secret, output.getvalue())
        parsed = json.loads(output.getvalue())
        self.assertEqual(parsed["status"], "configured_unverified")
        self.assertFalse(parsed["request_sent"])

    def test_require_configured_fails_closed_for_incomplete_config(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--json", "--require-configured"], {})
        self.assertEqual(code, 3)

    def test_require_configured_passes_static_validation_without_claiming_live_connectivity(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--json", "--require-configured"], {
                "JARVIS_LLM_PROVIDER": "openai_compatible",
                "JARVIS_LLM_ENDPOINT": "https://api.openai.com/v1/chat/completions",
                "JARVIS_LLM_MODEL": "model",
                "JARVIS_LLM_API_KEY": "test-secret",
            })
        self.assertEqual(code, 0)
        self.assertIn('"status": "configured_unverified"', output.getvalue())
        self.assertIn('"request_sent": false', output.getvalue())


if __name__ == "__main__":
    unittest.main()
