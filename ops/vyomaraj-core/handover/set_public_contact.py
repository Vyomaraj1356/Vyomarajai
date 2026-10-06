#!/usr/bin/env python3
"""Publish (or inspect) the owner's public contact address — the honest way.

Why this exists
---------------
PR #36 committed a personal email address literally into six public files. GitHub Pages serves this
repository's branch root, so that address became a public web page — exactly what
`sanitize_personal_data.py` exists to prevent. The privacy guard correctly failed the build.

The fix is NOT to hardcode an allowlist and NOT to leave a personal address in tracked files. A
deliberate public contact address is an *owner decision*, so it is made explicitly, once, here:

  python3 set_public_contact.py --check                 offline: report the current contact state
  python3 set_public_contact.py --email owner@x.com --confirm-publish
                                                        write config/public-contact.json with
                                                        owner_approved:true; ONLY then does
                                                        sanitize_personal_data.py allowlist it
  python3 set_public_contact.py                          print the plan and current state (no write)

Safety rules enforced here, not just stated:
  * a placeholder or example address is refused — publishing "[OWNER_EMAIL_REDACTED]" is meaningless;
  * nothing is written without BOTH --email and --confirm-publish (fail-closed);
  * the address is stored in one file (config/public-contact.json), never scattered across pages;
  * no secret, token or mailbox password is read, written or printed — only the public address.

Until the owner runs this with --confirm-publish, the tracked files stay redacted and the guard
stays green. This tool ships the capability and the instructions; it never fakes an approval.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONFIG = ROOT / "config" / "public-contact.json"

# A public contact address is a real, routable mailbox. These are the shapes we accept.
import re
EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Refuse anything that is obviously a placeholder rather than a decision.
PLACEHOLDER_TOKENS = ("redacted", "example.com", "example.org", "placeholder", "changeme",
                      "your-email", "you@", "owner@", "noreply@", "no-reply@", "test@", "@test",
                      "tbd", "todo", "xxx", "your@", "email@")

SCHEMA = {
    "schema_version": 1,
    "purpose": "Owner-approved public contact address. Read by sanitize_personal_data.allowed_emails().",
    "configured": False,
    "owner_approved": False,
    "email": None,
    "approved_at_utc": None,
    "note": "Written only by set_public_contact.py --email <addr> --confirm-publish.",
}


def is_placeholder(address: str) -> bool:
    low = address.lower()
    return any(tok in low for tok in PLACEHOLDER_TOKENS)


def current_state() -> dict:
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(SCHEMA)
    if not isinstance(data, dict):
        return dict(SCHEMA)
    return data


def check() -> int:
    state = current_state()
    configured = state.get("configured") is True
    approved = state.get("owner_approved") is True
    address = state.get("email")
    valid = isinstance(address, str) and bool(EMAIL_RX.fullmatch(address.strip())) and not is_placeholder(address)
    print(json.dumps({
        "config_file": str(CONFIG.relative_to(ROOT)),
        "configured": configured,
        "owner_approved": approved,
        "email_present_and_valid": valid,
        "email": (address[:3] + "…" + address[-12:]) if valid else None,   # partially masked
        "allowlist_active": bool(configured and approved and valid),
    }, indent=2))
    if configured and approved and not valid:
        print("FAIL: contact is marked approved but the address is missing or a placeholder.", file=sys.stderr)
        return 1
    if valid and not (configured and approved):
        print("NOTE: an address is present but not owner_approved; it will NOT be allowlisted.", file=sys.stderr)
    return 0


def publish(address: str) -> int:
    address = address.strip()
    if not EMAIL_RX.fullmatch(address):
        print(f"FAIL: {address!r} is not a well-formed email address.", file=sys.stderr)
        return 2
    if is_placeholder(address):
        print(f"FAIL: {address!r} looks like a placeholder, not a real contact decision.", file=sys.stderr)
        return 2
    record = {
        "schema_version": 1,
        "purpose": SCHEMA["purpose"],
        "configured": True,
        "owner_approved": True,
        "email": address,
        "approved_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": SCHEMA["note"],
    }
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {CONFIG.relative_to(ROOT)} — owner_approved:true for {address[:3]}…{address[-12:]}")
    print("next: run `python3 ops/vyomaraj-core/handover/sanitize_personal_data.py --check` to confirm "
          "the address is now allowlisted, then place it on the page where visitors need it.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="offline: report the current contact state")
    ap.add_argument("--email", help="the public contact address to publish")
    ap.add_argument("--confirm-publish", action="store_true",
                    help="required with --email; records owner_approved:true")
    args = ap.parse_args()

    if args.check:
        return check()
    if args.email and not args.confirm_publish:
        print("FAIL: --email requires --confirm-publish. Nothing was written.", file=sys.stderr)
        return 2
    if args.confirm_publish and not args.email:
        print("FAIL: --confirm-publish requires --email <address>. Nothing was written.", file=sys.stderr)
        return 2
    if args.email and args.confirm_publish:
        return publish(args.email)

    # No action requested: print the plan and the current state, write nothing.
    state = current_state()
    print("Public contact address — current state and how to change it")
    print("=" * 60)
    print(json.dumps({
        "config_file": str(CONFIG.relative_to(ROOT)),
        "configured": state.get("configured"),
        "owner_approved": state.get("owner_approved"),
        "email": state.get("email"),
    }, indent=2))
    print("\nTo publish the real address (owner action):")
    print("  python3 ops/vyomaraj-core/handover/set_public_contact.py "
          "--email you@yourdomain.com --confirm-publish")
    print("Until then the tracked files stay redacted and the privacy guard stays green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
