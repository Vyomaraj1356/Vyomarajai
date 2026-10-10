# Vyomaraj + Jarvis LLM harness

## Audit result

The repository has a minimal, provider-neutral, no-tools harness at [`llm_harness.py`](llm_harness.py). It exposes two user-owned role profiles (`vyomaraj` and `jarvis`) over an OpenAI-compatible `/chat/completions` endpoint. It is also an optional, explicit text-draft stage in the plan-only experience orchestrator. The revised prompts require requested English/Hindi/Hinglish, owner/policy authority, evidence/inference separation, untrusted retrieved data, and no fabricated heartbeats or execution.

The former Jarvis shell controller printed simulated device shifts and unsupported “live” states. It has been replaced by a wrapper around [`heartbeat_monitor.py`](heartbeat_monitor.py), a bounded read-only endpoint reachability probe. Empty example URLs report `not_configured`; a reachable `/healthz` endpoint still does not prove authenticated peer health, a live AI agent, or production DR. See [`README.md`](README.md) for local configuration.

## Safety and scope

- The harness has no tools, shell access, Git access, or automatic action execution.
- It does not copy private model/system prompts. Its short role prompts are user-owned project instructions.
- Prompts and responses are not logged or written to disk by the harness.
- API keys are read from process environment or the ignored local `llm-harness.env`; they are never printed.
- Remote endpoints must use HTTPS. Plain HTTP is permitted only for loopback endpoints such as a local model server. Redirects are refused so authorization headers are not forwarded elsewhere.
- Requests and responses have explicit size limits and a timeout. Provider errors expose only the HTTP status, not the response body.
- It does not load the legacy `jarvis.env` file.

## Existing configuration review required

The populated legacy `ops/jarvis/jarvis.env` file has been removed from this branch's working tree and added to `.gitignore`; the harness does not consume it. This does not erase earlier Git history. An owner must review historical revisions for credentials or personal data and rotate any real credentials found. The legacy example/controller should also be reviewed before further publication.


## Named prompt presets

The versioned user-owned preset registry lives at `config/ai/PROMPT_REGISTRY_V1.json`. The harness accepts an optional preset ID; the role contract remains active and the preset is sent as a separate system message.

```sh
printf '%s\\n' 'Audit this proposal and label facts versus assumptions.' | python3 ops/jarvis/llm_harness.py --role vyomaraj --preset truthmode
printf '%s\\n' 'Prepare a release plan with rollback and acceptance gates.' | python3 ops/jarvis/llm_harness.py --role jarvis --preset deploygate
```

Use `python3 -m unittest ops/jarvis/test_llm_harness.py` for offline tests. Presets are project-authored reusable instructions, not ChatGPT private system prompts or hidden reasoning. This feature does not add tool calling or execute actions. Provider configuration and production deployment remain separate owner-controlled steps; see [prompt runtime deployment gates](../../docs/ai/VYOMARAJ_JARVIS_PROMPT_RUNTIME_DEPLOYMENT_V1.md).

## Discover and use prompts

List available prompt presets without configuring a provider or making a network request:

```sh
python3 ops/jarvis/llm_harness.py --list-presets
```

Use a listed preset with `--preset <id>` and choose `--role vyomaraj` or `--role jarvis`. Example:

```sh
printf '%s\\n' 'Separate facts from assumptions and list missing evidence.' | python3 ops/jarvis/llm_harness.py --role jarvis --preset truthmode
```

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

## Experience-engine integration

The plan-only router and browser workspace live under [`ops/vyomaraj-core/experience/`](../vyomaraj-core/experience/), with the linked page at [`experience-studio.html`](../../experience-studio.html). They read the canonical agent registry, proposed safety-policy status, and a metadata-only content-pack catalog. The browser does not call this LLM harness or send briefs to a provider. For a local preview, use `python3 ops/vyomaraj-core/experience/preview_server.py --host 0.0.0.0 --port 4174`; its strict file allowlist does not serve the Jarvis environment, device manifest, or controller.

A local route plan can be built without any network access:

```sh
printf '%s\n' '{"title":"Sample menu","domain_id":"food_menu","experience_mode":"3d","brief":"Create an original concept for review."}' | python3 ops/vyomaraj-core/experience/orchestrator.py --output /tmp/experience-plan.json
```

For an optional LLM text draft, explicitly add `--llm-draft` (and optionally `--llm-role jarvis`). That action sends the job brief and minimal route context to the locally configured provider through the no-tools harness; repository content bodies are not included. It does not invoke image/video/3D tools, publish, or make the draft release-ready. Review provider privacy and terms before sending any brief; generated text is marked unreviewed. No provider is configured by this repository.

Offline router tests:

```sh
python3 ops/vyomaraj-core/experience/test_experience_orchestrator.py
```

## Offline LLM harness tests

```sh
python3 ops/jarvis/test_llm_harness.py
```

Tests mock the HTTP client and make no network calls.
