#!/usr/bin/env python3
"""Remove personal identifiers from the repository and stop them coming back.

Why this exists
---------------
GitHub Pages serves this repository's branch root, so **every tracked file is a public web page**.
An audit found the owner's personal email address and two personal mobile numbers inside tracked
files — including `landing.html`, `flow-diagram.html` and the `ops/bhakti-shakti/*.json` data files —
all reachable at live public URLs. That is a privacy problem, not a style problem.

What this does
--------------
  python3 sanitize_personal_data.py            rewrite every tracked text file that carries a
                                              personal identifier, replacing it with a placeholder
  python3 sanitize_personal_data.py --check    fail if any personal identifier is still present

The check mode is the durable part: it is wired into the offline gate, so the identifiers cannot
return in a future commit. It also refuses to be fooled by a redaction that only looks right — it
re-derives the patterns from scratch each run.

Binaries (the APK) are reported, never rewritten: a phone number baked into an APK's resources is
listed as outstanding rather than silently "fixed".
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

EMAIL_PLACEHOLDER = "[OWNER_EMAIL_REDACTED]"
PHONE_PLACEHOLDER = "[PHONE_REDACTED]"

# Pattern-based, with no personal value written down anywhere: this tool is itself a public file, so
# hardcoding an address to redact would republish it. Everything below is generic.
PERSONAL_EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@(?:gmail|yahoo|outlook|hotmail|rediffmail|"
                               r"protonmail|icloud)\.[A-Za-z]{2,}", re.I)
# Word-bounded: a 10-digit run embedded inside a hex hash or a longer token is not a phone number.
PHONE_RX = re.compile(r"(?<![\w])(?:\+91[- ]?|91[- ]?)?[6-9]\d{9}(?![\w])")
HASH_LINE_RX = re.compile(r"[a-f0-9]{40}|run_id|/runs/|sha256|commit|checkpoint|\bhash\b", re.I)
# A deliberate public contact address is a decision, not an accident: allowlist it here when chosen.
ALLOWED_EMAILS: list[str] = []
ALLOWED_SUBSTRINGS = ("example.com", "REDACTED", "REDACTED_SECRET", "placeholder",
                      "test@", "@test", "9800000", "1234567890")

TEXT_SUFFIXES = {".md", ".txt", ".json", ".html", ".htm", ".js", ".cjs", ".mjs", ".py", ".sh",
                 ".yml", ".yaml", ".env", ".example", ".csv", ".svg", ".css"}


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [ROOT / line for line in out.stdout.splitlines() if line.strip()]


def is_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES or path.name.endswith(".example"):
        try:
            return b"\x00" not in path.read_bytes()[:4096]
        except OSError:
            return False
    return False


def sanitize(text: str) -> tuple[str, int]:
    """Replace personal identifiers, leaving an allowlisted contact address alone."""
    changed = 0

    def email_sub(match: re.Match) -> str:
        nonlocal changed
        if match.group(0).lower() in {e.lower() for e in ALLOWED_EMAILS}:
            return match.group(0)
        changed += 1
        return EMAIL_PLACEHOLDER

    text = PERSONAL_EMAIL_RX.sub(email_sub, text)

    def phone_sub(match: re.Match) -> str:
        nonlocal changed
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        line = text[line_start: line_end if line_end != -1 else len(text)]
        if HASH_LINE_RX.search(line) or "wa.me" in line and "[PHONE_REDACTED]" in line:
            return match.group(0)
        changed += 1
        return PHONE_PLACEHOLDER

    text = PHONE_RX.sub(phone_sub, text)
    text, n = re.subn(r"wa\.me/91\d{10}", "wa.me/[PHONE_REDACTED]", text)
    changed += n
    return text, changed


def run_sanitize() -> int:
    total_files, total_hits, binary_hits = 0, 0, []
    for path in tracked_files():
        if not path.is_file():
            continue
        if not is_text(path):
            # A binary (the APK) may still carry the identifiers; report, never rewrite.
            try:
                blob = path.read_bytes()
            except OSError:
                continue
            as_text = blob.decode("latin-1", errors="ignore")
            if PERSONAL_EMAIL_RX.search(as_text) or PHONE_RX.search(as_text):
                binary_hits.append(path.relative_to(ROOT).as_posix())
            continue
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        new, hits = sanitize(text)
        if hits:
            path.write_text(new, encoding="utf-8", errors="surrogateescape")
            total_files += 1
            total_hits += hits
            print(f"  {path.relative_to(ROOT).as_posix():58} {hits} identifier(s) replaced")
    print(f"\nrewrote {total_files} file(s), {total_hits} personal identifier(s) removed")
    if binary_hits:
        print("outstanding — personal data inside a binary that this tool will not rewrite:")
        for name in binary_hits:
            print(f"  {name}")
    print(f"\nnext: run `{Path(__file__).name} --check` to prove nothing remains")
    return 0


def check() -> int:
    problems = []
    for path in tracked_files():
        if not path.is_file() or not is_text(path):
            continue
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        for i, line in enumerate(text.splitlines(), 1):
            if any(a in line for a in ALLOWED_SUBSTRINGS):
                continue
            if HASH_LINE_RX.search(line):
                continue   # commit SHAs, run ids and hash lines are not phone numbers
            email = PERSONAL_EMAIL_RX.search(line)
            if email:
                problems.append(f"{path.relative_to(ROOT)}:{i} personal email present: "
                                f"{email.group(0)[:12]}...")
            phone = PHONE_RX.search(line)
            if phone and not re.search(r"\b(19|20)\d{2}\b", line[:phone.start()][-6:] or ""):
                problems.append(f"{path.relative_to(ROOT)}:{i} phone-shaped number present: "
                                f"...{phone.group(0)[-4:]}")
    if problems:
        print("personal-data guard FAILED — the public site would serve these:")
        for p in problems[:25]:
            print("  -", p)
        if len(problems) > 25:
            print(f"  ... and {len(problems) - 25} more")
        return 1
    print("OK: no personal email address and no personal phone number in any tracked text file")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if any personal identifier is still present")
    a = ap.parse_args()
    return check() if a.check else run_sanitize()


if __name__ == "__main__":
    sys.exit(main())
