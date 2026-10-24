# Anthropic / Claude adapter — Trustmode

This is an opt-in, provider-specific adapter for the Anthropic Messages API. It is separate from the OpenAI-compatible harness; no endpoint compatibility is assumed.

## Configure in a protected runtime
Set `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL` in the approved secret manager/runtime. Never commit keys, put them in prompt files, or paste them into logs/chat. The adapter does not load `jarvis.env` and does not persist prompts or responses.

## Run a scriptwriter draft
```sh
printf '%s\n' 'Write a 60-second Hindi explainer about rainwater harvesting for families.' | python3 ops/jarvis/anthropic_adapter.py --task scriptwriter
```

Use `--task general` for a generic no-tools task. Input is read from stdin and bounded to 16,000 characters; timeout is bounded to 1–120 seconds. Output is draft content only.

## Trust and release boundary
- The adapter exposes no tools and has no publishing, file-write, deployment or DR actions.
- Redirects are rejected so the API key is not forwarded to another host.
- Provider errors are sanitized; prompts/responses and keys are not logged or stored.
- Code being present does **not** mean a key/model is configured or the provider is live.
- Live acceptance still requires a protected runtime secret, an approved model, a successful smoke test, cost/quota controls, privacy review and timeout/error-path checks.
- Human approval remains required for publishing, legal/financial commitments and other consequential external actions.
