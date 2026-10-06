#!/usr/bin/env python3
"""Vyomaraj/Bharath + Jarvis/Laxman mailbox adapter.

Safe default: read/classify only. Sending requires MAILBOX_AUTOREPLY_ENABLED=true
and MAILBOX_DRY_RUN=false in the deployment secret/config environment.
"""

import email
import imaplib
import os
import re
from email.header import decode_header

OWNER = os.getenv("VYOMARAJ_OWNER_MAILBOX", "Vyomarajai@gmail.com")
HOST = os.getenv("MAILBOX_IMAP_HOST", "imap.gmail.com")
PORT = int(os.getenv("MAILBOX_IMAP_PORT", "993"))
USER = os.getenv("MAILBOX_USERNAME", OWNER)
PASSWORD = os.getenv("VYOMARAJ_GMAIL_APP_PASSWORD", "")
AUTOREPLY = os.getenv("MAILBOX_AUTOREPLY_ENABLED", "false").lower() == "true"
DRY_RUN = os.getenv("MAILBOX_DRY_RUN", "true").lower() == "true"

RULES = {
    "finance": re.compile(r"\b(invoice|payment|payout|bank|money|refund|gst|tax)\b", re.I),
    "legal": re.compile(r"\b(legal|lawyer|court|notice|copyright|trademark|dispute)\b", re.I),
    "security": re.compile(r"\b(password|otp|token|credential|hacked|takeover)\b", re.I),
    "abuse": re.compile(r"\b(fuck|shit|bitch|idiot|moron|stupid)\b", re.I),
}

def classify(text):
    for category, pattern in RULES.items():
        if pattern.search(text):
            return category
    return "normal"

def decode_subject(value):
    parts = []
    for chunk, enc in decode_header(value or ""):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts)

def run_once():
    if not PASSWORD:
        raise RuntimeError("Mailbox password/app-password is not configured in the runtime secret store")
    with imaplib.IMAP4_SSL(HOST, PORT) as box:
        box.login(USER, PASSWORD)
        box.select("INBOX")
        status, data = box.search(None, "UNSEEN")
        if status != "OK":
            return
        for msg_id in data[0].split():
            status, raw = box.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(raw[0][1])
            subject = decode_subject(msg.get("Subject"))
            sender = msg.get("From", "unknown")
            body = msg.get_payload(decode=True)
            text = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body)
            category = classify(subject + "\n" + text)
            print({"sender": sender, "subject": subject, "category": category})
            if category in {"finance", "legal", "security"}:
                print("OWNER_ESCALATION_REQUIRED")
            elif category == "abuse":
                print("QUARANTINE_NO_REPLY")
            else:
                print("ROUTE_TO_BHARATH_AND_LAXMAN")
        box.logout()

if __name__ == "__main__":
    if AUTOREPLY and DRY_RUN:
        raise RuntimeError("Unsafe configuration: AUTOREPLY enabled while DRY_RUN=true")
    run_once()
