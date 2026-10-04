"""Offline checks that the transfer package matches its manifest and the canonical note."""
import hashlib
import io
import json
import unittest
import zipfile

import build_transfer_package as package


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(package.PACKAGE.is_file(),
                        'transfer package missing; run build_transfer_package.py')
        self.manifest = json.loads(package.MANIFEST.read_text())
        self.payload = package.PACKAGE.read_bytes()

    def test_package_matches_manifest_and_member_sources(self):
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), self.manifest['package_sha256'])
        self.assertEqual(len(self.payload), self.manifest['package_bytes'])
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            self.assertEqual(archive.namelist(), [name for name, _ in package.MEMBERS])
            for member in self.manifest['members']:
                self.assertEqual(archive.read(member['archive_name']),
                                 (package.ROOT / member['source']).read_bytes())

    def test_note_member_is_the_canonical_note(self):
        with zipfile.ZipFile(io.BytesIO(self.payload)) as archive:
            note = archive.read(package.NOTE)
        self.assertEqual(note, (package.HERE / package.NOTE).read_bytes())
        self.assertEqual(hashlib.sha256(note).hexdigest(), self.manifest['note_sha256'])

    def test_rebuild_has_identical_members(self):
        with zipfile.ZipFile(io.BytesIO(package.build_bytes())) as rebuilt, \
                zipfile.ZipFile(io.BytesIO(self.payload)) as committed:
            self.assertEqual(rebuilt.namelist(), committed.namelist())
            for name in rebuilt.namelist():
                self.assertEqual(rebuilt.read(name), committed.read(name))

    def test_no_secret_like_or_runtime_members(self):
        for name, source in package.MEMBERS:
            self.assertNotIn('secret', name.lower())
            self.assertFalse(name.endswith(('.env', '.local.env', '.pem', '.key', '.json.state')))
            self.assertNotIn('dr.local.env', source.as_posix())


if __name__ == '__main__':
    unittest.main()
