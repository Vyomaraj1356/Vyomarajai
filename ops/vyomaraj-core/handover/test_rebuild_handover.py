"""Offline regression tests for the metadata-only handover reconstruction."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import rebuild_handover as handover


class HandoverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in (handover.REGISTRY, handover.CATALOG):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((handover.ROOT / relative).read_bytes())
        catalog = json.loads((self.root / handover.CATALOG).read_text())
        for pack in catalog['packs']:
            for name in pack['files']:
                target = self.root / pack['path'] / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('DO_NOT_COPY_RUNTIME_SENTINEL')

    def mutate(self, relative, change):
        path = self.root / relative
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_checked_in_output_matches(self):
        self.assertEqual((handover.ROOT / handover.OUTPUT).read_text(), handover.render())

    def test_unknowns_and_scope_remain_explicit(self):
        text = handover.render(self.root)
        for expected in ('NOT the recovered original 365-line', 'Names: UNKNOWN (3 individuals)',
                         'Individual names: UNKNOWN; individual assignments: UNMAPPED',
                         'Remaining slot: UNMAPPED', 'NOT all 421 product titles'):
            self.assertIn(expected, text)
        self.assertNotIn('S20:', text)
        self.assertNotIn('DO_NOT_COPY_RUNTIME_SENTINEL', text)

    def test_only_two_metadata_files_are_read(self):
        original = Path.read_bytes
        seen = []
        allowed = {self.root / handover.REGISTRY, self.root / handover.CATALOG}

        def guarded_read(path):
            self.assertIn(path, allowed)
            seen.append(path)
            return original(path)

        with patch.object(Path, 'read_bytes', guarded_read):
            handover.render(self.root)
        self.assertEqual(set(seen), allowed)
        self.assertEqual(len(seen), 2)

    def test_bad_category_total_rejected(self):
        self.mutate(handover.REGISTRY, lambda d: d['categories'][0].update(products=7))
        with self.assertRaisesRegex(ValueError, 'Product count'):
            handover.render(self.root)

    def test_bad_group_count_rejected(self):
        self.mutate(handover.REGISTRY,
                    lambda d: d['rosters']['ENTERTAINMENT']['groups'][0].update(count=9))
        with self.assertRaisesRegex(ValueError, 'Entertainment group count'):
            handover.render(self.root)

    def test_duplicate_catalog_file_rejected(self):
        self.mutate(handover.CATALOG,
                    lambda d: d['packs'][0]['files'].__setitem__(1, d['packs'][0]['files'][0]))
        with self.assertRaisesRegex(ValueError, '32 unique'):
            handover.render(self.root)

    def test_missing_catalog_file_rejected(self):
        (self.root / 'ops/bhakti-shakti/damru.json').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing catalog file'):
            handover.render(self.root)

    def test_path_traversal_rejected(self):
        self.mutate(handover.CATALOG, lambda d: d['packs'][0].update(path='ops/../outside'))
        with self.assertRaisesRegex(ValueError, 'Invalid catalog directory'):
            handover.render(self.root)

    def test_new_platform_mapping_requires_review(self):
        self.mutate(handover.REGISTRY,
                    lambda d: d['rosters']['PLATFORM'].update(unmapped_slot_id='S20'))
        with self.assertRaisesRegex(ValueError, 'Platform mapping needs review'):
            handover.render(self.root)


if __name__ == '__main__':
    unittest.main()
