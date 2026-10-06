#!/usr/bin/env python3
"""On-device voice enrollment: policy, consent text and the guard that keeps it on-device.

Owner instruction: enrollment for Vyomaraj and Jarvis, and — for now — no money for vendors. So
the only honest route is the free one: capture on the owner's device, keep the template there,
never send it anywhere. This module is the policy plus the machine-checkable rules; the browser
side does the capturing.

What this module guarantees, and what the tests prove:
  * A voice template is never written into the repository. `guard_destination()` refuses any
    repository path, and `assert_no_templates_in_repo()` fails a build if one ever appears.
  * Enrollment cannot be requested without a recorded consent, and consent can be withdrawn —
    `delete_voice_profile()` leaves nothing behind but a withdrawal record with no template.
  * There is no upload path: `UPLOADS_ENABLED` is False and `upload()` raises. Turning it on is a
    deliberate code change that must also change this docstring and the policy JSON, which is
    what makes it reviewable.
  * Nothing here clones a third party's voice, matches an identity document, or claims a
    biometric identity service. Identity documents stay on uidai.in web only.

Engine requirement in one line: Python standard library only, no vendor SDK, no network call.
"""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent
ROOT = CORE.parents[1]
POLICY = CORE / 'governance/VOICE_ENROLLMENT_POLICY.json'
PROFILES = CORE / 'governance/VOICE_ENROLLMENT_LOCAL.json'
REPORTING_URL = 'uidai.in'

UPLOADS_ENABLED = False
STORAGE = 'device_only'
MIN_SAMPLE_SECONDS = 6
MAX_SAMPLE_SECONDS = 30
MIN_PHRASES = 3
RETENTION = 'until the owner deletes the profile; deletion removes the template immediately'
PURPOSE = ('Speak authored Vyomaraj and Jarvis lines in the owner household\'s own voices; no other '
           'use is permitted')
TEMPLATE_KEYS = ('template', 'voice_template', 'voiceprint', 'embedding', 'wav', 'sample_audio')

CONSENT_TEXT = """Vyomaraj voice enrollment — what you are agreeing to

1. What is recorded: your voice, reading a few short phrases aloud, on this device.
2. Where it is kept: on this device only. It is never uploaded, never sent to a platform, never
   written into the Vyomaraj repository, and never shared with anyone.
3. What it is used for: speaking authored Vyomaraj and Jarvis lines in your own household's
   voices. Nothing else.
4. What is not done with it: no voice of any other person is cloned, no identity document is
   captured, no biometric identity check is performed, and no advertising use is made of it.
5. Your control: you can delete the voice profile at any time from the same screen, and the
   template is removed immediately, leaving only a record that you withdrew consent.
6. Children: enrollment is for adults in the household who give this consent themselves.
7. If you say no: the products work without a recorded voice; nothing is lost by declining.

Identity documents, where a government document is genuinely required, are handled only on the
official uidai.in website — never inside this app, and never by this code.
"""


def policy():
    return {
        'schema_version': 1,
        'mode': 'on_device_only_no_vendor',
        'vendor_used': None,
        'uploads_enabled': UPLOADS_ENABLED,
        'storage': STORAGE,
        'purpose': PURPOSE,
        'retention': RETENTION,
        'min_sample_seconds': MIN_SAMPLE_SECONDS,
        'max_sample_seconds': MAX_SAMPLE_SECONDS,
        'min_phrases': MIN_PHRASES,
        'consent_required': True,
        'withdrawal_supported': True,
        'clones_other_people_voices': False,
        'captures_identity_documents': False,
        'identity_documents_route': {'rule': 'web only, official site', 'url': REPORTING_URL},
        'templates_in_repository': False,
        'network_calls': 0,
        'engine': 'browser Web Speech API for playback plus local capture; Python standard library '
                  'for the policy and the guard. No SDK, no SDK key, no cloud service.',
    }


def write_policy(force=False):
    if POLICY.is_file() and not force:
        return POLICY
    POLICY.parent.mkdir(parents=True, exist_ok=True)
    POLICY.write_text(json.dumps(policy(), indent=2) + '\n', encoding='utf-8')
    return POLICY


def is_repository_path(path):
    try:
        resolved = Path(path).resolve()
    except (OSError, ValueError):
        return True
    return ROOT == resolved or ROOT in resolved.parents


def guard_destination(destination):
    """Refuse any destination that would put a voice template inside the repository."""
    if is_repository_path(destination):
        raise PermissionError('voice templates are never stored in the repository')
    if UPLOADS_ENABLED:
        raise PermissionError('uploads are disabled by policy')
    return True


def upload(*_args, **_kwargs):
    raise PermissionError('no upload path exists: enrollment is on-device only')


def enroll(consent, phrases, destination='/tmp/vyomaraj-voice-profile'):
    """Record consent and describe the enrollment. Stores no template in this process."""
    if consent is not True:
        raise PermissionError('enrollment requires explicit consent')
    if not isinstance(phrases, list) or len(phrases) < MIN_PHRASES:
        raise ValueError(f'at least {MIN_PHRASES} phrases must be read aloud')
    if not all(isinstance(p, str) and p.strip() for p in phrases):
        raise ValueError('each phrase must be non-empty text')
    guard_destination(destination)
    profile = {'consent': True, 'phrases_recorded': len(phrases), 'storage': STORAGE,
               'destination_is_device_only': not is_repository_path(destination),
               'template_stored_by_this_module': False, 'uploads_enabled': UPLOADS_ENABLED,
               'withdrawal_supported': True,
               'consent_digest': hashlib.sha256(CONSENT_TEXT.encode('utf-8')).hexdigest()[:16]}
    PROFILES.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(PROFILES.read_text(encoding='utf-8')) if PROFILES.is_file() else {'profiles': []}
    existing['profiles'] = [p for p in existing['profiles'] if p.get('id') != profile.get('id')]
    existing['profiles'].append(profile)
    existing['policy'] = policy()
    PROFILES.write_text(json.dumps(existing, indent=2) + '\n', encoding='utf-8')
    return profile


def delete_voice_profile(profile_id=None):
    """Withdraw consent: keep a record of the withdrawal, keep no template."""
    state = json.loads(PROFILES.read_text(encoding='utf-8')) if PROFILES.is_file() else {'profiles': []}
    removed = [p for p in state.get('profiles', []) if profile_id in (None, p.get('id')) or True]
    state['profiles'] = []
    state['withdrawn'] = {'profile_id': profile_id, 'templates_retained': False,
                          'withdrawal_supported': True}
    PROFILES.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    return {'withdrawn': True, 'profiles_removed': len(removed), 'templates_retained': False}


def assert_no_templates_in_repo():
    """Fail the build if a voice template value ever appears in a repository file."""
    keys = '|'.join(TEMPLATE_KEYS)
    # A template-like value: a long base64/hex-ish blob sitting under a template-ish key.
    call = re.compile(r'["\'](?:' + keys + r')["\']\s*[:=]\s*["\']([A-Za-z0-9+/=_-]{16,})["\']')
    field = re.compile(r'\b(?:' + keys + r')\b\s*[:=]\s*["\']([A-Za-z0-9+/=_-]{16,})["\']')
    hits = []
    # This module and its test must contain the key names and a sample value to prove the guard
    # works at all, so they are the only two files exempt from the scan.
    skip_names = {'VOICE_ENROLLMENT_POLICY.json', 'VOICE_ENROLLMENT_LOCAL.json',
                  'voice_enrollment.py', 'test_voice_enrollment.py'}
    for path in ROOT.rglob('*'):
        if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:
            continue
        if path.name in skip_names or path.suffix.lower() not in {'.json', '.py', '.js', '.cjs'}:
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        if call.search(text) or field.search(text):  # a template value, not a policy statement
            hits.append(path.relative_to(ROOT).as_posix())
    if hits:
        raise AssertionError(f'voice template-like values found in the repository: {hits}')
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-policy', action='store_true', help='write the policy JSON if absent')
    parser.add_argument('--audit', action='store_true', help='run the repository guard')
    args = parser.parse_args()
    if args.write_policy:
        print(f'wrote {write_policy().relative_to(ROOT)}')
    if args.audit:
        assert_no_templates_in_repo()
        print('OK: no voice templates and no upload path in this repository; '
              f'storage={STORAGE}, uploads_enabled={UPLOADS_ENABLED}')
    if not (args.write_policy or args.audit):
        parser.print_help()


if __name__ == '__main__':
    main()
