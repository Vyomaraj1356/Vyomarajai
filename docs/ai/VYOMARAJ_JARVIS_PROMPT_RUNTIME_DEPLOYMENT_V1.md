# Vyomaraj + Jarvis prompt runtime — deployment and verification

**Status:** implementation prepared on branch `feat/vyomaraj-jarvis-prompt-runtime-v1`; not merged or deployed. Provider configuration remains owner-controlled and unconfigured until an approved endpoint/model/key are supplied through a secret manager or local ignored environment file.

## What this change installs in the repository

- `config/ai/PROMPT_REGISTRY_V1.json`: versioned, user-owned prompt presets with descriptions and allowed roles.
- `ops/jarvis/llm_harness.py`: `--preset <id>` loads a preset from the checked-in registry and sends it as a separate system message after the role contract. The harness still has no tools and cannot execute repository, browser, publishing, finance or deployment actions.
- `ops/jarvis/test_llm_harness.py`: offline tests for registry loading, preset routing and fail-closed behavior.

This does **not** copy ChatGPT private system/developer instructions, hidden internal prompts, private reasoning or inaccessible account data. It implements a project-owned prompt library.

## Local installation

From the repository root, use Python 3.10+ (standard library only):

```sh
python3 -m unittest ops/jarvis/test_llm_harness.py
cp ops/jarvis/llm-harness.env.example ops/jarvis/llm-harness.env
```

Edit `ops/jarvis/llm-harness.env` locally only. Set:
- `JARVIS_LLM_ENDPOINT`: approved HTTPS OpenAI-compatible URL ending in `/chat/completions`; loopback HTTP is allowed for local models only.
- `JARVIS_LLM_MODEL`: exact owner-approved model ID.
- `JARVIS_LLM_API_KEY`: provider key, only in the ignored local file or secret manager.
- Optional timeout/token limits.

Never commit the populated local environment file, paste keys into chat, or put secrets in prompts.

## Invoke presets

Run from the repository root. Examples:

```sh
printf '%s\\n' 'Audit this proposed release against the evidence.' | python3 ops/jarvis/llm_harness.py --role vyomaraj --preset audit
printf '%s\\n' 'Prepare a safe release plan for this branch.' | python3 ops/jarvis/llm_harness.py --role jarvis --preset deploygate
printf '%s\\n' 'Challenge the assumptions in this plan.' | python3 ops/jarvis/llm_harness.py --role jarvis --preset falsify
```

Preset IDs are the keys in `config/ai/PROMPT_REGISTRY_V1.json`. `--role` accepts `vyomaraj` or `jarvis`. Unknown IDs and disallowed role combinations fail before a network request. Omit `--preset` to preserve the prior default behavior.

## Merge and deployment gates

1. Review the proposed pull request and confirm the target branch is `main`.
2. Run the existing offline harness tests and repository-required checks. A passing test does not prove provider connectivity.
3. Merge only through the repository's normal review/protection process.
4. Configure the chosen provider endpoint/model/key in the deployment environment's secret manager. Do not add secret values to GitHub files, workflow YAML, prompts or logs.
5. Run a non-sensitive smoke prompt and verify provider/model, status, latency and cost using provider-side telemetry without logging the prompt or secret.
6. Confirm the deployed commit SHA and rollback path before enabling any consumer.
7. Keep external tools, publishing, financial actions, destructive writes, DR sync and failover disabled until separate capability adapters, server-side authorization, audit, evaluation and owner approval gates are implemented and tested.

## Current production blockers

- No AI provider/model has been selected and configured in the repository.
- This harness is text-only, provider-neutral and has no tool-calling capability.
- Existing repository evidence says primary/DR trees and package manifests were mismatched on the latest documented check; do not use DR sync or failover as part of this prompt-runtime change.
- The repository's latest README reports the main verification workflow gate failing; inspect and repair required checks before treating a PR as production-ready.
- This PR does not deploy GitHub Pages, a backend service, Android, macOS or a 24/7 peer runtime.

## Acceptance criteria

- Registry JSON parses and has a non-empty preset set.
- Offline harness tests pass, including unknown-preset no-network behavior.
- No provider request is made if configuration or preset validation fails.
- No credentials or prompt content are written to logs or the repository.
- PR checks, merge SHA, provider smoke test and deployed runtime identity are recorded separately.


## Expanded preset catalogue update

The prompt registry has been expanded to version 1.1.0 with 88 user-owned presets, including first-principles analysis, black-swan risk review, signal-versus-noise, scenario forecasting, constructive critique, tool discovery, child-focused education and safety, social publishing, collaboration, legal review and output-format aliases. See [Prompt Command Catalogue](./PROMPT_COMMAND_CATALOG_V1_1.md) and [Prompt Operating System](./PROMPT_OPERATING_SYSTEM_VYOMARAJ_JARVIS_v1.0.md).

This update changes reusable text instructions only. It does not enable tool calling, image generation, live search, email sending, automatic legal monitoring, moderation enforcement or social publishing. Validate registry parsing, preset listing, unknown-preset rejection and representative educational/safety presets with offline tests before merging.
