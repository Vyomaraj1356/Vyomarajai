# Vyomaraj + Jarvis LLM harness

## Audit result

The pushed Arena tree contained no runtime LLM provider client or tool-calling harness. The existing Jarvis shell controller maintains a local state file and performs a basic Pages reachability check; model/provider names in its status text are not evidence of an LLM integration. The repository also has no LLM runtime dependency manifest.

A minimal, provider-neutral harness is now available at [`llm_harness.py`](llm_harness.py). It exposes two user-owned role profiles (`vyomaraj` and `jarvis`) over an OpenAI-compatible `/chat/completions` endpoint. It is a standalone CLI; it does not silently change the existing 24x7 controller.

## Safety and scope

- The harness has no tools, shell access, Git access, or automatic action execution.
- It does not copy private model/system prompts. Its short role prompts are user-owned project instructions.
- Prompts and responses are not logged or written to disk by the harness.
- API keys are read from process environment or the ignored local `llm-harness.env`; they are never printed.
- Remote endpoints must use HTTPS. Plain HTTP is permitted only for loopback endpoints such as a local model server. Redirects are refused so authorization headers are not forwarded elsewhere.
- Requests and responses have explicit size limits and a timeout. Provider errors expose only the HTTP status, not the response body.
- It does not load the legacy `jarvis.env` file.

## Existing configuration review required

The repository already tracks `ops/jarvis/jarvis.env` with populated assignments, and the legacy example/controller contain personal-contact text. Their values are intentionally not reproduced here and were not altered by the harness change. An owner should review them before further publication; rotate any real credentials found. The new harness does not consume either legacy file.

## Configure locally

1. Copy `llm-harness.env.example` to `llm-harness.env`. The local file is Git-ignored.
2. Set `JARVIS_LLM_ENDPOINT` to the full trusted OpenAI-compatible URL ending in `/chat/completions`.
3. Set `JARVIS_LLM_MODEL` to a model approved by the owner.
4. Set `JARVIS_LLM_API_KEY` locally for a remote provider. A key may be omitted only for a loopback endpoint.
5. Run with a prompt on standard input:

   ```sh
   printf '%s\n' 'Summarize the supplied verified handoff.' | python3 ops/jarvis/llm_harness.py --role jarvis
   ```

   Use `--role vyomaraj` for the product/control-plane profile. The harness remains disabled until an endpoint and model are configured; no provider or model has been selected in this repository.

Do not paste API keys into chat or commit them. If a provider requires a non-OpenAI-compatible API, add a separately reviewed adapter rather than changing the generic client silently.

## Offline tests

```sh
python3 ops/jarvis/test_llm_harness.py
```

Tests mock the HTTP client and make no network calls.
