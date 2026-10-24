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

    def test_partial_configuration_is_incomplete(self):
        result = inspect_environment({"JARVIS_LLM_ENDPOINT": "https://api.example.com/v1/chat/completions"})
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("JARVIS_LLM_MODEL is missing.", result["issues"])

    def test_valid_openai_compatible_configuration_is_unverified(self):
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "https://api.example.com/v1/chat/completions",
            "JARVIS_LLM_MODEL": "approved-model",
            "JARVIS_LLM_API_KEY": "test-secret",
        })
        self.assertEqual(result["status"], "configured_unverified")
        self.assertTrue(result["checks"]["endpoint_valid"])
        self.assertFalse(result["request_sent"])

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
            "https://user:pass@api.example.com/v1/chat/completions",
            "https://api.example.com/v1/chat/completions?key=secret",
            "https://api.example.com/v1/chat/completions#fragment",
        ):
            with self.subTest(endpoint=endpoint):
                result = inspect_environment(dict(base, JARVIS_LLM_ENDPOINT=endpoint))
                self.assertEqual(result["status"], "invalid")

    def test_remote_http_is_rejected(self):
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "http://api.example.com/v1/chat/completions",
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
            "JARVIS_LLM_ENDPOINT": "https://api.example.com/v1/chat/completions",
            "JARVIS_LLM_MODEL": "model",
            "JARVIS_LLM_API_KEY": "test-secret",
        })
        self.assertEqual(result["status"], "invalid")

    def test_invalid_limits_are_rejected_without_echoing_values(self):
        secret = "top-secret-do-not-print"
        result = inspect_environment({
            "JARVIS_LLM_PROVIDER": "openai_compatible",
            "JARVIS_LLM_ENDPOINT": "https://api.example.com/v1/chat/completions",
            "JARVIS_LLM_MODEL": "model",
            "JARVIS_LLM_API_KEY": secret,
            "JARVIS_LLM_TIMEOUT_SECONDS": "0",
            "JARVIS_LLM_MAX_TOKENS": "99999",
        })
        rendered = json.dumps(result)
        self.assertEqual(result["status"], "invalid")
        self.assertNotIn(secret, rendered)
        self.assertNotIn("api.example.com", rendered)

    def test_api_key_is_never_echoed_in_json_cli_output(self):
        secret = "top-secret-do-not-print"
        output = StringIO()
        with redirect_stdout(output):
            code = main(["--json"], {
                "JARVIS_LLM_PROVIDER": "openai_compatible",
                "JARVIS_LLM_ENDPOINT": "https://api.example.com/v1/chat/completions",
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
                "JARVIS_LLM_ENDPOINT": "https://api.example.com/v1/chat/completions",
                "JARVIS_LLM_MODEL": "model",
                "JARVIS_LLM_API_KEY": "test-secret",
            })
        self.assertEqual(code, 0)
        self.assertIn('"status": "configured_unverified"', output.getvalue())
        self.assertIn('"request_sent": false', output.getvalue())


if __name__ == "__main__":
    unittest.main()
