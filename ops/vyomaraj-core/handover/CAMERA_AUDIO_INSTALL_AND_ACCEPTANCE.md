# Camera, Reels Review and Audio/Dolby — Installation & Acceptance

Date: 2026-10-24

## Software delivered in this branch
- /approvals/devices.html is a local browser device-check page served by the loopback-only Experience Studio.
- It enumerates browser-visible cameras, microphones and audio outputs; requests explicit permission; shows live camera preview; records a local-only MediaRecorder clip; plays it back; sends a test tone; and displays a microphone level meter.
- DEVICE_CAPABILITY_REGISTRY.json records evidence-based statuses.
- Test media is not uploaded, stored by the server or published. Reports are downloaded locally by user action.

## Run locally
From the repository root on the target device:
```powershell
python ops/vyomaraj-core/experience/studio_server.py --host 127.0.0.1 --port 4176 --home bhakti
```
Open http://127.0.0.1:4176/approvals/devices.html. Camera/microphone permissions generally work on localhost; if browser/OS policy blocks access, use an approved HTTPS deployment and explicit permission. Never bind the private studio to a public network.

## Acceptance steps
1. Refresh inventory; names may remain hidden until permission.
2. Choose camera and requested resolution; grant browser/OS permission; verify real live image and actual resolution.
3. Record a short, non-sensitive test clip, stop and play it; verify synchronization where audio is present. Download is optional and user-triggered.
4. Select output if supported, play test tone, and physically confirm it is audible.
5. Grant microphone permission, speak and confirm meter response; stop. This page does not transmit audio.
6. Verify Dolby separately using device vendor/OS diagnostics and a valid supported/licensed test path. Browser Web Audio cannot establish Dolby installation, licence, driver state or surround processing.
7. Test the owner approval queue with a valid action-bound token and test media; verify audit event. Publishing remains a separate gate.
8. Record device model, OS/build, browser, permission result, measured resolution, output route, Dolby evidence and timestamp in the private CMDB. Never put personal media, tokens or secrets in issues or CI logs.

## Limits
This adds software and a repeatable verification path; it does not remotely install camera drivers, Dolby software/licences, or control physical devices. It does not configure the owner-token issuer, upload media, enable notifications, deploy the private studio, or prove production behavior. Each target machine must pass acceptance before status is promoted to VERIFIED_IN_TEST; production requires deployment evidence as well.
