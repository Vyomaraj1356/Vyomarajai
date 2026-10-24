# Vyomaraj/Jarvis cross-device audio/video capability plan

**Status: contract and audit guard proposed; physical playback remains unverified.** Scope: web, Windows, Android, macOS, TV/home-cinema paths. This document does not assert that a device, codec, subscription, Dolby license, decoder, or provider integration exists.

## Audit findings (22 October 2026)

- Existing `ops/vyomaraj/media-capability-gate.sh` and `media_capability_inheritance.py` validate a general multimodal/3D architecture contract. They explicitly say provider calls are not made and external rendering is not verified. They do not prove audio/video playback.
- The public preview server is a bounded catalog/planner, not a media player or production media backend. Its `/healthz` reports process liveness only; its public security headers disable microphone and camera for that preview.
- The connected Runway workspace authenticated successfully and exposed sound-effect generation, but returned no available video or music models and marked video generation/editing/upscaling as gated. This proves tool account connectivity only, not integration into the Vyomaraj runtime. A tool-level speech feature, where available, is not evidence of a deployed app voice path.
- The connected Descript account returned zero accessible projects at audit time.
- No evidence found in inspected records proves Dolby Atmos/Dolby Vision licensing, a hardware decoder, a calibrated HDR display, a live mixer, a production playback path, or end-to-end device tests.

## Target architecture

1. **Capability registry** — each media capability has separate implementation and runtime states, evidence references, requirements, and a fallback.
2. **Device-aware client adapter** — detect supported browser APIs, codec/container support, output path, viewport/display limits, permissions, and network conditions where the platform exposes them. Do not infer physical HDMI/Atmos/HDR capability from user-agent strings alone.
3. **Audio chain** — permission-gated capture; optional speech recognition/TTS; voice activity detection, echo cancellation and noise suppression when supported; conservative gain; clipping/loudness tests; optional spatial output only when the full path supports it. Keep text-only and stereo fallbacks.
4. **Video chain** — select a source/rendition compatible with decoder, display, bandwidth and rights; adaptive bitrate only when a real streaming manifest/player and multiple renditions exist; captions/transcript and accessible controls.
5. **Premium formats** — Dolby Atmos and Dolby Vision are separate license/device/source/decoder/output-path questions. Use a verified supported fallback (multichannel/stereo, HDR10/SDR) and never label fallback output as the premium format.
6. **Owner safety** — microphone/camera are opt-in; no silent capture; publishing, purchases, license activation, external account changes and production deployment require owner approval. Never store provider secrets in the registry or evidence report.

## Acceptance tests before any capability becomes verified

- **All clients:** identify app/build, OS/browser, device model, selected source/rendition and test timestamp; store redacted evidence with no tokens or private media.
- **Audio:** user grants mic permission; capture starts/stops correctly; denied permission preserves text path; TTS audio plays; no clipped peaks in a known test fixture; output fallback works; channel count/spatial mode is reported only when observed.
- **Video:** known licensed test clip plays; selected resolution and codec are measured; playback survives a network downgrade if adaptive streaming is claimed; captions can be enabled; unsupported codecs fail gracefully.
- **4K/HDR:** verify actual source rendition, decoder path and display output; a 4K source file alone does not prove 4K display. HDR metadata alone does not prove HDR output.
- **Dolby:** capture authorized license/provider evidence, compatible source/decoder/output device and end-to-end result. Do not simulate or infer a pass.
- **Release:** run on real Windows, Android, macOS, web and TV/home-cinema target classes; record per-device outcomes. One device's pass does not generalize to all devices.

## Safe implementation in this change

- Adds a machine-readable capability contract and deterministic validator/test.
- All runtime states remain unverified until supported by evidence.
- Validator success means the contract is structurally consistent only. It is not an installation, deployment, hardware, licensing, playback or provider-connection test.
- This change does not alter public preview permissions, install OS codecs, connect providers, buy licenses, or deploy to devices.
