import unittest

from ops.jarvis.anthropic_adapter import AdapterError, build_payload


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


if __name__ == "__main__":
    unittest.main()
