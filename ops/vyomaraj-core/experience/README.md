# Vyomaraj Experience Engine — integration handover

**Status:** plan-only router + browser studio; external creative tools, live trend discovery, remote agent RPC, and publishing are not configured or invoked.

## What is integrated

- [`EXPERIENCE_ORCHESTRATOR.json`](EXPERIENCE_ORCHESTRATOR.json) is the data-driven routing contract: Vyomaraj → Jarvis → owner-supplied category → tool adapters → human approval.
- [`orchestrator.py`](orchestrator.py) reads that contract plus the canonical agent registry, proposed safety-policy status, and [`CONTENT_CATALOG.json`](CONTENT_CATALOG.json). It validates a job and produces a JSON route manifest without provider calls.
- [`studio.js`](studio.js) and [`studio.css`](studio.css) power the root [`experience-studio.html`](../../../experience-studio.html) page. The browser loads only the allowlisted JSON metadata and builds/downloads a plan locally; it does not send briefs to an LLM.
- [`preview_server.py`](preview_server.py) serves only an allowlist of the studio, public index, and safe registry/config metadata. It intentionally cannot serve `ops/jarvis/jarvis.env`, `devices.json`, or the controller.
- Optional `orchestrator.py --llm-draft` sends the user brief fields and minimal route context to the existing no-tools Jarvis LLM harness. It does not send repository content files. This is opt-in and is not used by the browser. Without that flag, planning is offline.

## Canonical directory and content coverage

- The manifest states **13 main categories, 133 sub-agent slots, 421 product counts**; arithmetic validates.
- Only `EDU`, `ENTERTAINMENT`, `PLATFORM`, `PODCAST`, and `WAR` have partial or named child-roster details. Every other category remains count-only. EDU's S8–S13 range is not mapped to six distinct names; PLATFORM supplies 19 named lanes for 20 slots; count-only entertainment groups remain unnamed. No sub-subagent roster is supplied.
- The content catalog lists 9 food-agent JSON modules, 20 Bhakti-Shakti JSON modules, and 3 Hanuman JSON configuration files by filename. It is not an item-level inventory of all 421 products. Source bodies are not loaded or attached to plans.
- The separately reported readiness figures (394 active-content products, 12 placeholder videos shared, 52 pending products requiring chapters, 5 planned products requiring chapters) remain unreconciled with 421 until the owner confirms overlap/status rules.

## Domain routing

- Direct category-description matches: food → `FOOD`; tourism → `TOUR`; education → `EDU`; non-operational war history → `WAR`.
- Provisional composites requiring owner review: hotel menus → `FOOD` + `TOUR`; temple/heritage → `BHAKTI` + `TOUR`; trend campaigns → `ENTERTAINMENT` + `PLATFORM`.
- Vehicle (car/bike) configurators and fashion visualization have no named specialist category in the canonical roster. They stay at the Vyomaraj/Jarvis planning layer and are marked `owner_mapping_required`; no category or agent name was invented.
- War/arms routing is historical or fictional, non-operational visualization only. No functional weapon design, performance optimization, targeting, or use guidance is in scope.

## Adapter state

The adapter IDs are stable extension points: `image_generation`, `video_generation`, `model_3d_generation`, `animation`, `rendering`, `ar_runtime`, `trend_source`, and `publisher`. Every visual/publishing adapter has `provider: null` and execution disabled. `trend_source` is manual-reference-only. This version has no visual-tool dispatch executor, so it remains plan-only even if an adapter's metadata is later marked configured. Do not enable a provider until the provider, endpoint, authentication handling, rights terms, user approval, safety controls, and a tested adapter implementation are in place.

The LLM harness exists at `ops/jarvis/llm_harness.py`, but no endpoint/model/provider is configured. The legacy Jarvis controller is present but this planner does not invoke it; its heartbeat/device state is not verified. `ops/jarvis/jarvis.env` has populated assignments and requires owner review before publication. Values are intentionally not copied into this handover, the browser, or generated plans. The two Vyomaraj bootstrap scripts remain separate and are not executed here.

## Run and verify

Browser preview, with the safe static allowlist:

```sh
python3 ops/vyomaraj-core/experience/preview_server.py --host 0.0.0.0 --port 4174
```

Plan-only CLI (no network):

```sh
printf '%s\n' '{"title":"Sample menu","domain_id":"food_menu","experience_mode":"3d","brief":"Create an original concept for review."}' \
  | python3 ops/vyomaraj-core/experience/orchestrator.py --output /tmp/experience-plan.json
```

Optional LLM draft (explicit provider call; review data before sending):

```sh
python3 ops/vyomaraj-core/experience/orchestrator.py job.json --llm-draft --llm-role vyomaraj
```

Offline tests:

```sh
python3 ops/vyomaraj-core/experience/test_experience_orchestrator.py
python3 ops/jarvis/test_llm_harness.py
```

The content-safety policy is labeled `proposed_owner_policy_specification_not_a_deployed_filter`. All generated/adapted work requires human review; trend references remain unverified; publishing stays blocked until an authorized adapter is configured.
