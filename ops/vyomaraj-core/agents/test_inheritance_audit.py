"""The inheritance audit must match its generator, its sources and its honesty rules."""
import json
import unittest
from pathlib import Path

import inheritance_audit as audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.registry = audit.load(audit.REGISTRY)
        self.index = audit.load(audit.INDEX)

    def test_checked_in_audit_matches_generator(self):
        self.assertEqual(audit.OUTPUT.read_text(encoding='utf-8'), audit.render())

    def test_totals_in_the_audit_come_from_the_registry(self):
        text = audit.render()
        totals = self.registry['totals']
        self.assertIn(f"**{totals['sub_agents']}**", text)
        self.assertIn(f"**{totals['named_sub_agents']}**", text)
        self.assertIn(f"**{totals['unnamed_numbered_sub_agents']}**", text)
        self.assertIn(str(self.index['indexed_reference_count']), text)

    def test_audit_keeps_unknowns_and_limits(self):
        text = audit.render()
        for marker in ('UNKNOWN', 'NOT_VERIFIED', 'UNRECONCILED', 'not** a runtime audit'):
            self.assertIn(marker, text)

    def test_audit_uses_repository_relative_paths(self):
        text = audit.render()
        self.assertNotIn(audit.ROOT.as_posix(), text)
        self.assertNotIn('/home/', text)

    def test_builder_refuses_tampered_metadata(self):
        original = audit.load
        try:
            audit.load = lambda path: (self.bad if str(path).endswith('AGENT_REGISTRY_CURRENT.json')
                                       else original(path))
            self.bad = json.loads(audit.REGISTRY.read_text())
            self.bad['totals']['sub_agents'] = 999
            with self.assertRaises(ValueError):
                audit.render()
        finally:
            audit.load = original


if __name__ == '__main__':
    unittest.main()
