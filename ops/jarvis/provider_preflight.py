"""Static provider configuration preflight. Never sends a request or prints secret values."""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
from urllib.parse import urlsplit
from typing import Mapping


SUPPORTED_PROVIDERS = {"openai_compatible", "anthropic"}
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_TOKENS = 1024
DEFAULT_ALLOWED_HOSTS = frozenset({
    "api.anthropic.com",
    "api.openai.com",
    "openrouter.ai",
    "api.groq.com",
    "api.together.xyz",
    "api.deepseek.com",
    "api.mistral.ai",
    "api.fireworks.ai",
    "api.perplexity.ai",
    "api.x.ai",
    "generativelanguage.googleapis.com",
    "api.cohere.com",
})


def _trusted_remote_hosts(environment: Mapping[str, str]) -> set[str]:
    """Return exact trusted hostnames; reject wildcard, URL, port, and IP entries."""
    hosts = set(DEFAULT_ALLOWED_HOSTS)
    configured = environment.get("JARVIS_LLM_ALLOWED_HOSTS", "")
    if not configured.strip():
        return hosts
    for entry in configured.split(","):
        host = entry.strip().lower()
        if (
            not host
            or host.endswith(".")
            or "*" in host
            or "/" in host
            or ":" in host
            or "@" in host
            or any(ch.isspace() for ch in host)
            or not re.fullmatch(r"(?=.{1,253}$)[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*", host)
        ):
            raise ValueError
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise ValueError
        hosts.add(host)
    return hosts


def inspect_environment(environment: Mapping[str, str]) -> dict[str, object]:
    """Inspect provider settings without network I/O or disclosure of configuration values."""
    provider = environment.get("JARVIS_LLM_PROVIDER", "openai_compatible").strip().lower()
    endpoint = environment.get("JARVIS_LLM_ENDPOINT", "").strip()
    model = environment.get("JARVIS_LLM_MODEL", "").strip()
    api_key = environment.get("JARVIS_LLM_API_KEY", "").strip()
    timeout_text = environment.get("JARVIS_LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)).strip()
    max_tokens_text = environment.get("JARVIS_LLM_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)).strip()

    supplied = any((
        endpoint,
        model,
        api_key,
        environment.get("JARVIS_LLM_PROVIDER", "").strip(),
        environment.get("JARVIS_LLM_ALLOWED_HOSTS", "").strip(),
    ))
    checks = {
        "provider_supported": provider in SUPPORTED_PROVIDERS,
        "endpoint_valid": False,
        "model_present": bool(model),
        "api_key_present": bool(api_key),
        "timeout_valid": False,
        "max_tokens_valid": False,
    }
    issues: list[str] = []
    try:
        trusted_hosts = _trusted_remote_hosts(environment)
    except ValueError:
        trusted_hosts = set()
        issues.append("JARVIS_LLM_ALLOWED_HOSTS must contain exact DNS hostnames only.")

    if not supplied:
        return {
            "status": "not_configured",
            "checks": checks,
            "request_sent": False,
            "issues": [],
        }

    if provider not in SUPPORTED_PROVIDERS:
        issues.append("JARVIS_LLM_PROVIDER must be openai_compatible or anthropic.")

    parsed = None
    hostname = ""
    if endpoint:
        # Only retain a parsed endpoint after all URL components (including port)
        # have validated. urlsplit() alone accepts malformed ports; allowing a
        # later hostname/path check to set endpoint_valid=True would be misleading.
        try:
            candidate = urlsplit(endpoint)
            candidate_hostname = (candidate.hostname or "").lower()
            candidate.port  # validate malformed ports without echoing the URL
        except ValueError:
            issues.append("JARVIS_LLM_ENDPOINT is not a valid URL.")
        else:
            parsed = candidate
            hostname = candidate_hostname

        if parsed is not None:
            if parsed.scheme not in ("https", "http") or not parsed.netloc or not hostname:
                issues.append("JARVIS_LLM_ENDPOINT must be an HTTPS URL, except local loopback HTTP.")
            elif parsed.username or parsed.password or parsed.query or parsed.fragment:
                issues.append("JARVIS_LLM_ENDPOINT must not contain credentials, query parameters, or fragments.")
            else:
                loopback = hostname in LOOPBACK_HOSTS
                host_safe = True
                if not loopback:
                    # Exact-host allowlisting prevents sending API keys to arbitrary
                    # configured domains. DNS names are not resolved here; production
                    # egress policy must also prevent DNS rebinding/private destinations.
                    try:
                        ipaddress.ip_address(hostname)
                    except ValueError:
                        if re.fullmatch(r"(?:[0-9.]+|0x[0-9a-f.]+)", hostname, re.IGNORECASE):
                            host_safe = False
                            issues.append("JARVIS_LLM_ENDPOINT must not use a noncanonical numeric host.")
                    else:
                        host_safe = False
                        issues.append("Remote IP-literal endpoints are not allowed.")
                    if hostname.endswith("."):
                        host_safe = False
                        issues.append("JARVIS_LLM_ENDPOINT must use a canonical hostname without a trailing dot.")
                    if hostname not in trusted_hosts:
                        host_safe = False
                        issues.append("JARVIS_LLM_ENDPOINT host is not trusted; use a built-in provider host or exact JARVIS_LLM_ALLOWED_HOSTS entry.")
                if parsed.scheme == "http" and not loopback:
                    issues.append("Unencrypted HTTP is allowed only for a local loopback endpoint.")
                if host_safe and provider == "anthropic":
                    if (
                        parsed.scheme == "https"
                        and hostname == "api.anthropic.com"
                        and parsed.path == "/v1/messages"
                        and parsed.port in (None, 443)
                    ):
                        checks["endpoint_valid"] = True
                    else:
                        issues.append(
                            "Anthropic requires https://api.anthropic.com/v1/messages on the default HTTPS port."
                        )
                elif host_safe and provider == "openai_compatible":
                    if parsed.path.rstrip("/").endswith("/chat/completions"):
                        checks["endpoint_valid"] = True
                    else:
                        issues.append("OpenAI-compatible endpoints must end with /chat/completions.")
    else:
        issues.append("JARVIS_LLM_ENDPOINT is missing.")

    if not model:
        issues.append("JARVIS_LLM_MODEL is missing.")
    elif len(model) > 160 or any(ord(ch) < 32 or ord(ch) == 127 for ch in model):
        issues.append("JARVIS_LLM_MODEL is invalid.")
        checks["model_present"] = False

    if api_key and any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in api_key):
        issues.append("JARVIS_LLM_API_KEY contains whitespace or control characters.")
        checks["api_key_present"] = False

    if endpoint and parsed is not None and hostname and hostname not in LOOPBACK_HOSTS and not api_key:
        issues.append("JARVIS_LLM_API_KEY is required for remote providers.")

    try:
        timeout = int(timeout_text)
        checks["timeout_valid"] = 1 <= timeout <= 120
    except ValueError:
        checks["timeout_valid"] = False
    if not checks["timeout_valid"]:
        issues.append("JARVIS_LLM_TIMEOUT_SECONDS must be an integer between 1 and 120.")

    try:
        max_tokens = int(max_tokens_text)
        checks["max_tokens_valid"] = 1 <= max_tokens <= 4096
    except ValueError:
        checks["max_tokens_valid"] = False
    if not checks["max_tokens_valid"]:
        issues.append("JARVIS_LLM_MAX_TOKENS must be an integer between 1 and 4096.")

    if issues:
        # Missing required values are incomplete; malformed supplied values are invalid.
        missing_only = all(
            issue.endswith("is missing.")
            or issue == "JARVIS_LLM_API_KEY is required for remote providers."
            for issue in issues
        )
        status = "incomplete" if missing_only else "invalid"
    else:
        status = "configured_unverified"

    return {
        "status": status,
        "checks": checks,
        "request_sent": False,
        "issues": issues,
    }


def main(argv: list[str] | None = None, environment: Mapping[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable status only")
    parser.add_argument(
        "--require-configured",
        action="store_true",
        help="return a nonzero exit code unless static validation passes",
    )
    args = parser.parse_args(argv)

    if environment is None:
        try:
            from ops.jarvis.llm_harness import read_environment
            current = read_environment()
        except (ImportError, OSError, ValueError):
            current = dict(os.environ)
    else:
        current = dict(environment)

    result = inspect_environment(current)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"status={result['status']}")
        print("request_sent=false")
        for issue in result["issues"]:
            print(f"issue={issue}")
    if args.require_configured and result["status"] != "configured_unverified":
        return 3
    return 0 if result["status"] in ("not_configured", "configured_unverified") else 2


if __name__ == "__main__":
    raise SystemExit(main())
