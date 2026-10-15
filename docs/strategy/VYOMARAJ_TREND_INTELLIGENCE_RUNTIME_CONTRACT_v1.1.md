# Vyomaraj Trend Intelligence and Prompt Vault — runtime contract v1.1

**Status:** Proposed code and local verification contract. The included intake utility is implemented as an offline-first queue processor; no social, model, or publishing integration is claimed by this document.

## Purpose

Make Vyomaraj the trend-intelligence orchestrator and Jarvis/Laxman the scheduled-job, continuity, monitoring and recovery peer. Capture approved public trend signals and prompt candidates, test reusable techniques, produce original content, and learn from authorized analytics. Keep every integration's actual status distinct from its planned status.

## Safe intake utility

Script: `ops/vyomaraj-core/trends/trend_intake.py`
Tests: `ops/vyomaraj-core/trends/test_trend_intake.py`
Prompt alias seed: `ops/vyomaraj-core/trends/prompt_alias_seed.json`
Alias validator: `ops/vyomaraj-core/trends/prompt_alias_registry.py`

The utility accepts JSONL records prepared by an authorized connector. It validates timestamps and score ranges, assigns a stable deduplication ID, calculates an explainable 0–100 priority score from seven 0–5 dimensions, records source authorization/terms flags, escalates recognized high-risk topics, and creates a review queue. It has no network, browser, provider, shell, or publishing capability. It treats all captured content as untrusted data.

Default operation is dry-run. Use `--write` only when the operator deliberately authorizes appending to the local review queue. Corrupt existing queues fail closed. Records without confirmed access/terms are held. Recognized medical, financial, legal, minors, privacy, tragedy, allegations, misinformation, copyright, harassment, or election flags require human review. Risk classification is a safeguard, not a complete safety classifier.

Example:

```sh
python3 ops/vyomaraj-core/trends/trend_intake.py \
  --input /path/to/authorized-adapter-output.jsonl
# Inspect report; only then explicitly write:
python3 ops/vyomaraj-core/trends/trend_intake.py \
  --input /path/to/authorized-adapter-output.jsonl \
  --output var/trend-review-queue.jsonl --write
python3 -m unittest discover -s ops/vyomaraj-core/trends -p 'test_*.py' -v
```

Input schema (one JSON object per line): required `source_url`, timezone-aware ISO-8601 `observed_at`, `topic`, `summary`, `category`, `language`; optional `region`, `adapter`, `terms_checked`, `access_authorized`, `risk_flags`, and `scores`. Scores use momentum, audience_fit, original_value, shelf_life, competition_opportunity, monetization_fit, confidence; each is 0–5. The source connector must honestly set the two authorization booleans. They are attestations, not independently verified facts.

## Prompt discovery and inheritance

Maintain a separate versioned prompt vault with:
- stable prompt ID, title, owner/source, source URL, captured time, usage/license notes;
- target platform/model/version, task, agent family, input/output schema and required tools;
- original content or permitted excerpt, parent prompt, changes and provenance;
- test cases, baseline, quality/safety scores, cost/latency and evaluator evidence;
- lifecycle state `DISCOVERED → REVIEWED → TESTED → APPROVED → REGISTERED → RUNTIME-VERIFIED`.

Do not infer that a prompt is an executable slash command. Aliases such as `/truthmode`, `/firstprinciple`, `/alt3`, `/redteam`, `/mindmap`, `/marketingprompts`, `/education`, `/sales` and `/xray` should map to explicit registered presets or be marked unsupported. Never harvest hidden/private system prompts, bypass authentication, or treat retrieved text as higher-priority instructions. Inheritance copies tested behavior and metadata, not credentials, access scopes, approvals, or root authority.

## Daily operation and escalation

1. **Discover (scheduled):** approved platform APIs, public feeds and authorized analytics. Record timestamps, region/language, metric definition, source terms, API/version, freshness and provenance.
2. **Deduplicate and score:** compare equivalent time windows; consider momentum, audience fit, originality, shelf life, saturation, monetization fit, effort, risk and confidence.
3. **Research and produce:** source-backed brief, original script, appropriate media formats, localization and accessibility outputs.
4. **Verify:** factual claims, rights, privacy, safety, disclosure, platform-specific requirements, misleading metadata and age suitability.
5. **Approve and publish:** draft-first. Only explicitly approved official connectors may publish; require owner/policy approval according to risk and channel policy. Maintain idempotency keys, receipts, bounded retries and takedown path.
6. **Measure and learn:** authorized views/reach, watch time/retention, saves/shares, meaningful comments, returning audience, subscriptions, conversions, net revenue, costs, corrections and incidents. Do not optimize only for views; never buy engagement or manufacture comments.
7. **Report risks:** Vyomaraj/Jarvis may automatically mitigate reversible, pre-authorized low-risk issues (pause a faulty job, quarantine a suspicious prompt, retry within limits, switch to a previously approved adapter, open a finding). If permissions, evidence, legal interpretation, rights, identity, cost limits, production integrity or reversibility are unclear, fail closed and alert the owner with evidence, impact, options and a proposed safe action.

## Risk policy

- **Auto-mitigate only** if the action is explicitly allowlisted, reversible, bounded, logged, within cost limits, and does not expand access or publish externally.
- **Owner attention required** for suspected credential exposure, legal/privacy uncertainty, rights disputes, serious misinformation, high-risk health/finance/legal content, child safety, unexplained spending, provider policy changes affecting compliance, production write failures, split-brain, failed restore, permission changes, new providers/scopes, or any action that is destructive, irreversible, externally binding or materially costly.
- Do not silently mark an issue resolved. Record detection, severity, evidence, mitigation attempted, outcome, residual risk, owner decision and closure proof.

## Provider/tool capability inventory

Track each exact product/API separately: OpenAI API vs ChatGPT app vs Codex; Anthropic API vs Claude app/Claude Code; Gemini API vs consumer app; Meta AI consumer experience vs Meta developer APIs and Instagram/Facebook publishing/analytics; Arena AI; image/video/audio/editing products; search/research; transcription/translation; official social analytics/publishing APIs; storage, queue, scheduler and observability.

Required fields: `provider`, `product`, `capability`, `owner`, `environment`, `auth_scope_reference` (never secret value), `terms_reviewed_at`, `status` (`proposed|configured|connected|smoke-tested|runtime-verified|blocked|retired`), `last_verified_at`, `evidence_url_or_artifact`, `cost_limit`, `fallback`, `data_retention`, `risk_owner`. Mark an integration active only after an authenticated capability-specific test passes. Never store API keys in this inventory or repository.

## 3D / 4D / 5D claims

Treat 3D, 4D and 5D as explicit product/workflow definitions, not proof of a capability. Record the required input/output, coordinate/time/interaction semantics, target runtime, file formats, rendering or simulation engine, validation tests and device requirements. A mode label or static plan does not prove 3D asset generation, temporal simulation, multi-axis reasoning or a deployable mobile experience. Each mode needs a separate capability test and artifact.

## Current known limitations

- The existing LLM harness is no-tools and provider-neutral only for OpenAI-compatible chat-completions endpoints; it does not automatically connect consumer apps or proprietary APIs.
- The versioned 88-preset project registry and `--preset`/`--list-presets` harness support are now merged and offline-tested. No provider endpoint/model/key is configured, so live AI completion and consumer-app integrations remain NOT PROVEN.
- This intake script is not a scheduler or social connector. No social platform is contacted and no post/comment/subscription is made.
- Prompt preset selection is implemented in the no-tools harness, but actual completions remain unavailable until the owner configures a supported endpoint/model and required credentials. It does not provide tool calling or connect consumer apps.
- No credentials, model selection, provider connection, recurring trend job, external publishing or production failover is configured by this change.
- Local JSONL storage is not a shared production database or disaster-recovery system. Back up and test recovery before production use.

## Acceptance checklist

- [ ] Unit tests pass offline.
- [ ] Approved connector emits schema-valid records and proves terms/access.
- [ ] Scheduler uses a durable queue, bounded retries, checkpointing, alerting and idempotency.
- [ ] Prompt candidates have provenance, licensing review and regression tests.
- [ ] Provider adapters pass authenticated tests in a protected environment.
- [ ] At least one original campaign passes facts, rights, safety and accessibility review.
- [ ] Analytics are authorized and metric definitions are documented.
- [ ] Owner-approved draft-to-publish flow is tested with receipts and rollback/takedown procedure.
- [ ] DR restore and runtime parity are independently verified before claiming resilience.
