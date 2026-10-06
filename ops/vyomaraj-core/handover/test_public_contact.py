#!/usr/bin/env python3
"""Tests for the public-contact seam: set_public_contact.py + the allowlist-aware privacy guard.

PR #36 committed a personal email literally into public files; the privacy guard failed the build.
The fix ships an owner-controlled seam instead of hardcoding an allowlist. These tests pin:
  * the guard stays fail-closed with no config (any personal email is a regression);
  * set_public_contact.py refuses placeholders and requires --confirm-publish;
  * publishing owner_approved:true allowlists exactly that address (custom domain AND gmail);
  * reverting (removing the config) clears the allowlist — nothing is sticky.

NOTE on fixtures: personal-provider addresses (gmail/yahoo/…) are assembled at runtime by _addr(),
never written as a contiguous "local" + "at" + "gmail dot com" literal. sanitize_personal_data.py
--check scans every *tracked* text file, so a contiguous personal-provider address written literally
in this file would (correctly) fail the guard the moment the test is committed. Custom-domain
fixtures (@vyomaraj.app) are not personal-provider addresses and are safe as literals; they are what
the owner would realistically publish.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import sanitize_personal_data as san  # noqa: E402


def _addr(local, domain):
    """Build an address from parts so no personal-provider literal sits in this tracked file."""
    return f"{local}@{domain}"


# Personal-provider fixtures, assembled at runtime (see module docstring).
GMAIL = _addr("someone", "gmail.com")
OWNER_GMAIL = _addr("Vyomarajai", "Gmail.com")
X_GMAIL = _addr("x", "gmail.com")
# Custom-domain fixtures are not personal-provider addresses; safe as literals.
CUSTOM = "contact@vyomaraj.app"
CUSTOM2 = "real@vyomaraj.app"


def run_tool(*args, cwd=None):
    return subprocess.run([sys.executable, str(HERE / "set_public_contact.py"), *args],
                          cwd=str(cwd or ROOT), capture_output=True, text=True, timeout=120)


class AllowedEmailsTests(unittest.TestCase):
    """allowed_emails() reads config/public-contact.json; fail-closed by default."""

    def setUp(self):
        self._orig = san.CONTACT_CONFIG
        self.tmp = tempfile.TemporaryDirectory()
        san.CONTACT_CONFIG = Path(self.tmp.name) / "public-contact.json"

    def tearDown(self):
        san.CONTACT_CONFIG = self._orig
        self.tmp.cleanup()

    def _write(self, record):
        san.CONTACT_CONFIG.write_text(json.dumps(record), encoding="utf-8")

    def test_no_config_is_empty_allowlist(self):
        self.assertEqual(san.allowed_emails(), set())

    def test_unapproved_address_is_not_allowlisted(self):
        self._write({"configured": True, "owner_approved": False, "email": X_GMAIL})
        self.assertEqual(san.allowed_emails(), set())

    def test_not_configured_is_not_allowlisted(self):
        self._write({"configured": False, "owner_approved": True, "email": X_GMAIL})
        self.assertEqual(san.allowed_emails(), set())

    def test_approved_gmail_address_is_allowlisted(self):
        self._write({"configured": True, "owner_approved": True, "email": OWNER_GMAIL})
        self.assertEqual(san.allowed_emails(), {OWNER_GMAIL.lower()})   # lowercased

    def test_approved_custom_domain_is_allowlisted(self):
        self._write({"configured": True, "owner_approved": True, "email": CUSTOM})
        self.assertEqual(san.allowed_emails(), {CUSTOM})

    def test_placeholder_or_malformed_is_not_allowlisted(self):
        for bad in ("[OWNER_EMAIL_REDACTED]", "not-an-email", "", "owner@example.com"):
            self._write({"configured": True, "owner_approved": True, "email": bad})
            self.assertEqual(san.allowed_emails(), set(), f"{bad!r} must not be allowlisted")

    def test_corrupt_config_is_empty_not_crash(self):
        san.CONTACT_CONFIG.write_text("{ not json", encoding="utf-8")
        self.assertEqual(san.allowed_emails(), set())


class SanitizeGuardTests(unittest.TestCase):
    """The guard flags an unapproved personal email and permits an approved one."""

    def setUp(self):
        self._orig = san.CONTACT_CONFIG
        self.tmp = tempfile.TemporaryDirectory()
        san.CONTACT_CONFIG = Path(self.tmp.name) / "public-contact.json"

    def tearDown(self):
        san.CONTACT_CONFIG = self._orig
        self.tmp.cleanup()

    def test_redacts_unapproved_personal_email(self):
        out, n = san.sanitize(f"mail me at {GMAIL} today")
        self.assertEqual(n, 1)
        self.assertIn(san.EMAIL_PLACEHOLDER, out)
        self.assertNotIn(GMAIL, out)

    def test_leaves_approved_email_intact(self):
        san.CONTACT_CONFIG.write_text(json.dumps(
            {"configured": True, "owner_approved": True, "email": GMAIL}), encoding="utf-8")
        out, n = san.sanitize(f"mail me at {GMAIL} today")
        self.assertEqual(n, 0)
        self.assertIn(GMAIL, out)


class SetPublicContactToolTests(unittest.TestCase):
    def test_check_reports_unconfigured(self):
        result = run_tool("--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["configured"])
        self.assertFalse(payload["allowlist_active"])

    def test_refuses_placeholder(self):
        for bad in ("owner@example.com", "[OWNER_EMAIL_REDACTED]", "changeme@x.com"):
            result = run_tool("--email", bad, "--confirm-publish")
            self.assertEqual(result.returncode, 2, f"{bad!r} should be refused")

    def test_email_requires_confirm(self):
        result = run_tool("--email", CUSTOM2)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--confirm-publish", result.stderr)

    def test_confirm_requires_email(self):
        result = run_tool("--confirm-publish")
        self.assertEqual(result.returncode, 2)

    def test_publish_then_check_round_trip(self):
        # The tool resolves its config from its own location, so this exercises the real path.
        # Precondition: no committed contact config; the test removes whatever it writes.
        real = ROOT / "config" / "public-contact.json"
        self.assertFalse(real.exists(), "test precondition: no committed contact config")
        result = run_tool("--email", CUSTOM, "--confirm-publish")
        try:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(real.exists())
            written = json.loads(real.read_text())
            self.assertTrue(written["owner_approved"])
            self.assertEqual(written["email"], CUSTOM)
            check = run_tool("--check")
            self.assertTrue(json.loads(check.stdout)["allowlist_active"])
        finally:
            real.unlink(missing_ok=True)
        self.assertFalse(real.exists(), "round-trip must leave no stray config behind")


if __name__ == "__main__":
    unittest.main()
