# Vyomaraj Experience Engine — integration handover

**Status:** plan/router + browser studio; multimodal capability inheritance is now defined, while external creative providers remain disabled until their adapters are verified.

## Canonical inheritance

- Education is the civilization and universal-knowledge spine.
- Scope: world civilizations -> India -> state/region -> district/city/town/village -> community/local heritage.
- Every topic inherits origin -> history -> current -> trends -> future scenario analysis with provenance/evidence labels.
- All authorized agents inherit multimodal planning capabilities.
- Food, Education, War and History/Heritage receive enhanced 3D/4D/5D, animation, timeline and reconstruction profiles.

## Media adapters

Stable extension points:
- image_generation
- video_generation
- model_3d_generation
- animation
- rendering
- ar_runtime
- trend_source
- publisher

The adapter layer is provider-neutral and can route to approved AI/media providers, but provider connectivity is not claimed until endpoint, credentials, rights, safety, evaluation and runtime smoke-test evidence exist.

## Experience semantics

- 3D = spatial representation.
- 4D = spatial representation plus time/motion.
- 5D = time/motion plus contextual and interactive knowledge dimensions.

These are product/experience labels, not claims about additional physical dimensions.

## Domain routing

- food -> FOOD + relevant Education history/culture links
- education/civilization -> EDU
- historical war content -> WAR + EDU
- history/heritage -> owning specialist category + EDU when educational context applies

The historical/military route remains educational and non-operational.

## Process

```
INTENT -> OWNER AUTHENTICATE -> KNOWLEDGE -> PROVENANCE
-> SCENE PLAN -> GENERATE -> ANIMATE -> RENDER
-> QUALITY -> SAFETY/RIGHTS -> KUBER COST -> OWNER GATE
-> PUBLISH -> MEASURE -> KUBER RECONCILE -> ARCHIVE
```

The browser remains a plan/preview surface and does not expose secrets. External creative tools and publishing remain blocked until their adapters are actually configured and verified.

## Verification

Architecture contracts:
```sh
python3 ops/vyomaraj/media_capability_inheritance.py
python3 ops/engineering/verify_2026_stack.py
```

A PASS from these checks means the repository contracts are internally consistent. It does not mean external AI/media providers are live or deployed.
