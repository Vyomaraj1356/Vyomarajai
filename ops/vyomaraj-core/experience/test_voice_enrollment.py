"""Offline checks for on-device voice enrollment.

These lock the promise that matters: the template never leaves the device, never enters the
repository, never uploads, and cannot be collected without consent that can be withdrawn.
"""
import json
import unittest
from pathlib import Path

import voice_enrollment as voice


class PolicyTests(unittest.TestCase):
    def test_policy_is_free_and_vendorless(self):
        policy = voice.policy()
        self.assertEqual(policy['mode'], 'on_device_only_no_vendor')
        self.assertIsNone(policy['vendor_used'])
        self.assertFalse(policy['uploads_enabled'])
        self.assertEqual(policy['storage'], 'device_only')
        self.assertEqual(policy['network_calls'], 0)

    def test_policy_refuses_cloning_and_identity_capture(self):
        policy = voice.policy()
        self.assertFalse(policy['clones_other_people_voices'])
        self.assertFalse(policy['captures_identity_documents'])
        self.assertFalse(policy['templates_in_repository'])
        self.assertIn('uidai.in', policy['identity_documents_route']['url'])

    def test_consent_text_states_purpose_storage_deletion_and_identity_route(self):
        text = voice.CONSENT_TEXT
        for marker in ('on this device only', 'never uploaded', 'delete the voice profile',
                       'no voice of any other person is cloned',
                       'no biometric identity check is performed', 'uidai.in',
                       'nothing is lost by declining'):
            self.assertIn(marker, text)


class GuardTests(unittest.TestCase):
    def test_repository_destinations_are_refused(self):
        for destination in (voice.ROOT, voice.ROOT / 'ops', voice.HERE, voice.HERE / 'voice.wav'):
            with self.subTest(destination=str(destination)):
                with self.assertRaises(PermissionError):
                    voice.guard_destination(destination)

    def test_device_destination_is_allowed(self):
        self.assertTrue(voice.guard_destination('/tmp/vyomaraj-voice-profile'))

    def test_no_upload_path_exists(self):
        with self.assertRaises(PermissionError):
            voice.upload('/tmp/voice.wav', 'https://example.invalid/collect')

    def test_no_templates_in_repository(self):
        self.assertTrue(voice.assert_no_templates_in_repo())

    def test_guard_notices_a_planted_template(self):
        planted = voice.ROOT / 'ops/vyomaraj-core/experience/_planted_template_probe.json'
        planted.write_text(json.dumps({'voice_template': 'A' * 64}), encoding='utf-8')
        try:
            with self.assertRaises(AssertionError) as error:
                voice.assert_no_templates_in_repo()
            self.assertIn('_planted_template_probe.json', str(error.exception))
        finally:
            planted.unlink(missing_ok=True)

    def test_guard_notices_a_template_in_an_executable_source(self):
        planted = voice.ROOT / 'ops/vyomaraj-core/experience/_planted_probe.cjs'
        planted.write_text('module.exports={ voiceprint: "BbCcDdEeFfGgHhIiJjKkLlMm" };\n', encoding='utf-8')
        try:
            with self.assertRaises(AssertionError):
                voice.assert_no_templates_in_repo()
        finally:
            planted.unlink(missing_ok=True)
        self.assertTrue(voice.assert_no_templates_in_repo())


class EnrollmentTests(unittest.TestCase):
    def test_enrollment_requires_consent(self):
        for consent in (False, None, 'yes', 1):
            with self.subTest(consent=consent), self.assertRaises(PermissionError):
                voice.enroll(consent, ['phrase one', 'phrase two', 'phrase three'])

    def test_enrollment_requires_enough_phrases(self):
        with self.assertRaises(ValueError):
            voice.enroll(True, ['only one'])

    def test_enrollment_never_stores_a_template_here(self):
        profile = voice.enroll(True, ['श्री राम जय राम', 'Jai Shri Ram', 'Shani Blue'])
        self.assertFalse(profile['template_stored_by_this_module'])
        self.assertTrue(profile['destination_is_device_only'])
        self.assertFalse(profile['uploads_enabled'])

    def test_withdrawal_leaves_no_template(self):
        result = voice.delete_voice_profile()
        self.assertTrue(result['withdrawn'])
        self.assertFalse(result['templates_retained'])
        state = json.loads(voice.PROFILES.read_text(encoding='utf-8'))
        self.assertEqual(state['profiles'], [])
        self.assertIn('withdrawn', state)

    def test_policy_file_matches_the_module(self):
        if not voice.POLICY.is_file():
            self.skipTest('policy file not written yet; run voice_enrollment.py --write-policy')
        self.assertEqual(json.loads(voice.POLICY.read_text(encoding='utf-8')), voice.policy())


if __name__ == '__main__':
    unittest.main()
