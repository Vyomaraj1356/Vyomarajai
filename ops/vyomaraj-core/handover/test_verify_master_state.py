#!/usr/bin/env python3
"""Regression tests for verify_master_state.py — the check behind two CI workflows.

The verifier resolved its state file through ``parents[2]`` (the parent of the repository) and so
always printed ``{"ok": false, "error": "master state missing"}`` and exited 2. The
`Vyomaraj Master State Verification` workflow ran that exit code as a failure on main
(run 37478806559). These tests pin the fixed behaviour and the safety promises the workflow
relies on: the authoritative state file is read, every component keeps its evidence class, no
probe happens unless the operator supplies a URL, and the safety block never claims live DR.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VERIFIER = HERE / 'verify_master_state.py'
STATE = HERE / 'VYOMARAJ_MASTER_STATE.json'


def run(cwd, env=None):
    return subprocess.run([sys.executable, str(VERIFIER)], cwd=str(cwd), capture_output=True,
                          text=True, timeout=120, env=env)


class VerifyMasterStateTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(run(ROOT).stdout)

    def test_master_state_is_found_and_read(self):
        result = run(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.payload['ok'])
        self.assertEqual(self.payload['master_state'], 'PRESENT')

    def test_paths_resolve_from_any_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)['ok'])

    def test_every_component_keeps_its_evidence_class(self):
        state = json.loads(STATE.read_text(encoding='utf-8'))
        allowed = set(state['classification_order']) | {'NOT_RUNNING'}
        components = self.payload['components']
        self.assertEqual(len(components), len(state['components']))
        for item in state['components']:
            reported = components[item['id']]
            self.assertEqual(reported['inventory_status'], item['status'])
            self.assertIn(reported['inventory_status'], allowed)
            self.assertEqual(reported['next_verification'], item['next_verification'])
            self.assertNotEqual(reported['runtime_status'], 'VERIFIED',
                                'no component may be upgraded to VERIFIED by a read-only verifier')

    def test_no_external_probe_without_an_operator_url(self):
        names = [key for key in self.payload['components'] if key.endswith('_PROBE_URL')]
        self.assertEqual(names, [], 'a probe component appeared with no operator-supplied URL')
        presence = self.payload['environment_secret_presence']
        self.assertIn('DR_SECONDARY_TOKEN', presence)
        for name, value in presence.items():
            self.assertIsInstance(value, bool, f'{name} must be reported as presence only')
        # Presence flags are booleans, never values: a secret is never printed.
        for line in json.dumps(self.payload).splitlines():
            self.assertNotIn('sk-', line)

    def test_safety_block_never_claims_live_dr_or_publishing(self):
        safety = self.payload['safety']
        for key, value in safety.items():
            self.assertFalse(value, f'safety flag {key} must stay false')
        self.assertIn('zero_rpo_claim', safety)
        self.assertIn('zero_rto_claim', safety)

    def test_prohibited_live_claims_are_still_recorded(self):
        state = json.loads(STATE.read_text(encoding='utf-8'))
        for claim in ('independent full runtime DR', 'zero-RPO', 'automatic publishing'):
            self.assertIn(claim, state['prohibited_live_claims'])


if __name__ == '__main__':
    unittest.main()
