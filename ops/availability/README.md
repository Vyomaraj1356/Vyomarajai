# Local Vyomaraj / Jarvis availability rehearsal

**Not an independent DR site, not a redundant production load balancer, not autonomous AI-agent replication, and not proof of zero RPO/RTO.** These two application replicas share one sandbox, checkout and SQLite queue. Loss of that machine/storage defeats both. The gateway itself is a single point of failure.

## Implemented for a local rehearsal — not running or production deployed

Run each command as its own managed long-lived process from the repository root:

```bash
python ops/vyomaraj-core/experience/studio_server.py --port 4181 --home aghor
python ops/vyomaraj-core/experience/studio_server.py --port 4182 --home aghor
python ops/availability/gateway.py --port 4176 --primary-port 4181 --secondary-port 4182
```

The studio replicas and gateway now default to **127.0.0.1** and reject non-loopback bind addresses. Gateway upstreams are fixed **server-side** loopback ports. Browser code uses relative URLs and never calls a sandbox `localhost` address from the user's device. Original Host/Origin identity is forwarded so same-origin checks work behind the gateway. Ports must be distinct; arbitrary upstream URLs are not accepted. This configuration is for a same-host local rehearsal only; it is not the public sandbox preview.

- `GET /healthz` at a replica checks application registry metadata only, not all dependencies or data durability.
- `GET /api/availability` at the gateway reports both replica checks and explicitly declares the single-host/shared-state limitations.
- Read-only GET requests fall back on connection errors or server failures, but legitimate 404s are not hidden.
- POST chooses a responding replica, then is sent **once**. Research enqueue/review and privileged approval/change actions require request-scoped, action-bound owner tokens; a missing or invalid token fails closed. Ambiguous write failure returns 503 and tells the caller to inspect state, rather than replaying an operation that might already have committed. The research worker is opt-in on each studio process. No trusted owner issuer is configured here, so these privileged paths are not usable until the owner provisions it out of band.
- Request bodies are bounded to 16 KB; chunked client uploads and unsupported methods are refused. Upstream replies are bounded to 16 MB. Socket timeouts are not comprehensive protection against every slow-client pattern; production ingress hardening is still needed.
- Discovery's SQLite lease and provider throttling are shared, so these two local workers do not intentionally run the same job simultaneously. If a worker dies during a job, the existing ten-minute lease-expiry handling applies; there is no zero-time job migration.

## Actual controlled drill

`LOCAL_FAILOVER_DRILL_2026_10_03.json` records real HTTP responses while these owned local processes were stopped/restarted:

1. Both up: 200 from primary.
2. Primary stopped: 200 from secondary.
3. Secondary stopped with primary restored: 200 from primary.
4. Both stopped: 503, no false healthy result.
5. Both restored: 200 from primary; both readiness checks true.

`LOCAL_FAILOVER_DRILL_2026_10_04.json` records a repeat of the same controlled drill on 2026-10-04 (200 → 200 from secondary → 200 from primary → 503 with both stopped → 200 restored, zero ambiguous POST failures) after the sandbox was re-provisioned. The same limitations apply.

Recorded milliseconds measure one request **after the fault**, not elapsed time from disaster onset, guaranteed detection time, production RTO or replication lag. No production traffic or Git ref was changed during the drill. No runtime database backup/restore, separate-host deployment or machine-loss recovery was tested.

## Production requirements still outstanding

Use independent hosts/failure domains, authenticated ingress, health-aware redundant routing, fencing/single-writer discipline, a replicated durable datastore and separately tested encrypted backups. Back up secrets through an appropriate secret manager, not through these reports or a Git mirror. Test restoration and failback with measured workloads and define an achievable RPO/RTO. The separate public sandbox landing preview remains static/read-only; this local rehearsal is loopback-only and must not be represented as a production approval system.
