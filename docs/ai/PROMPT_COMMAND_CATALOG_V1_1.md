# Vyomaraj / Jarvis Prompt & Command Catalogue v1.1

**Purpose:** owner-maintained, provider-neutral shortcuts for research, creation, education, solutions, social distribution and operations. These are aliases and reusable prompt presets, not a claim that every name is a native ChatGPT command.

## How to invoke

In the current repository text harness:

```sh
python3 ops/jarvis/llm_harness.py --list-presets
printf '%s\n' 'Your task here' | python3 ops/jarvis/llm_harness.py --role vyomaraj --preset truthmode
printf '%s\n' 'Your task here' | python3 ops/jarvis/llm_harness.py --role jarvis --preset kidseducation
```

Use one primary preset plus a small number of relevant lenses. Preset IDs are lowercase; use the registry as the source of truth. The text harness does not itself browse, generate images, run Python, publish content, send email, or execute external actions.

## Research and thinking aliases

| User alias / prompt | Canonical preset or route | Intended use |
|---|---|---|
| `/truthmode`, `/search` | `truthmode`, `search` | Evidence, current research, citations and uncertainty |
| `/firstprinciple` | `firstprinciple` | Rebuild from basic facts and constraints |
| `/blackswan` | `blackswan` | Tail risks, contingencies and early warnings |
| `/signalvsnoise` | `signalvsnoise` | Separate meaningful evidence from hype |
| `/predict` | `predict` | Base/upside/downside scenarios, indicators and uncertainty |
| `/x10think` | `x10think` | Leverage points and step-change improvement hypotheses |
| `/extendthinking`, `/xray` | `extendthinking`, `xray` | Structured rationale, hidden assumptions and gaps |
| `/mece`, `/scqa`, `/ooda`, `/socratic` | `mece`, `scqa`, `ooda`, `socratic` | Structure, decisions and targeted questions |
| `/falsify`, `/secondorder`, `/redteam` | `falsify`, `secondorder`, `redteam` | Challenge assumptions, downstream effects and safe adversarial review |
| `/steelman`, `/devils-advocate`, `/alt3` | `steelman`, `devilsadvocate`, `alt3` | Fair counterargument and alternative comparison |
| `/kill-critic` | `killcritic` | Convert criticism into constructive, testable improvements |
| `/tldr`, `/summary`, `/summarize` | `tldr`, `summary` | Concise answer or faithful source summary |
| `/futureyou`, `/roadmap`, `/plan`, `/next` | `futureyou`, `roadmap`, `plan` | Future-proofing, milestones and next actions |
| `/human`, `/transparent`, `/eli10` | `human`, `transparent`, `eli10` | Natural tone, auditability and plain-language explanation |

## Creation, education and child-first aliases

| User alias / prompt | Canonical preset or route | Intended use |
|---|---|---|
| `/content`, `/content-prompts` | `content` | Original content creation and repurposing |
| `/education`, `/chatgpt-in-education` | `education` | Lesson objectives, examples, practice and assessment |
| `/kidseducation`, `/child-safe-content` | `kidseducation`, `childsafecontent` | Age-appropriate, safe, privacy-conscious learning |
| `/userlike`, `/flavouring`, `/hook` | `userlike`, `flavouring`, `hook` | Enjoyable, audience-aware content without manipulation |
| `/anime-explainer`, `/eli10visual`, `/visualizelearning` | `animeexplainer`, `eli10visual`, `visualizelearning` | Visual explanation and storyboard briefs |
| `/quiz`, `/quizme`, `/flashcards` | `quizme`, `flashcards` | Retrieval practice and review |
| `/mindmap`, `/timeline`, `/sticky-notes` | `mindmap`, `timeline`, `sticky-notes` | Organizing concepts, history and tasks |
| `/cheatsheet`, `/blueprint`, `/infographics` | `cheatsheet`, `blueprint`, `infographic` | Quick reference, implementation plans and visual briefs |
| `/example`, `/analogy`, `/steps`, `/howto`, `/questions` | `example`, `analogy`, `steps`, `howto`, `questions` | Demonstration, analogy, procedure and inquiry |
| `/handwritten`, `/sketchnotes`, `/explodeview`, `/360view`, `/layers`, `/cycle`, `/iceberg`, `/powerflow` | `handwritten`, `explodedview`, `360view`, `layers`, `cycle`, `iceberg`, `powerflow` | Visual structures or a copy-ready visual brief |

## Marketing, sales, collaboration and publishing

| User alias / prompt | Canonical preset | Intended use |
|---|---|---|
| `/marketingprompts`, `/marketing` | `marketingprompt`, `marketing` | Ethical marketing, positioning and measurement |
| `/sales`, `/sales-prompts` | `sales` | Truthful sales scripts and objection handling |
| `/job-hunting-prompts` | `jobhunting` | Honest resumes, interviews and follow-ups |
| `/social-publish`, `/operationprompt` | `socialpublish`, `operationprompt` | Platform-aware package and SOP |
| `/collaboration` | `collaboration` | Partner fit, rights, terms, disclosure and outreach draft |
| `/legal-review` | `legalreview` | Jurisdiction-aware source-backed screening and owner decision packet |
| `/kuber` | `kuberfinance` | Cost, revenue, tax/royalty questions and ROI using verified figures |

## Capability commands: tool required, not just a prompt

| Alias | Required route | Honest fallback if unavailable |
|---|---|---|
| `/image`, `/generatehandwrittenimage` | Approved image-generation/editing tool | Provide prompt/design brief; say image tool unavailable |
| `/python`, `/math` | Sandboxed code runtime or verified calculation | Provide code/manual derivation, label unexecuted |
| `/canvas` | Supported canvas/editor integration | Provide copy-ready editable structure |
| `/pdf`, `/spreadsheet`, `/presentation` | File parsing or file-generation tool | Provide content/specification; don't claim a file was created |
| `/email` | Email connector with authorization | Draft only; do not claim sent |
| `/search` | Live search tool | State that live research could not be performed |
| `/all-plugins` | Tool discovery + explicit connection authorization | Inventory discoverable tools; never claim every plugin is installed |
| `/all-chatgpt-prompts`, `/all-chatgpt-commands`, `/help` | This public/user-owned catalogue plus active runtime capability discovery | Explain that private prompts, hidden reasoning and undocumented commands are not accessible |

## Universal output contract

For substantial work, return: **answer/recommendation → verified evidence → assumptions/unknowns → risks and alternatives → deliverable/draft → required approval → verification status → next action**. Add a final TL;DR, forecast, signal/noise or black-swan section only when useful/requested; never omit a critical warning merely to satisfy a style suffix.

## Child-focused release gate

Before a child-oriented lesson, video, short, game, post or campaign is released, verify:
1. Age band, learning objective and audience.
2. Accuracy and sources; distinguish facts, faith traditions, mythology and contested interpretations.
3. Developmental suitability, accessibility, inclusion and possible misinterpretations.
4. Child safety, privacy, consent, safe imitation and non-manipulative engagement.
5. Asset/music/voice/likeness rights and licenses.
6. Platform age rules, local availability, sponsorship/ad disclosure, automation and monetization eligibility.
7. Adult/editor review when required by risk or law.
8. Owner approval and evidence of the actual publishing result.

A preset is an instruction, not an enforcement control. Missing mandatory checks mean HOLD. External publishing and messaging require a supported tool, correct permissions, auditability and owner approval.

## Scope limitation

This catalogue does not expose private ChatGPT system/developer prompts or hidden chain-of-thought, and it does not make every alias a native slash command. It only describes user-owned prompt presets and routes available capabilities honestly.
