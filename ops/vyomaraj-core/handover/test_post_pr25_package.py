"""Offline checks for the post-PR25 companion package.

The companion must be a strict superset of the canonical transfer package (identical bytes for
every canonical member), reproducible byte-for-byte, faithful to its own manifest, and free of
secret-like members. The companion note must not claim the canonical note's SHA256 or any other
file's bytes as its own.
"""
import hashlib
import io
import json
import unittest
import zipfile

import build_post_pr25_package as companion
import build_transfer_package as canonical


class PostPr25PackageTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(companion.PACKAGE.is_file(),
                        'companion package missing; run build_post_pr25_package.py')
        self.assertTrue((companion.HERE / companion.NOTE).is_file(), 'companion note missing')
        self.manifest = json.loads(companion.MANIFEST.read_text())
        self.payload = companion.PACKAGE.read_bytes()

    def test_package_matches_manifest_and_member_sources(self):
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), self.manifest['package_sha256'])
        self.assertEqual(len(self.payload), self.manifest['package_bytes'])
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            self.assertEqual(archive.namelist(), [name for name, _ in companion.MEMBERS])
            for member in self.manifest['members']:
                data = archive.read(member['archive_name'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), member['sha256'])
                self.assertEqual(len(data), member['bytes'])

    def test_companion_is_a_superset_of_the_canonical_package(self):
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            canonical_total = self.manifest['canonical_members_total']
            names = archive.namelist()
            manifest_names = [m['archive_name'] for m in self.manifest['members']]
            self.assertEqual(names[:canonical_total], manifest_names[:canonical_total],
                             'frozen canonical members must be the leading block of the companion')
            self.assertEqual(len(names), self.manifest['members_total'])
            frozen = {m['archive_name']: m for m in self.manifest['members'][:self.manifest['canonical_members_total']]}
            for name in manifest_names[:self.manifest['canonical_members_total']]:
                data = archive.read(name)
                self.assertEqual(hashlib.sha256(data).hexdigest(), frozen[name]['sha256'],
                                 f'{name} differs from its frozen manifest member')

    def test_rebuild_is_deterministic_for_current_sources(self):
        first = companion.build_bytes()
        second = companion.build_bytes()
        self.assertEqual(first, second)

    def test_note_member_is_the_companion_note_and_not_the_canonical_note(self):
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            note = archive.read(companion.NOTE)
        self.assertEqual(note, (companion.HERE / companion.NOTE).read_bytes())
        self.assertEqual(hashlib.sha256(note).hexdigest(), self.manifest['note_sha256'])
        self.assertNotEqual(hashlib.sha256(note).hexdigest(),
                            hashlib.sha256((companion.HERE / canonical.NOTE).read_bytes()).hexdigest(),
                            'the companion note must not be a copy of the canonical note')

    def test_generated_evidence_is_not_a_member(self):
        names = [name for name, _ in companion.MEMBERS]
        for volatile in ('TEST_EVIDENCE_2026_10_04.json', 'PREVIEW_VERIFICATION_2026_10_04.json',
                         companion.MANIFEST.name, 'TRANSFER_MANIFEST_2026_10_04.json',
                         companion.PACKAGE.name):
            self.assertNotIn(volatile, names,
                             f'{volatile} is rewritten by a check run and must not be packaged')

    def test_no_secret_like_or_runtime_members(self):
        for name, source in companion.MEMBERS:
            self.assertNotIn('secret', name.lower())
            self.assertFalse(name.endswith(('.env', '.local.env', '.pem', '.key', '.json.state')))
            self.assertNotIn('dr.local.env', source.as_posix())


if __name__ == '__main__':
    unittest.main()
