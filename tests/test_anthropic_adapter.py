import json
import unittest
from urllib.error import URLError

from ops.jarvis.anthropic_adapter import AdapterError, API_URL, build_payload, request_messages


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.body[:limit]


class FakeOpener:
    def __init__(self, body=None, error=None):
        self.body = body
        self.error = error
        self.request = None
        self.timeout = None

    def open(self, request, timeout):
        self.request = request
        self.timeout = timeout
        if self.error:
            raise self.error
        return FakeResponse(self.body)


class AnthropicAdapterTests(unittest.TestCase):
    def test_scriptwriter_preset_is_draft_only_and_no_tools(self):
        payload = build_payload("Create a 30-second educational script.", "test-model")
        self.assertEqual(payload["messages"][0]["role"], "user")
        self.assertIn("draft-only", payload["system"])
        self.assertNotIn("tools", payload)
        self.assertEqual(payload["max_tokens"], 1200)

    def test_general_preset(self):
        payload = build_payload("Summarize this.", "test-model", "general")
        self.assertIn("untrusted data", payload["system"])

    def test_rejects_empty_prompt(self):
        with self.assertRaises(AdapterError):
            build_payload("  ", "test-model")

    def test_rejects_oversized_prompt(self):
        with self.assertRaises(AdapterError):
            build_payload("x" * 16001, "test-model")

    def test_rejects_unknown_task(self):
        with self.assertRaises(AdapterError):
            build_payload("hello", "test-model", "root")

    def test_rejects_missing_model(self):
        with self.assertRaises(AdapterError):
            build_payload("hello", "")

    def test_rejects_non_string_model(self):
        with self.assertRaises(AdapterError):
            build_payload("hello", None)

    def test_mocked_success_and_auth_header(self):
        body = json.dumps({"content": [{"type": "text", "text": "Draft ready"}]}).encode()
        opener = FakeOpener(body=body)
        output = request_messages("write a script", api_key="test-secret",
                                  model="test-model", opener=opener, timeout=5)
        self.assertEqual(output, "Draft ready")
        self.assertEqual(opener.request.full_url, API_URL)
        self.assertEqual(opener.request.get_header("X-api-key"), "test-secret")
        self.assertEqual(opener.timeout, 5)

    def test_provider_error_body_is_not_exposed(self):
        body = json.dumps({"type": "error", "content": [{"type": "text", "text": "secret detail"}]}).encode()
        with self.assertRaises(AdapterError) as caught:
            request_messages("write a script", api_key="test-secret",
                             model="test-model", opener=FakeOpener(body=body))
        self.assertNotIn("secret detail", str(caught.exception))

    def test_network_failure_is_sanitized(self):
        with self.assertRaises(AdapterError) as caught:
            request_messages("write a script", api_key="test-secret",
                             model="test-model", opener=FakeOpener(error=URLError("private detail")))
        self.assertNotIn("private detail", str(caught.exception))

    def test_rejects_invalid_timeout_before_request(self):
        opener = FakeOpener(body=b"{}")
        with self.assertRaises(AdapterError):
            request_messages("hello", api_key="test-secret", model="test-model",
                             timeout=0, opener=opener)
        self.assertIsNone(opener.request)


if __name__ == "__main__":
    unittest.main()
