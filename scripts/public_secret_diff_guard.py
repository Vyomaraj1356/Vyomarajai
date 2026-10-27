#!/usr/bin/env python3
"""Fail-closed scan of newly added PR diff lines for common secret material.

This deliberately does not read or scan the working tree or historical blobs.
It emits only path, line number, and rule ID—never the matched text.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import PurePosixPath

SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")

# High-confidence formats only; this is a guardrail, not a complete secret scanner.
SECRET_PATTERNS = (
    ("private-key-header", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("anthropic-key-shape", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("openai-key-shape", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b")),
    ("github-token-shape", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("google-api-key-shape", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("slack-token-shape", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("stripe-live-secret-shape", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
)

SENSITIVE_BASENAMES = frozenset({
    ".env",
    "jarvis.env",
    "llm-harness.env",
    "dr.local.env",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
})

SENSITIVE_SUFFIXES = (".pem", ".p12", ".pfx", ".key", ".keystore")

# High-risk GitHub Actions constructs are blocked when newly introduced into
# workflow/composite-action YAML. This is intentionally conservative; legitimate
# exceptions require a separate security review rather than a silent bypass.
WORKFLOW_RISK_PATTERNS = (
    ("workflow-pull-request-target", re.compile(r"^\s*pull_request_target\s*:", re.IGNORECASE)),
    ("workflow-self-hosted-runner", re.compile(r"^\s*runs-on\s*:\s*.*\bself-hosted\b", re.IGNORECASE)),
    ("workflow-write-all-permissions", re.compile(r"^\s*permissions\s*:\s*write-all\s*(?:#.*)?$", re.IGNORECASE)),
    ("workflow-contents-write", re.compile(r"^\s*contents\s*:\s*write\b", re.IGNORECASE)),
    ("workflow-id-token-write", re.compile(r"^\s*id-token\s*:\s*write\b", re.IGNORECASE)),
    ("workflow-persisted-checkout-credentials", re.compile(r"^\s*persist-credentials\s*:\s*true\b", re.IGNORECASE)),
)


def sensitive_path(path: str) -> bool:
    """Return whether a newly added path looks like a private environment/key file."""
    normalized = path.replace("\\", "/").strip("/")
    lowered = normalized.lower()
    basename = PurePosixPath(lowered).name

    # Explicitly named templates are safe to keep as examples.
    if lowered.endswith((".example", ".sample", ".template", ".dist")):
        return False
    if basename in SENSITIVE_BASENAMES:
        return True
    if basename.startswith(".env.") or ".env." in basename or basename.endswith(".env"):
        return True
    if basename.endswith(SENSITIVE_SUFFIXES):
        return True
    return False


def scan_unified_diff(diff_text: str) -> list[tuple[str, int, str]]:
    """Return redacted findings as (path, new_line_number, rule_id)."""
    findings: list[tuple[str, int, str]] = []
    seen: set[tuple[str, int, str]] = set()
    current_path: str | None = None
    new_line = 0
    path_findings: set[str] = set()

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            current_path = None
            new_line = 0
            continue
        if line.startswith("+++ "):
            marker = line[4:]
            if marker == "/dev/null":
                current_path = None
                continue
            current_path = marker[2:] if marker.startswith("b/") else marker
            if current_path and current_path not in path_findings and sensitive_path(current_path):
                finding = (current_path, 0, "sensitive-file-path")
                if finding not in seen:
                    findings.append(finding)
                    seen.add(finding)
                path_findings.add(current_path)
            continue
        if line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            new_line = int(match.group(1)) - 1 if match else 0
            continue
        if current_path is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            new_line += 1
            added_text = line[1:]
            is_action_yaml = (
                current_path.startswith((".github/workflows/", ".github/actions/"))
                and current_path.lower().endswith((".yml", ".yaml"))
            )
            if is_action_yaml and not added_text.lstrip().startswith("#"):
                for rule_id, pattern in WORKFLOW_RISK_PATTERNS:
                    if pattern.search(added_text):
                        finding = (current_path, new_line, rule_id)
                        if finding not in seen:
                            findings.append(finding)
                            seen.add(finding)
                        break
            for rule_id, pattern in SECRET_PATTERNS:
                if pattern.search(added_text):
                    finding = (current_path, new_line, rule_id)
                    if finding not in seen:
                        findings.append(finding)
                        seen.add(finding)
                    break
        elif line.startswith(" "):
            new_line += 1
        # Deleted lines and diff metadata are deliberately not inspected.

    return findings


def compare_commits(base: str, head: str) -> str:
    """Return a no-context diff of added/changed lines; never shell-expand refs."""
    if not SHA_RE.fullmatch(base) or not SHA_RE.fullmatch(head):
        raise ValueError("base and head must be full 40-character commit SHAs")
    result = subprocess.run(
        [
            "git", "diff", "--no-ext-diff", "--no-color", "--unified=0",
            f"{base}...{head}", "--",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="PR base commit SHA")
    parser.add_argument("--head", required=True, help="PR head commit SHA")
    args = parser.parse_args(argv)

    try:
        diff_text = compare_commits(args.base, args.head)
    except (ValueError, OSError, subprocess.SubprocessError):
        print("BLOCKED: unable to compare the requested commit range safely.", file=sys.stderr)
        return 2

    findings = scan_unified_diff(diff_text)
    if findings:
        print("BLOCKED: possible secret material or private file added; matched values are redacted.")
        for path, line_number, rule_id in findings:
            location = f"{path}:{line_number}" if line_number else path
            print(f"- {location} [{rule_id}]")
        return 1

    print("PASS: no known secret patterns or sensitive file paths found in added diff lines.")
    print("LIMITATION: historical files and unchanged lines were not scanned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
