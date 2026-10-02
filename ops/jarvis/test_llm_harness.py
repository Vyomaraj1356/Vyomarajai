#!/usr/bin/env python3
"""Offline tests for the no-tools Jarvis/Vyomaraj LLM harness."""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import patch

import llm_harness


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, limit: int = -1) -> bytes:
        return self.body if limit < 0 else self.body[:limit]


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "JARVIS_LLM_ENDPOINT": "https://llm.example.test/v1/chat/completions",
            "JARVIS_LLM_MODEL": "test-model",
            "JARVIS_LLM_API_KEY": "unit-test-only-secret",
        }

    def test_process_environment_overrides_local_file(self):
        with tempfile.TemporaryDirectory() as temp:
            env_file = Path(temp) / "local.env"
            env_file.write_text(
                "JARVIS_LLM_ENDPOINT=https://file.example.test/v1/chat/completions\n"
                "JARVIS_LLM_MODEL=file-model\n",
                encoding="utf-8",
            )
            environment = {
                "JARVIS_LLM_ENV_FILE": str(env_file),
                "JARVIS_LLM_MODEL": "process-model",
            }
            loaded = llm_harness.read_environment(environment)
            self.assertEqual(loaded["JARVIS_LLM_MODEL"], "process-model")
            self.assertEqual(
                loaded["JARVIS_LLM_ENDPOINT"],
                "https://file.example.test/v1/chat/completions",
            )

    def test_rejects_remote_plain_http_and_url_credentials(self):
        env = dict(self.env, JARVIS_LLM_ENDPOINT="http://provider.example/v1/chat/completions")
        with self.assertRaises(llm_harness.HarnessError):
            llm_harness.load_config(env)
        env = dict(self.env, JARVIS_LLM_ENDPOINT="https://user:pass@llm.example/v1/chat/completions")
        with self.assertRaises(llm_harness.HarnessError):
            llm_harness.load_config(env)

    def test_local_loopback_can_run_without_api_key(self):
        env = {
            "JARVIS_LLM_ENDPOINT": "http://127.0.0.1:11434/v1/chat/completions",
            "JARVIS_LLM_MODEL": "local-model",
        }
        config = llm_harness.load_config(env)
        self.assertEqual(config.api_key, "")

    def test_redirect_handler_refuses_forwarding(self):
        handler = llm_harness._NoRedirect()
        redirected = handler.redirect_request(None, None, 302, "redirect", {}, "https://other.example/")
        self.assertIsNone(redirected)

    def test_success_posts_only_messages_without_tools(self):
        provider_body = json.dumps(
            {"choices": [{"message": {"content": "Verified answer."}}]}
        ).encode()
        with patch.object(llm_harness, "_open_request", return_value=FakeResponse(provider_body)) as opener:
            answer = llm_harness.complete("hello", "jarvis", llm_harness.load_config(self.env))
        self.assertEqual(answer, "Verified answer.")
        request = opener.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "test-model")
        self.assertEqual([item["role"] for item in payload["messages"]], ["system", "user"])
        self.assertNotIn("tools", payload)
        self.assertEqual(request.get_header("Authorization"), "Bearer unit-test-only-secret")

    def test_http_error_body_and_key_are_not_returned(self):
        secret = self.env["JARVIS_LLM_API_KEY"]
        error = HTTPError(
            self.env["JARVIS_LLM_ENDPOINT"],
            401,
            "unauthorized",
            hdrs=None,
            fp=io.BytesIO(secret.encode()),
        )
        with patch.object(llm_harness, "_open_request", side_effect=error):
            with self.assertRaises(llm_harness.HarnessError) as raised:
                llm_harness.complete("hello", "vyomaraj", llm_harness.load_config(self.env))
        self.assertNotIn(secret, str(raised.exception))
        self.assertNotIn(secret, repr(raised.exception))
        self.assertIn("HTTP 401", str(raised.exception))

    def test_missing_configuration_fails_without_network_call(self):
        out = io.StringIO()
        err = io.StringIO()
        with patch.object(llm_harness, "_open_request") as opener:
            status = llm_harness.main(
                ["--role", "jarvis"],
                environment={},
                stdin=io.StringIO("private prompt"),
                stdout=out,
                stderr=err,
            )
        self.assertEqual(status, 2)
        self.assertIn("JARVIS_LLM_ENDPOINT", err.getvalue())
        self.assertNotIn("private prompt", err.getvalue())
        opener.assert_not_called()

    def test_remote_endpoint_requires_a_key(self):
        env = dict(self.env)
        env.pop("JARVIS_LLM_API_KEY")
        with self.assertRaises(llm_harness.HarnessError):
            llm_harness.load_config(env)


if __name__ == "__main__":
    unittest.main()
