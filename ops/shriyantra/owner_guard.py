#!/usr/bin/env python3
"""Fail-closed verification of owner-signed, action-bound ShriYantra approvals.

The signing private key belongs ONLY to the trusted control plane and must never
be copied to Arena, agents, this repository, or developer workstations.
Requires the 'cryptography' package for Ed25519 public-key verification.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


class AuthorizationDenied(RuntimeError):
    """Raised when an owner approval is missing, invalid, stale, or out of scope."""


def _b64url_decode(value: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as exc:
        raise AuthorizationDenied("Malformed authorization token.") from exc


def canonical_target(task: str, head: str, risk: str) -> str:
    """Stable hash binds approval to the exact task, autonomous head, and risk."""
    payload = json.dumps(
        {"task": task, "head": head, "risk": risk},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_claims(
    claims: dict[str, Any], *, action: str, target: str, required_scope: str,
    now: int | None = None,
) -> None:
    """Validate identity, audience, expiry, action, target, scope, and step-up."""
    now = int(time.time()) if now is None else now
    owner = os.environ.get("VYOMARAJ_OWNER_SUBJECT", "")
    issuer = os.environ.get("VYOMARAJ_AUTH_ISSUER", "")
    audience = os.environ.get("VYOMARAJ_AUTH_AUDIENCE", "shriyantra")
    epoch = os.environ.get("VYOMARAJ_SECURITY_EPOCH", "")

    if not owner or not issuer or not epoch:
        raise AuthorizationDenied(
            "Owner identity, trusted issuer, and security epoch must be configured."
        )
    if claims.get("sub") != owner:
        raise AuthorizationDenied("Approval subject is not the configured owner.")
    if claims.get("iss") != issuer:
        raise AuthorizationDenied("Untrusted approval issuer.")
    aud = claims.get("aud")
    if not (aud == audience or isinstance(aud, list) and audience in aud):
        raise AuthorizationDenied("Approval audience mismatch.")
    if not isinstance(claims.get("exp"), int) or claims["exp"] <= now:
        raise AuthorizationDenied("Approval is expired or has no valid expiry.")
    if not isinstance(claims.get("iat"), int) or claims["iat"] > now + 30:
        raise AuthorizationDenied("Approval issue time is invalid.")
    if now - claims["iat"] > 300:
        raise AuthorizationDenied("Approval is too old; request fresh owner approval.")
    if not claims.get("jti"):
        raise AuthorizationDenied("Approval must include a unique jti.")
    if claims.get("action") != action or claims.get("target") != target:
        raise AuthorizationDenied("Approval does not match this exact action and target.")
    scopes = claims.get("scope", [])
    if isinstance(scopes, str):
        scopes = scopes.split()
    if required_scope not in scopes:
        raise AuthorizationDenied("Approval does not grant the required scope.")
    if claims.get("security_epoch") != epoch:
        raise AuthorizationDenied("Security epoch mismatch; stale approvals are revoked.")
    if claims.get("authn") not in ("webauthn", "passkey"):
        raise AuthorizationDenied("A fresh passkey/WebAuthn owner authentication is required.")
    if action in {
        "user.create", "permission.change", "auth.recovery", "production.deploy",
        "external.publish", "data.destroy", "dr.failover", "dr.failback",
    } and claims.get("step_up") is not True:
        raise AuthorizationDenied("This privileged action requires explicit step-up approval.")


def verify_owner_approval(
    token: str, *, action: str, target: str, required_scope: str,
) -> dict[str, Any]:
    """Verify a compact EdDSA JWT using a control-plane public key; never issues tokens."""
    if not token or token.count(".") != 2:
        raise AuthorizationDenied("Missing or malformed owner approval token.")
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise AuthorizationDenied(
            "Secure verification dependency missing; install ops/shriyantra/requirements.txt."
        ) from exc

    header_part, payload_part, signature_part = token.split(".")
    header = json.loads(_b64url_decode(header_part))
    claims = json.loads(_b64url_decode(payload_part))
    if header.get("alg") != "EdDSA" or header.get("typ", "JWT") != "JWT":
        raise AuthorizationDenied("Only EdDSA-signed JWT approvals are accepted.")
    key_path = os.environ.get("VYOMARAJ_AUTH_PUBLIC_KEY", "")
    if not key_path or not Path(key_path).is_file():
        raise AuthorizationDenied("Trusted owner-approval public key is not configured.")
    try:
        public_key = serialization.load_pem_public_key(Path(key_path).read_bytes())
        if not isinstance(public_key, Ed25519PublicKey):
            raise AuthorizationDenied("Configured approval key must be Ed25519.")
        signed = (header_part + "." + payload_part).encode("ascii")
        public_key.verify(_b64url_decode(signature_part), signed)
    except AuthorizationDenied:
        raise
    except Exception as exc:
        raise AuthorizationDenied("Owner approval signature verification failed.") from exc

    if not isinstance(claims, dict):
        raise AuthorizationDenied("Approval claims must be a JSON object.")
    validate_claims(
        claims, action=action, target=target, required_scope=required_scope,
    )
    return claims


def consume_approval_jti(claims: dict[str, Any]) -> None:
    """Atomically consume a jti in a persistent/shared replay directory.

    Production workers must point this at a shared store with atomic create semantics,
    or replace it with the control plane's atomic one-time approval-consumption API.
    A per-machine directory does not prevent replay across different workers.
    """
    replay_dir_value = os.environ.get("VYOMARAJ_AUTHZ_REPLAY_DIR", "")
    if not replay_dir_value:
        raise AuthorizationDenied(
            "Approval replay protection is not configured; set a persistent shared replay directory."
        )
    replay_dir = Path(replay_dir_value).resolve()
    replay_dir.mkdir(parents=True, exist_ok=True)
    jti_hash = hashlib.sha256(str(claims["jti"]).encode("utf-8")).hexdigest()
    marker = replay_dir / (jti_hash + ".used")
    try:
        fd = os.open(str(marker), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({"consumed_at": int(time.time()), "jti_hash": jti_hash}))
    except FileExistsError as exc:
        raise AuthorizationDenied("This owner approval has already been used.") from exc


def require_owner_approval(*, action: str, target: str, required_scope: str) -> dict[str, Any]:
    """Verify and consume a short-lived approval; never issues owner tokens."""
    claims = verify_owner_approval(
        os.environ.get("VYOMARAJ_AUTHZ_TOKEN", ""),
        action=action, target=target, required_scope=required_scope,
    )
    consume_approval_jti(claims)
    return claims
