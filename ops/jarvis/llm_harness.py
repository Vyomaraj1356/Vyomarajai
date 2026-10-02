#!/usr/bin/env python3
"""Small, provider-neutral OpenAI-compatible chat-completions harness.

No tools are exposed to the model. Prompts and responses are not logged or stored.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_PROMPT_CHARS = 16_000
MAX_RESPONSE_BYTES = 1_048_576
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_TOKENS = 512

ROLE_PROMPTS = {
    "vyomaraj": (
        "You are Vyomaraj, a user-owned product and coordination assistant. "
        "Use only the context supplied in this request. Distinguish evidence from "
        "inference, do not claim access to private systems, and never expose secrets. "
        "You have no tools and must not claim to have executed actions."
    ),
    "jarvis": (
        "You are Jarvis, a user-owned orchestration and continuity assistant. "
        "Do not invent unavailable history or convert assumptions into verified facts. "
        "Preserve unresolved issues, distinguish evidence from inference, and never "
        "expose secrets. You have no tools and must not claim to have executed actions."
    ),
}


class HarnessError(Exception):
    """Safe-to-display configuration or provider error (never contains a key)."""


@dataclass(frozen=True)
class Config:
    endpoint: str
    model: str
    api_key: str
    timeout_seconds: int
    max_tokens: int


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, _request, _fp, _code, _message, _headers, _new_url):
        # Do not forward an Authorization header to a redirect destination.
        return None


def _open_request(request: Request, timeout: int):
    return build_opener(_NoRedirect()).open(request, timeout=timeout)


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse simple KEY=VALUE lines; no shell expansion or command execution."""
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError):
        raise HarnessError("Could not read the configured LLM environment file.") from None
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in line:
            raise HarnessError(f"Invalid LLM environment-file syntax on line {number}.")
        name, value = line.split("=", 1)
        name = name.strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
            raise HarnessError(f"Invalid LLM environment variable name on line {number}.")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        values[name] = value
    return values


def read_environment(environment: Mapping[str, str] | None = None) -> dict[str, str]:
    """Load the ignored local env file, then let the process environment win."""
    process_env = dict(os.environ if environment is None else environment)
    configured_path = process_env.get("JARVIS_LLM_ENV_FILE", "").strip()
    env_path = Path(configured_path).expanduser() if configured_path else Path(__file__).with_name("llm-harness.env")
    file_values = _parse_env_file(env_path) if env_path.is_file() else {}
    file_values.update(process_env)
    return file_values


def load_config(environment: Mapping[str, str]) -> Config:
    endpoint = environment.get("JARVIS_LLM_ENDPOINT", "").strip()
    model = environment.get("JARVIS_LLM_MODEL", "").strip()
    api_key = environment.get("JARVIS_LLM_API_KEY", "").strip()
    if not endpoint:
        raise HarnessError("Set JARVIS_LLM_ENDPOINT to a trusted OpenAI-compatible chat-completions URL.")
    if not model:
        raise HarnessError("Set JARVIS_LLM_MODEL to an approved model name.")

    try:
        parsed = urlsplit(endpoint)
        hostname = (parsed.hostname or "").lower()
        parsed.port  # Validate malformed port numbers without echoing the URL.
    except ValueError:
        raise HarnessError("JARVIS_LLM_ENDPOINT is not a valid URL.") from None
    if parsed.scheme not in ("https", "http") or not parsed.netloc or not hostname:
        raise HarnessError("JARVIS_LLM_ENDPOINT must be an HTTPS URL (or local loopback HTTP URL).")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise HarnessError("Do not put credentials, query parameters, or fragments in JARVIS_LLM_ENDPOINT.")
    if not parsed.path.rstrip("/").endswith("/chat/completions"):
        raise HarnessError("JARVIS_LLM_ENDPOINT must end with /chat/completions.")

    loopback = hostname in ("localhost", "127.0.0.1", "::1")
    if parsed.scheme == "http" and not loopback:
        raise HarnessError("Unencrypted HTTP is allowed only for a local loopback LLM endpoint.")
    if not api_key and not loopback:
        raise HarnessError("Set JARVIS_LLM_API_KEY in the local environment for a remote HTTPS provider.")

    timeout_text = environment.get("JARVIS_LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)).strip()
    max_tokens_text = environment.get("JARVIS_LLM_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)).strip()
    try:
        timeout = int(timeout_text)
        max_tokens = int(max_tokens_text)
    except ValueError:
        raise HarnessError("Timeout and token-limit settings must be integers.") from None
    if not 1 <= timeout <= 120:
        raise HarnessError("JARVIS_LLM_TIMEOUT_SECONDS must be between 1 and 120.")
    if not 1 <= max_tokens <= 4096:
        raise HarnessError("JARVIS_LLM_MAX_TOKENS must be between 1 and 4096.")

    return Config(endpoint, model, api_key, timeout, max_tokens)


def complete(prompt: str, role: str, config: Config) -> str:
    if role not in ROLE_PROMPTS:
        raise HarnessError("Unsupported assistant role.")
    if not prompt.strip():
        raise HarnessError("Prompt is empty.")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise HarnessError(f"Prompt exceeds the {MAX_PROMPT_CHARS}-character safety limit.")

    body = json.dumps(
        {
            "model": config.model,
            "messages": [
                {"role": "system", "content": ROLE_PROMPTS[role]},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": config.max_tokens,
            "stream": False,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    request = Request(config.endpoint, data=body, headers=headers, method="POST")

    try:
        with _open_request(request, timeout=config.timeout_seconds) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise HarnessError(f"LLM provider returned HTTP {exc.code}; response body was not logged.") from None
    except (URLError, TimeoutError, OSError):
        raise HarnessError("Could not complete the LLM request; endpoint details and credentials were not logged.") from None

    if len(payload) > MAX_RESPONSE_BYTES:
        raise HarnessError("LLM provider response exceeded the 1 MiB safety limit.")
    try:
        decoded = json.loads(payload.decode("utf-8"))
        content = decoded["choices"][0]["message"]["content"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        raise HarnessError("LLM provider returned an unsupported or malformed response.") from None
    if not isinstance(content, str):
        raise HarnessError("LLM provider response did not contain text content.")
    return content


def main(
    argv: list[str] | None = None,
    *,
    environment: Mapping[str, str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    parser = argparse.ArgumentParser(description="No-tools Vyomaraj/Jarvis LLM harness")
    parser.add_argument("--role", choices=tuple(ROLE_PROMPTS), default="jarvis")
    args = parser.parse_args(argv)
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        config = load_config(read_environment(environment))
        prompt = stdin.read(MAX_PROMPT_CHARS + 1)
        if len(prompt) > MAX_PROMPT_CHARS:
            raise HarnessError(f"Prompt exceeds the {MAX_PROMPT_CHARS}-character safety limit.")
        answer = complete(prompt, args.role, config)
    except HarnessError as exc:
        print(f"LLM harness: {exc}", file=stderr)
        return 2

    stdout.write(answer)
    if not answer.endswith("\n"):
        stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
