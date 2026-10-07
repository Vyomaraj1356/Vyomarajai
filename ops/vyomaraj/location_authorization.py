"""Owner-controlled, auditable location authorization policy."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

@dataclass(frozen=True)
class LocationAuthorization:
    authorization_id: str
    target: str
    purpose: str
    issued_at: datetime
    expires_at: datetime
    owner_authorized: bool
    consent_confirmed: bool
    revoked: bool = False

def issue_authorization(target: str, purpose: str, minutes: int,
                        owner_authorized: bool, consent_confirmed: bool) -> LocationAuthorization:
    if not owner_authorized:
        raise PermissionError("explicit owner authorization required")
    if not consent_confirmed:
        raise PermissionError("required device/user consent not confirmed")
    if minutes <= 0:
        raise ValueError("authorization must expire")
    now = datetime.now(timezone.utc)
    return LocationAuthorization(
        authorization_id=str(uuid4()), target=target, purpose=purpose,
        issued_at=now, expires_at=now + timedelta(minutes=minutes),
        owner_authorized=True, consent_confirmed=True,
    )

def is_active(auth: LocationAuthorization, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    return auth.owner_authorized and auth.consent_confirmed and not auth.revoked and now < auth.expires_at

def revoke(auth: LocationAuthorization) -> LocationAuthorization:
    return LocationAuthorization(**{**auth.__dict__, "revoked": True})
