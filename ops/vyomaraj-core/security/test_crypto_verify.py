#!/usr/bin/env python3
"""Regression tests for the read-only crypto-policy verifier added by PR #37.

PR #37 merged with a path defect: ``ROOT = Path(__file__).resolve().parents[3]`` resolved to the
*parent of the repository*, so the verifier looked for ``<repo-parent>/security/…`` and died with
FileNotFoundError. That broke the `ShriYantra Crypto Baseline` workflow on the PR and on main
(run 37478806529, step "Verify crypto policy"). These tests pin the behaviour that the workflow
depends on: the policy files are found from any working directory, the verifier exits 0 when the
baseline holds, and it never claims live external crypto without an explicit operator-supplied URL.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VERIFIER = HERE / 'crypto_verify.py'


def run_verifier(cwd, *extra):
    return subprocess.run([sys.executable, str(VERIFIER), *extra], cwd=str(cwd),
                          capture_output=True, text=True, timeout=120)


class CryptoVerifyTests(unittest.TestCase):
    def test_policy_files_resolve_inside_the_repository(self):
        sys.path.insert(0, str(HERE))
        try:
            import crypto_verify
        finally:
            sys.path.pop(0)
        for path in (crypto_verify.CRYPTO, crypto_verify.PERIMETER):
            self.assertTrue(path.is_file(), f'{path} is not a file — the verifier cannot read it')
        self.assertEqual(ROOT, crypto_verify.ROOT, 'ROOT must be the repository root')
        self.assertTrue(crypto_verify.CRYPTO.is_relative_to(ROOT))
        self.assertTrue(crypto_verify.PERIMETER.is_relative_to(ROOT))

    def test_verifier_passes_from_an_unrelated_working_directory(self):
        # The workflow runs it from the repository root; a human may run it from anywhere.
        with tempfile.TemporaryDirectory() as tmp:
            result = run_verifier(tmp)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertTrue(payload['policy_files_present'])
        self.assertTrue(payload['baseline_policy_valid'])

    def test_verifier_never_claims_live_crypto_without_an_explicit_probe(self):
        result = run_verifier(ROOT)
        payload = json.loads(result.stdout)
        self.assertEqual(payload['live_external_crypto'], 'UNVERIFIED')
        self.assertIsNone(payload['tls_probe'])
        self.assertFalse(payload['secrets_exposed'])

    def test_non_https_probe_url_is_rejected_not_fabricated(self):
        result = run_verifier(ROOT, '--https-url', 'http://127.0.0.1:9/')
        payload = json.loads(result.stdout)
        self.assertEqual(payload['tls_probe']['status'], 'REJECTED')
        self.assertEqual(payload['live_external_crypto'], 'REJECTED')
        # Exit code reports the policy verdict, not the optional probe; the policy still holds.
        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload['baseline_policy_valid'])
        # An unreachable https endpoint must degrade to UNVERIFIED, never to a fabricated pass.
        result2 = run_verifier(ROOT, '--https-url', 'https://127.0.0.1:9/')
        payload2 = json.loads(result2.stdout)
        self.assertEqual(payload2['tls_probe']['status'], 'UNVERIFIED')
        self.assertEqual(payload2['live_external_crypto'], 'UNVERIFIED')

    def test_output_carries_no_secret_values(self):
        result = run_verifier(ROOT)
        blob = (result.stdout + result.stderr).lower()
        for needle in ('api_key', 'password', 'private_key', 'token', 'begin'):
            self.assertNotIn(needle, blob)
        self.assertEqual(sorted(json.loads(result.stdout)),
                         ['baseline_policy_valid', 'live_external_crypto', 'policy_files_present',
                          'secrets_exposed', 'tls_probe'],
                         'the verifier must not grow new output fields silently')


if __name__ == '__main__':
    unittest.main()
