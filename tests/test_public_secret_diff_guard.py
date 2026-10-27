"""Offline tests for the redacted public-repository secret diff guard."""
from __future__ import annotations

import unittest

from scripts.public_secret_diff_guard import (
    compare_commits,
    scan_unified_diff,
    sensitive_path,
)


class PublicSecretDiffGuardTests(unittest.TestCase):
    def test_clean_diff_passes(self):
        diff = (
            "diff --git a/docs/example.md b/docs/example.md\n"
            "--- a/docs/example.md\n"
            "+++ b/docs/example.md\n"
            "@@ -1,0 +1,2 @@\n"
            "+Example configuration uses placeholder values.\n"
            "+No credentials are included.\n"
        )
        self.assertEqual(scan_unified_diff(diff), [])

    def test_anthropic_key_shape_is_reported_without_value(self):
        fake_value = "sk-ant-" + ("A" * 24)
        diff = (
            "diff --git a/config/demo.txt b/config/demo.txt\n"
            "--- /dev/null\n"
            "+++ b/config/demo.txt\n"
            "@@ -0,0 +1 @@\n"
            f"+TOKEN={fake_value}\n"
        )
        findings = scan_unified_diff(diff)
        self.assertEqual(findings, [("config/demo.txt", 1, "anthropic-key-shape")])
        self.assertNotIn(fake_value, repr(findings))

    def test_private_key_header_is_reported_without_line_content(self):
        header = "-" * 5 + "BEGIN PRIVATE KEY" + "-" * 5
        diff = (
            "diff --git a/docs/key-example.txt b/docs/key-example.txt\n"
            "--- a/docs/key-example.txt\n"
            "+++ b/docs/key-example.txt\n"
            "@@ -5,0 +6 @@\n"
            f"+{header}\n"
        )
        findings = scan_unified_diff(diff)
        self.assertEqual(findings, [("docs/key-example.txt", 6, "private-key-header")])
        self.assertNotIn("PRIVATE KEY", repr(findings))

    def test_sensitive_private_file_paths_are_blocked(self):
        diff = (
            "diff --git a/ops/jarvis/jarvis.env b/ops/jarvis/jarvis.env\n"
            "--- /dev/null\n"
            "+++ b/ops/jarvis/jarvis.env\n"
            "@@ -0,0 +1 @@\n"
            "+EMPTY_PLACEHOLDER=not-a-secret\n"
        )
        findings = scan_unified_diff(diff)
        self.assertIn(("ops/jarvis/jarvis.env", 0, "sensitive-file-path"), findings)

    def test_env_templates_are_allowed(self):
        self.assertFalse(sensitive_path("ops/jarvis/jarvis.env.example"))
        self.assertFalse(sensitive_path("config/service.env.template"))
        self.assertFalse(sensitive_path("docs/keys.sample"))

    def test_env_and_private_key_extensions_are_blocked(self):
        for path in (".env", ".env.local", ".env.production", "config/production.env",
                     "service.env.local", "keys/signing.pem", "backup/client.p12",
                     "backup/client.pfx", "keys/agent.key"):
            with self.subTest(path=path):
                self.assertTrue(sensitive_path(path))

    def test_deleted_lines_are_not_scanned(self):
        fake_value = "sk-ant-" + ("B" * 24)
        diff = (
            "diff --git a/config/demo.txt b/config/demo.txt\n"
            "--- a/config/demo.txt\n"
            "+++ b/config/demo.txt\n"
            "@@ -1 +0,0 @@\n"
            f"-TOKEN={fake_value}\n"
        )
        self.assertEqual(scan_unified_diff(diff), [])

    def test_context_lines_are_not_scanned(self):
        fake_value = "sk-ant-" + ("C" * 24)
        diff = (
            "diff --git a/config/demo.txt b/config/demo.txt\n"
            "--- a/config/demo.txt\n"
            "+++ b/config/demo.txt\n"
            "@@ -1,2 +1,2 @@\n"
            f" {fake_value}\n"
            "+ordinary text\n"
        )
        self.assertEqual(scan_unified_diff(diff), [])

    def test_high_risk_github_actions_constructs_are_blocked(self):
        samples = (
            ("pull_request_target:", "workflow-pull-request-target"),
            ("runs-on: [self-hosted, Linux, X64]", "workflow-self-hosted-runner"),
            ("permissions: write-all", "workflow-write-all-permissions"),
            ("contents: write", "workflow-contents-write"),
            ("id-token: write", "workflow-id-token-write"),
            ("persist-credentials: true", "workflow-persisted-checkout-credentials"),
        )
        for added_line, expected_rule in samples:
            with self.subTest(rule=expected_rule):
                diff = (
                    "diff --git a/.github/workflows/new.yml b/.github/workflows/new.yml\\n"
                    "--- /dev/null\\n"
                    "+++ b/.github/workflows/new.yml\\n"
                    "@@ -0,0 +1 @@\\n"
                    f"+{added_line}\\n"
                )
                findings = scan_unified_diff(diff)
                self.assertEqual(findings, [(".github/workflows/new.yml", 1, expected_rule)])

    def test_workflow_policy_ignores_comments_and_non_workflow_docs(self):
        comment_diff = (
            "diff --git a/.github/workflows/new.yml b/.github/workflows/new.yml\\n"
            "--- /dev/null\\n"
            "+++ b/.github/workflows/new.yml\\n"
            "@@ -0,0 +1 @@\\n"
            "+# pull_request_target: is discussed here, not configured\\n"
        )
        docs_diff = (
            "diff --git a/docs/security.md b/docs/security.md\\n"
            "--- /dev/null\\n"
            "+++ b/docs/security.md\\n"
            "@@ -0,0 +1 @@\\n"
            "+pull_request_target: is a dangerous workflow trigger\\n"
        )
        self.assertEqual(scan_unified_diff(comment_diff), [])
        self.assertEqual(scan_unified_diff(docs_diff), [])

    def test_invalid_commit_reference_is_rejected_before_git(self):
        with self.assertRaisesRegex(ValueError, "full 40-character commit SHAs"):
            compare_commits("--help", "0" * 40)

    def test_other_common_secret_shapes_are_detected(self):
        samples = (
            ("AKIA" + "A" * 16, "aws-access-key-id"),
            ("AIza" + "A" * 35, "google-api-key-shape"),
            ("xoxb-" + "A" * 12, "slack-token-shape"),
            ("github_pat_" + "A" * 24, "github-token-shape"),
            ("sk_live_" + "A" * 20, "stripe-live-secret-shape"),
        )
        for fake_value, expected_rule in samples:
            with self.subTest(rule=expected_rule):
                diff = (
                    "diff --git a/config/demo.txt b/config/demo.txt\n"
                    "--- a/config/demo.txt\n"
                    "+++ b/config/demo.txt\n"
                    "@@ -0,0 +1 @@\n"
                    f"+VALUE={fake_value}\n"
                )
                findings = scan_unified_diff(diff)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0][2], expected_rule)
                self.assertNotIn(fake_value, repr(findings))


if __name__ == "__main__":
    unittest.main()
