# Jarvis provider preflight

`ops/jarvis/provider_preflight.py` performs static configuration validation only. It does not send a model request, enable tools, publish content, or infer live connectivity from environment variables.

Run from the repository root:

```sh
python -m ops.jarvis.provider_preflight --json
python -m ops.jarvis.provider_preflight --require-configured
```

Status values:
- `not_configured`: no provider settings are supplied.
- `incomplete`: required settings are missing.
- `invalid`: static validation rejected a supplied setting.
- `configured_unverified`: static validation passed; live provider connectivity remains unverified.

The checker supports the existing OpenAI-compatible chat-completions endpoint format and the official Anthropic Messages endpoint. Anthropic must use HTTPS at `api.anthropic.com/v1/messages`; a gateway is not treated as direct Anthropic connectivity. Remote providers require a key, but its value is never included in output. Local loopback HTTP is permitted only for local OpenAI-compatible endpoints.

Remote OpenAI-compatible requests are restricted to an exact built-in provider-host allowlist (including OpenAI, OpenRouter, Groq, Together, DeepSeek, Mistral, Fireworks, Perplexity, xAI, Google Gemini's OpenAI-compatible endpoint, and Cohere). A custom gateway must be explicitly listed in `JARVIS_LLM_ALLOWED_HOSTS` as comma-separated exact DNS hostnames; wildcards, URL schemes, ports, trailing dots, and IP literals are rejected. This reduces accidental credential exfiltration to arbitrary hosts but does not resolve DNS or replace production egress controls against DNS rebinding and private-network destinations.

`--json` emits machine-readable status and field-presence checks without printing endpoint, model, or API-key values. `--require-configured` returns a nonzero exit code unless static validation passes. Exit code zero for `configured_unverified` means configuration is structurally acceptable only—not that a provider call succeeded.

A live acceptance test remains a separate owner-approved step. It must use an approved secret store, a model authorized for the account, a bounded budget, and sanitized evidence. Runtime, tool execution, publishing, deployment, and disaster-recovery permissions are never granted by this preflight.
