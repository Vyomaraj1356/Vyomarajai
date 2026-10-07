import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from ops.vyomaraj.daily_start import HANUMAN_INVOCATION, MANTRA, RAM_INVOCATION, SEQUENCE, run_daily_start
from ops.vyomaraj.location_authorization import issue_authorization, is_active, revoke

def test_daily_start_contains_mantra_and_peer_sequence():
    events = run_daily_start("bharath_vyomaraj", {
        "system_health_check": lambda: True,
        "owner_authority_check": lambda: True,
    })
    assert [e.step for e in events] == list(SEQUENCE)
    assert events[2].message == RAM_INVOCATION
    assert events[3].message == HANUMAN_INVOCATION
    assert MANTRA in events[4].message

def test_location_defaults_to_owner_authorization():
    try:
        issue_authorization("device-1", "test", 10, False, True)
        assert False
    except PermissionError:
        pass

def test_location_requires_consent():
    try:
        issue_authorization("device-1", "test", 10, True, False)
        assert False
    except PermissionError:
        pass

def test_location_expires_and_can_be_revoked():
    auth = issue_authorization("device-1", "test", 10, True, True)
    assert is_active(auth)
    assert not is_active(revoke(auth))
