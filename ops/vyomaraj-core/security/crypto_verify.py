#!/usr/bin/env python3
"""Read-only cryptography baseline verifier.

This verifier never prints or loads secret values. It checks the repository policy
and optionally validates that the runtime exposes a TLS 1.3 endpoint when a URL is
explicitly supplied by the operator.

It intentionally does not mark the system LIVE. External KMS/HSM, mTLS, certificate
rotation, PQC support, and provider-specific crypto must be proven separately.
"""
from __future__ import annotations

import argparse
import json
import ssl
import socket
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
CRYPTO = ROOT / "security" / "CRYPTOGRAPHY_BASELINE.json"
PERIMETER = ROOT / "security" / "SHRIYANTRA_SECURITY_PERIMETER.json"


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def tls13_probe(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return {"status": "REJECTED", "reason": "Only explicit https:// URLs are accepted"}
    port = parsed.port or 443
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    try:
        with socket.create_connection((parsed.hostname, port), timeout=8) as raw:
            with ctx.wrap_socket(raw, server_hostname=parsed.hostname) as s:
                return {
                    "status": "VERIFIED",
                    "tls_version": s.version(),
                    "cipher": s.cipher()[0] if s.cipher() else None,
                }
    except Exception as exc:
        return {"status": "UNVERIFIED", "reason": type(exc).__name__}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--https-url", help="Optional operator-supplied HTTPS endpoint for TLS 1.3 probe")
    args = ap.parse_args()

    crypto = load(CRYPTO)
    perimeter = load(PERIMETER)

    required = [
        crypto["at_rest"]["data_encryption"] == "AES-256-GCM",
        crypto["at_rest"]["envelope_encryption"] is True,
        crypto["in_transit"]["minimum"] == "TLS_1.3",
        perimeter["network"]["internal_mtls_required"] is True,
        perimeter["network"]["default_deny_ingress"] is True,
        perimeter["network"]["default_deny_egress"] is True,
        crypto["key_management"]["root_keys_exportable"] is False,
        crypto["passwords"]["algorithm"] == "Argon2id",
    ]

    result = {
        "policy_files_present": True,
        "baseline_policy_valid": all(required),
        "live_external_crypto": "UNVERIFIED",
        "tls_probe": None,
        "secrets_exposed": False,
    }

    if args.https_url:
        result["tls_probe"] = tls13_probe(args.https_url)
        result["live_external_crypto"] = result["tls_probe"]["status"]

    print(json.dumps(result, indent=2))
    return 0 if result["baseline_policy_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
