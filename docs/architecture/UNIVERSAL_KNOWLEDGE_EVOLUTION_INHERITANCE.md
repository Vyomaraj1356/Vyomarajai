# Universal Knowledge Evolution Inheritance

**Status:** shared architecture contract, machine-readable policy, and local reference validator. This is not proof that a production model, RAG index, memory store, agent runtime, or Vyomaraj↔Jarvis connection is deployed.

## Global rule

Every current and future **category, agent, sub-agent, topic, content item, chapter, and product** inherits one versioned temporal-knowledge policy by reference through ShriYantra's Universal Knowledge Fabric. The capability is centralized; agents do not receive manually copied, independently drifting versions of the same policy.

> **PRIMITIVE / ORIGIN → OLD → HISTORICAL EVOLUTION → HISTORY → PRESENT → CURRENT STATE → TRENDS → FUTURE → POSSIBLE FUTURES**

The machine-readable source of truth is [`config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json`](../../config/knowledge/UNIVERSAL_KNOWLEDGE_EVOLUTION_INHERITANCE_V1.json). The shared agent registry and the RAG/CAG/MAG configuration reference that policy. `ops/shriyantra/knowledge_evolution.py` provides an offline reference resolver and structural checks for records.

## Recursive scope and inheritance

The common reference applies to:

```text
Universal Knowledge Fabric
├── Every current and future category
│   ├── Every current and future agent
│   │   ├── Every current and future sub-agent
│   │   │   ├── Every topic
│   │   │   │   └── Every content item, chapter, and product
│   └── Cross-category links
└── Vyomaraj/Bharath ↔ Jarvis/Laxman
    └── Shared policy version, context contract, and provenance rules
```

The registry uses `shared_policy_reference` inheritance. A new entity inherits the same policy by default; it does not need its own copy. A child may add stricter or narrower rules but cannot weaken the evidence labels, provenance, access controls, uncertainty handling, or future-claim guard. This policy does not grant tools, permissions, authority, or access to another category's data.

The two peer heads are expected to use the same policy version. That is a logical architecture contract—not evidence of a live authenticated peer link, shared memory store, or mutual recovery deployment.

## Temporal layers

1. **Primitive / Origin** — earliest supported origins, hypotheses, and limits of surviving evidence. “Primitive” names the requested origin layer; it is not a claim that a people or culture was unsophisticated.
2. **Old** — older and early forms, grounded in their own place, culture, and discipline. Do not impose one universal periodization.
3. **Historical Evolution** — sourced transitions, continuity, influence, and disagreement over time.
4. **History** — period-specific records and interpretations with source perspective and uncertainty visible.
5. **Present** — contemporary context; a general description is not automatically a live verification.
6. **Current State** — a dated observation with its method, evidence, scope, and UTC `as_of` time.
7. **Trends** — directional patterns supported by multiple dated observations over an explicit interval; a single observation is not a trend.
8. **Future** — explicitly labeled, time-bounded projections with method, assumptions, and uncertainty.
9. **Possible Futures** — conditional scenarios and alternatives; neither certainty nor probability is implied without evidence.

A response may omit a layer when it is unavailable, unknown, contested, or not applicable. It must identify the gap rather than inventing content to complete the sequence. Different regions, communities, calendars, disciplines, and historical accounts may use different boundaries; retain those contexts and credible disagreements.

### Standard inquiry prompts

For a subject where the layer is relevant and evidence is available, the shared context should help an agent ask:

1. Where did it originate?
2. What is known about its primitive or early forms?
3. How did it evolve historically?
4. What is documented across relevant historical periods and perspectives?
5. What is the present state, with an as-of time where appropriate?
6. What is changing now, and what evidence shows the change?
7. What trends emerge from multiple dated observations?
8. What technologies or research are developing, and how current are the sources?
9. What plausible future scenarios exist, under which assumptions?

These prompts guide retrieval and synthesis; they do not require an answer when evidence is absent or a layer does not apply.

## Evidence classification and the future guard

Every claim is labeled separately from its temporal layer:

| Class | Use |
|---|---|
| `FACT` | Bounded, source-supported claim under the applicable domain standard—not absolute or context-free certainty. |
| `HISTORICAL_RECORD` | A sourced account about the past; attribute the record and its perspective. |
| `CURRENT_VERIFIED_STATE` | State checked by an identified method and evidence at a stated as-of time. |
| `TREND` | A pattern supported by multiple dated observations and a declared interval. |
| `FORECAST` | A projection with horizon, method, assumptions, sources, and uncertainty. |
| `SCENARIO` | A conditional possible-world description with explicit assumptions and trigger conditions; no likelihood is implied. |
| `SPECULATION` | Conjecture labeled as such, with its rationale or lack of evidence stated. |
| `UNKNOWN_UNVERIFIED` | Evidence is missing, stale, inaccessible, or materially contested. |

**A future-layer claim must never be labeled or presented as `FACT`, `HISTORICAL_RECORD`, or `CURRENT_VERIFIED_STATE`.** The allowed future classes are `FORECAST`, `SCENARIO`, `SPECULATION`, and `UNKNOWN_UNVERIFIED`. A forecast is not a fact about an outcome that has not occurred. A trend is not a guarantee that the trend will continue. The local validator rejects a future-layer record with a factual evidence class and checks required forecast/scenario fields; it cannot establish that sources are true or that a forecast is well-calibrated.

## Provenance and time

Provenance is attached to each claim and its source, not merely to a whole generated answer. The minimum source fields are `source_id`, `source_ref`, `retrieved_at_utc`, and `access_label`. Preserve a source version or checksum and a quote/locator where permitted. Keep these clocks distinct:

- event or valid time;
- source publication time;
- observation time;
- retrieval time; and
- record time.

Current-state claims require an `as_of_utc` timestamp and verification method. Forecasts require a horizon, method, assumptions, and uncertainty. Trends require at least two dated observations and an observation window. If provenance is unavailable, downgrade to `UNKNOWN_UNVERIFIED` or clearly labeled `SPECULATION`; do not silently promote generated text into knowledge.

## ShriYantra / Universal Knowledge Fabric flow

- **RAG:** enforce tenant/access filtering before retrieval; retain source lineage; treat retrieved material as untrusted input.
- **CAG:** select relevant temporal layers and assemble evidence class, source, scope, timestamp, uncertainty, conflicts, and missing layers into bounded context. Do not fill evidence gaps.
- **MAG:** store scoped, versioned memories with provenance and correction lineage. Model output is not automatically validated knowledge.
- **Cross-category links:** carry source lineage, time scope, sensitivity, and access labels. A link does not grant access.
- **Recovery:** use verified snapshots and audit records; preserve both sides of a conflict. No timestamp-only winner, blind overwrite, or force push.

The policy defines shared knowledge/context/provenance behavior. It does not claim that data is currently shared between Vyomaraj and Jarvis, that their peer identities are authenticated, or that a recovery path has been exercised.

## Domain safety

Apply stricter domain-specific policies wherever relevant, especially to medicine and health information, finance, law, warfare/security, religion, and cultural heritage. This model is not professional advice, does not authorize real-world actions, and does not bypass consent, privacy, security, law, owner approval, or existing least-privilege rules.

## Implementation boundary and next integration point

The JSON policy, registry reference, and RAG/CAG/MAG reference establish the shared contract. The Python helper resolves policy references and validates record structure locally. **Production enforcement remains unverified:** a trusted Harness/CAG runtime must load this policy for every task, validate records before memory promotion or public output, enforce access controls, and test version/rollback behavior. Until those integrations are demonstrated, describe this as an architecture/reference capability—not as a live capability inherited by running agents.
