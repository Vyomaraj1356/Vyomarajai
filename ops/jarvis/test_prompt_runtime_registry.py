#!/usr/bin/env python3
"""Offline tests for the checked-in prompt registry and CLI alias handling."""
import io
import unittest
from pathlib import Path
import tempfile
import json
from unittest.mock import patch

import llm_harness


class PromptRuntimeRegistryTests(unittest.TestCase):
    def test_registry_has_named_user_owned_presets(self):
        registry = llm_harness.load_prompt_registry()
        self.assertGreaterEqual(len(registry), 80)
        for name in ("truthmode", "firstprinciple", "blackswan", "signalvsnoise",
                     "predict", "tldr", "redteam", "education", "socialpublish",
                     "legalreview", "deploygate", "childsafecontent"):
            self.assertIn(name, registry)
            self.assertTrue(registry[name]["prompt"].strip())
            self.assertIn("jarvis", registry[name]["roles"])

    def test_list_presets_needs_no_provider_configuration_or_network(self):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(llm_harness, "_open_request") as opener:
            status = llm_harness.main(["--list-presets"], environment={}, stdout=out, stderr=err)
        self.assertEqual(status, 0, err.getvalue())
        self.assertIn("truthmode", out.getvalue())
        self.assertIn("socialpublish", out.getvalue())
        opener.assert_not_called()

    def test_unknown_preset_fails_without_network(self):
        out, err = io.StringIO(), io.StringIO()
        env = {"JARVIS_LLM_ENDPOINT":"https://llm.example.test/v1/chat/completions",
               "JARVIS_LLM_MODEL":"test-model","JARVIS_LLM_API_KEY":"unit-test-only-secret"}
        with patch.object(llm_harness, "_open_request") as opener:
            status = llm_harness.main(["--role","jarvis","--preset","not-a-real-preset"],
                                      environment=env, stdin=io.StringIO("check this"),
                                      stdout=out, stderr=err)
        self.assertEqual(status, 2)
        self.assertIn("Unknown preset", err.getvalue())
        opener.assert_not_called()

    def test_invalid_registry_fails_closed(self):
        path=None
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"bad.json"
            path.write_text(json.dumps({"schema_version":1,"presets":{"bad":{"prompt":"x","roles":["root"]}}}),encoding="utf-8")
            with self.assertRaises(llm_harness.HarnessError):
                llm_harness.load_prompt_registry(path)


if __name__ == "__main__":
    unittest.main()
