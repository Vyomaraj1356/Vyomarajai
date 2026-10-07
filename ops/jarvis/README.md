# Jarvis reachability monitor

The old V13 shell controller printed simulated device shifts, port states and “all heartbeats live” messages. Those statements were not backed by probes. The compatibility command `jarvis-24x7-controller.sh` now delegates to a read-only monitor and never sources `jarvis.env`.

## Configure a local probe

1. Copy `heartbeat-config.example.json` to an untracked `heartbeat-config.json`.
2. Add only health URLs for services you administer. Use HTTPS for remote hosts; plain HTTP is accepted only on loopback. URLs must end in `/healthz` and cannot contain credentials, query strings or fragments.
3. Set `JARVIS_HEARTBEAT_CONFIG` to that file, or keep it at the default path.
4. Run one probe with `./jarvis-24x7-controller.sh heartbeat`; inspect the recorded snapshot with `./jarvis-24x7-controller.sh status`.
5. To keep the *probe process* running, use `./jarvis-24x7-controller.sh run` under a user-owned service manager on the device where the repo is installed. This repository does not install services on the owner's phone, Mac or desktop.

The example configuration has empty peer URLs. It intentionally reports `not_configured` until an owner supplies real endpoints. Keep tokens and private keys out of this JSON file and out of Git.

## What the monitor proves

A `reachable` result means a configured endpoint answered a bounded HTTP GET. Any `ready` field in its response is an untrusted service claim. The output always sets `heartbeat_authenticated`, `production_peer_health_verified`, `production_dr_verified` and `failover_enabled` to false. This is not a mutual peer protocol, a 24/7 agent, a runtime replica, or an alerting service.

`shift` deliberately returns `BLOCKED`: device handover and DR failover require authenticated peers, shared durable state, quorum, writer fencing, tested recovery and owner authorization. A normal `/healthz` GET is not enough.

The Android APK in the repository is unsigned; this monitor does not install, sign or execute it. No macOS app source or signed package is present. The public landing page offers an installable web shell only, not a native application.
