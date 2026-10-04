# Platform configuration check — 2026-10-04

**Generated report.** The source list contains open owner/provider/platform checks; this report maps each one to a completion path. An assigned path is not proof of installation, provider access, owner approval or operational readiness.

Scope: Open configuration and owner-decision items only. A completion path is not evidence that a system is configured or operational.

**41 open items · all 41 have exactly one auto-align step.**

## How it gets configured (auto-align plan)

Use the step ids below in `AUTO_ALIGN_NEXT_SESSION_2026_10_04.md`. Each step defines an action, a verification, a `done_when` condition and a repository evidence path. The local runner does not configure accounts or services.

| Item | Area | Open item | Completion step | Action path |
|---|---|---|---|---|
| `O-01` | Owner decision | Select and configure the approved secret manager; record secret names and access policy, never secret values. | `o01-secret-manager` | Select the secret manager |
| `O-02` | Owner decision | Identify which contract record governs where the repository currently records a conflict. | `o02-contract-authority` | Resolve the governing contract record |
| `O-03` | Owner decision | Inventory the required tool accounts and owner-selected plans, without guessing plan limits or costs. | `o03-tool-accounts` | Confirm accounts and plans |
| `O-04` | Owner decision | Confirm the meaning and intended use of the recorded term "posilki". | `o04-posilki` | Clarify the recorded term |
| `P-01` | Research and drafting providers | Owner-authorize and configure the Perplexity research workflow. | `p01-research-drafting` | Configure research and drafting providers |
| `P-02` | Research and drafting providers | Owner-authorize and configure the ChatGPT workspace. | `p01-research-drafting` | Configure research and drafting providers |
| `P-03` | Research and drafting providers | Identify and review the custom GPTs required for the approved workflow. | `p01-research-drafting` | Configure research and drafting providers |
| `P-04` | Research and drafting providers | Owner-authorize and configure the Claude workflow. | `p01-research-drafting` | Configure research and drafting providers |
| `P-05` | Research and drafting providers | Owner-authorize and configure the Gemini workflow. | `p01-research-drafting` | Configure research and drafting providers |
| `P-06` | Media providers | Configure Canva canvas access and a reviewed asset workflow. | `p02-media-pipeline` | Configure media tools and rights evidence |
| `P-07` | Media providers | Configure ElevenLabs voice access with consent and review gates. | `p02-media-pipeline` | Configure media tools and rights evidence |
| `P-08` | Media providers | Configure Animaker access and a reviewed export path. | `p02-media-pipeline` | Configure media tools and rights evidence |
| `P-09` | Media providers | Configure CapCut access and a reviewed edit/export path. | `p02-media-pipeline` | Configure media tools and rights evidence |
| `P-10` | Media providers | Document approved stock image/video sources and item-level rights evidence. | `p02-media-pipeline` | Configure media tools and rights evidence |
| `P-11` | Media providers | Document approved music/audio sources and item-level rights evidence. | `p02-media-pipeline` | Configure media tools and rights evidence |
| `P-12` | Publishing, scheduling and analytics | Select publishing destinations and authorize accounts per platform. | `p03-publishing-stack` | Configure publishing, scheduling and analytics |
| `P-13` | Publishing, scheduling and analytics | Configure a human-approved scheduling workflow and its rollback path. | `p03-publishing-stack` | Configure publishing, scheduling and analytics |
| `P-14` | Publishing, scheduling and analytics | Configure analytics access, retention and owner review. | `p03-publishing-stack` | Configure publishing, scheduling and analytics |
| `P-15` | Review gates | Exercise review gates with real, owner-approved media before any publishing workflow is enabled. | `p04-review-gates` | Exercise review gates with real media |
| `S-01` | Studio and services | Install and verify the camera in the owner-approved studio location. | `s01-studio-install` | Install the studio path |
| `S-02` | Studio and services | Install and verify the voice/microphone path and consent controls. | `s01-studio-install` | Install the studio path |
| `S-03` | Studio and services | Install and verify the audio mixer and monitored signal path. | `s01-studio-install` | Install the studio path |
| `S-04` | Studio and services | Prepare the cut room and reviewed media handoff. | `s01-studio-install` | Install the studio path |
| `S-05` | Studio and services | Deploy a replicated work queue with documented ownership and recovery. | `s02-queue-events` | Deploy queue and event path |
| `S-06` | Studio and services | Deploy and test the queue event path, including duplicate and retry behavior. | `s02-queue-events` | Deploy queue and event path |
| `S-07` | Studio and services | Configure RAG sources, access scopes, freshness and deletion behavior. | `s03-rag-cag-mag` | Configure retrieval and memory boundaries |
| `S-08` | Studio and services | Configure CAG context assembly, provenance and review controls. | `s03-rag-cag-mag` | Configure retrieval and memory boundaries |
| `S-09` | Studio and services | Configure MAG memory boundaries, retention and per-agent access. | `s03-rag-cag-mag` | Configure retrieval and memory boundaries |
| `S-10` | Studio and services | Create scoped workspaces with least-privilege access and audit evidence. | `s04-workspaces-contracts` | Scope workspaces and agent contracts |
| `S-11` | Studio and services | Reconcile and approve per-agent contracts before assigning live work. | `s04-workspaces-contracts` | Scope workspaces and agent contracts |
| `S-12` | Studio and services | Install and exercise the Jarvis 24x7 runtime under an owner-approved service window. | `s05-jarvis-channels` | Configure Jarvis runtime and channels |
| `S-13` | Studio and services | Configure Jarvis communication channels with delivery and escalation tests. | `s05-jarvis-channels` | Configure Jarvis runtime and channels |
| `S-14` | Studio and services | Deploy ShriYantra control services with explicit authority and fail-closed behavior. | `s06-shriyantra` | Deploy ShriYantra control services |
| `D-01` | Disaster recovery and operations | Provision an independent DR failure domain; the local two-lane rehearsal is not independent DR. | `d01-independent-dr` | Establish independent DR and tested restore |
| `D-02` | Disaster recovery and operations | Run and record a tested restore from an independent, owner-approved backup. | `d01-independent-dr` | Establish independent DR and tested restore |
| `D-03` | Disaster recovery and operations | Define and approve the business maintenance window and escalation owner. | `d02-business-probes` | Define business window and real probes |
| `D-04` | Disaster recovery and operations | Run real, owner-approved probes and record their scope, result and limitations. | `d02-business-probes` | Define business window and real probes |
| `D-05` | Disaster recovery and operations | Define a staged rollout with explicit canary, stop and rollback gates. | `d03-rollout-hermes` | Stage rollout and Hermes monitoring |
| `D-06` | Disaster recovery and operations | Configure Hermes monitoring and prove actionable alert delivery. | `d03-rollout-hermes` | Stage rollout and Hermes monitoring |
| `D-07` | Disaster recovery and operations | Define runtime intelligence inputs, privacy scope and owner review before activation. | `d04-intelligence-learning` | Define runtime intelligence and learning loop |
| `D-08` | Disaster recovery and operations | Define a measured learning loop with versioned evaluations and rollback criteria. | `d04-intelligence-learning` | Define runtime intelligence and learning loop |

## Owner and execution boundaries

- Owner decisions, provider access, studio installation, real-media review, DR provisioning and live probes require explicit owner action.
- The checked-in local preview and Git snapshot evidence are not substitutes for independent production DR, runtime backup/restore or an approved business window.
- Evidence must be added to the step's repository path and reviewed before a status changes to DONE.
- No prices, plan limits or earnings projections are part of this report.

Source items: `ops/vyomaraj-core/handover/PLATFORM_OPEN_ITEMS_2026_10_04.json`
Completion plan: `ops/vyomaraj-core/handover/AUTO_ALIGN_NEXT_SESSION.json`
