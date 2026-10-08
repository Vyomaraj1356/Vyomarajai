"""Daily-start sequence and the location-authorization refusals.

Collected by `unittest discover` as well as pytest. These were module-level pytest
functions, which `unittest discover` does not collect, so the offline suite was not running
them and the location consent/expiry contract was effectively unenforced there. Assertions
are unchanged; only the wrapper is.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from ops.vyomaraj.daily_start import (  # noqa: E402
    HANUMAN_INVOCATION,
    MANTRA,
    RAM_INVOCATION,
    SEQUENCE,
    run_daily_start,
)
from ops.vyomaraj.location_authorization import (  # noqa: E402
    is_active,
    issue_authorization,
    revoke,
)


class DailyStartTests(unittest.TestCase):
    def test_daily_start_contains_mantra_and_peer_sequence(self):
        events = run_daily_start("bharath_vyomaraj", {
            "system_health_check": lambda: True,
            "owner_authority_check": lambda: True,
        })
        self.assertEqual([e.step for e in events], list(SEQUENCE))
        self.assertEqual(events[2].message, RAM_INVOCATION)
        self.assertEqual(events[3].message, HANUMAN_INVOCATION)
        self.assertIn(MANTRA, events[4].message)


class LocationAuthorizationTests(unittest.TestCase):
    def test_location_defaults_to_owner_authorization(self):
        with self.assertRaises(PermissionError):
            issue_authorization("device-1", "test", 10, False, True)

    def test_location_requires_consent(self):
        with self.assertRaises(PermissionError):
            issue_authorization("device-1", "test", 10, True, False)

    def test_location_expires_and_can_be_revoked(self):
        auth = issue_authorization("device-1", "test", 10, True, True)
        self.assertTrue(is_active(auth))
        self.assertFalse(is_active(revoke(auth)))


if __name__ == "__main__":
    unittest.main()
